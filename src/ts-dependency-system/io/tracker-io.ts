/**
 * IO module for tracker file operations using contextual keys.
 * Handles reading, writing, merging and exporting tracker files.
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import * as os from 'os';
import { fileExistsSync, mkdirSync } from '../utils/path-utils';
import { ConfigManager } from '../utils/config-manager';
import { CacheManager } from '../utils/cache-manager';
import { KeyInfo, validateKey, sortKeyStringsHierarchically, getKeyFromPath } from '../core/key-manager';
import { compress, decompress, createInitialGrid, validateGrid } from '../core/dependency-grid';
import { TrackerError } from '../core/exceptions';

// Constants for grid characters
export const PLACEHOLDER_CHAR = 'p';
export const EMPTY_CHAR = 'n';
export const DIAGONAL_CHAR = 'o';

// Logger
const logger = console; // TODO: Replace with proper logger

// Type definitions
export interface TrackerData {
  keys: Record<string, string>;  // Key string -> Path string map
  grid: Record<string, string>;  // Key string -> Compressed row map
  lastKeyEdit: string;
  lastGridEdit: string;
}

// Cache manager for tracker paths and data
const cacheManager = CacheManager.getInstance();

/**
 * Get the path to the appropriate tracker file based on type.
 * 
 * @param projectRoot Project root directory
 * @param trackerType Type of tracker ('main', 'doc', or 'mini')
 * @param modulePath The module path (required for mini-trackers)
 * @returns Normalized path to the tracker file
 */
export function getTrackerPath(
  projectRoot: string, 
  trackerType: 'main' | 'doc' | 'mini' = 'main', 
  modulePath?: string
): string {
  const configManager = ConfigManager.getInstance();
  const cacheKey = `tracker_path:${projectRoot}:${trackerType}:${modulePath || 'none'}:${configManager.getConfigLastModified()}`;
  
  const cachedPath = cacheManager.get<string>(cacheKey);
  if (cachedPath) {
    return cachedPath;
  }

  let trackerPath: string;
  
  if (trackerType === 'main') {
    // Assuming these functions are imported from respective modules
    // For now, we'll implement a simplified version
    const memoryDir = configManager.getPath('memory_dir', 'cline_docs');
    const memoryDirAbs = path.join(projectRoot, memoryDir);
    const trackerFilename = configManager.getPath('main_tracker_filename', 'module_relationship_tracker.md');
    trackerPath = path.join(memoryDirAbs, path.basename(trackerFilename));
  } 
  else if (trackerType === 'doc') {
    const memoryDir = configManager.getPath('memory_dir', 'cline_docs');
    const memoryDirAbs = path.join(projectRoot, memoryDir);
    const trackerFilename = configManager.getPath('doc_tracker_filename', 'doc_tracker.md');
    trackerPath = path.join(memoryDirAbs, path.basename(trackerFilename));
  } 
  else if (trackerType === 'mini') {
    if (!modulePath) {
      throw new Error('modulePath must be provided for mini-trackers');
    }
    // For mini-trackers, use module name as the file name base
    const moduleName = path.basename(modulePath);
    trackerPath = path.join(modulePath, `${moduleName}_module.md`);
  } 
  else {
    throw new Error(`Unknown tracker type: ${trackerType}`);
  }
  
  // Normalize path to use forward slashes
  const normalizedPath = trackerPath.replace(/\\/g, '/');
  
  // Cache the result
  cacheManager.set(cacheKey, normalizedPath);
  
  return normalizedPath;
}

/**
 * Read a tracker file and parse its contents.
 * 
 * @param trackerPath Path to the tracker file
 * @returns Dictionary with keys, grid, and metadata, or empty structure on failure
 */
