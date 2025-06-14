document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });

    // Fee prediction
    document.querySelectorAll('.prediction-form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const cryptoType = e.target.closest('.tab-content').id;
            const resultSection = e.target.nextElementSibling;
            resultSection.style.display = 'block';
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        cryptoType: cryptoType,
                        priority: 'all'
                    })
                });

                if (!response.ok) throw new Error('Network response was not ok');
                
                const data = await response.json();
                resultSection.innerHTML = '';

                // Create result grid
                const grid = document.createElement('div');
                grid.className = 'result-grid';

                // Display all fee predictions
                Object.entries(data).forEach(([speed, info]) => {
                    const item = document.createElement('div');
                    item.className = 'result-item';
                    item.innerHTML = `
                        <strong>${speed.toUpperCase()}</strong>
                        <div>Fee: ${info.fee}</div>
                        <div>Time: ${info.time}</div>
                    `;
                    grid.appendChild(item);
                });

                resultSection.appendChild(grid);
                resultSection.style.display = 'block';

            } catch (error) {
                resultSection.innerHTML = '<div class="error">Failed to fetch predictions</div>';
            }
        });
        
    });

    // Whale Watch functionality
    const whaleWatchTab = document.querySelector('#whale');
    if (whaleWatchTab) {
        const whaleForm = whaleWatchTab.querySelector('form');
        const whaleTransactions = whaleWatchTab.querySelector('.whale-transactions');
        let isTracking = false;
        let trackingInterval;

        // Initial fetch to show transactions immediately
        async function fetchTransactions(minAmount) {
            try {
                const response = await fetch(`/whale-watch/transactions?minAmount=${minAmount}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                if (data.output) {
                    const txDiv = document.createElement('div');
                    txDiv.className = 'whale-alert';
                    txDiv.style.whiteSpace = 'pre-wrap';
                    txDiv.style.fontFamily = 'monospace';
                    
                    // Format the output with colors
                    const formattedOutput = data.output
                        .replace(/🟢/g, '<span style="color: #28a745">🟢</span>')
                        .replace(/🟡/g, '<span style="color: #ffc107">🟡</span>')
                        .replace(/⚪/g, '<span style="color: #6c757d">⚪</span>')
                        .replace(/🔵/g, '<span style="color: #17a2b8">🔵</span>')
                        .replace(/↑/g, '<span style="color: #28a745">↑</span>')
                        .replace(/↓/g, '<span style="color: #dc3545">↓</span>');
                    
                    txDiv.innerHTML = formattedOutput;
                    whaleTransactions.insertBefore(txDiv, whaleTransactions.firstChild);
                }
            } catch (error) {
                console.error('Error fetching transactions:', error);
                whaleTransactions.innerHTML = '<div class="error">Failed to fetch whale transactions</div>';
            }
        }

        whaleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const button = whaleForm.querySelector('button');
            const minAmount = document.getElementById('minAmount').value;

            if (!isTracking) {
                button.textContent = 'Stop Tracking';
                isTracking = true;
                whaleTransactions.innerHTML = '<div>Starting whale watch...</div>';
                
                // Initial fetch
                await fetchTransactions(minAmount);
                
                // Set up polling
                trackingInterval = setInterval(() => fetchTransactions(minAmount), 30000);
            } else {
                button.textContent = 'Start Whale Watch';
                isTracking = false;
                clearInterval(trackingInterval);
                whaleTransactions.insertBefore(
                    document.createElement('div')
                        .appendChild(document.createTextNode('Whale tracking stopped')),
                    whaleTransactions.firstChild
                );
            }
        });
    }
});
