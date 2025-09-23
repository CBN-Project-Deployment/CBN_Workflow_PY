pipeline {
    agent any

    environment {
        PYTHON_ENV = "venv"
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
                            error "cbn_config.py is missing!"
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
                            mkdir -p ../nodejs_output
                            export PYTHONPATH=$(pwd):
                            echo "🔑 CBN_PASSWORD injected into environment."
                            python3 run_cbn_workflow.py cpp
                        '''
                    }
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                echo "Pushing Node.js output... (implement if needed)"
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
