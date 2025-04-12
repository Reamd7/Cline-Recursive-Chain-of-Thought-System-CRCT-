#!/usr/bin/env node

/**
 * Dependency Processor CLI
 * 
 * This is the command-line interface for the TypeScript implementation of the dependency processing system.
 * It provides commands for analyzing projects, managing dependencies, and other operations.
 */

import { Command } from 'commander';
import * as path from 'path';
import * as fs from 'fs';
import { 
  analyzeFile, 
  analyzeProject,
  sortSuggestionsByConfidence,
  generateEmbedding,
  clearEmbeddingCache
} from '../analysis';
import {
  compressGrid,
  decompressGrid,
  createGrid,
  setDependency,
  getDependenciesForKey,
  removeDependency,
  DependencyGrid
} from '../core/dependency-grid';
import {
  getKeyFromPath,
  validateKey,
  getPathFromKey,
  regenerateKeys
} from '../core/key-manager';
import {
  readTrackerFile,
  writeTrackerFile,
  mergeTrackers,
  exportTracker,
  removeKeyFromTracker,
  removeFileFromTracker,
  TrackerData
} from '../io/tracker-io';
import {
  ConfigManager,
  logger,
  clearAllCaches,
  getProjectRoot,
  normalizePath
} from '../utils';

// Configure logger
const log = logger;

// Create command object
const program = new Command();

program
  .name('dependency-processor')
  .description('TypeScript implementation of the dependency processing system')
  .version('1.0.0');

/**
 * Helper function to validate grid format used in IO module
 * @param grid Record mapping key to compressed grid row
 * @param keys List of keys
 * @returns True if valid, false otherwise
 */
function validateGridFormat(grid: Record<string, string>, keys: string[]): boolean {
  if (!grid || !keys) return false;
  
  // Check that all keys have a grid row
  for (const key of keys) {
    if (!grid[key]) {
      logger.warning(`Missing grid row for key: ${key}`);
      return false;
    }
  }
  
  return true;
}

// analyze-file command
program
  .command('analyze-file')
  .description('Analyze a single file for dependencies')
  .argument('<file_path>', 'Path to the file to analyze')
  .option('--detail', 'Show detailed analysis')
  .action(async (filePath, options) => {
    try {
      log.info(`Analyzing file: ${filePath}`);
      const result = await analyzeFile(filePath);
      
      if (options.detail) {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.log(`Analysis completed for ${filePath}`);
        console.log(`Found ${result.imports.length} imports and ${result.docReferences.length} document references`);
      }
    } catch (error: any) {
      log.error(`Error analyzing file: ${error.message}`);
      process.exit(1);
    }
  });

// analyze-project command
program
  .command('analyze-project')
  .description('Analyze the project and update tracker files')
  .option('--output <json_path>', 'Output path for JSON analysis results')
  .option('--force-embeddings', 'Force recalculation of embeddings')
  .option('--force-analysis', 'Force reanalysis of all files')
  .action(async (options) => {
    try {
      log.info('Starting project analysis');
      const result = await analyzeProject(options.forceAnalysis, options.forceEmbeddings);
      
      if (options.output) {
        fs.writeFileSync(options.output, JSON.stringify(result, null, 2));
        log.info(`Analysis results written to ${options.output}`);
      }
      
      log.info('Project analysis completed');
      
      if (result.status === 'success') {
        console.log('Project analysis completed successfully');
      } else {
        console.log(`Project analysis completed with status: ${result.status}`);
        console.log(`Message: ${result.message}`);
      }
    } catch (error: any) {
      log.error(`Error analyzing project: ${error.message}`);
      process.exit(1);
    }
  });

