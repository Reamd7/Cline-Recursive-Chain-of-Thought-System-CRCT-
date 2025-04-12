/**
 * Project Analyzer
 * 
 * This module provides functionality for analyzing an entire project,
 * including file dependency analysis, embedding generation, and dependency suggestions.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as glob from 'glob';
import { ConfigManager } from '../utils/config-manager';
import { normalizePath, isSubpath, getFileType, getProjectRoot } from '../utils/path-utils';
import { DependencySystemError, AnalysisError } from '../core/exceptions';
import { analyzeFile } from './dependency-analyzer';
import { suggestDependencies } from './dependency-suggester';
import { batchProcessEmbeddings } from './embedding-manager';
import { updateTracker } from '../io/tracker-io';
import { generateKeys, getKeyFromPath, KeyInfo } from '../core/key-manager';
import { processItems } from '../utils/batch-processor';

import * as logging from '../utils/logging';
const logger = logging.getLogger('project-analyzer');

/**
 * Analyzes an entire project
 * Matches Python version's analyze_project function
 * 
 * @param forceAnalysis Bypass cache and force reanalysis of files
 * @param forceEmbeddings Force regeneration of embeddings
 * @returns Object containing project-wide analysis results and status
 */
export async function analyzeProject(
  forceAnalysis: boolean = false,
  forceEmbeddings: boolean = false
): Promise<any> {
  // Initial setup
  const config = ConfigManager.getInstance();
  const projectRoot = getProjectRoot();
  logger.info(`Starting project analysis in directory: ${projectRoot}`);

  const results: any = {
    status: "success",
    message: "",
    tracker_initialization: {},
    embedding_generation: {},
    dependency_suggestion: {},
    tracker_update: {},
    file_analysis: {} // Store results keyed by normalized absolute path
  };

  // Exclusion setup
  const excludedDirsRel = config.get<string[]>('exclude.dirs', []);
  const excludedPathsRel = config.get<string[]>('exclude.paths', []);
  const excludedExtensions = new Set(config.get<string[]>('excluded_extensions', []));
  const excludedFilePatterns = config.get<string[]>('excluded_file_patterns', []);
  
  const excludedDirsAbs = new Set(excludedDirsRel.map(p => normalizePath(path.join(projectRoot, p))));
  const excludedPathsAbs = new Set(excludedPathsRel.map(p => normalizePath(path.join(projectRoot, p))));
  const allExcludedPathsAbs = [...excludedDirsAbs, ...excludedPathsAbs];

  // Early exit if project root itself is excluded
  const normProjectRoot = normalizePath(projectRoot);
  if (allExcludedPathsAbs.some(excludedPath => 
      normProjectRoot === excludedPath || 
      normProjectRoot.startsWith(excludedPath + path.sep))) {
    logger.info(`Skipping analysis of excluded project root: ${projectRoot}`);
    results.status = "skipped";
    results.message = "Project root is excluded";
    return results;
  }

  // Root directories setup
  const codeRootDirectoriesRel = config.get<string[]>('code_root_directories', []);
  const docDirectoriesRel = config.get<string[]>('doc_directories', []);
  
  // Combine unique roots
  const allRootsRel = [...new Set([...codeRootDirectoriesRel, ...docDirectoriesRel])];

  // Sort the relative root paths alphabetically to ensure stable order
  allRootsRel.sort();
  logger.debug(`Processing root directories in stable order: ${allRootsRel.join(', ')}`);

  if (codeRootDirectoriesRel.length === 0) {
    logger.error("No code root directories configured.");
    results.status = "error";
    results.message = "No code root directories configured.";
    return results;
  }
  
  if (docDirectoriesRel.length === 0) {
    logger.warning("No documentation directories configured. Proceeding without doc analysis.");
  }

  const absCodeRoots = new Set(codeRootDirectoriesRel.map(r => normalizePath(path.join(projectRoot, r))));
  const absDocRoots = new Set(docDirectoriesRel.map(r => normalizePath(path.join(projectRoot, r))));
  const absAllRoots = new Set(allRootsRel.map(r => normalizePath(path.join(projectRoot, r))));

  // Key generation
  logger.info("Generating keys...");
  let pathToKeyInfo: { [key: string]: KeyInfo } = {};
  let newlyGeneratedKeys: KeyInfo[] = [];

  try {
    const keyGenerationResult = await generateKeys(
      allRootsRel,
      {
        excludedDirs: excludedDirsRel,
        excludedExtensions: Array.from(excludedExtensions),
        excludedPaths: excludedPathsRel
      }
    );
    
    pathToKeyInfo = keyGenerationResult.pathToKeyInfo;
    newlyGeneratedKeys = keyGenerationResult.newKeys;
    
    results.tracker_initialization.key_generation = "success";
    logger.info(`Generated keys for ${Object.keys(pathToKeyInfo).length} files/dirs.`);
    
    if (newlyGeneratedKeys.length > 0) {
      logger.info(`Assigned ${newlyGeneratedKeys.length} new keys.`);
    }
  } catch (error: any) {
    results.status = "error";
    results.message = `Key generation failed: ${error.message}`;
    logger.error(results.message);
    return results;
  }

  // Create file-to-module mapping
  logger.info("Creating file-to-module mapping...");
  const fileToModule: { [key: string]: string } = {};
  
  for (const keyInfo of Object.values(pathToKeyInfo)) {
    if (!keyInfo.is_directory && keyInfo.parent_path) {
      fileToModule[keyInfo.norm_path] = keyInfo.parent_path;
    }
  }
  
  logger.info(`File-to-module mapping created with ${Object.keys(fileToModule).length} entries.`);

  // File identification and filtering
  logger.info("Identifying files for analysis...");
  const filesToAnalyzeAbs: string[] = [];

  for (const absRootDir of absAllRoots) {
    if (!fs.existsSync(absRootDir)) {
      logger.warn(`Configured root directory not found: ${absRootDir}`);
      continue;
    }
    
    // Find all files in this root directory
    const findFilesInDir = (rootDir: string) => {
      try {
        const files = fs.readdirSync(rootDir, { withFileTypes: true });
        
        for (const file of files) {
          const filePath = path.join(rootDir, file.name);
          const normFilePath = normalizePath(filePath);
          
          // Skip if directory or file is excluded
          if (file.isDirectory()) {
            // Check if this directory should be excluded
            if (
              excludedDirsRel.includes(file.name) ||
              allExcludedPathsAbs.some(p => normFilePath === p || isSubpath(normFilePath, p))
            ) {
              continue;
            }
            
            // Recursively process subdirectory
            findFilesInDir(filePath);
          } else if (file.isFile()) {
            // Check if file is excluded
            const fileExt = path.extname(file.name).toLowerCase().substring(1);
            const isExcluded = 
              excludedExtensions.has(fileExt) ||
              allExcludedPathsAbs.some(p => normFilePath === p || isSubpath(normFilePath, p)) ||
              excludedFilePatterns.some(pattern => {
                const regex = new RegExp(pattern);
                return regex.test(file.name);
              }) ||
              file.name.endsWith("_module.md");
            
            if (isExcluded) {
              logger.debug(`Skipping excluded file: ${normFilePath}`);
              continue;
            }
            
            // Add file if it has a key
            if (pathToKeyInfo[normFilePath]) {
              filesToAnalyzeAbs.push(normFilePath);
            } else {
              logger.warn(`File found but no key generated: ${normFilePath}`);
            }
          }
        }
      } catch (error) {
        logger.error(`Error reading directory ${rootDir}: ${error}`);
      }
    };
    
    findFilesInDir(absRootDir);
  }

  logger.info(`Found ${filesToAnalyzeAbs.length} files to analyze.`);

  // File analysis
  logger.info("Starting file analysis...");
  const fileAnalysisResults: { [key: string]: any } = {};
  let analyzedCount = 0, skippedCount = 0, errorCount = 0;
  
  // Use batch processing for potential parallelization
  const analysisResults = await processItems(filesToAnalyzeAbs, (filePath) => {
    return analyzeFile(filePath, forceAnalysis);
  });
  
  for (let i = 0; i < filesToAnalyzeAbs.length; i++) {
    const filePath = filesToAnalyzeAbs[i];
    const result = analysisResults[i];
    
    if (result) {
      if (result.error) {
        logger.warn(`Analysis error for ${filePath}: ${result.error}`);
        errorCount++;
      } else if (result.skipped) {
        skippedCount++;
      } else {
        fileAnalysisResults[filePath] = result;
        analyzedCount++;
      }
    } else {
      logger.warn(`Analysis returned no result for ${filePath}`);
      errorCount++;
    }
  }
  
  results.file_analysis = fileAnalysisResults;
  logger.info(`File analysis complete. Analyzed: ${analyzedCount}, Skipped: ${skippedCount}, Errors: ${errorCount}`);

  // Generate embeddings
  logger.info("Generating embeddings...");
  const embeddings = await batchProcessEmbeddings(Object.keys(fileAnalysisResults), projectRoot, forceEmbeddings);
  results.embedding_generation.count = Object.keys(embeddings).length;
  logger.info(`Generated embeddings for ${Object.keys(embeddings).length} files.`);

  // Suggest dependencies
  logger.info("Suggesting dependencies...");
  const suggestedDependencies: { [key: string]: Array<[string, string]> } = {};
  
  for (const filePath of Object.keys(fileAnalysisResults)) {
    try {
      const suggestions = suggestDependencies(
        filePath,
        pathToKeyInfo,
        projectRoot,
        fileAnalysisResults
      );
      
      if (suggestions.length > 0) {
        const fileKey = getKeyFromPath(filePath, pathToKeyInfo);
        if (fileKey) {
          suggestedDependencies[fileKey] = suggestions;
        }
      }
    } catch (error: any) {
      logger.error(`Error suggesting dependencies for ${filePath}: ${error.message}`);
    }
  }
  
  results.dependency_suggestion.count = Object.keys(suggestedDependencies).length;
  logger.info(`Generated dependency suggestions for ${Object.keys(suggestedDependencies).length} files.`);

  // Update trackers
  logger.info("Updating trackers...");
  try {
    // Update module relationship tracker
    const mainTrackerPath = path.join(projectRoot, "cline_docs", "module_relationship_tracker.md");
    await updateTracker(mainTrackerPath, suggestedDependencies, pathToKeyInfo);
    results.tracker_update.main_tracker = "success";
    
    // Update doc tracker
    if (docDirectoriesRel.length > 0) {
      const docTrackerPath = path.join(projectRoot, "cline_docs", "doc_tracker.md");
      await updateTracker(docTrackerPath, suggestedDependencies, pathToKeyInfo, true);
      results.tracker_update.doc_tracker = "success";
    }
    
    logger.info("Tracker updates completed successfully.");
  } catch (error: any) {
    logger.error(`Error updating trackers: ${error.message}`);
    results.tracker_update.error = error.message;
  }

  return results;
}

/**
 * Checks if a directory is empty
 * @param dirPath Directory path
 * @returns True if empty, false otherwise
 */
function _isEmptyDir(dirPath: string): boolean {
  try {
    const files = fs.readdirSync(dirPath);
    return files.length === 0;
  } catch (error) {
    return false;
  }
} 