export async function readTrackerFile(trackerPath: string): Promise<TrackerData> {
  const normalizedPath = trackerPath.replace(/\\/g, '/');
  
  // Create cache key based on path and last modified time
  let mtime = 0;
  try {
    const stats = await fs.stat(normalizedPath);
    mtime = stats.mtimeMs;
  } catch (error) {
    // File might not exist, continue with default mtime
  }
  
  const cacheKey = `tracker_data:${normalizedPath}:${mtime}`;
  const cachedData = cacheManager.get<TrackerData>(cacheKey);
  
  if (cachedData) {
    return cachedData;
  }
  
  // Default empty structure
  const emptyResult: TrackerData = {
    keys: {},
    grid: {},
    lastKeyEdit: '',
    lastGridEdit: ''
  };
  
  // Check if file exists
  try {
    await fs.access(normalizedPath);
  } catch (error) {
    logger.debug(`Tracker file not found: ${normalizedPath}. Returning empty structure.`);
    return emptyResult;
  }
  
  try {
    // Read file content
    const content = await fs.readFile(normalizedPath, 'utf-8');
    
    // Parse keys section
    const keys: Record<string, string> = {};
    const keysSectionMatch = content.match(/---KEY_DEFINITIONS_START---\n(.*?)\n---KEY_DEFINITIONS_END---/s);
    
    if (keysSectionMatch) {
      const keysSectionContent = keysSectionMatch[1];
      const lines = keysSectionContent.split('\n');
      
      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine || trimmedLine.toLowerCase().startsWith('key definitions:')) continue;
        
        const match = trimmedLine.match(/^([a-zA-Z0-9]+)\s*:\s*(.*)$/);
        if (match) {
          const [, key, value] = match;
          if (validateKey(key)) {
            keys[key] = value.trim().replace(/\\/g, '/');
          } else {
            logger.warning(`Skipping invalid key format in ${trackerPath}: '${key}'`);
          }
        }
      }
    }
    
    // Parse grid section
    const grid: Record<string, string> = {};
    const gridSectionMatch = content.match(/---GRID_START---\n(.*?)\n---GRID_END---/s);
    
    if (gridSectionMatch) {
      const gridSectionContent = gridSectionMatch[1];
      let lines = gridSectionContent.trim().split('\n');
      
      // Skip header line if present
      if (lines.length > 0 && (lines[0].trim().toUpperCase().startsWith('X ') || lines[0].trim() === 'X')) {
        lines = lines.slice(1);
      }
      
      for (const line of lines) {
        const trimmedLine = line.trim();
        const match = trimmedLine.match(/^([a-zA-Z0-9]+)\s*=\s*(.*)$/);
        
        if (match) {
          const [, key, value] = match;
          if (validateKey(key)) {
            grid[key] = value.trim();
          } else {
            logger.warning(`Grid row key '${key}' in ${trackerPath} has invalid format. Skipping.`);
          }
        }
      }
    }
    
    // Parse metadata
    let lastKeyEdit = '';
    let lastGridEdit = '';
    
    const lastKeyEditMatch = content.match(/^last_KEY_edit\s*:\s*(.*)$/m);
    if (lastKeyEditMatch) {
      lastKeyEdit = lastKeyEditMatch[1].trim();
    }
    
    const lastGridEditMatch = content.match(/^last_GRID_edit\s*:\s*(.*)$/m);
    if (lastGridEditMatch) {
      lastGridEdit = lastGridEditMatch[1].trim();
    }
    
    const result: TrackerData = {
      keys,
      grid,
      lastKeyEdit,
      lastGridEdit
    };
    
    logger.debug(`Read tracker '${path.basename(trackerPath)}': ${Object.keys(keys).length} keys, ${Object.keys(grid).length} grid rows`);
    
    // Cache the result
    cacheManager.set(cacheKey, result);
    
    return result;
  } catch (error) {
    logger.error(`Error reading tracker file ${trackerPath}: ${error}`);
    return emptyResult;
  }
}

/**
 * Write tracker data to a file in markdown format.
 * 
 * @param trackerPath Path to the tracker file
 * @param keyDefsToWrite Dictionary of key strings to path strings
 * @param gridToWrite Dictionary of grid rows (compressed strings)
 * @param lastKeyEdit Last key edit identifier
 * @param lastGridEdit Last grid edit identifier
 * @returns True if successful, False otherwise
 */
