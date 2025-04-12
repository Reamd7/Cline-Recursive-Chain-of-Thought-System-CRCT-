/**
 * Dependency Suggester
 * 
 * This module provides functionality for suggesting dependencies between files
 * based on analysis results, file content similarity, and project structure.
 * Assigns specific characters based on the type of dependency found.
 */

import * as fs from 'fs';
import * as path from 'path';
import { KeyInfo, getKeyFromPath } from '../core/key-manager';
import { ConfigManager } from '../utils/config-manager';
import { normalizePath, resolveRelativePath, isSubpath, getFileType, getProjectRoot } from '../utils/path-utils';
import { cached, clearAllCaches } from '../utils/cache-manager';
import { DependencySystemError } from '../core/exceptions';

import * as logging from '../utils/logging';
const logger = logging.getLogger('dependency-suggester');

// Character Definitions (matching Python version):
// <: Row depends on column.
// >: Column depends on row.
// x: Mutual dependency.
// d: Documentation dependency.
// o: Self dependency (diagonal only).
// n: Verified no dependency.
// p: Placeholder (unverified).
// s: Semantic dependency (weak .06-.07)
// S: Semantic dependency (strong .07+)

/**
 * Clear all internal caches
 */
export function clearCaches(): void {
  clearAllCaches();
}

/**
 * Load metadata file with caching
 * @param metadataPath Path to the metadata file
 * @returns Dictionary containing metadata or empty object on failure
 */
export function loadMetadata(metadataPath: string): any {
  try {
    const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
    return metadata;
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      logger.warn(`Metadata file not found at ${metadataPath}. Run generate-embeddings first.`);
    } else if (error instanceof SyntaxError) {
      logger.error(`Invalid JSON in metadata file ${metadataPath}: ${error}`);
    } else {
      logger.error(`Unexpected error reading metadata ${metadataPath}: ${error}`);
    }
    return {};
  }
}

/**
 * Suggest dependencies for a file, assigning appropriate characters, using contextual keys
 * Matches Python version's suggest_dependencies function
 * 
 * @param filePath Path to the file to analyze
 * @param pathToKeyInfo Global map from normalized paths to KeyInfo objects
 * @param projectRoot Root directory of the project
 * @param fileAnalysisResults Pre-computed analysis results for files
 * @param threshold Confidence threshold for semantic suggestions (0.0 to 1.0)
 * @returns List of (dependency_key_string, dependency_character) tuples
 */
export function suggestDependencies(
  filePath: string,
  pathToKeyInfo: { [key: string]: KeyInfo },
  projectRoot: string,
  fileAnalysisResults: { [key: string]: any },
  threshold: number = 0.7
): Array<[string, string]> { // Return type matches Python: List[Tuple[str, str]]
  if (!fs.existsSync(filePath)) {
    logger.warn(`File not found: ${filePath}`);
    return [];
  }

  const normPath = normalizePath(filePath);
  const fileExt = path.extname(normPath).toLowerCase();

  // Pass pathToKeyInfo down to appropriate suggester
  if (fileExt === '.py') {
    return suggestPythonDependencies(normPath, pathToKeyInfo, projectRoot, fileAnalysisResults, threshold);
  } else if (fileExt === '.js' || fileExt === '.ts') {
    return suggestJavaScriptDependencies(normPath, pathToKeyInfo, projectRoot, fileAnalysisResults, threshold);
  } else if (fileExt === '.md' || fileExt === '.rst') {
    const config = ConfigManager.getInstance();
    const embeddingsDirRel = config.get<string>('paths.embeddings_dir', 'src/ts-dependency-system/analysis/embeddings');
    const embeddingsDir = normalizePath(path.join(projectRoot, embeddingsDirRel));
    const metadataPath = path.join(embeddingsDir, "metadata.json");
    return suggestDocumentationDependencies(normPath, pathToKeyInfo, projectRoot, fileAnalysisResults, threshold, embeddingsDir, metadataPath);
  } else {
    // Generic uses semantic only
    return suggestGenericDependencies(normPath, pathToKeyInfo, projectRoot, threshold);
  }
}

