# Project Structure

Clean, organized structure for golang-webapp.devops-mid-task.com

## Directory Structure

```
devops-mid-task/
├── main.go                      # Go web application
├── go.mod                       # Go module dependencies
├── Dockerfile                   # Web application container image
│
├── nginx/
│   ├── nginx.conf              # Nginx reverse proxy configuration
│   ├── Dockerfile              # Nginx container image
│   └── README.md               # Nginx documentation
│
├── docker-compose.yml          # Main deployment configuration
├── docker-compose.prod.yml     # Production overrides
├── deploy.py                   # Python deployment pipeline (recommended)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
│
├── README.md                   # Main project documentation
├── QUICK_START.md              # Quick reference guide
├── DEPLOYMENT.md               # Detailed deployment guide
├── CERTIFICATES.md             # Certificate generation guide
├── PYTHON_DEPLOYMENT.md        # Python script documentation
└── PROJECT_STRUCTURE.md        # This file

## Auto-Generated Directories (Not in Git)

```
certs/                          # SSL/TLS certificates (auto-generated)
├── ca.key                      # CA private key
├── ca.crt                      # CA certificate
├── server.key                  # Server private key
├── server.crt                  # Server certificate
├── server.csr                  # Certificate signing request
├── server.ext                  # Certificate extensions
├── ca.srl                      # Serial number
└── README.md                   # Auto-generated certificate docs

logs/                           # Application logs (auto-generated)
└── nginx/                      # Nginx access and error logs
```

## File Purposes

### Application Code

| File | Purpose |
|------|---------|
| `main.go` | Go web application with HTTPS support |
| `go.mod` | Go module dependencies |
| `Dockerfile` | Multi-stage Docker build for web app |

### Nginx Configuration

| File | Purpose |
|------|---------|
| `nginx/nginx.conf` | Reverse proxy, SSL termination, HTTP→HTTPS redirect |
| `nginx/Dockerfile` | Nginx container with SSL certificates |
| `nginx/README.md` | Nginx configuration documentation |

### Deployment Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Main orchestration (development & production) |
| `docker-compose.prod.yml` | Production-specific overrides |
| `deploy.py` | Python deployment pipeline (automated, recommended) |
| `.env.example` | Environment variable template |

### Security & Certificates

| File | Purpose |
|------|---------|
| `deploy.py` | SSL/TLS certificate generation (via `certs` command) |
| `.gitignore` | Excludes certs/, logs/, and sensitive files |

### Documentation

| File | Purpose | Length |
|------|---------|--------|
| `README.md` | Main overview and documentation | ~340 lines |
| `QUICK_START.md` | Quick reference guide | 148 lines |
| `DEPLOYMENT.md` | Detailed deployment guide | 613 lines |
| `CERTIFICATES.md` | Certificate generation guide | 321 lines |
| `PYTHON_DEPLOYMENT.md` | Python script documentation | ~480 lines |
| `PROJECT_STRUCTURE.md` | This file | ~290 lines |

## What's Tracked by Git

✅ **Included in Repository:**
- All source code (`.go`, `Dockerfile`, etc.)
- Configuration files (`nginx.conf`, `docker-compose.yml`, etc.)
- Scripts (`deploy.py`)
- Documentation (`*.md` files)
- Examples (`.env.example`)

❌ **Excluded from Repository:**
- `certs/` - SSL certificates (auto-generated)
- `logs/` - Application logs
- `.env` - Environment variables
- `.idea/`, `.vscode/` - IDE files
- `main` - Compiled binaries

## Quick Navigation

### Getting Started
1. Start here: [README.md](README.md)
2. Quick setup: [QUICK_START.md](QUICK_START.md)
3. Detailed guide: [DEPLOYMENT.md](DEPLOYMENT.md)

### Configuration
- Nginx: [nginx/README.md](nginx/README.md)
- Certificates: [CERTIFICATES.md](CERTIFICATES.md)
- Environment: [.env.example](.env.example)

### Deployment
- Python Script: [deploy.py](deploy.py) - Automated deployment pipeline
- Docker Compose: [docker-compose.yml](docker-compose.yml) - Container orchestration
- Documentation: [PYTHON_DEPLOYMENT.md](PYTHON_DEPLOYMENT.md)

## Lines of Code

```
Language       Files    Lines    Code    Comments    Blanks
─────────────────────────────────────────────────────────────
Go             1        129      98      13          18
Python         1        917      750     120         47
Dockerfile     2        77       53      15          9
YAML           2        141      134     7           0
Shell          1        334      229     65          40
Nginx          1        122      89      23          10
Markdown       6        1833     -       -           -
─────────────────────────────────────────────────────────────
Total                   3553
```

## Dependencies

### Runtime
- **Go**: 1.21 (Alpine-based)
- **Nginx**: 1.29+ (Alpine-based)
- **Alpine Linux**: 3.22+
- **OpenSSL**: For certificate generation

### Development/Deployment
- **Python**: 3.6+ (for deploy.py script)
- **Docker**: 20.10+ or Podman
- **Docker Compose**: 2.0+ (optional)
- **curl**: For testing endpoints
- **OpenSSL**: For certificate generation

## Port Configuration

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Nginx | 80 | HTTP | Redirects to HTTPS |
| Nginx | 443 | HTTPS | SSL/TLS termination |
| Webapp | 8443 | HTTPS | Backend API (internal) |

**Note**: For development without root, use ports 8080 (HTTP) and 8443 (HTTPS).

## Environment Variables

See [.env.example](.env.example) for full configuration.

**Key Variables:**
- `API_VERSION` - API version (default: 1.0.0)
- `HTTP_PORT` - External HTTP port (default: 80)
- `HTTPS_PORT` - External HTTPS port (default: 443)
- `COMPOSE_PROJECT_NAME` - Docker Compose project name

## Container Images

| Image | Base | Size | Purpose |
|-------|------|------|---------|
| `mini-webapp` | golang:1.21-alpine | ~22 MB | Web application |
| `mini-webapp-nginx` | nginx:alpine | ~54 MB | Reverse proxy |

## Development Workflow

```bash
# 1. Clone repository
git clone <repo-url>
cd devops-mid-task

