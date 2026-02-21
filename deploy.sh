#!/bin/bash

# My Adventures - Docker + Jenkins Deployment Script
# This script sets up the complete CI/CD pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
JENKINS_URL="http://localhost:8081/jenkins"
PROJECT_NAME="my-adventures"
IMAGE_NAME="my-adventures"
CONTAINER_PREFIX="my-adventures"

echo -e "${BLUE}🚀 My Adventures - Docker + Jenkins Deployment${NC}"
echo "=================================================="

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
check_docker() {
    echo "Checking Docker installation..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_status "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    echo "Checking Docker Compose..."
    if ! docker-compose version > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    print_status "Docker Compose is available"
}

# Build Jenkins image
build_jenkins() {
    echo "Building Jenkins image..."
    docker build -f jenkins/Dockerfile.jenkins -t ${PROJECT_NAME}-jenkins .
    print_status "Jenkins image built successfully"
}

# Start Jenkins and supporting services
start_jenkins() {
    echo "Starting Jenkins and supporting services..."
    docker-compose -f docker-compose.jenkins.yml up -d jenkins nginx-proxy
    print_status "Jenkins services started"
    
    # Wait for Jenkins to be ready
    echo "Waiting for Jenkins to be ready..."
    sleep 30
    
    # Get initial admin password
    echo "Getting Jenkins initial admin password..."
    JENKINS_PASSWORD=$(docker exec ${CONTAINER_PREFIX}-jenkins cat /var/jenkins_home/secrets/initialAdminPassword)
    echo -e "${BLUE}Jenkins Initial Admin Password: ${JENKINS_PASSWORD}${NC}"
    echo -e "${BLUE}Jenkins URL: ${JENKINS_URL}${NC}"
}

# Setup Jenkins with plugins and credentials
setup_jenkins() {
    echo "Setting up Jenkins configuration..."
    
    # Wait for Jenkins to be fully ready
    until curl -s ${JENKINS_URL} > /dev/null; do
        echo "Waiting for Jenkins to be ready..."
        sleep 10
    done
    
    print_status "Jenkins is ready for configuration"
    
    # Note: In a real setup, you would use Jenkins CLI or REST API to configure
    # For now, we'll provide instructions
    echo ""
    echo "Please complete Jenkins setup manually:"
    echo "1. Open ${JENKINS_URL} in your browser"
    echo "2. Use the initial admin password: ${JENKINS_PASSWORD}"
    echo "3. Install suggested plugins"
    echo "4. Create admin user"
    echo "5. Configure Jenkins URL"
    echo ""
    echo "After setup, you can:"
    echo "- Create a new pipeline job"
    echo "- Use the Jenkinsfile from jenkins/jenkins.yaml"
    echo "- Configure Docker credentials if needed"
}

# Build and test application
build_and_test() {
    echo "Building and testing application..."
    
    # Build main application
    echo "Building application image..."
    docker build -f Dockerfile -t ${IMAGE_NAME}:latest .
    print_status "Application image built"
    
    # Build test image
    echo "Building test image..."
    docker build -f Dockerfile.selenium -t ${IMAGE_NAME}-tests:latest .
    print_status "Test image built"
    
    # Run tests
    echo "Running tests..."
    docker run --rm --network=host -e BASE_URL=http://localhost:9090 ${IMAGE_NAME}-tests:latest
    print_status "Tests completed"
}

# Deploy to staging
deploy_staging() {
    echo "Deploying to staging environment..."
    docker-compose -f docker-compose.jenkins.yml up -d --profile staging
    print_status "Staging environment deployed"
    echo -e "${BLUE}Staging URL: http://localhost:9090${NC}"
}

# Deploy to production
deploy_production() {
    echo "Deploying to production environment..."
    docker-compose -f docker-compose.jenkins.yml up -d --profile production
    print_status "Production environment deployed"
    echo -e "${BLUE}Production URL: http://localhost:9091${NC}"
}

