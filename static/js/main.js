document.addEventListener('DOMContentLoaded', () => {
    // Tab handling
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            
            // Update active states
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(target).classList.add('active');
            
            // Reset result display when switching tabs
            const result = document.getElementById('result');
            result.style.display = 'none';
        });
    });

    // Form submissions
    const forms = document.querySelectorAll('.prediction-form');
    const result = document.getElementById('result');

    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const formData = new FormData(form);
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                result.style.display = 'block';
                
                // Update all result fields
                result.querySelector('.fee').textContent = data.fee;
                result.querySelector('.time').textContent = data.time;
                result.querySelector('.network').textContent = data.network;
                result.querySelector('.probability').textContent = data.probability;
                result.querySelector('.block').textContent = data.block;
                result.querySelector('.confirmation').textContent = data.confirmation;
                result.querySelector('.impact').textContent = data.impact;
            } catch (error) {
                result.style.display = 'block';
                result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        });
    });

    // Add whale watching functionality
    let whaleWatchActive = false;
    let whaleUpdateInterval;

    document.querySelector('#whale .prediction-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const button = e.target.querySelector('.whale-button');
        const container = document.querySelector('.whale-container');
        
        if (!whaleWatchActive) {
            // Start whale watching
            try {
                const formData = new FormData(e.target);
                const response = await fetch('/whale-watch/start', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) throw new Error('Failed to start whale watch');
                
                whaleWatchActive = true;
                button.textContent = 'Stop Tracking';
                container.style.display = 'block';
                
                // Start periodic updates
                whaleUpdateInterval = setInterval(updateWhaleTransactions, 90000); // 1.5 minutes
                updateWhaleTransactions(); // Initial update
                
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to start whale watching');
            }
        } else {
            // Stop whale watching
            try {
                await fetch('/whale-watch/stop', { method: 'POST' });
                clearInterval(whaleUpdateInterval);
                whaleWatchActive = false;
                button.textContent = 'Start Tracking';
                container.style.display = 'none';
            } catch (error) {
                console.error('Error:', error);
            }
        }
    });

    async function updateWhaleTransactions() {
        if (!whaleWatchActive) return;
        
        try {
            const response = await fetch('/whale-watch/transactions');
            const transactions = await response.json();
            
            if (transactions.length > 0) {
                const container = document.querySelector('.whale-transactions');
                
                transactions.forEach(tx => {
                    const txElement = document.createElement('div');
                    txElement.className = 'whale-transaction';
                    
                    // Determine transaction type color
                    const typeColors = {
                        'DEPOSIT': '#28a745',
                        'WITHDRAWAL': '#dc3545',
                        'INTERNAL TRANSFER': '#ffc107',
                        'UNKNOWN TRANSFER': '#17a2b8'
                    };
                    
                    txElement.innerHTML = `
                        <div class="tx-header" style="color: ${typeColors[tx.tx_type] || '#17a2b8'}">
                            🚨 Bitcoin ${tx.tx_type} Alert! ${tx.timestamp}
                        </div>
                        <div class="tx-hash">Hash: ${tx.transaction_hash}</div>
                        <div class="tx-amount">
                            ${tx.btc_volume} BTC        Fee: ${tx.fee_btc} BTC
                        </div>
                        <div class="tx-from">
                            From: ${tx.sender} ${tx.from_entity ? `(${tx.from_entity.name.toUpperCase()} ${tx.from_entity.type})` : ''}
                            <div class="tx-history">
                                History: [↑${tx.sender_stats.sent_count}|↓${tx.sender_stats.received_count}] 
                                Total: ↑${tx.sender_stats.total_sent}|↓${tx.sender_stats.total_received} BTC
                            </div>
                        </div>
                        <div class="tx-to">
                            To: ${tx.receiver} ${tx.to_entity ? `(${tx.to_entity.name.toUpperCase()} ${tx.to_entity.type})` : ''}
                            <div class="tx-history">
                                History: [↑${tx.receiver_stats.sent_count}|↓${tx.receiver_stats.received_count}] 
                                Total: ↑${tx.receiver_stats.total_sent}|↓${tx.receiver_stats.total_received} BTC
                            </div>
                        </div>
                        <div class="tx-separator"></div>
                    `;
                    
                    container.insertBefore(txElement, container.firstChild);
                    
                    // Keep max 50 transactions in view
                    if (container.children.length > 50) {
                        container.removeChild(container.lastChild);
                    }
                });
            }
        } catch (error) {
            console.error('Error fetching whale transactions:', error);
        }
    }

    // Update interval to 90 seconds (1.5 minutes)
    whaleUpdateInterval = setInterval(updateWhaleTransactions, 90000);
});