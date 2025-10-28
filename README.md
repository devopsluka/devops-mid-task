# Mini Go Web App

A simple Go web application containerized with Docker.

## Features

- RESTful API with JSON responses
- Health check endpoint
- Multi-stage Docker build for minimal image size
- Built-in health checks
- Configurable API version via environment variable
- **HTTPS/TLS support with custom SSL certificates**
- **Nginx reverse proxy with SSL/TLS termination**
- HTTP to HTTPS automatic redirect
- Automatic fallback to HTTP if certificates are not present
- Secure TLS configuration (TLS 1.2+, strong cipher suites)
- HTTP/2 support
- Security headers (HSTS, X-Frame-Options, etc.)

## API Endpoints

- `GET /` - Home endpoint with welcome message
- `GET /health` - Health check endpoint with uptime and version
- `GET /about` - About information

## Docker Image

The Docker image has been built and is ready for deployment:

- **Image name**: `mini-webapp:latest`
- **Image size**: ~20 MB
- **Exposed ports**:
  - `8443` - HTTPS (primary)
  - `8080` - HTTP (fallback if no certificates)
- **Includes**: SSL/TLS certificates for golang-webapp.devops-mid-task.com

## SSL/TLS Certificates

⚠️ **Important**: Certificates are **auto-generated** during deployment and are **NOT included in the repository** for security reasons.

The application uses self-signed SSL/TLS certificates for secure HTTPS communication:

- **Domain**: golang-webapp.devops-mid-task.com (customizable)
- **Certificate Authority**: DevOps Mid Task Root CA (self-signed)
- **Validity**: Server cert - 825 days (~2.25 years), CA cert - 10 years
- **SANs**: golang-webapp.devops-mid-task.com, *.devops-mid-task.com, localhost, 127.0.0.1
- **Auto-generated**: Certificates are created automatically during deployment

### Generating Certificates

Certificates are auto-generated during deployment:
```bash
python3 deploy.py deploy              # Full deployment (auto-generates certs)
docker-compose up -d                  # Docker Compose (requires certs first)
```

Manual certificate generation:
```bash
python3 deploy.py certs                              # Default domain
python3 deploy.py certs --domain yourdomain.com      # Custom domain
```

For detailed certificate information, see [CERTIFICATES.md](CERTIFICATES.md)

## Quick Start with Python Script 🐍

The easiest way to deploy everything:

```bash
# Full deployment pipeline (certificates + build + deploy + test)
python3 deploy.py deploy
```

This single command will:
1. Generate SSL/TLS certificates
2. Build Docker images
3. Deploy containers with networking
4. Wait for services to be healthy
5. Run comprehensive tests
6. Display status and access URLs

**Other useful commands:**
```bash
python3 deploy.py status    # Show current status
python3 deploy.py test      # Run health checks
python3 deploy.py stop      # Stop containers
python3 deploy.py clean     # Remove everything
```

For complete Python script documentation, see [PYTHON_DEPLOYMENT.md](PYTHON_DEPLOYMENT.md)

## Nginx Reverse Proxy

The application includes an Nginx reverse proxy configuration that provides:

- **SSL/TLS termination** at the edge
- **HTTP to HTTPS redirect** (all HTTP traffic automatically redirected)
- **Reverse proxy** to the backend Go application
- **Security headers** (HSTS, X-Frame-Options, X-Content-Type-Options, etc.)
- **HTTP/2 support** for improved performance
- **Modern TLS configuration** (TLS 1.2+, strong ciphers)

### Architecture

```
┌──────────┐      HTTP/HTTPS       ┌───────────┐      HTTPS      ┌────────────┐
│  Client  │ ───────────────────> │   Nginx   │ ──────────────> │  Go App    │
│          │   Port 80/443        │  (Proxy)  │   Port 8443     │  (Backend) │
└──────────┘                       └───────────┘                  └────────────┘
```

### Configuration Files

- `nginx/nginx.conf` - Main Nginx configuration
- `nginx/Dockerfile` - Nginx Docker image with SSL certificates
- `nginx/README.md` - Detailed Nginx documentation

For detailed Nginx configuration and customization options, see [nginx/README.md](nginx/README.md)

## Environment Variables

- `API_VERSION` - Sets the API version displayed in the health endpoint (default: `1.0.0`)
- `HTTPS_PORT` - HTTPS port to listen on (default: `8443`)
- `HTTP_PORT` - HTTP port to listen on when certificates are not available (default: `8080`)
- `TLS_CERT_FILE` - Path to TLS certificate file (default: `certs/server.crt`)
- `TLS_KEY_FILE` - Path to TLS private key file (default: `certs/server.key`)

## Running the Application

### Recommended: Run with Docker Compose (Nginx + Web App)

The recommended way to run the application is using Docker Compose, which starts both the Nginx reverse proxy and the Go web application:

```bash
# Start all services (nginx reverse proxy + web app)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**Access the application:**
- HTTPS: `https://localhost:8443/` (or `https://localhost:443/` if running as root)
- HTTP: `http://localhost:8080/` (redirects to HTTPS)

**Test the endpoints:**
```bash
# Using CA certificate
curl --cacert certs/ca.crt https://localhost:8443/health

# Test HTTP to HTTPS redirect
curl -I http://localhost:8080/health
```

