# Quick Start Guide

Get the application running in 3 simple steps!

## Prerequisites

- Docker installed and running
- Python 3.6+ (for Python script - recommended)
- Docker Compose installed (optional)
- OpenSSL (for certificate generation - usually pre-installed)

## ⚠️ Important: Certificates

**Certificates are auto-generated** during deployment. You don't need to create them manually!

The `certs/` directory doesn't exist in the repository and will be created automatically.

## Option 0: Quick Start with Python Script (Recommended) 🐍

The easiest way - just one command:

```bash
# Full deployment pipeline (certificates + build + deploy + test)
python3 deploy.py deploy
```

That's it! The script will:
1. Generate SSL/TLS certificates automatically
2. Build Docker images
3. Deploy containers with proper networking
4. Wait for services to be healthy
5. Run comprehensive tests
6. Display status and access URLs

**Access the application:**
```bash
# HTTPS (with CA certificate)
curl --cacert certs/ca.crt https://localhost:8443/health

# Or visit in browser (after trusting CA)
# https://localhost:8443/
```

**Other useful commands:**
```bash
python3 deploy.py status    # Show current status
python3 deploy.py test      # Run tests
python3 deploy.py stop      # Stop containers
python3 deploy.py clean     # Remove everything
```

See [PYTHON_DEPLOYMENT.md](PYTHON_DEPLOYMENT.md) for complete documentation.

## Option 1: Quick Start with Docker Compose

```bash
# 1. Generate certificates
python3 deploy.py certs

# 2. Start all services
docker-compose up -d

# 3. Test the application
curl --cacert certs/ca.crt https://localhost:8443/health

# 4. Access in browser (after trusting CA certificate)
# Visit: https://localhost:8443/
```

## Option 2: Quick Start without Docker Compose

```bash
# 1. Build both images
docker build -t mini-webapp:latest .
docker build -f nginx/Dockerfile -t mini-webapp-nginx:latest .

# 2. Create network and start containers
docker network create webapp-network
docker run -d --name webapp --network webapp-network mini-webapp:latest
docker run -d --name nginx-proxy --network webapp-network -p 8080:80 -p 8443:443 mini-webapp-nginx:latest

# 3. Test the application
curl --cacert certs/ca.crt https://localhost:8443/health
```

## Available Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check with uptime and version
- `GET /about` - Application information

## Testing

```bash
# Test HTTPS (recommended)
curl --cacert certs/ca.crt https://localhost:8443/
curl --cacert certs/ca.crt https://localhost:8443/health
curl --cacert certs/ca.crt https://localhost:8443/about

# Test HTTP to HTTPS redirect
curl -I http://localhost:8080/health
# Should return: 301 Moved Permanently with Location: https://...

# Test without certificate validation (not recommended)
curl -k https://localhost:8443/health
```

## Trusting the CA Certificate (Optional)

To avoid certificate warnings in browsers:

### Linux
```bash
sudo cp certs/ca.crt /usr/local/share/ca-certificates/devops-mid-task-ca.crt
sudo update-ca-certificates
```

### macOS
```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certs/ca.crt
```

### Windows (PowerShell as Admin)
```powershell
certutil -addstore -f "ROOT" certs/ca.crt
```

## Stopping the Application

### With Docker Compose
```bash
docker-compose down
```

### Without Docker Compose
```bash
docker stop nginx-proxy webapp
docker rm nginx-proxy webapp
```

## Viewing Logs

### With Docker Compose
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f webapp
docker-compose logs -f nginx
```

### Without Docker Compose
```bash
docker logs -f webapp
docker logs -f nginx-proxy
```

## Next Steps

- See [README.md](README.md) for detailed documentation
- See [nginx/README.md](nginx/README.md) for Nginx configuration details
- See [certs/README.md](certs/README.md) for SSL certificate information

## Troubleshooting

**Problem**: "Permission denied" on ports 80 or 443
- **Solution**: Use high ports (8080, 8443) or run with sudo/root privileges

**Problem**: Certificate warnings in browser
- **Solution**: Trust the CA certificate using the instructions above

**Problem**: Connection refused
- **Solution**: Check if containers are running with `docker ps`

**Problem**: Docker Compose not found
- **Solution**: Use the manual method or install Docker Compose

For more help, see the full [README.md](README.md)
