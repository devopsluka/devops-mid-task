# Deployment Guide

Complete guide for deploying the golang-webapp.devops-mid-task.com application stack.

## Table of Contents

- [Quick Deploy](#quick-deploy)
- [Prerequisites](#prerequisites)
- [Deployment Methods](#deployment-methods)
- [Configuration](#configuration)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Production Considerations](#production-considerations)

## Quick Deploy

### Method 1: Using Python Deployment Script (Recommended)

```bash
# Full deployment pipeline (certificates + build + deploy + test)
python3 deploy.py deploy

# The script will:
# - Generate SSL/TLS certificates
# - Build Docker images
# - Create network
# - Start containers
# - Wait for health checks
# - Run comprehensive tests
```

### Method 2: Using Docker Compose

```bash
# Generate certificates first (if not already done)
python3 deploy.py certs

# Deploy
docker-compose up -d

# Test
python3 deploy.py test
```

## Prerequisites

### Required

- **Docker** (or Podman): v20.10+ recommended
- **Disk Space**: ~500MB for images
- **Ports**: 80, 443 (or 8080, 8443 for non-root)
- **OS**: Linux, macOS, or Windows with WSL2

### Optional

- **Docker Compose**: v2.0+ (for compose-based deployment)
- **Python**: 3.6+ (for deploy.py script - recommended)
- **curl**: For testing endpoints
- **jq**: For prettier JSON output

### Install Docker Compose (if needed)

```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Or use pip
pip install docker-compose
```

## Deployment Methods

### A. Python Deployment Script (`deploy.py`)

Best for: Quick testing, CI/CD pipelines, automated deployments

```bash
# Full deployment pipeline
python3 deploy.py deploy

# Or step-by-step:
python3 deploy.py certs     # Generate certificates
python3 deploy.py build     # Build images
python3 deploy.py start     # Start containers
python3 deploy.py test      # Run tests

# Management:
python3 deploy.py status    # View status
python3 deploy.py stop      # Stop services
python3 deploy.py clean     # Clean everything
```

**Features:**
- ✅ Comprehensive deployment pipeline
- ✅ Auto-generates SSL/TLS certificates
- ✅ Automatic health checks with timeout
- ✅ Colored output with progress indicators
- ✅ Error handling and validation
- ✅ Works with both Docker and Podman
- ✅ No Docker Compose required

For complete documentation, see [PYTHON_DEPLOYMENT.md](PYTHON_DEPLOYMENT.md)

### B. Docker Compose

Best for: Development, production, multi-container orchestration

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

**Features:**
- ✅ Declarative configuration
- ✅ Service dependencies
- ✅ Volume management
- ✅ Environment variable support
- ✅ Easy scaling


## Configuration

### Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` to customize:

```bash
# Application
API_VERSION=1.0.0

# Ports (for production use 80/443)
HTTP_PORT=80
HTTPS_PORT=443

# For development (unprivileged ports)
# HTTP_PORT=8080
# HTTPS_PORT=8443
```

### Port Configuration

**Production (requires root/sudo):**
```bash
HTTP_PORT=80
HTTPS_PORT=443
```

**Development (non-root):**
```bash
HTTP_PORT=8080
HTTPS_PORT=8443
```

### Resource Limits

For production, uncomment resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
```

Or use the production compose file:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Testing

### Automated Tests

```bash
# Using Python deployment script (recommended)
python3 deploy.py test

# Manual testing
curl --cacert certs/ca.crt https://localhost:443/health
curl -I http://localhost:80/health  # Should redirect to HTTPS
```

### Health Checks

```bash
# Check service health manually
docker inspect --format='{{.State.Health.Status}}' golang-webapp
docker inspect --format='{{.State.Health.Status}}' nginx-proxy

# Or check status with Python script
python3 deploy.py status
```

### Manual Testing

```bash
# Test HTTPS endpoints
curl --cacert certs/ca.crt https://localhost:443/
curl --cacert certs/ca.crt https://localhost:443/health
curl --cacert certs/ca.crt https://localhost:443/about

# Test HTTP redirect
curl -I http://localhost:80/
# Expected: 301 Moved Permanently, Location: https://...

# Test without CA cert (will show certificate details)
curl -kv https://localhost:443/health
```

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f webapp
docker-compose logs -f nginx

# Or manually
docker logs -f golang-webapp
docker logs -f nginx-proxy
```

### Resource Usage

```bash
# View resource usage
docker stats golang-webapp nginx-proxy
```

### Service Status

```bash
# Using Python script
python3 deploy.py status

# Or manually
docker-compose ps
docker ps --filter "label=com.devops-mid-task.service"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │         Host Machine                 │
        │  Ports: 80 (HTTP), 443 (HTTPS)      │
        └──────────────────┬───────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │     Docker Network (webapp-network)  │
        │                                       │
        │  ┌────────────────────────────────┐  │
        │  │  Nginx Container (nginx)       │  │
        │  │  - Port 80: HTTP → HTTPS       │  │
        │  │  - Port 443: HTTPS/TLS         │  │
        │  │  - SSL/TLS Termination         │  │
        │  │  - Reverse Proxy               │  │
        │  └───────────┬────────────────────┘  │
        │              │ HTTPS                  │
        │              ▼                        │
        │  ┌────────────────────────────────┐  │
        │  │  Webapp Container (webapp)     │  │
        │  │  - Port 8443: HTTPS            │  │
        │  │  - Go Application              │  │
        │  │  - REST API                    │  │
        │  └────────────────────────────────┘  │
        └───────────────────────────────────────┘
```

## Troubleshooting

### Port Already in Use

**Problem:** "bind: address already in use"

**Solution:**
```bash
# Find process using port
sudo lsof -i :80
sudo lsof -i :443

# Use different ports
HTTP_PORT=8080 HTTPS_PORT=8443 docker-compose up -d
```

### Permission Denied (Ports 80/443)

**Problem:** Cannot bind to privileged ports

**Solution:**
```bash
# Option 1: Use unprivileged ports
HTTP_PORT=8080 HTTPS_PORT=8443 docker-compose up -d

# Option 2: Run with sudo (not recommended)
sudo docker-compose up -d

# Option 3: Configure unprivileged port binding (Linux)
sudo sysctl net.ipv4.ip_unprivileged_port_start=80
```

### Container Won't Start

**Problem:** Container exits immediately

**Solution:**
```bash
# Check logs
docker logs webapp
docker logs nginx

# Check health status
docker inspect webapp
docker inspect nginx

# Rebuild images
docker-compose build --no-cache
```

### Certificate Errors

**Problem:** SSL certificate verification failed

**Solution:**
```bash
# Verify certificates exist
ls -l certs/

# Verify certificate chain
openssl verify -CAfile certs/ca.crt certs/server.crt

# Trust CA certificate
sudo cp certs/ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

### Network Issues

**Problem:** Cannot reach webapp from nginx

**Solution:**
```bash
# Check network
docker network inspect webapp-network

# Verify both containers are on same network
docker inspect webapp | grep -A 10 Networks
docker inspect nginx | grep -A 10 Networks

# Recreate network
docker network rm webapp-network
docker network create webapp-network
```

### DNS Resolution Issues (Podman)

**Problem:** "host not found in upstream"

**Solution:**
```bash
# Ensure containers use correct names
# webapp container must be named "webapp"
# nginx must be able to resolve "webapp"

# Test DNS resolution
docker run --rm --network webapp-network alpine ping -c 1 webapp
```

## Production Considerations

### 1. Use Production Compose File

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

This enables:
- Resource limits
- Restart policies
- Log rotation
- Production ports (80/443)

### 2. Use Real SSL Certificates

Replace self-signed certificates with ones from a trusted CA:

```bash
# Example: Let's Encrypt
# Copy your certificates
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem certs/server.crt
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem certs/server.key

# Rebuild
docker-compose build nginx
docker-compose up -d nginx
```

### 3. Configure Log Rotation

Logs are in `logs/nginx/`. Configure logrotate:

```bash
sudo vi /etc/logrotate.d/webapp
```

```
/path/to/project/logs/nginx/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

### 4. Set Up Monitoring

```bash
# Prometheus
# Add metrics endpoint to application
# Configure prometheus to scrape containers

# Health checks
# Use external monitoring service
curl --cacert certs/ca.crt https://yourdomain.com/health
```

### 5. Backup Strategy

```bash
# Backup certificates
tar -czf certs-backup-$(date +%Y%m%d).tar.gz certs/

# Backup logs (optional)
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

### 6. Security Hardening

```bash
# Run containers as non-root (already configured in Dockerfiles)
# Use read-only file systems where possible
# Scan images for vulnerabilities
docker scan mini-webapp:latest
docker scan mini-webapp-nginx:latest

# Keep images updated
docker-compose pull
docker-compose up -d
```

### 7. High Availability

For production HA:

```bash
# Use Docker Swarm or Kubernetes
# Configure load balancer
# Use managed database (if adding database later)
# Implement health checks in load balancer
```

## Deployment Checklist

- [ ] Prerequisites installed (Docker, Docker Compose)
- [ ] Ports available (80, 443 or 8080, 8443)
- [ ] Environment variables configured (.env file)
- [ ] SSL certificates generated
- [ ] Images built successfully
- [ ] Containers started
- [ ] Health checks passing
- [ ] HTTP redirects to HTTPS
- [ ] HTTPS endpoints working
- [ ] Logs accessible
- [ ] Monitoring configured (production)
- [ ] Backup strategy in place (production)

## Quick Reference

### Common Commands

```bash
# Deploy
python3 deploy.py deploy              # Python script (recommended)
docker-compose up -d                  # Docker Compose

# Stop
python3 deploy.py stop                # Python script
docker-compose down                   # Docker Compose

# Logs
docker-compose logs -f                # All services
docker logs -f golang-webapp          # Webapp
docker logs -f nginx-proxy            # Nginx

# Test
python3 deploy.py test                # Python script (recommended)
curl --cacert certs/ca.crt https://localhost/health

# Status
python3 deploy.py status              # View deployment status

# Clean
python3 deploy.py clean               # Python script (removes everything)
docker-compose down -v --rmi local    # Docker Compose (removes everything)
```

### Access URLs

- **HTTPS**: https://localhost:443/ (or https://localhost:8443/)
- **HTTP**: http://localhost:80/ (redirects to HTTPS)
- **Health**: https://localhost:443/health
- **About**: https://localhost:443/about

## Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review logs: `docker-compose logs`
3. Check [README.md](README.md) for detailed documentation
4. Check [nginx/README.md](nginx/README.md) for Nginx-specific issues
5. Check [certs/README.md](certs/README.md) for certificate issues

## Next Steps

After deployment:

1. Trust the CA certificate (see [QUICK_START.md](QUICK_START.md))
2. Configure DNS (point your domain to the server)
3. Set up monitoring and alerting
4. Configure backups
5. Implement log aggregation
6. Set up CI/CD pipeline
