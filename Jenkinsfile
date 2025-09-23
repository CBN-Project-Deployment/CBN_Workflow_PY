pipeline {
    agent any

    environment {
        WORKSPACE_DIR = "${env.WORKSPACE}"
        PYTHON_WORKFLOW_DIR = "${env.WORKSPACE}/CBN_Workflow_PY"
        CPP_CODE_DIR = "${env.WORKSPACE}/cpp_code"
        NODEJS_OUTPUT_DIR = "${env.WORKSPACE}/nodejs_output"
    }

    stages {
        stage('Checkout Python Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    git branch: 'main', url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
                }
            }
        }

        stage('Checkout C++ Repository') {
            steps {
                dir('cpp_code') {
                    git branch: 'main', url: 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git'
                }
            }
        }

        stage('Setup Python Environment & Install Dependencies') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh '''
                    # Clean previous virtualenv
                    rm -rf venv

                    # Create new virtualenv
                    python3 -m venv venv
                    . venv/bin/activate

                    # Upgrade pip
                    python3 -m pip install --upgrade pip

                    # Install requirements if file exists
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi

                    # Always install requests as fallback
                    pip install requests
                    '''
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh '''
                    # Activate virtualenv
                    . venv/bin/activate

                    # Ensure workflow directory is on PYTHONPATH
                    export PYTHONPATH=$PWD

                    # Create output directory if missing
                    mkdir -p ${NODEJS_OUTPUT_DIR}

                    # Run the workflow
                    python3 run_cbn_workflow.py --input ${CPP_CODE_DIR} --output ${NODEJS_OUTPUT_DIR}
                    '''
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            steps {
                dir('nodejs_output') {
                    sh '''
                    # Example: push output to GitHub (fill in your commands)
                    git init
                    git add .
                    git commit -m "Update Node.js output"
                    git remote add origin <YOUR_NODEJS_OUTPUT_REPO_URL>
                    git push -f origin main
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning workspace...'
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
