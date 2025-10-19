# 🚀 IntelliAttend - Production Deployment Guide

This guide covers deploying IntelliAttend to production environments.

## 🏗️ Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Server    │    │   Database      │
│   (Nginx/ALB)   │────│   (Frontend)    │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│   API Server    │──────────────┘
                        │   (Backend)     │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │   WebSocket     │
                        │   (Real-time)   │
                        └─────────────────┘
```

## 🌐 Cloud Deployment Options

### Option 1: AWS Deployment

#### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- Docker installed

#### Backend Deployment (AWS EC2 + RDS)

```bash
# 1. Create EC2 instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-12345678 \
  --subnet-id subnet-12345678

# 2. Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier intelliattend-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password your-secure-password \
  --allocated-storage 20

# 3. Deploy backend
scp -r backend/ ec2-user@your-ec2-ip:~/
ssh ec2-user@your-ec2-ip
cd backend
sudo yum update -y
sudo yum install python3 python3-pip -y
pip3 install -r requirements.txt
# Update .env with RDS connection string
python3 run_server.py
```

#### Frontend Deployment (AWS S3 + CloudFront)

```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Create S3 bucket
aws s3 mb s3://intelliattend-frontend

# 3. Upload build files
aws s3 sync build/ s3://intelliattend-frontend --delete

# 4. Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json
```

### Option 2: Google Cloud Platform

#### Backend (Google Cloud Run)

```bash
# 1. Create Dockerfile for backend
cat > backend/Dockerfile << EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "run_server.py"]
EOF

# 2. Build and deploy
cd backend
gcloud builds submit --tag gcr.io/PROJECT_ID/intelliattend-backend
gcloud run deploy intelliattend-backend \
  --image gcr.io/PROJECT_ID/intelliattend-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Frontend (Firebase Hosting)

```bash
# 1. Install Firebase CLI
npm install -g firebase-tools

# 2. Initialize Firebase
cd frontend
firebase init hosting

# 3. Build and deploy
npm run build
firebase deploy
```

### Option 3: DigitalOcean Droplet

```bash
# 1. Create droplet
doctl compute droplet create intelliattend \
  --size s-2vcpu-2gb \
  --image ubuntu-20-04-x64 \
  --region nyc1 \
  --ssh-keys your-ssh-key-id

# 2. Setup server
ssh root@your-droplet-ip
apt update && apt upgrade -y
apt install python3 python3-pip nodejs npm nginx postgresql -y

# 3. Deploy application
git clone https://github.com/yourusername/IntelliAttend.git
cd IntelliAttend
./setup.sh
```

## 🐳 Docker Deployment

### Complete Docker Setup

```bash
# 1. Create docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/intelliattend
    depends_on:
      - db
    volumes:
      - ./backend:/app
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8080/api
    volumes:
      - ./frontend:/app
    
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=intelliattend
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    
  realtime:
    build: ./realtime_presence
    ports:
      - "8765:8765"
    depends_on:
      - backend

volumes:
  postgres_data:
EOF

# 2. Create Dockerfiles
# Backend Dockerfile
cat > backend/Dockerfile << EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "run_server.py"]
EOF

# Frontend Dockerfile
cat > frontend/Dockerfile << EOF
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
EOF

# Real-time Dockerfile
cat > realtime_presence/Dockerfile << EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8765
CMD ["python", "server.py"]
EOF

# 3. Deploy with Docker Compose
docker-compose up -d
```

## 🔒 Production Security Configuration

### Environment Variables

```bash
# Backend production .env
cat > backend/.env << EOF
DATABASE_URL=postgresql://user:secure_password@db_host:5432/intelliattend
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8080
BCRYPT_LOG_ROUNDS=14
SESSION_TIMEOUT_MINUTES=15
EOF

# Frontend production .env
cat > frontend/.env << EOF
REACT_APP_API_BASE_URL=https://api.yourdomain.com/api
REACT_APP_WEBSOCKET_URL=wss://ws.yourdomain.com
REACT_APP_DEBUG=false
GENERATE_SOURCEMAP=false
EOF
```

### SSL/TLS Configuration

```nginx
# Nginx configuration
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📊 Monitoring and Logging

### Application Monitoring

```bash
# Install monitoring tools
pip install prometheus-client
npm install @prometheus/client

# Add health check endpoints
# Backend: /health, /metrics
# Frontend: /health
```

### Log Management

```bash
# Configure log rotation
cat > /etc/logrotate.d/intelliattend << EOF
/var/log/intelliattend/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
EOF
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd frontend && npm install
        cd ../backend && pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd frontend && npm test
        cd ../backend && python -m pytest
    
    - name: Build frontend
      run: |
        cd frontend && npm run build
    
    - name: Deploy to server
      run: |
        # Add your deployment commands here
        echo "Deploying to production..."
```

## 📱 Mobile App Distribution

### Google Play Store

1. **Prepare release build**:
   ```bash
   cd mobile/app
   ./gradlew assembleRelease
   ```

2. **Sign the APK**:
   ```bash
   jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
     -keystore your-release-key.keystore \
     app-release-unsigned.apk alias_name
   ```

3. **Upload to Play Console**

### Enterprise Distribution

```bash
# Build signed APK for enterprise distribution
cd mobile/app
./gradlew assembleRelease

# Host APK on your server
cp app/build/outputs/apk/release/app-release.apk /var/www/html/downloads/
```

## 🔧 Database Migration

### Production Database Setup

```sql
-- Create production database
CREATE DATABASE intelliattend_prod;
CREATE USER intelliattend_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE intelliattend_prod TO intelliattend_user;

-- Run migrations
cd backend
python migrations.py
```

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump intelliattend_prod > /backups/intelliattend_$DATE.sql
aws s3 cp /backups/intelliattend_$DATE.sql s3://your-backup-bucket/

# Add to crontab
0 2 * * * /path/to/backup_script.sh
```

## 🚀 Performance Optimization

### Backend Optimization

```python
# Add caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

# Database connection pooling
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=0)
```

### Frontend Optimization

```bash
# Build optimization
npm run build

# Enable gzip compression in Nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

## 📈 Scaling Considerations

### Horizontal Scaling

- **Load Balancer**: Nginx, AWS ALB, or Google Cloud Load Balancer
- **Multiple Backend Instances**: Use Docker Swarm or Kubernetes
- **Database Clustering**: PostgreSQL with read replicas
- **CDN**: CloudFront, CloudFlare for static assets

### Monitoring

- **Application Performance**: New Relic, DataDog
- **Infrastructure**: Prometheus + Grafana
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)

---

This deployment guide provides multiple options for different environments and scales. Choose the approach that best fits your infrastructure and requirements.