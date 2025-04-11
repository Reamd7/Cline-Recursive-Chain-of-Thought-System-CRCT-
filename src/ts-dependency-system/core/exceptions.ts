/**
 * Custom exception classes for the dependency tracking system.
 */

/**
 * Base class for dependency system exceptions.
 */
export class DependencySystemError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'DependencySystemError';
    // This is necessary for proper instanceof checks in TypeScript
    Object.setPrototypeOf(this, DependencySystemError.prototype);
  }
}

/**
 * Exception related to tracker operations.
 */
export class TrackerError extends DependencySystemError {
  constructor(message: string) {
    super(message);
    this.name = 'TrackerError';
    Object.setPrototypeOf(this, TrackerError.prototype);
  }
}

/**
 * Exception related to embedding operations.
 */
export class EmbeddingError extends DependencySystemError {
  constructor(message: string) {
    super(message);
    this.name = 'EmbeddingError';
    Object.setPrototypeOf(this, EmbeddingError.prototype);
  }
}

/**
 * Exception related to analysis operations.
 */
export class AnalysisError extends DependencySystemError {
  constructor(message: string) {
    super(message);
    this.name = 'AnalysisError';
    Object.setPrototypeOf(this, AnalysisError.prototype);
  }
}

/**
 * Exception related to configuration errors.
 */
export class ConfigurationError extends DependencySystemError {
  constructor(message: string) {
    super(message);
    this.name = 'ConfigurationError';
    Object.setPrototypeOf(this, ConfigurationError.prototype);
  }
}

/**
 * Exception related to cache operations.
 */
export class CacheError extends DependencySystemError {
  constructor(message: string) {
    super(message);
    this.name = 'CacheError';
    Object.setPrototypeOf(this, CacheError.prototype);
  }
}

/**
 * Exception related to key generation failures.
 */
export class KeyGenerationError extends DependencySystemError {
  constructor(message: string) {
    super(message);
    this.name = 'KeyGenerationError';
    Object.setPrototypeOf(this, KeyGenerationError.prototype);
  }
}

/**
 * Exception related to grid validation failures.
 */
export class GridValidationError extends DependencySystemError {
  constructor(message: string) {
    super(message);
    this.name = 'GridValidationError';
    Object.setPrototypeOf(this, GridValidationError.prototype);
  }
}