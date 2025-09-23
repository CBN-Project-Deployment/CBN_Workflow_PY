pipeline {
    agent any

    environment {
        // Repositories
        PYTHON_REPO = 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
        CPP_REPO    = 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git'
        NODEJS_REPO = 'git@github.com:Mrityunjai-demo/NodeJS_Output.git'
    }

    stages {

        stage('Checkout Repositories') {
            parallel {
                stage('Python Workflow') {
                    steps {
                        dir('CBN_Workflow_PY') {
                            git branch: 'main', url: "${env.PYTHON_REPO}"
                        }
                    }
                }
                stage('C++ Code') {
                    steps {
                        dir('cpp_code') {
                            git branch: 'main', url: "${env.CPP_REPO}"
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
                            error "❌ cbn_config.py not found! Please add it to the repo."
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
                            export PYTHONPATH=$PWD:$PYTHONPATH
                            echo "🔑 CBN_PASSWORD injected into environment."
                            python3 run_cbn_workflow.py cpp
                        '''
                    }
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            steps {
                dir('nodejs_output') {
                    withCredentials([sshUserPrivateKey(credentialsId: 'git-ssh-key', keyFileVariable: 'SSH_KEY')]) {
                        sh '''
                            eval `ssh-agent -s`
                            ssh-add $SSH_KEY
                            git init
                            git remote add origin ${NODEJS_REPO}
                            git checkout -b main || git checkout main
                            git add .
                            git -c user.name="Jenkins" -c user.email="jenkins@example.com" commit -m "Automated commit from Jenkins CbN workflow" || echo "No changes to commit"
                            git push -u origin main
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
    }
}
