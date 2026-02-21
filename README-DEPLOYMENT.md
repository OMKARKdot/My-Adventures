# My Adventures - Docker + Jenkins Deployment Guide

This guide provides complete instructions for deploying the My Adventures waterpark website using Docker and Jenkins for CI/CD.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                           │
├─────────────────────────────────────────────────────────────┤
│  GitHub/GitLab → Jenkins → Docker → Nginx → Website         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Git       │  │   Jenkins   │  │   Docker Containers │  │
│  │  Repository │  │             │  │                     │  │
│  │             │  │  • Build    │  │  • Web App (nginx)  │  │
│  │  • Code     │  │  • Test     │  │  • Jenkins          │  │
│  │  • Tests    │  │  • Deploy   │  │  • Tests            │  │
│  │  • Configs  │  │  • Monitor  │  │  • Proxy (nginx)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git** (for source code management)
- **8GB+ RAM** (recommended for Jenkins)
- **4GB+ Disk Space**

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone your project repository
git clone <your-repo-url>
cd <your-project-directory>

# Make deployment script executable
chmod +x deploy.sh
```

### 2. One-Command Deployment

```bash
# Full deployment (recommended for first time)
./deploy.sh deploy
```

This will:
- ✅ Build Jenkins Docker image
- ✅ Start Jenkins server and proxy
- ✅ Build application and test images
- ✅ Run comprehensive test suite
- ✅ Deploy to staging environment
- ✅ Deploy to production environment
- ✅ Create Jenkins pipeline job

### 3. Access Services

After deployment:

- **Jenkins Dashboard**: http://localhost:8080/jenkins
- **Staging Environment**: http://localhost:9090
- **Production Environment**: http://localhost:9091

## 🔧 Manual Deployment Steps

### Step 1: Build Jenkins

```bash
# Build Jenkins with Docker support
./deploy.sh build
```

### Step 2: Start Services

```bash
# Start Jenkins and proxy
./deploy.sh start
```

### Step 3: Complete Jenkins Setup

1. Open http://localhost:8080/jenkins in your browser
2. Use the initial admin password (shown in terminal)
3. Install suggested plugins
4. Create admin user
5. Configure Jenkins URL

### Step 4: Create Pipeline Job

1. Go to Jenkins Dashboard
2. Click "New Item"
3. Enter job name: `my-adventures-pipeline`
4. Select "Pipeline" and click "OK"
5. In Pipeline section:
   - Select "Pipeline script from SCM"
   - Set SCM to "Git"
   - Repository URL: your project repository
   - Script Path: `jenkins/jenkins.yaml`
6. Click "Save"

### Step 5: Deploy Environments

```bash
# Deploy to staging
./deploy.sh staging

# Deploy to production
./deploy.sh production
```

## 📁 Project Structure

```
my-adventures/
├── 🐳 Docker Files
│   ├── Dockerfile              # Main application (nginx)
│   ├── Dockerfile.selenium     # Test environment
│   ├── docker-compose.jenkins.yml  # Jenkins + Services
│   └── docker-compose.test.yml     # Test orchestration
│
├── 🔧 Jenkins Configuration
│   ├── jenkins/
│   │   ├── Dockerfile.jenkins  # Jenkins with Docker support
│   │   └── jenkins.yaml        # Pipeline configuration
│   └── jenkins-job-config.xml  # Job configuration
│
├── 🚀 Deployment
│   ├── deploy.sh               # Main deployment script
│   ├── README-DEPLOYMENT.md    # This file
│   └── nginx.conf              # Nginx configuration
│
├── 🧪 Testing
│   ├── test.py                 # Selenium test suite (36 tests)
│   ├── requirements.txt        # Python dependencies
│   └── SELENIUM_TESTING.md     # Test documentation
│
└── 🌐 Application
    ├── index.html              # Main website
    ├── login.html              # Login page
    ├── booking.html            # Booking page
    ├── payment.html            # Payment page
    ├── blog.html               # Blog page
    ├── portfolio.html          # Portfolio page
    └── contact.html            # Contact page
