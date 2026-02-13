import React, { useState, useEffect, useRef } from 'react';
import { getTrackedSatellites, getSatellitesAbove, getSatellitePasses, getSentinelPasses } from '../../api/client';
import dataCache, { CACHE_KEYS } from '../../services/DataCache';

const SENTINEL_SATS = [
    { norad_id: 40697, name: 'SENTINEL-2A', type: 'Optical Imaging', band: 'Multi-spectral (13 bands)' },
    { norad_id: 42063, name: 'SENTINEL-2B', type: 'Optical Imaging', band: 'Multi-spectral (13 bands)' },
    { norad_id: 39634, name: 'SENTINEL-1A', type: 'SAR Radar', band: 'C-band (all weather)' },
    { norad_id: 41456, name: 'SENTINEL-1B', type: 'SAR Radar', band: 'C-band (all weather)' },
];

const KEY_SATS = [
    { norad_id: 25544, name: 'ISS (ZARYA)' },
    { norad_id: 36411, name: 'PLEIADES-1' },
    { norad_id: 43013, name: 'NOAA-20' },
];

export default function OrbitTracker({ voiceEnabled, speakText }) {
    // Initialize from cache for instant display
    const [tracked, setTracked] = useState(() => dataCache.get(CACHE_KEYS.SATELLITE_TRACKED));
    const [above, setAbove] = useState(() => dataCache.get(CACHE_KEYS.SATELLITE_ABOVE));
    const [sentinelData, setSentinelData] = useState(() => dataCache.get(CACHE_KEYS.SENTINEL_PASSES));
    const [countdown, setCountdown] = useState(null);
    const [loading, setLoading] = useState(!dataCache.get(CACHE_KEYS.SATELLITE_TRACKED));
    const [hoveredSat, setHoveredSat] = useState(null);
    const announcedRef = useRef({});
    const countdownRef = useRef(null);

    useEffect(() => {
        // If we have cached data, just refresh in background
        const hasCached = dataCache.get(CACHE_KEYS.SATELLITE_TRACKED) || 
                         dataCache.get(CACHE_KEYS.SENTINEL_PASSES);
        loadData(!hasCached); // Only show loading if no cache
        
        const interval = setInterval(() => loadData(false), 120000);
        return () => clearInterval(interval);
    }, []);

    // Countdown timer
    useEffect(() => {
        if (countdownRef.current) clearInterval(countdownRef.current);
        if (!sentinelData?.next_pass) return;

        countdownRef.current = setInterval(() => {
            const now = Date.now() / 1000;
            const nextUtc = sentinelData.next_pass.start_utc;
            const diff = Math.max(0, nextUtc - now);
            const hours = Math.floor(diff / 3600);
            const mins = Math.floor((diff % 3600) / 60);
            const secs = Math.floor(diff % 60);
            setCountdown({ hours, mins, secs, total_seconds: diff, satellite: sentinelData.next_pass.satellite });

            // Voice alerts
            if (voiceEnabled && speakText) {
                const key5 = `5min-${sentinelData.next_pass.satellite}`;
                const keyOver = `over-${sentinelData.next_pass.satellite}`;
                if (diff <= 320 && diff > 280 && !announcedRef.current[key5]) {
                    announcedRef.current[key5] = true;
                    speakText(`SENTINEL ALERT: ${sentinelData.next_pass.satellite} will be overhead in approximately 5 minutes. Prepare for imagery acquisition.`);
                }
                if (diff <= 30 && diff > 0 && !announcedRef.current[keyOver]) {
                    announcedRef.current[keyOver] = true;
                    speakText(`${sentinelData.next_pass.satellite} is now passing over Kebbi State. Imagery acquisition in progress.`);
                }
            }
        }, 1000);

        return () => clearInterval(countdownRef.current);
    }, [sentinelData, voiceEnabled, speakText]);

    const loadData = async (showLoading = false) => {
        if (showLoading) setLoading(true);
        try {
            const [trackedRes, aboveRes, sentinelRes] = await Promise.all([
                getTrackedSatellites().catch(() => null),
                getSatellitesAbove().catch(() => null),
                getSentinelPasses(3).catch(() => null),
            ]);
            
            if (trackedRes) {
                const trackedData = {
                    satellites: trackedRes.tracked_satellites || trackedRes.satellites || [],
                    total: trackedRes.total || 0,
                };
                setTracked(trackedData);
                dataCache.set(CACHE_KEYS.SATELLITE_TRACKED, trackedData);
            }
            
            if (aboveRes) {
                const aboveData = {
                    satcount: aboveRes.satellites_count || 0,
                    sats: aboveRes.satellites || [],
                };
                setAbove(aboveData);
                dataCache.set(CACHE_KEYS.SATELLITE_ABOVE, aboveData);
            }
            
            if (sentinelRes) {
                setSentinelData(sentinelRes);
                dataCache.set(CACHE_KEYS.SENTINEL_PASSES, sentinelRes);
            }
        } catch (e) { 
            // On error, keep cached data if available
            console.error('[OrbitTracker] Error loading data:', e);
        }
        setLoading(false);
    };

    const formatCountdown = () => {
        if (!countdown) return '--:--:--';
        return `${String(countdown.hours).padStart(2, '0')}:${String(countdown.mins).padStart(2, '0')}:${String(countdown.secs).padStart(2, '0')}`;
    };

    return (
        <div>
            <h2 className="section-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
                SATELLITE ORBIT TRACKER
                <span style={{ fontSize: '0.7rem', color: '#4a5568' }}>N2YO Live Tracking</span>
            </h2>

            {/* Sentinel Pass Countdown */}
            <div className="glass-panel" style={{ marginBottom: 16, padding: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                    <h3 style={{ color: '#00f0ff', fontFamily: 'Orbitron', fontSize: '0.75rem', margin: 0 }}>
                        🛰️ SENTINEL PASS COUNTDOWN
                    </h3>
                    {countdown && countdown.total_seconds < 300 && (
                        <span className="pulse-dot live" style={{ background: '#ff0040' }} />
                    )}
                </div>
                <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
                    <div style={{
                        fontFamily: 'Orbitron',
                        fontSize: '2rem',
                        color: countdown && countdown.total_seconds < 300 ? '#ff0040' : '#00f0ff',
                        textShadow: `0 0 20px ${countdown && countdown.total_seconds < 300 ? 'rgba(255,0,64,0.5)' : 'rgba(0,240,255,0.5)'}`,
                        letterSpacing: '0.05em',
                    }}>
                        {formatCountdown()}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: '#8a94a6' }}>
                        {countdown?.satellite && (
                            <div style={{ color: '#00ff80', fontFamily: 'Orbitron', fontSize: '0.65rem' }}>
                                NEXT: {countdown.satellite}
                            </div>
                        )}
                        {countdown && countdown.total_seconds < 300 ? (
                            <div style={{ color: '#ff0040', fontWeight: 'bold' }}>⚡ APPROACHING — PREPARE FOR IMAGERY</div>
                        ) : countdown && countdown.total_seconds < 1800 ? (
                            <div style={{ color: '#f0ff00' }}>⏱ PASSING SOON</div>
                        ) : (
                            <div>Next Sentinel pass over Kebbi State</div>
                        )}
                    </div>
                </div>
                {/* Upcoming passes */}
                {sentinelData?.upcoming_passes?.length > 0 && (
                    <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                        {sentinelData.upcoming_passes.slice(0, 4).map((p, i) => (
                            <div key={i} style={{
                                padding: '4px 10px',
                                background: i === 0 ? 'rgba(0,240,255,0.15)' : 'rgba(255,255,255,0.03)',
                                border: `1px solid ${i === 0 ? 'rgba(0,240,255,0.3)' : 'rgba(255,255,255,0.05)'}`,
                                borderRadius: 4,
                                fontSize: '0.6rem',
                                fontFamily: 'JetBrains Mono',
                            }}>
                                <span style={{ color: '#00f0ff' }}>{p.satellite}</span>
                                <span style={{ color: '#4a5568', margin: '0 4px' }}>|</span>
                                <span>{p.start_time ? new Date(p.start_time).toLocaleString() : `${Math.round(p.seconds_until / 60)}min`}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Sentinel Status Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 12, marginBottom: 16 }}>
                {SENTINEL_SATS.map(sat => {
                    const data = sentinelData?.sentinels?.[sat.name];
                    const isHovered = hoveredSat === sat.norad_id;
                    return (
                        <div
                            key={sat.norad_id}
                            className="glass-panel"
                            style={{ padding: 12, cursor: 'pointer', position: 'relative', transition: 'all 0.3s' }}
                            onMouseEnter={() => setHoveredSat(sat.norad_id)}
                            onMouseLeave={() => setHoveredSat(null)}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span style={{ fontFamily: 'Orbitron', fontSize: '0.65rem', color: '#00f0ff' }}>{sat.name}</span>
                                <span className="pulse-dot live" style={{ background: '#00ff80' }} />
                            </div>
                            <div style={{ fontSize: '0.6rem', color: '#8a94a6' }}>
                                <div>{sat.type}</div>
                                <div style={{ color: '#4a5568' }}>{sat.band}</div>
                                {data?.position && (
                                    <div style={{ marginTop: 4, color: '#00ff80', fontFamily: 'JetBrains Mono' }}>
                                        {data.position.latitude?.toFixed(2)}°N, {data.position.longitude?.toFixed(2)}°E
                                        <br />Alt: {data.position.altitude_km?.toFixed(0)} km
                                    </div>
                                )}
                                {data?.next_pass && (
                                    <div style={{ marginTop: 4, color: '#f0ff00' }}>
                                        Next pass: {data.next_pass.start_time ? new Date(data.next_pass.start_time).toLocaleString() : 'Calculating...'}
                                    </div>
                                )}
                            </div>
                            {/* Hover tooltip */}
                            {isHovered && (
                                <div style={{
                                    position: 'absolute',
                                    bottom: '105%',
                                    left: 0,
                                    right: 0,
                                    background: 'rgba(10,15,25,0.95)',
                                    border: '1px solid rgba(0,240,255,0.3)',
                                    borderRadius: 8,
                                    padding: 12,
                                    zIndex: 100,
                                    fontSize: '0.6rem',
                                    boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
                                }}>
                                    <div style={{ color: '#00f0ff', fontFamily: 'Orbitron', marginBottom: 6 }}>{sat.name} — ACTIVE</div>
                                    <div style={{ color: '#8a94a6' }}>
                                        <div>• Type: {sat.type}</div>
                                        <div>• Band: {sat.band}</div>
                                        <div>• NORAD: {sat.norad_id}</div>
                                        <div>• Passes scheduled: {data?.pass_count || 0}</div>
                                        {sat.type === 'SAR Radar' ? (
                                            <div style={{ color: '#00ff80', marginTop: 4 }}>✓ Can image through clouds and at night</div>
                                        ) : (
                                            <div style={{ color: '#f0ff00', marginTop: 4 }}>⚠ Requires clear skies for optical imaging</div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Satellites Above Kebbi */}
            <div className="glass-panel" style={{ padding: 16, marginBottom: 16 }}>
                <h3 style={{ color: '#00f0ff', fontFamily: 'Orbitron', fontSize: '0.75rem', marginBottom: 12 }}>
                    SATELLITES ABOVE KEBBI ({above?.satcount || 0})
                </h3>
                {loading ? (
                    <div style={{ color: '#4a5568', textAlign: 'center', padding: 20 }}>Loading satellite data...</div>
                ) : above?.sats?.length > 0 ? (
                    <div style={{ maxHeight: 200, overflowY: 'auto' }}>
                        <table style={{ width: '100%', fontSize: '0.65rem', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ color: '#4a5568', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                    <th style={{ textAlign: 'left', padding: '4px 8px' }}>Name</th>
                                    <th>NORAD</th>
                                    <th>Lat</th>
                                    <th>Lon</th>
                                    <th>Alt (km)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {above.sats.slice(0, 20).map((s, i) => (
                                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                                        <td style={{ padding: '4px 8px', color: '#e2e8f0' }}>{s.satname}</td>
                                        <td style={{ textAlign: 'center', color: '#4a5568' }}>{s.satid}</td>
                                        <td style={{ textAlign: 'center' }}>{s.satlat?.toFixed(2)}°</td>
                                        <td style={{ textAlign: 'center' }}>{s.satlng?.toFixed(2)}°</td>
                                        <td style={{ textAlign: 'center', color: '#00f0ff' }}>{s.satalt?.toFixed(0)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div style={{ color: '#4a5568', textAlign: 'center' }}>No satellites detected above Kebbi at this time</div>
                )}
            </div>

            {/* Tracked Satellite Positions */}
            <div className="glass-panel" style={{ padding: 16 }}>
                <h3 style={{ color: '#00f0ff', fontFamily: 'Orbitron', fontSize: '0.75rem', marginBottom: 12 }}>
                    TRACKED RECONNAISSANCE ASSETS
                </h3>
                {tracked?.satellites?.length > 0 ? (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 8 }}>
                        {tracked.satellites.map((sat, i) => (
                            <div key={i} style={{
                                padding: 8,
                                background: 'rgba(255,255,255,0.02)',
                                borderRadius: 6,
                                border: '1px solid rgba(255,255,255,0.05)',
                                fontSize: '0.6rem',
                            }}>
                                <div style={{ color: '#00f0ff', fontFamily: 'Orbitron', fontSize: '0.6rem', marginBottom: 4 }}>{sat.name}</div>
                                {sat.position && (
                                    <div style={{ color: '#8a94a6', fontFamily: 'JetBrains Mono' }}>
                                        {sat.position.latitude?.toFixed(2)}°N, {sat.position.longitude?.toFixed(2)}°E
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ color: '#4a5568', textAlign: 'center' }}>Loading tracked assets...</div>
                )}
            </div>
        </div>
    );
}
