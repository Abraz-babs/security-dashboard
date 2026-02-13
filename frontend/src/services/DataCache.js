/**
 * DataCache - Persistent cache for dashboard data
 * Survives tab switching and provides instant data on component mount
 */

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

class DataCache {
    constructor() {
        this.memory = new Map();
        this.subscribers = new Map();
    }

    // Get data from cache (memory or localStorage)
    get(key) {
        // Check memory first (fastest)
        const memEntry = this.memory.get(key);
        if (memEntry && Date.now() - memEntry.timestamp < CACHE_DURATION) {
            return memEntry.data;
        }

        // Check localStorage
        try {
            const stored = localStorage.getItem(`citadel_cache_${key}`);
            if (stored) {
                const parsed = JSON.parse(stored);
                if (Date.now() - parsed.timestamp < CACHE_DURATION) {
                    // Restore to memory
                    this.memory.set(key, parsed);
                    return parsed.data;
                }
            }
        } catch (e) {
            console.error('[DataCache] Error reading from localStorage:', e);
        }

        return null;
    }

    // Store data in cache
    set(key, data) {
        const entry = {
            data,
            timestamp: Date.now()
        };
        
        // Store in memory
        this.memory.set(key, entry);
        
        // Store in localStorage for persistence
        try {
            localStorage.setItem(`citadel_cache_${key}`, JSON.stringify(entry));
        } catch (e) {
            console.error('[DataCache] Error writing to localStorage:', e);
        }

        // Notify subscribers
        const subs = this.subscribers.get(key) || [];
        subs.forEach(callback => callback(data));
    }

    // Check if data is fresh (within last minute)
    isFresh(key) {
        const entry = this.memory.get(key);
        if (!entry) return false;
        return Date.now() - entry.timestamp < 60000; // 1 minute
    }

    // Get timestamp of last update
    getTimestamp(key) {
        const entry = this.memory.get(key) || 
            JSON.parse(localStorage.getItem(`citadel_cache_${key}`) || '{}');
        return entry?.timestamp || null;
    }

    // Subscribe to changes
    subscribe(key, callback) {
        if (!this.subscribers.has(key)) {
            this.subscribers.set(key, []);
        }
        this.subscribers.get(key).push(callback);
        
        // Return unsubscribe function
        return () => {
            const subs = this.subscribers.get(key) || [];
            const idx = subs.indexOf(callback);
            if (idx > -1) subs.splice(idx, 1);
        };
    }

    // Clear specific key or all cache
    clear(key = null) {
        if (key) {
            this.memory.delete(key);
            localStorage.removeItem(`citadel_cache_${key}`);
        } else {
            this.memory.clear();
            // Clear all citadel_cache keys
            Object.keys(localStorage)
                .filter(k => k.startsWith('citadel_cache_'))
                .forEach(k => localStorage.removeItem(k));
        }
    }

    // Preload data from localStorage to memory
    preload() {
        Object.keys(localStorage)
            .filter(k => k.startsWith('citadel_cache_'))
            .forEach(key => {
                try {
                    const parsed = JSON.parse(localStorage.getItem(key));
                    const shortKey = key.replace('citadel_cache_', '');
                    if (Date.now() - parsed.timestamp < CACHE_DURATION) {
                        this.memory.set(shortKey, parsed);
                    }
                } catch (e) {
                    // Invalid entry, skip
                }
            });
    }
}

// Singleton instance
const dataCache = new DataCache();
dataCache.preload(); // Load from localStorage on startup

export default dataCache;

// Cache keys
export const CACHE_KEYS = {
    DASHBOARD: 'dashboard_overview',
    LGAS: 'lga_data',
    SATELLITE_TRACKED: 'satellite_tracked',
    SATELLITE_ABOVE: 'satellite_above',
    SENTINEL_PASSES: 'sentinel_passes',
    INTEL_REPORTS: 'intel_reports',
    FIRMS_HOTSPOTS: 'firms_hotspots',
    COPERNICUS_PRODUCTS: 'copernicus_products',
};
