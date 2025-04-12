/**
 * 集成测试：项目分析
 * 
 * 这个测试集验证完整的项目分析流程，包括文件分析、依赖建议和跟踪器更新。
 */

import * as fs from 'fs';
import * as path from 'path';
import mockFs from 'mock-fs';
import { analyzeProject } from '../../analysis/project-analyzer';
import { readTrackerFile } from '../../io/tracker-io';
import { ConfigManager } from '../../utils/config-manager';
import { clearAllCaches } from '../../utils';

describe('项目分析集成测试', () => {
  // 在测试前禁用Console输出
  let consoleSpy: jest.SpyInstance;
  
  beforeAll(() => {
    consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    jest.spyOn(console, 'error').mockImplementation();
    jest.spyOn(console, 'warn').mockImplementation();
  });
  
  afterAll(() => {
    consoleSpy.mockRestore();
  });
  
  beforeEach(() => {
    clearAllCaches();
    
    // 模拟文件系统
    mockFs({
      '/project': {
        'src': {
          'module1': {
            'file1.ts': 'import { something } from "../module2/file2";\nexport function func1() { return "hello"; }',
            'file3.ts': 'import { func1 } from "./file1";\nexport function func3() { func1(); }',
          },
          'module2': {
            'file2.ts': 'export const something = "world";\nimport { func3 } from "../module1/file3";',
          },
        },
        'docs': {
          'readme.md': '# Project\nSee [module1](../src/module1/file1.ts)',
        },
        'cline_docs': {
          'module_relationship_tracker.md': '# Module Relationship Tracker\n\n|  | module1 | module2 |\n|---|---|---|\n| module1 | o | p |\n| module2 | p | o |',
          'doc_tracker.md': '# Doc Tracker\n\n|  | readme.md |\n|---|---|\n| readme.md | o |',
        },
        '.clinerules.config.json': JSON.stringify({
          paths: {
            project_root: '/project',
            doc_dir: ['docs'],
            code_root_dirs: ['src'],
            excluded_paths: ['node_modules', 'dist'],
          },
          thresholds: {
            code_similarity: 0.7,
          },
        }),
      },
    });
    
    // 配置ConfigManager
    const configManager = ConfigManager.getInstance();
    // 使用updateConfigSetting方法设置配置路径
    configManager.updateConfigSetting('paths.project_root', '/project');
    configManager.updateConfigSetting('paths.doc_dir', ['docs']);
    configManager.updateConfigSetting('paths.code_root_dirs', ['src']);
    configManager.updateConfigSetting('paths.excluded_paths', ['node_modules', 'dist']);
    configManager.updateConfigSetting('thresholds.code_similarity', 0.7);
  });
  
  afterEach(() => {
    mockFs.restore();
  });
  
  test('应该分析项目并更新跟踪器', async () => {
    // 执行项目分析
    const result = await analyzeProject(true, true);
    
    // 验证结果
    expect(result.status).toBe('success');
    
    // 验证主跟踪器是否已更新
    const mainTrackerPath = '/project/cline_docs/module_relationship_tracker.md';
    expect(fs.existsSync(mainTrackerPath)).toBe(true);
    
    const mainTracker = await readTrackerFile(mainTrackerPath);
    expect(mainTracker).toBeDefined();
    expect(mainTracker.keys).toBeDefined();
    expect(Object.keys(mainTracker.keys).length).toBeGreaterThan(0);
    
    // 验证是否所有的占位符('p')都已被替换
    const mainTrackerGrid = mainTracker.grid;
    const hasPlaceholders = Object.values(mainTrackerGrid).some(row => row.includes('p'));
    expect(hasPlaceholders).toBe(false);
    
    // 验证文档跟踪器是否已更新
    const docTrackerPath = '/project/cline_docs/doc_tracker.md';
    expect(fs.existsSync(docTrackerPath)).toBe(true);
    
    const docTracker = await readTrackerFile(docTrackerPath);
    expect(docTracker).toBeDefined();
    expect(docTracker.keys).toBeDefined();
    expect(Object.keys(docTracker.keys).length).toBeGreaterThan(0);
  });
}); 