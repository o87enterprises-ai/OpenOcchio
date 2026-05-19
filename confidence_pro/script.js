// script.js – OpenOcchio Mobile PWA

// Initial settings with localStorage support
const DEFAULT_API_URL = "https://YOUR-HF-USERNAME-openocchio-api.hf.space/confidence";
let API_URL = localStorage.getItem('occhio_backend_url') || DEFAULT_API_URL;
let CUSTOM_KEY = localStorage.getItem('occhio_api_key') || "";
let DEMO_MODE = localStorage.getItem('occhio_demo_mode') === 'true';

const form = document.getElementById('confidence-form');
const input = document.getElementById('prompt-input');
const resultDiv = document.getElementById('result');
const submitBtn = document.getElementById('submit-btn');
const modeBtns = document.querySelectorAll('.mode-btn');
const historyArea = document.getElementById('history');
const historyList = document.getElementById('history-list');

// Settings Elements
const settingsToggle = document.getElementById('settings-toggle');
const settingsModal = document.getElementById('settings-modal');
const saveSettingsBtn = document.getElementById('save-settings');
const backendUrlInput = document.getElementById('backend-url');
const apiKeyInput = document.getElementById('api-key');
const demoModeToggle = document.getElementById('demo-mode-toggle');

// Initialize Settings UI
backendUrlInput.value = API_URL;
apiKeyInput.value = CUSTOM_KEY;
demoModeToggle.checked = DEMO_MODE;

let currentMode = 'generate';
let history = JSON.parse(localStorage.getItem('occhio_history') || '[]');

// Load history on start
updateHistoryUI();

// Settings Logic
settingsToggle.addEventListener('click', () => {
    settingsModal.style.display = 'block';
});

saveSettingsBtn.addEventListener('click', () => {
    API_URL = backendUrlInput.value.trim() || DEFAULT_API_URL;
    CUSTOM_KEY = apiKeyInput.value.trim();
    DEMO_MODE = demoModeToggle.checked;
    
    localStorage.setItem('occhio_backend_url', API_URL);
    localStorage.setItem('occhio_api_key', CUSTOM_KEY);
    localStorage.setItem('occhio_demo_mode', DEMO_MODE);
    
    settingsModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
        settingsModal.style.display = 'none';
    }
});

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
        const headers = { 'Content-Type': 'application/json' };
        if (CUSTOM_KEY) {
            headers['X-API-Key'] = CUSTOM_KEY;
        }

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: headers,
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

        data.prompt = prompt; // Store prompt with result
        addToHistory(data);
        displayResult(data);
    } catch (err) {
        console.warn("API Error:", err.message);
        
        if (DEMO_MODE) {
            console.log("Falling back to Demo Mode");
            const mockConfidence = Math.random();
            const mockData = {
                confidence: mockConfidence,
                model: "demo-model-v2",
                method: "heuristic-analysis",
                markers: mockConfidence > 0.7 ? ["certainly", "indeed", "correct"] : (mockConfidence < 0.4 ? ["maybe", "not sure", "depends"] : ["likely", "possible"]),
                prompt: prompt
            };
            addToHistory(mockData);
            displayResult(mockData);
        } else {
            displayError(err.message);
        }
    } finally {
        setLoading(false);
    }
});

function setLoading(isLoading) {
    if (isLoading) {
        submitBtn.disabled = true;
        resultDiv.innerHTML = `
            <div class="loader"></div>
            <div class="status-msg" style="text-align: center; color: var(--text-muted); font-size: 0.9rem;">Consulting the Truth Oracle...</div>
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

    const inverseConf = 1.0 - confidence;
    const noseWidth = 24 + (inverseConf * 136);

    resultDiv.innerHTML = `
        <div class="score-container">
            <div class="puppet-widget">
                <div class="puppet-head-container">
                    <div class="puppet-nose" style="width: ${noseWidth}px">
                        <div class="puppet-led" style="background-color: ${color}; box-shadow: 0 0 ${10 + inverseConf * 15}px ${color}"></div>
                    </div>
                </div>
                <div class="puppet-labels">
                    <span class="${state === 'truth' ? 'active truth' : ''}">Truth</span>
                    <span class="${state === 'uncertain' ? 'active uncertain' : ''}">Unsure</span>
                    <span class="${state === 'lie' ? 'active lie' : ''}">Lie</span>
                </div>
            </div>

            <div class="score-display">
                <div class="score-circle" style="border-color: ${color}">
                    <div class="score-value" style="color: ${color}">${(confidence * 100).toFixed(0)}%</div>
                    <div class="score-label" style="color: ${color}">${label}</div>
                </div>
                
                ${data.markers ? `
                    <div class="marker-chips">
                        ${data.markers.map(m => `<span class="marker-chip">${m}</span>`).join('')}
                    </div>
                ` : ''}

                <div class="meta-info">
                    <strong>Model:</strong> ${data.model}<br>
                    <strong>Method:</strong> ${data.method}
                </div>
            </div>
        </div>
    `;
}

function addToHistory(data) {
    const item = {
        id: Date.now(),
        prompt: data.prompt.substring(0, 50) + (data.prompt.length > 50 ? '...' : ''),
        confidence: data.confidence,
        timestamp: new Date().toLocaleTimeString()
    };
    history.unshift(item);
    if (history.length > 5) history.pop();
    localStorage.setItem('occhio_history', JSON.stringify(history));
    updateHistoryUI();
}

function updateHistoryUI() {
    if (history.length === 0) {
        historyArea.style.display = 'none';
        return;
    }
    historyArea.style.display = 'block';
    historyList.innerHTML = history.map(item => `
        <div class="history-item" style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #f5f5f7; border-radius: 12px; margin-bottom: 8px; font-size: 0.85rem;">
            <div style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-right: 12px;">
                <strong>${item.timestamp}</strong>: ${item.prompt}
            </div>
            <div style="font-weight: 800; color: ${item.confidence >= 0.8 ? 'var(--truth-green)' : (item.confidence >= 0.4 ? 'var(--uncertain-yellow)' : 'var(--lie-red)')}">
                ${(item.confidence * 100).toFixed(0)}%
            </div>
        </div>
    `).join('');
}

function displayError(message) {
    resultDiv.innerHTML = `
        <div class="error-msg" style="color: var(--danger); background: #fff5f5; padding: 16px; border-radius: 12px; border: 1px solid #ffcfcf; margin-top: 20px;">
            <strong>Connection Failed</strong><br>
            <span style="font-size: 0.85rem;">${message}</span><br>
            <small style="display: block; margin-top: 8px;">Check if the backend is running or enable Demo Mode in settings.</small>
        </div>
    `;
}

