/**
 * Tests for the dependency analyzer module
 */

import * as fs from 'fs';
import * as path from 'path';
import * as mockFs from 'mock-fs';
import { FileType, analyzeFile, AnalysisResult } from '../../analysis/dependency-analyzer';
import { normalizePath } from '../../utils/path-utils';

describe('Dependency Analyzer', () => {
  // Set up mock file system
  beforeEach(() => {
    mockFs({
      '/project': {
        'package.json': JSON.stringify({
          name: 'test-project',
          dependencies: {
            'lodash': '^4.17.21'
          }
        }),
        'src': {
          'index.ts': `
            import { add } from './math';
            import * as utils from './utils';
            
            console.log(add(1, 2));
            utils.format('hello');
          `,
          'math.ts': `
            export function add(a: number, b: number): number {
              return a + b;
            }
            
            export function subtract(a: number, b: number): number {
              return a - b;
            }
          `,
          'utils.ts': `
            import { add } from './math';
            
            export function format(str: string): string {
              return str.toUpperCase();
            }
            
            export function calculate(a: number, b: number): number {
              return add(a, b);
            }
          `
        },
        'docs': {
          'readme.md': `
            # Test Project
            
            This is a test project.
            
            ## API
            
            - [Math](./api/math.md)
            - [Utils](./api/utils.md)
          `,
          'api': {
            'math.md': `
              # Math API
              
              \`\`\`typescript
              import { add } from './math';
              \`\`\`
              
              ## Functions
              
              ### add(a, b)
              
              Adds two numbers.
            `,
            'utils.md': `
              # Utils API
              
              \`\`\`typescript
              import { format } from './utils';
              \`\`\`
              
              ## Functions
              
              ### format(str)
              
              Formats a string.
            `
          }
        }
      }
    });
  });
  
  // Clean up mock file system
  afterEach(() => {
    mockFs.restore();
  });

  test('analyzeFile should detect imports in TypeScript files', async () => {
    const result = await analyzeFile('/project/src/index.ts', '/project');
    
    expect(result.imports).toContain(normalizePath('/project/src/math.ts'));
    expect(result.imports).toContain(normalizePath('/project/src/utils.ts'));
  });

  test('analyzeFile should detect function calls in TypeScript files', async () => {
    const result = await analyzeFile('/project/src/index.ts', '/project');
    
    expect(result.functionCalls).toContain('utils');
  });

  test('analyzeFile should detect imports in nested files', async () => {
    const result = await analyzeFile('/project/src/utils.ts', '/project');
    
    expect(result.imports).toContain(normalizePath('/project/src/math.ts'));
  });

  test('analyzeFile should detect documentation references in Markdown files', async () => {
    const result = await analyzeFile('/project/docs/readme.md', '/project');
    
    expect(result.documentationReferences).toContain(normalizePath('/project/docs/api/math.md'));
    expect(result.documentationReferences).toContain(normalizePath('/project/docs/api/utils.md'));
  });

  test('analyzeFile should detect code references in Markdown files', async () => {
    const result = await analyzeFile('/project/docs/api/math.md', '/project');
    
    expect(result.semanticDependencies).toContain('code_reference');
  });

  test('analyzeFile should throw an error for non-existent files', async () => {
    await expect(analyzeFile('/project/non-existent.ts', '/project'))
      .rejects.toThrow('File not found');
  });

  test('analyzeFile should return empty results for excluded files', async () => {
    // Simulate excluded file by modifying the isPathExcluded function
    jest.mock('../../utils/path-utils', () => ({
      ...jest.requireActual('../../utils/path-utils'),
      isPathExcluded: jest.fn().mockReturnValue(true)
    }));

    const result = await analyzeFile('/project/src/index.ts', '/project');
    
    expect(result.imports).toEqual([]);
    expect(result.functionCalls).toEqual([]);
    expect(result.semanticDependencies).toEqual([]);
    expect(result.documentationReferences).toEqual([]);
  });
}); 