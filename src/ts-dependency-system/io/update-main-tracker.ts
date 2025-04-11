/**
 * IO module for main tracker specific data, including key filtering
 * and dependency aggregation logic using contextual keys.
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import { KeyInfo, sortKeyStringsHierarchically } from '../core/key-manager';
import { ConfigManager } from '../utils/config-manager';
import { isSubpath, normalizePath, joinPaths } from '../utils/path-utils';
import { decompress, PLACEHOLDER_CHAR, DIAGONAL_CHAR } from '../core/dependency-grid';
import { getTrackerPath, readTrackerFile } from './tracker-io';

// Logger
const logger = console;

// Type definition for dependency suggestions
export type DependencySuggestion = [string, string]; // [targetKey, depChar]

/**
 * Gets the path to the main tracker file (module_relationship_tracker.md).
 * 
 * @param projectRoot Absolute path to the project root
 * @returns Path to the main tracker file
 */
export function getMainTrackerPath(projectRoot: string): string {
  const configManager = ConfigManager.getInstance();
  
  // Default relative path, can be overridden in .clinerules
  const memoryDirRel = configManager.getPath("memory_dir", "cline_docs/memory");
  const memoryDirAbs = joinPaths(projectRoot, memoryDirRel);
  
  // Use get_path for the filename as well, providing a default
  const trackerFilename = configManager.getPath("main_tracker_filename", "module_relationship_tracker.md");
  // Ensure tracker_filename is just the filename, not potentially a nested path
  const baseFilename = path.basename(trackerFilename);
  
  return joinPaths(memoryDirAbs, baseFilename);
}

/**
 * Logic for determining which modules (directories represented by KeyInfo)
 * to include in the main tracker. Includes only directories within configured code roots.
 * 
 * @param projectRoot Absolute path to the project root
 * @param pathToKeyInfo The global map from normalized paths to KeyInfo objects
 * @returns A dictionary mapping the normalized path of each filtered module (directory) to its corresponding KeyInfo object
 */
export function mainKeyFilter(
  projectRoot: string,
  pathToKeyInfo: Record<string, KeyInfo>
): Record<string, KeyInfo> {
  const configManager = ConfigManager.getInstance();
  const rootDirectoriesRel: string[] = configManager.getCodeRootDirectories();
  const filteredModules: Record<string, KeyInfo> = {}; // {norm_path: KeyInfo}
  
  // Normalize project root path
  const normalizedProjectRoot = normalizePath(projectRoot);
  
  // Get absolute paths for all code roots
  const absCodeRoots: Set<string> = new Set(
    rootDirectoriesRel.map(dir => normalizePath(path.join(normalizedProjectRoot, dir)))
  );
  
  if (absCodeRoots.size === 0) {
    logger.warn("No code root directories defined for main tracker key filtering.");
    return {};
  }
  
  // Iterate through all KeyInfo objects
  for (const [normPath, keyInfo] of Object.entries(pathToKeyInfo)) {
    // Check if the path represents a directory
    if (keyInfo.isDirectory) {
      // Check if the directory is equal to or within any of the code roots
      if (Array.from(absCodeRoots).some(rootDir => normPath === rootDir || isSubpath(normPath, rootDir))) {
        filteredModules[normPath] = keyInfo; // Add the KeyInfo object
      }
    }
  }
  
  logger.info(`Main key filter selected ${Object.keys(filteredModules).length} module paths for the main tracker.`);
  return filteredModules;
}

/**
 * Helper to get all descendant paths (INCLUDING self) for hierarchical check.
 * 
 * @param parentPath The parent path to find descendants for
 * @param hierarchy Map of parent paths to their direct children
 * @returns Set of all descendant paths including the parent path
 */
function _getDescendantsPaths(parentPath: string, hierarchy: Record<string, string[]>): Set<string> {
  // Ensure paths are normalized
  const normParentPath = normalizePath(parentPath);
  const descendants = new Set<string>([normParentPath]);
  
  // Use a proper queue for BFS
  const queue: string[] = (hierarchy[normParentPath] || []).map(p => normalizePath(p));
  const processed = new Set<string>([normParentPath]);
  
  while (queue.length > 0) {
    const childPath = queue.shift()!; // BFS style
    
    if (!processed.has(childPath)) {
      descendants.add(childPath);
      processed.add(childPath);
      
      // Add grandchildren (normalized) to the queue
      const grandchildren = (hierarchy[childPath] || []).map(p => normalizePath(p));
      queue.push(...grandchildren);
    }
  }
  
  return descendants;
}

