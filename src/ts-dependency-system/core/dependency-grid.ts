/**
 * Core module for dependency grid operations.
 * Handles dependency grid creation, validation, and dependency relationship queries.
 */

import { GridValidationError } from './exceptions';
import { KeyInfo } from './key-manager';

/**
 * Represents a dependency relationship between two keys.
 */
export interface Dependency {
  sourceKey: string;
  targetKey: string;
  type: '>' | '<' | 'x' | 'd' | 's' | 'S' | 'n' | 'p';
}

/**
 * Represents a dependency grid with keys and their relationships.
 */
export interface DependencyGrid {
  keys: string[];
  grid: string[][];
  keyToIndex: Record<string, number>;
}

/**
 * Creates a new dependency grid from a list of keys.
 * @param keys List of keys to include in the grid
 * @returns A new dependency grid
 */
export function createGrid(keys: string[]): DependencyGrid {
  const sortedKeys = [...keys].sort();
  const keyToIndex: Record<string, number> = {};
  const grid: string[][] = [];

  // Initialize key to index mapping
  sortedKeys.forEach((key, index) => {
    keyToIndex[key] = index;
  });

  // Initialize grid with 'o' (self-dependency) on diagonal and 'p' (placeholder) elsewhere
  for (let i = 0; i < sortedKeys.length; i++) {
    grid[i] = new Array(sortedKeys.length).fill('p');
    grid[i][i] = 'o'; // Self-dependency
  }

  return {
    keys: sortedKeys,
    grid,
    keyToIndex
  };
}

/**
 * Validates the dependency grid for consistency.
 * @param grid The dependency grid to validate
 * @throws GridValidationError if the grid is invalid
 */
export function validateGrid(grid: DependencyGrid): void {
  const { keys, grid: gridData } = grid;

  // Check grid dimensions
  if (gridData.length !== keys.length) {
    throw new GridValidationError('Grid dimensions do not match number of keys');
  }

  // Validate each cell
  for (let i = 0; i < keys.length; i++) {
    for (let j = 0; j < keys.length; j++) {
      const cell = gridData[i][j];
      
      // Check for valid dependency types
      if (!['>', '<', 'x', 'd', 's', 'S', 'n', 'p', 'o'].includes(cell)) {
        throw new GridValidationError(`Invalid dependency type '${cell}' at position (${i},${j})`);
      }

      // Check for self-dependency
      if (i === j && cell !== 'o') {
        throw new GridValidationError(`Self-dependency must be 'o' at position (${i},${j})`);
      }

      // Check for mutual dependencies
      if (cell === 'x' && gridData[j][i] !== 'x') {
        throw new GridValidationError(`Mutual dependency 'x' must be symmetric at positions (${i},${j}) and (${j},${i})`);
      }

      // Check for directional dependencies
      if (cell === '>' && gridData[j][i] !== '<') {
        throw new GridValidationError(`Directional dependency '>' must have corresponding '<' at position (${j},${i})`);
      }
      if (cell === '<' && gridData[j][i] !== '>') {
        throw new GridValidationError(`Directional dependency '<' must have corresponding '>' at position (${j},${i})`);
      }
    }
  }
}

/**
 * Gets all dependencies for a specific key.
 * @param grid The dependency grid
 * @param key The key to get dependencies for
 * @returns Array of dependencies for the key
 */
export function getDependenciesForKey(grid: DependencyGrid, key: string): Dependency[] {
  const { keys, grid: gridData, keyToIndex } = grid;
  const dependencies: Dependency[] = [];
  const sourceIndex = keyToIndex[key];

  if (sourceIndex === undefined) {
    throw new GridValidationError(`Key '${key}' not found in grid`);
  }

  for (let targetIndex = 0; targetIndex < keys.length; targetIndex++) {
    const dependencyType = gridData[sourceIndex][targetIndex];
    if (dependencyType !== 'o' && dependencyType !== 'n' && dependencyType !== 'p') {
      dependencies.push({
        sourceKey: key,
        targetKey: keys[targetIndex],
        type: dependencyType as Dependency['type']
      });
    }
  }

  return dependencies;
}