// compress command
program
  .command('compress')
  .description('Compress a dependency grid')
  .argument('<tracker_file>', 'Path to the tracker file')
  .action(async (trackerFile) => {
    try {
      log.info(`Compressing tracker file: ${trackerFile}`);
      const trackerData = await readTrackerFile(trackerFile);
      
      if (!trackerData || !trackerData.keys) {
        log.error('Invalid tracker file format');
        process.exit(1);
      }
      
      // Convert TrackerData to DependencyGrid
      const keysList = Object.keys(trackerData.keys);
      const grid = createGrid(keysList);
      
      // Convert compressed grid strings to grid array
      for (let i = 0; i < keysList.length; i++) {
        const key = keysList[i];
        if (trackerData.grid[key]) {
          // Decompress the row and add it to the grid
          const rowString = trackerData.grid[key];
          let index = 0;
          let col = 0;
          
          while (index < rowString.length) {
            const match = rowString.slice(index).match(/^(\d+)([><xdsSnpo])/);
            if (!match) break;
            
            const [_, count, char] = match;
            const numCount = parseInt(count, 10);
            
            for (let k = 0; k < numCount; k++) {
              if (col < keysList.length && i < keysList.length) {
                grid.grid[i][col] = char;
                col++;
              }
            }
            
            index += match[0].length;
          }
        }
      }
      
      const compressed = compressGrid(grid);
      console.log(compressed);
      
      log.info('Compression completed');
    } catch (error: any) {
      log.error(`Error compressing grid: ${error.message}`);
      process.exit(1);
    }
  });

// decompress command
program
  .command('decompress')
  .description('Decompress a compressed grid string')
  .argument('<compressed_string>', 'Compressed grid string')
  .argument('<keys_file>', 'Path to a file containing the keys (one per line)')
  .action(async (compressedString, keysFile) => {
    try {
      log.info('Decompressing grid');
      
      if (!fs.existsSync(keysFile)) {
        log.error(`Keys file not found: ${keysFile}`);
        process.exit(1);
      }
      
      const keysContent = fs.readFileSync(keysFile, 'utf-8');
      const keys = keysContent.trim().split('\n');
      
      const grid = decompressGrid(compressedString, keys);
      console.log(JSON.stringify(grid, null, 2));
      
      log.info('Decompression completed');
    } catch (error: any) {
      log.error(`Error decompressing grid: ${error.message}`);
      process.exit(1);
    }
  });

// get_char command
program
  .command('get_char')
  .description('Get the dependency character between two keys')
  .argument('<tracker_file>', 'Path to the tracker file')
  .argument('<source_key>', 'Source key')
  .argument('<target_key>', 'Target key')
  .action(async (trackerFile, sourceKey, targetKey) => {
    try {
      log.info(`Getting dependency character from ${trackerFile}`);
      
      // Validate keys
      if (!validateKey(sourceKey) || !validateKey(targetKey)) {
        log.error('Invalid key format');
        process.exit(1);
      }
      
      const trackerData = await readTrackerFile(trackerFile);
      
      if (!trackerData || !trackerData.keys) {
        log.error('Invalid tracker file format');
        process.exit(1);
      }
      
      // Convert TrackerData to DependencyGrid
      const keysList = Object.keys(trackerData.keys);
      const grid = createGrid(keysList);
      
      // Convert compressed grid strings to grid array
      for (let i = 0; i < keysList.length; i++) {
        const key = keysList[i];
        if (trackerData.grid[key]) {
          // Decompress the row and add it to the grid
          const rowString = trackerData.grid[key];
          let index = 0;
          let col = 0;
          
          while (index < rowString.length) {
            const match = rowString.slice(index).match(/^(\d+)([><xdsSnpo])/);
            if (!match) break;
            
            const [_, count, char] = match;
            const numCount = parseInt(count, 10);
            
            for (let k = 0; k < numCount; k++) {
              if (col < keysList.length && i < keysList.length) {
                grid.grid[i][col] = char;
                col++;
              }
            }
            
            index += match[0].length;
          }
        }
      }
      
      const dependencies = getDependenciesForKey(grid, sourceKey)
        .filter(dep => dep.targetKey === targetKey);
      
      if (dependencies.length > 0) {
        console.log(dependencies[0].type);
      } else {
        console.log('No dependency found between the specified keys');
      }
    } catch (error: any) {
      log.error(`Error getting dependency character: ${error.message}`);
      process.exit(1);
    }
  });