/**
 * Identifies Python structural dependencies (calls, attributes, inheritance) using contextual keys
 * @param sourcePath Path to the source file
 * @param sourceAnalysis Analysis result for the source file
 * @param pathToKeyInfo Map from normalized paths to KeyInfo objects
 * @param projectRoot Root directory of the project
 * @returns List of tuples (dependency_key_string, dependency_character)
 */
function _identifyStructuralDependencies(
  sourcePath: string, 
  sourceAnalysis: any,
  pathToKeyInfo: { [key: string]: KeyInfo },
  projectRoot: string
): Array<[string, string]> {
  const suggestions: Array<[string, string]> = [];
  if (!sourceAnalysis) return [];

  const imports = sourceAnalysis.imports || [];
  const calls = sourceAnalysis.calls || [];
  const attributes = sourceAnalysis.attribute_accesses || [];
  const inheritance = sourceAnalysis.inheritance || [];
  const sourceDir = path.dirname(sourcePath);

  // --- Import map building (resolves to paths) ---
  const importMapCache: { [key: string]: { [key: string]: string } } = {};
  
  function _buildImportMap(currentSourcePath: string): { [key: string]: string } {
    const normSourcePath = normalizePath(currentSourcePath);
    if (importMapCache[normSourcePath]) {
      return importMapCache[normSourcePath];
    }
    
    const localImportMap: { [key: string]: string } = {};
    try {
      const content = fs.readFileSync(normSourcePath, 'utf8');
      // Simple implementation to extract imports (TypeScript doesn't have AST parsing like Python)
      // This is a simplified version
      
      // Extract standard imports
      const importRegex = /import\s+(\w+)\s+from\s+['"]([^'"]+)['"]/g;
      let match;
      while ((match = importRegex.exec(content)) !== null) {
        const importedName = match[1];
        const moduleName = match[2];
        const possiblePaths = _convertImportToPath(moduleName, path.dirname(normSourcePath), projectRoot);
        if (possiblePaths.length > 0) {
          localImportMap[importedName] = normalizePath(possiblePaths[0]);
        }
      }
      
      // Extract named imports
      const namedImportRegex = /import\s+\{([^}]+)\}\s+from\s+['"]([^'"]+)['"]/g;
      while ((match = namedImportRegex.exec(content)) !== null) {
        const importedNames = match[1].split(',').map(name => {
          const parts = name.trim().split(' as ');
          return parts.length > 1 ? parts[1].trim() : parts[0].trim();
        });
        const moduleName = match[2];
        const possiblePaths = _convertImportToPath(moduleName, path.dirname(normSourcePath), projectRoot);
        if (possiblePaths.length > 0) {
          for (const name of importedNames) {
            localImportMap[name] = normalizePath(possiblePaths[0]);
          }
        }
      }
      
    } catch (error) {
      logger.error(`Error building import map for ${normSourcePath}: ${error}`);
    }
    
    importMapCache[normSourcePath] = localImportMap;
    return localImportMap;
  }

  // Build the import map for the current source file
  const importMap = _buildImportMap(sourcePath);

  // --- Helper to resolve potential source name to key string ---
  const resolvedCache: { [key: string]: string | null } = {};
  
  function _resolveSourceToKeyString(potentialSourceName: string | null): string | null {
    if (!potentialSourceName) return null;
    
    const cacheKey = `${sourcePath}:${potentialSourceName}`;
    if (cacheKey in resolvedCache) {
      return resolvedCache[cacheKey];
    }

    // Check the primary name part (e.g., 'os' in 'os.path.join')
    const baseName = potentialSourceName.split('.')[0];
    const resolvedModulePath = importMap[baseName]; // Get path from import map

    let foundKeyString = null;
    if (resolvedModulePath) {
      foundKeyString = getKeyFromPath(resolvedModulePath, pathToKeyInfo);
    }

    resolvedCache[cacheKey] = foundKeyString;
    return foundKeyString;
  }

  // Get source key string once for logging/comparison
  const sourceKeyString = getKeyFromPath(sourcePath, pathToKeyInfo);
  
  // Process Calls
  for (const call of calls) {
    const targetKeyString = _resolveSourceToKeyString(call.potential_source);
    if (targetKeyString && targetKeyString !== sourceKeyString) {
      logger.debug(`Suggesting ${sourceKeyString} -> ${targetKeyString} (>) due to call: ${call.target_name}`);
      suggestions.push([targetKeyString, ">"]);
    }
  }

  // Process Attribute Accesses
  for (const attr of attributes) {
    const targetKeyString = _resolveSourceToKeyString(attr.potential_source);
    if (targetKeyString && targetKeyString !== sourceKeyString) {
      logger.debug(`Suggesting ${sourceKeyString} -> ${targetKeyString} (>) due to attr access: ${attr.potential_source}.${attr.target_name}`);
      suggestions.push([targetKeyString, ">"]);
    }
  }

  // Process Inheritance
  for (const inh of inheritance) {
    const targetKeyString = _resolveSourceToKeyString(inh.potential_source);
    if (targetKeyString && targetKeyString !== sourceKeyString) {
      logger.debug(`Suggesting ${sourceKeyString} -> ${targetKeyString} (<) due to inheritance from: ${inh.base_class_name}`);
      suggestions.push([targetKeyString, "<"]);
    }
  }

  return [...new Set(suggestions.map(s => JSON.stringify(s)))].map(s => JSON.parse(s));
}

