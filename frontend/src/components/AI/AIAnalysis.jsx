import React, { useState } from 'react';
import { runAIAnalysis } from '../../api/client';

export default function AIAnalysis({ dashboardData, speakText, voiceEnabled }) {
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleAnalyze = async (focusArea = null) => {
        setLoading(true);
        setError('');
        try {
            const result = await runAIAnalysis(dashboardData, focusArea);
            setAnalysis(result);

            // Voice briefing of analysis
            if (voiceEnabled && speakText && result.analysis) {
                const summary = result.analysis.substring(0, 400).replace(/[#*_\-|]/g, '');
                speakText(`CITADEL AI analysis complete. ${summary}... End of executive summary.`);
            }
        } catch (e) {
            setError(`Analysis failed: ${e.message}`);
        }
        setLoading(false);
    };

    return (
        <div className="fade-in">
            <div className="section-header">
                <h2>AI Threat Analysis</h2>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.6rem', color: '#4a5568' }}>
                    Powered by Groq • llama-3.3-70b-versatile
                </div>
            </div>

            {/* Analysis Actions */}
            <div className="glass-panel" style={{ padding: 18, marginBottom: 16 }}>
                <div className="heading-section">Analysis Operations</div>
                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                    <button className="btn-neon btn-filled" onClick={() => handleAnalyze()} disabled={loading}>
                        {loading ? '◈ ANALYZING...' : '◈ FULL DASHBOARD ANALYSIS'}
                    </button>
                    <button className="btn-neon" onClick={() => handleAnalyze('southern_corridor')} disabled={loading}>
                        Southern Corridor Focus
                    </button>
                    <button className="btn-neon" onClick={() => handleAnalyze('cross_border')} disabled={loading}>
                        Cross-Border Threats
                    </button>
                    <button className="btn-neon" onClick={() => handleAnalyze('banditry_patterns')} disabled={loading}>
                        Banditry Patterns
                    </button>
                    <button className="btn-neon" onClick={() => handleAnalyze('force_posture')} disabled={loading}>
                        Force Posture Review
                    </button>
                </div>
            </div>

            {error && (
                <div className="glass-panel" style={{ padding: 16, marginBottom: 16, borderColor: 'rgba(255,0,64,0.3)' }}>
                    <span style={{ color: '#ff0040', fontFamily: 'JetBrains Mono', fontSize: '0.8rem' }}>{error}</span>
                </div>
            )}

            {loading && (
                <div className="glass-panel" style={{ padding: 40, textAlign: 'center' }}>
                    <div className="loading-spinner" style={{ justifyContent: 'center' }}>Processing intelligence data through AI analysis engine...</div>
                    <div className="loading-bar" style={{ marginTop: 16 }} />
                </div>
            )}

            {analysis && !loading && (
                <div className="glass-panel" style={{ padding: 24 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                        <div className="heading-section" style={{ marginBottom: 0 }}>Intelligence Assessment</div>
                        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            {analysis.data_sources?.map((s, i) => (
                                <span key={i} className="badge badge-low" style={{ fontSize: '0.5rem' }}>{s}</span>
                            ))}
                            <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.55rem', color: '#4a5568' }}>
                                {analysis.timestamp ? new Date(analysis.timestamp).toLocaleString() : ''}
                            </span>
                        </div>
                    </div>
                    <div className="sitrep-content" style={{ padding: 0 }}>
                        {analysis.analysis}
                    </div>
                </div>
            )}

            {!analysis && !loading && (
                <div className="glass-panel" style={{ padding: 50, textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', marginBottom: 12, opacity: 0.3 }}>⬢</div>
                    <div style={{ fontFamily: 'Orbitron', fontSize: '0.8rem', color: '#4a5568', letterSpacing: '0.15em', marginBottom: 8 }}>
                        AI ANALYSIS ENGINE READY
                    </div>
                    <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.7rem', color: '#4a5568' }}>
                        Select an analysis operation above to process current intelligence data<br />
                        through the CITADEL AI threat assessment engine.
                    </div>
                </div>
            )}
        </div>
    );
}
