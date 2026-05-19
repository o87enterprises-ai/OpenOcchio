// script.js – OpenOcchio Mobile PWA

// IMPORTANT: Replace this with your actual Hugging Face Space URL
const API_URL = "https://YOUR-HF-USERNAME-openocchio-api.hf.space/confidence";

const form = document.getElementById('confidence-form');
const input = document.getElementById('prompt-input');
const resultDiv = document.getElementById('result');
const submitBtn = document.getElementById('submit-btn');
const modeBtns = document.querySelectorAll('.mode-btn');

let currentMode = 'generate';

// Mode Switching
modeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        modeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentMode = btn.dataset.mode;
        
        // Update placeholder
        if (currentMode === 'generate') {
            input.placeholder = "Ask a question to see AI confidence...";
        } else {
            input.placeholder = "Paste an AI response here to analyze its confidence markers...";
        }
    });
});

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
            body: JSON.stringify({ 
                prompt: prompt, 
                mode: currentMode,
                model: "llama3-8b-8192" 
            })
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
        console.warn("API Error, falling back to Demo Mode:", err.message);
        // DEMO MODE: Generate a random confidence score for preview purposes
        const mockConfidence = Math.random();
        displayResult({
            confidence: mockConfidence,
            model: "demo-model-v1",
            method: "demo-mode-simulation"
        });
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
    let state = '';
    let color = '';

    // State Logic (matches component spec)
    // High confidence (0.8 - 1.0) -> Truth
    // Medium confidence (0.4 - 0.79) -> Unsure
    // Low confidence (0.0 - 0.39) -> Lie
    if (confidence >= 0.8) {
        state = 'truth';
        label = 'Truth';
        color = 'var(--truth-green)';
    } else if (confidence >= 0.4) {
        state = 'uncertain';
        label = 'Unsure';
        color = 'var(--uncertain-yellow)';
    } else {
        state = 'lie';
        label = 'Lie';
        color = 'var(--lie-red)';
    }

    // Map confidence to nose width (High conf 1.0 = short nose, Low conf 0.0 = long nose)
    // Range: 24px (min) to 140px (max)
    const inverseConf = 1.0 - confidence;
    const noseWidth = 24 + (inverseConf * 116);

    resultDiv.innerHTML = `
        <div class="score-container">
            <div class="puppet-widget">
                <div class="puppet-head-container">
                    <div class="puppet-nose" style="width: ${noseWidth}px">
                        <div class="puppet-led" style="background-color: ${color}; box-shadow: 0 0 ${6 + inverseConf * 10}px ${color}"></div>
                    </div>
                </div>
                <div class="puppet-labels">
                    <span class="${state === 'truth' ? 'active' : ''}">Truth</span>
                    <span class="${state === 'uncertain' ? 'active' : ''}">Unsure</span>
                    <span class="${state === 'lie' ? 'active' : ''}">Lie</span>
                </div>
            </div>

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
