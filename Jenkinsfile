pipeline {
    agent any
    environment {
        OPENAI_API_KEY = credentials('OPENAI_API_KEY')
        DOCKER_IMAGE = "ai-service"
        CONTAINER_NAME = "ai-logic-prod"
        HOST_PORT = "8002"
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Docker Build') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:latest ."
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
                        -e OPENAI_API_KEY=${OPENAI_API_KEY} \
                        ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }
    }
}