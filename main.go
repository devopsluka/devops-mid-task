package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

type Response struct {
	Message   string    `json:"message"`
	Timestamp time.Time `json:"timestamp"`
}

type HealthResponse struct {
	Status  string    `json:"status"`
	Uptime  string    `json:"uptime"`
	Version string    `json:"version"`
}

var startTime time.Time
var apiVersion string

func init() {
	startTime = time.Now()

	// Read API version from environment variable, default to "1.0.0"
	apiVersion = os.Getenv("API_VERSION")
	if apiVersion == "" {
		apiVersion = "1.0.0"
	}
}

func homeHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	response := Response{
		Message:   "Welcome to the Mini Go Web App!",
		Timestamp: time.Now(),
	}
	json.NewEncoder(w).Encode(response)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	uptime := time.Since(startTime).String()
	response := HealthResponse{
		Status:  "healthy",
		Uptime:  uptime,
		Version: apiVersion,
	}
	json.NewEncoder(w).Encode(response)
}

func aboutHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	response := Response{
		Message:   "This is a simple Go web application running in Docker",
		Timestamp: time.Now(),
	}
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/", homeHandler)
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/about", aboutHandler)

	// Get certificate and key paths from environment or use defaults
	certFile := os.Getenv("TLS_CERT_FILE")
	if certFile == "" {
		certFile = "certs/server.crt"
	}

	keyFile := os.Getenv("TLS_KEY_FILE")
	if keyFile == "" {
		keyFile = "certs/server.key"
	}

	// Check if certificates exist
	if _, err := os.Stat(certFile); err == nil {
		// Certificates found, start HTTPS server
		httpsPort := os.Getenv("HTTPS_PORT")
		if httpsPort == "" {
			httpsPort = "8443"
		}

		// Configure TLS
		tlsConfig := &tls.Config{
			MinVersion:               tls.VersionTLS12,
			CurvePreferences:         []tls.CurveID{tls.CurveP521, tls.CurveP384, tls.CurveP256},
			PreferServerCipherSuites: true,
			CipherSuites: []uint16{
				tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
				tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
				tls.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,
				tls.TLS_RSA_WITH_AES_256_GCM_SHA384,
				tls.TLS_RSA_WITH_AES_256_CBC_SHA,
			},
		}

		server := &http.Server{
			Addr:         ":" + httpsPort,
			TLSConfig:    tlsConfig,
			ReadTimeout:  15 * time.Second,
			WriteTimeout: 15 * time.Second,
			IdleTimeout:  60 * time.Second,
		}

		fmt.Printf("Server starting with HTTPS on port %s...\n", httpsPort)
		fmt.Printf("API Version: %s\n", apiVersion)
		fmt.Printf("Using TLS certificate: %s\n", certFile)
		log.Fatal(server.ListenAndServeTLS(certFile, keyFile))
	} else {
		// No certificates found, start HTTP server
		httpPort := os.Getenv("HTTP_PORT")
		if httpPort == "" {
			httpPort = "8080"
		}

		fmt.Printf("Server starting with HTTP on port %s...\n", httpPort)
		fmt.Printf("API Version: %s\n", apiVersion)
		fmt.Println("Warning: Running without TLS encryption")
		log.Fatal(http.ListenAndServe(":"+httpPort, nil))
	}
}