/**
 * Sets a dependency relationship between two keys.
 * @param grid The dependency grid
 * @param sourceKey The source key
 * @param targetKey The target key
 * @param type The dependency type
 * @returns The updated dependency grid
 */
export function setDependency(
  grid: DependencyGrid,
  sourceKey: string,
  targetKey: string,
  type: Dependency['type']
): DependencyGrid {
  const { keys, grid: gridData, keyToIndex } = grid;
  const sourceIndex = keyToIndex[sourceKey];
  const targetIndex = keyToIndex[targetKey];

  if (sourceIndex === undefined || targetIndex === undefined) {
    throw new GridValidationError(`One or both keys not found in grid: '${sourceKey}', '${targetKey}'`);
  }

  // Create a deep copy of the grid
  const newGrid = gridData.map(row => [...row]);

  // Set the dependency
  newGrid[sourceIndex][targetIndex] = type;

  // Set the corresponding dependency if needed
  if (type === 'x') {
    newGrid[targetIndex][sourceIndex] = 'x';
  } else if (type === '>') {
    newGrid[targetIndex][sourceIndex] = '<';
  } else if (type === '<') {
    newGrid[targetIndex][sourceIndex] = '>';
  }

  return {
    ...grid,
    grid: newGrid
  };
}

/**
 * Removes a dependency relationship between two keys.
 * @param grid The dependency grid
 * @param sourceKey The source key
 * @param targetKey The target key
 * @returns The updated dependency grid
 */
export function removeDependency(
  grid: DependencyGrid,
  sourceKey: string,
  targetKey: string
): DependencyGrid {
  const { keys, grid: gridData, keyToIndex } = grid;
  const sourceIndex = keyToIndex[sourceKey];
  const targetIndex = keyToIndex[targetKey];

  if (sourceIndex === undefined || targetIndex === undefined) {
    throw new GridValidationError(`One or both keys not found in grid: '${sourceKey}', '${targetKey}'`);
  }

  // Create a deep copy of the grid
  const newGrid = gridData.map(row => [...row]);

  // Remove the dependency
  newGrid[sourceIndex][targetIndex] = 'n';
  newGrid[targetIndex][sourceIndex] = 'n';

  return {
    ...grid,
    grid: newGrid
  };
}

/**
 * Compresses the dependency grid into a more compact format.
 * @param grid The dependency grid to compress
 * @returns The compressed grid string
 */
export function compressGrid(grid: DependencyGrid): string {
  const { keys, grid: gridData } = grid;
  let result = '';

  for (let i = 0; i < keys.length; i++) {
    let currentChar = gridData[i][0];
    let count = 1;

    for (let j = 1; j < keys.length; j++) {
      if (gridData[i][j] === currentChar) {
        count++;
      } else {
        result += `${count}${currentChar}`;
        currentChar = gridData[i][j];
        count = 1;
      }
    }
    result += `${count}${currentChar}`;
  }

  return result;
}

/**
 * Decompresses a compressed grid string back into a dependency grid.
 * @param compressed The compressed grid string
 * @param keys The list of keys
 * @returns The decompressed dependency grid
 */
export function decompressGrid(compressed: string, keys: string[]): DependencyGrid {
  const grid = createGrid(keys);
  let index = 0;
  let i = 0;
  let j = 0;

  while (index < compressed.length) {
    const match = compressed.slice(index).match(/^(\d+)([><xdsSnpo])/);
    if (!match) {
      throw new GridValidationError('Invalid compressed grid format');
    }

    const [_, count, char] = match;
    const numCount = parseInt(count, 10);

    for (let k = 0; k < numCount; k++) {
      if (j >= keys.length) {
        j = 0;
        i++;
      }
      if (i < keys.length) {
        grid.grid[i][j] = char;
        j++;
      }
    }

    index += match[0].length;
  }

  return grid;
} 