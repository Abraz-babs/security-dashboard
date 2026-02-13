import React, { useEffect, useState } from 'react';
import { getDashboardOverview, getLGAData } from '../../api/client';
import dataCache, { CACHE_KEYS } from '../../services/DataCache';

const STAT_TOOLTIPS = {
    active_threats: {
        title: 'Active Threats',
        detail: 'Combined count of critical/high severity intel reports, thermal anomalies, and critical LGA zones. Calculated from live NewsData OSINT, NASA FIRMS, and dynamic LGA risk assessment.',
    },
    surveillance_assets: {
        title: 'Surveillance Assets',
        detail: 'Real count of tracked satellites from N2YO including Sentinel-1A/1B (SAR Radar), Sentinel-2A/2B (Optical), ISS, NOAA-20, Pleiades, and other reconnaissance platforms.',
    },
    intel_reports: {
        title: 'Intel Reports',
        detail: 'Live OSINT feeds from NewsData.io covering Nigeria security, military operations, kidnapping, and Northwest Nigeria threats. Auto-refreshes every 2 minutes. If showing 0, the API key may need upgrading.',
    },
    fire_hotspots: {
        title: 'Thermal Anomalies',
        detail: 'Fire and thermal hotspots detected by NASA FIRMS using VIIRS and MODIS satellite sensors. High brightness values (>400K) may indicate large fires or industrial activity.',
    },
};

