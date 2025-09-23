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
                            echo "✅ cbn_config.py exists, continuing..."
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
                        // Check if Python workflow script exists
                        def workflowScript = ''
                        if (fileExists('run_cbn.py')) {
                            workflowScript = 'run_cbn.py'
                        } else if (fileExists('cbn_workflow.py')) {
                            workflowScript = 'cbn_workflow.py'
                        } else {
                            error "No Python workflow script found!"
                        }

                        echo "Running Python workflow: ${workflowScript}"
                        sh """
                            . venv/bin/activate
                            python3 ${workflowScript} input_files/cpp
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}
