document.addEventListener('DOMContentLoaded', () => {
    // Tab handling
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
    const form = document.querySelector('.prediction-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const cryptoType = document.querySelector('.tab-button.active').dataset.tab;
            const resultSection = document.querySelector('.result-section');
            
            resultSection.innerHTML = '<div>Loading predictions...</div>';
            
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

                Object.entries(data).forEach(([speed, info]) => {
                    const feeBox = document.createElement('div');
                    feeBox.className = 'fee-box';
                    feeBox.innerHTML = `
                        <div class="fee-prediction">
                            <h3>${speed.toUpperCase()}</h3>
                            <p class="fee">Fee: ${info.fee}</p>
                            <p class="time">Expected Time: ${info.time}</p>
                        </div>
                    `;
                    resultSection.appendChild(feeBox);
                });
            } catch (error) {
                console.error('Error:', error);
                resultSection.innerHTML = '<div class="error-message">Failed to fetch fee predictions</div>';
            }
        });
    }
});
