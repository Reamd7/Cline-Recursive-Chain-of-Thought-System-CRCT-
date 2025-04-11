import { CacheManager, cached } from '../../utils/cache-manager';
import { logger } from '../../utils/logger';

jest.mock('../../utils/logger', () => ({
  logger: {
    debug: jest.fn(),
    info: jest.fn(),
    warning: jest.fn(),
    error: jest.fn()
  }
}));

describe('Cache Manager', () => {
  let cacheManager: CacheManager;

  beforeEach(() => {
    cacheManager = CacheManager.getInstance();
    cacheManager.clearAll();
  });

  afterEach(() => {
    cacheManager.clearAll();
  });

  describe('Singleton Pattern', () => {
    it('should return the same instance', () => {
      const instance1 = CacheManager.getInstance();
      const instance2 = CacheManager.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('Cache Operations', () => {
    it('should set and get cache values', () => {
      const cache = cacheManager.getCache('test-cache');
      cache.set('key1', 'value1');
      expect(cache.get('key1')).toBe('value1');
    });

    it('should handle cache misses', () => {
      const cache = cacheManager.getCache('test-cache');
      expect(cache.get('nonexistent')).toBeNull();
    });

    it('should respect TTL', async () => {
      const cache = cacheManager.getCache('test-cache', 1); // 1 second TTL
      cache.set('key1', 'value1');
      expect(cache.get('key1')).toBe('value1');
      
      await new Promise(resolve => setTimeout(resolve, 1100)); // Wait for TTL to expire
      expect(cache.get('key1')).toBeNull();
    });

    it('should handle cache dependencies', () => {
      const cache = cacheManager.getCache('test-cache');
      cache.set('key1', 'value1', ['dep1']);
      cache.set('key2', 'value2', ['dep1']);
      
      cache.invalidate('dep1');
      expect(cache.get('key1')).toBeNull();
      expect(cache.get('key2')).toBeNull();
    });
  });

  describe('Cache Decorator', () => {
    it('should cache function results', () => {
      let callCount = 0;
      
      @cached('test-cache')
      function testFunction(arg: string): string {
        callCount++;
        return `result-${arg}`;
      }

      const result1 = testFunction('test');
      const result2 = testFunction('test');
      
      expect(result1).toBe('result-test');
      expect(result2).toBe('result-test');
      expect(callCount).toBe(1);
    });

    it('should handle async functions', async () => {
      let callCount = 0;
      
      @cached('test-cache')
      async function asyncFunction(arg: string): Promise<string> {
        callCount++;
        return `result-${arg}`;
      }

      const result1 = await asyncFunction('test');
      const result2 = await asyncFunction('test');
      
      expect(result1).toBe('result-test');
      expect(result2).toBe('result-test');
      expect(callCount).toBe(1);
    });

    it('should handle cache misses with dependencies', () => {
      const cache = cacheManager.getCache('test-cache');
      
      @cached('test-cache', (arg: string) => `key-${arg}`)
      function testFunction(arg: string): [string, string[]] {
        return [`result-${arg}`, [`dep-${arg}`]];
      }

      const [result1] = testFunction('test');
      expect(result1).toBe('result-test');
      expect(cache.get('key-test')).toBe('result-test');
      
      cache.invalidate('dep-test');
      const [result2] = testFunction('test');
      expect(result2).toBe('result-test');
    });
  });

  describe('Error Handling', () => {
    it('should handle cache errors gracefully', () => {
      const cache = cacheManager.getCache('test-cache');
      cache.set('key1', 'value1');
      
      // Simulate cache corruption
      (cache as any).data = null;
      
      expect(() => cache.get('key1')).not.toThrow();
      expect(logger.error).toHaveBeenCalled();
    });
  });
}); 