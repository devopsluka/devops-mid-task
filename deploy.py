#!/usr/bin/env python3

"""
============================================================================
Deployment Pipeline Script for golang-webapp.devops-mid-task.com
============================================================================
This script provides a complete deployment pipeline including:
  - SSL/TLS certificate generation
  - Docker image building
  - Container deployment with HTTPS
  - HTTP to HTTPS redirection
  - Health checks and testing
  - Cleanup and uninstallation

Usage:
  python3 deploy.py deploy      # Full deployment
  python3 deploy.py build       # Build images only
  python3 deploy.py start       # Start containers only
  python3 deploy.py stop        # Stop containers
  python3 deploy.py clean       # Clean everything
  python3 deploy.py test        # Run tests
  python3 deploy.py status      # Show status

Requirements:
  - Python 3.6+
  - Docker
  - OpenSSL
============================================================================
"""

import argparse
import subprocess
import sys
import os
import time
import json
from pathlib import Path
from typing import Optional, List, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'


class Config:
    """Configuration constants"""
    DOMAIN = "golang-webapp.devops-mid-task.com"
    CERTS_DIR = "certs"
    NETWORK_NAME = "webapp-network"
    WEBAPP_IMAGE = "mini-webapp:latest"
    NGINX_IMAGE = "mini-webapp-nginx:latest"
    WEBAPP_CONTAINER = "webapp"
    NGINX_CONTAINER = "nginx"
    HTTP_PORT = int(os.getenv("HTTP_PORT", "8080"))
    HTTPS_PORT = int(os.getenv("HTTPS_PORT", "8443"))
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    CERT_DAYS = 825  # ~2.25 years
    CA_DAYS = 3650  # 10 years


class Logger:
    """Logging utility with colored output"""

    @staticmethod
    def header(message: str):
        """Print a header message"""
        line = "=" * 60
        print(f"{Colors.GREEN}{line}{Colors.NC}")
        print(f"{Colors.GREEN}{message}{Colors.NC}")
        print(f"{Colors.GREEN}{line}{Colors.NC}")

    @staticmethod
    def success(message: str):
        """Print a success message"""
        print(f"{Colors.GREEN}✓ {message}{Colors.NC}")

    @staticmethod
    def error(message: str):
        """Print an error message"""
        print(f"{Colors.RED}✗ {message}{Colors.NC}", file=sys.stderr)

    @staticmethod
    def info(message: str):
        """Print an info message"""
        print(f"{Colors.YELLOW}→ {message}{Colors.NC}")

    @staticmethod
    def warning(message: str):
        """Print a warning message"""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.NC}")


