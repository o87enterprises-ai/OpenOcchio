// script.js – OpenOcchio Mobile PWA

// IMPORTANT: Replace this with your actual Hugging Face Space URL
const API_URL = "https://YOUR-HF-USERNAME-openocchio-api.hf.space/confidence";

const form = document.getElementById('confidence-form');
const input = document.getElementById('prompt-input');
const resultDiv = document.getElementById('result');
const submitBtn = document.getElementById('submit-btn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = input.value.trim();
    if (!prompt) return;

    // UI Feedback
    setLoading(true);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt, model: "llama3-8b-8192" })
        });

        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        displayResult(data);
    } catch (err) {
        displayError(err.message);
    } finally {
        setLoading(false);
    }
});

function setLoading(isLoading) {
    if (isLoading) {
        submitBtn.disabled = true;
        resultDiv.innerHTML = `
            <div class="loader"></div>
            <div class="status-msg">Analyzing confidence...</div>
        `;
    } else {
        submitBtn.disabled = false;
    }
}

function displayResult(data) {
    const confidence = data.confidence;
    let label = '';
    let color = '';

    if (confidence >= 0.8) {
        label = 'High Confidence';
        color = 'var(--success)';
    } else if (confidence >= 0.5) {
        label = 'Moderate Confidence';
        color = 'var(--warning)';
    } else {
        label = 'Low Confidence';
        color = 'var(--danger)';
    }

    resultDiv.innerHTML = `
        <div class="score-container">
            <div class="score-circle" style="border-color: ${color}">
                <div class="score-value" style="color: ${color}">${(confidence * 100).toFixed(0)}%</div>
                <div class="score-label" style="color: ${color}">${label}</div>
            </div>
            <div class="meta-info">
                Model: ${data.model}<br>
                Method: ${data.method}
            </div>
        </div>
    `;
}

function displayError(message) {
    resultDiv.innerHTML = `
        <div class="error-msg" style="color: var(--danger)">
            <strong>Error:</strong> ${message}<br>
            <small>Check if the backend is running and the URL is correct.</small>
        </div>
    `;
}
