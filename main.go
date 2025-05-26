package main

import (
    "encoding/json"
    "html/template"
    "log"
    "net/http"
    "os"
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
    
    // Parse the request body to get the cryptocurrency type
    var request struct {
        CryptoType string `json:"cryptoType"`
        Priority   string `json:"priority"`
    }
    
    if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    
    // Define the fee prediction type
    type FeeInfo struct {
        Fee  string `json:"fee"`
        Time string `json:"time"`
    }
    
    // Different predictions based on cryptocurrency type
    switch request.CryptoType {
    case "ethereum":
        predictions := map[string]FeeInfo{
            "fastest":   {"250 GWEI", "15 seconds"},
            "fast":      {"150 GWEI", "30 seconds"},
            "standard":  {"100 GWEI", "2 minutes"},
            "economic":  {"80 GWEI", "5 minutes"},
            "minimum":   {"50 GWEI", "10 minutes"},
        }
        json.NewEncoder(w).Encode(predictions)
    default:
        // Bitcoin and other predictions remain unchanged
        predictions := map[string]FeeInfo{
            "fastest":   {"0.00050 BTC", "1-2 minutes"},
            "fast":      {"0.00030 BTC", "3-5 minutes"},
            "standard":  {"0.00020 BTC", "10-20 minutes"},
            "economic":  {"0.00015 BTC", "30-60 minutes"},
            "minimum":   {"0.00010 BTC", "1-2 hours"},
        }
        json.NewEncoder(w).Encode(predictions)
    }
}