class CommandRunner:
    """Utility for running shell commands"""

    @staticmethod
    def run(cmd: List[str], capture_output: bool = False, check: bool = True,
            cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """
        Run a shell command

        Args:
            cmd: Command and arguments as list
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero exit
            cwd: Working directory

        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=cwd,
                    check=check
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, cwd=cwd, check=check)
                return result.returncode, "", ""
        except subprocess.CalledProcessError as e:
            if capture_output:
                return e.returncode, e.stdout or "", e.stderr or ""
            return e.returncode, "", ""
        except Exception as e:
            Logger.error(f"Command failed: {e}")
            return 1, "", str(e)

    @staticmethod
    def run_silent(cmd: List[str]) -> bool:
        """Run command silently and return success status"""
        returncode, _, _ = CommandRunner.run(
            cmd,
            capture_output=True,
            check=False
        )
        return returncode == 0


class CertificateGenerator:
    """Handle SSL/TLS certificate generation"""

    def __init__(self, domain: str = Config.DOMAIN, certs_dir: str = Config.CERTS_DIR):
        self.domain = domain
        self.certs_dir = Path(certs_dir)
        self.country = "US"
        self.state = "State"
        self.city = "City"
        self.org = "DevOps Mid Task"
        self.ou = "IT"

    def check_prerequisites(self) -> bool:
        """Check if OpenSSL is available"""
        Logger.header("Checking Prerequisites")

        if not CommandRunner.run_silent(["openssl", "version"]):
            Logger.error("OpenSSL is not installed")
            Logger.info("Install OpenSSL:")
            Logger.info("  Ubuntu/Debian: sudo apt-get install openssl")
            Logger.info("  CentOS/RHEL:   sudo yum install openssl")
            Logger.info("  macOS:         brew install openssl")
            return False

        returncode, stdout, _ = CommandRunner.run(
            ["openssl", "version"],
            capture_output=True
        )
        Logger.success(f"OpenSSL is installed ({stdout.strip()})")
        return True

    def create_certs_directory(self) -> bool:
        """Create certificates directory"""
        Logger.header("Creating Certificates Directory")

        if self.certs_dir.exists():
            Logger.warning(f"Directory '{self.certs_dir}' already exists")
            Logger.info("Using existing directory")
        else:
            self.certs_dir.mkdir(parents=True, exist_ok=True)
            Logger.success(f"Directory created: {self.certs_dir}")

        return True

    def generate_ca_certificate(self) -> bool:
        """Generate CA certificate"""
        Logger.header("Generating CA Certificate")

        ca_key = self.certs_dir / "ca.key"
        ca_crt = self.certs_dir / "ca.crt"

        # Generate CA private key
        Logger.info("Generating CA private key (4096-bit RSA)...")
        returncode, _, stderr = CommandRunner.run(
            ["openssl", "genrsa", "-out", str(ca_key), "4096"],
            capture_output=True,
            check=False
        )
        if returncode != 0:
            Logger.error(f"Failed to generate CA key: {stderr}")
            return False
        Logger.success(f"CA private key generated: {ca_key}")

        # Generate self-signed CA certificate
        Logger.info("Generating self-signed CA certificate...")
        subject = f"/C={self.country}/ST={self.state}/L={self.city}/O={self.org} CA/OU={self.ou}/CN={self.org} Root CA"
        returncode, _, stderr = CommandRunner.run(
            [
                "openssl", "req", "-new", "-x509", "-days", str(Config.CA_DAYS),
                "-key", str(ca_key),
                "-out", str(ca_crt),
                "-subj", subject
            ],
            capture_output=True,
            check=False
        )
        if returncode != 0:
            Logger.error(f"Failed to generate CA certificate: {stderr}")
            return False
        Logger.success(f"CA certificate generated: {ca_crt} (valid for 10 years)")

        return True

    def generate_server_certificate(self) -> bool:
        """Generate server certificate"""
        Logger.header("Generating Server Certificate")

        server_key = self.certs_dir / "server.key"
        server_csr = self.certs_dir / "server.csr"
        server_crt = self.certs_dir / "server.crt"
        server_ext = self.certs_dir / "server.ext"
        ca_key = self.certs_dir / "ca.key"
        ca_crt = self.certs_dir / "ca.crt"

        # Generate server private key
        Logger.info("Generating server private key (2048-bit RSA)...")
        returncode, _, stderr = CommandRunner.run(
            ["openssl", "genrsa", "-out", str(server_key), "2048"],
            capture_output=True,
            check=False
        )
        if returncode != 0:
            Logger.error(f"Failed to generate server key: {stderr}")
            return False
        Logger.success(f"Server private key generated: {server_key}")

        # Generate CSR
        Logger.info("Generating certificate signing request (CSR)...")
        subject = f"/C={self.country}/ST={self.state}/L={self.city}/O={self.org}/OU={self.ou}/CN={self.domain}"
        returncode, _, stderr = CommandRunner.run(
            [
                "openssl", "req", "-new",
                "-key", str(server_key),
                "-out", str(server_csr),
                "-subj", subject
            ],
            capture_output=True,
            check=False
        )
        if returncode != 0:
            Logger.error(f"Failed to generate CSR: {stderr}")
            return False
        Logger.success(f"CSR generated: {server_csr}")

        # Create extensions file
        Logger.info("Creating certificate extensions file...")
        extensions_content = f"""authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = {self.domain}
DNS.2 = *.{self.domain}
DNS.3 = localhost
IP.1 = 127.0.0.1
"""
        server_ext.write_text(extensions_content)
        Logger.success(f"Extensions file created: {server_ext}")

        # Sign server certificate
        Logger.info("Signing server certificate with CA...")
        returncode, _, stderr = CommandRunner.run(
            [
                "openssl", "x509", "-req",
                "-in", str(server_csr),
                "-CA", str(ca_crt),
                "-CAkey", str(ca_key),
                "-CAcreateserial",
                "-out", str(server_crt),
                "-days", str(Config.CERT_DAYS),
                "-sha256",
                "-extfile", str(server_ext)
            ],
            capture_output=True,
            check=False
        )
        if returncode != 0:
            Logger.error(f"Failed to sign certificate: {stderr}")
            return False
        Logger.success(f"Server certificate signed: {server_crt} (valid for {Config.CERT_DAYS} days)")

        return True

    def verify_certificates(self) -> bool:
        """Verify certificate chain"""
        Logger.header("Verifying Certificates")

        ca_crt = self.certs_dir / "ca.crt"
        server_crt = self.certs_dir / "server.crt"

        Logger.info("Verifying certificate chain...")
        returncode, stdout, stderr = CommandRunner.run(
            ["openssl", "verify", "-CAfile", str(ca_crt), str(server_crt)],
            capture_output=True,
            check=False
        )

        if returncode == 0 and "OK" in stdout:
            Logger.success("Certificate chain is valid")
            return True
        else:
            Logger.error(f"Certificate verification failed: {stderr}")
            return False

    def set_permissions(self) -> bool:
        """Set proper file permissions"""
        Logger.header("Setting Permissions")

        # Set private key permissions to 600
        for key_file in self.certs_dir.glob("*.key"):
            key_file.chmod(0o600)
        Logger.success("Private keys secured (600 permissions)")

        # Set other files to 644
        for file in self.certs_dir.glob("*"):
            if file.suffix != ".key" and file.is_file():
                file.chmod(0o644)
        Logger.success("Certificates set to readable (644 permissions)")

        return True

    def create_readme(self) -> bool:
        """Create README in certs directory"""
        readme_path = self.certs_dir / "README.md"
        readme_content = """# SSL/TLS Certificates

This directory contains auto-generated SSL/TLS certificates for development and testing.

## ⚠️ Important

These certificates are **self-signed** and intended for **development/testing only**.

For production, use certificates from a trusted Certificate Authority (e.g., Let's Encrypt, DigiCert).

## Generated Files

- `ca.key` - CA private key (**keep secure, excluded from git**)
- `ca.crt` - CA certificate
- `server.key` - Server private key (**keep secure, excluded from git**)
- `server.crt` - Server certificate (signed by CA)
- `server.csr` - Certificate Signing Request
- `server.ext` - Certificate extensions configuration
- `ca.srl` - Serial number file

## Regenerating Certificates

To regenerate certificates, run:

```bash
python3 deploy.py certs
```

## Security Notes

- Private keys (`*.key`) are excluded from git via `.gitignore`
- Never commit private keys to version control
- Certificates should be regenerated periodically
- Use proper certificates from a trusted CA for production
"""
        readme_path.write_text(readme_content)
        Logger.success(f"README created: {readme_path}")
        return True

    def generate_all(self) -> bool:
        """Generate all certificates"""
        if not self.check_prerequisites():
            return False

        if not self.create_certs_directory():
            return False

        if not self.generate_ca_certificate():
            return False

        if not self.generate_server_certificate():
            return False

        if not self.verify_certificates():
            return False

        if not self.set_permissions():
            return False

        if not self.create_readme():
            return False

        Logger.header("Certificate Generation Complete")
        Logger.success("All certificates generated successfully!")
        print()
        Logger.info(f"Domain:         {self.domain}")
        Logger.info(f"Valid for:      {Config.CERT_DAYS} days (~2.25 years)")
        Logger.info(f"CA valid for:   {Config.CA_DAYS} days (10 years)")
        Logger.info(f"Algorithm:      RSA SHA-256")
        Logger.info(f"Key sizes:      CA: 4096-bit, Server: 2048-bit")
        print()

        return True


class DockerDeployer:
    """Handle Docker image building and container deployment"""

    def __init__(self):
        self.project_dir = Path.cwd()

    def check_docker(self) -> bool:
        """Check if Docker is available"""
        if not CommandRunner.run_silent(["docker", "--version"]):
            Logger.error("Docker is not installed or not running")
            return False
        return True

    def build_images(self) -> bool:
        """Build Docker images"""
        Logger.header("Building Docker Images")

        # Check if Dockerfile exists
        if not (self.project_dir / "Dockerfile").exists():
            Logger.error("Dockerfile not found. Are you in the project root?")
            return False

        # Build webapp image
        Logger.info("Building webapp image...")
        returncode, _, stderr = CommandRunner.run(
            ["docker", "build", "-t", Config.WEBAPP_IMAGE, "."],
            check=False
        )
        if returncode != 0:
            Logger.error(f"Failed to build webapp image: {stderr}")
            return False
        Logger.success("Webapp image built")

        # Build nginx image
        Logger.info("Building nginx image...")
        returncode, _, stderr = CommandRunner.run(
            ["docker", "build", "-f", "nginx/Dockerfile", "-t", Config.NGINX_IMAGE, "."],
            check=False
        )
        if returncode != 0:
            Logger.error(f"Failed to build nginx image: {stderr}")
            return False
        Logger.success("Nginx image built")

        return True

    def create_network(self) -> bool:
        """Create Docker network"""
        Logger.header("Creating Docker Network")

        # Check if network exists
        returncode, stdout, _ = CommandRunner.run(
            ["docker", "network", "inspect", Config.NETWORK_NAME],
            capture_output=True,
            check=False
        )

        if returncode == 0:
            Logger.info(f"Network {Config.NETWORK_NAME} already exists")
            return True

        # Create network
        returncode, _, stderr = CommandRunner.run(
            ["docker", "network", "create", Config.NETWORK_NAME],
            capture_output=True,
            check=False
        )
        if returncode != 0:
            Logger.error(f"Failed to create network: {stderr}")
            return False

        Logger.success(f"Network {Config.NETWORK_NAME} created")
        return True

    def stop_existing_containers(self) -> bool:
        """Stop and remove existing containers"""
        Logger.header("Stopping Existing Containers")

        for container in [Config.WEBAPP_CONTAINER, Config.NGINX_CONTAINER]:
            # Check if container exists
            returncode, stdout, _ = CommandRunner.run(
                ["docker", "ps", "-a", "--filter", f"name={container}", "--format", "{{.Names}}"],
                capture_output=True,
                check=False
            )

            if container in stdout:
                Logger.info(f"Stopping and removing {container}...")
                CommandRunner.run_silent(["docker", "stop", container])
                CommandRunner.run_silent(["docker", "rm", container])
                Logger.success(f"{container} removed")

        return True

    def start_webapp(self) -> bool:
        """Start webapp container"""
        Logger.header("Starting Web Application")

        returncode, _, stderr = CommandRunner.run(
            [
                "docker", "run", "-d",
                "--name", Config.WEBAPP_CONTAINER,
                "--network", Config.NETWORK_NAME,
                "-e", f"API_VERSION={Config.API_VERSION}",
                "-e", "HTTPS_PORT=8443",
                "--restart", "unless-stopped",
                "--health-cmd", "curl -f https://localhost:8443/health || exit 1",
                "--health-interval", "30s",
                "--health-timeout", "3s",
                "--health-retries", "3",
                "--health-start-period", "5s",
                "--label", "com.devops-mid-task.service=webapp",
                Config.WEBAPP_IMAGE
            ],
            capture_output=True,
            check=False
        )

        if returncode != 0:
            Logger.error(f"Failed to start webapp: {stderr}")
            return False

        Logger.success("Webapp container started")
        return True

    def start_nginx(self) -> bool:
        """Start nginx container"""
        Logger.header("Starting Nginx Reverse Proxy")

        returncode, _, stderr = CommandRunner.run(
            [
                "docker", "run", "-d",
                "--name", Config.NGINX_CONTAINER,
                "--network", Config.NETWORK_NAME,
                "-p", f"{Config.HTTP_PORT}:80",
                "-p", f"{Config.HTTPS_PORT}:443",
                "--restart", "unless-stopped",
                "--health-cmd", "wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1",
                "--health-interval", "30s",
                "--health-timeout", "3s",
                "--health-retries", "3",
                "--health-start-period", "10s",
                "--label", "com.devops-mid-task.service=nginx-proxy",
                Config.NGINX_IMAGE
            ],
            capture_output=True,
            check=False
        )

        if returncode != 0:
            Logger.error(f"Failed to start nginx: {stderr}")
            return False

        Logger.success("Nginx container started")
        return True

    def wait_for_health(self) -> bool:
        """Wait for containers to become healthy"""
        Logger.header("Waiting for Services to be Healthy")

        max_attempts = 30

        # Wait for webapp
        Logger.info("Waiting for webapp...")
        for attempt in range(max_attempts):
            returncode, stdout, _ = CommandRunner.run(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", Config.WEBAPP_CONTAINER],
                capture_output=True,
                check=False
            )

            if "healthy" in stdout:
                Logger.success("Webapp is healthy")
                break

            time.sleep(2)
        else:
            Logger.error("Webapp did not become healthy in time")
            CommandRunner.run(["docker", "logs", Config.WEBAPP_CONTAINER])
            return False

        # Wait for nginx
        Logger.info("Waiting for nginx...")
        for attempt in range(max_attempts):
            returncode, stdout, _ = CommandRunner.run(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", Config.NGINX_CONTAINER],
                capture_output=True,
                check=False
            )

            if "healthy" in stdout:
                Logger.success("Nginx is healthy")
                break

            time.sleep(2)
        else:
            Logger.error("Nginx did not become healthy in time")
            CommandRunner.run(["docker", "logs", Config.NGINX_CONTAINER])
            return False

        return True

    def run_tests(self) -> bool:
        """Run health checks"""
        Logger.header("Running Health Checks")

        # Test HTTPS endpoint
        Logger.info("Testing HTTPS endpoint...")
        if CommandRunner.run_silent([
            "curl", "--cacert", "certs/ca.crt", "-sf",
            f"https://localhost:{Config.HTTPS_PORT}/health"
        ]):
            Logger.success("HTTPS endpoint is working")
        else:
            Logger.error("HTTPS endpoint test failed")
            return False

        # Test HTTP redirect
        Logger.info("Testing HTTP redirect...")
        returncode, stdout, _ = CommandRunner.run(
            ["curl", "-I", f"http://localhost:{Config.HTTP_PORT}/health"],
            capture_output=True,
            check=False
        )
        if "location: https" in stdout.lower():
            Logger.success("HTTP redirects to HTTPS")
        else:
            Logger.error("HTTP redirect test failed")
            return False

        # Test all endpoints
        Logger.info("Testing all endpoints...")
        endpoints = ["/", "/health", "/about"]
        for endpoint in endpoints:
            if CommandRunner.run_silent([
                "curl", "--cacert", "certs/ca.crt", "-sf",
                f"https://localhost:{Config.HTTPS_PORT}{endpoint}"
            ]):
                Logger.success(f"GET {endpoint} working")
            else:
                Logger.error(f"GET {endpoint} failed")
                return False

        return True

    def show_status(self):
        """Show deployment status"""
        Logger.header("Deployment Summary")

        print()
        Logger.success("Services are running!")
        print()
        print(f"{Colors.YELLOW}Access URLs:{Colors.NC}")
        print(f"  HTTPS: https://localhost:{Config.HTTPS_PORT}/")
        print(f"  HTTP:  http://localhost:{Config.HTTP_PORT}/ (redirects to HTTPS)")
        print()
        print(f"{Colors.YELLOW}Container Status:{Colors.NC}")
        CommandRunner.run([
            "docker", "ps",
            "--filter", "label=com.devops-mid-task.service",
            "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ])
        print()
        print(f"{Colors.YELLOW}Useful Commands:{Colors.NC}")
        print(f"  View logs:       docker logs -f {Config.WEBAPP_CONTAINER}")
        print(f"                   docker logs -f {Config.NGINX_CONTAINER}")
        print(f"  Stop services:   python3 deploy.py stop")
        print(f"  Run tests:       python3 deploy.py test")
        print(f"  Clean up:        python3 deploy.py clean")
        print()

    def stop_containers(self) -> bool:
        """Stop running containers"""
        Logger.header("Stopping Services")

        for container in [Config.NGINX_CONTAINER, Config.WEBAPP_CONTAINER]:
            CommandRunner.run_silent(["docker", "stop", container])
            CommandRunner.run_silent(["docker", "rm", container])

        Logger.success("Services stopped")
        return True

    def clean_all(self) -> bool:
        """Clean up everything"""
        Logger.header("Cleaning Up")

        # Stop containers
        self.stop_containers()

        # Remove network
        CommandRunner.run_silent(["docker", "network", "rm", Config.NETWORK_NAME])
        Logger.success("Network removed")

        # Remove images
        CommandRunner.run_silent(["docker", "rmi", Config.WEBAPP_IMAGE])
        CommandRunner.run_silent(["docker", "rmi", Config.NGINX_IMAGE])
        Logger.success("Images removed")

        Logger.success("Cleanup complete")
        return True

    def show_container_status(self):
        """Show current container status"""
        Logger.header("Service Status")

        print()
        CommandRunner.run([
            "docker", "ps", "-a",
            "--filter", "label=com.devops-mid-task.service",
            "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ])
        print()


class DeploymentPipeline:
    """Main deployment pipeline orchestrator"""

    def __init__(self):
        self.cert_gen = CertificateGenerator()
        self.deployer = DockerDeployer()

    def generate_certs(self) -> bool:
        """Generate SSL/TLS certificates"""
        return self.cert_gen.generate_all()

    def build(self) -> bool:
        """Build Docker images"""
        if not self.deployer.check_docker():
            return False
        return self.deployer.build_images()

    def start(self) -> bool:
        """Start containers"""
        if not self.deployer.check_docker():
            return False

        if not self.deployer.create_network():
            return False

        if not self.deployer.stop_existing_containers():
            return False

        if not self.deployer.start_webapp():
            return False

        if not self.deployer.start_nginx():
            return False

        if not self.deployer.wait_for_health():
            return False

        return True

    def deploy(self) -> bool:
        """Full deployment pipeline"""
        Logger.header("Starting Deployment Pipeline")
        print()

        # Step 1: Generate certificates
        certs_exist = (Path(Config.CERTS_DIR) / "server.crt").exists()
        if not certs_exist:
            Logger.info("Generating SSL/TLS certificates...")
            if not self.generate_certs():
                Logger.error("Certificate generation failed")
                return False
        else:
            Logger.success("Certificates already exist")

        # Step 2: Check Docker
        if not self.deployer.check_docker():
            return False

        # Step 3: Build images
        if not self.build():
            Logger.error("Build failed")
            return False

        # Step 4: Deploy containers
        if not self.start():
            Logger.error("Deployment failed")
            return False

        # Step 5: Run tests
        if not self.deployer.run_tests():
            Logger.error("Tests failed")
            return False

        # Step 6: Show status
        self.deployer.show_status()

        Logger.header("Deployment Complete")
        Logger.success("All services deployed and tested successfully!")

        return True

    def stop(self) -> bool:
        """Stop all services"""
        return self.deployer.stop_containers()

    def clean(self) -> bool:
        """Clean up everything"""
        return self.deployer.clean_all()

    def test(self) -> bool:
        """Run tests only"""
        return self.deployer.run_tests()

    def status(self):
        """Show status"""
        self.deployer.show_container_status()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Deployment pipeline for golang-webapp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 deploy.py deploy       # Full deployment (certs + build + start + test)
  python3 deploy.py certs        # Generate certificates only
  python3 deploy.py build        # Build Docker images only
  python3 deploy.py start        # Start containers only
  python3 deploy.py stop         # Stop containers
  python3 deploy.py test         # Run health checks
  python3 deploy.py clean        # Remove everything (containers, images, network)
  python3 deploy.py status       # Show current status
        """
    )

    parser.add_argument(
        "action",
        choices=["deploy", "certs", "build", "start", "stop", "test", "clean", "status"],
        help="Action to perform"
    )

    parser.add_argument(
        "--domain",
        default=Config.DOMAIN,
        help=f"Domain for certificates (default: {Config.DOMAIN})"
    )

    args = parser.parse_args()

    # Update domain if specified
    if args.domain != Config.DOMAIN:
        Config.DOMAIN = args.domain

    # Create pipeline
    pipeline = DeploymentPipeline()

    # Execute action
    try:
        if args.action == "deploy":
            success = pipeline.deploy()
        elif args.action == "certs":
            success = pipeline.generate_certs()
        elif args.action == "build":
            success = pipeline.build()
        elif args.action == "start":
            success = pipeline.start()
        elif args.action == "stop":
            success = pipeline.stop()
        elif args.action == "test":
            success = pipeline.test()
        elif args.action == "clean":
            success = pipeline.clean()
        elif args.action == "status":
            pipeline.status()
            success = True
        else:
            parser.print_help()
            sys.exit(1)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print()
        Logger.warning("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
