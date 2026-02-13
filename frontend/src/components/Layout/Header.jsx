import React, { useState, useEffect } from 'react';

export default function Header({ dashboardData, voiceEnabled, onToggleVoice }) {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    const threatLevel = dashboardData?.threat_level || 'LOADING';
    const threatColor = {
        'CRITICAL': '#ff0040', 'HIGH': '#ff6600',
        'ELEVATED': '#f0ff00', 'GUARDED': '#00ff80', 'LOADING': '#4a5568'
    }[threatLevel] || '#00f0ff';

    return (
        <div className="header-bar">
            <div className="header-left">
                <div className="header-clock">{time.toLocaleTimeString('en-GB', { hour12: false })}</div>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: '#4a5568' }}>
                    {time.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).toUpperCase()}
                </div>
                <div className="header-status">
                    <span className="pulse-dot live" />
                    <span>OPERATIONAL</span>
                </div>
            </div>
            <div className="header-right">
                <div className="header-alert" style={{ background: `${threatColor}15`, color: threatColor, borderColor: `${threatColor}30` }}>
                    <span className="pulse-dot" style={{ background: threatColor }} />
                    THREAT: {threatLevel}
                </div>
                <button
                    className={`voice-toggle${voiceEnabled ? ' active' : ''}`}
                    onClick={onToggleVoice}
                    title={voiceEnabled ? 'Mute voice' : 'Enable voice'}
                >
                    {voiceEnabled ? '🔊' : '🔇'} {voiceEnabled ? 'VOICE ON' : 'MUTED'}
                </button>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.6rem', color: '#4a5568' }}>
                    UTC {time.toISOString().substring(11, 19)}
                </div>
            </div>
        </div>
    );
}
