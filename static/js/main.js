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
});