export default function DashboardView({ data, wsData, sentinelAlert }) {
    // Initialize from cache immediately (persistent across tab switches)
    const cachedOverview = dataCache.get(CACHE_KEYS.DASHBOARD);
    const cachedLgas = dataCache.get(CACHE_KEYS.LGAS);
    
    const [overview, setOverview] = useState(data || cachedOverview);
    const [lgas, setLgas] = useState(cachedLgas);
    const [loading, setLoading] = useState(!data && !cachedOverview);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [hoveredStat, setHoveredStat] = useState(null);

    // Update when props change
    useEffect(() => {
        if (data) { 
            setOverview(data); 
            dataCache.set(CACHE_KEYS.DASHBOARD, data);
            setLoading(false);
        }
    }, [data]);

    // Initial load and periodic refresh
    useEffect(() => {
        let isMounted = true;
        
        const load = async () => {
            // If we have cached data, show it immediately and refresh in background
            const hasCachedData = dataCache.get(CACHE_KEYS.DASHBOARD);
            if (hasCachedData) {
                setIsRefreshing(true);
            }
            
            try {
                const overviewPromise = getDashboardOverview().catch(() => null);
                const lgaPromise = getLGAData().catch(() => null);
                
                const [d, l] = await Promise.all([overviewPromise, lgaPromise]);
                
                if (!isMounted) return;
                
                if (d) {
                    setOverview(d);
                    dataCache.set(CACHE_KEYS.DASHBOARD, d);
                }
                if (l) {
                    setLgas(l);
                    dataCache.set(CACHE_KEYS.LGAS, l);
                }
            } catch (e) { 
                console.error('[Dashboard] Load error:', e);
            }
            if (isMounted) {
                setLoading(false);
                setIsRefreshing(false);
            }
        };
        
        // Load immediately
        load();
        
        // Refresh every 60 seconds
        const interval = setInterval(load, 60000);
        
        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, []);

    // Show loading only if no data at all
    if (loading) return <div className="loading-spinner">Initializing Command Center...</div>;

    const stats = overview?.stats || {};
    const alerts = overview?.recent_alerts || [];
    const threatLevel = overview?.threat_level || 'GUARDED';
    const threatScore = overview?.threat_score || 0.25;
    const lgaList = lgas?.lgas || [];
    const mlInsights = overview?.ml_insights;
    const dataQuality = overview?.data_quality;

    const threatColors = {
        'CRITICAL': '#ff0040', 'HIGH': '#ff6600',
        'ELEVATED': '#f0ff00', 'GUARDED': '#00ff80'
    };

    const statCards = [
        { key: 'active_threats', label: 'Active Threats', value: stats.active_threats ?? 0, sub: 'Across operational area', className: 'critical' },
        { key: 'surveillance_assets', label: 'Surveillance Assets', value: stats.surveillance_assets ?? 10, sub: 'Satellites tracked (live)', className: '' },
        { key: 'intel_reports', label: 'Intel Reports', value: stats.intel_reports ?? 0, sub: dataQuality?.intel_source || 'OSINT feeds', className: stats.intel_reports > 0 ? 'warning' : '' },
        { key: 'fire_hotspots', label: 'Fire Hotspots', value: stats.fire_hotspots ?? 0, sub: dataQuality?.fire_source || 'NASA FIRMS', className: '', valueColor: stats.fire_hotspots > 0 ? '#ff6600' : '#00ff80' },
    ];

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
                    Refreshing data...
                </div>
            )}

            {/* Stat Cards with Hover Tooltips */}
            <div className="stat-grid">
                {statCards.map(card => (
                    <div
                        key={card.key}
                        className={`glass-panel stat-card ${card.className}`}
                        style={{ position: 'relative', cursor: 'pointer' }}
                        onMouseEnter={() => setHoveredStat(card.key)}
                        onMouseLeave={() => setHoveredStat(null)}
                    >
                        <div className="stat-label">{card.label}</div>
                        <div className="stat-value" style={card.valueColor ? { color: card.valueColor } : {}}>{card.value}</div>
                        <div className="stat-sub">{card.sub}</div>

                        {hoveredStat === card.key && STAT_TOOLTIPS[card.key] && (
                            <div style={{
                                position: 'absolute',
                                top: '105%',
                                left: 0,
                                right: 0,
                                background: 'rgba(10,15,25,0.95)',
                                border: '1px solid rgba(0,240,255,0.3)',
                                borderRadius: 8,
                                padding: 12,
                                zIndex: 100,
                                fontSize: '0.6rem',
                                color: '#8a94a6',
                                boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
                                lineHeight: 1.6,
                            }}>
                                <div style={{ color: '#00f0ff', fontFamily: 'Orbitron', marginBottom: 4, fontSize: '0.6rem' }}>
                                    {STAT_TOOLTIPS[card.key].title}
                                </div>
                                {STAT_TOOLTIPS[card.key].detail}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            <div className="two-col">
                {/* Threat Level Gauge */}
                <div className="glass-panel threat-gauge">
                    <div className="heading-section">Threat Assessment</div>
                    <div className="threat-level-text" style={{ color: threatColors[threatLevel] || '#00f0ff' }}>
                        {threatLevel}
                    </div>
                    <div className="threat-gauge-bar">
                        <div className="threat-gauge-indicator" style={{ left: `${threatScore * 100}%` }} />
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'JetBrains Mono', fontSize: '0.6rem', color: '#4a5568' }}>
                        <span>LOW</span><span>GUARDED</span><span>ELEVATED</span><span>HIGH</span><span>CRITICAL</span>
                    </div>

                    {mlInsights?.trends && (
                        <div style={{ marginTop: 12, padding: 8, background: 'rgba(0,240,255,0.05)', borderRadius: 6, fontSize: '0.6rem' }}>
                            <span style={{ color: '#00f0ff', fontFamily: 'Orbitron', fontSize: '0.55rem' }}>ML TREND: </span>
                            <span style={{
                                color: mlInsights.trends.direction === 'up' ? '#ff6600' : mlInsights.trends.direction === 'down' ? '#00ff80' : '#f0ff00'
                            }}>
                                {mlInsights.trends.trend?.toUpperCase()} {mlInsights.trends.direction === 'up' ? '↑' : mlInsights.trends.direction === 'down' ? '↓' : '→'}
                            </span>
                            {mlInsights.trends.recommendation && (
                                <div style={{ color: '#8a94a6', marginTop: 4, fontSize: '0.55rem' }}>{mlInsights.trends.recommendation}</div>
                            )}
                        </div>
                    )}
                </div>

                {/* Recent Alerts */}
                <div className="glass-panel" style={{ padding: 18 }}>
                    <div className="heading-section">Recent Alerts</div>
                    {alerts.length === 0 ? (
                        <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.75rem', color: '#4a5568', textAlign: 'center', padding: 20 }}>
                            No recent alerts — monitoring active
                        </div>
                    ) : (
                        alerts.map((alert, i) => (
                            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '10px 0', borderBottom: '1px solid rgba(0,240,255,0.05)' }}>
                                <span className={`pulse-dot ${alert.severity === 'critical' ? 'alert' : alert.severity === 'high' ? 'warn' : 'live'}`} style={{ marginTop: 5 }} />
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontSize: '0.8rem', fontWeight: 500, marginBottom: 2 }}>{alert.title}</div>
                                    <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.6rem', color: '#4a5568' }}>
                                        {alert.source} • {alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'Just now'}
                                    </div>
                                </div>
                                <span className={`badge badge-${alert.severity}`}>{alert.severity}</span>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* LGA Risk Grid — FIRST */}
            <div style={{ marginTop: 20 }}>
                <div className="section-header">
                    <h2>All 21 LGA Risk Assessment</h2>
                    <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: '#4a5568' }}>
                        {lgas?.summary ? `Critical: ${lgas.summary.critical} | High: ${lgas.summary.high} | Medium: ${lgas.summary.medium} | Low: ${lgas.summary.low}` : ''}
                        {lgas?.risk_method === 'dynamic' && (
                            <span style={{ color: '#00ff80', marginLeft: 8 }}>● LIVE RISK</span>
                        )}
                    </div>
                </div>
                <div className="lga-grid">
                    {lgaList.map((lga, i) => (
                        <div key={lga.name} className="glass-panel lga-card" style={{ animationDelay: `${i * 0.03}s` }}>
                            <div className="lga-name" style={{ color: lga.color || '#e0e6f0' }}>{lga.name}</div>
                            <div className="lga-risk" style={{ color: lga.color || '#4a5568' }}>
                                ● {lga.label || lga.risk?.toUpperCase()}
                            </div>
                            <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.55rem', color: '#4a5568', marginTop: 4 }}>
                                {lga.lat?.toFixed(4)}°N, {lga.lon?.toFixed(4)}°E
                            </div>
                            {lga.risk_score > 0 && (
                                <div style={{
                                    marginTop: 4,
                                    height: 3,
                                    borderRadius: 2,
                                    background: 'rgba(255,255,255,0.05)',
                                    overflow: 'hidden',
                                }}>
                                    <div style={{
                                        width: `${lga.risk_score * 100}%`,
                                        height: '100%',
                                        background: lga.color || '#00f0ff',
                                        borderRadius: 2,
                                        transition: 'width 0.8s ease',
                                    }} />
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* ML Anomaly Detection — BELOW LGA grid */}
            {mlInsights?.anomalies?.anomalies_detected && (
                <div className="glass-panel fade-in" style={{ marginTop: 16, padding: 16, borderLeft: '3px solid #ff0040' }}>
                    <div className="heading-section" style={{ color: '#ff0040' }}>⚠ ML ANOMALY DETECTION</div>
                    {mlInsights.anomalies.details.map((anomaly, i) => (
                        <div key={i} style={{ padding: '6px 0', borderBottom: '1px solid rgba(255,255,255,0.03)', fontSize: '0.7rem' }}>
                            <span className={`badge badge-${anomaly.severity}`} style={{ marginRight: 8 }}>{anomaly.severity}</span>
                            <span style={{ color: '#e2e8f0' }}>{anomaly.description}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* WebSocket Live Feed */}
            {wsData?.type === 'intel_update' && (
                <div className="glass-panel fade-in" style={{ marginTop: 16, padding: 16 }}>
                    <div className="heading-section" style={{ color: '#00f0ff' }}>⚡ Live Intel Update</div>
                    <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.75rem', color: '#8892a4' }}>
                        {wsData.intel_count} intel reports • {wsData.fire_count} thermal anomalies • {new Date(wsData.timestamp).toLocaleString()}
                    </div>
                </div>
            )}

            {/* Data Quality Footer */}
            {dataQuality && (
                <div style={{ marginTop: 16, padding: '8px 12px', fontSize: '0.5rem', fontFamily: 'JetBrains Mono', color: '#4a5568', textAlign: 'center' }}>
                    Intel: {dataQuality.intel_source} | Fire: {dataQuality.fire_source} | LGA Risk: {dataQuality.lga_risk_method}
                </div>
            )}
        </div>
    );
}
