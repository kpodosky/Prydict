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
            const data = await response.json();
            
            const container = document.querySelector('.whale-transactions');
            
            data.transactions.forEach(tx => {
                const alert = document.createElement('div');
                alert.className = 'whale-alert';
                alert.innerHTML = `
================================================================================
🚨 Bitcoin ${tx.type} Alert! ${tx.timestamp}
Hash: ${tx.hash}
${tx.amount} BTC        Fee: ${tx.fee} BTC
From: ${tx.from_address} (${tx.from_label})
    History: ${tx.from_history}
To: ${tx.to_address} (${tx.to_label})
    History: ${tx.to_history}
================================================================================`;
                
                container.insertBefore(alert, container.firstChild);
            });
            
            // Keep only last 50 transactions
            const alerts = container.querySelectorAll('.whale-alert');
            if (alerts.length > 50) {
                alerts.forEach((alert, index) => {
                    if (index >= 50) alert.remove();
                });
            }
        } catch (error) {
            console.error('Error fetching whale transactions:', error);
        }
    }

    // Update interval to 90 seconds (1.5 minutes)
    whaleUpdateInterval = setInterval(updateWhaleTransactions, 90000);
});