# Create Jenkins job
create_jenkins_job() {
    echo "Creating Jenkins pipeline job..."
    
    # Create job configuration
    cat > jenkins-job-config.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1183.v73d5b_8a_a_b_74b_">
  <actions/>
  <description>My Adventures CI/CD Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <com.cloudbees.plugins.credentials.ViewCredentialsAction_-DescriptorImpl>
      <useOwnerCredentials>false</useOwnerCredentials>
    </com.cloudbees.plugins.credentials.ViewCredentialsAction_-DescriptorImpl>
    <org.jenkinsci.plugins.workflow.job.properties.DisableConcurrentBuildsJobProperty/>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2636.v25e1492f3f1c">
    <script>
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'your-registry.com'
        IMAGE_NAME = 'my-adventures'
        IMAGE_TAG = "${BUILD_NUMBER}"
        CONTAINER_NAME = 'my-adventures-web'
        TEST_CONTAINER_NAME = 'my-adventures-tests'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Application') {
            steps {
                script {
                    echo 'Building Docker image...'
                    sh """
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -f Dockerfile .
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                    """
                }
            }
        }
        
        stage('Run Tests') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        script {
                            echo 'Running unit tests...'
                            sh """
                                docker build -t ${TEST_CONTAINER_NAME}:${IMAGE_TAG} -f Dockerfile.selenium .
                                docker run --rm --network=host -e BASE_URL=http://localhost:9090 ${TEST_CONTAINER_NAME}:${IMAGE_TAG}
                            """
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        script {
                            echo 'Running security scan...'
                            sh """
                                docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                                    -v $(pwd):/src aquasec/trivy image ${IMAGE_NAME}:${IMAGE_TAG}
                            """
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            steps {
                script {
                    echo 'Deploying to staging environment...'
                    sh """
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true
                        docker run -d --name ${CONTAINER_NAME} -p 9090:80 ${IMAGE_NAME}:${IMAGE_TAG}
                    """
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                script {
                    echo 'Running integration tests...'
                    sh """
                        sleep 10  # Wait for container to start
                        docker run --rm --network=host -e BASE_URL=http://localhost:9090 ${TEST_CONTAINER_NAME}:${IMAGE_TAG}
                    """
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo 'Deploying to production...'
                    sh """
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest
                        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest
                    """
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo 'Cleaning up Docker containers...'
                sh """
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true
                    docker rmi ${TEST_CONTAINER_NAME}:${IMAGE_TAG} || true
                """
            }
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
    </script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF
    
    print_status "Jenkins job configuration created"
    echo "To create the job in Jenkins:"
    echo "1. Go to Jenkins dashboard"
    echo "2. Click 'New Item'"
    echo "3. Enter job name: my-adventures-pipeline"
    echo "4. Select 'Pipeline' and click 'OK'"
    echo "5. In the Pipeline section, select 'Pipeline script from SCM'"
    echo "6. Set SCM to Git and repository URL to your project"
    echo "7. Set Script Path to: jenkins/jenkins.yaml"
    echo "8. Click 'Save'"
}

# Show status
show_status() {
    echo ""
    echo "=================================================="
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo "=================================================="
    echo ""
    echo "📋 Services Status:"
    docker-compose -f docker-compose.jenkins.yml ps
    echo ""
    echo "🌐 URLs:"
    echo -e "  Jenkins:        ${BLUE}${JENKINS_URL}${NC}"
    echo -e "  Staging:        ${BLUE}http://localhost:9090${NC}"
    echo -e "  Production:     ${BLUE}http://localhost:9091${NC}"
    echo ""
    echo "🔧 Next Steps:"
    echo "  1. Complete Jenkins setup in browser"
    echo "  2. Create pipeline job using jenkins/jenkins.yaml"
    echo "  3. Configure webhooks for automatic builds"
    echo "  4. Set up Docker registry credentials if needed"
    echo ""
    echo "📝 Commands:"
    echo "  View Jenkins logs: docker logs ${CONTAINER_PREFIX}-jenkins"
    echo "  Stop all services: docker-compose -f docker-compose.jenkins.yml down"
    echo "  Start staging only: docker-compose -f docker-compose.jenkins.yml up -d --profile staging"
    echo "  Start production only: docker-compose -f docker-compose.jenkins.yml up -d --profile production"
}

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    docker-compose -f docker-compose.jenkins.yml down
    docker rmi ${PROJECT_NAME}-jenkins 2>/dev/null || true
    docker rmi ${IMAGE_NAME}:latest 2>/dev/null || true
    docker rmi ${IMAGE_NAME}-tests:latest 2>/dev/null || true
    print_status "Cleanup completed"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            check_docker
            check_docker_compose
            build_jenkins
            start_jenkins
            setup_jenkins
            build_and_test
            deploy_staging
            deploy_production
            create_jenkins_job
            show_status
            ;;
        "build")
            check_docker
            build_jenkins
            build_and_test
            ;;
        "start")
            check_docker
            check_docker_compose
            docker-compose -f docker-compose.jenkins.yml up -d
            ;;
        "stop")
            check_docker
            check_docker_compose
            docker-compose -f docker-compose.jenkins.yml down
            ;;
        "staging")
            check_docker
            check_docker_compose
            deploy_staging
            ;;
        "production")
            check_docker
            check_docker_compose
            deploy_production
            ;;
        "cleanup")
            cleanup
            ;;
        "logs")
            docker-compose -f docker-compose.jenkins.yml logs -f
            ;;
        *)
            echo "Usage: $0 {deploy|build|start|stop|staging|production|cleanup|logs}"
            echo ""
            echo "Commands:"
            echo "  deploy      - Full deployment (default)"
            echo "  build       - Build Jenkins and test application"
            echo "  start       - Start all services"
            echo "  stop        - Stop all services"
            echo "  staging     - Deploy to staging environment"
            echo "  production  - Deploy to production environment"
            echo "  cleanup     - Remove all containers and images"
            echo "  logs        - Show service logs"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"