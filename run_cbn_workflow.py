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
def get_user_project(headers, project_name, namespace):
    """
    Retrieve project ID and wallet ID for the given project name.
    """
    url = f"{cfg.URL_BASE}/projects"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    for project in response.json().get('results', []):
        if project.get('name') == project_name and  project.get('namespace') == namespace:
            print("CbN Project :", project.get('name'))
            return project.get('id'), project.get('wallet_id')

    raise ValueError(f"Project '{project_name}' not found.")

# -------------------------------
# DOWNLOAD CbN OUTPUT
# -------------------------------
def download_blob(headers, container, blob_id):
    """
    Download blob which is output of CbN workflow
    """
    url = f"{cfg.URL_BASE}/datalake/{container}/{blob_id}"
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Blob downloaded successfully")
        return response.content  # binary data
    else:
        print("Error:", response.status_code, response.text)
        return None

# -------------------------------
# STREAM LISTENER
# -------------------------------
def listen_to_stream(headers, output_path):
    """
    Listen to the streaming endpoint and save results as files.
    Handles both direct JSON results and Blob downloads.
    """

    stream_url = f"{cfg.URL_BASE}/stream"
    try:
        with requests.get(stream_url, headers=headers, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    decoded = line.decode('utf-8')
                    if not decoded.startswith("data: "):
                        continue
                    json_part = decoded[6:].strip()
                    if not json_part:
                        continue

                    data = json.loads(json_part)
                    execution_id = data.get('id')
                    result = None

                    # --- Handle blob or direct result ---
                    data_content = data.get('data', {})
                    data_type = data_content.get('type')

                    if data_type == 'Blob':
                        blob_id = data_content.get('id')
                        container = data_content.get('container')
                        #-----Function call to download blob-----
                        blob_data = download_blob(headers, container, blob_id)
                        if blob_data:
                            blob_data = blob_data.decode("utf-8")
                            blob_data = json.loads(blob_data)
                            result = blob_data.get("Final_Result")
                    else:
                        result = data_content.get("Final_Result")
                    # ---- ------------- ------------- ------
                    
                    if execution_id and result:
                        stream_results.append(execution_id)
                        filename = execution_id_dict.get(execution_id)
                        if filename:
                            output_file = Path(output_path) / f"{filename}.js"
                            with open(output_file, "w", encoding="utf-8") as f:
                                f.write(result)
                            print(f"{filename}.js : file created.")
                except json.JSONDecodeError:
                    continue
    except requests.RequestException as e:
        print(f"Stream connection failed: {e}")

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
        print("Usage: python run_cbn_workflow.py [datastage|stored_procedure]")
        sys.exit(1)

    FILETYPE = sys.argv[1]
    PASSWORD = os.environ.get("CBN_PASSWORD")

    if not PASSWORD:
        print("Environment variable 'CBN_PASSWORD' not set.")
        sys.exit(1)

    cbn_namespace = cfg.CBN_NAMESPACE
    cbn_project = cfg.CBN_PROJECT
    input_dir = f"{cfg.INPUT_DIR}/{FILETYPE}"
    output_dir = f"{cfg.OUTPUT_DIR}/{FILETYPE}"

    # Ensure input directory exists and has files
    if not os.path.exists(input_dir) or not any(Path(input_dir).iterdir()):
        print(f"No input files found in {input_dir}")
        sys.exit(1)

    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Step 1: Authenticate and retrieve token
        token = authenticate(PASSWORD)
        print("Authentication successful.")

        # Step 2: Retrieve project and wallet ID
        headers = {'Authorization': f'Bearer {token}'}
        project_id, wallet_id = get_user_project(headers, cbn_project, cbn_namespace)

    except requests.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

    # Determine suffix based on file type
    suffix = "datastage" if FILETYPE == "datastage" else "cpp"
    encoding = "utf-8" if FILETYPE == "datastage" else "windows-1252"

    # Step 3: Start stream listener in background
    stream_thread = threading.Thread(target=listen_to_stream, args=(headers, output_dir), daemon=True)
    stream_thread.start()
    time.sleep(2)  # Ensure the stream is ready

    # Step 4: Send files and get execution IDs
    execution_ids = send_file_to_api(input_dir, suffix, headers, project_id, wallet_id, encoding)

    # Step 5: Check for stream to end
    check_for_stream(execution_ids)

# -------------------------------
# SCRIPT ENTRY POINT
# -------------------------------
if __name__ == '__main__':
    main()
