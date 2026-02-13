/**
 * CITADEL KEBBI - API Client (V2 Enhanced)
 * Handles all communication with the FastAPI backend.
 * Includes client-side caching for faster tab switching.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

// ── Cache Layer ──
const cache = new Map();
const CACHE_TTL = 60000; // 60 seconds

function getCached(key) {
    const item = cache.get(key);
    if (item && Date.now() - item.ts < CACHE_TTL) return item.data;
    return null;
}

function setCache(key, data) {
    cache.set(key, { data, ts: Date.now() });
}

export function invalidateCache(pattern) {
    for (const key of cache.keys()) {
        if (!pattern || key.includes(pattern)) cache.delete(key);
    }
}

async function request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
    const cacheKey = options.method ? null : url; // Only cache GET requests

    if (cacheKey && !options.noCache) {
        const cached = getCached(cacheKey);
        if (cached) return cached;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), options.timeout || 20000); // 20s default timeout

    const config = {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        signal: controller.signal,
        ...options,
    };
    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    try {
        const resp = await fetch(url, config);
        clearTimeout(timeoutId);

        if (!resp.ok) {
            const errorData = await resp.json().catch(() => ({}));
            throw new Error(errorData.detail || `API Error ${resp.status}: ${resp.statusText}`);
        }
        const data = await resp.json();

        if (cacheKey) setCache(cacheKey, data);
        return data;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('Request timeout - backend is not responding');
        }
        throw error;
    }
}

// ── Auth ──
export const login = (username, password) =>
    request('/api/auth/login', { method: 'POST', body: { username, password } });

// ── Dashboard ──
export const getDashboardOverview = () => request('/api/dashboard/overview', { timeout: 30000 });
export const getLGAData = () => request('/api/dashboard/lgas');
export const getThreatLevel = () => request('/api/dashboard/threat-level');
export const getMLInsights = () => request('/api/dashboard/ml-insights');

// ── Satellite ──
export const getCopernicusProducts = (days = 7) =>
    request(`/api/satellite/copernicus/products?days=${days}`);
export const getCopernicusPasses = () => request('/api/satellite/copernicus/passes');
export const getSARProducts = (days = 7) => request(`/api/satellite/copernicus/sar?days=${days}`);
export const getFireSatelliteCorrelation = (days = 3) => request(`/api/satellite/correlate/fires?days=${days}`);
export const getFIRMSHotspots = (sensor = 'VIIRS_SNPP_NRT', days = 2) =>
    request(`/api/satellite/firms/hotspots?sensor=${sensor}&days=${days}`);
export const getFIRMSAll = (days = 2) => request(`/api/satellite/firms/all?days=${days}`);
export const getSatellitePosition = (noradId) =>
    request(`/api/satellite/n2yo/position/${noradId}`);
export const getSatellitePasses = (noradId, days = 5) =>
    request(`/api/satellite/n2yo/passes/${noradId}?days=${days}`);
export const getSatellitesAbove = () => request('/api/satellite/n2yo/above');
export const getTrackedSatellites = () => request('/api/satellite/n2yo/tracked');
export const getSentinelPasses = (days = 5) =>
    request(`/api/satellite/sentinel/passes?days=${days}`, { noCache: true });

// ── Intel ──
export const getIntelFeed = (query = '', limit = 10) =>
    request(`/api/intel/feed?query=${encodeURIComponent(query || 'Nigeria security')}&limit=${limit}`, { timeout: 25000 });
// Security intel - use cache if available, 25s timeout for slow RSS feeds
export const getSecurityIntel = () => request('/api/intel/security', { timeout: 25000 });

// ── AI ──
export const sendChatMessage = (message, context = null) =>
    request('/api/ai/chat', { method: 'POST', body: { message, context } });
export const runAIAnalysis = (dashboardData = null, focusArea = null) =>
    request('/api/ai/analyze', { method: 'POST', body: { dashboard_data: dashboardData, focus_area: focusArea }, timeout: 45000 });
export const generateSITREP = (period = '24h') =>
    request('/api/ai/sitrep', { method: 'POST', body: { period, include_ai_analysis: true }, timeout: 45000 });
export const clearChatHistory = () =>
    request('/api/ai/clear-history', { method: 'POST' });

// ── WebSocket ──
export function createWebSocket(onMessage) {
    const ws = new WebSocket(`${WS_BASE}/ws`);
    ws.onopen = () => {
        ws.send(JSON.stringify({ type: 'subscribe', channel: 'all' }));
    };
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            onMessage(data);
        } catch (e) { /* ignore */ }
    };
    ws.onerror = () => { };
    ws.onclose = () => {
        setTimeout(() => createWebSocket(onMessage), 5000);
    };
    return ws;
}
