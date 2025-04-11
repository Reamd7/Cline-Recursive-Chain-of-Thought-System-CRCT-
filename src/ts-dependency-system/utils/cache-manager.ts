/**
 * Cache management module with dynamic, TTL-based caching for dependency tracking system.
 * Supports on-demand cache creation, automatic expiration, and granular invalidation.
 */

interface CacheEntry<T> {
    value: T;
    accessTime: number;
    expiryTime: number | null;
}

interface CacheDependencies {
    [key: string]: string[]; // key -> dependent keys
}

interface CacheStats {
    hits: number;
    misses: number;
    size: number;
}

class Cache<T> {
    private data: Map<string, CacheEntry<T>>;
    private dependencies: CacheDependencies;
    private reverseDeps: CacheDependencies;
    private creationTime: number;
    private hits: number;
    private misses: number;

    constructor(
        private name: string,
        private ttl: number = 600, // 10 minutes in seconds
        private maxSize: number = 1000
    ) {
        this.data = new Map();
        this.dependencies = {};
        this.reverseDeps = {};
        this.creationTime = Date.now();
        this.hits = 0;
        this.misses = 0;
    }

    get(key: string): T | null {
        const entry = this.data.get(key);
        if (entry) {
            if (entry.expiryTime === null || Date.now() < entry.expiryTime) {
                entry.accessTime = Date.now();
                this.hits++;
                return entry.value;
            } else {
                this.removeKey(key);
            }
        }
        this.misses++;
        return null;
    }

    set(
        key: string,
        value: T,
        dependencies: string[] = [],
        ttl: number | null = null
    ): void {
        if (this.data.size >= this.maxSize) {
            this.evictLRU();
        }

        const expiryTime = ttl !== null
            ? Date.now() + ttl * 1000
            : this.ttl !== null
                ? Date.now() + this.ttl * 1000
                : null;

        this.data.set(key, {
            value,
            accessTime: Date.now(),
            expiryTime
        });

        if (dependencies.length > 0) {
            this.dependencies[key] = dependencies;
            for (const dep of dependencies) {
                if (!this.reverseDeps[dep]) {
                    this.reverseDeps[dep] = [];
                }
                this.reverseDeps[dep].push(key);
            }
        }
    }

    private evictLRU(): void {
        if (this.data.size === 0) return;
        let lruKey = '';
        let minAccessTime = Infinity;

        for (const [key, entry] of this.data.entries()) {
            if (entry.accessTime < minAccessTime) {
                minAccessTime = entry.accessTime;
                lruKey = key;
            }
        }

        if (lruKey) {
            this.removeKey(lruKey);
        }
    }

    private removeKey(key: string): void {
        this.data.delete(key);

        if (this.dependencies[key]) {
            for (const dep of this.dependencies[key]) {
                if (this.reverseDeps[dep]) {
                    const index = this.reverseDeps[dep].indexOf(key);
                    if (index !== -1) {
                        this.reverseDeps[dep].splice(index, 1);
                    }
                    if (this.reverseDeps[dep].length === 0) {
                        delete this.reverseDeps[dep];
                    }
                }
            }
            delete this.dependencies[key];
        }
    }

    cleanupExpired(): void {
        const now = Date.now();
        for (const [key, entry] of this.data.entries()) {
            if (entry.expiryTime !== null && now > entry.expiryTime) {
                this.removeKey(key);
            }
        }
    }

    isExpired(): boolean {
        return (Date.now() - this.creationTime) > this.ttl * 1000 && this.data.size === 0;
    }

    invalidate(keyPattern: string): void {
        const pattern = new RegExp(keyPattern);
        for (const key of this.data.keys()) {
            if (pattern.test(key)) {
                this.removeKey(key);
            }
        }
    }

    stats(): CacheStats {
        return {
            hits: this.hits,
            misses: this.misses,
            size: this.data.size
        };
    }
}

export class CacheManager {
    private caches: Map<string, Cache<any>>;

    constructor(private persist: boolean = false) {
        this.caches = new Map();
    }

    getCache<T>(cacheName: string, ttl: number = 600): Cache<T> {
        let cache = this.caches.get(cacheName);
        if (!cache || cache.isExpired()) {
            cache = new Cache<T>(cacheName, ttl);
            this.caches.set(cacheName, cache);
        }
        return cache;
    }

    cleanup(): void {
        for (const [name, cache] of this.caches.entries()) {
            if (cache.isExpired()) {
                this.caches.delete(name);
            } else {
                cache.cleanupExpired();
            }
        }
    }

    clearAll(): void {
        this.caches.clear();
    }
}

export const cacheManager = new CacheManager(false);

export function getTrackerCacheKey(trackerPath: string, trackerType: string): string {
    return `tracker:${trackerPath}:${trackerType}`;
}

export function clearAllCaches(): void {
    cacheManager.clearAll();
}

export function invalidateDependentEntries(cacheName: string, key: string): void {
    const cache = cacheManager.getCache(cacheName);
    cache.invalidate(key);
}

export function fileModified(
    filePath: string,
    projectRoot: string,
    cacheType: string = 'all'
): void {
    const key = cacheType === 'all'
        ? `.*:${filePath}:.*`
        : `${cacheType}:${filePath}:.*`;
    
    for (const cache of cacheManager['caches'].values()) {
        cache.invalidate(key);
    }
}

export function trackerModified(
    trackerPath: string,
    trackerType: string,
    projectRoot: string,
    cacheType: string = 'all'
): void {
    const key = cacheType === 'all'
        ? getTrackerCacheKey(trackerPath, trackerType)
        : `${cacheType}:${trackerPath}:.*`;
    
    invalidateDependentEntries('tracker', key);
}

export function cached<T>(
    cacheName: string,
    keyFunc?: (...args: any[]) => string,
    ttl?: number
) {
    return function (
        target: any,
        propertyKey: string,
        descriptor: PropertyDescriptor
    ) {
        const originalMethod = descriptor.value;
        
        descriptor.value = function (...args: any[]) {
            const key = keyFunc ? keyFunc(...args) : `${propertyKey}:${JSON.stringify(args)}`;
            const cache = cacheManager.getCache<T>(cacheName, ttl);
            
            const cachedValue = cache.get(key);
            if (cachedValue !== null) {
                return cachedValue;
            }
            
            const result = originalMethod.apply(this, args);
            let value: T;
            let dependencies: string[] = [];
            
            if (Array.isArray(result) && result.length === 2 && Array.isArray(result[1])) {
                [value, dependencies] = result;
            } else {
                value = result;
                if (['loadEmbedding', 'loadMetadata', 'analyzeFile', 'analyzeProject', 'getFileType'].includes(propertyKey)) {
                    if (args.length > 0 && typeof args[0] === 'string') {
                        dependencies.push(`file:${args[0]}`);
                    }
                }
            }
            
            cache.set(key, value, dependencies, ttl);
            cacheManager.cleanup();
            return value;
        };
        
        return descriptor;
    };
} 