/**
 * Tests for the embedding manager module
 */

import * as fs from 'fs';
import * as path from 'path';
import mockFs from 'mock-fs';
import { 
  generateContentHash,
  loadEmbedding,
  saveEmbedding,
  generateEmbedding,
  compareEmbeddings,
  clearEmbeddingCache,
  batchProcessEmbeddings
} from '../../analysis/embedding-manager';
import { ConfigManager } from '../../utils/config-manager';
import { normalizePath } from '../../utils/path-utils';

describe('Embedding Manager', () => {
  const projectRoot = '/project';
  const testFile = '/project/src/test.ts';
  const testContent = 'const x = 1; console.log(x);';
  const embeddingDir = '/project/src/ts-dependency-system/analysis/embeddings';
  
  // Set up mock file system
  beforeEach(() => {
    mockFs({
      '/project': {
        'package.json': JSON.stringify({
          name: 'test-project'
        }),
        '.clinerules.config.json': JSON.stringify({
          paths: {
            embeddings_dir: 'src/ts-dependency-system/analysis/embeddings'
          }
        }),
        'src': {
          'test.ts': testContent,
          'ts-dependency-system': {
            'analysis': {
              'embeddings': {
                // This will be populated in some tests
              }
            }
          }
        }
      }
    });
    
    // Mock the ConfigManager methods
    jest.spyOn(ConfigManager.prototype, 'get').mockImplementation((key, defaultValue) => {
      if (key === 'paths.embeddings_dir') {
        return 'src/ts-dependency-system/analysis/embeddings';
      }
      if (key === 'models.code_model_name') {
        return 'all-mpnet-base-v2';
      }
      return defaultValue;
    });
    
    // Mock ConfigManager.getInstance to return a singleton instance
    jest.spyOn(ConfigManager, 'getInstance').mockImplementation(() => {
      return new ConfigManager();
    });
  });
  
  // Clean up mock file system
  afterEach(() => {
    mockFs.restore();
    jest.restoreAllMocks();
  });

  // Test content hash generation
  test('generateContentHash should create consistent hashes', () => {
    const hash1 = generateContentHash(testContent);
    const hash2 = generateContentHash(testContent);
    
    expect(hash1).toBe(hash2);
    expect(hash1.length).toBeGreaterThan(0);
  });
  
  // Test embedding generation
  test('generateEmbedding should create an embedding vector', async () => {
    const embedding = await generateEmbedding(testContent, 'js');
    
    expect(Array.isArray(embedding)).toBe(true);
    expect(embedding.length).toBeGreaterThan(0);
    
    // Check if the embedding is normalized
    const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
    expect(magnitude).toBeCloseTo(1, 6);
  });
  
  // Test embedding saving and loading
  test('saveEmbedding and loadEmbedding should work together', async () => {
    const embedding = await generateEmbedding(testContent, 'js');
    
    // Save the embedding
    const saved = await saveEmbedding(testFile, embedding, testContent, projectRoot);
    expect(saved).toBe(true);
    
    // Check if the embedding file was created
    const embeddingPath = path.join(embeddingDir, 'src_test_ts.embedding.json');
    expect(fs.existsSync(embeddingPath)).toBe(true);
    
    // Load the embedding
    const loaded = await loadEmbedding(testFile, projectRoot);
    expect(loaded).not.toBeNull();
    expect(Array.isArray(loaded)).toBe(true);
    expect(loaded!.length).toBe(embedding.length);
    
    // Check if the loaded embedding matches the saved one
    for (let i = 0; i < embedding.length; i++) {
      expect(loaded![i]).toBe(embedding[i]);
    }
  });
  
  // Test embedding comparison
  test('compareEmbeddings should calculate cosine similarity', () => {
    const embedding1 = [0.1, 0.2, 0.3];
    const embedding2 = [0.1, 0.2, 0.3];
    const embedding3 = [-0.1, -0.2, -0.3];
    
    // Same embeddings should have similarity 1
    const similarity1 = compareEmbeddings(embedding1, embedding2);
    expect(similarity1).toBeCloseTo(1, 6);
    
    // Opposite embeddings should have similarity -1
    const similarity2 = compareEmbeddings(embedding1, embedding3);
    expect(similarity2).toBeCloseTo(-1, 6);
    
    // Orthogonal embeddings should have similarity 0
    const similarity3 = compareEmbeddings([1, 0, 0], [0, 1, 0]);
    expect(similarity3).toBeCloseTo(0, 6);
  });
  
  // Test batch processing
  test('batchProcessEmbeddings should process multiple files', async () => {
    const files = [testFile];
    
    const embeddings = await batchProcessEmbeddings(files, projectRoot);
    
    expect(Object.keys(embeddings).length).toBe(1);
    expect(Array.isArray(embeddings[normalizePath(testFile)])).toBe(true);
  });
  
  // Test loading non-existent embedding
  test('loadEmbedding should return null for non-existent embeddings', async () => {
    const loaded = await loadEmbedding('/project/src/non-existent.ts', projectRoot);
    expect(loaded).toBeNull();
  });
  
  // Test clearing the embedding cache
  test('clearEmbeddingCache should clear the cache', async () => {
    const embedding = await generateEmbedding(testContent, 'js');
    await saveEmbedding(testFile, embedding, testContent, projectRoot);
    
    // Load the embedding to cache it
    await loadEmbedding(testFile, projectRoot);
    
    // Clear the cache
    clearEmbeddingCache();
    
    // This is a bit tricky to test directly since we don't have access to the cache
    // But we can at least verify the function runs without errors
    expect(() => clearEmbeddingCache()).not.toThrow();
  });
}); 