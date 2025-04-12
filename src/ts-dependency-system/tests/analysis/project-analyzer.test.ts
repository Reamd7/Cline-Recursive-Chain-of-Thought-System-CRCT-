/**
 * Tests for the project analyzer module
 */

import * as fs from 'fs';
import * as path from 'path';
import * as mockFs from 'mock-fs';
import { analyzeProject, ProjectAnalysisOptions } from '../../analysis/project-analyzer';
import { ConfigManager } from '../../utils/config-manager';
import { normalizePath } from '../../utils/path-utils';

// Mock dependencies
jest.mock('../../analysis/dependency-analyzer', () => ({
  analyzeFile: jest.fn().mockResolvedValue({
    imports: ['/project/src/utils.ts'],
    functionCalls: ['utils'],
    semanticDependencies: [],
    documentationReferences: []
  })
}));

jest.mock('../../analysis/embedding-manager', () => ({
  batchProcessEmbeddings: jest.fn().mockResolvedValue({
    '/project/src/index.ts': [0.1, 0.2, 0.3],
    '/project/src/utils.ts': [0.15, 0.25, 0.35]
  }),
  generateContentHash: jest.fn().mockReturnValue('hash123')
}));

jest.mock('../../analysis/dependency-suggester', () => ({
  suggestDependencies: jest.fn().mockResolvedValue([
    {
      sourcePath: '/project/src/index.ts',
      targetPath: '/project/src/utils.ts',
      direction: '<',
      confidence: 1.0,
      type: 'direct',
      reason: 'Direct import detected'
    }
  ]),
  aggregateSuggestions: jest.fn().mockImplementation(arr => arr),
  sortSuggestionsByConfidence: jest.fn().mockImplementation(arr => arr),
  DependencyDirection: {
    SOURCE_TO_TARGET: '<',
    TARGET_TO_SOURCE: '>',
    BIDIRECTIONAL: 'x',
    DOCUMENT: 'd',
    SEMANTIC: 's',
    NONE: 'n'
  }
}));

jest.mock('../../io/update-main-tracker', () => ({
  updateMainTracker: jest.fn().mockResolvedValue(true)
}));

jest.mock('../../io/update-doc-tracker', () => ({
  updateDocTracker: jest.fn().mockResolvedValue(true)
}));

jest.mock('../../io/update-mini-tracker', () => ({
  updateMiniTracker: jest.fn().mockResolvedValue(true)
}));

jest.mock('../../core/key-manager', () => ({
  generateKeys: jest.fn().mockResolvedValue(true),
  getKeyFromPath: jest.fn().mockReturnValue('1Aa1')
}));

describe('Project Analyzer', () => {
  // Set up mock file system
  beforeEach(() => {
    mockFs({
      '/project': {
        'package.json': JSON.stringify({
          name: 'test-project'
        }),
        '.clinerules.config.json': JSON.stringify({
          exclude: {
            paths: ['node_modules', 'dist']
          }
        }),
        'src': {
          'index.ts': 'import { format } from "./utils";',
          'utils.ts': 'export function format(str: string): string { return str.toUpperCase(); }'
        },
        'docs': {
          'readme.md': '# Project Documentation'
        },
        'node_modules': {
          'some-package': {
            'index.js': 'console.log("This should be excluded");'
          }
        }
      }
    });
    
    // Mock ConfigManager
    jest.spyOn(ConfigManager, 'getInstance').mockImplementation(() => {
      const instance = {
        get: jest.fn().mockImplementation((key, defaultValue) => {
          if (key === 'excluded_extensions') {
            return ['.jpg', '.png'];
          }
          return defaultValue;
        }),
        getExcludedPaths: jest.fn().mockReturnValue(['node_modules', 'dist']),
        getDocDirectories: jest.fn().mockReturnValue(['docs'])
      };
      return instance as unknown as ConfigManager;
    });
  });
  
  // Clean up
  afterEach(() => {
    mockFs.restore();
    jest.clearAllMocks();
  });

  test('analyzeProject should analyze all files in a project', async () => {
    const options: ProjectAnalysisOptions = {
      projectRoot: '/project',
      verbose: true
    };
    
    const result = await analyzeProject(options);
    
    // Should find both src files but not the node_modules file
    expect(result.files.length).toBe(3); // index.ts, utils.ts, and readme.md
    expect(result.files.some(f => f.includes('node_modules'))).toBe(false);
    
    // Should have analysis results for each file
    expect(Object.keys(result.fileAnalyses).length).toBe(3);
    
    // Should have suggestions
    expect(result.suggestions).toBeDefined();
    expect(Array.isArray(result.suggestions)).toBe(true);
  });
  
  test('analyzeProject should handle excluded paths', async () => {
    const options: ProjectAnalysisOptions = {
      projectRoot: '/project',
      excludedPaths: ['docs'], // Exclude docs directory
      verbose: false
    };
    
    const result = await analyzeProject(options);
    
    // Should not include docs files
    expect(result.files.every(f => !f.includes('/docs/'))).toBe(true);
  });
  
  test('analyzeProject should use default options when not provided', async () => {
    const options: ProjectAnalysisOptions = {
      projectRoot: '/project'
    };
    
    const result = await analyzeProject(options);
    
    // Should still work with minimal options
    expect(result.files.length).toBeGreaterThan(0);
    expect(result.fileAnalyses).toBeDefined();
    expect(result.suggestions).toBeDefined();
  });
  
  test('analyzeProject should throw for invalid project root', async () => {
    const options: ProjectAnalysisOptions = {
      projectRoot: '/non-existent'
    };
    
    await expect(analyzeProject(options)).rejects.toThrow();
  });
}); 