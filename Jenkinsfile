pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Install dependencies') {
            steps { sh 'python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt' }
        }
        stage('Run tests') {
            steps { sh '. venv/bin/activate && pytest -v' }
        }
    }
    post {
        success {
            withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                sh '''
                curl -s -X POST \
                  -H "Authorization: token $GITHUB_TOKEN" \
                  -H "Content-Type: application/json" \
                  https://api.github.com/repos/Vikassinghs624/de-practice-pipeline/statuses/$GIT_COMMIT \
                  -d '{"state":"success","context":"jenkins-ci-build","description":"CI build passed"}'
                '''
            }
        }
        failure {
            withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
                sh '''
                curl -s -X POST \
                  -H "Authorization: token $GITHUB_TOKEN" \
                  -H "Content-Type: application/json" \
                  https://api.github.com/repos/Vikassinghs624/de-practice-pipeline/statuses/$GIT_COMMIT \
                  -d '{"state":"failure","context":"jenkins-ci-build","description":"CI build failed"}'
                '''
            }
        }
    }
}
