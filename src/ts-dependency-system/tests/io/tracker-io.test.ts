/**
 * Tests for the tracker-io module
 */

import * as path from 'path';
import * as fs from 'fs/promises';
import mockFs from 'mock-fs';
import {
  getTrackerPath,
  readTrackerFile,
  writeTrackerFile,
  backupTrackerFile,
  mergeTrackers,
  exportTracker,
  removeFileFromTracker,
  removeKeyFromTracker
} from '../../io/tracker-io';
import { ConfigManager } from '../../utils/config-manager';
import { KeyInfo } from '../../core/key-manager';

// Mock ConfigManager instance
jest.mock('../../utils/config-manager', () => {
  return {
    ConfigManager: {
      getInstance: jest.fn().mockReturnValue({
        getPath: jest.fn((key, defaultValue) => defaultValue),
        getConfigLastModified: jest.fn().mockReturnValue(0),
        getDocDirectories: jest.fn().mockReturnValue(['docs']),
        getCodeRootDirectories: jest.fn().mockReturnValue(['src'])
      })
    }
  };
});

// Mocking the console for tests
const originalConsole = console;
beforeEach(() => {
  global.console = {
    ...originalConsole,
    log: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    info: jest.fn(),
    debug: jest.fn()
  };
});

afterEach(() => {
  global.console = originalConsole;
  jest.clearAllMocks();
  mockFs.restore();
});

