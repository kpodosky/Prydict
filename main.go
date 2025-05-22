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
    
    // Use correct path without quotes for space in filename
    cmd := exec.Command("python3", "report bitcoin.py")
    
    // Get absolute path to the project directory
    projectDir := "/home/kilanko/APPs/prydict"
    cmd.Dir = projectDir
    
    output, err := cmd.CombinedOutput()
    if err != nil {
        log.Printf("Error executing Python script: %v\nOutput: %s", err, string(output))
        log.Printf("Working directory: %s", projectDir)
        // Fall back to dummy data on error
        dummyData := map[string]interface{}{
            "transactions": []map[string]string{
                {
                    "type": "INTERNAL TRANSFER",
                    "timestamp": "2025-05-22 14:30:25",
                    "hash": "0x7a23c98ff44b3214567890abcdef123456789012345678901234567890abcdef",
                    "amount": "235.45 BTC",
                    "from_address": "3FaA4dJuuvJFyUHbqHLkZKJcuDPugvG3zE",
                    "from_label": "Coinbase",
                    "to_address": "1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s",
                    "to_label": "Gemini",
                },
            },
        }
        json.NewEncoder(w).Encode(dummyData)
        return
    }

    // Log the output for debugging
    log.Printf("Raw Python output: %s", string(output))
}