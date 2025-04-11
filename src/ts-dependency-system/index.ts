/**
 * TypeScript Dependency System
 * 
 * This is the main entry point for the TypeScript implementation of the dependency processing system.
 * It exports all public APIs from the core, utils, io, and analysis modules.
 */

// Export from core module
export * from './core';

// Export from utils module
export * from './utils';

// Export from io module
export * from './io';

// Export from analysis module
export * from './analysis';

// Simple hello world function for initial testing
export function helloWorld(): string {
  return 'Hello, World! TypeScript Dependency System is initialized.';
}

// Log a message when the module is imported
console.log(helloWorld());