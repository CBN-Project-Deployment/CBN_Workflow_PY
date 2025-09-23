pipeline {
    agent any

    environment {
        PYTHON_REPO = 'CBN_Workflow_PY'                     // Python workflow repo folder
        CPP_REPO    = 'cpp_code'                             // C++ repo folder
        NODE_OUTPUT = 'nodejs_output'                        // Output folder for Node.js code
        GITHUB_CPP  = 'https://github.com/Mrityunjai-demo/Gridctrl_src_CplusPlus.git'
        GITHUB_PY   = 'https://github.com/Mrityunjai-demo/CBN_Workflow_PY.git'
        GITHUB_NODE = 'https://github.com/Mrityunjai-demo/NodeJS_Output.git'  // Output repo
        GIT_CREDENTIALS = 'github-creds'                     // Jenkins Git credentials ID
    }

    stages {
        stage('Checkout Python Workflow') {
            steps {
                dir(PYTHON_REPO) {
                    git branch: 'main',
                        url: env.GITHUB_PY,
                        credentialsId: env.GIT_CREDENTIALS
                }
            }
        }

        stage('Clone C++ Repo') {
            steps {
                dir(CPP_REPO) {
                    git branch: 'main',
                        url: env.GITHUB_CPP,
                        credentialsId: env.GIT_CREDENTIALS
                }
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                dir(PYTHON_REPO) {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        fi
                        mkdir -p ../${NODE_OUTPUT}
                        python3 run_cbn_workflow.py --input ../${CPP_REPO} --output ../${NODE_OUTPUT}
                    '''
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            steps {
                dir(NODE_OUTPUT) {
                    sh '''
                        git init
                        git remote add origin ${GITHUB_NODE}
                        git add .
                        git commit -m "Add Node.js output from CbN workflow"
                        git push -u origin main --force
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning workspace...'
            cleanWs()
        }
    }
}