```

## 🔄 CI/CD Pipeline Stages

### 1. **Checkout**
- Pull latest code from repository
- Verify source code integrity

### 2. **Build Application**
- Build Docker image from `Dockerfile`
- Tag with build number and `latest`

### 3. **Run Tests** (Parallel)
- **Unit Tests**: Selenium test suite (36 comprehensive tests)
- **Security Scan**: Trivy vulnerability scanning

### 4. **Deploy to Staging**
- Stop existing container
- Start new container on port 9090
- Deploy to staging environment

### 5. **Integration Tests**
- Run tests against staging environment
- Verify deployment success

### 6. **Deploy to Production** (Main Branch Only)
- Tag image for registry
- Push to Docker registry
- Deploy to production environment

### 7. **Cleanup**
- Remove temporary containers
- Clean up unused images

## 🛠️ Available Commands

```bash
# Full deployment
./deploy.sh deploy

# Individual operations
./deploy.sh build          # Build Jenkins and test
./deploy.sh start          # Start all services
./deploy.sh stop           # Stop all services
./deploy.sh staging        # Deploy to staging
./deploy.sh production     # Deploy to production
./deploy.sh cleanup        # Remove all containers/images
./deploy.sh logs           # Show service logs

# Docker Compose operations
docker-compose -f docker-compose.jenkins.yml up -d
docker-compose -f docker-compose.jenkins.yml down
docker-compose -f docker-compose.jenkins.yml ps
```

## 🔍 Monitoring and Logs

### Jenkins Logs
```bash
# View Jenkins container logs
docker logs my-adventures-jenkins

# Follow logs in real-time
docker logs -f my-adventures-jenkins
```

### Application Logs
```bash
# View web application logs
docker logs my-adventures-staging
docker logs my-adventures-production
```

### System Status
```bash
# Check all container status
docker-compose -f docker-compose.jenkins.yml ps

# View resource usage
docker stats
```

## 🚨 Troubleshooting

### Common Issues

**1. Jenkins Won't Start**
```bash
# Check if port 8080 is available
netstat -an | grep 8080

# Stop conflicting services
sudo systemctl stop apache2  # or other services using port 8080
```

**2. Docker Permission Denied**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in, or restart terminal
```

**3. Tests Failing**
```bash
# Check if website is running
curl http://localhost:9090

# Run tests manually
docker run --rm --network=host -e BASE_URL=http://localhost:9090 my-adventures-tests:latest
```

**4. Jenkins Setup Stuck**
```bash
# Get initial admin password
docker exec my-adventures-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Debug Commands

```bash
# Check Docker daemon status
systemctl status docker

# Verify Docker Compose
docker-compose --version

# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Inspect Jenkins container
docker inspect my-adventures-jenkins
```

## 🔒 Security Considerations

### Jenkins Security
- Change default admin password
- Configure user authentication
- Set up role-based access control
- Enable CSRF protection
- Configure backup strategy

### Docker Security
- Use official base images
- Scan images for vulnerabilities
- Run containers with non-root users
- Limit container resource usage
- Use secrets for sensitive data

### Network Security
- Use HTTPS in production
- Configure firewall rules
- Use VPN for remote access
- Implement rate limiting

## 📊 Performance Optimization

### Jenkins Optimization
```bash
# Increase Jenkins memory
docker run -e JAVA_OPTS="-Xmx2g -Xms1g" ...

# Configure build executors
# (Set in Jenkins → Manage Jenkins → Configure System)
```

### Docker Optimization
```bash
# Use multi-stage builds
# Optimize Dockerfile layers
# Use .dockerignore
# Cache dependencies
```

### Nginx Optimization
```nginx
# Enable gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

# Configure caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🔄 Production Deployment

### Environment Variables
```bash
# Set in Jenkins or deployment script
export DOCKER_REGISTRY=your-registry.com
export IMAGE_NAME=my-adventures
export STAGING_URL=staging.yourdomain.com
export PRODUCTION_URL=yourdomain.com
```

### SSL/HTTPS Setup
```bash
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/nginx.key -out ssl/nginx.crt

# Update nginx.conf for HTTPS
# Restart proxy service
```

### Load Balancing
```yaml
# Add to docker-compose.jenkins.yml
web-production:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '1.0'
        memory: 512M
```

## 📈 Monitoring and Alerting

### Health Checks
```bash
# Add to docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Metrics Collection
- Use Prometheus for metrics
- Grafana for visualization
- AlertManager for notifications
- ELK stack for logging

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📞 Support

For issues and questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [Docker logs](#monitoring-and-logs)
3. Check [Jenkins console output](#monitoring-and-logs)
4. Create [GitHub Issue](https://github.com/your-repo/issues)

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

**Happy Deploying! 🚀🐳🔧**

For more information, see:
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)