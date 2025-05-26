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

    // Fee prediction
    const form = document.querySelector('.prediction-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const cryptoType = document.querySelector('.tab-button.active').dataset.tab;
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    cryptoType: cryptoType
                })
            });
            
            const data = await response.json();
            const resultSection = document.querySelector('.result-section');
            resultSection.innerHTML = '';
            
            // Show multiple fee suggestions
            const suggestions = ['fastest', 'fast', 'standard'];
            suggestions.forEach(speed => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                resultItem.innerHTML = `
                    <h3>${speed.toUpperCase()}</h3>
                    <p>Fee: ${data[speed].fee}</p>
                    <p>Estimated Time: ${data[speed].time}</p>
                `;
                resultSection.appendChild(resultItem);
            });
        } catch (error) {
            console.error('Error:', error);
        }
    });
});
