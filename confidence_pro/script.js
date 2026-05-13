// UI Elements
const settingsPanel = document.getElementById('settings-panel');
const mainView = document.getElementById('main-view');
const inferenceFrame = document.getElementById('inference-frame');
const confidenceWidget = document.getElementById('confidence-widget');
const widgetToggle = document.getElementById('widget-toggle');
const gaugeBar = document.getElementById('gauge-bar');
const confScore = document.getElementById('conf-score');
const confLabel = document.getElementById('conf-label');
const statusMsg = document.getElementById('status-msg');

// State
let config = {
    targetUrl: '',
    apiUrl: '',
    modelName: ''
};

// Initialize
document.getElementById('launch-btn').addEventListener('click', () => {
    config.targetUrl = document.getElementById('target-url').value;
    config.apiUrl = document.getElementById('api-url').value;
    config.modelName = document.getElementById('model-name').value;

    settingsPanel.classList.add('hidden');
    mainView.classList.remove('hidden');
    inferenceFrame.src = config.targetUrl;
});

widgetToggle.addEventListener('click', () => {
    confidenceWidget.classList.toggle('collapsed');
    document.getElementById('expand-icon').innerText = 
        confidenceWidget.classList.contains('collapsed') ? '▲' : '▼';
});

// OpenOcchio Engine (JS Port)
async function getAIResponse(prompt, temperature = 0.7) {
    const response = await fetch(`${config.apiUrl}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model: config.modelName,
            prompt: prompt,
            stream: false,
            options: { temperature, num_predict: 100 }
        })
    });
    const data = await response.json();
    return data.response;
}

function detectRefusal(text) {
    const patterns = [
        /as an? (ai|artificial intelligence|language model)/i,
        /i (cannot|can't|am unable to) (answer|provide|respond|describe)/i,
        /there is no (real|correct|objective) answer/i,
        /subjective/i,
        /opinion-based/i
    ];
    return patterns.some(p => p.test(text));
}

function calculateJaccard(s1, s2) {
    const set1 = new Set(s1.toLowerCase().split(/\s+/));
    const set2 = new Set(s2.toLowerCase().split(/\s+/));
    const intersection = new Set([...set1].filter(x => set2.has(x)));
    const union = new Set([...set1, ...set2]);
    return intersection.size / union.size;
}

async function runConfidenceCheck(prompt) {
    updateUI(0.1, 'Analyzing...');
    
    const samples = [];
    let refusalCount = 0;
    const numSamples = 3;
    
    try {
        for (let i = 0; i < numSamples; i++) {
            const res = await getAIResponse(prompt, 0.8);
            samples.push(res);
            if (detectRefusal(res)) refusalCount++;
            updateUI((i + 1) / numSamples * 0.5, 'Sampling...');
        }

        let totalSim = 0;
        let pairs = 0;
        for (let i = 0; i < samples.length; i++) {
            for (let j = i + 1; j < samples.length; j++) {
                totalSim += calculateJaccard(samples[i], samples[j]);
                pairs++;
            }
        }

        let score = pairs > 0 ? totalSim / pairs : 1.0;
        
        // Refusal penalty
        const refusalRatio = refusalCount / samples.length;
        if (refusalRatio > 0.5) {
            score = score * (1.0 - (refusalRatio * 0.5));
        }

        displayResult(score);
    } catch (e) {
        console.error(e);
        updateUI(0, 'Connection Error');
    }
}

function updateUI(percent, msg) {
    gaugeBar.style.width = `${percent * 100}%`;
    if (msg) document.querySelector('.status-msg').innerText = msg;
}

function displayResult(score) {
    const rounded = score.toFixed(2);
    confScore.innerText = rounded;
    
    let label = '';
    let color = '';

    if (score >= 0.8) { label = 'Confident'; color = '#2ecc71'; }
    else if (score >= 0.6) { label = 'Steady'; color = '#f1c40f'; }
    else if (score >= 0.4) { label = 'Unsure'; color = '#e67e22'; }
    else { label = 'Insecure'; color = '#e74c3c'; }

    confLabel.innerText = label;
    confLabel.style.color = color;
    gaugeBar.style.backgroundColor = color;
    gaugeBar.style.width = `${score * 100}%`;
    document.querySelector('.status-msg').innerText = 'Verification complete.';
}

// Manual Check Implementation
document.getElementById('manual-check').addEventListener('click', () => {
    const prompt = prompt("What prompt should we verify?");
    if (prompt) runConfidenceCheck(prompt);
});

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js');
    });
}
