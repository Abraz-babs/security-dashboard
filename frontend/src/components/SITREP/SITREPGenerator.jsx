import React, { useState } from 'react';
import { generateSITREP } from '../../api/client';

export default function SITREPGenerator() {
    const [sitrep, setSitrep] = useState(null);
    const [loading, setLoading] = useState(false);
    const [period, setPeriod] = useState('24h');
    const [error, setError] = useState('');

    const handleGenerate = async () => {
        setLoading(true);
        setError('');
        try {
            const result = await generateSITREP(period);
            setSitrep(result);
        } catch (e) {
            setError(`SITREP generation failed: ${e.message}`);
        }
        setLoading(false);
    };

    const handlePrint = () => {
        if (!sitrep?.sitrep) return;
        
        // Check for popup blocker - v2 fix
        const printWin = window.open('', '_blank');
        if (!printWin) {
            alert('Please allow popups to print SITREP');
            return;
        }
        
        const content = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SITREP - CITADEL KEBBI</title>
    <style>
        body { font-family: 'Courier New', monospace; padding: 40px; font-size: 12px; line-height: 1.8; }
        h1 { font-size: 16px; text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }
        .classification { text-align: center; font-weight: bold; color: red; margin: 10px 0; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        @media print {
            body { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="classification">TOP SECRET // KEBBI STATE GOVERNMENT</div>
    <h1>SITUATION REPORT (SITREP)</h1>
    <div class="classification">CITADEL KEBBI INTELLIGENCE COMMAND CENTER</div>
    <pre>${sitrep.sitrep.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
    <div class="classification">TOP SECRET // KEBBI STATE GOVERNMENT</div>
    <script>
        window.onload = function() {
            setTimeout(function() {
                window.print();
            }, 250);
        };
    </script>
</body>
</html>`;
        
        printWin.document.write(content);
        printWin.document.close();
    };

    return (
        <div className="fade-in">
            <div className="section-header">
                <h2>SITREP Generator</h2>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.6rem', color: '#4a5568' }}>
                    Military-Format Situation Report
                </div>
            </div>

            {/* Controls */}
            <div className="glass-panel" style={{ padding: 18, marginBottom: 16 }}>
                <div className="heading-section">Report Configuration</div>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', gap: 6 }}>
                        {['6h', '12h', '24h', '48h', '72h'].map(p => (
                            <button key={p} className={`btn-neon${period === p ? ' btn-filled' : ''}`} style={{ padding: '6px 14px', fontSize: '0.6rem' }} onClick={() => setPeriod(p)}>
                                {p.toUpperCase()}
                            </button>
                        ))}
                    </div>
                    <button className="btn-neon btn-filled" onClick={handleGenerate} disabled={loading} style={{ padding: '10px 28px' }}>
                        {loading ? '◈ GENERATING...' : '◈ GENERATE SITREP'}
                    </button>
                    {sitrep && (
                        <button className="btn-neon btn-success" onClick={handlePrint} style={{ padding: '10px 20px' }}>
                            🖨️ PRINT / EXPORT
                        </button>
                    )}
                </div>
            </div>

            {error && (
                <div className="glass-panel" style={{ padding: 16, marginBottom: 16, borderColor: 'rgba(255,0,64,0.3)' }}>
                    <span style={{ color: '#ff0040', fontFamily: 'JetBrains Mono', fontSize: '0.8rem' }}>{error}</span>
                </div>
            )}

            {loading && (
                <div className="glass-panel" style={{ padding: 40, textAlign: 'center' }}>
                    <div className="loading-spinner" style={{ justifyContent: 'center' }}>Generating SITREP from live intelligence...</div>
                    <div className="loading-bar" style={{ marginTop: 16 }} />
                    <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: '#4a5568', marginTop: 12 }}>
                        Aggregating: NASA FIRMS • NewsData OSINT • LGA Intelligence • AI Analysis
                    </div>
                </div>
            )}

            {sitrep && !loading && (
                <div className="glass-panel">
                    <div style={{ padding: '12px 18px', borderBottom: '1px solid rgba(0,240,255,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ fontFamily: 'Orbitron', fontSize: '0.75rem', color: '#ff0040', letterSpacing: '0.15em' }}>
                            TOP SECRET // SITREP
                        </div>
                        <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.6rem', color: '#4a5568' }}>
                            Period: {sitrep.period} • Generated: {sitrep.timestamp ? new Date(sitrep.timestamp).toLocaleString() : 'Now'}
                        </div>
                    </div>
                    <div className="sitrep-content">
                        {sitrep.sitrep}
                    </div>
                </div>
            )}

            {!sitrep && !loading && (
                <div className="glass-panel" style={{ padding: 50, textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', marginBottom: 12, opacity: 0.3 }}>▣</div>
                    <div style={{ fontFamily: 'Orbitron', fontSize: '0.8rem', color: '#4a5568', letterSpacing: '0.15em', marginBottom: 8 }}>
                        SITREP GENERATOR READY
                    </div>
                    <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.7rem', color: '#4a5568' }}>
                        Select reporting period and click Generate to produce a military-format<br />
                        Situation Report from live intelligence data.
                    </div>
                </div>
            )}
        </div>
    );
}
