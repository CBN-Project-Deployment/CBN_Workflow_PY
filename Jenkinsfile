pipeline {
    agent any

    environment {
        PYTHON_VENV = "venv"
        NODEJS_OUTPUT = "nodejs_output"
        CPLUSPLUS_REPO = "https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git"
        PYTHON_WORKFLOW_REPO = "https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git"
    }

    stages {
        stage('Checkout Python Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    git url: "${PYTHON_WORKFLOW_REPO}", branch: 'main'
                }
            }
        }

        stage('Clone C++ Repository') {
            steps {
                dir('cpp_code') {
                    git url: "${CPLUSPLUS_REPO}", branch: 'main'
                }
            }
        }

        stage('Setup Python Environment & Install Dependencies') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh """
                        python3 -m venv ${PYTHON_VENV}
                        . ${PYTHON_VENV}/bin/activate
                        pip install --upgrade pip
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        fi
                        # Ensure 'requests' and other common dependencies are installed
                        pip install requests
                    """
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir('CBN_WorkFLOW_PY') {
                    sh """
                        mkdir -p ../${NODEJS_OUTPUT}
                        . ${PYTHON_VENV}/bin/activate
                        python3 run_cbn_workflow.py --input ../cpp_code --output ../${NODEJS_OUTPUT}
                    """
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            steps {
                dir("${NODEJS_OUTPUT}") {
                    script {
                        sh """
                            git init
                            git remote add origin https://github.com/Mrityunjai-demo/NodeJS_Output.git
                            git checkout -b main || git switch -c main
                            git add .
                            git commit -m "Add Node.js output from CbN workflow"
                            git push -u origin main --force
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning workspace..."
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed!"
        }
    }
}