# 2. Full deployment (one command)
python3 deploy.py deploy

# Or step-by-step:
# 2a. Generate certificates
python3 deploy.py certs

# 2b. Build images
python3 deploy.py build

# 2c. Start services
python3 deploy.py start

# 3. Test
python3 deploy.py test

# 4. View status
python3 deploy.py status

# 5. Stop
python3 deploy.py stop
```

## Production Workflow

```bash
# 1. Clone repository
git clone <repo-url>
cd devops-mid-task

# 2. Configure environment
cp .env.example .env
# Edit .env for production settings

# 3. Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Security Features

✅ Auto-generated SSL/TLS certificates
✅ HTTP to HTTPS redirect (301)
✅ TLS 1.2+ only
✅ Strong cipher suites
✅ Security headers (HSTS, X-Frame-Options, etc.)
✅ Non-root containers
✅ Minimal base images
✅ Multi-stage Docker builds
✅ Private keys excluded from git

## Key Features

- **HTTPS by default**: Auto-configured SSL/TLS
- **Auto-scaling ready**: Docker Compose orchestration
- **Production-ready**: Resource limits, health checks, restart policies
- **Secure**: No secrets in repository
- **Flexible**: Configurable ports, domains, and settings
- **Well-documented**: Comprehensive guides and examples
- **Automated**: Python deployment pipeline for common tasks

## Contributing

For changes:
1. Update relevant documentation
2. Test deployment with `python3 deploy.py deploy`
3. Verify certificates regenerate correctly
4. Check all scripts work

## Maintenance

### Certificate Renewal
```bash
python3 deploy.py certs
python3 deploy.py build
python3 deploy.py start
```

### Update Application
```bash
# Edit main.go
python3 deploy.py build
python3 deploy.py start
```

### Clean Everything
```bash
python3 deploy.py clean
```

## Support

- Issues: Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
- Documentation: See individual .md files
- Logs: `docker-compose logs` or `docker logs <container-name>`

---

**Project Status**: Production-ready
**Last Updated**: 2025-10-26
