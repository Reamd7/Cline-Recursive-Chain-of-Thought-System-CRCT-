/**
 * Analysis Module
 * 
 * This module provides analysis functionality for the dependency processing system,
 * including dependency analysis, dependency suggestion, embedding management, and project analysis.
 */

// Export from dependency-analyzer.ts
export {
  FileType,
  AnalysisResult,
  analyzeFile
} from './dependency-analyzer';

// Export from dependency-suggester.ts
export {
  DependencyType,
  DependencyDirection,
  DependencySuggestion,
  suggestDependencies,
  sortSuggestionsByConfidence,
  aggregateSuggestions
} from './dependency-suggester';

// Export from embedding-manager.ts
export {
  EmbeddingMetadata,
  generateContentHash,
  loadEmbedding,
  saveEmbedding,
  generateEmbedding,
  compareEmbeddings,
  clearEmbeddingCache,
  batchProcessEmbeddings
} from './embedding-manager';

// Export from project-analyzer.ts
export {
  ProjectAnalysisOptions,
  analyzeProject
} from './project-analyzer';