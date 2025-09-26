pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        // Inject your CBN_PASSWORD from Jenkins Credentials (Secret Text)
        CBN_PASSWORD = credentials('CBN_PASSWORD_CREDENTIAL_ID')
    }

    stages {
        // stage('Checkout SCM') {
        //     steps {
        //         checkout scm
        //     }
        // }

        // stage('Checkout Repositories') {
        //     parallel {
                stage('cbn-devops-code') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            git url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git', branch: 'main'
                        }
                    }
                }

                stage('source-app-code') {
                    steps {
                        dir('source_code') {
                            git url: 'https://github.com/ChrisMaunder/MFC-GridCtrl.git', branch: 'master'
                        }
                    }
                }
            }
        // }

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

        stage('Verify files availability') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (!fileExists('cbn_config.py'))
                        {
                            error "❌ cbn_config.py not present."
                            failure {
                                echo "❌ Stopping process as file not found."
                            }
                        } 
                        else if !fileExists('run_cbn_workflow.py')
                        {
                            error "❌ run_cbn_workflow.py not present."
                            failure {
                                echo "❌ Stopping process as file not found."
                            }
                        } 
                        else
                        {
                            echo "✅ all .py files exist, continuing..."
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
                        touch input_files/cpp/merged.cpp
                        cat ../cpp_code/GridCtrl.h \
                            ../cpp_code/GridCtrl.h.cpp \
                            ../cpp_code/CellRange.h \
                            ../cpp_code/GridCell.h \
                            ../cpp_code/GridCell.cpp \
                            ../cpp_code/GridCellBase.h \
                            ../cpp_code/GridCellBase.cpp \
                            ../cpp_code/GridDropTarget.h \
                            ../cpp_code/GridDropTarget.cpp \
                            ../cpp_code/InPlaceEdit.h \
                            ../cpp_code/InPlaceEdit.cpp \
                            ../cpp_code/MemDC.h \
                            ../cpp_code/Titletip.h \
                            ../cpp_code/Titletip.cpp >> input_files/cpp/merged.cpp
                    '''
                }
            }
        }

        stage('Run CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (!fileExists('run_cbn_workflow.py')) {
                            error "❌ run_cbn_workflow.py not found!"
                            failure {
                                echo "❌ Stopping process as file not found."
                            }
                        } else {
                            echo "Running CbN workflow to convert c++ code into js code..."
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
