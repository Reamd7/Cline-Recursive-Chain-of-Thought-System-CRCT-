/**
 * Embedding Manager
 * 
 * Handles the generation, storage, loading, and comparison of text embeddings
 * for file content similarity analysis.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';
import { ConfigManager } from '../utils/config-manager';
import { normalizePath, joinPaths, getFileType } from '../utils/path-utils';
import { DependencySystemError, EmbeddingError } from '../core/exceptions';
import { cached } from '../utils/cache-manager';

import * as logging from '../utils/logging';
const logger = logging.getLogger('embedding-manager');

// Interface for embedding metadata
export interface EmbeddingMetadata {
  filePath: string;
  fileHash: string;
  timestamp: number;
  dimensions: number;
  model: string;
}

/**
 * Generates a hash for a file's content
 * @param content File content
 * @returns SHA-256 hash of the content
 */
export function generateContentHash(content: string): string {
  return crypto.createHash('sha256').update(content).digest('hex');
}

/**
 * Loads embeddings for a file if they exist
 * @param filePath Path to the file
 * @param projectRoot Root directory of the project
 * @returns Embedding vector or null if not available
 */
export async function loadEmbedding(filePath: string, projectRoot: string): Promise<number[] | null> {
  const normalizedPath = normalizePath(filePath);
  
  try {
    // Get embedding file path
    const embeddingPath = getEmbeddingPath(normalizedPath, projectRoot);
    if (!fs.existsSync(embeddingPath)) {
      return null;
    }
    
    // Read embedding file
    const embeddingContent = fs.readFileSync(embeddingPath, 'utf8');
    const embeddingData = JSON.parse(embeddingContent);
    
    // Validate embedding metadata
    if (!validateEmbedding(embeddingData, normalizedPath)) {
      return null;
    }
    
    return embeddingData.embedding;
  } catch (error: any) {
    logger.warn(`Error loading embedding for ${filePath}: ${error.message}`);
    return null;
  }
}

/**
 * Saves an embedding for a file
 * @param filePath Path to the file
 * @param embedding Embedding vector
 * @param fileContent File content (for hashing)
 * @param projectRoot Root directory of the project
 * @returns True if successful, false otherwise
 */
export async function saveEmbedding(
  filePath: string,
  embedding: number[],
  fileContent: string,
  projectRoot: string
): Promise<boolean> {
  const normalizedPath = normalizePath(filePath);
  
  try {
    // Get embedding file path
    const embeddingPath = getEmbeddingPath(normalizedPath, projectRoot);
    const embeddingDir = path.dirname(embeddingPath);
    
    // Create directory if it doesn't exist
    if (!fs.existsSync(embeddingDir)) {
      fs.mkdirSync(embeddingDir, { recursive: true });
    }
    
    // Create embedding metadata
    const configManager = ConfigManager.getInstance();
    const modelName = configManager.get<string>('models.code_model_name', 'all-mpnet-base-v2');
    
    const metadata: EmbeddingMetadata = {
      filePath: normalizedPath,
      fileHash: generateContentHash(fileContent),
      timestamp: Date.now(),
      dimensions: embedding.length,
      model: modelName
    };
    
    // Save embedding to file
    fs.writeFileSync(embeddingPath, JSON.stringify({
      metadata,
      embedding
    }, null, 2));
    
    return true;
  } catch (error: any) {
    logger.error(`Error saving embedding for ${filePath}: ${error.message}`);
    return false;
  }
}

/**
 * Generates an embedding for a file's content
 * In Python version, this would use a machine learning model.
 * For TypeScript version, we create a placeholder embedding based on content hash.
 * 
 * @param content File content
 * @param fileType Type of the file
 * @returns Embedding vector with 384 dimensions (matching Python version)
 */
export async function generateEmbedding(content: string, fileType: string): Promise<number[]> {
  try {
    // This is a placeholder implementation that matches Python's dimensions
    const hash = generateContentHash(content);
    const dimensions = 384; // Match Python's embedding size exactly
    
    // Generate a pseudo-embedding from the hash
    // This is just for demonstration and testing purposes
    const embedding: number[] = [];
    for (let i = 0; i < dimensions; i++) {
      // Use parts of the hash to seed the embedding values
      const hashPart = parseInt(hash.substring(i % hash.length, (i % hash.length) + 2), 16);
      embedding.push((hashPart / 255) * 2 - 1); // Scale to range [-1, 1]
    }
    
    // Normalize the embedding
    const norm = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
    return embedding.map(val => val / norm);
  } catch (error: any) {
    throw new EmbeddingError(`Error generating embedding: ${error.message}`);
  }
}

/**
 * Compares two embeddings using cosine similarity
 * @param embedding1 First embedding vector
 * @param embedding2 Second embedding vector
 * @returns Similarity score (0-1)
 */
