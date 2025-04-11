/**
 * Core Module
 *
 * This module provides the core functionality for the dependency processing system,
 * including dependency grid operations, key management, and exception handling.
 */

// Export all exception classes
export * from './exceptions';

// Export all key management functions and interfaces
export * from './key-manager';

// Export all dependency grid functions and interfaces
export * from './dependency-grid';

// This indicates that the core module has been initialized
export const coreModuleInitialized = true;