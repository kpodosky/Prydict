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
    
    // Use the working directory where the script is located
    wd, err := os.Getwd()
    if err != nil {
        log.Printf("Error getting working directory: %v", err)
        http.Error(w, "Internal server error", http.StatusInternalServerError)
        return
    }
    
    // Execute Python script with proper path
    cmd := exec.Command("python3", "report bitcoin.py")
    cmd.Dir = wd
    
    // Get the output directly from the Python script
    output, err := cmd.CombinedOutput()
    if err != nil {
        log.Printf("Error executing Python script: %v\nOutput: %s", err, string(output))
        http.Error(w, "Failed to get transactions", http.StatusInternalServerError)
        return
    }

    // Pass through the Python script output directly
    w.Write(output)
}