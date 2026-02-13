import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage, clearChatHistory } from '../../api/client';

export default function ChatBot({ voiceEnabled, speakText, stopSpeaking }) {
    const [messages, setMessages] = useState([
        { role: 'ai', content: 'CITADEL AI online. I am your intelligence analysis assistant for Kebbi State security operations. How can I assist you, Analyst?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [voiceReadback, setVoiceReadback] = useState(true);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    useEffect(scrollToBottom, [messages]);

    const SUGGESTED = [
        'What is the current threat assessment for Kebbi State?',
        'Analyze banditry patterns in southern Kebbi LGAs',
        'What are the key security concerns for Zuru and Wasagu/Danko?',
        'Summarize cross-border threats from Niger Republic',
        'Recommend force deployment for high-risk LGAs',
    ];

    const handleSend = async (text) => {
        const msg = text || input.trim();
        if (!msg || loading) return;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: msg }]);
        setLoading(true);

        try {
            const result = await sendChatMessage(msg);
            const aiResponse = result.response || 'Analysis unavailable.';
            setMessages(prev => [...prev, { role: 'ai', content: aiResponse, timestamp: result.timestamp }]);

            // Voice readback of AI response
            if (voiceEnabled && voiceReadback && speakText) {
                // Summarize for voice (first 300 chars)
                const voiceText = aiResponse.length > 300
                    ? aiResponse.substring(0, 300).replace(/[#*_\-]/g, '') + '... End of briefing.'
                    : aiResponse.replace(/[#*_\-]/g, '');
                speakText(voiceText);
            }
        } catch (e) {
            setMessages(prev => [...prev, { role: 'ai', content: `[COMMS ERROR] Unable to reach CITADEL AI core: ${e.message}. Check backend connectivity.` }]);
        }
        setLoading(false);
    };

    const handleClear = async () => {
        try { await clearChatHistory(); } catch (e) { /* ok */ }
        setMessages([{ role: 'ai', content: 'CITADEL AI session cleared. Ready for new analysis.' }]);
    };

    return (
        <div className="fade-in chat-container">
            {/* Chat Header */}
            <div className="glass-panel" style={{ padding: '12px 18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderRadius: '6px 6px 0 0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ fontFamily: 'Orbitron', fontSize: '1.1rem', color: '#00f0ff' }}>⬡</span>
                    <div>
                        <div style={{ fontFamily: 'Orbitron', fontSize: '0.75rem', color: '#00f0ff', letterSpacing: '0.15em' }}>CITADEL AI</div>
                        <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.55rem', color: '#4a5568' }}>llama-3.3-70b • Groq Engine</div>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <button
                        className={`voice-toggle${voiceReadback ? ' active' : ''}`}
                        onClick={() => {
                            if (voiceReadback && stopSpeaking) stopSpeaking();
                            setVoiceReadback(!voiceReadback);
                        }}
                        style={{ fontSize: '0.6rem', padding: '4px 10px' }}
                    >
                        {voiceReadback ? '🔊 READ' : '🔇 MUTE'}
                    </button>
                    <button className="btn-neon btn-danger" style={{ padding: '4px 12px', fontSize: '0.55rem' }} onClick={handleClear}>CLEAR</button>
                </div>
            </div>

            {/* Messages */}
            <div className="chat-messages" style={{ background: 'rgba(5,5,8,0.6)' }}>
                {messages.map((msg, i) => (
                    <div key={i} className={`chat-msg ${msg.role}`}>
                        {msg.role === 'ai' && <div className="msg-label">◈ CITADEL AI</div>}
                        <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{msg.content}</div>
                        {msg.timestamp && (
                            <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.55rem', color: '#4a5568', marginTop: 6 }}>
                                {new Date(msg.timestamp).toLocaleTimeString()}
                            </div>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className="chat-msg ai">
                        <div className="msg-label">◈ CITADEL AI</div>
                        <div style={{ color: '#4a5568' }}>Analyzing...</div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Suggested Prompts */}
            <div style={{ padding: '8px 16px', background: 'rgba(10,13,20,0.7)', display: 'flex', gap: 6, overflowX: 'auto' }}>
                {SUGGESTED.map((s, i) => (
                    <button key={i} className="btn-neon" style={{ fontSize: '0.55rem', padding: '4px 10px', whiteSpace: 'nowrap', flexShrink: 0 }} onClick={() => handleSend(s)}>
                        {s.length > 40 ? s.substring(0, 40) + '...' : s}
                    </button>
                ))}
            </div>

            {/* Input */}
            <div className="chat-input-area">
                <input
                    className="chat-input"
                    placeholder="Ask CITADEL AI about Kebbi State security..."
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSend()}
                    disabled={loading}
                />
                <button className="btn-neon btn-filled" onClick={() => handleSend()} disabled={loading} style={{ padding: '10px 24px' }}>
                    {loading ? '◈...' : '◈ SEND'}
                </button>
            </div>
        </div>
    );
}