/**
 * Suggests dependencies for a Python file using contextual keys
 * @param filePath Path to the file
 * @param pathToKeyInfo Map from normalized paths to KeyInfo objects
 * @param projectRoot Root directory of the project
 * @param fileAnalysisResults Pre-computed analysis results for files
 * @param threshold Confidence threshold for semantic suggestions
 * @returns List of dependency suggestions
 */
export function suggestPythonDependencies(
  filePath: string,
  pathToKeyInfo: { [key: string]: KeyInfo },
  projectRoot: string,
  fileAnalysisResults: { [key: string]: any },
  threshold: number
): Array<[string, string]> {
  const normFilePath = normalizePath(filePath);
  const analysis = fileAnalysisResults[normFilePath];
  
  if (!analysis) {
    logger.warn(`No analysis results for ${normFilePath}`);
    return [];
  }
  
  if (analysis.error || analysis.skipped) {
    logger.info(`Skipping suggestion for ${normFilePath} due to analysis error/skip`);
    return [];
  }

  // 1. Explicit import dependency ('>')
  const explicitSuggestions: Array<[string, string]> = [];
  const explicitDepsPaths = _identifyPythonDependencies(
    normFilePath, 
    analysis, 
    fileAnalysisResults, 
    projectRoot, 
    pathToKeyInfo
  );
  
  for (const [depPath, depType] of explicitDepsPaths) {
    const depKeyString = getKeyFromPath(depPath, pathToKeyInfo);
    if (depKeyString) {
      const sourceKeyString = getKeyFromPath(normFilePath, pathToKeyInfo);
      if (sourceKeyString && depKeyString !== sourceKeyString) {
        logger.debug(`Suggesting ${sourceKeyString} -> ${depKeyString} (${depType}) due to explicit Python import`);
        explicitSuggestions.push([depKeyString, depType]);
      }
    }
  }

  // 2. Structural dependency ('>'/'<')
  const structuralSuggestions = _identifyStructuralDependencies(normFilePath, analysis, pathToKeyInfo, projectRoot);

  // 3. Semantic suggestions ('s'/'S')
  const semanticSuggestions = suggestSemanticDependencies(normFilePath, pathToKeyInfo, projectRoot);

  // 4. Combine
  const allSuggestions = [...explicitSuggestions, ...structuralSuggestions, ...semanticSuggestions];
  return _combineSuggestionsWithCharPriority(allSuggestions);
}

