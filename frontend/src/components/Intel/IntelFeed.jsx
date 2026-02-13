import React, { useState, useEffect, useCallback } from 'react';
import { getSecurityIntel, getIntelFeed } from '../../api/client';
import dataCache, { CACHE_KEYS } from '../../services/DataCache';

export default function IntelFeed() {
    // Initialize from cache immediately - PERSISTENT across tab switches
    const cachedIntel = dataCache.get(CACHE_KEYS.INTEL_REPORTS);
    
    const [reports, setReports] = useState(cachedIntel?.reports || []);
    const [loading, setLoading] = useState(!cachedIntel); // Only loading if no cache
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [filter, setFilter] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [expanded, setExpanded] = useState(null);
    const [source, setSource] = useState(cachedIntel?.source || '');
    const [lastUpdate, setLastUpdate] = useState(() => {
        const ts = dataCache.getTimestamp(CACHE_KEYS.INTEL_REPORTS);
        return ts ? new Date(ts).toLocaleTimeString() : null;
    });
    const [autoRefresh, setAutoRefresh] = useState(true);

    const loadIntel = useCallback(async (showRefreshIndicator = false) => {
        // If we have data, show refresh indicator instead of loading spinner
        if (reports.length > 0 && showRefreshIndicator) {
            setIsRefreshing(true);
        } else if (!cachedIntel) {
            setLoading(true);
        }
        
        try {
            let data;
            if (searchQuery.trim()) {
                data = await getIntelFeed(searchQuery, 20);
            } else {
                data = await getSecurityIntel();
            }
            
            if (data?.reports) {
                setReports(data.reports);
                dataCache.set(CACHE_KEYS.INTEL_REPORTS, data);
            }
            setSource(data?.source || 'unknown');
            setLastUpdate(new Date().toLocaleTimeString());
        } catch (e) {
            console.error('Intel fetch error:', e);
        }
        
        setLoading(false);
        setIsRefreshing(false);
    }, [searchQuery, reports.length, cachedIntel]);

    // Initial load - fetch from API but show cached data immediately
    useEffect(() => {
        loadIntel(true);
    }, []);

    // Auto-refresh every 2 min
    useEffect(() => {
        if (!autoRefresh) return;
        const interval = setInterval(() => loadIntel(true), 120000);
        return () => clearInterval(interval);
    }, [autoRefresh, loadIntel]);

    const handleSearch = (e) => {
        e.preventDefault();
        loadIntel(true);
    };

    const filteredReports = reports.filter(r => {
        if (filter === 'all') return true;
        return r.severity === filter;
    });

    const severityCounts = {
        all: reports.length,
        critical: reports.filter(r => r.severity === 'critical').length,
        high: reports.filter(r => r.severity === 'high').length,
        medium: reports.filter(r => r.severity === 'medium').length,
        low: reports.filter(r => r.severity === 'low').length,
    };

    const severityColors = {
        critical: '#ff0040',
        high: '#ff6600',
        medium: '#f0ff00',
        low: '#00ff80',
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: 60 }}>
                <div className="loading-spinner" style={{ margin: '0 auto 20px' }} />
                <div style={{ color: '#4a5568', fontSize: '0.8rem' }}>Loading intelligence feeds...</div>
            </div>
        );
    }

    return (
        <div>
            {/* Header with refresh indicator */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h2 className="section-header" style={{ margin: 0 }}>OSINT INTELLIGENCE FEED</h2>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                    {isRefreshing && (
                        <div style={{ 
                            fontSize: '0.6rem', 
                            color: '#00f0ff',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6
                        }}>
                            <span className="loading-spinner" style={{ width: 12, height: 12, margin: 0 }} />
                            Refreshing...
                        </div>
                    )}
                    <div style={{ fontSize: '0.6rem', display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span className="pulse-dot live" />
                        <span style={{ color: '#00ff80' }}>LIVE</span>
                    </div>
                    <button className="btn-neon" onClick={() => loadIntel(true)} style={{ fontSize: '0.65rem', padding: '4px 12px' }}>
                        ↻ REFRESH
                    </button>
                </div>
            </div>

            {/* Search */}
            <form className="glass-panel" style={{ padding: 12, marginBottom: 12, display: 'flex', gap: 12 }} onSubmit={handleSearch}>
                <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="Search intel... (e.g., 'Kebbi bandit attack', 'Nigeria military')"
                    style={{
                        flex: 1,
                        background: 'rgba(255,255,255,0.03)',
                        border: '1px solid rgba(0,240,255,0.15)',
                        borderRadius: 6,
                        padding: '8px 12px',
                        color: '#e2e8f0',
                        fontFamily: 'JetBrains Mono',
                        fontSize: '0.7rem',
                    }}
                />
                <button className="btn-neon btn-filled" type="submit" style={{ padding: '8px 16px' }}>SEARCH</button>
            </form>

            {/* Severity Filters */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap', alignItems: 'center' }}>
                {Object.entries(severityCounts).map(([key, count]) => (
                    <button
                        key={key}
                        onClick={() => setFilter(key)}
                        style={{
                            padding: '4px 12px',
                            borderRadius: 4,
                            border: `1px solid ${filter === key ? (severityColors[key] || '#00f0ff') : 'rgba(255,255,255,0.1)'}`,
                            background: filter === key ? `${severityColors[key] || '#00f0ff'}22` : 'transparent',
                            color: severityColors[key] || '#00f0ff',
                            fontFamily: 'JetBrains Mono',
                            fontSize: '0.6rem',
                            cursor: 'pointer',
                            textTransform: 'uppercase',
                        }}
                    >
                        {key} ({count})
                    </button>
                ))}
                <span style={{ marginLeft: 'auto', fontSize: '0.55rem', color: '#4a5568' }}>
                    Source: {source} | Updated: {lastUpdate || '--'}
                </span>
            </div>

            {/* Reports */}
            <div className="glass-panel" style={{ padding: 12 }}>
                {filteredReports.length > 0 ? (
                    <div style={{ maxHeight: 500, overflowY: 'auto' }}>
                        {filteredReports.map((report, i) => (
                            <div
                                key={i}
                                style={{
                                    padding: 12,
                                    marginBottom: 8,
                                    background: 'rgba(255,255,255,0.02)',
                                    borderRadius: 8,
                                    borderLeft: `3px solid ${severityColors[report.severity] || '#4a5568'}`,
                                    cursor: 'pointer',
                                    transition: 'all 0.2s',
                                }}
                                onClick={() => setExpanded(expanded === i ? null : i)}
                                onMouseEnter={e => e.currentTarget.style.background = 'rgba(0,240,255,0.05)'}
                                onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                                    <div style={{ flex: 1 }}>
                                        <span style={{
                                            display: 'inline-block',
                                            padding: '2px 6px',
                                            borderRadius: 3,
                                            background: `${severityColors[report.severity]}22`,
                                            color: severityColors[report.severity],
                                            fontFamily: 'Orbitron',
                                            fontSize: '0.5rem',
                                            marginRight: 8,
                                            textTransform: 'uppercase',
                                        }}>
                                            {report.severity}
                                        </span>
                                        <span style={{
                                            display: 'inline-block',
                                            padding: '2px 6px',
                                            borderRadius: 3,
                                            background: 'rgba(255,255,255,0.05)',
                                            color: '#8a94a6',
                                            fontSize: '0.5rem',
                                            marginRight: 8,
                                        }}>
                                            {report.category}
                                        </span>
                                        {report.kebbi_relevant && (
                                            <span style={{
                                                display: 'inline-block',
                                                padding: '2px 6px',
                                                borderRadius: 3,
                                                background: 'rgba(0,240,255,0.15)',
                                                color: '#00f0ff',
                                                fontSize: '0.5rem',
                                            }}>
                                                KEBBI
                                            </span>
                                        )}
                                    </div>
                                    <span style={{ fontSize: '0.55rem', color: '#4a5568', whiteSpace: 'nowrap' }}>
                                        {report.published_at ? new Date(report.published_at).toLocaleString() : ''}
                                    </span>
                                </div>
                                <div style={{ color: '#e2e8f0', fontSize: '0.75rem', fontWeight: 600, marginBottom: 4 }}>
                                    {report.title}
                                </div>
                                <div style={{ fontSize: '0.6rem', color: '#4a5568' }}>
                                    Source: {report.source}
                                </div>
                                {expanded === i && (
                                    <div style={{
                                        marginTop: 8,
                                        padding: 8,
                                        background: 'rgba(0,0,0,0.2)',
                                        borderRadius: 6,
                                        fontSize: '0.65rem',
                                        color: '#8a94a6',
                                        lineHeight: 1.6,
                                    }}>
                                        {report.description || 'No additional details available.'}
                                        {report.url && (
                                            <div style={{ marginTop: 8 }}>
                                                <a href={report.url} target="_blank" rel="noopener noreferrer"
                                                    style={{ color: '#00f0ff', textDecoration: 'none' }}>
                                                    View Source →
                                                </a>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ textAlign: 'center', padding: 40, color: '#4a5568' }}>
                        {isRefreshing || source === 'warming' ? (
                            <>
                                <div className="loading-spinner" style={{ margin: '0 auto 16px' }} />
                                <div>Initializing intelligence feeds...</div>
                                <div style={{ fontSize: '0.6rem', marginTop: 8, opacity: 0.7 }}>
                                    Gathering data from multiple sources
                                </div>
                            </>
                        ) : (
                            <>
                                <div style={{ marginBottom: 12 }}>No intel reports available.</div>
                                <button className="btn-neon" onClick={() => loadIntel(true)}>
                                    Retry Fetch
                                </button>
                            </>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
