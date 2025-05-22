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
});