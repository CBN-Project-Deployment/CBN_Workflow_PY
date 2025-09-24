pipeline {
    agent any

    environment {
        CBN_PASSWORD = credentials('cbn-password')
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
                            git 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
                        }
                    }
                }
                stage('C++ Code') {
                    steps {
                        dir('cpp_code') {
                            git 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git'
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
                dir('CBN_Workflow_PY') {
                    script {
                        if (!fileExists('cbn_config.py')) {
                            error "❌ cbn_config.py not found!"
                        }
                        echo "✅ cbn_config.py exists, continuing..."
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
                        cp ../cpp_code/*.cpp input_files/cpp/
                    '''
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (fileExists('run_cbn_workflow.py')) {
                            echo "Running Python workflow: run_cbn_workflow.py"
                            sh '''
                                . venv/bin/activate
                                python3 run_cbn_workflow.py cpp
                            '''
                        } else {
                            error "❌ run_cbn_workflow.py not found!"
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