export async function writeTrackerFile(
  trackerPath: string,
  keyDefsToWrite: Record<string, string>,
  gridToWrite: Record<string, string>,
  lastKeyEdit: string,
  lastGridEdit: string = ''
): Promise<boolean> {
  const normalizedPath = trackerPath.replace(/\\/g, '/');
  
  try {
    // Ensure directory exists
    const dirname = path.dirname(normalizedPath);
    await fs.mkdir(dirname, { recursive: true });
    
    // Sort key strings hierarchically
    const sortedKeysList = sortKeyStringsHierarchically(Object.keys(keyDefsToWrite));
    
    // Validate grid before writing
    if (!validateGrid(gridToWrite, sortedKeysList)) {
      logger.error(`Aborting write to ${trackerPath} due to grid validation failure.`);
      return false;
    }
    
    // Rebuild/Fix Grid to ensure consistency with sortedKeysList
    const finalGrid: Record<string, string> = {};
    const expectedLen = sortedKeysList.length;
    const keyToIdx = Object.fromEntries(sortedKeysList.map((key, index) => [key, index]));
    
    for (const rowKey of sortedKeysList) {
      const compressedRow = gridToWrite[rowKey];
      let rowList: string[] | null = null;
      
      if (compressedRow !== undefined) {
        try {
          const decompressedRow = decompress(compressedRow);
          if (decompressedRow.length === expectedLen) {
            rowList = Array.from(decompressedRow);
          } else {
            logger.warning(`Correcting grid row length for key '${rowKey}' in ${trackerPath} (expected ${expectedLen}, got ${decompressedRow.length}).`);
          }
        } catch (error) {
          logger.warning(`Error decompressing row for key '${rowKey}' in ${trackerPath}: ${error}. Re-initializing.`);
        }
      }
      
      if (rowList === null) {
        rowList = Array(expectedLen).fill(PLACEHOLDER_CHAR);
        const rowIdx = keyToIdx[rowKey];
        if (rowIdx !== undefined) {
          rowList[rowIdx] = DIAGONAL_CHAR;
        } else {
          logger.error(`Key '${rowKey}' not found in index map during grid rebuild!`);
        }
      }
      
      finalGrid[rowKey] = compress(rowList.join(''));
    }
    
    // Build content
    let content = '';
    
    // Write key definitions
    content += '---KEY_DEFINITIONS_START---\n';
    content += 'Key Definitions:\n';
    
    for (const key of sortedKeysList) {
      content += `${key}: ${keyDefsToWrite[key].replace(/\\/g, '/')}\n`;
    }
    
    content += '---KEY_DEFINITIONS_END---\n\n';
    
    // Write metadata
    content += `last_KEY_edit: ${lastKeyEdit}\n`;
    content += `last_GRID_edit: ${lastGridEdit}\n\n`;
    
    // Write grid
    content += '---GRID_START---\n';
    
    if (sortedKeysList.length > 0) {
      // Header row with column keys
      content += 'X ' + sortedKeysList.join(' ') + '\n';
      
      // Data rows
      for (const rowKey of sortedKeysList) {
        content += `${rowKey} = ${finalGrid[rowKey]}\n`;
      }
    }
    
    content += '---GRID_END---\n';
    
    // Write to file
    await fs.writeFile(normalizedPath, content, 'utf-8');
    
    // Invalidate cache
    const cacheKey = `tracker_data:${normalizedPath}:`;
    cacheManager.invalidatePattern(cacheKey);
    
    logger.info(`Successfully wrote tracker file: ${trackerPath}`);
    return true;
  } catch (error) {
    logger.error(`Error writing tracker file ${trackerPath}: ${error}`);
    return false;
  }
}

/**
 * Create a backup of a tracker file.
 * 
 * @param trackerPath Path to the tracker file
 * @returns Path to the backup file or empty string on failure
 */
export async function backupTrackerFile(trackerPath: string): Promise<string> {
  const normalizedPath = trackerPath.replace(/\\/g, '/');
  
  try {
    // Check if file exists
    try {
      await fs.access(normalizedPath);
    } catch (error) {
      logger.warning(`Cannot backup nonexistent file: ${normalizedPath}`);
      return '';
    }
    
    // Create backups directory if it doesn't exist
    const dirname = path.dirname(normalizedPath);
    const backupDir = path.join(dirname, 'backups');
    await fs.mkdir(backupDir, { recursive: true });
    
    // Generate backup filename with timestamp
    const filename = path.basename(normalizedPath);
    const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
    const backupFilename = `${filename}.${timestamp}.bak`;
    const backupPath = path.join(backupDir, backupFilename);
    
    // Copy file to backup location
    await fs.copyFile(normalizedPath, backupPath);
    
    logger.info(`Created backup of ${normalizedPath} at ${backupPath}`);
    return backupPath.replace(/\\/g, '/');
  } catch (error) {
    logger.error(`Error creating backup of ${trackerPath}: ${error}`);
    return '';
  }
}

/**
 * Merge two tracker files.
 * 
 * @param primaryTrackerPath Path to the primary tracker file
 * @param secondaryTrackerPath Path to the secondary tracker file
 * @param outputPath Optional output path for the merged tracker
 * @returns The merged tracker data or null on failure
 */
