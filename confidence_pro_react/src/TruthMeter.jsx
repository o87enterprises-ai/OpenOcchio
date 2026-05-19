import React, { useState, useEffect, useRef } from 'react';
import './TruthMeter.css';

const TRUTH_GREEN = "#2ecc71";
const UNCERTAIN_YELLOW = "#f1c40f";
const LIE_RED = "#e74c3c";

const TruthMeter = ({ glowColor = "132, 0, 255" }) => {
    const [prompt, setPrompt] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [history, setHistory] = useState(() => JSON.parse(localStorage.getItem('occhio_history') || '[]'));
    const [demoMode, setDemoMode] = useState(() => localStorage.getItem('occhio_demo_mode') === 'true');
    const [apiUrl, setApiUrl] = useState(() => localStorage.getItem('occhio_backend_url') || "https://YOUR-HF-USERNAME-openocchio-api.hf.space/confidence");
    
    const historyEndRef = useRef(null);

    useEffect(() => {
        localStorage.setItem('occhio_history', JSON.stringify(history));
        scrollToBottom();
    }, [history]);

    const scrollToBottom = () => {
        historyEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const checkConfidence = async (e) => {
        e.preventDefault();
        if (!prompt.trim() || loading) return;

        const currentPrompt = prompt;
        setPrompt('');
        setLoading(true);

        try {
            let data;
            if (demoMode) {
                await new Promise(r => setTimeout(r, 1200));
                const mockConfidence = Math.random();
                data = {
                    confidence: mockConfidence,
                    model: "demo-model-v2",
                    method: "heuristic-analysis",
                    markers: mockConfidence > 0.7 ? ["certainly", "indeed", "correct"] : (mockConfidence < 0.4 ? ["maybe", "not sure", "depends"] : ["likely", "possible"]),
                    prompt: currentPrompt
                };
            } else {
                if (apiUrl.includes("YOUR-HF-USERNAME")) {
                    throw new Error("Backend URL not configured. Please switch to Demo mode or update settings.");
                }

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: currentPrompt, mode: 'generate' })
                });

                if (!response.ok) throw new Error(`Server error: ${response.status}`);
                
                data = await response.json();
                data.prompt = currentPrompt;
            }
            handleResult(data);
        } catch (err) {
            console.error(err);
            const errorItem = {
                id: Date.now(),
                prompt: currentPrompt,
                error: err.message,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };
            setHistory(prev => [...prev, errorItem].slice(-10));
        } finally {
            setLoading(false);
        }
    };

    const handleResult = (data) => {
        setResult(data);
        const item = {
            id: Date.now(),
            prompt: data.prompt,
            confidence: data.confidence,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setHistory(prev => [...prev, item].slice(-10)); // Keep last 10 messages
    };

    const getStatus = (conf) => {
        if (conf >= 0.8) return { label: 'Truth', color: TRUTH_GREEN, state: 'truth' };
        if (conf >= 0.4) return { label: 'Unsure', color: UNCERTAIN_YELLOW, state: 'uncertain' };
        return { label: 'Lie', color: LIE_RED, state: 'lie' };
    };

    const status = result ? getStatus(result.confidence) : { label: 'Neutral', color: '#888', state: 'neutral' };
    const noseWidth = result ? 24 + (1.0 - result.confidence) * 110 : 24;

    return (
        <div className="chat-interface">
            <header className="chat-header">
                <div className="chat-header-info">
                    <span className="oracle-status-dot" style={{ backgroundColor: loading ? '#007aff' : '#34c759' }}></span>
                    <h2>OpenOcchio Oracle</h2>
                </div>
                <button className="demo-toggle" onClick={() => setDemoMode(!demoMode)}>
                    {demoMode ? '🌙 Demo' : '☀️ Live'}
                </button>
            </header>

            <div className="gauge-viewport">
                <div className="puppet-widget">
                    <div className="puppet-head-container">
                        <div className="puppet-nose" style={{ width: `${noseWidth}px` }}>
                            <div className="puppet-led" style={{ 
                                backgroundColor: status.color, 
                                boxShadow: `0 0 ${10 + (result ? (1.0 - result.confidence) * 15 : 0)}px ${status.color}` 
                            }}></div>
                        </div>
                    </div>
                    <div className="puppet-labels">
                        <span className={status.state === 'truth' ? 'active truth' : ''}>Truth</span>
                        <span className={status.state === 'uncertain' ? 'active uncertain' : ''}>Unsure</span>
                        <span className={status.state === 'lie' ? 'active lie' : ''}>Lie</span>
                    </div>
                </div>
                {result && (
                    <div className="current-score">
                        <span className="score-pct" style={{ color: status.color }}>{(result.confidence * 100).toFixed(0)}%</span>
                        <span className="score-lbl">{status.label}</span>
                    </div>
                )}
            </div>

            <div className="chat-history">
                {history.length === 0 ? (
                    <div className="chat-welcome">
                        <p>Ask me anything. I'll analyze the truth behind the AI's words.</p>
                    </div>
                ) : (
                    history.map(item => {
                        const s = item.error ? null : getStatus(item.confidence);
                        return (
                            <div key={item.id} className="chat-message" style={{ borderLeft: item.error ? `3px solid ${LIE_RED}` : 'none' }}>
                                <div className="msg-prompt">{item.prompt}</div>
                                <div className="msg-meta">
                                    <span className="msg-time">{item.timestamp}</span>
                                    {item.error ? (
                                        <span className="msg-error" style={{ color: LIE_RED }}>Error: {item.error}</span>
                                    ) : (
                                        <span className="msg-confidence" style={{ color: s.color }}>
                                            {s.label} ({(item.confidence * 100).toFixed(0)}%)
                                        </span>
                                    )}
                                </div>
                            </div>
                        )
                    })
                )}
                <div ref={historyEndRef} />
            </div>

            <form onSubmit={checkConfidence} className="chat-input-area">
                <input 
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Enter query..."
                    disabled={loading}
                />
                <button type="submit" disabled={loading || !prompt.trim()}>
                    {loading ? '...' : '→'}
                </button>
            </form>
        </div>
    );
};

export default TruthMeter;
