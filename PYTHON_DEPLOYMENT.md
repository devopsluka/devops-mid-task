# Python Deployment Script

A comprehensive Python deployment pipeline script that automates the entire deployment process.

## Features

- **Certificate Generation**: Auto-generates SSL/TLS certificates for HTTPS
- **Docker Image Building**: Builds both webapp and nginx images
- **Container Deployment**: Deploys containers with proper networking
- **Health Checks**: Waits for services to become healthy
- **Testing**: Runs comprehensive endpoint tests
- **Cleanup**: Clean removal of all resources
- **Status Monitoring**: View current deployment status

## Requirements

- Python 3.6 or higher
- Docker
- OpenSSL
- curl (for testing)

## Installation

No installation required! The script is self-contained. Just make sure you have Python 3 installed:

```bash
python3 --version
```

## Usage

### Full Deployment Pipeline

Deploy everything in one command (certificates + build + deploy + test):

```bash
python3 deploy.py deploy
```

This command will:
1. Generate SSL/TLS certificates (if not already present)
2. Build Docker images (webapp and nginx)
3. Create Docker network
4. Deploy webapp container with HTTPS
5. Deploy nginx reverse proxy (HTTP→HTTPS redirect)
6. Wait for services to become healthy
7. Run comprehensive health checks
8. Display status and access URLs

### Individual Commands

#### Generate Certificates Only

```bash
python3 deploy.py certs
```

Generate SSL/TLS certificates for the domain. Certificates are created in the `certs/` directory.

**Custom domain:**
```bash
python3 deploy.py certs --domain yourdomain.com
```

#### Build Docker Images Only

```bash
python3 deploy.py build
```

Build both the webapp and nginx Docker images without deploying.

#### Start Containers Only

```bash
python3 deploy.py start
```

Start containers (assumes images are already built). This command:
- Creates Docker network
- Stops existing containers
- Starts webapp container
- Starts nginx container
- Waits for health checks

#### Run Tests

```bash
python3 deploy.py test
```

Run health checks on running containers:
- Test HTTPS endpoint
- Test HTTP→HTTPS redirect
- Test all endpoints (/, /health, /about)

#### Stop Containers

```bash
python3 deploy.py stop
```

Stop and remove running containers (preserves images and network).

#### Show Status

```bash
python3 deploy.py status
```

Display current status of containers.

#### Clean Everything

```bash
python3 deploy.py clean
```

Remove everything:
- Stop and remove containers
- Remove Docker images
- Remove Docker network

**Note**: This does NOT remove certificates. To remove certificates, run:
```bash
rm -rf certs/
```

## Command Reference

| Command | Description | What It Does |
|---------|-------------|--------------|
| `deploy` | Full deployment | Generate certs → Build → Deploy → Test |
| `certs` | Generate certificates | Create SSL/TLS certificates only |
| `build` | Build images | Build Docker images only |
| `start` | Start containers | Deploy containers only |
| `stop` | Stop containers | Stop and remove containers |
| `test` | Run tests | Run health checks |
| `clean` | Clean up | Remove containers, images, network |
| `status` | Show status | Display container status |

## Examples

### Complete Deployment Workflow

```bash
# Full deployment with default settings
python3 deploy.py deploy

# Access the application
curl --cacert certs/ca.crt https://localhost:8443/health
```

### Custom Domain Deployment

```bash
# Generate certificates for custom domain
python3 deploy.py certs --domain myapp.example.com

# Build and deploy
python3 deploy.py build
python3 deploy.py start
python3 deploy.py test
```

### Development Workflow

```bash
# Initial setup
python3 deploy.py deploy

# Make changes to code...
# Rebuild and redeploy
python3 deploy.py stop
python3 deploy.py build
python3 deploy.py start

# Test changes
python3 deploy.py test
```

### Clean Deployment

```bash
# Remove everything
python3 deploy.py clean

# Remove certificates too
rm -rf certs/

# Fresh deployment
python3 deploy.py deploy
```

## Output

The script provides colored output for easy reading:

- **Green (✓)**: Success messages
- **Yellow (→)**: Info messages
- **Red (✗)**: Error messages
- **Yellow (⚠)**: Warning messages

### Example Output

```
============================================================
Starting Deployment Pipeline
============================================================

→ Generating SSL/TLS certificates...
============================================================
Checking Prerequisites
============================================================
✓ OpenSSL is installed (OpenSSL 3.x.x)
============================================================
Generating CA Certificate
============================================================
→ Generating CA private key (4096-bit RSA)...
✓ CA private key generated: certs/ca.key
...
✓ All certificates generated successfully!

============================================================
Building Docker Images
============================================================
→ Building webapp image...
✓ Webapp image built
...

============================================================
Deployment Summary
============================================================

✓ Services are running!

Access URLs:
  HTTPS: https://localhost:8443/
  HTTP:  http://localhost:8080/ (redirects to HTTPS)

Container Status:
NAMES     STATUS                   PORTS
nginx     Up 10 seconds (healthy)  0.0.0.0:8080->80/tcp, 0.0.0.0:8443->443/tcp
webapp    Up 15 seconds (healthy)
```

