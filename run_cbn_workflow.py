import json
import os
from pathlib import Path
import requests
import sys
import threading
import time

import cbn_config as cfg  # Custom config file with constants

# Dictionary to store results from stream by execution_id
execution_id_dict = {}
stream_results = []

# -------------------------------
# AUTHENTICATION
# -------------------------------
def authenticate(password):
    """
    Authenticate the user and return an access token.
    """
    payload = {
        'grant_type': 'password',
        'username': cfg.USERNAME,
        'password': password,
        'scope': f'openid {cfg.ROPC_CLIENT_ID} offline_access',
        'client_id': cfg.ROPC_CLIENT_ID,
        'response_type': 'token id_token'
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(cfg.AUTH_ROPC_URL, data=payload, headers=headers)
    response.raise_for_status()

    return response.json().get('access_token')


# -------------------------------
# PROJECT RETRIEVAL
# -------------------------------
def get_user_project(headers, project_name):
    """
    Retrieve project ID and wallet ID for the given project name.
    """
    url = f"{cfg.URL_BASE}/projects"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    for project in response.json().get('results', []):
        if project.get('name') == project_name:
            return project.get('id'), project.get('wallet_id')

    raise ValueError(f"Project '{project_name}' not found.")


# -------------------------------
# STREAM LISTENER
# -------------------------------
def listen_to_stream(headers, output_path):
    """
    Connect to the streaming endpoint and listen for final results.
    Runs in a separate thread.
    """
    stream_url = f"{cfg.URL_BASE}/stream"

    with requests.get(stream_url, headers=headers, stream=True) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith("data: "):
                json_part = decoded_line[6:].strip()
                if not json_part:
                    continue
                try:
                    data = json.loads(json_part)
                    execution_id = data.get('id')
                    result = data.get('data', {}).get('Final_Result')
                    if execution_id and result:
                        stream_results.append(execution_id)
                        filename = execution_id_dict.get(execution_id)
                        if filename:
                            output_file = Path(output_path) / f"{filename}.md"
                            with open(output_file, "w", encoding="utf-8") as f:
                                f.write(result)
                            print(f"{filename}.md : file created.")
                        #print(f"Elapsed time (ms): {data.get('elapsed_time_ms', '0')}")
                except json.JSONDecodeError:
                    continue


# -------------------------------
# FILE PROCESSING
# -------------------------------
def send_file_to_api(file_path, suffix, headers, project_id, wallet_id, encoding):
    """
    Send all files in the specified directory to the API for processing.
    Returns a dictionary mapping filenames to execution IDs.
    """
    url = f"{cfg.URL_BASE}/dags/api-workflow-{suffix}-01"
    dir_path = Path(file_path)

    for file in dir_path.iterdir():
        if file.is_file():
            print(f"Processing: {file.name}")

            with open(file, mode="r", encoding=encoding) as f:
                file_content = f.read()

            body = {
                "project_id": project_id,
                "wallet_id": wallet_id,
                "data": {"content": file_content}
            }

            response = requests.post(url, headers=headers, json=body)

            if response.ok:
                execution_id = response.json().get("execution_id")
                if execution_id:
                    execution_id_dict[execution_id] = file.name
                else:
                    print(f"No execution_id in response: {response.json()}")
            else:
                print(f"Failed to process {file.name}: {response.status_code} - {response.text}")

    return execution_id_dict


# -------------------------------
# Check if need to wait for stream
# -------------------------------
def check_for_stream(execution_ids):
    """
    Wait for all stream results.
    """
    timeout = time.time() + 600 # Close stream after 10 minutes.
    print("\nWaiting for stream results...\n")
    
    # Wait until all execution IDs have results
    while True:
        if all(eid in stream_results for eid in execution_ids) or time.time() > timeout:
            break
        time.sleep(1)

    if time.time() > timeout:
        print("Timeout reached. Some results may be missing.")
    else:
        print("\n=== All results received from stream...exiting...===\n")
# -------------------------------
# MAIN ENTRY POINT
# -------------------------------
def main():
    """
    Main function to execute the workflow: authenticate, send files, listen for results, and save outputs.
    """
    if len(sys.argv) != 2:
        print("Usage: python run_cbn_workflow.py [cpp|stored_procedure]")
        sys.exit(1)

    FILETYPE = sys.argv[1]
    PASSWORD = os.getenv("CBN_PASSWORD")

    if not PASSWORD:
        print("⚠️  CBN_PASSWORD not set — running in NO-AUTH mode (test only).")
        PASSWORD = None

    cbn_project = cfg.CBN_PROJECT
    INPUT_DIR = f"{cfg.INPUT_DIR}/{FILETYPE}"
    OUTPUT_DIR = f"{cfg.OUTPUT_DIR}/{FILETYPE}"

    # Ensure input directory exists and has files
    if not os.path.exists(INPUT_DIR) or not any(Path(INPUT_DIR).iterdir()):
        print(f"No input files found in {INPUT_DIR}")
        sys.exit(1)

    # Create output directory if needed
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        if PASSWORD:
            # Step 1: Authenticate and retrieve token
            token = authenticate(PASSWORD)
            print("✅ Authentication successful.")

            # Step 2: Retrieve project and wallet ID
            headers = {'Authorization': f'Bearer {token}'}
            project_id, wallet_id = get_user_project(headers, cbn_project)
        else:
            # Fallback test mode
            print("🚀 Skipping authentication and project lookup (test mode).")
            headers, project_id, wallet_id = {}, None, None

    except requests.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

    # Determine suffix and encoding
    suffix = "datastage" if FILETYPE == "datastage" else "stored-procedure"
    encoding = "utf-8" if FILETYPE == "datastage" else "utf-16"

    # Step 3: Start stream listener in background
    stream_thread = threading.Thread(target=listen_to_stream, args=(headers, OUTPUT_DIR), daemon=True)
    stream_thread.start()
    time.sleep(2)  # Ensure the stream is ready

    # Step 4: Send files and get execution IDs
    execution_ids = send_file_to_api(INPUT_DIR, suffix, headers, project_id, wallet_id, encoding)

    # Step 5: Check for stream to end
    check_for_stream(execution_ids)

    # Create output directory if needed
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        # Step 1: Authenticate and retrieve token
        token = authenticate(PASSWORD)
        print("Authentication successful.")

        # Step 2: Retrieve project and wallet ID
        headers = {'Authorization': f'Bearer {token}'}
        project_id, wallet_id = get_user_project(headers, cbn_project)

    except requests.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

    # Determine suffix based on file type
    suffix = "datastage" if FILETYPE == "datastage" else "stored-procedure"
    encoding = "utf-8" if FILETYPE == "datastage" else "utf-16"

    # Step 3: Start stream listener in background
    stream_thread = threading.Thread(target=listen_to_stream, args=(headers,OUTPUT_DIR), daemon=True)
    stream_thread.start()
    time.sleep(2)  # Ensure the stream is ready

    # Step 4: Send files and get execution IDs
    execution_ids = send_file_to_api(INPUT_DIR, suffix, headers, project_id, wallet_id, encoding)

    # Step 5: Check for stream to end
    check_for_stream(execution_ids)


# -------------------------------
# SCRIPT ENTRY POINT
# -------------------------------
if __name__ == '__main__':
    main()