/**
 * Aggregates dependencies from mini-trackers to the main tracker,
 * using paths as primary identifiers and handling contextual keys. Includes
 * hierarchical rollup.
 * 
 * @param projectRoot Absolute path to the project root
 * @param pathToKeyInfo Global mapping of normalized paths to KeyInfo objects
 * @param filteredModules The paths and KeyInfo for modules (directories) in the main tracker
 * @param fileToModule Mapping from normalized file paths to their containing module's normalized path
 * @returns A dictionary where keys are source module keys and values are lists of (target_module_key, aggregated_dependency_char) tuples
 */
export async function aggregateDependenciesContextual(
  projectRoot: string,
  pathToKeyInfo: Record<string, KeyInfo>,
  filteredModules: Record<string, KeyInfo>,
  fileToModule?: Record<string, string>
): Promise<Record<string, DependencySuggestion[]>> {
  if (!fileToModule) {
    logger.error("File-to-module mapping missing, cannot perform main tracker aggregation.");
    return {};
  }
  
  if (Object.keys(filteredModules).length === 0) {
    logger.warn("No module paths/keys provided for main tracker aggregation.");
    return {};
  }
  
  const configManager = ConfigManager.getInstance();
  const getCharPriority = (char: string): number => {
    const priorities: Record<string, number> = {
      'x': 5, // Mutual dependency (highest)
      '<': 4, // Source depends on target
      '>': 3, // Target depends on source
      'd': 2, // Document dependency
      's': 1, // Semantic dependency
      'n': 0, // No dependency (validated)
      'p': -1 // Placeholder (unvalidated, lowest priority)
    };
    return priorities[char] || -1;
  };
  
  // Stores source_module_path -> target_module_path -> (highest_priority_char, highest_priority)
  const aggregatedDepsPrio: Record<string, Record<string, [string, number]>> = {};
  
  logger.info(`Starting aggregation for ${Object.keys(filteredModules).length} main tracker modules...`);
  
  // --- Step 1: Gather direct foreign dependencies from all relevant mini-trackers ---
  let processedMiniTrackers = 0;
  
  // Iterate through the modules designated for the main tracker
  for (const [sourceModulePath, _] of Object.entries(filteredModules)) {
    // Paths in filteredModules should already be normalized
    const normSourceModulePath = sourceModulePath;
    const miniTrackerPath = await getTrackerPath(projectRoot, 'mini', normSourceModulePath);
    
    try {
      await fs.access(miniTrackerPath);
    } catch (error) {
      // Mini tracker doesn't exist, skip
      continue;
    }
    
    processedMiniTrackers++;
    
    try {
      // read_tracker_file returns data based on the *file content*, keys are strings
      const miniData = await readTrackerFile(miniTrackerPath);
      const miniGrid = miniData.grid;
      
      // Key definitions LOCAL to this mini-tracker: {key_string: path_string}
      const miniKeysDefinedRaw = miniData.keys;
      
      // Normalize paths defined in the mini-tracker for consistent lookup
      const miniKeysDefined: Record<string, string> = {};
      for (const [key, pathStr] of Object.entries(miniKeysDefinedRaw)) {
        miniKeysDefined[key] = normalizePath(pathStr);
      }
      
      if (Object.keys(miniGrid).length === 0 || Object.keys(miniKeysDefined).length === 0) {
        logger.debug(`Mini tracker ${path.basename(miniTrackerPath)} grid/keys empty.`);
        continue;
      }
      
      // Get the list of key strings defined in this mini-tracker and sort them
      const miniGridKeyStrings = sortKeyStringsHierarchically(Object.keys(miniKeysDefined));
      
      const keyStringToIdxMini: Record<string, number> = {};
      miniGridKeyStrings.forEach((key, index) => {
        keyStringToIdxMini[key] = index;
      });
      
      // Iterate through rows (sources) of the mini-tracker grid using key strings
      for (const [miniSourceKeyString, compressedRow] of Object.entries(miniGrid)) {
        if (!(miniSourceKeyString in keyStringToIdxMini)) continue;
        
        // Find the path corresponding to the key string *within this mini-tracker*
        const miniSourcePath = miniKeysDefined[miniSourceKeyString];
        if (!miniSourcePath) continue; // Path must be defined locally
        
        // Determine the module the source path belongs to using the global map
        const actualSourceModulePath = fileToModule[miniSourcePath];
        if (!actualSourceModulePath) {
          // Not in file_to_module map
          continue;
        }
        
        // IMPORTANT CHECK: Aggregate only if the source's module *is* the module this mini-tracker represents
        if (actualSourceModulePath !== normSourceModulePath) {
          continue;
        }
        
        // Process the columns (targets) for this valid source row
        try {
          const decompressedRow = decompress(compressedRow);
          
          if (decompressedRow.length !== miniGridKeyStrings.length) {
            logger.warn(`Row length mismatch for '${miniSourceKeyString}' in ${miniTrackerPath}.`);
            continue;
          }
          
          for (let colIdx = 0; colIdx < decompressedRow.length; colIdx++) {
            const depChar = decompressedRow[colIdx];
            
            // Skip placeholders and diagonal entries
            if (depChar === PLACEHOLDER_CHAR || depChar === DIAGONAL_CHAR) continue;
            
            const miniTargetKeyString = miniGridKeyStrings[colIdx];
            
            // Find the path for the target key string defined locally
            const targetPath = miniKeysDefined[miniTargetKeyString];
            if (!targetPath) continue; // Target path must be defined locally
            
            // Find the module the target path belongs to using the global map
            const targetModulePath = fileToModule[targetPath];
            if (!targetModulePath) {
              continue;
            }
            
            // --- Check for FOREIGN relationship (source module != target module) ---
            if (targetModulePath !== actualSourceModulePath) {
              // Use module paths as keys in aggregated_deps_prio
              const currentPriority = getCharPriority(depChar);
              
              // Initialize if needed
              if (!aggregatedDepsPrio[actualSourceModulePath]) {
                aggregatedDepsPrio[actualSourceModulePath] = {};
              }
              
              const stored = aggregatedDepsPrio[actualSourceModulePath][targetModulePath] || [PLACEHOLDER_CHAR, -1];
              const [_storedChar, storedPriority] = stored;
              
              if (currentPriority > storedPriority) {
                aggregatedDepsPrio[actualSourceModulePath][targetModulePath] = [depChar, currentPriority];
              }
            }
          }
        } catch (error) {
          logger.error(`Error processing mini-tracker grid row: ${error}`);
        }
      }
    } catch (error) {
      logger.error(`Error processing mini-tracker ${miniTrackerPath}: ${error}`);
    }
  }
  
  logger.info(`Processed ${processedMiniTrackers} mini-trackers for dependency aggregation.`);
  
  // --- Step 2: Convert aggregated dependencies to the output format ---
  const result: Record<string, DependencySuggestion[]> = {};
  
  for (const [sourcePath, targets] of Object.entries(aggregatedDepsPrio)) {
    // Get the key for this source module path
    const sourceModuleKeyInfo = pathToKeyInfo[sourcePath];
    if (!sourceModuleKeyInfo) continue;
    
    const sourceKey = sourceModuleKeyInfo.keyString;
    result[sourceKey] = [];
    
    for (const [targetPath, [depChar, _]] of Object.entries(targets)) {
      // Get the key for this target module path
      const targetModuleKeyInfo = pathToKeyInfo[targetPath];
      if (!targetModuleKeyInfo) continue;
      
      const targetKey = targetModuleKeyInfo.keyString;
      result[sourceKey].push([targetKey, depChar]);
    }
  }
  
  return result;
}

/**
 * Data structure for main tracker
 */
export const mainTrackerData = {
  getTrackerPath: getMainTrackerPath,
  mainKeyFilter: mainKeyFilter,
  aggregateDependencies: aggregateDependenciesContextual
}; 