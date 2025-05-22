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
    
    // Create transaction data structure
    txData := map[string]interface{}{
        "transactions": []map[string]string{
            {
                "type": "INTERNAL TRANSFER",
                "timestamp": "2025-05-22 14:30:25",
                "hash": "0x7a23c98ff44b3214567890abcdef123456789012345678901234567890abcdef",
                "amount": "235.45 BTC",
                "amount_usd": "$7,063,500.00",
                "fee": "0.00034521 BTC",
                "fee_usd": "$10.35",
                "from_address": "3FaA4dJuuvJFyUHbqHLkZKJcuDPugvG3zE",
                "from_label": "BINANCE",
                "from_history": "(BINANCE EXCHANGE) [↑1234|↓789] Total: ↑45678.23|↓34567.12 BTC",
                "to_address": "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",
                "to_label": "GEMINI",
                "to_history": "(GEMINI EXCHANGE) [↑567|↓890] Total: ↑23456.78|↓12345.67 BTC",
                "market_impact": "≈0.15% of 24h volume",
                "analysis": "⚪ SIGNIFICANT internal movement - Exchange rebalancing",

                "stats": "Processed 2,453 transactions, found 1 whale movements",
            },
        },
    }

    // Return formatted JSON
    if err := json.NewEncoder(w).Encode(txData); err != nil {
        log.Printf("Error encoding response: %v", err)
        http.Error(w, "Failed to encode response", http.StatusInternalServerError)
        return
    }
}