describe('tracker-io', () => {
  describe('getTrackerPath', () => {
    it('should return path for main tracker', () => {
      const projectRoot = '/project';
      const path = getTrackerPath(projectRoot, 'main');
      expect(path).toContain('cline_docs');
      expect(path).toContain('module_relationship_tracker.md');
    });

    it('should return path for doc tracker', () => {
      const projectRoot = '/project';
      const path = getTrackerPath(projectRoot, 'doc');
      expect(path).toContain('cline_docs');
      expect(path).toContain('doc_tracker.md');
    });

    it('should return path for mini tracker', () => {
      const projectRoot = '/project';
      const modulePath = '/project/src/module1';
      const path = getTrackerPath(projectRoot, 'mini', modulePath);
      expect(path).toContain('module1');
      expect(path).toContain('_module.md');
    });

    it('should throw error if modulePath is missing for mini tracker', () => {
      const projectRoot = '/project';
      expect(() => getTrackerPath(projectRoot, 'mini')).toThrow();
    });
  });

  describe('readTrackerFile', () => {
    beforeEach(() => {
      // Setup mock filesystem
      mockFs({
        '/project/tracker.md': `---KEY_DEFINITIONS_START---
Key Definitions:
1Aa: /path/to/file1.ts
1Ab: /path/to/file2.ts
---KEY_DEFINITIONS_END---

last_KEY_edit: test_edit_1
last_GRID_edit: test_edit_2

---GRID_START---
X 1Aa 1Ab
1Aa = o<
1Ab = >o
---GRID_END---`
      });
    });

    it('should read and parse a tracker file', async () => {
      const result = await readTrackerFile('/project/tracker.md');
      
      expect(result.keys).toEqual({
        '1Aa': '/path/to/file1.ts',
        '1Ab': '/path/to/file2.ts'
      });
      
      expect(Object.keys(result.grid)).toHaveLength(2);
      expect(result.lastKeyEdit).toBe('test_edit_1');
      expect(result.lastGridEdit).toBe('test_edit_2');
    });

    it('should return empty structure for non-existent file', async () => {
      const result = await readTrackerFile('/non-existent.md');
      
      expect(result.keys).toEqual({});
      expect(result.grid).toEqual({});
      expect(result.lastKeyEdit).toBe('');
      expect(result.lastGridEdit).toBe('');
    });
  });

  describe('writeTrackerFile', () => {
    beforeEach(() => {
      // Setup mock filesystem
      mockFs({
        '/project': {}
      });
    });

    it('should write tracker data to a file', async () => {
      const trackerPath = '/project/new-tracker.md';
      const keys = {
        '1Aa': '/path/to/file1.ts',
        '1Ab': '/path/to/file2.ts'
      };
      const grid = {
        '1Aa': 'o<',
        '1Ab': '>o'
      };

      const success = await writeTrackerFile(
        trackerPath,
        keys,
        grid,
        'test_edit_1',
        'test_edit_2'
      );

      expect(success).toBe(true);

      // Check if file was created
      const fileExists = await fs.access(trackerPath)
        .then(() => true)
        .catch(() => false);
      expect(fileExists).toBe(true);

      // Read back and verify
      const fileContent = await fs.readFile(trackerPath, 'utf-8');
      expect(fileContent).toContain('---KEY_DEFINITIONS_START---');
      expect(fileContent).toContain('1Aa: /path/to/file1.ts');
      expect(fileContent).toContain('last_KEY_edit: test_edit_1');
      expect(fileContent).toContain('---GRID_START---');
    });
  });

  describe('mergeTrackers', () => {
    beforeEach(() => {
      // Setup mock filesystem with two tracker files
      mockFs({
        '/project/tracker1.md': `---KEY_DEFINITIONS_START---
Key Definitions:
1Aa: /path/to/file1.ts
1Ab: /path/to/file2.ts
---KEY_DEFINITIONS_END---

last_KEY_edit: test_edit_1
last_GRID_edit: test_edit_2

---GRID_START---
X 1Aa 1Ab
1Aa = o<
1Ab = >o
---GRID_END---`,
        '/project/tracker2.md': `---KEY_DEFINITIONS_START---
Key Definitions:
1Ab: /path/to/file2.ts
1Ac: /path/to/file3.ts
---KEY_DEFINITIONS_END---

last_KEY_edit: test_edit_3
last_GRID_edit: test_edit_4

---GRID_START---
X 1Ab 1Ac
1Ab = o>
1Ac = <o
---GRID_END---`
      });
    });

    it('should merge two tracker files', async () => {
      const primaryPath = '/project/tracker1.md';
      const secondaryPath = '/project/tracker2.md';
      const outputPath = '/project/merged.md';

      const result = await mergeTrackers(primaryPath, secondaryPath, outputPath);

      expect(result).not.toBeNull();
      if (result) {
        // Check merged keys
        expect(Object.keys(result.keys)).toHaveLength(3);
        expect(result.keys).toHaveProperty('1Aa');
        expect(result.keys).toHaveProperty('1Ab');
        expect(result.keys).toHaveProperty('1Ac');

        // Check merged grid
        expect(Object.keys(result.grid)).toHaveLength(3);
      }

      // Check if output file was created
      const fileExists = await fs.access(outputPath)
        .then(() => true)
        .catch(() => false);
      expect(fileExists).toBe(true);
    });
  });

  describe('exportTracker', () => {
    beforeEach(() => {
      // Setup mock filesystem
      mockFs({
        '/project/tracker.md': `---KEY_DEFINITIONS_START---
Key Definitions:
1Aa: /path/to/file1.ts
1Ab: /path/to/file2.ts
---KEY_DEFINITIONS_END---

last_KEY_edit: test_edit_1
last_GRID_edit: test_edit_2

---GRID_START---
X 1Aa 1Ab
1Aa = o<
1Ab = >o
---GRID_END---`
      });
    });

    it('should export tracker to JSON format', async () => {
      const trackerPath = '/project/tracker.md';
      const outputPath = '/project/tracker.json';

      const result = await exportTracker(trackerPath, 'json', outputPath);

      expect(result).toBe(outputPath);

      // Check if output file was created
      const fileExists = await fs.access(outputPath)
        .then(() => true)
        .catch(() => false);
      expect(fileExists).toBe(true);

      // Verify JSON content
      const jsonContent = await fs.readFile(outputPath, 'utf-8');
      const jsonData = JSON.parse(jsonContent);
      expect(jsonData).toHaveProperty('keys');
      expect(jsonData).toHaveProperty('grid');
      expect(jsonData).toHaveProperty('metadata');
    });

    it('should export tracker to CSV format', async () => {
      const trackerPath = '/project/tracker.md';
      const outputPath = '/project/tracker.csv';

      const result = await exportTracker(trackerPath, 'csv', outputPath);

      expect(result).toBe(outputPath);

      // Check if output file was created
      const fileExists = await fs.access(outputPath)
        .then(() => true)
        .catch(() => false);
      expect(fileExists).toBe(true);

      // Verify CSV content
      const csvContent = await fs.readFile(outputPath, 'utf-8');
      expect(csvContent).toContain('Key,Path');
      expect(csvContent).toContain('1Aa,/path/to/file1.ts');
    });

    it('should export tracker to DOT format', async () => {
      const trackerPath = '/project/tracker.md';
      const outputPath = '/project/tracker.dot';

      const result = await exportTracker(trackerPath, 'dot', outputPath);

      expect(result).toBe(outputPath);

      // Check if output file was created
      const fileExists = await fs.access(outputPath)
        .then(() => true)
        .catch(() => false);
      expect(fileExists).toBe(true);

      // Verify DOT content
      const dotContent = await fs.readFile(outputPath, 'utf-8');
      expect(dotContent).toContain('digraph dependencies');
      expect(dotContent).toContain('rankdir=LR');
    });
  });

  describe('removeKeyFromTracker', () => {
    beforeEach(() => {
      // Setup mock filesystem
      mockFs({
        '/project/tracker.md': `---KEY_DEFINITIONS_START---
Key Definitions:
1Aa: /path/to/file1.ts
1Ab: /path/to/file2.ts
1Ac: /path/to/file3.ts
---KEY_DEFINITIONS_END---

last_KEY_edit: test_edit_1
last_GRID_edit: test_edit_2

---GRID_START---
X 1Aa 1Ab 1Ac
1Aa = o<<
1Ab = >o<
1Ac = >>o
---GRID_END---`,
        '/project/backups': {}
      });
    });

    it('should remove a key from tracker', async () => {
      const trackerPath = '/project/tracker.md';
      const keyToRemove = '1Ab';

      const result = await removeKeyFromTracker(trackerPath, keyToRemove);

      expect(result).toBe(true);

      // Read back and verify key was removed
      const trackerData = await readTrackerFile(trackerPath);
      expect(trackerData.keys).not.toHaveProperty(keyToRemove);
      expect(Object.keys(trackerData.keys)).toHaveLength(2);
      expect(Object.keys(trackerData.grid)).toHaveLength(2);
    });

    it('should create a backup before removing key', async () => {
      const trackerPath = '/project/tracker.md';
      const keyToRemove = '1Ab';

      await removeKeyFromTracker(trackerPath, keyToRemove);

      // Check if backup was created
      const backupFiles = await fs.readdir('/project/backups');
      expect(backupFiles.length).toBeGreaterThan(0);
      expect(backupFiles[0]).toContain('tracker.md');
    });
  });

  describe('removeFileFromTracker', () => {
    beforeEach(() => {
      // Setup mock filesystem
      mockFs({
        '/project/tracker.md': `---KEY_DEFINITIONS_START---
Key Definitions:
1Aa: /path/to/file1.ts
1Ab: /path/to/file2.ts
---KEY_DEFINITIONS_END---

last_KEY_edit: test_edit_1
last_GRID_edit: test_edit_2

---GRID_START---
X 1Aa 1Ab
1Aa = o<
1Ab = >o
---GRID_END---`,
        '/project/backups': {}
      });
    });

    it('should remove a file from tracker using its path and key', async () => {
      const trackerPath = '/project/tracker.md';
      const fileToRemove = '/path/to/file1.ts';
      const pathToKeyInfo: Record<string, KeyInfo> = {
        '/path/to/file1.ts': {
          keyString: '1Aa',
          isDirectory: false,
          normPath: '/path/to/file1.ts',
          parentPath: '/path/to',
          tier: 1
        }
      };

      const result = await removeFileFromTracker(trackerPath, fileToRemove, pathToKeyInfo);

      expect(result).toBe(true);

      // Read back and verify file was removed
      const trackerData = await readTrackerFile(trackerPath);
      expect(trackerData.keys).not.toHaveProperty('1Aa');
      expect(Object.keys(trackerData.keys)).toHaveLength(1);
    });
  });

  describe('backupTrackerFile', () => {
    beforeEach(() => {
      // Setup mock filesystem
      mockFs({
        '/project/tracker.md': 'Test content',
        '/project/backups': {}
      });
    });

    it('should create a backup of a tracker file', async () => {
      const trackerPath = '/project/tracker.md';
      
      const backupPath = await backupTrackerFile(trackerPath);
      
      expect(backupPath).not.toBe('');
      expect(backupPath).toContain('/project/backups');
      expect(backupPath).toContain('tracker.md');
      
      // Check if backup file exists and has correct content
      const backupContent = await fs.readFile(backupPath, 'utf-8');
      expect(backupContent).toBe('Test content');
    });

    it('should return empty string for non-existent file', async () => {
      const trackerPath = '/project/non-existent.md';
      
      const backupPath = await backupTrackerFile(trackerPath);
      
      expect(backupPath).toBe('');
    });
  });
}); 