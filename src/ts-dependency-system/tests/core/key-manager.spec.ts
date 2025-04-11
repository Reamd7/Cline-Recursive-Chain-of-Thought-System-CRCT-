import mock from 'mock-fs';
import pathe from 'pathe';
import {
  KeyInfo,
  validateKey,
  getFileTypeForKey,
  sortKeyStringsHierarchically,
  sortKeys,
  getPathFromKey,
  generateKeys,
  getKeyFromPath
} from '../../core/key-manager';
import { KeyGenerationError } from '../../core/exceptions';

// 禁用console输出，避免测试中的错误
global.console.debug = jest.fn();
global.console.warn = jest.fn();
global.console.error = jest.fn();

// 模拟fs和path模块
jest.mock('path', () => (require('pathe')));

describe('Key Manager', () => {
  beforeEach(() => {
    mock({})
  });
  afterEach(() => {
    mock.restore();
    jest.clearAllMocks();
  });
  describe('validateKey', () => {
    it('应该验证有效的键', () => {
      expect(validateKey('1A')).toBe(true);      // 顶级目录
      expect(validateKey('1A1')).toBe(true);     // 顶级目录中的文件
      expect(validateKey('1Aa')).toBe(true);     // 子目录
      expect(validateKey('1Aa1')).toBe(true);    // 子目录中的文件
      expect(validateKey('2Ba')).toBe(true);     // 第2层的子目录
      expect(validateKey('10Zz99')).toBe(true);  // 复杂键
    });

    it('应该拒绝无效的键', () => {
      expect(validateKey('')).toBe(false);       // 空字符串
      expect(validateKey('A1')).toBe(false);     // 缺少层级
      expect(validateKey('1a')).toBe(false);     // 小写目录字母
      expect(validateKey('0A')).toBe(false);     // 层级从0开始
      expect(validateKey('1A-1')).toBe(false);   // 包含无效字符
      expect(validateKey('1AA')).toBe(false);    // 多个大写字母
    });
  });

  describe('getFileTypeForKey', () => {
    it('应该根据扩展名返回正确的文件类型', () => {
      expect(getFileTypeForKey('file.py')).toBe('py');
      expect(getFileTypeForKey('file.js')).toBe('js');
      expect(getFileTypeForKey('file.ts')).toBe('js');
      expect(getFileTypeForKey('file.jsx')).toBe('js');
      expect(getFileTypeForKey('file.tsx')).toBe('js');
      expect(getFileTypeForKey('file.md')).toBe('md');
      expect(getFileTypeForKey('file.rst')).toBe('md');
      expect(getFileTypeForKey('file.html')).toBe('html');
      expect(getFileTypeForKey('file.htm')).toBe('html');
      expect(getFileTypeForKey('file.css')).toBe('css');
      expect(getFileTypeForKey('file.txt')).toBe('generic');
      expect(getFileTypeForKey('file')).toBe('generic');
    });

    it('应该处理大小写不敏感的扩展名', () => {
      expect(getFileTypeForKey('file.PY')).toBe('py');
      expect(getFileTypeForKey('file.Js')).toBe('js');
      expect(getFileTypeForKey('file.MD')).toBe('md');
    });
  });

  describe('sortKeyStringsHierarchically', () => {
    it('应该按层次结构对键字符串进行排序', () => {
      const unsortedKeys = ['1A10', '1A2', '1A1', '2B1', '1Aa1', '1Ab1', '1Aa2'];
      const expectedOrder = ['1A1', '1A2', '1A10', '1Aa1', '1Aa2', '1Ab1', '2B1'];
      
      expect(sortKeyStringsHierarchically(unsortedKeys)).toEqual(expectedOrder);
    });

    it('应该处理空数组和无效键', () => {
      expect(sortKeyStringsHierarchically([])).toEqual([]);
      expect(sortKeyStringsHierarchically(['', null, undefined, '1A1'] as any)).toEqual(['1A1']);
    });
  });

  describe('sortKeys', () => {
    it('应该按层级和键字符串对KeyInfo对象进行排序', () => {
      const keyInfos: KeyInfo[] = [
        { keyString: '1A10', normPath: '/path/to/1A10', parentPath: '/path/to', tier: 1, isDirectory: false },
        { keyString: '1A2', normPath: '/path/to/1A2', parentPath: '/path/to', tier: 1, isDirectory: false },
        { keyString: '2B1', normPath: '/path/to/2B1', parentPath: '/path/to', tier: 2, isDirectory: false },
        { keyString: '1Aa1', normPath: '/path/to/1Aa1', parentPath: '/path/to/1Aa', tier: 1, isDirectory: false }
      ];
      
      const sorted = sortKeys(keyInfos);
      
      // 首先按层级排序，然后按键字符串排序
      expect(sorted[0].keyString).toBe('1A2');
      expect(sorted[1].keyString).toBe('1A10');
      expect(sorted[2].keyString).toBe('1Aa1');
      expect(sorted[3].keyString).toBe('2B1');
    });

    it('应该处理空数组和无效KeyInfo对象', () => {
      expect(sortKeys([])).toEqual([]);
      
      const invalidKeyInfos = [
        null,
        { keyString: '1A1', normPath: '/path/to/1A1', parentPath: '/path/to', tier: 1, isDirectory: false }
      ] as any;
      
      const sorted = sortKeys(invalidKeyInfos);
      expect(sorted.length).toBe(2);
      expect(sorted[0].keyString).toBe('1A1');
    });
  });


  describe('getPathFromKey and getKeyFromPath', () => {
    it('应该在键和路径之间进行转换', () => {
      const pathToKeyInfo: Record<string, KeyInfo> = {
        '/path/to/dir': { keyString: '1A', normPath: '/path/to/dir', parentPath: '/path/to', tier: 1, isDirectory: true },
        '/path/to/dir/file.txt': { keyString: '1A1', normPath: '/path/to/dir/file.txt', parentPath: '/path/to/dir', tier: 1, isDirectory: false }
      };
      
      expect(getPathFromKey('1A', pathToKeyInfo)).toBe('/path/to/dir');
      expect(getPathFromKey('1A1', pathToKeyInfo)).toBe('/path/to/dir/file.txt');
      expect(getPathFromKey('1B', pathToKeyInfo)).toBeNull();
      
      expect(getKeyFromPath('/path/to/dir', pathToKeyInfo)).toBe('1A');
      expect(getKeyFromPath('/path/to/dir/file.txt', pathToKeyInfo)).toBe('1A1');
      expect(getKeyFromPath('/nonexistent/path', pathToKeyInfo)).toBeNull();
    });

    it('应该使用上下文解决歧义键', () => {
      const pathToKeyInfo: Record<string, KeyInfo> = {
        '/path/to/dir1/file.txt': { keyString: '1A1', normPath: '/path/to/dir1/file.txt', parentPath: '/path/to/dir1', tier: 1, isDirectory: false },
        '/path/to/dir2/file.txt': { keyString: '1A1', normPath: '/path/to/dir2/file.txt', parentPath: '/path/to/dir2', tier: 1, isDirectory: false }
      };
      
      // 没有上下文，无法解决歧义
      expect(getPathFromKey('1A1', pathToKeyInfo)).toBeNull();
      
      // 使用上下文解决歧义
      expect(getPathFromKey('1A1', pathToKeyInfo, '/path/to/dir1')).toBe('/path/to/dir1/file.txt');
      expect(getPathFromKey('1A1', pathToKeyInfo, '/path/to/dir2')).toBe('/path/to/dir2/file.txt');
      
      // 无效上下文
      expect(getPathFromKey('1A1', pathToKeyInfo, '/path/to/dir3')).toBeNull();
    });
  });
});