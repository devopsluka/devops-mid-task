# Nginx Reverse Proxy Configuration

This directory contains the Nginx configuration for the golang-webapp reverse proxy with HTTPS/TLS support.

## Overview

The Nginx reverse proxy provides:
- **HTTPS/TLS termination** using the self-signed certificates
- **HTTP to HTTPS redirect** for all traffic
- **Reverse proxy** to the backend Go application
- **Security headers** and modern TLS configuration
- **HTTP/2 support** for better performance

## Architecture

```
Client (HTTP/HTTPS) → Nginx (Port 80/443) → Go App (Port 8443 via HTTPS)
```

## Files

- `nginx.conf` - Main Nginx configuration file
- `Dockerfile` - Docker image for Nginx with certificates
- `README.md` - This file

## Configuration Details

### HTTP Server (Port 80)
- Listens on port 80
- Redirects all traffic to HTTPS with 301 status code
- Logs to `/var/log/nginx/http_access.log` and `/var/log/nginx/http_error.log`

### HTTPS Server (Port 443)
- Listens on port 443 with SSL/TLS
- HTTP/2 enabled for improved performance
- Uses certificates from `/etc/nginx/certs/`
- Proxies to backend at `https://webapp:8443`
- Logs to `/var/log/nginx/https_access.log` and `/var/log/nginx/https_error.log`

### SSL/TLS Configuration
- **Protocols**: TLSv1.2, TLSv1.3
- **Cipher Suites**: Modern, secure ciphers with ECDHE and AES-GCM
- **Session Cache**: 10m shared cache
- **Session Timeout**: 10 minutes
- **Server Cipher Preference**: Enabled

### Security Headers
The following security headers are added to all HTTPS responses:
- `Strict-Transport-Security`: Forces HTTPS for 1 year
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME-type sniffing
- `X-XSS-Protection`: Enables XSS filtering
- `Referrer-Policy`: Controls referrer information

### Proxy Configuration
- Real IP forwarding
- Custom headers for proper upstream identification
- 60s timeouts for connections
- Proxy buffering disabled for real-time applications
- WebSocket support included

## Building the Nginx Image

```bash
# From the project root directory
docker build -f nginx/Dockerfile -t mini-webapp-nginx:latest .
```

## Running Standalone

### Create Network
```bash
docker network create webapp-network
```

### Start Backend Application
```bash
docker run -d \
  --name webapp \
  --network webapp-network \
  -e API_VERSION=1.0.0 \
  mini-webapp:latest
```

### Start Nginx Proxy
```bash
# For development (using high ports)
docker run -d \
  --name nginx-proxy \
  --network webapp-network \
  -p 8080:80 \
  -p 8443:443 \
  mini-webapp-nginx:latest

# For production (requires root/privileges)
docker run -d \
  --name nginx-proxy \
  --network webapp-network \
  -p 80:80 \
  -p 443:443 \
  mini-webapp-nginx:latest
```

## Using Docker Compose

The easiest way to run the entire stack is using Docker Compose:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Testing

### Test HTTP Redirect
```bash
# Should return 301 redirect to HTTPS
curl -I http://localhost:8080/health
```

Expected response:
```
HTTP/1.1 301 Moved Permanently
Location: https://localhost/health
```

### Test HTTPS Endpoints
```bash
# Using CA certificate (recommended)
curl --cacert certs/ca.crt https://localhost:8443/health
curl --cacert certs/ca.crt https://localhost:8443/
curl --cacert certs/ca.crt https://localhost:8443/about

# Or with certificate validation disabled (not recommended)
curl -k https://localhost:8443/health
```

### Test HTTP/2
```bash
# Check if HTTP/2 is being used
curl -I --http2 --cacert certs/ca.crt https://localhost:8443/health
```

## Logs

Nginx logs are available at:
- Access logs: `/var/log/nginx/https_access.log` and `/var/log/nginx/http_access.log`
- Error logs: `/var/log/nginx/https_error.log` and `/var/log/nginx/http_error.log`

### View Logs
```bash
# View nginx logs from container
docker logs nginx-proxy

# View specific log files
docker exec nginx-proxy tail -f /var/log/nginx/https_access.log
docker exec nginx-proxy tail -f /var/log/nginx/https_error.log
```

### Persistent Logs
When using Docker Compose, logs are mounted to `./logs/nginx/` on the host for persistence.

## Customization

### Update Server Name
Edit `nginx.conf` and change the `server_name` directive:
```nginx
server_name your-domain.com www.your-domain.com;
```

### Add Custom Headers
Add to the `server` block in `nginx.conf`:
```nginx
add_header Custom-Header "value" always;
```

### Change Backend URL
Edit the `upstream` block in `nginx.conf`:
```nginx
upstream webapp_backend {
    server your-backend:port;
}
```

### Enable Backend SSL Verification
For production, enable SSL verification for the backend:
```nginx
proxy_ssl_verify on;
proxy_ssl_trusted_certificate /etc/nginx/certs/ca.crt;
```

## Troubleshooting

### Check Nginx Configuration
```bash
docker exec nginx-proxy nginx -t
```

### Reload Nginx After Config Changes
```bash
docker exec nginx-proxy nginx -s reload
```

### Certificate Issues
If you encounter certificate errors:
1. Verify certificates exist in container:
   ```bash
   docker exec nginx-proxy ls -l /etc/nginx/certs/
   ```
2. Check certificate validity:
   ```bash
   docker exec nginx-proxy openssl x509 -in /etc/nginx/certs/server.crt -text -noout
   ```

### Connection Issues
1. Check if nginx is running:
   ```bash
   docker ps | grep nginx-proxy
   ```
2. Check if backend is accessible:
   ```bash
   docker exec nginx-proxy wget --spider https://webapp:8443/health
   ```

## Production Recommendations

1. **Use Real Certificates**: Replace self-signed certificates with ones from a trusted CA (Let's Encrypt, DigiCert, etc.)
2. **Enable OCSP Stapling**: Once using real certificates, enable `ssl_stapling on`
3. **Generate DH Parameters**: Create and use Diffie-Hellman parameters:
   ```bash
   openssl dhparam -out dhparam.pem 2048
   ```
4. **Enable Backend SSL Verification**: Set `proxy_ssl_verify on` for production
5. **Rate Limiting**: Add rate limiting to prevent abuse:
   ```nginx
   limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
   ```
6. **Monitoring**: Set up monitoring for Nginx metrics
7. **Log Rotation**: Configure log rotation to prevent disk space issues
8. **Security Updates**: Regularly update the Nginx base image

## Performance Tuning

### Worker Processes
Nginx automatically tunes worker processes. To customize:
```nginx
worker_processes auto;
worker_connections 1024;
```

### Caching
Add caching for static content:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
proxy_cache my_cache;
```

### Compression
Enable gzip compression (already enabled in base nginx image):
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```
