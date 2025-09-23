pipeline {
    agent any

    environment {
        PYTHONPATH = "${WORKSPACE}/CBN_Workflow_PY"
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
                        dir("${WORKSPACE}/CBN_Workflow_PY") {
                            git url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git', branch: 'main'
                        }
                    }
                }
                stage('C++ Code') {
                    steps {
                        dir("${WORKSPACE}/cpp_code") {
                            git url: 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git', branch: 'main'
                        }
                    }
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                dir("${WORKSPACE}/CBN_Workflow_PY") {
                    sh '''
                        rm -rf venv
                        python3 -m venv venv
                        . venv/bin/activate
                        python3 -m pip install --upgrade pip
                        pip install requests
                    '''
                }
            }
        }

        stage('Verify cbn_config.py') {
            steps {
                dir("${WORKSPACE}/CBN_Workflow_PY") {
                    script {
                        if (!fileExists('cbn_config.py')) {
                            error "cbn_config.py not found!"
                        } else {
                            echo "cbn_config.py exists, continuing..."
                        }
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir("${WORKSPACE}/CBN_Workflow_PY") {
                    sh '''
                        mkdir -p input_files/cpp
                        mkdir -p input_files/stored_procedure
                        cp ../cpp_code/GridCell.cpp ../cpp_code/GridCellBase.cpp ../cpp_code/GridCtrl.cpp ../cpp_code/GridCtrl_All.cpp ../cpp_code/GridDropTarget.cpp ../cpp_code/InPlaceEdit.cpp ../cpp_code/TitleTip.cpp input_files/cpp/
                    '''
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir("${WORKSPACE}/CBN_Workflow_PY") {
                    script {
                        // Only use credentials if provided
                        def cbnPasswordId = env.CBN_PASSWORD_ID
                        if (cbnPasswordId) {
                            withCredentials([string(credentialsId: cbnPasswordId, variable: 'CBN_PASSWORD')]) {
                                sh ". venv/bin/activate && python3 run_cbn.py input_files/cpp"
                            }
                        } else {
                            echo "No CBN_PASSWORD provided, running without credentials."
                            sh ". venv/bin/activate && python3 run_cbn.py input_files/cpp"
                        }
                    }
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            when {
                expression { false } // skipped for testing without credentials
            }
            steps {
                echo "Skipping push stage in test run."
            }
        }
    }

    post {
        always {
            echo "Cleaning workspa"
            cleanWs()
        }
        success {
            echo "pipeline completed successfully!"
        }
        failure {
            echo "pipeline failed!"
        }
    }
}
