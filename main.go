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
    
    // Initialize whale tracker if not already running
    tracker.Start()
    w.WriteHeader(http.StatusOK)
}

func handleWhaleStop(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }
    
    tracker.Stop()
    w.WriteHeader(http.StatusOK)
}

func handleWhaleTransactions(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]interface{}{
        "transactions": tracker.GetTransactions(),
    })
}