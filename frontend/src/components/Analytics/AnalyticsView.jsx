import React, { useState, useEffect } from 'react';
import { getDashboardOverview, getLGAData, getFIRMSAll, getSecurityIntel } from '../../api/client';
import dataCache, { CACHE_KEYS } from '../../services/DataCache';

export default function AnalyticsView({ dashboardData }) {
    // Initialize from cache immediately
    const cachedLgas = dataCache.get(CACHE_KEYS.LGAS);
    const cachedHotspots = dataCache.get(CACHE_KEYS.FIRMS_HOTSPOTS);
    const cachedIntel = dataCache.get(CACHE_KEYS.INTEL_REPORTS);
    
    const [lgas, setLgas] = useState(cachedLgas);
    const [hotspots, setHotspots] = useState(cachedHotspots);
    const [intel, setIntel] = useState(cachedIntel);
    const [loading, setLoading] = useState(!cachedLgas && !cachedHotspots && !cachedIntel);
    const [isRefreshing, setIsRefreshing] = useState(false);

    useEffect(() => {
        const load = async () => {
            // If we have cached data, show refresh indicator
            if (cachedLgas || cachedHotspots || cachedIntel) {
                setIsRefreshing(true);
            }
            
            // Fetch each independently so one failure doesn't block all
            await Promise.all([
                // LGA Data
                (async () => {
                    try {
                        const l = await getLGAData();
                        setLgas(l);
                        dataCache.set(CACHE_KEYS.LGAS, l);
                    } catch (e) { console.warn('Analytics: LGA failed', e); }
                })(),
                
                // FIRMS Hotspots
                (async () => {
                    try {
                        const h = await getFIRMSAll(7);
                        setHotspots(h);
                        dataCache.set(CACHE_KEYS.FIRMS_HOTSPOTS, h);
                    } catch (e) { console.warn('Analytics: FIRMS failed', e); }
                })(),
                
                // Intel
                (async () => {
                    try {
                        const i = await getSecurityIntel();
                        setIntel(i);
                        dataCache.set(CACHE_KEYS.INTEL_REPORTS, i);
                    } catch (e) { console.warn('Analytics: Intel failed', e); }
                })()
            ]);

            setLoading(false);
            setIsRefreshing(false);
        };
        
        load();
    }, []);

    // Show loading only if no cached data at all
    if (loading) return (
        <div style={{ textAlign: 'center', padding: 60 }}>
            <div className="loading-spinner" style={{ margin: '0 auto 20px' }} />
            <div style={{ color: '#4a5568', fontSize: '0.8rem' }}>Loading analytics...</div>
        </div>
    );

    const lgaList = lgas?.lgas || [];
    const stats = dashboardData?.stats || {};
    const reports = intel?.reports || [];
    const fires = hotspots?.hotspots || [];

    // Risk distribution
    const riskDist = { critical: 0, high: 0, medium: 0, low: 0 };
    lgaList.forEach(l => { riskDist[l.risk] = (riskDist[l.risk] || 0) + 1; });

    // Category distribution  
    const catDist = {};
    reports.forEach(r => { catDist[r.category] = (catDist[r.category] || 0) + 1; });

    // Severity distribution
    const sevDist = { critical: 0, high: 0, medium: 0, low: 0 };
    reports.forEach(r => { sevDist[r.severity] = (sevDist[r.severity] || 0) + 1; });

    const BarChart = ({ data, colors, title }) => {
        const max = Math.max(...Object.values(data), 1);
        return (
            <div className="glass-panel" style={{ padding: 18 }}>
                <div className="heading-section">{title}</div>
                {Object.entries(data).map(([key, val]) => (
                    <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                        <div style={{ width: 80, fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: colors[key] || '#8892a4', textTransform: 'uppercase' }}>{key}</div>
                        <div style={{ flex: 1, height: 20, background: 'rgba(255,255,255,0.03)', borderRadius: 3, overflow: 'hidden' }}>
                            <div style={{
                                width: `${(val / max) * 100}%`, height: '100%',
                                background: `linear-gradient(90deg, ${colors[key] || '#00f0ff'}40, ${colors[key] || '#00f0ff'})`,
                                borderRadius: 3, transition: 'width 0.8s ease',
                                boxShadow: `0 0 8px ${colors[key] || '#00f0ff'}40`,
                            }} />
                        </div>
                        <div style={{ width: 30, fontFamily: 'JetBrains Mono', fontSize: '0.75rem', color: '#e0e6f0', textAlign: 'right' }}>{val}</div>
                    </div>
                ))}
            </div>
        );
    };

    const riskColors = { critical: '#ff0040', high: '#ff6600', medium: '#f0ff00', low: '#00ff80' };
    const catColors = { general: '#00f0ff', military: '#ff6600', criminal: '#ff0040', terrorism: '#ff0040', political: '#f0ff00', environmental: '#00ff80' };

    return (
        <div className="fade-in">
            {/* Refresh indicator */}
            {isRefreshing && (
                <div style={{ 
                    position: 'fixed', 
                    top: 70, 
                    right: 20, 
                    padding: '6px 12px', 
                    background: 'rgba(0,0,0,0.7)',
                    border: '1px solid rgba(0,240,255,0.3)',
                    borderRadius: 4,
                    fontSize: '0.6rem',
                    color: '#00f0ff',
                    zIndex: 1000,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8
                }}>
                    <span className="loading-spinner" style={{ width: 12, height: 12, margin: 0 }} />
                    Refreshing analytics...
                </div>
            )}

            <div className="section-header">
                <h2>Analytics Dashboard</h2>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.6rem', color: '#4a5568' }}>
                    Data from live API feeds
                </div>
            </div>

            {/* Summary Stats */}
            <div className="stat-grid" style={{ marginBottom: 20 }}>
                <div className="glass-panel stat-card">
                    <div className="stat-label">Total LGAs</div>
                    <div className="stat-value">{lgaList.length || 21}</div>
                    <div className="stat-sub">Kebbi State</div>
                </div>
                <div className="glass-panel stat-card critical">
                    <div className="stat-label">Critical Zones</div>
                    <div className="stat-value">{riskDist.critical}</div>
                    <div className="stat-sub">Immediate attention</div>
                </div>
                <div className="glass-panel stat-card warning">
                    <div className="stat-label">Intel Reports</div>
                    <div className="stat-value">{reports.length}</div>
                    <div className="stat-sub">OSINT collected</div>
                </div>
                <div className="glass-panel stat-card" style={{ '--stat-color': '#ff6600' }}>
                    <div className="stat-label">Thermal Anomalies</div>
                    <div className="stat-value" style={{ color: fires.length > 0 ? '#ff6600' : '#00ff80' }}>{fires.length}</div>
                    <div className="stat-sub">Last 7 days</div>
                </div>
            </div>

            {/* Charts Row */}
            <div className="two-col" style={{ marginBottom: 20 }}>
                <BarChart data={riskDist} colors={riskColors} title="LGA Risk Distribution" />
                <BarChart data={sevDist} colors={riskColors} title="Intel Severity Distribution" />
            </div>

            <div className="two-col" style={{ marginBottom: 20 }}>
                <BarChart data={catDist} colors={catColors} title="Intel Category Breakdown" />

                {/* LGA Risk Heatmap */}
                <div className="glass-panel" style={{ padding: 18 }}>
                    <div className="heading-section">LGA Risk Heatmap</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4 }}>
                        {lgaList.map((lga, i) => (
                            <div key={i} title={`${lga.name}: ${lga.risk}`} style={{
                                aspectRatio: '1', borderRadius: 4,
                                background: lga.color || '#4a5568',
                                opacity: 0.7, cursor: 'pointer',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                fontSize: '0.45rem', fontFamily: 'JetBrains Mono',
                                color: '#050508', fontWeight: 700,
                                transition: 'all 0.2s',
                            }}
                                onMouseEnter={e => { e.target.style.opacity = '1'; e.target.style.transform = 'scale(1.15)'; }}
                                onMouseLeave={e => { e.target.style.opacity = '0.7'; e.target.style.transform = 'scale(1)'; }}
                            >
                                {lga.name.substring(0, 3)}
                            </div>
                        ))}
                    </div>
                    <div style={{ display: 'flex', gap: 12, marginTop: 12, justifyContent: 'center' }}>
                        {Object.entries(riskColors).map(([k, c]) => (
                            <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 4, fontFamily: 'JetBrains Mono', fontSize: '0.55rem', color: '#8892a4' }}>
                                <div style={{ width: 10, height: 10, background: c, borderRadius: 2 }} />
                                {k.toUpperCase()}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Fire Hotspot Map (simple table) */}
            {fires.length > 0 && (
                <div className="glass-panel" style={{ padding: 18 }}>
                    <div className="heading-section">Thermal Anomaly Locations (7 days)</div>
                    <table className="data-table">
                        <thead>
                            <tr><th>#</th><th>Latitude</th><th>Longitude</th><th>Brightness</th><th>Confidence</th><th>Date</th></tr>
                        </thead>
                        <tbody>
                            {fires.slice(0, 20).map((f, i) => (
                                <tr key={i}>
                                    <td>{i + 1}</td>
                                    <td style={{ color: '#00f0ff' }}>{f.latitude?.toFixed(4)}°N</td>
                                    <td style={{ color: '#00f0ff' }}>{f.longitude?.toFixed(4)}°E</td>
                                    <td style={{ color: f.brightness > 350 ? '#ff0040' : '#f0ff00' }}>{f.brightness?.toFixed(1)} K</td>
                                    <td>{f.confidence}</td>
                                    <td>{f.acq_date}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
