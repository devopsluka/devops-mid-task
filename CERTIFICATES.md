# Certificate Generation Guide

This project uses **auto-generated SSL/TLS certificates** for HTTPS support.

## ⚠️ Important Note

**Certificates are NOT included in the repository** for security reasons. They are generated automatically when you deploy the application.

## How It Works

Certificates are generated automatically using the Python deployment script during deployment.

### Automatic Generation

Certificates are auto-generated when you use any of these deployment methods:

1. **Python Deployment Script (Recommended)**:
   ```bash
   python3 deploy.py deploy  # Full pipeline (includes cert generation)
   python3 deploy.py certs   # Generate certs only
   ```

2. **Docker Compose** (manual cert generation first):
   ```bash
   python3 deploy.py certs  # Generate certificates
   docker-compose up -d     # Deploy
   ```

### Manual Generation

To manually generate or regenerate certificates:

```bash
python3 deploy.py certs                           # Default domain
python3 deploy.py certs --domain mydomain.com     # Custom domain
```

### View Certificate Information

```bash
# View certificate details
openssl x509 -in certs/server.crt -text -noout

# View certificate chain
openssl x509 -in certs/ca.crt -text -noout

# Verify certificate chain
openssl verify -CAfile certs/ca.crt certs/server.crt
```

## Generated Files

When certificates are generated, the following files are created in the `certs/` directory:

| File | Description | In Git? |
|------|-------------|---------|
| `ca.key` | CA private key (4096-bit RSA) | ❌ No (excluded) |
| `ca.crt` | CA certificate (valid 10 years) | ❌ No (excluded) |
| `server.key` | Server private key (2048-bit RSA) | ❌ No (excluded) |
| `server.crt` | Server certificate (valid 825 days) | ❌ No (excluded) |
| `server.csr` | Certificate signing request | ❌ No (excluded) |
| `server.ext` | Certificate extensions config | ❌ No (excluded) |
| `ca.srl` | Serial number file | ❌ No (excluded) |
| `README.md` | Certificate documentation | ❌ No (excluded) |

**All certificate files are excluded from git** via `.gitignore` for security.

## Certificate Details

- **Domain**: golang-webapp.devops-mid-task.com (configurable)
- **Algorithm**: RSA with SHA-256
- **CA Key Size**: 4096-bit
- **Server Key Size**: 2048-bit
- **CA Validity**: 10 years (3650 days)
- **Server Validity**: ~2.25 years (825 days)
- **Type**: Self-signed (for development/testing)

### Subject Alternative Names (SANs)

The server certificate includes:
- `golang-webapp.devops-mid-task.com`
- `*.golang-webapp.devops-mid-task.com` (wildcard)
- `localhost`
- `127.0.0.1`

## Why Certificates Are Not In Git

1. **Security**: Private keys should never be committed to version control
2. **Flexibility**: Each environment can use its own certificates
3. **Expiration**: Certificates expire and need to be regenerated
4. **Custom Domains**: Users can generate certificates for their own domains
5. **Best Practice**: Sensitive files should not be in repositories

## First-Time Setup

When you first clone this repository:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd devops-mid-task
   ```

2. The `certs/` directory won't exist - **this is normal!**

3. Deploy using any method, certificates will be auto-generated:
   ```bash
   python3 deploy.py deploy
   # or
   python3 deploy.py certs && docker-compose up -d
   ```

## Trusting the CA Certificate

To avoid browser warnings, add the CA certificate to your system's trust store:

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

## Production Considerations

### For Production Deployments

⚠️ **Do NOT use self-signed certificates in production!**

Instead:

1. **Use Let's Encrypt** (free, automated):
   ```bash
   # Example with certbot
   certbot certonly --standalone -d yourdomain.com
   ```

2. **Use a commercial CA** (DigiCert, GlobalSign, etc.)

3. **Configure nginx to use real certificates**:
   - Copy real certificates to `certs/` directory
   - Or modify nginx configuration to point to certificate location

4. **Set up automatic renewal**:
   ```bash
   # Example: Let's Encrypt auto-renewal
   certbot renew --deploy-hook "docker-compose restart nginx"
   ```

## Verifying Certificates

### Check if certificates exist
```bash
ls -la certs/
```

### Verify certificate chain
```bash
openssl verify -CAfile certs/ca.crt certs/server.crt
```

### View certificate details
```bash
# Server certificate
openssl x509 -in certs/server.crt -text -noout

# Check expiration
openssl x509 -in certs/server.crt -noout -dates
```

### Test with curl
```bash
# With CA certificate
curl --cacert certs/ca.crt https://localhost:8443/health

# Without validation (not recommended)
curl -k https://localhost:8443/health
```

## Troubleshooting

### Problem: "Certificates not found" error

**Solution**: Generate certificates using the Python script:
```bash
python3 deploy.py certs
```

### Problem: Certificate already exists error

**Solution**: Remove and regenerate:
```bash
rm -rf certs/
python3 deploy.py certs
```

### Problem: Browser shows "Not Secure" warning

**Solution**: Trust the CA certificate (see "Trusting the CA Certificate" section above)

### Problem: Certificate expired

**Solution**: Regenerate certificates:
```bash
python3 deploy.py certs
# Then rebuild and restart containers
python3 deploy.py build
python3 deploy.py start
```

## Custom Domain Certificates

To generate certificates for a custom domain:

```bash
# Generate for your domain
python3 deploy.py certs --domain yourdomain.com

# Then deploy
docker-compose up -d
```

The certificates will include:
- yourdomain.com
- *.yourdomain.com
- localhost
- 127.0.0.1

## Security Best Practices

1. ✅ **Never commit private keys** to git (enforced by `.gitignore`)
2. ✅ **Regenerate certificates periodically** (before expiration)
3. ✅ **Use strong key sizes** (4096-bit for CA, 2048-bit for server)
4. ✅ **Use proper certificates in production** (not self-signed)
5. ✅ **Protect private keys** (600 permissions set automatically)
6. ✅ **Monitor certificate expiration** (set up alerts)

## Quick Reference

```bash
# Generate certificates
python3 deploy.py certs                           # Default domain
python3 deploy.py certs --domain mydomain.com     # Custom domain

# View certificate information
openssl x509 -in certs/server.crt -text -noout    # Server cert
openssl x509 -in certs/ca.crt -text -noout        # CA cert

# Verify certificate chain
openssl verify -CAfile certs/ca.crt certs/server.crt

# Deploy with auto-generation
python3 deploy.py deploy                          # Full pipeline
python3 deploy.py certs && docker-compose up -d   # Step-by-step
```

## Related Documentation

- [README.md](README.md) - Main documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [certs/README.md](certs/README.md) - Certificate-specific docs (auto-generated)
- [QUICK_START.md](QUICK_START.md) - Quick reference

---

**Remember**: The `certs/` directory is **auto-generated** and **not tracked by git**. This is by design for security and flexibility!
