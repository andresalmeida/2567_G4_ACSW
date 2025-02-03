document.getElementById('predict-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById('prediction').textContent = result.prediction === 0 ? '<=50K' : '>50K';
        document.getElementById('probability').textContent = result.probability !== null ? result.probability.toFixed(2) : 'N/A';
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
