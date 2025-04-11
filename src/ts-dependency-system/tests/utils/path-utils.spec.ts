import {
    normalizePath,
    getFileType,
    resolveRelativePath,
    getRelativePath,
    getProjectRoot,
    joinPaths,
    isPathExcluded,
    isSubpath,
    getCommonPath,
    isValidProjectPath
} from '../../utils/path-utils';
import { existsSync } from 'fs';
import { join } from 'path';

describe('Path Utils', () => {
    describe('normalizePath', () => {
        it('should normalize empty path', () => {
            expect(normalizePath('')).toBe('');
        });

        it('should normalize relative path', () => {
            const result = normalizePath('test/path');
            expect(result).toBe(join(process.cwd(), 'test/path').replace(/\\/g, '/'));
        });

        it('should normalize absolute path', () => {
            const result = normalizePath('/test/path');
            expect(result).toBe('/test/path');
        });

        it('should convert backslashes to forward slashes', () => {
            const result = normalizePath('test\\path');
            expect(result).toBe(join(process.cwd(), 'test/path').replace(/\\/g, '/'));
        });

        it('should remove trailing slash', () => {
            const result = normalizePath('/test/path/');
            expect(result).toBe('/test/path');
        });

        it('should preserve root slash', () => {
            const result = normalizePath('/');
            expect(result).toBe('/');
        });
    });

    describe('getFileType', () => {
        it('should return correct file type for Python files', () => {
            expect(getFileType('test.py')).toBe('py');
        });

        it('should return correct file type for JavaScript files', () => {
            expect(getFileType('test.js')).toBe('js');
            expect(getFileType('test.ts')).toBe('js');
            expect(getFileType('test.jsx')).toBe('js');
            expect(getFileType('test.tsx')).toBe('js');
        });

        it('should return correct file type for Markdown files', () => {
            expect(getFileType('test.md')).toBe('md');
            expect(getFileType('test.rst')).toBe('md');
        });

        it('should return correct file type for HTML files', () => {
            expect(getFileType('test.html')).toBe('html');
            expect(getFileType('test.htm')).toBe('html');
        });

        it('should return correct file type for CSS files', () => {
            expect(getFileType('test.css')).toBe('css');
        });

        it('should return generic for unknown file types', () => {
            expect(getFileType('test.txt')).toBe('generic');
        });
    });

    describe('resolveRelativePath', () => {
        it('should resolve relative path with default extension', () => {
            const result = resolveRelativePath('/test', './module');
            expect(result).toBe('/test/module.js');
        });

        it('should not add extension if path already has one', () => {
            const result = resolveRelativePath('/test', './module.ts');
            expect(result).toBe('/test/module.ts');
        });

        it('should handle parent directory references', () => {
            const result = resolveRelativePath('/test/path', '../module');
            expect(result).toBe('/test/module.js');
        });
    });

    describe('getRelativePath', () => {
        it('should get relative path between two directories', () => {
            const result = getRelativePath('/test/path/file.txt', '/test');
            expect(result).toBe('path/file.txt');
        });

        it('should handle same directory', () => {
            const result = getRelativePath('/test/file.txt', '/test');
            expect(result).toBe('file.txt');
        });

        it('should handle different drives', () => {
            const result = getRelativePath('C:/test/file.txt', 'D:/test');
            expect(result).toBe('C:/test/file.txt');
        });
    });

    describe('getProjectRoot', () => {
        it('should find project root directory', () => {
            const result = getProjectRoot();
            expect(existsSync(join(result, '.clinerules'))).toBe(true);
        });
    });

    describe('joinPaths', () => {
        it('should join and normalize paths', () => {
            const result = joinPaths('/test', 'path', 'file.txt');
            expect(result).toBe('/test/path/file.txt');
        });

        it('should handle multiple path components', () => {
            const result = joinPaths('/test', 'path', 'subpath', 'file.txt');
            expect(result).toBe('/test/path/subpath/file.txt');
        });
    });

    describe('isPathExcluded', () => {
        it('should return false for empty exclusion list', () => {
            expect(isPathExcluded('/test/path', [])).toBe(false);
        });

        it('should match exact path', () => {
            expect(isPathExcluded('/test/path', ['/test/path'])).toBe(true);
        });

        it('should match wildcard pattern', () => {
            expect(isPathExcluded('/test/path/file.txt', ['/test/*/file.txt'])).toBe(true);
        });

        it('should match subpath', () => {
            expect(isPathExcluded('/test/path/file.txt', ['/test'])).toBe(true);
        });
    });

    describe('isSubpath', () => {
        it('should return true for subpath', () => {
            expect(isSubpath('/test/path/file.txt', '/test')).toBe(true);
        });

        it('should return false for same path', () => {
            expect(isSubpath('/test', '/test')).toBe(false);
        });

        it('should return false for parent path', () => {
            expect(isSubpath('/test', '/test/path')).toBe(false);
        });
    });

    describe('getCommonPath', () => {
        it('should find common path prefix', () => {
            const result = getCommonPath([
                '/test/path1/file.txt',
                '/test/path2/file.txt',
                '/test/path3/file.txt'
            ]);
            expect(result).toBe('/test');
        });

        it('should return empty string for empty list', () => {
            expect(getCommonPath([])).toBe('');
        });

        it('should return single path if only one provided', () => {
            expect(getCommonPath(['/test/path'])).toBe('/test/path');
        });
    });

    describe('isValidProjectPath', () => {
        it('should return true for path within project root', () => {
            const projectRoot = getProjectRoot();
            expect(isValidProjectPath(join(projectRoot, 'test/path'))).toBe(true);
        });

        it('should return true for project root itself', () => {
            const projectRoot = getProjectRoot();
            expect(isValidProjectPath(projectRoot)).toBe(true);
        });

        it('should return false for path outside project root', () => {
            expect(isValidProjectPath('/outside/path')).toBe(false);
        });
    });
}); 