# Google Cloud Platform Deployment Guide

This guide will help you deploy your SearXNG API container to Google Cloud Platform using the Google Cloud Console.

## Prerequisites

1. **Google Cloud Account** - You need a Google Cloud account with billing enabled
2. **Google Cloud SDK** - Install the Google Cloud CLI
3. **Docker** - Install Docker on your local machine
4. **Domain Name** (Optional) - For production deployment

## Step 1: Set Up Google Cloud Project

### 1.1 Create a New Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "searxng-api")
5. Click "Create"

### 1.2 Enable Required APIs
1. Go to "APIs & Services" > "Library"
2. Search for and enable these APIs:
   - **Container Registry API**
   - **Cloud Build API**
   - **Compute Engine API**
   - **Cloud Logging API**

### 1.3 Set Up Billing
1. Go to "Billing"
2. Link a billing account to your project
3. Note: This deployment will cost approximately $20-50/month

## Step 2: Configure Local Environment

### 2.1 Install Google Cloud SDK
```bash
# macOS (using Homebrew)
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### 2.2 Authenticate and Configure
```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Configure Docker for GCP
gcloud auth configure-docker
```

## Step 3: Build and Push Container

### 3.1 Build the API Container
```bash
# Build the container
docker build -f Dockerfile.api -t gcr.io/YOUR_PROJECT_ID/searxng-api:latest .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/searxng-api:latest
```

### 3.2 Verify Container Registry
1. Go to Google Cloud Console
2. Navigate to "Container Registry"
3. You should see your `searxng-api` image

## Step 4: Deploy to Compute Engine

### 4.1 Create Compute Engine Instance

#### Option A: Using Google Cloud Console (Recommended)

1. Go to "Compute Engine" > "VM instances"
2. Click "Create Instance"
3. Configure the instance:
   - **Name**: `searxng-api-instance`
   - **Region/Zone**: `us-central1-a` (or your preferred zone)
   - **Machine type**: `e2-medium` (2 vCPU, 4 GB memory)
   - **Boot disk**: 
     - OS: Debian 11
     - Size: 20 GB
   - **Firewall**: Check "Allow HTTP traffic" and "Allow HTTPS traffic"
4. Click "Create"

#### Option B: Using Command Line
```bash
gcloud compute instances create searxng-api-instance \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=debian-11 \
    --image-project=debian-cloud \
    --boot-disk-size=20GB \
    --tags=http-server,https-server
```

### 4.2 Install Docker on the Instance

1. SSH into your instance:
   ```bash
   gcloud compute ssh searxng-api-instance --zone=us-central1-a
   ```

2. Install Docker:
   ```bash
   # Update system
   sudo apt-get update
   
   # Install Docker
   sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
   curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io
   
   # Add user to docker group
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. Install Docker Compose:
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

4. Install Google Cloud SDK:
   ```bash
   echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
   sudo apt-get update && sudo apt-get install -y google-cloud-cli
   
   # Configure Docker for GCP
   gcloud auth configure-docker --quiet
   ```

## Step 5: Deploy the Application

### 5.1 Upload Configuration Files

1. Create the deployment files on your local machine:

**docker-compose.gcp.yaml** (already created)

**Create .env file:**
```bash
cat > .env << EOF
# SearXNG Configuration
SEARXNG_HOSTNAME=YOUR_DOMAIN_OR_IP
SEARXNG_TLS=internal
SEARXNG_UWSGI_WORKERS=4
SEARXNG_UWSGI_THREADS=4

# API Configuration
API_PORT=5001
VERIFY_SSL=false
MAX_RESULTS_LIMIT=50
REQUEST_TIMEOUT=30
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# GCP Configuration
PROJECT_ID=YOUR_PROJECT_ID
EOF
```

2. Upload files to the instance:
```bash
gcloud compute scp --zone=us-central1-a \
    docker-compose.gcp.yaml \
    Caddyfile \
    .env \
    searxng/ \
    searxng-api-instance:~/
```

### 5.2 Deploy the Containers

1. SSH into the instance and deploy:
```bash
gcloud compute ssh searxng-api-instance --zone=us-central1-a
```

2. Set environment variables:
```bash
export PROJECT_ID=YOUR_PROJECT_ID
export SEARXNG_HOSTNAME=YOUR_DOMAIN_OR_IP
```

