import React, { useState, useEffect } from 'react';

export default function AdminPanel() {
    const [status, setStatus] = useState({ backend: 'checking', apis: {} });

    useEffect(() => {
        checkStatus();
        const interval = setInterval(checkStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    const checkStatus = async () => {
        try {
            const res = await fetch('/api/health/detailed');
            const data = await res.json();
            setStatus({ backend: 'online', data });
        } catch {
            setStatus({ backend: 'offline', data: null });
        }
    };

    const apis = [
        { name: 'NASA FIRMS', key: 'nasa_firms', desc: 'Fire/Thermal Data' },
        { name: 'N2YO', key: 'n2yo', desc: 'Satellite Tracking' },
        { name: 'Copernicus', key: 'copernicus', desc: 'Sentinel Imagery' },
        { name: 'GNews', key: 'gnews', desc: 'News API' },
    ];

    return (
        <div className="fade-in">
            <h2 className="section-header">ADMIN / SETTINGS</h2>

            {/* Backend Status */}
            <div className="glass-panel" style={{ padding: 20, marginBottom: 20 }}>
                <h3 style={{ color: '#00f0ff', fontFamily: 'Orbitron', fontSize: '0.8rem', marginBottom: 16 }}>
                    BACKEND STATUS
                </h3>
                <div style={{
                    padding: 12,
                    background: status.backend === 'online' ? 'rgba(0,255,128,0.1)' : 'rgba(255,0,64,0.1)',
                    borderRadius: 8,
                    border: `1px solid ${status.backend === 'online' ? '#00ff80' : '#ff0040'}`,
                    color: status.backend === 'online' ? '#00ff80' : '#ff0040',
                    fontFamily: 'Orbitron',
                    fontSize: '0.8rem'
                }}>
                    {status.backend === 'online' ? '● SYSTEM OPERATIONAL' : '● SYSTEM OFFLINE'}
                </div>
            </div>

            {/* API Configuration */}
            <div className="glass-panel" style={{ padding: 20, marginBottom: 20 }}>
                <h3 style={{ color: '#00f0ff', fontFamily: 'Orbitron', fontSize: '0.8rem', marginBottom: 16 }}>
                    API CONFIGURATION
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
                    {apis.map(api => {
                        const isConfigured = status.data?.external_apis?.[api.key]?.status === 'configured';
                        return (
                            <div key={api.key} style={{
                                padding: 12,
                                background: 'rgba(255,255,255,0.03)',
                                borderRadius: 8,
                                border: '1px solid rgba(255,255,255,0.05)'
                            }}>
                                <div style={{ fontSize: '0.7rem', color: '#8892a4' }}>{api.desc}</div>
                                <div style={{ fontFamily: 'Orbitron', fontSize: '0.75rem', color: '#e0e6f0' }}>
                                    {api.name}
                                </div>
                                <div style={{
                                    marginTop: 8,
                                    fontSize: '0.6rem',
                                    color: isConfigured ? '#00ff80' : '#ff0040'
                                }}>
                                    {isConfigured ? '● CONFIGURED' : '● NOT CONFIGURED'}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Quick Actions */}
            <div className="glass-panel" style={{ padding: 20 }}>
                <h3 style={{ color: '#00f0ff', fontFamily: 'Orbitron', fontSize: '0.8rem', marginBottom: 16 }}>
                    QUICK ACTIONS
                </h3>
                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                    <button 
                        onClick={() => window.location.reload()}
                        style={{
                            padding: '10px 20px',
                            background: 'rgba(0,240,255,0.1)',
                            border: '1px solid #00f0ff',
                            borderRadius: 6,
                            color: '#00f0ff',
                            fontFamily: 'Orbitron',
                            fontSize: '0.7rem',
                            cursor: 'pointer'
                        }}
                    >
                        REFRESH DATA
                    </button>
                    <button 
                        onClick={checkStatus}
                        style={{
                            padding: '10px 20px',
                            background: 'rgba(0,255,128,0.1)',
                            border: '1px solid #00ff80',
                            borderRadius: 6,
                            color: '#00ff80',
                            fontFamily: 'Orbitron',
                            fontSize: '0.7rem',
                            cursor: 'pointer'
                        }}
                    >
                        CHECK STATUS
                    </button>
                </div>
            </div>
        </div>
    );
}