/**
 * Suggests dependencies for a JavaScript/TypeScript file
 * @param filePath Path to the file
 * @param pathToKeyInfo Map from normalized paths to KeyInfo objects
 * @param projectRoot Root directory of the project
 * @param fileAnalysisResults Pre-computed analysis results for files
 * @param threshold Confidence threshold for semantic suggestions
 * @returns List of dependency suggestions
 */
export function suggestJavaScriptDependencies(
  filePath: string,
  pathToKeyInfo: { [key: string]: KeyInfo },
  projectRoot: string,
  fileAnalysisResults: { [key: string]: any },
  threshold: number
): Array<[string, string]> {
  // Implementation similar to suggestPythonDependencies
  // Simplified for brevity
  
  const normFilePath = normalizePath(filePath);
  const analysis = fileAnalysisResults[normFilePath];
  
  if (!analysis) {
    logger.warn(`No analysis results for ${normFilePath}`);
    return [];
  }
  
  if (analysis.error || analysis.skipped) {
    logger.info(`Skipping suggestion for ${normFilePath} due to analysis error/skip`);
    return [];
  }
  
  // 1. Explicit import dependency ('>')
  const explicitSuggestions: Array<[string, string]> = [];
  const explicitDepsPaths = _identifyJavaScriptDependencies(
    normFilePath, 
    analysis, 
    fileAnalysisResults, 
    projectRoot, 
    pathToKeyInfo
  );
  
  for (const [depPath, depType] of explicitDepsPaths) {
    const depKeyString = getKeyFromPath(depPath, pathToKeyInfo);
    if (depKeyString) {
      const sourceKeyString = getKeyFromPath(normFilePath, pathToKeyInfo);
      if (sourceKeyString && depKeyString !== sourceKeyString) {
        logger.debug(`Suggesting ${sourceKeyString} -> ${depKeyString} (${depType}) due to explicit JS/TS import`);
        explicitSuggestions.push([depKeyString, depType]);
      }
    }
  }
  
  // 2. Semantic suggestions ('s'/'S')
  const semanticSuggestions = suggestSemanticDependencies(normFilePath, pathToKeyInfo, projectRoot);
  
  // 3. Combine
  const allSuggestions = [...explicitSuggestions, ...semanticSuggestions];
  return _combineSuggestionsWithCharPriority(allSuggestions);
}

/**
 * Suggests documentation dependencies
 * @param filePath Path to the file
 * @param pathToKeyInfo Map from normalized paths to KeyInfo objects
 * @param projectRoot Root directory of the project
 * @param fileAnalysisResults Pre-computed analysis results for files
 * @param threshold Confidence threshold for semantic suggestions
 * @param embeddingsDir Directory containing embeddings
 * @param metadataPath Path to embeddings metadata file
 * @returns List of dependency suggestions
 */
