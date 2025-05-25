pipeline {
    agent any

    environment {
        APP_NAME = 'pii-redaction-service'
        DOCKER_REGISTRY = 'your-docker-registry'
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/${APP_NAME}"
        GIT_BRANCH = env.BRANCH_NAME ?: 'main'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                script {
                    // Create virtual environment and install dependencies
                    sh '''
                    python -m venv venv
                    source venv/bin/activate
                    pip install -r requirements.txt
                    
                    # Run tests with coverage
                    pytest -v tests/ --cov=.
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker image with version tag
                    def version = sh(script: 'git describe --tags --always', returnStdout: true).trim()
                    def imageTag = "${DOCKER_IMAGE}:${version}-${GIT_BRANCH}"
                    
                    sh "docker build -t ${imageTag} ."
                    
                    // Tag with latest for main branch
                    if (env.BRANCH_NAME == 'main') {
                        sh "docker tag ${imageTag} ${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Push to Docker registry
                    def version = sh(script: 'git describe --tags --always', returnStdout: true).trim()
                    def imageTag = "${DOCKER_IMAGE}:${version}-${GIT_BRANCH}"
                    
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'docker-registry-credentials',
                            usernameVariable: 'DOCKER_USERNAME',
                            passwordVariable: 'DOCKER_PASSWORD'
                        )
                    ]) {
                        sh """
                        docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD} ${DOCKER_REGISTRY}
                        docker push ${imageTag}
                        
                        if [ "${env.BRANCH_NAME}" = "main" ]; then
                            docker push ${DOCKER_IMAGE}:latest
                        fi
                        """
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Deploy to Kubernetes
                    withCredentials([
                        string(credentialsId: 'k8s-namespace', variable: 'NAMESPACE'),
                        string(credentialsId: 'k8s-context', variable: 'CONTEXT')
                    ]) {
                        sh """
                        kubectl config use-context ${CONTEXT}
                        kubectl apply -f k8s/deployment.yaml -n ${NAMESPACE}
                        kubectl apply -f k8s/service.yaml -n ${NAMESPACE}
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
        }
        failure {
            mail to: 'devops@yourcompany.com',
                 subject: "Failed Pipeline: ${env.JOB_NAME}",
                 body: "Something is wrong with ${env.BUILD_URL}"
        }
    }
}