// set_char command
program
  .command('set_char')
  .description('Set the dependency character between two keys')
  .argument('<tracker_file>', 'Path to the tracker file')
  .argument('<source_key>', 'Source key')
  .argument('<target_key>', 'Target key')
  .argument('<char>', 'Dependency character (one of >, <, x, d, s, S, n, p)')
  .action(async (trackerFile, sourceKey, targetKey, char) => {
    try {
      log.info(`Setting dependency character in ${trackerFile}`);
      
      // Validate character
      if (!['>', '<', 'x', 'd', 's', 'S', 'n', 'p'].includes(char)) {
        log.error('Invalid dependency character');
        process.exit(1);
      }
      
      // Validate keys
      if (!validateKey(sourceKey) || !validateKey(targetKey)) {
        log.error('Invalid key format');
        process.exit(1);
      }
      
      const trackerData = await readTrackerFile(trackerFile);
      
      if (!trackerData || !trackerData.keys) {
        log.error('Invalid tracker file format');
        process.exit(1);
      }
      
      // Convert TrackerData to DependencyGrid
      const keysList = Object.keys(trackerData.keys);
      const grid = createGrid(keysList);
      
      // Convert compressed grid strings to grid array
      for (let i = 0; i < keysList.length; i++) {
        const key = keysList[i];
        if (trackerData.grid[key]) {
          // Decompress the row and add it to the grid
          const rowString = trackerData.grid[key];
          let index = 0;
          let col = 0;
          
          while (index < rowString.length) {
            const match = rowString.slice(index).match(/^(\d+)([><xdsSnpo])/);
            if (!match) break;
            
            const [_, count, charMatch] = match;
            const numCount = parseInt(count, 10);
            
            for (let k = 0; k < numCount; k++) {
              if (col < keysList.length && i < keysList.length) {
                grid.grid[i][col] = charMatch;
                col++;
              }
            }
            
            index += match[0].length;
          }
        }
      }
      
      const updatedGrid = setDependency(grid, sourceKey, targetKey, char as any);
      
      // Convert back to TrackerData format
      const updatedTrackerData: TrackerData = {
        keys: trackerData.keys,
        grid: {},
        lastKeyEdit: trackerData.lastKeyEdit,
        lastGridEdit: new Date().toISOString()
      };
      
      for (let i = 0; i < keysList.length; i++) {
        const key = keysList[i];
        updatedTrackerData.grid[key] = compressGrid({
          keys: keysList,
          grid: [updatedGrid.grid[i]],
          keyToIndex: updatedGrid.keyToIndex
        });
      }
      
      const lastKeyEdit = trackerData.lastKeyEdit || '';
      const lastGridEdit = new Date().toISOString();
      
      await writeTrackerFile(
        trackerFile, 
        updatedTrackerData.keys, 
        updatedTrackerData.grid, 
        lastKeyEdit,
        lastGridEdit
      );
      
      log.info('Dependency character updated successfully');
    } catch (error: any) {
      log.error(`Error setting dependency character: ${error.message}`);
      process.exit(1);
    }
  });

