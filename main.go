package main

import (
    "html/template"
    "log"
    "net/http"
)

type PageData struct {
    Title string
    Form  PredictionForm
}

type PredictionForm struct {
    BTCAmount  float64
    TxSize     string
    ETHAmount  float64
    GasLimit   string
    USDCAmount float64
    USDTAmount float64
}

func main() {
    // Serve static files
    fs := http.FileServer(http.Dir("static"))
    http.Handle("/static/", http.StripPrefix("/static/", fs))

    // Serve static files
    fs = http.FileServer(http.Dir("static"))
    http.Handle("/static/", http.StripPrefix("/static/", fs))

    // Routes
    http.HandleFunc("/", handleHome)
    http.HandleFunc("/predict/btc", handleBTCPrediction)
    http.HandleFunc("/predict/eth", handleETHPrediction)

    log.Println("Server starting on http://localhost:8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

func handleHome(w http.ResponseWriter, r *http.Request) {
    tmpl := template.Must(template.ParseFiles("templates/layout.html"))
    data := PageData{
        Title: "Prydict - Crypto Fee Predictor",
        Form:  PredictionForm{},
    }
    tmpl.Execute(w, data)
}

func handleBTCPrediction(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Redirect(w, r, "/", http.StatusSeeOther)
        return
    }
    // TODO: Implement BTC prediction logic
}

func handleETHPrediction(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Redirect(w, r, "/", http.StatusSeeOther)
        return
    }
    // TODO: Implement ETH prediction logic
}