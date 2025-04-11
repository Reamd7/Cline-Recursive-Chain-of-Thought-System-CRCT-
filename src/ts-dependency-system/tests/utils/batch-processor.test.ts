import { BatchProcessor, processItems, processWithCollector } from '../../utils/batch-processor';
import { logger } from '../../utils/logger';

jest.mock('../../utils/logger', () => ({
  logger: {
    debug: jest.fn(),
    info: jest.fn(),
    warning: jest.fn(),
    error: jest.fn()
  }
}));

describe('Batch Processor', () => {
  describe('BatchProcessor Class', () => {
    let processor: BatchProcessor<number, number>;

    beforeEach(() => {
      processor = new BatchProcessor<number, number>({ showProgress: false });
    });

    it('should process items in batches', async () => {
      const items = [1, 2, 3, 4, 5];
      const results = await processor.processItems(items, async (item: number) => item * 2);
      expect(results).toEqual([2, 4, 6, 8, 10]);
    });

    it('should handle empty input', async () => {
      const results = await processor.processItems([], async (item: number) => item * 2);
      expect(results).toEqual([]);
    });

    it('should handle errors gracefully', async () => {
      const items = [1, 2, 3];
      const results = await processor.processItems(items, async (item: number) => {
        if (item === 2) throw new Error('Test error');
        return item * 2;
      });
      expect(results).toEqual([2, 6]);
      expect(logger.error).toHaveBeenCalled();
    });

    it('should respect maxWorkers option', async () => {
      const processor = new BatchProcessor<number, number>({ maxWorkers: 2, showProgress: false });
      const items = [1, 2, 3, 4, 5];
      const results = await processor.processItems(items, async (item: number) => item * 2);
      expect(results).toEqual([2, 4, 6, 8, 10]);
    });

    it('should respect batchSize option', async () => {
      const processor = new BatchProcessor<number, number>({ batchSize: 2, showProgress: false });
      const items = [1, 2, 3, 4, 5];
      const results = await processor.processItems(items, async (item: number) => item * 2);
      expect(results).toEqual([2, 4, 6, 8, 10]);
    });
  });

  describe('processItems Function', () => {
    it('should process items using convenience function', async () => {
      const items = [1, 2, 3];
      const results = await processItems<number, number>(items, async (item: number) => item * 2);
      expect(results).toEqual([2, 4, 6]);
    });

    it('should respect options', async () => {
      const items = [1, 2, 3];
      const results = await processItems<number, number>(items, async (item: number) => item * 2, {
        maxWorkers: 2,
        batchSize: 1,
        showProgress: false
      });
      expect(results).toEqual([2, 4, 6]);
    });
  });

  describe('processWithCollector Function', () => {
    it('should process items and collect results', async () => {
      const items = [1, 2, 3];
      const result = await processWithCollector<number, number, number>(
        items,
        async (item: number) => item * 2,
        async (results) => results.reduce((a, b) => a + b, 0)
      );
      expect(result).toBe(12); // 2 + 4 + 6
    });

    it('should handle collector errors', async () => {
      const items = [1, 2, 3];
      await expect(
        processWithCollector<number, number, number>(
          items,
          async (item: number) => item * 2,
          async () => {
            throw new Error('Collector error');
          }
        )
      ).rejects.toThrow('Collector error');
    });
  });

  describe('Progress Display', () => {
    it('should show progress when enabled', async () => {
      const processor = new BatchProcessor<number, number>({ showProgress: true });
      const items = [1, 2, 3];
      
      // Mock process.stdout.write to capture output
      const originalWrite = process.stdout.write;
      const writeCalls: string[] = [];
      process.stdout.write = (str: string) => {
        writeCalls.push(str);
        return true;
      };

      await processor.processItems(items, async (item: number) => item * 2);
      
      // Restore original write
      process.stdout.write = originalWrite;

      expect(writeCalls.length).toBeGreaterThan(0);
      expect(writeCalls[0]).toContain('Progress:');
    });

    it('should not show progress when disabled', async () => {
      const processor = new BatchProcessor<number, number>({ showProgress: false });
      const items = [1, 2, 3];
      
      // Mock process.stdout.write to capture output
      const originalWrite = process.stdout.write;
      const writeCalls: string[] = [];
      process.stdout.write = (str: string) => {
        writeCalls.push(str);
        return true;
      };

      await processor.processItems(items, async (item: number) => item * 2);
      
      // Restore original write
      process.stdout.write = originalWrite;

      expect(writeCalls.length).toBe(0);
    });
  });
}); 