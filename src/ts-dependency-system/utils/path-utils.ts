/**
 * Core module for path utilities.
 * Handles path normalization, validation, and comparison.
 */

import { normalize as pathNormalize, join, relative, dirname, isAbsolute, resolve } from 'path';
import { existsSync, statSync } from 'fs';
// 使用相对路径导入
import { cacheManager } from './cache-manager';

// 创建路径相关缓存
const pathCache = cacheManager.getCache<string>('path-utils', 1800); // 30分钟缓存
const projectRootCache = cacheManager.getCache<string>('project-root', 3600); // 1小时缓存
const fileTypeCache = cacheManager.getCache<string>('file-type', 1800); // 30分钟缓存

/**
 * Normalize a file path for consistent comparison.
 * @param path - Path to normalize
 * @returns Normalized path
 */
export function normalizePath(path: string): string {
    if (!path) return '';
    
    // 检查缓存
    const cacheKey = `normalize:${path}`;
    const cached = pathCache.get(cacheKey);
    if (cached !== null) {
        return cached;
    }
    
    // Ensure absolute path before normalization for consistency
    let absolutePath = path;
    if (!isAbsolute(path)) {
        absolutePath = resolve(path);
    }
    
    // Normalize path and convert to forward slashes
    let normalized = pathNormalize(absolutePath).replace(/\\/g, '/');
    
    // Remove trailing slash unless it's the root directory
    if (normalized.length > 1 && normalized.endsWith('/')) {
        normalized = normalized.slice(0, -1);
    }
    
    // 缓存结果
    pathCache.set(cacheKey, normalized);
    return normalized;
}

/**
 * Determines the file type based on its extension.
 * @param filePath - The path to the file
 * @returns The file type as a string (e.g., "py", "js", "md", "generic")
 */
export function getFileType(filePath: string): string {
    // 检查缓存
    const cacheKey = `filetype:${filePath}`;
    const cached = fileTypeCache.get(cacheKey);
    if (cached !== null) {
        return cached;
    }
    
    const ext = filePath.split('.').pop()?.toLowerCase() || '';
    let fileType: string;
    
    switch (ext) {
        case 'py': fileType = 'py'; break;
        case 'js':
        case 'ts':
        case 'jsx':
        case 'tsx': fileType = 'js'; break;
        case 'md':
        case 'rst': fileType = 'md'; break;
        case 'html':
        case 'htm': fileType = 'html'; break;
        case 'css': fileType = 'css'; break;
        default: fileType = 'generic';
    }
    
    // 缓存结果
    fileTypeCache.set(cacheKey, fileType);
    return fileType;
}

/**
 * Resolve a relative import path to an absolute path based on the source directory.
 * @param sourceDir - The directory of the source file
 * @param relativePath - The relative import path
 * @param defaultExtension - The file extension to append if none is present (default is '.js')
 * @returns The resolved absolute path
 */
export function resolveRelativePath(
    sourceDir: string,
    relativePath: string,
    defaultExtension: string = '.js'
): string {
    // 检查缓存
    const cacheKey = `resolve:${sourceDir}:${relativePath}:${defaultExtension}`;
    const cached = pathCache.get(cacheKey);
    if (cached !== null) {
        return cached;
    }
    
    let resolved = normalizePath(join(sourceDir, relativePath));
    if (!resolved.includes('.')) {
        resolved = resolved + defaultExtension;
    }
    
    // 缓存结果
    pathCache.set(cacheKey, resolved);
    return resolved;
}

/**
 * Get a path relative to a base path.
 * @param path - Path to convert
 * @param basePath - Base path to make relative to
 * @returns Relative path
 */
export function getRelativePath(path: string, basePath: string): string {
    // 检查缓存
    const cacheKey = `relative:${path}:${basePath}`;
    const cached = pathCache.get(cacheKey);
    if (cached !== null) {
        return cached;
    }
    
    const normPath = normalizePath(path);
    const normBase = normalizePath(basePath);
    let relativePath: string;
    
    try {
        relativePath = relative(normBase, normPath).replace(/\\/g, '/');
    } catch {
        relativePath = normPath; // Different drive
    }
    
    // 缓存结果
    pathCache.set(cacheKey, relativePath);
    return relativePath;
}

/**
 * Find the project root directory.
 * @returns Path to the project root directory
 */
export function getProjectRoot(): string {
    // 检查缓存
    const cacheKey = `project-root:${process.cwd()}`;
    const cached = projectRootCache.get(cacheKey);
    if (cached !== null) {
        return cached;
    }
    
    const rootIndicators = [
        '.git',
        '.clinerules',
        'pyproject.toml',
        'setup.py',
        'package.json',
        'Cargo.toml',
        'CMakeLists.txt',
        '.clinerules.config.json'
    ];

    let currentDir = process.cwd();
    while (true) {
        for (const indicator of rootIndicators) {
            if (existsSync(join(currentDir, indicator))) {
                const normalized = normalizePath(currentDir);
                // 缓存结果
                projectRootCache.set(cacheKey, normalized);
                return normalized;
            }
        }
        const parentDir = dirname(currentDir);
        if (parentDir === currentDir) {
            break;
        }
        currentDir = parentDir;
    }
    
    const result = normalizePath(process.cwd());
    // 缓存结果
    projectRootCache.set(cacheKey, result);
    return result;
}

