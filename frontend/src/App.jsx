import React, { useState, useEffect, useCallback, useRef } from 'react';
import LoginScreen from './components/Auth/LoginScreen';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import DashboardView from './components/Dashboard/DashboardView';
import SatelliteView from './components/Satellite/SatelliteView';
import OrbitTracker from './components/Satellite/OrbitTracker';
import IntelFeed from './components/Intel/IntelFeed';
import ChatBot from './components/AI/ChatBot';
import AIAnalysis from './components/AI/AIAnalysis';
import SITREPGenerator from './components/SITREP/SITREPGenerator';
import AnalyticsView from './components/Analytics/AnalyticsView';
import Globe3D from './components/Globe/Globe3D';
import AdminPanel from './components/Admin/AdminPanel';
import { createWebSocket, getDashboardOverview, invalidateCache } from './api/client';
import dataCache, { CACHE_KEYS } from './services/DataCache';

export default function App() {
    // Persist auth across page refresh using localStorage
    const [authenticated, setAuthenticated] = useState(() => {
        const saved = localStorage.getItem('citadel_user');
        return !!saved;
    });
    const [user, setUser] = useState(() => {
        try { return JSON.parse(localStorage.getItem('citadel_user') || 'null'); }
        catch { return null; }
    });
    const [activeTab, setActiveTab] = useState('dashboard');
    // Use cache for initial dashboard data (survives tab switching)
    const [dashboardData, setDashboardData] = useState(() => dataCache.get(CACHE_KEYS.DASHBOARD));
    const [voiceEnabled, setVoiceEnabled] = useState(true);
    const [wsData, setWsData] = useState(null);
    const [sentinelAlert, setSentinelAlert] = useState(null);
    const wsRef = useRef(null);
    const prevIntelCount = useRef(0);
    const welcomeSpoken = useRef(!!localStorage.getItem('citadel_user'));

    // WebSocket connection
    useEffect(() => {
        if (!authenticated) return;
        wsRef.current = createWebSocket((data) => {
            setWsData(data);
            if (data.type === 'intel_update' && voiceEnabled) {
                speakIntelUpdate(data);
            }
            if (data.type === 'sentinel_alert' && voiceEnabled) {
                setSentinelAlert(data);
                speakText(`SENTINEL ALERT: ${data.message}`);
            }
        });
        return () => { if (wsRef.current) wsRef.current.close(); };
    }, [authenticated]);

    // Periodic dashboard refresh with caching
    useEffect(() => {
        if (!authenticated) return;
        
        const refresh = async () => {
            try {
                const data = await getDashboardOverview();
                setDashboardData(data);
                dataCache.set(CACHE_KEYS.DASHBOARD, data); // Persist to cache
            } catch (e) { 
                // If fetch fails, use cached data if available
                const cached = dataCache.get(CACHE_KEYS.DASHBOARD);
                if (cached && !dashboardData) {
                    setDashboardData(cached);
                }
            }
        };
        
        // If no cached data, fetch immediately
        if (!dataCache.get(CACHE_KEYS.DASHBOARD)) {
            refresh();
        }
        
        const interval = setInterval(refresh, 120000); // Refresh every 2 minutes
        return () => clearInterval(interval);
    }, [authenticated]);

    // Welcome voice on login (only the first time after clicking login, not on refresh)
    const handleLogin = useCallback((userData) => {
        setAuthenticated(true);
        setUser(userData);
        localStorage.setItem('citadel_user', JSON.stringify(userData));
        localStorage.setItem('citadel_token', userData?.token || 'active');
        if (!welcomeSpoken.current) {
            welcomeSpoken.current = true;
            setTimeout(() => {
                const name = userData?.username || 'Analyst';
                speakTextDirect(
                    `Welcome to CITADEL, ${name}. All surveillance systems are operational. ` +
                    `Intelligence feeds active. Standing by for your instructions.`
                );
            }, 1500);
        }
    }, []);

    // Text-to-Speech
    const speakTextDirect = (text) => {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.95;
        utterance.pitch = 0.9;
        utterance.volume = 0.8;
        const voices = window.speechSynthesis.getVoices();
        const preferred = voices.find(v => v.name.includes('Google') && v.lang.startsWith('en'));
        if (preferred) utterance.voice = preferred;
        window.speechSynthesis.speak(utterance);
    };

    const speakText = useCallback((text) => {
        if (!voiceEnabled || !window.speechSynthesis) return;
        speakTextDirect(text);
    }, [voiceEnabled]);

    const stopSpeaking = useCallback(() => {
        window.speechSynthesis?.cancel();
    }, []);

    // Dynamic intel update voice
    const speakIntelUpdate = useCallback((data) => {
        if (!voiceEnabled) return;
        const newCount = data.intel_count || 0;
        const fires = data.fire_count || 0;
        const delta = newCount - prevIntelCount.current;
        prevIntelCount.current = newCount;

        let msg = `CITADEL intelligence update. `;
        if (delta > 0) {
            msg += `${delta} new intel reports received, bringing total to ${newCount}. `;
        } else if (newCount > 0) {
            msg += `${newCount} active intel reports being monitored. `;
        } else {
            msg += `Intel feeds active, no new reports at this time. `;
        }
        if (fires > 0) msg += `${fires} thermal anomalies detected in the operational area. `;
        if (data.sentinel_next_pass) {
            const mins = Math.round(data.sentinel_next_pass.seconds_until / 60);
            if (mins <= 30) {
                msg += `${data.sentinel_next_pass.satellite} pass in approximately ${mins} minutes. `;
            }
        }
        speakText(msg);
    }, [voiceEnabled, speakText]);

    // Periodic voice briefing
    useEffect(() => {
        if (!authenticated || !voiceEnabled) return;
        const briefingInterval = setInterval(() => {
            if (!voiceEnabled || !dashboardData) return;
            const level = dashboardData?.threat_level || 'UNKNOWN';
            const threats = dashboardData?.stats?.active_threats || 0;
            const intel = dashboardData?.stats?.intel_reports || 0;
            const fires = dashboardData?.stats?.fire_hotspots || 0;

            let briefing = `CITADEL periodic briefing. Current threat level: ${level}. `;
            briefing += `${threats} active threats detected across Kebbi State. `;
            if (intel > 0) briefing += `${intel} intelligence reports being tracked. `;
            if (fires > 0) briefing += `${fires} thermal anomalies under surveillance. `;
            briefing += `All surveillance systems operational.`;
            speakText(briefing);
        }, 300000);
        return () => clearInterval(briefingInterval);
    }, [authenticated, voiceEnabled, dashboardData, speakText]);

    // Logout handler
    const handleLogout = useCallback(() => {
        stopSpeaking();
        localStorage.removeItem('citadel_token');
        localStorage.removeItem('citadel_user');
        invalidateCache();
        dataCache.clear(); // Clear all cached data
        setAuthenticated(false);
        setUser(null);
        setDashboardData(null);
        setActiveTab('dashboard');
        welcomeSpoken.current = false;
        prevIntelCount.current = 0;
        if (wsRef.current) wsRef.current.close();
    }, [stopSpeaking]);

    if (!authenticated) {
        return <LoginScreen onLogin={handleLogin} />;
    }

    const renderContent = () => {
        switch (activeTab) {
            case 'dashboard': return <DashboardView data={dashboardData} wsData={wsData} sentinelAlert={sentinelAlert} />;
            case 'satellite': return <SatelliteView />;
            case 'orbit': return <OrbitTracker voiceEnabled={voiceEnabled} speakText={speakText} />;
            case 'intel': return <IntelFeed />;
            case 'chat': return <ChatBot voiceEnabled={voiceEnabled} speakText={speakText} stopSpeaking={stopSpeaking} />;
            case 'analysis': return <AIAnalysis dashboardData={dashboardData} speakText={speakText} voiceEnabled={voiceEnabled} />;
            case 'sitrep': return <SITREPGenerator />;
            case 'analytics': return <AnalyticsView dashboardData={dashboardData} />;
            case 'globe': return <Globe3D />;
            case 'admin': return <AdminPanel />;
            default: return <DashboardView data={dashboardData} wsData={wsData} />;
        }
    };

    return (
        <>
            <div className="tech-grid-bg" />
            <div className="scan-line-overlay" />
            <div className="app-layout">
                <Sidebar activeTab={activeTab} onTabChange={setActiveTab} onLogout={handleLogout} user={user} />
                <div className="main-content">
                    <Header
                        dashboardData={dashboardData}
                        voiceEnabled={voiceEnabled}
                        onToggleVoice={() => {
                            if (voiceEnabled) stopSpeaking();
                            setVoiceEnabled(!voiceEnabled);
                        }}
                    />
                    <div className="content-area">
                        {sentinelAlert && sentinelAlert.alert === 'overhead' && (
                            <div className="sentinel-banner">
                                🛰️ {sentinelAlert.satellite} IS NOW OVERHEAD — IMAGERY ACQUISITION IN PROGRESS
                            </div>
                        )}
                        {renderContent()}
                    </div>
                </div>
            </div>
        </>
    );
}
