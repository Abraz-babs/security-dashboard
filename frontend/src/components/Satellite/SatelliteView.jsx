import React, { useState, useEffect } from 'react';
import { getCopernicusProducts, getFIRMSAll, getSARProducts, getFireSatelliteCorrelation } from '../../api/client';
import dataCache, { CACHE_KEYS } from '../../services/DataCache';

export default function SatelliteView() {
    // Initialize from cache immediately
    const cachedProducts = dataCache.get(CACHE_KEYS.COPERNICUS_PRODUCTS);
    const cachedHotspots = dataCache.get(CACHE_KEYS.FIRMS_HOTSPOTS);
    const cachedSAR = dataCache.get('sar_products');
    
    const [products, setProducts] = useState(cachedProducts);
    const [hotspots, setHotspots] = useState(cachedHotspots);
    const [sarProducts, setSarProducts] = useState(cachedSAR);
    const [fireCorrelations, setFireCorrelations] = useState(null);
    const [loading, setLoading] = useState(!cachedProducts && !cachedHotspots);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [activeTab, setActiveTab] = useState('imagery');

    useEffect(() => {
        const load = async () => {
            // If we have cached data, show refresh indicator
            if (cachedProducts || cachedHotspots) {
                setIsRefreshing(true);
            }
            
            try {
                const [p, h, s] = await Promise.all([
                    getCopernicusProducts(7),
                    getFIRMSAll(2),
                    getSARProducts(7).catch(() => null),
                ]);
                
                if (p) {
                    setProducts(p);
                    dataCache.set(CACHE_KEYS.COPERNICUS_PRODUCTS, p);
                }
                if (h) {
                    setHotspots(h);
                    dataCache.set(CACHE_KEYS.FIRMS_HOTSPOTS, h);
                }
                if (s) {
                    setSarProducts(s);
                    dataCache.set('sar_products', s);
                }
                
                // Load fire correlations if we have hotspots
                if (h && h.total > 0) {
                    const correlations = await getFireSatelliteCorrelation(3).catch(() => null);
                    if (correlations) {
                        setFireCorrelations(correlations);
                    }
                }
            } catch (e) { 
                console.error('Satellite data error:', e);
            }
            
            setLoading(false);
            setIsRefreshing(false);
        };
        
        load();
    }, []);

    if (loading) return <div className="loading-spinner">Acquiring satellite data...</div>;

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
                    Refreshing satellite data...
                </div>
            )}

            <div className="section-header">
                <h2>Satellite Intelligence</h2>
                <div style={{ display: 'flex', gap: 8 }}>
                    <button className={`btn-neon${activeTab === 'imagery' ? ' btn-filled' : ''}`} onClick={() => setActiveTab('imagery')}>Copernicus</button>
                    <button className={`btn-neon${activeTab === 'sar' ? ' btn-filled' : ''}`} onClick={() => setActiveTab('sar')} title="Works through clouds">SAR (All-Weather)</button>
                    <button className={`btn-neon${activeTab === 'thermal' ? ' btn-filled' : ''}`} onClick={() => setActiveTab('thermal')}>NASA FIRMS</button>
                </div>
            </div>

            {activeTab === 'imagery' && (
                <div>
                    <div className="glass-panel" style={{ padding: 18, marginBottom: 16 }}>
                        <div className="heading-section">Sentinel-2 Products — Kebbi State</div>
                        <div style={{ display: 'flex', gap: 16, marginBottom: 12 }}>
                            <div className="badge badge-low">◉ {products?.total || 0} Products Found</div>
                            <div className="badge" style={{ background: 'rgba(0,240,255,0.1)', color: '#00f0ff', border: '1px solid rgba(0,240,255,0.2)' }}>
                                Source: {products?.source || 'loading'}
                            </div>
                        </div>
                    </div>
                    {(products?.products || []).length === 0 ? (
                        <div className="glass-panel" style={{ padding: 30, textAlign: 'center' }}>
                            <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem', color: '#8892a4' }}>
                                No Sentinel-2 products available for the current query window.<br />
                                <span style={{ fontSize: '0.65rem', color: '#4a5568' }}>This may be due to cloud cover or orbital timing. System is monitoring.</span>
                            </div>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gap: 12 }}>
                            {(products?.products || []).map((p, i) => (
                                <div key={i} className="glass-panel" style={{ padding: 16 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div>
                                            <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem', fontWeight: 600, color: '#e0e6f0', marginBottom: 6, wordBreak: 'break-all' }}>{p.name}</div>
                                            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                                                <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: '#8892a4' }}>📅 {p.date ? new Date(p.date).toLocaleDateString() : 'N/A'}</span>
                                                <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: '#8892a4' }}>☁️ Cloud: {p.cloud_cover !== 'N/A' ? `${p.cloud_cover}%` : 'N/A'}</span>
                                                <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: '#8892a4' }}>📦 {(p.size / 1e6).toFixed(1)} MB</span>
                                            </div>
                                        </div>
                                        <span className={`badge ${p.online ? 'badge-low' : 'badge-medium'}`}>{p.online ? 'ONLINE' : 'ARCHIVED'}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'sar' && (
                <div>
                    <div className="glass-panel" style={{ padding: 18, marginBottom: 16 }}>
                        <div className="heading-section">Sentinel-1 SAR — All Weather Imaging</div>
                        <div style={{ display: 'flex', gap: 16, marginBottom: 12, flexWrap: 'wrap' }}>
                            <div className="badge badge-low">◉ {sarProducts?.total || 0} SAR Products</div>
                            <div className="badge" style={{ background: 'rgba(255,193,7,0.15)', color: '#ffc107', border: '1px solid rgba(255,193,7,0.3)' }}>
                                ☁️ Penetrates Clouds
                            </div>
                            <div className="badge" style={{ background: 'rgba(0,240,255,0.1)', color: '#00f0ff', border: '1px solid rgba(0,240,255,0.2)' }}>
                                🌙 Night Capable
                            </div>
                        </div>
                        <div style={{ fontSize: '0.7rem', color: '#8892a4', marginTop: 8 }}>
                            Use SAR during rainy season or when optical imagery is blocked by cloud cover.
                            SAR radar penetrates clouds and works 24/7.
                        </div>
                    </div>
                    {(sarProducts?.products || []).length === 0 ? (
                        <div className="glass-panel" style={{ padding: 30, textAlign: 'center' }}>
                            <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem', color: '#8892a4' }}>
                                No Sentinel-1 SAR products available.<br />
                                <span style={{ fontSize: '0.65rem', color: '#4a5568' }}>SAR passes less frequently than optical. Check back in 24-48 hours.</span>
                            </div>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gap: 12 }}>
                            {(sarProducts?.products || []).map((p, i) => (
                                <div key={i} className="glass-panel" style={{ padding: 16 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div>
                                            <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem', fontWeight: 600, color: '#ffc107', marginBottom: 6, wordBreak: 'break-all' }}>
                                                {p.name}
                                            </div>
                                            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                                                <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: '#8892a4' }}>📅 {p.date ? new Date(p.date).toLocaleDateString() : 'N/A'}</span>
                                                <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: '#ffc107' }}>📡 {p.mode} Mode</span>
                                                <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: '#ffc107' }}>📶 {p.polarization}</span>
                                                <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem', color: '#8892a4' }}>📦 {(p.size / 1e6).toFixed(1)} MB</span>
                                            </div>
                                        </div>
                                        <span className={`badge ${p.online ? 'badge-low' : 'badge-medium'}`}>{p.online ? 'ONLINE' : 'ARCHIVED'}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'thermal' && (
                <div>
                    <div className="glass-panel" style={{ padding: 18, marginBottom: 16 }}>
                        <div className="heading-section">Fire & Thermal Anomalies — NASA FIRMS</div>
                        <div style={{ display: 'flex', gap: 16, marginBottom: 12 }}>
                            <div className={`badge ${(hotspots?.total || 0) > 0 ? 'badge-critical' : 'badge-low'}`}>
                                🔥 {hotspots?.total || 0} Hotspots Detected
                            </div>
                            <div className="badge" style={{ background: 'rgba(0,240,255,0.1)', color: '#00f0ff', border: '1px solid rgba(0,240,255,0.2)' }}>
                                Sensors: {hotspots?.sensors_queried || 0}
                            </div>
                        </div>
                    </div>
                    
                    {/* Fire Correlation Recommendations */}
                    {fireCorrelations && fireCorrelations.recommendations && fireCorrelations.recommendations.length > 0 && (
                        <div className="glass-panel" style={{ padding: 18, marginBottom: 16, border: '1px solid rgba(255,193,7,0.3)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                                <span style={{ fontSize: '1.2rem' }}>📡</span>
                                <div className="heading-section" style={{ margin: 0, color: '#ffc107' }}>Imaging Recommendations</div>
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#8892a4', marginBottom: 12 }}>
                                Detected fires matched with upcoming satellite passes for optimal imaging:
                            </div>
                            <div style={{ display: 'grid', gap: 10 }}>
                                {fireCorrelations.recommendations.map((rec, i) => (
                                    <div key={i} style={{ 
                                        padding: 12, 
                                        background: 'rgba(255,193,7,0.05)', 
                                        borderRadius: 6,
                                        border: '1px solid rgba(255,193,7,0.15)'
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                                            <span style={{ fontSize: '0.7rem', color: '#ffc107', fontWeight: 600 }}>
                                                FIRE #{i+1}: {rec.hotspot.lat.toFixed(3)}°N, {rec.hotspot.lon.toFixed(3)}°E
                                            </span>
                                            <span className={`badge ${rec.priority === 'HIGH' ? 'badge-critical' : 'badge-medium'}`}>
                                                {rec.priority} PRIORITY
                                            </span>
                                        </div>
                                        <div style={{ fontSize: '0.7rem', color: '#e0e6f0' }}>
                                            🛰️ {rec.recommended_pass.satellite} in {rec.recommended_pass.hours_until}h
                                            {' '}(elev: {rec.recommended_pass.max_elevation}°)
                                        </div>
                                        <div style={{ fontSize: '0.6rem', color: '#8892a4', marginTop: 4 }}>
                                            {rec.rationale}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    {(hotspots?.hotspots || []).length === 0 ? (
                        <div className="glass-panel" style={{ padding: 30, textAlign: 'center' }}>
                            <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem', color: '#00ff80' }}>
                                ✓ No active fire/thermal anomalies detected in Kebbi State AOR
                            </div>
                        </div>
                    ) : (
                        <table className="data-table glass-panel">
                            <thead>
                                <tr>
                                    <th>Latitude</th><th>Longitude</th><th>Brightness</th>
                                    <th>Confidence</th><th>Date</th><th>Satellite</th><th>FRP</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(hotspots?.hotspots || []).map((h, i) => (
                                    <tr key={i}>
                                        <td style={{ color: '#00f0ff' }}>{h.latitude?.toFixed(4)}°N</td>
                                        <td style={{ color: '#00f0ff' }}>{h.longitude?.toFixed(4)}°E</td>
                                        <td style={{ color: h.brightness > 350 ? '#ff0040' : '#f0ff00' }}>{h.brightness?.toFixed(1)} K</td>
                                        <td><span className={`badge badge-${h.confidence === 'high' ? 'critical' : h.confidence === 'nominal' ? 'medium' : 'low'}`}>{h.confidence}</span></td>
                                        <td>{h.acq_date} {h.acq_time}</td>
                                        <td>{h.satellite}</td>
                                        <td>{h.frp ? `${h.frp.toFixed(1)} MW` : 'N/A'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}
        </div>
    );
}