// add-dependency command
program
  .command('add-dependency')
  .description('Add a dependency between two keys')
  .option('--tracker <tracker_file>', 'Path to the tracker file')
  .option('--source-key <source_key>', 'Source key')
  .option('--target-key <target_key>', 'Target key')
  .option('--dep-type <char>', 'Dependency type character')
  .action(async (options) => {
    try {
      if (!options.tracker || !options.sourceKey || !options.targetKey || !options.depType) {
        log.error('Missing required options');
        console.log('Usage: add-dependency --tracker <tracker_file> --source-key <source_key> --target-key <target_key> --dep-type <char>');
        process.exit(1);
      }
      
      log.info(`Adding dependency in ${options.tracker}`);
      
      // Validate character
      if (!['>', '<', 'x', 'd', 's', 'S', 'n', 'p'].includes(options.depType)) {
        log.error('Invalid dependency character');
        process.exit(1);
      }
      
      // Validate keys
      if (!validateKey(options.sourceKey) || !validateKey(options.targetKey)) {
        log.error('Invalid key format');
        process.exit(1);
      }
      
      const trackerData = await readTrackerFile(options.tracker);
      
      if (!trackerData || !trackerData.keys) {
        log.error('Invalid tracker file format');
        process.exit(1);
      }
      
      // Convert TrackerData to DependencyGrid
      const keysList = Object.keys(trackerData.keys);
      const grid = createGrid(keysList);
      
      // Convert compressed grid strings to grid array
      for (let i = 0; i < keysList.length; i++) {
        const key = keysList[i];
        if (trackerData.grid[key]) {
          // Decompress the row and add it to the grid
          const rowString = trackerData.grid[key];
          let index = 0;
          let col = 0;
          
          while (index < rowString.length) {
            const match = rowString.slice(index).match(/^(\d+)([><xdsSnpo])/);
            if (!match) break;
            
            const [_, count, charMatch] = match;
            const numCount = parseInt(count, 10);
            
            for (let k = 0; k < numCount; k++) {
              if (col < keysList.length && i < keysList.length) {
                grid.grid[i][col] = charMatch;
                col++;
              }
            }
            
            index += match[0].length;
          }
        }
      }
      
      const updatedGrid = setDependency(grid, options.sourceKey, options.targetKey, options.depType as any);
      
      // Convert back to TrackerData format
      const updatedTrackerData: TrackerData = {
        keys: trackerData.keys,
        grid: {},
        lastKeyEdit: trackerData.lastKeyEdit,
        lastGridEdit: new Date().toISOString()
      };
      
      for (let i = 0; i < keysList.length; i++) {
        const key = keysList[i];
        updatedTrackerData.grid[key] = compressGrid({
          keys: keysList,
          grid: [updatedGrid.grid[i]],
          keyToIndex: updatedGrid.keyToIndex
        });
      }
      
      const lastKeyEdit = trackerData.lastKeyEdit || '';
      const lastGridEdit = new Date().toISOString();
      
      await writeTrackerFile(
        options.tracker, 
        updatedTrackerData.keys, 
        updatedTrackerData.grid,
        lastKeyEdit,
        lastGridEdit
      );
      
      log.info('Dependency added successfully');
    } catch (error: any) {
      log.error(`Error adding dependency: ${error.message}`);
      process.exit(1);
    }
  });

// remove-key command
program
  .command('remove-key')
  .description('Remove a key from a tracker file')
  .argument('<tracker_file>', 'Path to the tracker file')
  .argument('<key>', 'Key to remove')
  .action(async (trackerFile, key) => {
    try {
      log.info(`Removing key ${key} from ${trackerFile}`);
      
      // Validate key
      if (!validateKey(key)) {
        log.error('Invalid key format');
        process.exit(1);
      }
      
      await removeKeyFromTracker(trackerFile, key);
      
      log.info('Key removed successfully');
    } catch (error: any) {
      log.error(`Error removing key: ${error.message}`);
      process.exit(1);
    }
  });