/**
 * Join paths and normalize the result.
 * @param basePath - Base path
 * @param paths - Additional path components
 * @returns Joined and normalized path
 */
export function joinPaths(basePath: string, ...paths: string[]): string {
    // 检查缓存
    const pathsStr = paths.join(':');
    const cacheKey = `join:${basePath}:${pathsStr}`;
    const cached = pathCache.get(cacheKey);
    if (cached !== null) {
        return cached;
    }
    
    const result = normalizePath(join(basePath, ...paths));
    // 缓存结果
    pathCache.set(cacheKey, result);
    return result;
}

/**
 * Check if a path should be excluded based on a list of exclusion patterns.
 * @param path - Path to check
 * @param excludedPaths - List of exclusion patterns
 * @returns True if the path should be excluded, False otherwise
 */
export function isPathExcluded(path: string, excludedPaths: string[]): boolean {
    if (!excludedPaths.length) return false;
    
    // 检查缓存 - 使用路径和排除模式数量作为缓存键
    const excludedHash = excludedPaths.length.toString();
    const cacheKey = `excluded:${path}:${excludedHash}`;
    const cached = pathCache.get(cacheKey);
    if (cached !== null) {
        return cached === 'true';
    }
    
    const normPath = normalizePath(path);
    
    for (const excluded of excludedPaths) {
        const normExcluded = normalizePath(excluded);
        if (normExcluded.includes('*')) {
            // Convert wildcard to regex
            const patternStr = normExcluded
                .replace(/\./g, '\\.')
                .replace(/\*/g, '.*');
            try {
                const pattern = new RegExp(`^${patternStr}$`);
                if (pattern.test(normPath)) {
                    // 缓存结果
                    pathCache.set(cacheKey, 'true');
                    return true;
                }
            } catch (e) {
                console.warn(`Invalid regex pattern derived from exclusion '${excluded}': ${e}`);
            }
        } else if (normPath === normExcluded || isSubpath(normPath, normExcluded)) {
            // 缓存结果
            pathCache.set(cacheKey, 'true');
            return true;
        }
    }
    
    // 缓存结果
    pathCache.set(cacheKey, 'false');
    return false;
}

/**
 * Check if a path is a subpath of another path.
 * @param path - Path to check
 * @param parentPath - Potential parent path
 * @returns True if path is a subpath of parentPath, False otherwise
 */
export function isSubpath(path: string, parentPath: string): boolean {
    // 检查缓存
    const cacheKey = `subpath:${path}:${parentPath}`;
    const cached = pathCache.get(cacheKey);
    if (cached !== null) {
        return cached === 'true';
    }
    
    const normPath = normalizePath(path);
    const normParent = normalizePath(parentPath);
    
    if (!normParent || normPath === normParent) {
        // 缓存结果
        pathCache.set(cacheKey, 'false');
        return false;
    }
    
    const parentWithSep = normParent + '/';
    const result = normPath.startsWith(parentWithSep);
    
    // 缓存结果
    pathCache.set(cacheKey, result ? 'true' : 'false');
    return result;
}

/**
 * Find the common path prefix for a list of paths.
 * @param paths - List of paths
 * @returns Common path prefix
 */
export function getCommonPath(paths: string[]): string {
    if (!paths.length) return '';
    
    // 检查缓存 - 使用路径数量和前几个路径作为缓存键
    const pathSample = paths.slice(0, 3).join(':');
    const cacheKey = `common:${paths.length}:${pathSample}`;
    const cached = pathCache.get(cacheKey);
    if (cached !== null) {
        return cached;
    }
    
    const normPaths = paths.map(p => normalizePath(p));
    
    let common = normPaths[0];
    for (let i = 1; i < normPaths.length; i++) {
        const path = normPaths[i];
        let j = 0;
        while (j < common.length && j < path.length && common[j] === path[j]) {
            j++;
        }
        common = common.slice(0, j);
        if (!common) break;
    }
    
    const result = normalizePath(common);
    // 缓存结果
    pathCache.set(cacheKey, result);
    return result;
}

/**
 * Check if a path is within the project root directory.
 * @param path - Path to check
 * @returns True if the path is within the project root, False otherwise
 */
export function isValidProjectPath(path: string): boolean {
    // 检查缓存
    const cacheKey = `valid-project:${path}`;
    const cached = pathCache.get(cacheKey);
    if (cached !== null) {
        return cached === 'true';
    }
    
    const projectRoot = getProjectRoot();
    const normPath = normalizePath(path);
    const result = normPath === projectRoot || normPath.startsWith(projectRoot + '/');
    
    // 缓存结果
    pathCache.set(cacheKey, result ? 'true' : 'false');
    return result;
}

/**
 * 清除所有路径相关缓存
 */
export function clearPathCaches(): void {
    pathCache.invalidate('.*');
    projectRootCache.invalidate('.*');
    fileTypeCache.invalidate('.*');
} 