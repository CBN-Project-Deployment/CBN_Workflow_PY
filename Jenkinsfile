pipeline {
    agent any

    environment {
        PYTHON_VENV = "${WORKSPACE}/CBN_Workflow_PY/venv"
        INPUT_DIR = "${WORKSPACE}/CBN_Workflow_PY/input_files"  // <-- define INPUT_DIR
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Checkout Repositories') {
            parallel {
                stage('Python Workflow') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            git url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git', branch: 'main'
                        }
                    }
                }

                stage('C++ Code') {
                    steps {
                        dir('cpp_code') {
                            git url: 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git', branch: 'main'
                        }
                    }
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh """
                        rm -rf venv
                        python3 -m venv venv
                        . venv/bin/activate
                        python3 -m pip install --upgrade pip
                        pip install requests
                    """
                }
            }
        }

        stage('Verify cbn_config.py') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (!fileExists('cbn_config.py')) {
                            error "cbn_config.py does not exist!"
                        } else {
                            echo " cbn_config.py exists, continuing..."
                        }
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh """
                        mkdir -p ${INPUT_DIR}/cpp
                        mkdir -p ${INPUT_DIR}/stored_procedure

                        # Copy C++ files into input directory
                        cp ../cpp_code/*.cpp ${INPUT_DIR}/cpp/ || echo "No cpp files found"
                    """
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                withCredentials([string(credentialsId: 'CBN_PASSWORD', variable: 'CBN_PASSWORD')]) {
                    dir('CBN_Workflow_PY') {
                        sh """
                            . venv/bin/activate
                            export PYTHONPATH=${WORKSPACE}/CBN_Workflow_PY
                            echo " CBN_PASSWORD injected into environment."
                            python3 run_cbn_workflow.py cpp
                        """
                    }
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            when {
                expression { return false } // skip if workflow fails
            }
            steps {
                echo "This stage will be skipped due to earlier failures."
            }
        }
    }

    post {
        always {
            echo " Cleaning worksp"
            cleanWs()
        }
        failure {
            echo "Pipeline failed!"
        }
    }
}
