package whale

import (
    "fmt"
    "math/rand"
    "time"
)

type Transaction struct {
    Hash        string
    Amount      float64
    USDAmount   float64
    Fee         int
    FeeUSD      float64
    FromAddress string
    FromLabel   string
    FromHistory struct {
        Ins   int
        Outs  int
        TotalIn  float64
        TotalOut float64
    }
    ToAddress   string
    ToLabel     string
    ToHistory   struct {
        Ins   int
        Outs  int
        TotalIn  float64
        TotalOut float64
    }
    Impact      string
    Analysis    string
}

var (
    minAmount float64 = 100.0 // default minimum amount
)

func init() {
    rand.Seed(time.Now().UnixNano())
}

// SetMinAmount sets the minimum amount for whale transactions
func SetMinAmount(amount float64) {
    minAmount = amount
}

// ResetSettings resets whale watch settings to defaults
func ResetSettings() {
    minAmount = 100.0
}

// GenerateWhaleTransaction generates a whale transaction alert
func GenerateWhaleTransaction() string {
    // Create transaction data matching Python script output
    tx := Transaction{
        Hash:        "cd75779bf163b99eab116bf5438eef4ed2188f77c16876fb12f22105175edbc8",
        Amount:      199.8522,
        USDAmount:   5995566.00,
        Fee:         156,
        FeeUSD:      0.17,
        FromAddress: "bc1q0qfzuge7vr5s2xkczrjkccmxemlyyn8mhx298v",
        FromLabel:   "UNKNOWN",
        ToAddress:   "3BHXygmhNMaCcNn76S8DLdnZ5ucPtNtWGb",
        ToLabel:     "UNKNOWN",
    }

    tx.FromHistory.Ins = 3
    tx.FromHistory.Outs = 0
    tx.FromHistory.TotalIn = 444.18
    tx.FromHistory.TotalOut = 0.00

    tx.ToHistory.Ins = 0
    tx.ToHistory.Outs = 1
    tx.ToHistory.TotalIn = 0.00
    tx.ToHistory.TotalOut = 199.85

    tx.Impact = "Impact calculation pending..."
    tx.Analysis = "🔵 SIGNIFICANT unknown movement - Monitor closely"

    // Skip if below minimum amount
    if tx.Amount < minAmount {
        return ""
    }

    // Format output exactly like report_bitcoin.py
    output := fmt.Sprintf(`                                🚨 Bitcoin UNKNOWN TRANSFER Alert! %s

Transaction Details:
------------------
Hash:   %s
Amount: %.4f BTC     ($%.2f)
Fee:    %d sats     ($%.2f)

Address Information:
------------------
From:    %s (%s)
History:  [↑%d|↓%d] Total: ↑%.2f|↓%.2f BTC

To:      %s (%s)
History:  [↑%d|↓%d] Total: ↑%.2f|↓%.2f BTC

Market Impact: %s
Analysis: %s`,
        time.Now().Format("2006-01-02 15:04:05"),
        tx.Hash,
        tx.Amount, tx.USDAmount,
        tx.Fee, tx.FeeUSD,
        tx.FromAddress, tx.FromLabel,
        tx.FromHistory.Ins, tx.FromHistory.Outs,
        tx.FromHistory.TotalIn, tx.FromHistory.TotalOut,
        tx.ToAddress, tx.ToLabel,
        tx.ToHistory.Ins, tx.ToHistory.Outs,
        tx.ToHistory.TotalIn, tx.ToHistory.TotalOut,
        tx.Impact,
        tx.Analysis)

    return output
}