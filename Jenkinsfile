pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        // Inject your CBN_PASSWORD from Jenkins Credentials (Secret Text)
        CBN_PASSWORD = credentials('CBN_PASSWORD_CREDENTIAL_ID')
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Checkout Repositories') {
            parallel {
                stage('Python Workflow Repo') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            git url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git', branch: 'main'
                        }
                    }
                }

                stage('C++ Code Repo') {
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
                    sh '''
                        rm -rf venv
                        ${PYTHON} -m venv venv
                        . venv/bin/activate
                        ${PYTHON} -m pip install --upgrade pip
                        pip install requests
                    '''
                }
            }
        }

        stage('Verify cbn_config.py') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (!fileExists('cbn_config.py')) {
                            error "❌ cbn_config.py not found!"
                        } else {
                            echo "✅ cbn_config.py exists, continuing..."
                        }
                    }
                }
            }
        }

        stage('Prepare Input Files') {
            steps {
                dir('CBN_Workflow_PY') {
                    sh '''
                        mkdir -p input_files/cpp
                        mkdir -p input_files/stored_procedure
                        cp ../cpp_code/GridCell.cpp \
                           ../cpp_code/GridCellBase.cpp \
                           ../cpp_code/GridCtrl.cpp \
                           ../cpp_code/GridCtrl_All.cpp \
                           ../cpp_code/GridDropTarget.cpp \
                           ../cpp_code/InPlaceEdit.cpp \
                           ../cpp_code/TitleTip.cpp \
                           input_files/cpp/
                    '''
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (!fileExists('run_cbn_workflow.py')) {
                            error "❌ run_cbn_workflow.py not found!"
                        } else {
                            echo "Running Python workflow with real CBN_PASSWORD..."
                            sh '''
                                . venv/bin/activate
                                python3 run_cbn_workflow.py cpp
                            '''
                        }
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
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}