export function suggestDocumentationDependencies(
  filePath: string,
  pathToKeyInfo: { [key: string]: KeyInfo },
  projectRoot: string,
  fileAnalysisResults: { [key: string]: any },
  threshold: number,
  embeddingsDir: string,
  metadataPath: string
): Array<[string, string]> {
  const normFilePath = normalizePath(filePath);
  const analysis = fileAnalysisResults[normFilePath];
  
  if (!analysis) {
    logger.warn(`No analysis results for ${normFilePath}`);
    return [];
  }
  
  if (analysis.error || analysis.skipped) {
    logger.info(`Skipping suggestion for ${normFilePath} due to analysis error/skip`);
    return [];
  }
  
  // 1. Explicit document reference dependency ('d')
  const explicitSuggestions: Array<[string, string]> = [];
  const explicitDepsPaths = _identifyMarkdownDependencies(
    normFilePath, 
    analysis, 
    fileAnalysisResults, 
    projectRoot, 
    pathToKeyInfo
  );
  
  for (const [depPath, depType] of explicitDepsPaths) {
    const depKeyString = getKeyFromPath(depPath, pathToKeyInfo);
    if (depKeyString) {
      const sourceKeyString = getKeyFromPath(normFilePath, pathToKeyInfo);
      if (sourceKeyString && depKeyString !== sourceKeyString) {
        logger.debug(`Suggesting ${sourceKeyString} -> ${depKeyString} (${depType}) due to explicit markdown reference`);
        explicitSuggestions.push([depKeyString, depType]);
      }
    }
  }
  
  // 2. Semantic suggestions ('s'/'S')
  const semanticSuggestions = suggestSemanticDependencies(normFilePath, pathToKeyInfo, projectRoot);
  
  // 3. Combine
  const allSuggestions = [...explicitSuggestions, ...semanticSuggestions];
  return _combineSuggestionsWithCharPriority(allSuggestions);
}

/**
 * Suggests generic dependencies for files not covered by specific analyzers
 * @param filePath Path to the file
 * @param pathToKeyInfo Map from normalized paths to KeyInfo objects
 * @param projectRoot Root directory of the project
 * @param threshold Confidence threshold for semantic suggestions
 * @returns List of dependency suggestions
 */
export function suggestGenericDependencies(
  filePath: string,
  pathToKeyInfo: { [key: string]: KeyInfo },
  projectRoot: string,
  threshold: number
): Array<[string, string]> {
  // Generic files only use semantic suggestions
  return suggestSemanticDependencies(filePath, pathToKeyInfo, projectRoot);
}

/**
 * Suggests semantic dependencies based on embeddings
 * @param filePath Path to the file
 * @param pathToKeyInfo Map from normalized paths to KeyInfo objects
 * @param projectRoot Root directory of the project
 * @returns List of dependency suggestions
 */
export function suggestSemanticDependencies(
  filePath: string,
  pathToKeyInfo: { [key: string]: KeyInfo },
  projectRoot: string
): Array<[string, string]> {
  // This is a placeholder implementation
  // In the real implementation, this would load embeddings and calculate similarity
  
  const normFilePath = normalizePath(filePath);
  const sourceKeyString = getKeyFromPath(normFilePath, pathToKeyInfo);
  
  if (!sourceKeyString) {
    logger.warn(`No key found for file: ${normFilePath}`);
    return [];
  }
  
  const suggestions: Array<[string, string]> = [];
  
  // In a real implementation, we would:
  // 1. Load the embedding for the source file
  // 2. Load embeddings for other files
  // 3. Calculate similarity scores
  // 4. Add suggestions for files that exceed the threshold
  
  return suggestions;
}

/**
 * Combines suggestions with character priority
 * @param suggestions List of dependency suggestions
 * @returns Combined list with prioritized characters
 */
function _combineSuggestionsWithCharPriority(suggestions: Array<[string, string]>): Array<[string, string]> {
  // Character priority (highest to lowest)
  const charPriority: { [key: string]: number } = {
    'x': 5, // Mutual dependency (highest)
    '<': 4, // Row depends on column
    '>': 3, // Column depends on row
    'd': 2, // Documentation dependency
    'S': 1, // Strong semantic dependency
    's': 0  // Weak semantic dependency (lowest)
  };
  
  // Group suggestions by key
  const groupedSuggestions: { [key: string]: string[] } = {};
  
  for (const [key, char] of suggestions) {
    if (!groupedSuggestions[key]) {
      groupedSuggestions[key] = [];
    }
    groupedSuggestions[key].push(char);
  }
  
  // Select highest priority character for each key
  const result: Array<[string, string]> = [];
  
  for (const [key, chars] of Object.entries(groupedSuggestions)) {
    // Check for bidirectional dependencies
    if (chars.includes('<') && chars.includes('>')) {
      result.push([key, 'x']);
    } else {
      // Find highest priority character
      let highestPriorityChar = chars[0];
      let highestPriority = charPriority[highestPriorityChar] || -1;
      
      for (const char of chars) {
        const priority = charPriority[char] || -1;
        if (priority > highestPriority) {
          highestPriorityChar = char;
          highestPriority = priority;
        }
      }
      
      result.push([key, highestPriorityChar]);
    }
  }
  
  return result;
}

