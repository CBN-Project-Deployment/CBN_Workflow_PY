pipeline {
    agent any

    environment {
        WORKSPACE_DIR = "${env.WORKSPACE}"
        PYTHON_WORKFLOW_DIR = "${env.WORKSPACE}/CBN_Workflow_PY"
        CPP_CODE_DIR = "${env.WORKSPACE}/cpp_code"
        OUTPUT_DIR = "${env.WORKSPACE}/nodejs_output"
    }

    stages {

        stage('Checkout Repositories') {
            parallel {
                stage('Checkout Python Workflow') {
                    steps {
                        dir("${PYTHON_WORKFLOW_DIR}") {
                            git url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git', branch: 'main'
                        }
                    }
                }
                stage('Checkout C++ Code') {
                    steps {
                        dir("${CPP_CODE_DIR}") {
                            git url: 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git', branch: 'main'
                        }
                    }
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                dir("${PYTHON_WORKFLOW_DIR}") {
                    // Clean virtualenv if it exists
                    sh '''
                        rm -rf venv
                        python3 -m venv venv
                        . venv/bin/activate
                        python3 -m pip install --upgrade pip
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        fi
                        pip install requests
                    '''
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir("${PYTHON_WORKFLOW_DIR}") {
                    sh '''
                        . venv/bin/activate
                        mkdir -p "${OUTPUT_DIR}"
                        export PYTHONPATH="${PYTHON_WORKFLOW_DIR}"
                        python3 run_cbn_workflow.py --input "${CPP_CODE_DIR}" --output "${OUTPUT_DIR}"
                    '''
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            steps {
                dir("${OUTPUT_DIR}") {
                    // Example push, configure credentials and remote before using
                    sh '''
                        git init
                        git add .
                        git commit -m "Update Node.js workflow output"
                        git remote add origin https://<USERNAME>:<TOKEN>@github.com/<USER>/<REPO>.git
                        git push -u origin main
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
        failure {
            echo 'Pipeline failed!'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
    }
}
