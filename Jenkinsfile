pipeline {
    agent any

    environment {
        // C++ repo to clone
        CPP_REPO      = 'https://github.com/YourUser/CppRepo.git'
        CPP_DIR       = 'cpp_code'

        // Python workflow repo (already on Jenkins)
        PYTHON_SCRIPT = 'run_cbn_workflow.py'

        // Node.js output repo
        NODE_REPO     = 'https://github.com/YourUser/NodeJsRepo.git'
        NODE_DIR      = 'node_output'

        // GitHub credentials IDs in Jenkins
        GIT_CREDENTIALS = 'github-creds'
    }

    stages {

        stage('Clone C++ Repo') {
            steps {
                // Clean previous run
                deleteDir()
                
                // Clone C++ code
                git branch: 'main', url: "${CPP_REPO}", credentialsId: "${GIT_CREDENTIALS}"
                
                // Move to cpp_code folder
                sh 'mkdir -p ${CPP_DIR} && mv * ${CPP_DIR}/'
            }
        }

        stage('Run Python CbN Workflow') {
            steps {
                script {
                    // Activate Python virtualenv
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        fi
                    '''

                    // Set environment variables if needed
                    sh '''
                        export CBN_INPUT_DIR=${WORKSPACE}/${CPP_DIR}
                        export CBN_OUTPUT_DIR=${WORKSPACE}/node_output
                    '''

                    // Run the Python workflow
                    sh "python ${PYTHON_SCRIPT} datastage"
                }
            }
        }

        stage('Push Node.js Output to GitHub') {
            steps {
                script {
                    // Clone Node.js repo
                    sh """
                        git clone ${NODE_REPO} ${NODE_DIR}
                        rsync -av --exclude='.git' ${WORKSPACE}/node_output/ ${WORKSPACE}/${NODE_DIR}/
                    """

                    // Push updated Node.js code
                    dir("${NODE_DIR}") {
                        sh '''
                            git add .
                            git commit -m "Update Node.js code from CbN workflow"
                            git push origin main
                        '''
                    }
                }
            }
        }
    }
}