export async function mergeTrackers(
  primaryTrackerPath: string,
  secondaryTrackerPath: string,
  outputPath?: string
): Promise<TrackerData | null> {
  try {
    // Read both tracker files
    const primaryData = await readTrackerFile(primaryTrackerPath);
    const secondaryData = await readTrackerFile(secondaryTrackerPath);
    
    // Merge keys from both trackers
    const mergedKeys: Record<string, string> = { ...primaryData.keys };
    for (const [key, path] of Object.entries(secondaryData.keys)) {
      if (!mergedKeys[key]) {
        mergedKeys[key] = path;
      }
    }
    
    // Get sorted lists of keys
    const primaryKeysList = sortKeyStringsHierarchically(Object.keys(primaryData.keys));
    const secondaryKeysList = sortKeyStringsHierarchically(Object.keys(secondaryData.keys));
    const mergedKeysList = sortKeyStringsHierarchically(Object.keys(mergedKeys));
    
    // Merge grids
    const mergedGrid = _mergeGrids(
      primaryData.grid,
      secondaryData.grid,
      primaryKeysList,
      secondaryKeysList,
      mergedKeysList
    );
    
    // Create merged data
    const mergedData: TrackerData = {
      keys: mergedKeys,
      grid: mergedGrid,
      lastKeyEdit: `merged:${Date.now()}`,
      lastGridEdit: `merged:${Date.now()}`
    };
    
    // Write merged data to output file if specified
    if (outputPath) {
      const success = await writeTrackerFile(
        outputPath,
        mergedData.keys,
        mergedData.grid,
        mergedData.lastKeyEdit,
        mergedData.lastGridEdit
      );
      
      if (!success) {
        logger.error(`Failed to write merged tracker to ${outputPath}`);
        return null;
      }
    }
    
    return mergedData;
  } catch (error) {
    logger.error(`Error merging trackers: ${error}`);
    return null;
  }
}

/**
 * Helper function to merge grid data from two trackers.
 */
function _mergeGrids(
  primaryGrid: Record<string, string>,
  secondaryGrid: Record<string, string>,
  primaryKeysList: string[],
  secondaryKeysList: string[],
  mergedKeysList: string[]
): Record<string, string> {
  const mergedGrid: Record<string, string> = {};
  
  // Helper to safely decompress grid data
  function safeDecompress(gridData: Record<string, string>, keysList: string[], rowKey: string): string[] {
    try {
      if (gridData[rowKey]) {
        const decompressed = decompress(gridData[rowKey]);
        if (decompressed.length === keysList.length) {
          return Array.from(decompressed);
        }
      }
    } catch (error) {
      logger.warning(`Error decompressing grid row for ${rowKey}: ${error}`);
    }
    
    // Return default row with diagonal set
    const defaultRow = Array(keysList.length).fill(PLACEHOLDER_CHAR);
    const rowIndex = keysList.indexOf(rowKey);
    if (rowIndex >= 0) {
      defaultRow[rowIndex] = DIAGONAL_CHAR;
    }
    return defaultRow;
  }
  
  // Create mappings from key to index
  const primaryKeyToIdx = Object.fromEntries(primaryKeysList.map((key, index) => [key, index]));
  const secondaryKeyToIdx = Object.fromEntries(secondaryKeysList.map((key, index) => [key, index]));
  const mergedKeyToIdx = Object.fromEntries(mergedKeysList.map((key, index) => [key, index]));
  
  // Process each key in the merged list
  for (const rowKey of mergedKeysList) {
    // Initialize merged row with placeholders
    const mergedRow = Array(mergedKeysList.length).fill(PLACEHOLDER_CHAR);
    
    // Set diagonal value
    const rowIndex = mergedKeyToIdx[rowKey];
    if (rowIndex !== undefined) {
      mergedRow[rowIndex] = DIAGONAL_CHAR;
    }
    
    // If key exists in primary grid, copy its values
    if (primaryGrid[rowKey]) {
      const primaryRow = safeDecompress(primaryGrid, primaryKeysList, rowKey);
      
      for (const [colKey, colIdx] of Object.entries(mergedKeyToIdx)) {
        if (primaryKeyToIdx[colKey] !== undefined && primaryKeyToIdx[rowKey] !== undefined) {
          const primaryColIdx = primaryKeyToIdx[colKey];
          const primaryVal = primaryRow[primaryColIdx];
          if (primaryVal !== PLACEHOLDER_CHAR) {
            mergedRow[colIdx] = primaryVal;
          }
        }
      }
    }
    
    // If key exists in secondary grid, copy its values (if not already set from primary)
    if (secondaryGrid[rowKey]) {
      const secondaryRow = safeDecompress(secondaryGrid, secondaryKeysList, rowKey);
      
      for (const [colKey, colIdx] of Object.entries(mergedKeyToIdx)) {
        if (secondaryKeyToIdx[colKey] !== undefined && secondaryKeyToIdx[rowKey] !== undefined) {
          const secondaryColIdx = secondaryKeyToIdx[colKey];
          const secondaryVal = secondaryRow[secondaryColIdx];
          if (secondaryVal !== PLACEHOLDER_CHAR && mergedRow[colIdx] === PLACEHOLDER_CHAR) {
            mergedRow[colIdx] = secondaryVal;
          }
        }
      }
    }
    
    // Compress and store the merged row
    mergedGrid[rowKey] = compress(mergedRow.join(''));
  }
  
  return mergedGrid;
}

