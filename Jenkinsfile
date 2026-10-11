pipeline {
    agent any
    triggers {
        pollSCM('H/2 * * * *')
    }
    environment {
        IMAGE_NAME = 'aceest-fitness-api:jenkins'
        DOCKER_AVAILABLE = 'false'
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

        stage('Check Docker Access') {
            steps {
                script {
                    def dockerStatus = sh(
                        script: 'docker info >/dev/null 2>&1',
                        returnStatus: true
                    )
                    env.DOCKER_AVAILABLE = dockerStatus == 0 ? 'true' : 'false'

                    if (env.DOCKER_AVAILABLE == 'false') {
                        echo 'Docker is not available to the Jenkins user. Skipping Docker build and containerized tests.'
                    }
                }
            }
        }

        stage('Docker Image Assembly') {
            when {
                environment name: 'DOCKER_AVAILABLE', value: 'true'
            }
            steps {
                sh 'docker build -t $IMAGE_NAME .'
            }
        }

        stage('Containerized Tests') {
            when {
                environment name: 'DOCKER_AVAILABLE', value: 'true'
            }
            steps {
                sh 'docker run --rm $IMAGE_NAME python -m pytest'
            }
        }
        stage('Code Inspection') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'sonar-token',
                        variable: 'SONAR_TOKEN'
                    )
                ]) {
                    sh '''
                        export PATH=/opt/sonar-scanner/bin:$PATH
                        sonar-scanner \
                            -Dsonar.host.url=http://localhost:9000 \
                            -Dsonar.token=$SONAR_TOKEN
                    '''
                }
            }
        }
    }

    post {
        always {
            cleanWs(deleteDirs: true)
        }
    }
}
