/**
 * Dependency Analyzer
 * 
 * This module provides functionality for analyzing dependencies between files in a project.
 * It can analyze different types of files (JavaScript, TypeScript, Python, Markdown, etc.)
 * and identify imports, function calls, and other relationships.
 */

import * as fs from 'fs';
import * as path from 'path';
import { ConfigManager } from '../utils/config-manager';
import { normalizePath, getFileType, isSubpath, getProjectRoot } from '../utils/path-utils';
import { DependencySystemError, AnalysisError } from '../core/exceptions';
import { cached, invalidateDependentEntries } from '../utils/cache-manager';

// Regular expressions for import detection (matching Python version)
const PYTHON_IMPORT_PATTERN = /^\s*from\s+([.\w]+)\s+import\s+(?:\(|\*|\w+)/gm;
const PYTHON_IMPORT_MODULE_PATTERN = /^\s*import\s+([.\w]+(?:\s*,\s*[.\w]+)*)/gm;
const JAVASCRIPT_IMPORT_PATTERN = /import(?:["\'\s]*(?:[\w*{}\n\r\s,]+)from\s*)?["\']([^"\']+)["\']|\brequire\s*\(\s*["\']([^"\']+)["\']\s*\)|import\s*\(\s*["\']([^"\']+)["\']\s*\)/g;
const MARKDOWN_LINK_PATTERN = /\[(?:[^\]]+)\]\(([^)]+)\)/g;
const HTML_A_HREF_PATTERN = /<a\s+(?:[^>]*?\s+)?href=(["\'])(?<url>[^"\']+?)\1/gi;
const HTML_SCRIPT_SRC_PATTERN = /<script\s+(?:[^>]*?\s+)?src=(["\'])(?<url>[^"\']+?)\1/gi;
const HTML_LINK_HREF_PATTERN = /<link\s+(?:[^>]*?\s+)?href=(["\'])(?<url>[^"\']+?)\1/gi;
const HTML_IMG_SRC_PATTERN = /<img\s+(?:[^>]*?\s+)?src=(["\'])(?<url>[^"\']+?)\1/gi;
const CSS_IMPORT_PATTERN = /@import\s+(?:url\s*\(\s*)?["\']?([^"\')\s]+[^"\')]*?)["\']?(?:\s*\))?;/gi;

/**
 * Analyzes a file for dependencies
 * Matches Python version's analyze_file function
 * 
 * @param filePath Path to the file to analyze
 * @param force If true, bypass the cache for this specific file analysis
 * @returns Analysis result with detected dependencies or error/skipped status
 */
export function analyzeFile(filePath: string, force: boolean = false): any {
  const normFilePath = normalizePath(filePath);
  
  if (!fs.existsSync(normFilePath) || !fs.statSync(normFilePath).isFile()) {
    return { error: "File not found or not a file" };
  }
  
  const configManager = ConfigManager.getInstance();
  const projectRoot = getProjectRoot();
  const excludedDirsRel = configManager.get<string[]>('exclude.dirs', []);
  const excludedPathsRel = configManager.get<string[]>('exclude.paths', []);
  const excludedExtensions = new Set(configManager.get<string[]>('excluded_extensions', []));
  
  const excludedDirsAbs = new Set(excludedDirsRel.map(p => normalizePath(path.join(projectRoot, p))));
  const excludedPathsAbs = new Set(excludedPathsRel.map(p => normalizePath(path.join(projectRoot, p))));
  
  // Check exclusions
  if (
    [...excludedDirsAbs, ...excludedPathsAbs].some(excluded => isSubpath(normFilePath, excluded)) ||
    excludedExtensions.has(path.extname(normFilePath).toLowerCase().substring(1)) ||
    path.basename(normFilePath).endsWith("_module.md")
  ) {
    return { skipped: true, reason: "Excluded path, extension, or tracker file" };
  }
  
  try {
    const fileType = getFileType(normFilePath);
    const analysisResult: any = {
      file_path: normFilePath,
      file_type: fileType,
      imports: [],
      links: []
    };
    
    try {
      const content = fs.readFileSync(normFilePath, 'utf8');
      
      if (fileType === "py") {
        _analyzePythonFile(normFilePath, content, analysisResult);
      } else if (fileType === "js" || fileType === "ts") {
        _analyzeJavaScriptFile(normFilePath, content, analysisResult);
      } else if (fileType === "md") {
        _analyzeMarkdownFile(normFilePath, content, analysisResult);
      } else if (fileType === "html") {
        _analyzeHtmlFile(normFilePath, content, analysisResult);
      } else if (fileType === "css") {
        _analyzeCssFile(normFilePath, content, analysisResult);
      }
      
      analysisResult.size = fs.statSync(normFilePath).size;
      return analysisResult;
    } catch (error: any) {
      if (error.code === 'ENOENT') {
        return { error: "File disappeared during analysis" };
      }
      if (error instanceof SyntaxError) {
        return { error: "Syntax error", details: error.message };
      }
      return { error: "File read error", details: error.message };
    }
  } catch (error: any) {
    return { error: "Unexpected analysis error", details: error.message };
  }
}

/**
 * Analyzes Python file content using regex
 * @param filePath Path to the file
 * @param content File content
 * @param result Analysis result object to be populated
 */
function _analyzePythonFile(filePath: string, content: string, result: any): void {
  result.imports = [];
  result.functions = [];
  result.classes = [];
  result.calls = [];
  result.attribute_accesses = [];
  result.inheritance = [];
  
  // This is a simplified version as we can't use Python's AST
  // Extract imports
  let match;
  while ((match = PYTHON_IMPORT_PATTERN.exec(content)) !== null) {
    result.imports.push(match[1]);
  }
  
  while ((match = PYTHON_IMPORT_MODULE_PATTERN.exec(content)) !== null) {
    const modules = match[1].split(',').map(m => m.trim());
    result.imports.push(...modules);
  }
  
  // Extract functions (simplified)
  const funcPattern = /def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g;
  while ((match = funcPattern.exec(content)) !== null) {
    result.functions.push({
      name: match[1],
      line: content.substring(0, match.index).split('\n').length
    });
  }
  
  // Extract classes (simplified)
  const classPattern = /class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(([^)]*)\))?:/g;
  while ((match = classPattern.exec(content)) !== null) {
    result.classes.push({
      name: match[1],
      line: content.substring(0, match.index).split('\n').length
    });
    
    // Extract inheritance (simplified)
    if (match[2]) {
      const bases = match[2].split(',').map(b => b.trim());
      for (const base of bases) {
        if (base) {
          result.inheritance.push({
            class_name: match[1],
            base_class_name: base,
            potential_source: base,
            line: content.substring(0, match.index).split('\n').length
          });
        }
      }
    }
  }
}

/**
 * Analyzes JavaScript or TypeScript file content using regex
 * @param filePath Path to the file
 * @param content File content
 * @param result Analysis result object to be populated
 */
function _analyzeJavaScriptFile(filePath: string, content: string, result: any): void {
  result.imports = [];
  result.functions = [];
  result.classes = [];
  
  // Extract imports
  let match;
  while ((match = JAVASCRIPT_IMPORT_PATTERN.exec(content)) !== null) {
    const importPath = match[1] || match[2] || match[3];
    if (importPath) {
      result.imports.push(importPath);
    }
  }
  
  // Extract functions
  const funcPattern = /(?:async\s+)?function\s*\*?\s*([a-zA-Z_$][\w$]*)\s*\([^)]*\)/g;
  while ((match = funcPattern.exec(content)) !== null) {
    result.functions.push({
      name: match[1],
      line: content.substring(0, match.index).split('\n').length
    });
  }
  
  // Extract arrow functions
  const arrowPattern = /(?:const|let|var)\s+([a-zA-Z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>/g;
  while ((match = arrowPattern.exec(content)) !== null) {
    result.functions.push({
      name: match[1],
      line: content.substring(0, match.index).split('\n').length,
      type: "arrow"
    });
  }
  
  // Extract classes
  const classPattern = /class\s+([a-zA-Z_$][\w$]*)/g;
  while ((match = classPattern.exec(content)) !== null) {
    result.classes.push({
      name: match[1],
      line: content.substring(0, match.index).split('\n').length
    });
  }
}

/**
 * Analyzes Markdown file content
 * @param filePath Path to the file
 * @param content File content
 * @param result Analysis result object to be populated
 */
function _analyzeMarkdownFile(filePath: string, content: string, result: any): void {
  result.links = [];
  result.code_blocks = [];
  
  // Extract links
  let match;
  while ((match = MARKDOWN_LINK_PATTERN.exec(content)) !== null) {
    const url = match[1];
    if (url && !url.startsWith('#') && !url.startsWith('http:') && 
        !url.startsWith('https:') && !url.startsWith('mailto:') && 
        !url.startsWith('tel:')) {
      result.links.push({
        url: url,
        line: content.substring(0, match.index).split('\n').length
      });
    }
  }
  
  // Extract code blocks
  const codeBlockPattern = /```(\w+)?\n(.*?)```/gs;
  while ((match = codeBlockPattern.exec(content)) !== null) {
    const lang = match[1] || "text";
    result.code_blocks.push({
      language: lang.toLowerCase(),
      line: content.substring(0, match.index).split('\n').length
    });
  }
}

/**
 * Analyzes HTML file content
 * @param filePath Path to the file
 * @param content File content
 * @param result Analysis result object to be populated
 */
function _analyzeHtmlFile(filePath: string, content: string, result: any): void {
  result.links = [];
  result.scripts = [];
  result.stylesheets = [];
  result.images = [];
  
  // Helper function to extract resources
  function findResources(pattern: RegExp, typeList: any[]) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const url = match.groups?.url;
      if (url && !url.startsWith('#') && !url.startsWith('http:') && 
          !url.startsWith('https:') && !url.startsWith('mailto:') && 
          !url.startsWith('tel:') && !url.startsWith('data:')) {
        typeList.push({
          url: url,
          line: content.substring(0, match.index).split('\n').length
        });
      }
    }
  }
  
  findResources(HTML_A_HREF_PATTERN, result.links);
  findResources(HTML_SCRIPT_SRC_PATTERN, result.scripts);
  findResources(HTML_IMG_SRC_PATTERN, result.images);
  
  // Extract stylesheets (need special handling for rel="stylesheet")
  const linkTagPattern = /<link([^>]+)>/gi;
  const hrefPattern = /href=(["\'])(?<url>[^"\']+?)\1/i;
  const relPattern = /rel=(["\'])stylesheet\1/i;
  
  let match;
  while ((match = linkTagPattern.exec(content)) !== null) {
    const tagContent = match[1];
    const hrefMatch = hrefPattern.exec(tagContent);
    const relMatch = relPattern.exec(tagContent);
    
    if (hrefMatch && relMatch) {
      const url = hrefMatch.groups?.url;
      if (url && !url.startsWith('#') && !url.startsWith('http:') && 
          !url.startsWith('https:') && !url.startsWith('mailto:') && 
          !url.startsWith('tel:') && !url.startsWith('data:')) {
        result.stylesheets.push({
          url: url,
          line: content.substring(0, match.index).split('\n').length
        });
      }
    }
  }
}

/**
 * Analyzes CSS file content
 * @param filePath Path to the file
 * @param content File content
 * @param result Analysis result object to be populated
 */
function _analyzeCssFile(filePath: string, content: string, result: any): void {
  result.imports = [];
  
  let match;
  while ((match = CSS_IMPORT_PATTERN.exec(content)) !== null) {
    const url = match[1];
    if (url && !url.startsWith('#') && !url.startsWith('http:') && 
        !url.startsWith('https:') && !url.startsWith('data:')) {
      result.imports.push({
        url: url.trim(),
        line: content.substring(0, match.index).split('\n').length
      });
    }
  }
} 