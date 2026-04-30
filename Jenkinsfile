pipeline {
    agent any
    environment {
        GEMINI_API_KEY = credentials('GEMINI_API_KEY')
        DOCKER_IMAGE = "ai-service"
        CONTAINER_NAME = "ai-logic-prod"
        HOST_PORT = "8001"
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Docker Build') {
            steps {
                sh "DOCKER_BUILDKIT=1 docker build -t ${DOCKER_IMAGE}:latest ."
            }
        }
        stage('Deploy') {
            steps {
                script {
                    sh "docker stop ${CONTAINER_NAME} || true"
                    sh "docker rm ${CONTAINER_NAME} || true"

                    sh """
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${HOST_PORT}:8000 \
                        -e GEMINI_API_KEY=${GEMINI_API_KEY} \
                        ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
    }
}