/**
 * Helper function to convert an import path to file path
 * @param importName Import name/path
 * @param sourceDir Source directory
 * @param projectRoot Project root directory
 * @param isFromImport Whether this is a "from X import Y" style import
 * @param relativeLevel Level of relative import (number of dots)
 * @returns List of possible file paths
 */
function _convertImportToPath(
  importName: string, 
  sourceDir: string, 
  projectRoot: string, 
  isFromImport: boolean = false,
  relativeLevel: number = 0
): string[] {
  // Very simplified implementation compared to Python version
  if (importName.startsWith('.')) {
    // Relative import
    let targetDir = sourceDir;
    for (let i = 1; i < importName.length; i++) {
      if (importName[i] === '.') {
        targetDir = path.dirname(targetDir);
      } else {
        break;
      }
    }
    
    const importWithoutDots = importName.replace(/^\.+/, '');
    const targetPath = path.join(targetDir, importWithoutDots);
    
    // Check for different possible files
    const possibleExtensions = ['.js', '.ts', '.py'];
    const possiblePaths = [];
    
    // Check for direct file
    for (const ext of possibleExtensions) {
      if (fs.existsSync(targetPath + ext)) {
        possiblePaths.push(targetPath + ext);
      }
    }
    
    // Check for package directory with index or __init__
    if (fs.existsSync(targetPath) && fs.statSync(targetPath).isDirectory()) {
      for (const ext of possibleExtensions) {
        const indexPath = path.join(targetPath, 'index' + ext);
        const initPath = path.join(targetPath, '__init__' + ext);
        
        if (fs.existsSync(indexPath)) {
          possiblePaths.push(indexPath);
        }
        
        if (fs.existsSync(initPath)) {
          possiblePaths.push(initPath);
        }
      }
      
      if (possiblePaths.length === 0) {
        // If no index/init files found, use the directory itself
        possiblePaths.push(targetPath);
      }
    }
    
    return possiblePaths;
  } else {
    // Absolute import - simplified
    // In a real implementation, this would need to be more sophisticated
    // to handle node_modules, Python packages, etc.
    const possiblePaths = [
      path.join(projectRoot, importName),
      path.join(projectRoot, 'node_modules', importName),
      // Add more paths as needed
    ];
    
    return possiblePaths.filter(p => fs.existsSync(p));
  }
}

/**
 * Identifies Python dependencies
 * @param sourcePath Source file path
 * @param sourceAnalysis Analysis result for source file
 * @param fileAnalysisResults All file analysis results
 * @param projectRoot Project root directory
 * @param pathToKeyInfo Map from normalized paths to KeyInfo objects
 * @returns List of (dependency_path, dependency_character) tuples
 */
