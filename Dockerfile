# Build stage
FROM golang:1.21-alpine AS builder

# Set working directory
WORKDIR /app

# Copy go mod files
COPY go.mod ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Production stage
FROM alpine:latest

# Install ca-certificates and curl for HTTPS health checks
RUN apk --no-cache add ca-certificates curl

WORKDIR /root/

# Copy the binary from builder
COPY --from=builder /app/main .

# Create certs directory
RUN mkdir -p /root/certs

# Copy certificates (server cert and key only, not CA private key)
COPY certs/server.crt /root/certs/
COPY certs/server.key /root/certs/
COPY certs/ca.crt /root/certs/

# Trust the CA certificate in the system trust store
# This allows curl and other tools to verify our self-signed certificates
COPY certs/ca.crt /usr/local/share/ca-certificates/devops-mid-task-ca.crt
RUN update-ca-certificates

# Expose ports (8080 for HTTP, 8443 for HTTPS)
EXPOSE 8080 8443

# Set API version environment variable
ENV API_VERSION=1.0.0

# Health check (using HTTPS - CA certificate is now trusted)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f https://localhost:8443/health || exit 1

# Run the application
CMD ["./main"]
