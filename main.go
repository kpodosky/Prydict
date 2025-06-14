package main

import (
    "encoding/json"
    "html/template"
    "log"
    "net/http"
    "os"

    "prydict/whale"
)

func main() {
    // Create a new mux for routing
    mux := http.NewServeMux()

    // Serve static files
    fileServer := http.FileServer(http.Dir("static"))
    mux.Handle("/static/", http.StripPrefix("/static/", fileServer))

    // Register route handlers
    mux.HandleFunc("/", handleHome)
    mux.HandleFunc("/predict", handlePredict)
    // Add whale watch endpoints
    mux.HandleFunc("/whale-watch/start", handleWhaleWatchStart)
    mux.HandleFunc("/whale-watch/stop", handleWhaleWatchStop)
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

    // Parse the request body
    var request struct {
        CryptoType string `json:"cryptoType"`
        Priority   string `json:"priority"`
    }

    if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    // Define the fee prediction type
    type FeeInfo struct {
        Fee  string `json:"fee"`
        Time string `json:"time"`
    }

    // Different predictions based on cryptocurrency type
    var predictions map[string]FeeInfo

    switch request.CryptoType {
    case "ethereum":
        predictions = map[string]FeeInfo{
            "fastest":   {"250 GWEI", "15 seconds"},
            "fast":      {"150 GWEI", "30 seconds"},
            "standard":  {"100 GWEI", "2 minutes"},
            "economic":  {"80 GWEI", "5 minutes"},
            "minimum":   {"50 GWEI", "10 minutes"},
        }
    case "bitcoin":
        predictions = map[string]FeeInfo{
            "fastest":   {"50,000 sats", "1-2 minutes"},
            "fast":      {"30,000 sats", "3-5 minutes"},
            "standard":  {"20,000 sats", "10-20 minutes"},
            "economic":  {"15,000 sats", "30-60 minutes"},
            "minimum":   {"10,000 sats", "1-2 hours"},
        }
    case "usdt":
        predictions = map[string]FeeInfo{
            "fastest":   {"100 GWEI", "15 seconds"},
            "fast":      {"80 GWEI", "30 seconds"},
            "standard":  {"60 GWEI", "1 minute"},
            "economic":  {"40 GWEI", "3 minutes"},
            "minimum":   {"20 GWEI", "5 minutes"},
        }
    case "usdc":
        predictions = map[string]FeeInfo{
            "fastest":   {"100 GWEI", "15 seconds"},
            "fast":      {"80 GWEI", "30 seconds"},
            "standard":  {"60 GWEI", "1 minute"},
            "economic":  {"40 GWEI", "3 minutes"},
            "minimum":   {"20 GWEI", "5 minutes"},
        }
    default:
        http.Error(w, "Unsupported cryptocurrency type", http.StatusBadRequest)
        return
    }

    if err := json.NewEncoder(w).Encode(predictions); err != nil {
        http.Error(w, "Failed to encode response", http.StatusInternalServerError)
        return
    }
}

func handleWhaleTransactions(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodGet {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }

    w.Header().Set("Content-Type", "application/json")

    // Generate whale transaction output using whale.go directly
    output := whale.GenerateWhaleTransaction()

    response := map[string]string{
        "output": output,
    }

    if err := json.NewEncoder(w).Encode(response); err != nil {
        log.Printf("Error encoding response: %v", err)
        http.Error(w, "Failed to encode response", http.StatusInternalServerError)
        return
    }
}

func handleWhaleWatchStart(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }

    // Parse form data
    var request struct {
        MinAmount float64    `json:"minAmount"`
        TxTypes   []string   `json:"txTypes"`
    }

    if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
        http.Error(w, "Invalid request format", http.StatusBadRequest)
        return
    }

    // Set minimum amount for whale transactions
    whale.SetMinAmount(request.MinAmount)

    w.WriteHeader(http.StatusOK)
}

func handleWhaleWatchStop(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }

    // Reset whale watch settings
    whale.ResetSettings()

    w.WriteHeader(http.StatusOK)
}