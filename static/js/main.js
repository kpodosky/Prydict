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
    const whaleTab = document.getElementById('whale');
    if (whaleTab) {
        const form = whaleTab.querySelector('form');
        const resultSection = document.createElement('div');
        resultSection.className = 'whale-transactions';
        whaleTab.appendChild(resultSection);

        let isTracking = false;
        let trackingInterval;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const button = form.querySelector('button');

            if (!isTracking) {
                // Start tracking
                try {
                    await fetch('/whale-watch/start', { method: 'POST' });
                    button.textContent = 'Stop Tracking';
                    isTracking = true;
                    
                    // Poll for new transactions
                    trackingInterval = setInterval(async () => {
                        const response = await fetch('/whale-watch/transactions');
                        const data = await response.json();
                        if (data.output) {
                            const alert = document.createElement('div');
                            alert.className = 'whale-alert';
                            alert.style.whiteSpace = 'pre-wrap';
                            alert.style.fontFamily = 'monospace';
                            alert.innerHTML = data.output;
                            resultSection.insertBefore(alert, resultSection.firstChild);
                        }
                    }, 30000); // Check every 30 seconds
                } catch (error) {
                    console.error('Error:', error);
                }
            } else {
                // Stop tracking
                try {
                    await fetch('/whale-watch/stop', { method: 'POST' });
                    button.textContent = 'Track Whales';
                    isTracking = false;
                    clearInterval(trackingInterval);
                } catch (error) {
                    console.error('Error:', error);
                }
            }
        });
    }
});
