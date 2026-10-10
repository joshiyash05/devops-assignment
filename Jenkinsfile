pipeline {
    agent any

    environment {
        IMAGE_NAME = 'aceest-fitness-api:jenkins'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Build and Lint') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m compileall app.py aceest tests
                '''
            }
        }

        stage('Automated Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m pytest
                '''
            }
        }

        stage('Docker Image Assembly') {
            steps {
                sh 'docker build -t $IMAGE_NAME .'
            }
        }

        stage('Containerized Tests') {
            steps {
                sh 'docker run --rm $IMAGE_NAME python -m pytest'
            }
        }
    }

    post {
        always {
            cleanWs(deleteDirs: true)
        }
    }
}