// remove-file command
program
  .command('remove-file')
  .description('Remove a file from a tracker file')
  .argument('<tracker_file>', 'Path to the tracker file')
  .argument('<file_path>', 'Path to the file to remove')
  .action(async (trackerFile, filePath) => {
    try {
      log.info(`Removing file ${filePath} from ${trackerFile}`);
      const normalizedPath = normalizePath(path.resolve(filePath));
      
      // 需要先获取一个空的path到key的映射
      const pathToKeyInfo: Record<string, any> = {};
      
      // 先获取trackerData
      const trackerData = await readTrackerFile(trackerFile);
      if (trackerData && trackerData.keys) {
        // 遍历keys生成pathToKeyInfo映射
        for (const [key, pathStr] of Object.entries(trackerData.keys)) {
          pathToKeyInfo[pathStr] = {
            keyString: key,
            norm_path: pathStr
          };
        }
      }
      
      await removeFileFromTracker(trackerFile, normalizedPath, pathToKeyInfo);
      
      log.info('File removed successfully');
    } catch (error: any) {
      log.error(`Error removing file: ${error.message}`);
      process.exit(1);
    }
  });

// merge-trackers command
program
  .command('merge-trackers')
  .description('Merge two tracker files')
  .argument('<primary_tracker>', 'Path to the primary tracker file')
  .argument('<secondary_tracker>', 'Path to the secondary tracker file')
  .option('--output <output_path>', 'Output path for the merged tracker')
  .action(async (primaryTracker, secondaryTracker, options) => {
    try {
      log.info(`Merging trackers: ${primaryTracker} and ${secondaryTracker}`);
      
      const outputPath = options.output || primaryTracker;
      
      await mergeTrackers(primaryTracker, secondaryTracker, outputPath);
      
      log.info(`Trackers merged successfully to ${outputPath}`);
    } catch (error: any) {
      log.error(`Error merging trackers: ${error.message}`);
      process.exit(1);
    }
  });

// export-tracker command
program
  .command('export-tracker')
  .description('Export a tracker file to a different format')
  .argument('<tracker_file>', 'Path to the tracker file')
  .option('--format <format>', 'Export format (json, csv, dot)', 'json')
  .option('--output <output_path>', 'Output path for the exported file')
  .action(async (trackerFile, options) => {
    try {
      log.info(`Exporting tracker ${trackerFile} to ${options.format} format`);
      
      const format = options.format;
      if (!['json', 'csv', 'dot'].includes(format)) {
        log.error('Invalid export format. Supported formats: json, csv, dot');
        process.exit(1);
      }
      
      const outputPath = options.output || `${trackerFile}.${format}`;
      
      await exportTracker(trackerFile, format, outputPath);
      
      log.info(`Tracker exported successfully to ${outputPath}`);
    } catch (error: any) {
      log.error(`Error exporting tracker: ${error.message}`);
      process.exit(1);
    }
  });

// clear-caches command
program
  .command('clear-caches')
  .description('Clear all caches used by the dependency system')
  .action(() => {
    try {
      log.info('Clearing all caches');
      
      clearAllCaches();
      clearEmbeddingCache();
      
      log.info('Caches cleared successfully');
    } catch (error: any) {
      log.error(`Error clearing caches: ${error.message}`);
      process.exit(1);
    }
  });

// update-config command
program
  .command('update-config')
  .description('Update a configuration value')
  .argument('<key_path>', 'Configuration key path (e.g., paths.doc_dir)')
  .argument('<value>', 'New value')
  .action((keyPath, value) => {
    try {
      log.info(`Updating configuration: ${keyPath} = ${value}`);
      
      const config = ConfigManager.getInstance();
      
      // Parse value if it's an array or object
      let parsedValue = value;
      if (value.startsWith('[') || value.startsWith('{')) {
        try {
          parsedValue = JSON.parse(value);
        } catch (error) {
          log.error('Invalid JSON value');
          process.exit(1);
        }
      } else if (value === 'true' || value === 'false') {
        parsedValue = value === 'true';
      } else if (!isNaN(Number(value))) {
        parsedValue = Number(value);
      }
      
      // 直接使用set方法更新配置
      config.set(keyPath, parsedValue);
      
      log.info('Configuration updated successfully');
    } catch (error: any) {
      log.error(`Error updating configuration: ${error.message}`);
      process.exit(1);
    }
  });

