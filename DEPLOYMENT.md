# 🚢 Deployment Guide

This document provides comprehensive deployment instructions for the Drishti AI platform across various environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Nginx Configuration](#nginx-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- OS: Ubuntu 20.04+, Windows Server 2019+, or macOS 11+

**Recommended (Production):**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB+ SSD
- OS: Ubuntu 22.04 LTS

### Software Dependencies

- Docker 24.0+
- Docker Compose 2.0+
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Nginx 1.18+
- Git

## Local Development

### Backend Setup

```bash
# Clone repository
git clone https://github.com/your-org/drishti.git
cd drishti/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python init_db.py

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd drishti/frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env
# Edit .env with backend URL

# Run development server
npm run dev
```

## Docker Deployment

### Quick Start

```bash
# From project root
cd drishti

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Custom Docker Configuration

**Backend Dockerfile:**

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create ChromaDB directory
RUN mkdir -p /app/chroma_db

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

**Docker Compose (Production):**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    container_name: drishti-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-drishti}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-drishti}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U drishti"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: drishti-backend
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - PYTHONUNBUFFERED=1
    volumes:
      - chroma_data:/app/chroma_db
      - ./backend/logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: drishti-frontend
    environment:
      - VITE_API_URL=${API_URL:-http://localhost:8000}
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 3s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: drishti-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  chroma_data:
    driver: local

networks:
  default:
    name: drishti-network
```

## Production Deployment

### Cloud Deployment (AWS/Azure/GCP)

#### AWS EC2 Deployment

```bash
# 1. Launch EC2 Instance
# - AMI: Ubuntu 22.04 LTS
# - Instance Type: t3.medium or larger
# - Security Group: Open ports 80, 443, 22

# 2. Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 4. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 5. Clone and deploy
git clone https://github.com/your-org/drishti.git
cd drishti
cp .env.example .env
# Edit .env with production values
docker-compose -f docker-compose.prod.yml up -d
```

#### AWS RDS for PostgreSQL

```bash
# Create RDS instance via AWS Console
# Update .env with RDS endpoint:
DATABASE_URL=postgresql://username:password@your-rds-endpoint.rds.amazonaws.com:5432/drishti
```

### Kubernetes Deployment

**Backend Deployment:**

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drishti-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: drishti-backend
  template:
    metadata:
      labels:
        app: drishti-backend
    spec:
      containers:
      - name: backend
        image: your-registry/drishti-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: drishti-secrets
              key: database-url
        - name: MISTRAL_API_KEY
          valueFrom:
            secretKeyRef:
              name: drishti-secrets
              key: mistral-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: drishti-backend-service
spec:
  selector:
    app: drishti-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

**Frontend Deployment:**

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drishti-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: drishti-frontend
  template:
    metadata:
      labels:
        app: drishti-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/drishti-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: drishti-frontend-service
spec:
  selector:
    app: drishti-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

**Deploy to Kubernetes:**

```bash
# Create secrets
kubectl create secret generic drishti-secrets \
  --from-literal=database-url="your-database-url" \
  --from-literal=mistral-api-key="your-api-key"

# Deploy applications
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Check status
kubectl get pods
kubectl get services
```

## Database Setup

### PostgreSQL Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

```sql
-- Create database
CREATE DATABASE drishti;

-- Create user
CREATE USER drishti_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE drishti TO drishti_user;

-- Exit
\q
```

### Database Initialization

```bash
cd backend

# Run initialization script
python init_db.py
```

**SQL Schema (init_db.sql):**

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('constable', 'inspector', 'sp', 'admin')),
    assigned_district VARCHAR(100),
    assigned_station_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crimes table
CREATE TABLE IF NOT EXISTS crimes (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) UNIQUE NOT NULL,
    crime_date DATE NOT NULL,
    district VARCHAR(100) NOT NULL,
    police_station_id INTEGER NOT NULL,
    crime_type VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'closed', 'cold')),
    lat FLOAT,
    lng FLOAT,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolution_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criminals table
CREATE TABLE IF NOT EXISTS criminals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    criminal_history_count INTEGER DEFAULT 0,
    is_repeat_offender BOOLEAN DEFAULT FALSE,
    first_offense_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crime-Criminal association table
CREATE TABLE IF NOT EXISTS crime_criminals (
    id SERIAL PRIMARY KEY,
    crime_id INTEGER REFERENCES crimes(id) ON DELETE CASCADE,
    criminal_id INTEGER REFERENCES criminals(id) ON DELETE CASCADE,
    role VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(crime_id, criminal_id)
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    query TEXT,
    response TEXT,
    ip_address VARCHAR(45),
    session_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_crimes_district ON crimes(district);
CREATE INDEX idx_crimes_date ON crimes(crime_date);
CREATE INDEX idx_crimes_type ON crimes(crime_type);
CREATE INDEX idx_crimes_status ON crimes(status);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);

