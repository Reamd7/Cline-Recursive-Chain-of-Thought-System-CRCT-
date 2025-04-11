/**
 * Unit tests for the dependency grid module.
 */

import {
  createGrid,
  validateGrid,
  getDependenciesForKey,
  setDependency,
  removeDependency,
  compressGrid,
  decompressGrid,
  DependencyGrid
} from '../dependency-grid';
import { GridValidationError } from '../exceptions';

describe('Dependency Grid', () => {
  let grid: DependencyGrid;

  beforeEach(() => {
    // Create a test grid with 3 keys
    grid = createGrid(['1A', '2B', '3C']);
  });

  describe('createGrid', () => {
    it('should create a grid with correct dimensions', () => {
      expect(grid.keys).toEqual(['1A', '2B', '3C']);
      expect(grid.grid.length).toBe(3);
      expect(grid.grid[0].length).toBe(3);
    });

    it('should initialize with self-dependencies', () => {
      expect(grid.grid[0][0]).toBe('o');
      expect(grid.grid[1][1]).toBe('o');
      expect(grid.grid[2][2]).toBe('o');
    });

    it('should initialize with placeholders', () => {
      expect(grid.grid[0][1]).toBe('p');
      expect(grid.grid[0][2]).toBe('p');
      expect(grid.grid[1][0]).toBe('p');
      expect(grid.grid[1][2]).toBe('p');
      expect(grid.grid[2][0]).toBe('p');
      expect(grid.grid[2][1]).toBe('p');
    });
  });

  describe('validateGrid', () => {
    it('should validate a correct grid', () => {
      expect(() => validateGrid(grid)).not.toThrow();
    });

    it('should throw for invalid grid dimensions', () => {
      const invalidGrid = { ...grid, grid: [[], []] };
      expect(() => validateGrid(invalidGrid)).toThrow(GridValidationError);
    });

    it('should throw for invalid dependency types', () => {
      const invalidGrid = { ...grid, grid: grid.grid.map(row => [...row]) };
      invalidGrid.grid[0][1] = 'z' as any;
      expect(() => validateGrid(invalidGrid)).toThrow(GridValidationError);
    });

    it('should throw for invalid self-dependency', () => {
      const invalidGrid = { ...grid, grid: grid.grid.map(row => [...row]) };
      invalidGrid.grid[0][0] = 'x';
      expect(() => validateGrid(invalidGrid)).toThrow(GridValidationError);
    });

    it('should throw for invalid mutual dependency', () => {
      const invalidGrid = { ...grid, grid: grid.grid.map(row => [...row]) };
      invalidGrid.grid[0][1] = 'x';
      invalidGrid.grid[1][0] = '>';
      expect(() => validateGrid(invalidGrid)).toThrow(GridValidationError);
    });
  });

  describe('getDependenciesForKey', () => {
    it('should return empty array for key with no dependencies', () => {
      const deps = getDependenciesForKey(grid, '1A');
      expect(deps).toEqual([]);
    });

    it('should return correct dependencies', () => {
      const updatedGrid = setDependency(grid, '1A', '2B', '>');
      const deps = getDependenciesForKey(updatedGrid, '1A');
      expect(deps).toEqual([{ sourceKey: '1A', targetKey: '2B', type: '>' }]);
    });

    it('should throw for non-existent key', () => {
      expect(() => getDependenciesForKey(grid, 'non-existent')).toThrow(GridValidationError);
    });
  });

  describe('setDependency', () => {
    it('should set a dependency and its inverse', () => {
      const updatedGrid = setDependency(grid, '1A', '2B', '>');
      expect(updatedGrid.grid[0][1]).toBe('>');
      expect(updatedGrid.grid[1][0]).toBe('<');
    });

    it('should set a mutual dependency', () => {
      const updatedGrid = setDependency(grid, '1A', '2B', 'x');
      expect(updatedGrid.grid[0][1]).toBe('x');
      expect(updatedGrid.grid[1][0]).toBe('x');
    });

    it('should throw for non-existent keys', () => {
      expect(() => setDependency(grid, '1A', 'non-existent', '>')).toThrow(GridValidationError);
    });
  });

  describe('removeDependency', () => {
    it('should remove a dependency and its inverse', () => {
      const withDependency = setDependency(grid, '1A', '2B', '>');
      const updatedGrid = removeDependency(withDependency, '1A', '2B');
      expect(updatedGrid.grid[0][1]).toBe('n');
      expect(updatedGrid.grid[1][0]).toBe('n');
    });

    it('should throw for non-existent keys', () => {
      expect(() => removeDependency(grid, '1A', 'non-existent')).toThrow(GridValidationError);
    });
  });

  describe('compressGrid and decompressGrid', () => {
    it('should compress and decompress a grid correctly', () => {
      // Set some dependencies
      const withDependencies = setDependency(
        setDependency(grid, '1A', '2B', '>'),
        '2B',
        '3C',
        'x'
      );

      // Compress the grid
      const compressed = compressGrid(withDependencies);

      // Decompress the grid
      const decompressed = decompressGrid(compressed, withDependencies.keys);

      // Verify the decompressed grid matches the original
      expect(decompressed.grid).toEqual(withDependencies.grid);
    });

    it('should handle empty grid compression', () => {
      const emptyGrid = createGrid([]);
      const compressed = compressGrid(emptyGrid);
      const decompressed = decompressGrid(compressed, []);
      expect(decompressed.grid).toEqual([]);
    });

    it('should throw for invalid compressed format', () => {
      expect(() => decompressGrid('invalid', ['1A'])).toThrow(GridValidationError);
    });
  });
}); 