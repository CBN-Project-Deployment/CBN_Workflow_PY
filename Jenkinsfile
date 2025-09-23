pipeline {
    agent any

    environment {
        WORKSPACE_PY = "${env.WORKSPACE}/CBN_Workflow_PY"
        WORKSPACE_CPP = "${env.WORKSPACE}/cpp_code"
        OUTPUT_DIR = "${env.WORKSPACE}/nodejs_output"
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
                    git(
                        branch: 'main',
                        url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
                    )
                }
            }
        }

        stage('Clone C++ Repository') {
            steps {
                dir("${WORKSPACE_CPP}") {
                    git(
                        branch: 'main',
                        url: 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git'
                    )
                }
            }
        }

        stage('Setup Python Environment & Install Dependencies') {
            steps {
                dir("${WORKSPACE_PY}") {
                    sh '''
                        rm -rf venv
                        python3 -m venv venv
                        . venv/bin/activate
                        python3 -m pip install --upgrade pip
                        pip install -r requirements.txt || true
                        pip install requests
                    '''
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir("${WORKSPACE_PY}") {
                    sh '''
                        mkdir -p ${OUTPUT_DIR}
                        . venv/bin/activate
                        export PYTHONPATH=$(pwd)
                        python3 run_cbn_workflow.py --input ${WORKSPACE_CPP} --output ${OUTPUT_DIR}
                    '''
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            steps {
                dir("${OUTPUT_DIR}") {
                    sh '''
                        git init
                        git remote add origin https://github.com/Mrityunjai-demo/CBN_Workflow_NodeJS_Output.git
                        git add .
                        git commit -m "Update Node.js output"
                        git push -u origin main --force
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