**Note:** If you don't have Docker Compose installed, you can run the containers manually (see below) or install Docker Compose from [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

### Run with Docker (HTTPS)

```bash
# Run with HTTPS (default - recommended)
docker run -d -p 8443:8443 --name mini-webapp mini-webapp:latest

# Run with custom API version and HTTPS
docker run -d -p 8443:8443 --name mini-webapp -e API_VERSION=2.1.3 mini-webapp:latest

# Run with custom HTTPS port
docker run -d -p 9443:9443 --name mini-webapp -e HTTPS_PORT=9443 mini-webapp:latest
```

### Test the HTTPS endpoints

```bash
# Using the included CA certificate (recommended)
curl --cacert certs/ca.crt https://localhost:8443/health

# Or bypass certificate validation (not recommended for production)
curl -k https://localhost:8443/health

# Test all endpoints with CA certificate
curl --cacert certs/ca.crt https://localhost:8443/
curl --cacert certs/ca.crt https://localhost:8443/health
curl --cacert certs/ca.crt https://localhost:8443/about
```

### Run with Nginx Manually (without Docker Compose)

If you don't have Docker Compose, you can run Nginx and the web app manually:

```bash
# 1. Create a network
docker network create webapp-network

# 2. Build the nginx image
docker build -f nginx/Dockerfile -t mini-webapp-nginx:latest .

# 3. Start the web application
docker run -d \
  --name webapp \
  --network webapp-network \
  -e API_VERSION=1.0.0 \
  mini-webapp:latest

# 4. Start nginx reverse proxy
# For development (using high ports)
docker run -d \
  --name nginx-proxy \
  --network webapp-network \
  -p 8080:80 \
  -p 8443:443 \
  mini-webapp-nginx:latest

# 5. Test the setup
curl --cacert certs/ca.crt https://localhost:8443/health
curl -I http://localhost:8080/health  # Should redirect to HTTPS
```

### Run with HTTP (fallback mode)

If you want to run without HTTPS, you can run a container without the certificates:

```bash
# This would require building a separate image without certificates
# The current image includes certificates and will use HTTPS by default
docker run -d -p 8080:8080 --name mini-webapp -e HTTP_PORT=8080 mini-webapp:latest
```

### Stop the container

```bash
docker stop mini-webapp
docker rm mini-webapp
```

## Trusting the CA Certificate

For browsers and other clients to trust the HTTPS connection without warnings, you need to add the CA certificate to your system's trust store:

### Linux
```bash
sudo cp certs/ca.crt /usr/local/share/ca-certificates/devops-mid-task-ca.crt
sudo update-ca-certificates
```

### macOS
```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certs/ca.crt
```

### Windows (PowerShell as Administrator)
```powershell
certutil -addstore -f "ROOT" certs/ca.crt
```

### For curl only
```bash
# Use the --cacert flag with each request
curl --cacert certs/ca.crt https://localhost:8443/health
```

## Deployment

The Docker images are production-ready and can be:
- Pushed to a container registry (Docker Hub, AWS ECR, GCR, etc.)
- Deployed to Kubernetes, Docker Swarm, or any container orchestration platform
- Run on any Docker-compatible environment

### Tag and Push to Registry

```bash
# Tag the web application image
docker tag mini-webapp:latest your-registry/mini-webapp:latest

# Tag the nginx image
docker tag mini-webapp-nginx:latest your-registry/mini-webapp-nginx:latest

# Push both images to registry
docker push your-registry/mini-webapp:latest
docker push your-registry/mini-webapp-nginx:latest
```

### Deploy with Docker Compose

Update `docker-compose.yml` to use your registry images:
```yaml
services:
  webapp:
    image: your-registry/mini-webapp:latest
    # ... rest of config

  nginx:
    image: your-registry/mini-webapp-nginx:latest
    # ... rest of config
```

Then deploy:
```bash
docker-compose pull  # Pull latest images
docker-compose up -d # Start services
```

## Build from Source

### Build with Docker Compose (Recommended)

```bash
# Build all images using Docker Compose
docker-compose build

# Start all services
docker-compose up -d

# Test the HTTPS endpoint through nginx
curl --cacert certs/ca.crt https://localhost:8443/health
```

### Build Manually

```bash
# Build the web application image (includes SSL certificates)
docker build -t mini-webapp:latest .

# Build the nginx image
docker build -f nginx/Dockerfile -t mini-webapp-nginx:latest .

# Run the containers (see "Run with Nginx Manually" section above)
```

## Security Considerations

### SSL/TLS Certificates
- The included certificates are **self-signed** and intended for development/testing
- For production, use certificates from a trusted Certificate Authority (e.g., Let's Encrypt, DigiCert)
- The CA private key (`certs/ca.key`) is excluded from the Docker image for security
- Server private key (`certs/server.key`) is included in the image - protect access to the image

### TLS Configuration
- Minimum TLS version: 1.2
- Strong cipher suites configured
- Server prefers its own cipher suite order
- ECDHE and RSA key exchange supported

### Recommendations for Production
1. Use certificates from a trusted CA
2. Implement certificate rotation before expiration (825 days)
3. Store private keys securely (e.g., Kubernetes secrets, AWS Secrets Manager)
4. Use environment variables to inject certificate paths
5. Monitor certificate expiration dates
6. Consider using cert-manager for Kubernetes deployments
