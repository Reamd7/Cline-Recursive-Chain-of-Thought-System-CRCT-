/**
 * Tests for the dependency suggester module
 */

import { 
  suggestDependencies, 
  DependencyType, 
  DependencyDirection,
  sortSuggestionsByConfidence,
  aggregateSuggestions
} from '../../analysis/dependency-suggester';
import { AnalysisResult } from '../../analysis/dependency-analyzer';
import { normalizePath } from '../../utils/path-utils';

describe('Dependency Suggester', () => {
  // Create test paths
  const sourcePath = normalizePath('/project/src/index.ts');
  const targetPath = normalizePath('/project/src/utils.ts');
  
  // Define mock analysis results
  const baseAnalysisResult: AnalysisResult = {
    imports: [],
    functionCalls: [],
    semanticDependencies: [],
    documentationReferences: []
  };

  // Test direct dependencies
  test('suggestDependencies should detect direct import dependencies', async () => {
    const sourceAnalysis: AnalysisResult = {
      ...baseAnalysisResult,
      imports: [targetPath]
    };
    const targetAnalysis: AnalysisResult = {
      ...baseAnalysisResult
    };

    const suggestions = await suggestDependencies(
      sourcePath,
      targetPath,
      sourceAnalysis,
      targetAnalysis
    );

    expect(suggestions.length).toBe(1);
    expect(suggestions[0].sourcePath).toBe(sourcePath);
    expect(suggestions[0].targetPath).toBe(targetPath);
    expect(suggestions[0].direction).toBe(DependencyDirection.SOURCE_TO_TARGET);
    expect(suggestions[0].type).toBe(DependencyType.DIRECT);
    expect(suggestions[0].confidence).toBe(1.0);
  });

  test('suggestDependencies should detect direct import dependencies in both directions', async () => {
    const sourceAnalysis: AnalysisResult = {
      ...baseAnalysisResult,
      imports: [targetPath]
    };
    const targetAnalysis: AnalysisResult = {
      ...baseAnalysisResult,
      imports: [sourcePath]
    };

    const suggestions = await suggestDependencies(
      sourcePath,
      targetPath,
      sourceAnalysis,
      targetAnalysis
    );

    expect(suggestions.length).toBe(2);
    
    // Find the source-to-target suggestion
    const sourceToTarget = suggestions.find(s => 
      s.direction === DependencyDirection.SOURCE_TO_TARGET
    );
    expect(sourceToTarget).toBeDefined();
    expect(sourceToTarget!.type).toBe(DependencyType.DIRECT);
    
    // Find the target-to-source suggestion
    const targetToSource = suggestions.find(s => 
      s.direction === DependencyDirection.TARGET_TO_SOURCE
    );
    expect(targetToSource).toBeDefined();
    expect(targetToSource!.type).toBe(DependencyType.DIRECT);
  });

  // Test documentation dependencies
  test('suggestDependencies should detect documentation references', async () => {
    const sourceAnalysis: AnalysisResult = {
      ...baseAnalysisResult,
      documentationReferences: [targetPath]
    };
    const targetAnalysis: AnalysisResult = {
      ...baseAnalysisResult
    };

    const suggestions = await suggestDependencies(
      sourcePath,
      targetPath,
      sourceAnalysis,
      targetAnalysis
    );

    expect(suggestions.length).toBe(1);
    expect(suggestions[0].sourcePath).toBe(sourcePath);
    expect(suggestions[0].targetPath).toBe(targetPath);
    expect(suggestions[0].direction).toBe(DependencyDirection.SOURCE_TO_TARGET);
    expect(suggestions[0].type).toBe(DependencyType.DOCUMENT);
    expect(suggestions[0].confidence).toBe(0.9);
  });

  // Test semantic dependencies
  test('suggestDependencies should detect semantic similarity', async () => {
    const sourceAnalysis: AnalysisResult = {
      ...baseAnalysisResult
    };
    const targetAnalysis: AnalysisResult = {
      ...baseAnalysisResult
    };
    
    // Mock embeddings with high similarity
    const embeddings = {
      [sourcePath]: [0.1, 0.2, 0.3],
      [targetPath]: [0.15, 0.25, 0.35]
    };

    const suggestions = await suggestDependencies(
      sourcePath,
      targetPath,
      sourceAnalysis,
      targetAnalysis,
      embeddings
    );

    expect(suggestions.length).toBe(1);
    expect(suggestions[0].sourcePath).toBe(sourcePath);
    expect(suggestions[0].targetPath).toBe(targetPath);
    expect(suggestions[0].direction).toBe(DependencyDirection.BIDIRECTIONAL);
    expect(suggestions[0].type).toBe(DependencyType.SEMANTIC);
    expect(suggestions[0].confidence).toBeGreaterThan(0.7);
  });

  // Test sorting suggestions
  test('sortSuggestionsByConfidence should sort suggestions by confidence', () => {
    const suggestions = [
      {
        sourcePath,
        targetPath,
        direction: DependencyDirection.SOURCE_TO_TARGET,
        confidence: 0.5,
        type: DependencyType.INFERRED,
        reason: 'Inferred'
      },
      {
        sourcePath,
        targetPath,
        direction: DependencyDirection.SOURCE_TO_TARGET,
        confidence: 0.8,
        type: DependencyType.DOCUMENT,
        reason: 'Documentation'
      },
      {
        sourcePath,
        targetPath,
        direction: DependencyDirection.SOURCE_TO_TARGET,
        confidence: 1.0,
        type: DependencyType.DIRECT,
        reason: 'Direct import'
      }
    ];

    const sorted = sortSuggestionsByConfidence(suggestions);
    
    expect(sorted[0].confidence).toBe(1.0);
    expect(sorted[1].confidence).toBe(0.8);
    expect(sorted[2].confidence).toBe(0.5);
  });

  // Test aggregating suggestions
  test('aggregateSuggestions should combine suggestions with the same direction', () => {
    const suggestions = [
      {
        sourcePath,
        targetPath,
        direction: DependencyDirection.SOURCE_TO_TARGET,
        confidence: 0.5,
        type: DependencyType.INFERRED,
        reason: 'Inferred'
      },
      {
        sourcePath,
        targetPath,
        direction: DependencyDirection.SOURCE_TO_TARGET,
        confidence: 0.8,
        type: DependencyType.DOCUMENT,
        reason: 'Documentation'
      },
      {
        sourcePath,
        targetPath,
        direction: DependencyDirection.TARGET_TO_SOURCE,
        confidence: 1.0,
        type: DependencyType.DIRECT,
        reason: 'Direct import'
      }
    ];

    const aggregated = aggregateSuggestions(suggestions);
    
    expect(aggregated.length).toBe(2);
    
    // Find the source-to-target suggestion
    const sourceToTarget = aggregated.find(s => 
      s.direction === DependencyDirection.SOURCE_TO_TARGET
    );
    expect(sourceToTarget).toBeDefined();
    expect(sourceToTarget!.confidence).toBe(0.8); // Max of 0.5 and 0.8
    expect(sourceToTarget!.reason).toContain('Inferred');
    expect(sourceToTarget!.reason).toContain('Documentation');
    
    // Find the target-to-source suggestion
    const targetToSource = aggregated.find(s => 
      s.direction === DependencyDirection.TARGET_TO_SOURCE
    );
    expect(targetToSource).toBeDefined();
    expect(targetToSource!.confidence).toBe(1.0);
  });
  
  // Test direct dependency takes precedence in aggregation
  test('aggregateSuggestions should prioritize direct dependencies', () => {
    const suggestions = [
      {
        sourcePath,
        targetPath,
        direction: DependencyDirection.SOURCE_TO_TARGET,
        confidence: 0.8,
        type: DependencyType.DOCUMENT,
        reason: 'Documentation'
      },
      {
        sourcePath,
        targetPath,
        direction: DependencyDirection.SOURCE_TO_TARGET,
        confidence: 0.7,
        type: DependencyType.DIRECT,
        reason: 'Direct import'
      }
    ];

    const aggregated = aggregateSuggestions(suggestions);
    
    expect(aggregated.length).toBe(1);
    expect(aggregated[0].type).toBe(DependencyType.DIRECT);
    expect(aggregated[0].confidence).toBe(0.8); // Takes the max confidence
  });
}); 