3. Pull and start containers:
```bash
# Pull the latest API image
docker pull gcr.io/YOUR_PROJECT_ID/searxng-api:latest

# Start all services
docker-compose -f docker-compose.gcp.yaml up -d

# Check status
docker-compose -f docker-compose.gcp.yaml ps
```

## Step 6: Configure Domain and SSL (Optional)

### 6.1 Set Up Domain (if you have one)
1. Point your domain to the instance's external IP
2. Update the `SEARXNG_HOSTNAME` in the `.env` file
3. Restart the containers

### 6.2 Get External IP
```bash
gcloud compute instances describe searxng-api-instance \
    --zone=us-central1-a \
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

## Step 7: Test the Deployment

### 7.1 Test API Endpoints
```bash
# Get the external IP
EXTERNAL_IP=$(gcloud compute instances describe searxng-api-instance --zone=us-central1-a --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

# Test health endpoint
curl "http://$EXTERNAL_IP/api/health"

# Test search endpoint
curl "http://$EXTERNAL_IP/api/search?q=test&mode=general"

# Get available modes
curl "http://$EXTERNAL_IP/api/modes"
```

### 7.2 Access Web Interface
- **SearXNG Web**: `http://EXTERNAL_IP`
- **API Base**: `http://EXTERNAL_IP/api`

## Step 8: Monitoring and Management

### 8.1 View Logs
```bash
# SSH into instance
gcloud compute ssh searxng-api-instance --zone=us-central1-a

# View all logs
docker-compose -f docker-compose.gcp.yaml logs -f

# View specific service logs
docker-compose -f docker-compose.gcp.yaml logs -f api
docker-compose -f docker-compose.gcp.yaml logs -f searxng
```

### 8.2 Manage Services
```bash
# Restart services
docker-compose -f docker-compose.gcp.yaml restart

# Stop services
docker-compose -f docker-compose.gcp.yaml down

# Update and restart
docker pull gcr.io/YOUR_PROJECT_ID/searxng-api:latest
docker-compose -f docker-compose.gcp.yaml up -d
```

### 8.3 Monitor Resources
1. Go to Google Cloud Console
2. Navigate to "Compute Engine" > "VM instances"
3. Click on your instance to see CPU, memory, and network usage

## Step 9: Security and Optimization

### 9.1 Create Firewall Rules
```bash
gcloud compute firewall-rules create allow-searxng-api \
    --allow tcp:80,tcp:443,tcp:4000,tcp:5001 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow SearXNG API traffic"
```

### 9.2 Set Up Monitoring
1. Go to "Monitoring" in Google Cloud Console
2. Create alerts for:
   - High CPU usage
   - High memory usage
   - Disk space
   - Network traffic

### 9.3 Backup Strategy
1. Set up automated snapshots of your instance
2. Consider using Cloud Storage for persistent data
3. Regularly backup your configuration files

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker-compose -f docker-compose.gcp.yaml logs api
   
   # Check if ports are available
   netstat -tulpn | grep :5001
   ```

2. **API not responding**
   ```bash
   # Check if containers are running
   docker ps
   
   # Test internal connectivity
   curl http://localhost:5001/api/health
   ```

3. **Permission issues**
   ```bash
   # Fix Docker permissions
   sudo chmod 666 /var/run/docker.sock
   ```

4. **Out of disk space**
   ```bash
   # Clean up Docker
   docker system prune -a
   ```

### Getting Help

1. Check Google Cloud Console logs
2. Review Docker container logs
3. Verify firewall rules
4. Check instance resource usage

## Cost Estimation

- **Compute Engine (e2-medium)**: ~$25/month
- **Container Registry**: ~$5/month (for storage)
- **Network**: ~$5-10/month
- **Total**: ~$35-40/month

## Next Steps

1. Set up automated deployments using Cloud Build
2. Configure custom domain with SSL
3. Set up monitoring and alerting
4. Implement backup strategies
5. Consider using Cloud Run for serverless deployment

## Useful Commands

```bash
# Quick status check
gcloud compute ssh searxng-api-instance --zone=us-central1-a --command='docker-compose -f docker-compose.gcp.yaml ps'

# View recent logs
gcloud compute ssh searxng-api-instance --zone=us-central1-a --command='docker-compose -f docker-compose.gcp.yaml logs --tail=50'

# Restart services
gcloud compute ssh searxng-api-instance --zone=us-central1-a --command='docker-compose -f docker-compose.gcp.yaml restart'

# Get external IP
gcloud compute instances describe searxng-api-instance --zone=us-central1-a --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
``` 