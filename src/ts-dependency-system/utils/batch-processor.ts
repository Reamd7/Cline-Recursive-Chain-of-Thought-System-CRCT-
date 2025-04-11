/**
 * Utility module for parallel batch processing.
 * Provides efficient parallel execution of tasks with adaptive batch sizing.
 */

import os from 'os';
import { Worker, isMainThread, parentPort, workerData } from 'worker_threads';
import { promisify } from 'util';
import { performance } from 'perf_hooks';
import { logger } from './logger';

type ProcessorFunc<T, R> = (item: T) => Promise<R>;
type CollectorFunc<R, C> = (results: R[]) => Promise<C>;

interface BatchProcessorOptions {
  maxWorkers?: number;
  batchSize?: number;
  showProgress?: boolean;
}

export class BatchProcessor<T, R> {
  private maxWorkers: number;
  private batchSize?: number;
  private shouldShowProgress: boolean;
  private totalItems: number;
  private processedItems: number;
  private startTime: number;

  constructor(options: BatchProcessorOptions = {}) {
    const cpuCount = os.cpus().length;
    this.maxWorkers = Math.max(1, options.maxWorkers || Math.min(32, cpuCount * 2));
    this.batchSize = options.batchSize;
    this.shouldShowProgress = options.showProgress ?? true;
    this.totalItems = 0;
    this.processedItems = 0;
    this.startTime = 0;
  }

  async processItems(items: T[], processorFunc: ProcessorFunc<T, R>): Promise<R[]> {
    if (typeof processorFunc !== 'function') {
      logger.error('processorFunc must be a function');
      throw new TypeError('processorFunc must be a function');
    }

    this.totalItems = items.length;
    if (!this.totalItems) {
      logger.info('No items to process');
      return [];
    }

    this.processedItems = 0;
    this.startTime = performance.now();

    const results: (R | null)[] = [];
    let itemsProcessedInBatches = 0;

    const batchSize = this.determineBatchSize();
    logger.info(`Processing ${this.totalItems} items with batch size: ${batchSize}, workers: ${this.maxWorkers}`);

    if (this.shouldShowProgress && this.totalItems > 0) {
      process.stdout.write(`Progress: 0/${this.totalItems} (0.0%) | 0.0 items/s | ETA: 0.0s`);
    }

    for (let i = 0; i < items.length; i += batchSize) {
      const batchItems = items.slice(i, i + batchSize);
      const batchResults = await this.processBatch(batchItems, processorFunc);

      for (let j = 0; j < batchItems.length; j++) {
        results.push(batchResults.get(j) ?? null);
      }

      itemsProcessedInBatches += batchItems.length;
      this.processedItems = itemsProcessedInBatches;
      if (this.shouldShowProgress) {
        this.showProgress();
      }
    }

    const finalTime = (performance.now() - this.startTime) / 1000;
    logger.info(`Processed ${this.totalItems} items in ${finalTime.toFixed(2)} seconds`);

    const finalResults = results.filter((res): res is R => res !== null);
    if (finalResults.length !== results.length) {
      logger.warning(`Some items failed processing (${results.length - finalResults.length} errors). Results list contains only successful items.`);
    }

    if (this.shouldShowProgress && this.totalItems > 0) {
      process.stdout.write('\n');
    }

    return finalResults;
  }

  async processWithCollector<C>(
    items: T[],
    processorFunc: ProcessorFunc<T, R>,
    collectorFunc: CollectorFunc<R, C>
  ): Promise<C> {
    const allResults = await this.processItems(items, processorFunc);
    logger.info('Calling collector function with all results...');
    return collectorFunc(allResults);
  }

