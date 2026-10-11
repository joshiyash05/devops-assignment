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

        stage('Deploy') {
            steps {
                echo 'Deploying ACEest Fitness API'
                sh '''
                    set -eu

                    DEPLOY_DIR=/tmp/aceest-fitness-api
                    mkdir -p "$DEPLOY_DIR/aceest"
                    cp app.py requirements.txt "$DEPLOY_DIR/"
                    cp -r aceest/. "$DEPLOY_DIR/aceest/"

                    cd "$DEPLOY_DIR"
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt

                    if [ -f app.pid ]; then
                        old_pid=$(cat app.pid)
                        if ps -p "$old_pid" -o args= | grep -Fq "$DEPLOY_DIR/.venv/bin/python $DEPLOY_DIR/app.py"; then
                            kill "$old_pid"
                            attempt=0
                            while kill -0 "$old_pid" 2>/dev/null && [ "$attempt" -lt 10 ]; do
                                sleep 1
                                attempt=$((attempt + 1))
                            done
                            if kill -0 "$old_pid" 2>/dev/null; then
                                echo "Previous ACEest API process $old_pid did not stop." >&2
                                exit 1
                            fi
                        fi
                        rm -f app.pid
                    fi

                    nohup "$DEPLOY_DIR/.venv/bin/python" "$DEPLOY_DIR/app.py" \
                        > app.log 2>&1 < /dev/null &
                    app_pid=$!
                    echo "$app_pid" > app.pid

                    attempt=0
                    until curl --fail --silent http://127.0.0.1:5000/health >/dev/null; do
                        if ! kill -0 "$app_pid" 2>/dev/null; then
                            cat app.log
                            echo "ACEest API process exited before becoming healthy." >&2
                            exit 1
                        fi
                        if [ "$attempt" -ge 10 ]; then
                            cat app.log
                            echo "ACEest API health check failed at http://127.0.0.1:5000/health." >&2
                            exit 1
                        fi
                        sleep 1
                        attempt=$((attempt + 1))
                    done

                    echo "ACEest Fitness API is healthy at http://127.0.0.1:5000."
                '''
            }
        }
    }

    post {
        always {
            cleanWs(deleteDirs: true)
        }
    }
}