export function compareEmbeddings(embedding1: number[], embedding2: number[]): number {
  if (embedding1.length !== embedding2.length) {
    throw new EmbeddingError('Embeddings must have the same dimensions');
  }
  
  let dotProduct = 0;
  let norm1 = 0;
  let norm2 = 0;
  
  for (let i = 0; i < embedding1.length; i++) {
    dotProduct += embedding1[i] * embedding2[i];
    norm1 += embedding1[i] * embedding1[i];
    norm2 += embedding2[i] * embedding2[i];
  }
  
  norm1 = Math.sqrt(norm1);
  norm2 = Math.sqrt(norm2);
  
  if (norm1 === 0 || norm2 === 0) {
    return 0;
  }
  
  return dotProduct / (norm1 * norm2);
}

/**
 * Validates an embedding based on its metadata
 * @param embeddingData Embedding data with metadata
 * @param filePath Path to the file
 * @returns True if valid, false otherwise
 */
function validateEmbedding(embeddingData: any, filePath: string): boolean {
  // Check if the embedding data has the required fields
  if (!embeddingData || !embeddingData.metadata || !embeddingData.embedding) {
    return false;
  }
  
  const metadata = embeddingData.metadata;
  
  // Check if the embedding is for the correct file
  if (metadata.filePath !== filePath) {
    return false;
  }
  
  // Check if the file has been modified since the embedding was generated
  if (!fs.existsSync(filePath)) {
    return false;
  }
  
  const fileContent = fs.readFileSync(filePath, 'utf8');
  const currentHash = generateContentHash(fileContent);
  
  if (metadata.fileHash !== currentHash) {
    return false;
  }
  
  return true;
}

/**
 * Gets the path to store the embedding for a file
 * Matches Python version's embedding path logic
 * 
 * @param filePath Path to the file
 * @param projectRoot Root directory of the project
 * @returns Path to the embedding file
 */
function getEmbeddingPath(filePath: string, projectRoot: string): string {
  const configManager = ConfigManager.getInstance();
  const embeddingsDir = configManager.get<string>(
    'paths.embeddings_dir', 
    'cline_utils/dependency_system/analysis/embeddings'
  );
  
  // Create a unique path based on the file path
  const relativePath = path.relative(projectRoot, filePath);
  const safePath = relativePath.replace(/[^a-zA-Z0-9-_]/g, '_');
  const embeddingFilename = `${safePath}.json`;
  
  return path.join(projectRoot, embeddingsDir, embeddingFilename);
}

/**
 * Clears the embedding cache
 */
export function clearEmbeddingCache(): void {
  // In Python version, this would clear a cache
  // For TypeScript, we just log as we're not using an in-memory cache
  logger.info('Embedding cache cleared');
}

/**
 * Batch processes embeddings for multiple files
 * @param filePaths Array of file paths
 * @param projectRoot Root directory of the project
 * @param force Whether to force regeneration of embeddings
 * @returns Dictionary mapping file paths to embeddings
 */
export async function batchProcessEmbeddings(
  filePaths: string[],
  projectRoot: string,
  force: boolean = false
): Promise<{ [key: string]: number[] }> {
  logger.info(`Processing embeddings for ${filePaths.length} files`);
  
  const embeddings: { [key: string]: number[] } = {};
  const batchSize = 100; // Process files in batches
  
  for (let i = 0; i < filePaths.length; i += batchSize) {
    const batch = filePaths.slice(i, i + batchSize);
    logger.info(`Processing batch ${Math.floor(i / batchSize) + 1} of ${Math.ceil(filePaths.length / batchSize)}`);
    
    // Process files in parallel
    const promises = batch.map(async (filePath) => {
      try {
        const normalizedPath = normalizePath(filePath);
        
        // Skip if not a file
        if (!fs.existsSync(normalizedPath) || !fs.statSync(normalizedPath).isFile()) {
          return;
        }
        
        // Check if embedding already exists
        let embedding = await loadEmbedding(normalizedPath, projectRoot);
        
        // Generate new embedding if needed
        if (embedding === null || force) {
          const fileContent = fs.readFileSync(normalizedPath, 'utf8');
          const fileType = getFileType(normalizedPath);
          
          embedding = await generateEmbedding(fileContent, fileType);
          await saveEmbedding(normalizedPath, embedding, fileContent, projectRoot);
        }
        
        embeddings[normalizedPath] = embedding;
      } catch (error: any) {
        logger.error(`Error processing embedding for ${filePath}: ${error.message}`);
      }
    });
    
    await Promise.all(promises);
  }
  
  logger.info(`Processed embeddings for ${Object.keys(embeddings).length} files`);
  return embeddings;
} 