  private determineBatchSize(): number {
    if (this.batchSize !== undefined) {
      return Math.max(1, this.batchSize);
    }

    if (this.totalItems === 0) return 1;

    const effectiveWorkers = Math.max(1, this.maxWorkers);
    const minSensibleBatch = 4;
    let minBatch: number;

    if (this.totalItems < effectiveWorkers * minSensibleBatch) {
      minBatch = Math.max(1, Math.floor(this.totalItems / effectiveWorkers));
    } else {
      minBatch = minSensibleBatch;
    }

    const targetBatchesPerWorker = 5;
    const denominator = effectiveWorkers * targetBatchesPerWorker;
    const calculatedBatchSize = Math.max(1, Math.floor(this.totalItems / denominator));

    const maxSensibleBatch = 100;
    const maxBatch = Math.min(this.totalItems, maxSensibleBatch);

    const finalBatchSize = Math.min(maxBatch, Math.max(minBatch, calculatedBatchSize));
    const numBatches = Math.ceil(this.totalItems / finalBatchSize);

    logger.debug(
      `Adaptive batch size: Total=${this.totalItems}, Workers=${effectiveWorkers}, ` +
      `TargetBatches/Worker=${targetBatchesPerWorker} => Calculated=${calculatedBatchSize}, ` +
      `Min=${minBatch}, Max=${maxBatch} -> Final=${finalBatchSize}, Batches=${numBatches}`
    );

    return finalBatchSize;
  }

  private async processBatch(
    batch: T[],
    processorFunc: ProcessorFunc<T, R>
  ): Promise<Map<number, R>> {
    if (!batch.length) {
      return new Map();
    }

    const batchResultsMap = new Map<number, R>();
    const workers = Math.min(this.maxWorkers, batch.length);
    const itemsPerWorker = Math.ceil(batch.length / workers);

    const workerPromises = batch.map((item, index) => {
      return new Promise<[number, R | null]>((resolve) => {
        try {
          processorFunc(item)
            .then(result => resolve([index, result]))
            .catch(error => {
              logger.error(`Error processing item (batch index ${index}): ${error}`);
              resolve([index, null]);
            });
        } catch (error) {
          logger.error(`Error processing item (batch index ${index}): ${error}`);
          resolve([index, null]);
        }
      });
    });

    const results = await Promise.all(workerPromises);
    for (const [index, result] of results) {
      if (result !== null) {
        batchResultsMap.set(index, result);
      }
    }

    return batchResultsMap;
  }

  private showProgress(): void {
    const elapsedTime = (performance.now() - this.startTime) / 1000;
    if (elapsedTime < 0.01) return;

    const itemsPerSecond = this.processedItems / elapsedTime;
    const percentComplete = (this.processedItems / Math.max(1, this.totalItems)) * 100;
    const remainingItems = this.totalItems - this.processedItems;
    const etaSeconds = itemsPerSecond > 0 ? remainingItems / itemsPerSecond : 0;

    let etaStr: string;
    if (etaSeconds > 3600) {
      etaStr = `${(etaSeconds / 3600).toFixed(1)}h`;
    } else if (etaSeconds > 60) {
      etaStr = `${(etaSeconds / 60).toFixed(1)}m`;
    } else {
      etaStr = `${etaSeconds.toFixed(1)}s`;
    }

    const progressStr = `${this.processedItems.toString().padStart(this.totalItems.toString().length)}/${this.totalItems}`;

    process.stdout.write(
      `\x1b[2K\rProgress: ${progressStr} (${percentComplete.toFixed(1).padStart(6)}%) | ` +
      `${itemsPerSecond.toFixed(1).padStart(6)} items/s | ` +
      `ETA: ${etaStr.padEnd(6)}`
    );
  }
}

// Convenience functions
export async function processItems<T, R>(
  items: T[],
  processorFunc: ProcessorFunc<T, R>,
  options: BatchProcessorOptions = {}
): Promise<R[]> {
  const processor = new BatchProcessor<T, R>(options);
  return processor.processItems(items, processorFunc);
}

export async function processWithCollector<T, R, C>(
  items: T[],
  processorFunc: ProcessorFunc<T, R>,
  collectorFunc: CollectorFunc<R, C>,
  options: BatchProcessorOptions = {}
): Promise<C> {
  const processor = new BatchProcessor<T, R>(options);
  return processor.processWithCollector(items, processorFunc, collectorFunc);
} 