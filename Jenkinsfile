pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
    }

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        LOCAL_IMAGE = 'aceest-fitness-api'
        DOCKERHUB_REPOSITORY = 'aceest-fitness-api'
        SONARQUBE_SERVER = 'SonarQube'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Version') {
            steps {
                script {
                    def gitTag = sh(
                        script: 'git describe --tags --exact-match HEAD 2>/dev/null || true',
                        returnStdout: true
                    ).trim()
                    def shortCommit = sh(
                        script: 'git rev-parse --short=7 HEAD',
                        returnStdout: true
                    ).trim()

                    if (gitTag && !(gitTag ==~ /^v\d+\.\d+\.\d+$/)) {
                        error("Release tag '${gitTag}' must use the vMAJOR.MINOR.PATCH format.")
                    }

                    env.IMAGE_TAG = gitTag ?: "sha-${shortCommit}"
                    env.LOCAL_IMAGE_VERSIONED = "${env.LOCAL_IMAGE}:${env.IMAGE_TAG}"
                }
                echo "Building image version ${IMAGE_TAG}"
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

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t "$LOCAL_IMAGE_VERSIONED" .'
            }
        }

        stage('Containerized Tests') {
            steps {
                sh 'docker run --rm "$LOCAL_IMAGE_VERSIONED" python -m pytest'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_SERVER}") {
                    sh '''
                        export PATH=/opt/sonar-scanner/bin:$PATH
                        sonar-scanner
                    '''
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Publish to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_PASSWORD'
                    )
                ]) {
                    sh '''
                        set -eu
                        export DOCKER_CONFIG="$WORKSPACE/.docker"
                        trap 'docker logout >/dev/null 2>&1 || true' EXIT
                        registry_image="${DOCKERHUB_USERNAME}/${DOCKERHUB_REPOSITORY}:${IMAGE_TAG}"
                        echo "$DOCKERHUB_PASSWORD" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
                        docker tag "$LOCAL_IMAGE_VERSIONED" "$registry_image"
                        docker push "$registry_image"
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_PASSWORD'
                    ),
                    file(
                        credentialsId: 'kubeconfig',
                        variable: 'KUBECONFIG'
                    )
                ]) {
                    script {
                        try {
                            sh '''
                                set -eu
                                kubectl apply -f k8s/base/namespace.yaml
                                kubectl apply -f k8s/base/deployment.yaml -f k8s/base/service.yaml
                                kubectl -n aceest set image deployment/aceest-api \
                                    aceest-api="docker.io/${DOCKERHUB_USERNAME}/${DOCKERHUB_REPOSITORY}:${IMAGE_TAG}"
                                kubectl -n aceest rollout status deployment/aceest-api --timeout=180s
                            '''
                        } catch (err) {
                            def rollbackStatus = sh(
                                script: 'kubectl -n aceest rollout undo deployment/aceest-api',
                                returnStatus: true
                            )
                            if (rollbackStatus != 0) {
                                echo 'Kubernetes rollout failed, and automatic rollback also failed; inspect the cluster before retrying.'
                            } else {
                                echo 'Kubernetes rollout failed; the previous Deployment revision was restored.'
                            }
                            throw err
                        }
                    }
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
