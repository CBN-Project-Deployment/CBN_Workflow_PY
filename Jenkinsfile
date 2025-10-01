pipeline {
  agent any

  options {
    timestamps()
    ansiColor('xterm')
    disableConcurrentBuilds()
  }

  environment {
    PYTHON = 'python3'
    CBN_PASSWORD = credentials('CBN_PASSWORD_CREDENTIAL_ID')
  }

  stages {

    stage('Checkout Repositories') {
      parallel {
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
    }

    stage('Install dependencies') {
      steps {
        sh '''
          python3 -m pip install --upgrade pip
          python3 -m pip install requests
        '''
      }
    }

    stage('Verify files availability') {
      steps {
        dir('CBN_Workflow_PY') {
          script {
            def missing = []
            ['cbn_config.py', 'run_cbn_workflow.py'].each { f ->
              if (!fileExists(f)) { missing << f }
            }
            if (missing) {
              error "❌ Required file(s) missing: ${missing.join(', ')}"
            } else {
              echo "✅ all required .py files exist, continuing..."
            }
          }
        }
      }
    }

    stage('Prepare Input Files') {
      steps {
        sh '''
          set -eu
          mkdir -p CBN_Workflow_PY/input_files/cpp
          : > CBN_Workflow_PY/input_files/cpp/merged.cpp

          # List of expected source files (update if the repo structure differs)
          files=(
            "GridCtrl.h"
            "GridCtrl.cpp"
            "CellRange.h"
            "GridCell.h"
            "GridCell.cpp"
            "GridCellBase.h"
            "GridCellBase.cpp"
            "GridDropTarget.h"
            "GridDropTarget.cpp"
            "InPlaceEdit.h"
            "InPlaceEdit.cpp"
            "MemDC.h"
            "TitleTip.h"
            "TitleTip.cpp"
          )

          # Many of the above live under "GridCtrl" in that repo; try both root and GridCtrl/
          for f in "${files[@]}"; do
            if [ -f "source_code/$f" ]; then
              cat "source_code/$f" >> CBN_Workflow_PY/input_files/cpp/merged.cpp
            elif [ -f "source_code/GridCtrl/$f" ]; then
              cat "source_code/GridCtrl/$f" >> CBN_Workflow_PY/input_files/cpp/merged.cpp
            else
              echo "Missing expected file: $f" >&2
              exit 1
            fi
            echo -e "\n\n" >> CBN_Workflow_PY/input_files/cpp/merged.cpp
          done

          echo "✅ merged.cpp prepared"
        '''
      }
    }

  stage('Run CbN Workflow') {
    steps {
      sh 'python3 run_cbn_workflow.py cpp'
    }
  }

  }

  post {
    success {
      echo "✅ Pipeline succeeded."
      // If your script outputs generated JS into, say, output_js/, archive it:
      // archiveArtifacts artifacts: 'CBN_Workflow_PY/output_js/**', fingerprint: true, onlyIfSuccessful: true
    }
    always {
      echo "🧹 Cleaning workspace..."
      cleanWs()
    }
    failure {
      echo "❌ Pipeline failed!"
    }
  }
}
