pipeline {
    agent any

    environment {
        PYTHON_VENV = 'venv'
        NODEJS_OUTPUT = 'nodejs_output'
    }

    stages {

        stage('Checkout Main SCM') {
            steps {
                checkout([$class: 'GitSCM', 
                          branches: [[name: '*/main']],
                          userRemoteConfigs: [[url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git']]])
            }
        }

        stage('Checkout Python Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    git branch: 'main', url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
                }
            }
        }

        stage('Clone C++ Repository') {
            steps {
                dir('cpp_code') {
                    git branch: 'main', url: 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git'
                }
            }
        }

        stage('Setup Python Environment & Install Dependencies') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh """
                        python3 -m venv ${PYTHON_VENV}
                        . ${PYTHON_VENV}/bin/activate
                        python3 -m pip install --upgrade pip
                        pip install -r requirements.txt || pip install requests
                    """
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
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
                    // Optional: push output to a Git repo if needed
                    // sh 'git add . && git commit -m "Update Node.js output" && git push'
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
        success {
            echo 'Pipeline completed successfully!'
        }
    }
}
