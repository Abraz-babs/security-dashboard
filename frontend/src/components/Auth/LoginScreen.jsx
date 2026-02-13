import React, { useState } from 'react';
import { login } from '../../api/client';

export default function LoginScreen({ onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username || !password) { setError('Enter credentials to access the system'); return; }
        setLoading(true);
        setError('');
        try {
            const result = await login(username, password);
            if (result.success) {
                localStorage.setItem('citadel_token', result.token);
                localStorage.setItem('citadel_user', JSON.stringify(result.user));
                onLogin(result.user);
            }
        } catch (e) {
            setError(e.message || 'Invalid credentials. Access denied.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-screen">
            <div className="scan-line-overlay" />
            <form className="login-card glass-panel" onSubmit={handleSubmit}>
                <div style={{ marginBottom: 24, textAlign: 'center' }}>
                    <img
                        src="/kebbi-seal.png"
                        alt="Kebbi State Government Seal"
                        style={{
                            width: 100,
                            height: 100,
                            borderRadius: '50%',
                            marginBottom: 12,
                            border: '2px solid rgba(0,240,255,0.3)',
                            boxShadow: '0 0 30px rgba(0,240,255,0.2)',
                        }}
                        onError={(e) => { e.target.style.display = 'none'; }}
                    />
                    <h1>CITADEL</h1>
                    <div className="login-subtitle">Kebbi State Security Intelligence Command Center</div>
                </div>
                {error && (
                    <div style={{
                        color: '#ff0040',
                        fontFamily: 'JetBrains Mono',
                        fontSize: '0.7rem',
                        marginBottom: 16,
                        padding: '8px 12px',
                        background: 'rgba(255,0,64,0.1)',
                        borderRadius: 4,
                        border: '1px solid rgba(255,0,64,0.2)'
                    }}>
                        ⚠ {error}
                    </div>
                )}
                <div className="login-field">
                    <label>Operator ID</label>
                    <input
                        type="text"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                        placeholder="Enter operator ID"
                        autoFocus
                    />
                </div>
                <div className="login-field">
                    <label>Access Code</label>
                    <input
                        type="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        placeholder="Enter access code"
                    />
                </div>
                <button type="submit" className="btn-neon btn-filled login-btn" disabled={loading}>
                    {loading ? '◈ AUTHENTICATING...' : '◈ ACCESS SYSTEM'}
                </button>
                <div style={{ marginTop: 20, fontFamily: 'JetBrains Mono', fontSize: '0.6rem', color: '#4a5568', textAlign: 'center' }}>
                    CLASSIFICATION: TOP SECRET // KEBBI STATE GOVERNMENT<br />
                    SYSTEM v2.0.0 | ALL ACCESS MONITORED
                </div>
            </form>
        </div>
    );
}