-- Insert default admin user
INSERT INTO users (email, password_hash, role)
VALUES ('admin@ksp.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyW.PJ8QYMrW', 'admin')
ON CONFLICT (email) DO NOTHING;
-- Password: Admin@123
```

### Database Backup

```bash
# Backup database
pg_dump -U drishti_user -d drishti -F c -b -v -f drishti_backup_$(date +%Y%m%d).dump

# Restore database
pg_restore -U drishti_user -d drishti -v drishti_backup_20240101.dump

# Automated daily backup script
cat > /etc/cron.daily/drishti-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/drishti"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump -U drishti_user -d drishti -F c -f $BACKUP_DIR/drishti_$DATE.dump
find $BACKUP_DIR -type f -mtime +7 -delete
EOF

chmod +x /etc/cron.daily/drishti-backup
```

## Environment Configuration

### Backend Environment Variables

```bash
# backend/.env.example

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/drishti
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# AI/ML
MISTRAL_API_KEY=your-mistral-api-key

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# ChromaDB
CHROMA_DB_PATH=/app/chroma_db
```

### Frontend Environment Variables

```bash
# frontend/.env.example

# API Configuration
VITE_API_URL=https://api.yourdomain.com

# Feature Flags
VITE_ENABLE_VOICE=true
VITE_ENABLE_KANNADA=true

# Analytics (optional)
VITE_GA_TRACKING_ID=your-ga-id
```

### Environment Variable Security

```bash
# Generate secure JWT secret
openssl rand -hex 32

# Encrypt environment file (optional)
gpg --symmetric --cipher-algo AES256 .env
```

## Nginx Configuration

### Basic Configuration

```nginx
# /etc/nginx/sites-available/drishti

upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Frontend (React)
    location / {
        root /var/www/drishti/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### SSL Certificate Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (add to cron)
sudo certbot renew --dry-run

# Auto-renewal cron job (already setup by certbot)
# Certificates will auto-renew when they're close to expiration
```

### Enable Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/drishti /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## Monitoring & Logging

### Application Logging

**Backend Logging Configuration:**

```python
# backend/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                f"{log_dir}/drishti.log",
                maxBytes=10485760,  # 10MB
                backupCount=10
            ),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)
```

### System Monitoring with Prometheus

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

### Log Aggregation with ELK Stack

```yaml
# docker-compose.elk.yml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:8.9.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:8.9.0
    volumes:
      - ./logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:8.9.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

volumes:
  es_data:
```

## Backup & Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/drishti"
DATE=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="s3://your-backup-bucket/drishti"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -U drishti_user -d drishti -F c -f $BACKUP_DIR/db_$DATE.dump

# Backup ChromaDB
tar -czf $BACKUP_DIR/chroma_$DATE.tar.gz /app/chroma_db

# Backup configuration files
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /path/to/config

# Upload to S3 (optional)
aws s3 sync $BACKUP_DIR $S3_BUCKET

# Clean old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Disaster Recovery

```bash
# Restore from backup

# 1. Restore database
pg_restore -U drishti_user -d drishti -c -v backup_file.dump

# 2. Restore ChromaDB
tar -xzf chroma_backup.tar.gz -C /app

# 3. Restore configuration
tar -xzf config_backup.tar.gz -C /path/to/config

# 4. Restart services
docker-compose restart
```

## Troubleshooting

### Common Issues

**Issue: Backend won't start**
```bash
# Check logs
docker-compose logs backend

# Check database connection
docker exec -it drishti-backend python -c "from database import get_db_connection; print(get_db_connection())"

# Verify environment variables
docker exec -it drishti-backend env | grep DATABASE_URL
```

**Issue: Frontend can't connect to backend**
```bash
# Check CORS settings
# Verify VITE_API_URL in frontend/.env
# Check backend CORS middleware configuration
```

**Issue: Database connection errors**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U drishti_user -d drishti -h localhost

# Check firewall
sudo ufw status
```

**Issue: High memory usage**
```bash
# Check container stats
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### Performance Optimization

```bash
# Enable gzip compression in Nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript;

# PostgreSQL tuning
# Edit /etc/postgresql/14/main/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
```

### Health Checks

```bash
# Check all services
curl http://localhost:8000/
curl http://localhost:5173/

# Check database
docker exec drishti-postgres pg_isready

# Check logs
docker-compose logs --tail=50 backend
docker-compose logs --tail=50 frontend
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong JWT secret
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Network isolation
- [ ] Least privilege access

## Maintenance

### Regular Tasks

**Daily:**
- Monitor system logs
- Check disk space
- Verify backups

**Weekly:**
- Review security logs
- Update dependencies
- Performance analysis

**Monthly:**
- Security patches
- Database optimization
- Backup testing

---

For deployment support, contact the DevOps team or create an issue in the repository.