## Environment Variables

The script respects the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HTTP_PORT` | 8080 | HTTP port for nginx |
| `HTTPS_PORT` | 8443 | HTTPS port for nginx |
| `API_VERSION` | 1.0.0 | API version for webapp |

### Using Environment Variables

```bash
# Deploy with custom ports
HTTP_PORT=80 HTTPS_PORT=443 python3 deploy.py deploy

# Deploy with custom API version
API_VERSION=2.0.0 python3 deploy.py deploy
```

## Accessing the Application

After deployment, access the application at:

- **HTTPS**: https://localhost:8443/
- **HTTP**: http://localhost:8080/ (automatically redirects to HTTPS)

### Available Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check with uptime and version
- `GET /about` - Application information

### Testing with curl

```bash
# Using CA certificate (recommended)
curl --cacert certs/ca.crt https://localhost:8443/health

# Bypass certificate validation (not recommended)
curl -k https://localhost:8443/health

# Test HTTP redirect
curl -I http://localhost:8080/health
```

## Trusting the CA Certificate

To avoid certificate warnings in browsers, add the CA certificate to your system's trust store:

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

## Troubleshooting

### Problem: "Docker is not installed or not running"

**Solution**: Install Docker and ensure the Docker daemon is running:
```bash
docker --version
sudo systemctl start docker  # Linux
```

### Problem: "OpenSSL is not installed"

**Solution**: Install OpenSSL:
```bash
# Ubuntu/Debian
sudo apt-get install openssl

# CentOS/RHEL
sudo yum install openssl

# macOS
brew install openssl
```

### Problem: "Permission denied" on ports 80/443

**Solution**: Either:
1. Use unprivileged ports (8080/8443 - default)
2. Run with sudo/root privileges for ports 80/443

### Problem: Containers fail health checks

**Solution**: Check container logs:
```bash
docker logs webapp
docker logs nginx
```

### Problem: Certificate warnings in browser

**Solution**: Trust the CA certificate using the instructions above.

## Script Architecture

The script is organized into several classes:

- **`Config`**: Configuration constants
- **`Logger`**: Colored output logging
- **`CommandRunner`**: Execute shell commands
- **`CertificateGenerator`**: Generate SSL/TLS certificates
- **`DockerDeployer`**: Build and deploy Docker containers
- **`DeploymentPipeline`**: Main orchestrator

## Comparison with Shell Scripts

| Feature | deploy.py (Python) | deploy.sh (Bash) | Makefile |
|---------|-------------------|------------------|----------|
| Certificate generation | ✅ Built-in | ❌ Calls external script | ❌ Calls external script |
| Single command deploy | ✅ Yes | ✅ Yes | ✅ Yes |
| Health checks | ✅ Yes | ✅ Yes | ✅ Yes |
| Cross-platform | ✅ Excellent | ⚠️ Good | ⚠️ Good |
| Error handling | ✅ Excellent | ⚠️ Good | ⚠️ Basic |
| Colored output | ✅ Yes | ✅ Yes | ✅ Yes |
| Modular design | ✅ Classes | ⚠️ Functions | ❌ Targets |
| Easy to extend | ✅ Very easy | ⚠️ Moderate | ⚠️ Moderate |

## Advantages of Python Script

1. **Self-contained**: All functionality in one script
2. **Better error handling**: Proper exception handling
3. **Cross-platform**: Works on Windows, Linux, macOS
4. **Modular**: Easy to extend and modify
5. **Type hints**: Better code documentation
6. **Object-oriented**: Clean, organized code structure
7. **No external dependencies**: Self-contained certificate generation

## Security Notes

- Private keys are set to 600 permissions (owner read/write only)
- Certificates are excluded from git via `.gitignore`
- Self-signed certificates are for development/testing only
- Use proper certificates from a trusted CA for production

## Next Steps

After successful deployment:

1. **Test the application**: Visit https://localhost:8443/
2. **Trust the CA certificate**: Follow the instructions above
3. **Monitor logs**: `docker logs -f webapp`
4. **Make changes**: Modify code and redeploy
5. **Production deployment**: Replace certificates with trusted CA certificates

## Additional Resources

- [README.md](README.md) - Main project documentation
- [QUICK_START.md](QUICK_START.md) - Quick reference guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [CERTIFICATES.md](CERTIFICATES.md) - Certificate management guide
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Project organization

## Support

If you encounter issues:

1. Check logs: `docker logs webapp` and `docker logs nginx`
2. Run status check: `python3 deploy.py status`
3. Review [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
4. Clean and redeploy: `python3 deploy.py clean && python3 deploy.py deploy`

---

**Project Status**: Production-ready
**Last Updated**: 2025-10-27
