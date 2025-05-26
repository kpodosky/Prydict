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
    const forms = document.querySelectorAll('.prediction-form');
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const tabId = form.closest('.tab-content').id;
            const priority = form.querySelector('select[name="priority"]').value;
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        cryptoType: tabId,
                        priority: priority
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                displayPredictions(data, tabId);
            } catch (error) {
                console.error('Error:', error);
                const resultSection = form.nextElementSibling;
                resultSection.innerHTML = '<div class="error">Failed to fetch fee predictions. Please try again.</div>';
            }
        });
    });
    
    function displayPredictions(predictions, cryptoType) {
        const resultSection = document.querySelector(`#${cryptoType} .result-section`);
        resultSection.innerHTML = '';
        
        Object.entries(predictions).forEach(([speed, info]) => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';
            resultItem.innerHTML = `
                <h3>${speed.toUpperCase()}</h3>
                <p>Fee: ${info.fee}</p>
                <p>Estimated Time: ${info.time}</p>
            `;
            resultSection.appendChild(resultItem);
        });
    }
});