/**
 * Export a tracker file to a different format.
 * 
 * @param trackerPath Path to the tracker file
 * @param outputFormat Format to export to ('json', 'csv', or 'dot')
 * @param outputPath Optional output path
 * @returns Path to the exported file or empty string on failure
 */
export async function exportTracker(
  trackerPath: string,
  outputFormat: 'json' | 'csv' | 'dot' = 'json',
  outputPath?: string
): Promise<string> {
  try {
    // Read tracker file
    const trackerData = await readTrackerFile(trackerPath);
    
    // Determine output path if not provided
    if (!outputPath) {
      const basePath = trackerPath.replace(/\.md$/, '');
      outputPath = `${basePath}.${outputFormat}`;
    }
    
    // Get sorted keys
    const sortedKeys = sortKeyStringsHierarchically(Object.keys(trackerData.keys));
    
    if (outputFormat === 'json') {
      // Export as JSON
      const jsonData = {
        keys: trackerData.keys,
        grid: trackerData.grid,
        metadata: {
          lastKeyEdit: trackerData.lastKeyEdit,
          lastGridEdit: trackerData.lastGridEdit
        }
      };
      
      await fs.writeFile(outputPath, JSON.stringify(jsonData, null, 2), 'utf-8');
    } 
    else if (outputFormat === 'csv') {
      // Export as CSV
      let csvContent = 'Key,Path,' + sortedKeys.join(',') + '\n';
      
      for (const rowKey of sortedKeys) {
        const rowPath = trackerData.keys[rowKey] || '';
        let row = `${rowKey},${rowPath}`;
        
        if (trackerData.grid[rowKey]) {
          const decompressed = decompress(trackerData.grid[rowKey]);
          if (decompressed.length === sortedKeys.length) {
            for (const char of decompressed) {
              row += `,${char}`;
            }
          } else {
            logger.warning(`Row length mismatch for ${rowKey} during CSV export`);
            for (let i = 0; i < sortedKeys.length; i++) {
              row += ',p';
            }
          }
        } else {
          for (let i = 0; i < sortedKeys.length; i++) {
            row += ',p';
          }
        }
        
        csvContent += row + '\n';
      }
      
      await fs.writeFile(outputPath, csvContent, 'utf-8');
    } 
    else if (outputFormat === 'dot') {
      // Export as GraphViz DOT format
      let dotContent = 'digraph dependencies {\n';
      dotContent += '  rankdir=LR;\n';
      dotContent += '  node [shape=box, style=filled, fillcolor=lightblue];\n\n';
      
      // Add nodes
      for (const key of sortedKeys) {
        const path = trackerData.keys[key] || '';
        const label = path.split('/').pop() || key;
        dotContent += `  "${key}" [label="${label}\\n(${key})"];\n`;
      }
      
      dotContent += '\n';
      
      // Add edges
      for (const rowKey of sortedKeys) {
        if (trackerData.grid[rowKey]) {
          const decompressed = decompress(trackerData.grid[rowKey]);
          
          if (decompressed.length === sortedKeys.length) {
            for (let i = 0; i < sortedKeys.length; i++) {
              const colKey = sortedKeys[i];
              const char = decompressed[i];
              
              if (char === '<') {
                dotContent += `  "${colKey}" -> "${rowKey}" [color=blue];\n`;
              } else if (char === '>') {
                dotContent += `  "${rowKey}" -> "${colKey}" [color=red];\n`;
              } else if (char === 'x') {
                dotContent += `  "${rowKey}" -> "${colKey}" [dir=both, color=purple];\n`;
              } else if (char === 'd') {
                dotContent += `  "${rowKey}" -> "${colKey}" [style=dotted, color=green];\n`;
              } else if (char === 's') {
                dotContent += `  "${rowKey}" -> "${colKey}" [style=dashed, color=orange];\n`;
              }
            }
          }
        }
      }
      
      dotContent += '}\n';
      
      await fs.writeFile(outputPath, dotContent, 'utf-8');
    } 
    else {
      throw new Error(`Unsupported export format: ${outputFormat}`);
    }
    
    logger.info(`Exported tracker to ${outputPath} in ${outputFormat} format`);
    return outputPath;
  } catch (error) {
    logger.error(`Error exporting tracker: ${error}`);
    return '';
  }
}

