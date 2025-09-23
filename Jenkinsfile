pipeline {
    agent any

    environment {
        CPLUS_REPO = 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git'
        PYTHON_REPO = 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
        NODEJS_REPO = 'https://github.com/Mrityunjai-demo/NodeJS_Output.git'
        GITHUB_CREDS = 'github-creds'  // Jenkins credential ID
    }

    stages {
        stage('Checkout Python Workflow') {
            steps {
                git branch: 'main', url: "${PYTHON_REPO}"
            }
        }

        stage('Clone C++ Repo') {
            steps {
                dir('cpp_code') {
                    git branch: 'main', url: "${CPLUS_REPO}", credentialsId: "${GITHUB_CREDS}"
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                    # Run your CbN Python workflow
                    python3 run_cbn_workflow.py --input cpp_code --output nodejs_output
                '''
            }
        }

        stage('Push Node.js Output to GitHub') {
            steps {
                dir('nodejs_output') {
                    withCredentials([usernamePassword(credentialsId: "${GITHUB_CREDS}", usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {
                        sh '''
                            git init
                            git remote add origin https://${GIT_USER}:${GIT_PASS}@github.com/Mrityunjai-demo/NodeJS_Output.git
                            git add .
                            git commit -m "Update Node.js output from CbN workflow"
                            git push -u origin main --force
                        '''
                    }
                }
            }
        }
    }
}
