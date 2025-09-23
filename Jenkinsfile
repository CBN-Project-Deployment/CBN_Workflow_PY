pipeline {
    agent any

    environment {
        PYTHON_VERSION = "python3"
        WORKSPACE_PY = "${WORKSPACE}/CBN_Workflow_PY"
        WORKSPACE_CPP = "${WORKSPACE}/cpp_code"
        OUTPUT_DIR = "${WORKSPACE}/nodejs_output"
    }

    stages {

        stage('Checkout Main SCM') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git']]
                ])
            }
        }

        stage('Checkout Python Workflow') {
            steps {
                dir("${WORKSPACE_PY}") {
                    git branch: 'main', url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
                }
            }
        }

        stage('Clone C++ Repository') {
            steps {
                dir("${WORKSPACE_CPP}") {
                    git branch: 'main', url: 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git'
                }
            }
        }

        stage('Setup Python Environment & Install Dependencies') {
            steps {
                dir("${WORKSPACE_PY}") {
                    sh """
                        # Remove old virtualenv if exists
                        [ -d venv ] && rm -rf venv
                        
                        # Create fresh virtualenv
                        ${env.PYTHON_VERSION} -m venv venv
                        
                        # Activate virtualenv and upgrade pip
                        . venv/bin/activate
                        python3 -m pip install --upgrade pip
                        
                        # Install dependencies
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        fi
                        pip install requests
                    """
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir("${WORKSPACE_PY}") {
                    sh """
                        mkdir -p ${OUTPUT_DIR}
                        . venv/bin/activate
                        export PYTHONPATH=\$PWD:\$PYTHONPATH
                        python3 run_cbn_workflow.py --input ${WORKSPACE_CPP} --output ${OUTPUT_DIR}
                    """
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            when {
                expression { return fileExists("${OUTPUT_DIR}") }
            }
            steps {
                dir("${OUTPUT_DIR}") {
                    sh """
                        git init
                        git add .
                        git commit -m "Automated Node.js output update"
                        git branch -M main
                        git remote add origin <YOUR_NODEJS_REPO_URL>
                        git push -u origin main --force
                    """
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning workspace...'
            cleanWs()
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
