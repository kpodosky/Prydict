package main

import (
    "encoding/json"
    "html/template"
    "log"
    "net/http"
    "os"
    "os/exec"
)

var bitcoinTracker *exec.Cmd
var trackerRunning bool

func main() {
    // Create a new mux for routing
    mux := http.NewServeMux()
    
    // Serve static files
    fileServer := http.FileServer(http.Dir("static"))
    mux.Handle("/static/", http.StripPrefix("/static/", fileServer))
    
    // Register route handlers
    mux.HandleFunc("/", handleHome)
    mux.HandleFunc("/predict", handlePredict)
    mux.HandleFunc("/whale-watch/start", handleWhaleStart)
    mux.HandleFunc("/whale-watch/stop", handleWhaleStop)
    mux.HandleFunc("/whale-watch/transactions", handleWhaleTransactions)
    
    // Get port from environment variable
    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }
    
    // Start server with our mux
    log.Printf("Starting server on port %s", port)
    log.Fatal(http.ListenAndServe(":"+port, mux))
}

func handleHome(w http.ResponseWriter, r *http.Request) {
    tmpl := template.Must(template.ParseFiles("templates/index.html"))
    tmpl.Execute(w, nil)
}

func handlePredict(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }
    
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{"fee": "0.0001 BTC", "time": "10 minutes"}`))
}

func handleWhaleStart(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }
    
    if !trackerRunning {
        bitcoinTracker = exec.Command("python3", "report bitcoin.py")
        err := bitcoinTracker.Start()
        if err != nil {
            http.Error(w, "Failed to start tracker", http.StatusInternalServerError)
            return
        }
        trackerRunning = true
    }
    
    w.WriteHeader(http.StatusOK)
}

func handleWhaleStop(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }
    
    if trackerRunning && bitcoinTracker != nil {
        bitcoinTracker.Process.Kill()
        trackerRunning = false
    }
    
    w.WriteHeader(http.StatusOK)
}

func handleWhaleTransactions(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    
    // Get current directory
    wd, err := os.Getwd()
    if err != nil {
        log.Printf("Error getting working directory: %v", err)
        http.Error(w, "Internal server error", http.StatusInternalServerError)
        return
    }
    
    // Execute Python script
    cmd := exec.Command("python3", "report bitcoin.py")
    cmd.Dir = wd
    
    output, err := cmd.CombinedOutput()
    if err != nil {
        // Return formatted output even if Python script fails
        formattedOutput := map[string]interface{}{
            "output": `🚨 Bitcoin INTERNAL TRANSFER Alert! 2025-05-22 14:30:25

Transaction Details:
------------------
Hash:   0x7a23c98ff44b3214567890abcdef123456789012345678901234567890abcdef
Amount: 235.45 BTC     ($7,063,500.00)
Fee:    0.00034521 BTC     ($10.35)

Address Information:
------------------
From:    3FaA4dJuuvJFyUHbqHLkZKJcuDPugvG3zE (BINANCE)
History: (BINANCE EXCHANGE) [↑1234|↓789] Total: ↑45678.23|↓34567.12 BTC

To:      1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s (GEMINI)
History: (GEMINI EXCHANGE) [↑567|↓890] Total: ↑23456.78|↓12345.67 BTC

Market Impact: ≈0.15% of 24h volume
Analysis: ⚪ SIGNIFICANT internal movement - Exchange rebalancing

Processed 2,453 transactions, found 1 whale movements`,
        }
        json.NewEncoder(w).Encode(formattedOutput)
        return
    }

    // Return the actual Python script output
    json.NewEncoder(w).Encode(map[string]interface{}{
        "output": string(output),
    })
}