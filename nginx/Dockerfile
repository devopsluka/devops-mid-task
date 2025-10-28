FROM nginx:alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/webapp.conf

# Create directory for SSL certificates
RUN mkdir -p /etc/nginx/certs

# Copy SSL certificates
COPY certs/server.crt /etc/nginx/certs/
COPY certs/server.key /etc/nginx/certs/
COPY certs/ca.crt /etc/nginx/certs/

# Trust the CA certificate in the system trust store
# This allows health checks and internal tools to verify our self-signed certificates
COPY certs/ca.crt /usr/local/share/ca-certificates/devops-mid-task-ca.crt
RUN update-ca-certificates

# Create log directory
RUN mkdir -p /var/log/nginx

# Expose ports
EXPOSE 80 443

# Health check
# Check that nginx is responding (don't follow redirects to avoid port issues)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --spider --server-response --max-redirect=0 http://localhost:80/ 2>&1 | grep -q "HTTP/" && exit 0 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
