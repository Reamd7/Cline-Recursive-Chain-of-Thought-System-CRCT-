/**
 * IO module for doc tracker specific data using contextual keys.
 */

import * as path from 'path';
import * as fs from 'fs/promises';
import { KeyInfo } from '../core/key-manager';
import { ConfigManager } from '../utils/config-manager';
import { isSubpath, normalizePath, joinPaths } from '../utils/path-utils';

// Logger
const logger = console;

/**
 * Logic for determining which files/dirs (represented by KeyInfo) to include
 * in the doc tracker based on configured documentation directories.
 * 
 * @param projectRoot Absolute path to the project root
 * @param pathToKeyInfo The global map from normalized paths to KeyInfo objects
 * @returns A dictionary mapping the normalized path of each filtered item to its corresponding KeyInfo object
 */
export function docFileInclusionLogic(
  projectRoot: string,
  pathToKeyInfo: Record<string, KeyInfo>
): Record<string, KeyInfo> {
  const configManager = ConfigManager.getInstance();
  const docDirectoriesRel: string[] = configManager.getDocDirectories();
  const filteredItems: Record<string, KeyInfo> = {}; // {norm_path: KeyInfo}
  
  // Normalize project root to ensure consistent path handling
  const normalizedProjectRoot = normalizePath(projectRoot);
  
  // Get absolute paths for all doc directories
  const absDocRoots: string[] = docDirectoriesRel.map(
    dir => normalizePath(path.join(normalizedProjectRoot, dir))
  );
  
  if (absDocRoots.length === 0) {
    logger.warn("No documentation directories configured for doc tracker filtering.");
    return {};
  }
  
  // Iterate through all KeyInfo objects
  for (const [normPath, keyInfo] of Object.entries(pathToKeyInfo)) {
    // Check if the item's path is equal to or within any of the configured doc roots
    if (absDocRoots.some(docRoot => normPath === docRoot || isSubpath(normPath, docRoot))) {
      filteredItems[normPath] = keyInfo; // Add the KeyInfo object
    }
  }
  
  logger.info(`Doc tracker filter selected ${Object.keys(filteredItems).length} items.`);
  return filteredItems;
}

/**
 * Gets the path to the doc tracker file.
 * 
 * @param projectRoot Absolute path to the project root
 * @returns Path to the doc tracker file
 */
export function getDocTrackerPath(projectRoot: string): string {
  const configManager = ConfigManager.getInstance();
  
  // Default relative path, can be overridden in .clinerules
  const memoryDirRel = configManager.getPath("memory_dir", "cline_docs/memory");
  const memoryDirAbs = joinPaths(projectRoot, memoryDirRel);
  
  // Use get_path for the filename as well, providing a default
  const trackerFilename = configManager.getPath("doc_tracker_filename", "doc_tracker.md");
  // Ensure just filename
  const baseFilename = path.basename(trackerFilename); 
  
  return joinPaths(memoryDirAbs, baseFilename);
}

/**
 * Data structure for doc tracker
 */
export const docTrackerData = {
  // File inclusion logic for filtering paths
  fileInclusion: docFileInclusionLogic,
  // Function to get the path to the doc tracker file
  getTrackerPath: getDocTrackerPath
}; 