import React from 'react';

const NAV_ITEMS = [
    { id: 'dashboard', label: 'Dashboard', icon: '◆' },
    { id: 'satellite', label: 'Satellite Intel', icon: '◉' },
    { id: 'orbit', label: 'Orbit Tracker', icon: '◎' },
    { id: 'intel', label: 'Intel Feed', icon: '◈' },
    { id: 'chat', label: 'AI Chatbot', icon: '⬡' },
    { id: 'analysis', label: 'AI Analysis', icon: '⬢' },
    { id: 'sitrep', label: 'SITREP', icon: '▣' },
    { id: 'analytics', label: 'Analytics', icon: '◧' },
    { id: 'globe', label: '3D Globe', icon: '◉' },
    { id: 'admin', label: 'Admin / Settings', icon: '⚙' },
];

export default function Sidebar({ activeTab, onTabChange, onLogout }) {
    return (
        <nav className="sidebar">
            <div className="sidebar-header">
                <h1>CITADEL</h1>
                <div className="subtitle">KEBBI INTELLIGENCE</div>
            </div>
            <div className="sidebar-nav">
                {NAV_ITEMS.map(item => (
                    <div
                        key={item.id}
                        className={`nav-item${activeTab === item.id ? ' active' : ''}`}
                        onClick={() => onTabChange(item.id)}
                    >
                        <span style={{ fontFamily: 'Orbitron', fontSize: '1rem', width: 24, textAlign: 'center' }}>{item.icon}</span>
                        <span>{item.label}</span>
                    </div>
                ))}
            </div>
            <div className="sidebar-footer">
                {onLogout && (
                    <button
                        onClick={onLogout}
                        className="logout-btn"
                        style={{
                            width: '100%',
                            padding: '8px 12px',
                            marginBottom: 10,
                            background: 'rgba(255,0,64,0.1)',
                            border: '1px solid rgba(255,0,64,0.3)',
                            borderRadius: 6,
                            color: '#ff4060',
                            fontFamily: 'JetBrains Mono',
                            fontSize: '0.65rem',
                            cursor: 'pointer',
                            letterSpacing: '0.1em',
                            transition: 'all 0.3s ease',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: 6,
                        }}
                        onMouseEnter={e => { e.target.style.background = 'rgba(255,0,64,0.25)'; e.target.style.borderColor = '#ff0040'; }}
                        onMouseLeave={e => { e.target.style.background = 'rgba(255,0,64,0.1)'; e.target.style.borderColor = 'rgba(255,0,64,0.3)'; }}
                    >
                        ⏻ LOGOUT
                    </button>
                )}
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.55rem', color: '#4a5568', textAlign: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginBottom: 4 }}>
                        <span className="pulse-dot live" />
                        <span style={{ color: '#00ff80' }}>SYSTEM ONLINE</span>
                    </div>
                    v2.0.0 | TOP SECRET
                </div>
            </div>
        </nav>
    );
}