/**
 * Remove a file from a tracker.
 * 
 * @param trackerPath Path to the tracker file
 * @param fileToRemove Path of the file to remove
 * @param pathToKeyInfo Map of paths to key info objects
 * @returns True if successful, false otherwise
 */
export async function removeFileFromTracker(
  trackerPath: string,
  fileToRemove: string,
  pathToKeyInfo: Record<string, KeyInfo>
): Promise<boolean> {
  try {
    // Normalize path
    const normalizedFileToRemove = fileToRemove.replace(/\\/g, '/');
    
    // Try to get the key for the file path
    const keyInfo = pathToKeyInfo[normalizedFileToRemove];
    if (!keyInfo) {
      logger.warning(`File ${fileToRemove} not found in pathToKeyInfo map`);
      return false;
    }
    
    const keyToRemove = keyInfo.keyString;
    return await removeKeyFromTracker(trackerPath, keyToRemove);
  } catch (error) {
    logger.error(`Error removing file from tracker: ${error}`);
    return false;
  }
}

/**
 * Remove a key from a tracker.
 * 
 * @param trackerPath Path to the tracker file
 * @param keyToRemove Key to remove
 * @returns True if successful, false otherwise
 */
export async function removeKeyFromTracker(
  trackerPath: string,
  keyToRemove: string
): Promise<boolean> {
  try {
    // Backup the tracker file
    await backupTrackerFile(trackerPath);
    
    // Read the tracker data
    const trackerData = await readTrackerFile(trackerPath);
    
    // Check if key exists
    if (!trackerData.keys[keyToRemove]) {
      logger.warning(`Key ${keyToRemove} not found in tracker ${trackerPath}`);
      return false;
    }
    
    // Remove key from keys section
    const newKeys = { ...trackerData.keys };
    delete newKeys[keyToRemove];
    
    // Remove key from grid
    const newGrid = { ...trackerData.grid };
    delete newGrid[keyToRemove];
    
    // Remove reference to key in other grid rows
    for (const rowKey of Object.keys(newGrid)) {
      try {
        const decompressed = decompress(newGrid[rowKey]);
        const updatedRow = Array.from(decompressed);
        
        // Get the index of the key to remove
        const keysList = sortKeyStringsHierarchically(Object.keys(trackerData.keys));
        const keyIndex = keysList.indexOf(keyToRemove);
        
        if (keyIndex >= 0 && keyIndex < updatedRow.length) {
          // Remove the element at the key's index
          updatedRow.splice(keyIndex, 1);
          newGrid[rowKey] = compress(updatedRow.join(''));
        }
      } catch (error) {
        logger.warning(`Error updating grid row ${rowKey}: ${error}`);
      }
    }
    
    // Write updated tracker
    const lastKeyEdit = `removed_key:${keyToRemove}:${Date.now()}`;
    const lastGridEdit = `removed_key:${keyToRemove}:${Date.now()}`;
    
    const success = await writeTrackerFile(
      trackerPath,
      newKeys,
      newGrid,
      lastKeyEdit,
      lastGridEdit
    );
    
    if (success) {
      logger.info(`Successfully removed key ${keyToRemove} from tracker ${trackerPath}`);
    }
    
    return success;
  } catch (error) {
    logger.error(`Error removing key from tracker: ${error}`);
    return false;
  }
} 