document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predictionForm');
    const result = document.getElementById('result');

    form.onsubmit = async (e) => {
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
            result.innerHTML = `
                <div class="result-item">
                    <span>Estimated Fee:</span> ${data.fee}
                </div>
                <div class="result-item">
                    <span>Expected Time:</span> ${data.time}
                </div>
            `;
        } catch (error) {
            result.style.display = 'block';
            result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        }
    };
});