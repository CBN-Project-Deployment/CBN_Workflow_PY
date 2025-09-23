pipeline {
    agent any

    environment {
        PYTHONPATH = "${WORKSPACE}/CBN_Workflow_PY"
        VENV_DIR = "${WORKSPACE}/CBN_Workflow_PY/venv"
        NODE_OUTPUT_DIR = "${WORKSPACE}/nodejs_output"
    }

    stages {

        stage('Checkout Repositories') {
            parallel {
                stage('Checkout Python Workflow') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            git branch: 'main', url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
                        }
                    }
                }

                stage('Checkout C++ Code') {
                    steps {
                        dir('cpp_code') {
                            git branch: 'main', url: 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git'
                        }
                    }
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                dir('CBN_Workflow_PY') {
                    // Clean previous virtual environment
                    sh 'rm -rf venv'
                    sh 'python3 -m venv venv'

                    // Activate virtualenv and upgrade pip
                    sh """
                        . venv/bin/activate
                        python3 -m pip install --upgrade pip
                    """

                    // Install required packages if requirements.txt exists
                    sh """
                        if [ -f requirements.txt ]; then
                            . venv/bin/activate
                            pip install -r requirements.txt
                        fi

                        # Always ensure 'requests' is installed
                        . venv/bin/activate
                        pip install requests
                    """
                }
            }
        }

        stage('Verify cbn_config.py') {
            steps {
                dir('CBN_Workflow_PY') {
                    // Fail gracefully if cbn_config.py is missing
                    sh """
                        if [ ! -f cbn_config.py ]; then
                            echo "ERROR: cbn_config.py not found! Pipeline cannot proceed."
                            exit 1
                        else
                            echo "cbn_config.py exists, continuing..."
                        fi
                    """
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh """
                        mkdir -p ${NODE_OUTPUT_DIR}
                        . venv/bin/activate
                        python3 run_cbn_workflow.py --input ${WORKSPACE}/cpp_code --output ${NODE_OUTPUT_DIR}
                    """
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            when {
                expression { return fileExists("${NODE_OUTPUT_DIR}") }
            }
            steps {
                dir("${NODE_OUTPUT_DIR}") {
                    sh """
                        git init
                        git remote add origin https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git
                        git add .
                        git commit -m "Automated Node.js output commit"
                        git push -u origin main
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
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
