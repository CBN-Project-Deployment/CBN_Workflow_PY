pipeline {
    agent any

    environment {
        PYTHON_ENV = "venv"
        PYTHON_PATH = "${WORKSPACE}/CBN_Workflow_PY"
        NODE_OUTPUT_DIR = "${WORKSPACE}/nodejs_output"
    }

    stages {

        stage('Checkout Repositories') {
            parallel {
                stage('Python Workflow') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            git branch: 'main', url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
                        }
                    }
                }
                stage('C++ Code') {
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
                    sh """
                        rm -rf ${PYTHON_ENV}
                        python3 -m venv ${PYTHON_ENV}
                        . ${PYTHON_ENV}/bin/activate
                        python3 -m pip install --upgrade pip
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        else
                            pip install requests
                        fi
                    """
                }
            }
        }

        stage('Verify cbn_config.py') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (!fileExists('cbn_config.py')) {
                            error("cbn_config.py not found! Please add it to the repo before running the workflow.")
                        } else {
                            echo "cbn_config.py exists, continuing..."
                        }
                    }
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh """
                        . ${PYTHON_ENV}/bin/activate
                        mkdir -p ${NODE_OUTPUT_DIR}
                        export PYTHONPATH=${PYTHON_PATH}
                        python3 run_cbn_workflow.py cpp
                    """
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            when {
                expression { fileExists("${NODE_OUTPUT_DIR}") }
            }
            steps {
                dir("${NODE_OUTPUT_DIR}") {
                    sh """
                        git init
                        git remote add origin https://github.com/Mrityunjai-demo/NodeJS_Output.git || true
                        git add .
                        git commit -m "Update Node.js output from Jenkins build ${BUILD_NUMBER}" || true
                        git push -u origin main --force
                    """
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning workspace..."
            cleanWs()
        }
        failure {
            echo "Pipeline failed!"
        }
        success {
            echo "Pipeline completed successfully!"
        }
    }
}
