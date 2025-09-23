pipeline {
    agent any

    environment {
        WORKSPACE_DIR   = "${env.WORKSPACE}"
        PYTHON_PATH     = "${env.WORKSPACE}/CBN_Workflow_PY"
        NODE_OUTPUT_DIR = "${env.WORKSPACE}/nodejs_output"
    }

    stages {
        stage('Checkout Repositories') {
            parallel {
                stage('Python Workflow') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            checkout([$class: 'GitSCM',
                                branches: [[name: 'main']],
                                userRemoteConfigs: [[url: 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git']]
                            ])
                        }
                    }
                }

                stage('C++ Code') {
                    steps {
                        dir('cpp_code') {
                            checkout([$class: 'GitSCM',
                                branches: [[name: 'main']],
                                userRemoteConfigs: [[url: 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git']]
                            ])
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
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        else
                            pip install requests
                        fi
                    '''
                }
            }
        }

        stage('Verify cbn_config.py') {
            steps {
                dir('CBN_Workflow_PY') {
                    script {
                        if (!fileExists('cbn_config.py')) {
                            error "❌ ERROR: cbn_config.py not found in CBN_Workflow_PY repo!"
                        } else {
                            echo "✅ cbn_config.py exists, continuing..."
                        }
                    }
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir('CBN_Workflow_PY') {
                    withCredentials([string(credentialsId: 'CBN_PASSWORD', variable: 'CBN_PASSWORD')]) {
                        sh '''
                            . venv/bin/activate
                            mkdir -p ${NODE_OUTPUT_DIR}
                            export PYTHONPATH=${PYTHON_PATH}

                            # Export secret into runtime environment
                            export CBN_PASSWORD=${CBN_PASSWORD}

                            echo "🔑 CBN_PASSWORD injected into environment."
                            python3 run_cbn_workflow.py cpp
                        '''
                    }
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            when {
                expression { return fileExists("${NODE_OUTPUT_DIR}") }
            }
            steps {
                echo "📦 Node.js output ready — implement push to GitHub here."
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
        success {
            echo "✅ Pipeline completed successfully!"
        }
    }
}