function _identifyPythonDependencies(
  sourcePath: string,
  sourceAnalysis: any,
  fileAnalysisResults: { [key: string]: any },
  projectRoot: string,
  pathToKeyInfo: { [key: string]: KeyInfo }
): Array<[string, string]> {
  const dependencies: Array<[string, string]> = [];
  const imports = sourceAnalysis.imports || [];
  const sourceDir = path.dirname(sourcePath);
  
  for (const importName of imports) {
    // Handle relative imports
    if (importName.startsWith('.')) {
      const possiblePaths = _convertImportToPath(
        importName,
        sourceDir,
        projectRoot,
        true,
        importName.split('').filter((c: string) => c === '.').length
      );
      
      for (const possiblePath of possiblePaths) {
        if (fileAnalysisResults[possiblePath]) {
          dependencies.push([possiblePath, '>']);
          break;
        }
      }
    } else {
      // Handle absolute imports
      // This is simplified compared to Python version
      const parts = importName.split('.');
      const possiblePaths = [];
      
      let currentPath = '';
      for (let i = 0; i < parts.length; i++) {
        currentPath = currentPath ? `${currentPath}.${parts[i]}` : parts[i];
        possiblePaths.push(currentPath);
      }
      
      for (const possibleName of possiblePaths) {
        const possibleImportPaths = _convertImportToPath(possibleName, sourceDir, projectRoot);
        
        for (const possiblePath of possibleImportPaths) {
          if (fileAnalysisResults[possiblePath]) {
            dependencies.push([possiblePath, '>']);
            break;
          }
        }
      }
    }
  }
  
  return dependencies;
}

/**
 * Identifies JavaScript/TypeScript dependencies
 * @param sourcePath Source file path
 * @param sourceAnalysis Analysis result for source file
 * @param fileAnalyses All file analysis results
 * @param projectRoot Project root directory
 * @param pathToKeyInfo Map from normalized paths to KeyInfo objects
 * @returns List of (dependency_path, dependency_character) tuples
 */
function _identifyJavaScriptDependencies(
  sourcePath: string,
  sourceAnalysis: any,
  fileAnalyses: { [key: string]: any },
  projectRoot: string,
  pathToKeyInfo: { [key: string]: KeyInfo }
): Array<[string, string]> {
  const dependencies: Array<[string, string]> = [];
  const imports = sourceAnalysis.imports || [];
  const sourceDir = path.dirname(sourcePath);
  
  for (const importName of imports) {
    // Handle relative imports
    if (importName.startsWith('.')) {
      const possiblePaths = _convertImportToPath(importName, sourceDir, projectRoot);
      
      for (const possiblePath of possiblePaths) {
        if (fileAnalyses[possiblePath]) {
          dependencies.push([possiblePath, '>']);
          break;
        }
      }
    } else {
      // Handle absolute imports
      // This is simplified compared to Python version
      const possibleImportPaths = _convertImportToPath(importName, sourceDir, projectRoot);
      
      for (const possiblePath of possibleImportPaths) {
        if (fileAnalyses[possiblePath]) {
          dependencies.push([possiblePath, '>']);
          break;
        }
      }
    }
  }
  
  return dependencies;
}

/**
 * Identifies Markdown/documentation dependencies
 * @param sourcePath Source file path
 * @param sourceAnalysis Analysis result for source file
 * @param fileAnalyses All file analysis results
 * @param projectRoot Project root directory
 * @param pathToKeyInfo Map from normalized paths to KeyInfo objects
 * @returns List of (dependency_path, dependency_character) tuples
 */
function _identifyMarkdownDependencies(
  sourcePath: string,
  sourceAnalysis: any,
  fileAnalyses: { [key: string]: any },
  projectRoot: string,
  pathToKeyInfo: { [key: string]: KeyInfo }
): Array<[string, string]> {
  const dependencies: Array<[string, string]> = [];
  const links = sourceAnalysis.links || [];
  const sourceDir = path.dirname(sourcePath);
  
  for (const link of links) {
    const url = link.url;
    if (!url) continue;
    
    // Resolve relative URL to absolute path
    const resolvedPath = resolveRelativePath(url, sourceDir);
    if (!resolvedPath) continue;
    
    const normResolvedPath = normalizePath(resolvedPath);
    
    // Check if this is a known file
    if (fileAnalyses[normResolvedPath]) {
      dependencies.push([normResolvedPath, 'd']);
    }
  }
  
  return dependencies;
} 