// reset-config command
program
  .command('reset-config')
  .description('Reset the configuration to default values')
  .action(() => {
    try {
      log.info('Resetting configuration to default values');
      
      const config = ConfigManager.getInstance();
      config.resetToDefaults();
      
      log.info('Configuration reset successfully');
    } catch (error: any) {
      log.error(`Error resetting configuration: ${error.message}`);
      process.exit(1);
    }
  });

// show-dependencies command
program
  .command('show-dependencies')
  .description('Show all dependencies for a specific key')
  .option('--key <key>', 'Key to show dependencies for')
  .action(async (options) => {
    try {
      if (!options.key) {
        log.error('Missing required option: --key');
        console.log('Usage: show-dependencies --key <key>');
        process.exit(1);
      }
      
      log.info(`Showing dependencies for key: ${options.key}`);
      
      // Validate key
      if (!validateKey(options.key)) {
        log.error('Invalid key format');
        process.exit(1);
      }
      
      const projectRoot = getProjectRoot();
      const config = ConfigManager.getInstance();
      
      // Get paths to tracker files
      const trackerPaths = [
        path.join(projectRoot, config.get('paths.memory_dir', 'cline_docs'), 'module_relationship_tracker.md'),
        path.join(projectRoot, config.get('paths.memory_dir', 'cline_docs'), 'doc_tracker.md')
      ];
      
      // Also add mini trackers if they exist
      const moduleDir = path.join(projectRoot, config.get('paths.memory_dir', 'cline_docs'));
      const miniTrackers = fs.readdirSync(moduleDir)
        .filter(file => file.endsWith('_module.md'))
        .map(file => path.join(moduleDir, file));
      
      trackerPaths.push(...miniTrackers);
      
      const dependencies: any[] = [];
      
      for (const trackerPath of trackerPaths) {
        if (fs.existsSync(trackerPath)) {
          try {
            const trackerData = await readTrackerFile(trackerPath);
            
            if (!trackerData || !trackerData.keys) {
              continue;
            }
            
            // Convert TrackerData to DependencyGrid
            const keysList = Object.keys(trackerData.keys);
            const grid = createGrid(keysList);
            
            // Convert compressed grid strings to grid array
            for (let i = 0; i < keysList.length; i++) {
              const key = keysList[i];
              if (trackerData.grid[key]) {
                // Decompress the row and add it to the grid
                const rowString = trackerData.grid[key];
                let index = 0;
                let col = 0;
                
                while (index < rowString.length) {
                  const match = rowString.slice(index).match(/^(\d+)([><xdsSnpo])/);
                  if (!match) break;
                  
                  const [_, count, charMatch] = match;
                  const numCount = parseInt(count, 10);
                  
                  for (let k = 0; k < numCount; k++) {
                    if (col < keysList.length && i < keysList.length) {
                      grid.grid[i][col] = charMatch;
                      col++;
                    }
                  }
                  
                  index += match[0].length;
                }
              }
            }
            
            if (grid.keyToIndex[options.key] !== undefined) {
              const deps = getDependenciesForKey(grid, options.key);
              
              deps.forEach(dep => {
                dependencies.push({
                  ...dep,
                  tracker: path.basename(trackerPath)
                });
              });
            }
          } catch (error) {
            log.warning(`Error reading tracker ${trackerPath}: ${error}`);
          }
        }
      }
      
      if (dependencies.length > 0) {
        console.log('Dependencies:');
        dependencies.forEach(dep => {
          console.log(`${dep.sourceKey} ${dep.type} ${dep.targetKey} [${dep.tracker}]`);
        });
      } else {
        console.log(`No dependencies found for key: ${options.key}`);
      }
    } catch (error: any) {
      log.error(`Error showing dependencies: ${error.message}`);
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse(process.argv);

// If no arguments are provided, display help
if (process.argv.length === 2) {
  program.help();
}