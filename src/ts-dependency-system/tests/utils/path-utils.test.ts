import { normalizePath, isSubPath, getRelativePath } from '../../utils/path-utils';

describe('Path Utils', () => {
  describe('normalizePath', () => {
    it('should normalize Windows paths', () => {
      expect(normalizePath('C:\\Users\\test\\file.txt')).toBe('c:/Users/test/file.txt');
      expect(normalizePath('C:/Users/test/file.txt')).toBe('c:/Users/test/file.txt');
    });

    it('should normalize Unix paths', () => {
      expect(normalizePath('/home/user/test/file.txt')).toBe('/home/user/test/file.txt');
      expect(normalizePath('/home/user/test/')).toBe('/home/user/test');
    });

    it('should handle relative paths', () => {
      expect(normalizePath('./test/file.txt')).toBe(process.cwd() + '/test/file.txt');
      expect(normalizePath('../test/file.txt')).toBe(process.cwd() + '/../test/file.txt');
    });

    it('should handle empty paths', () => {
      expect(normalizePath('')).toBe('');
    });
  });

  describe('isSubPath', () => {
    it('should detect subpaths correctly', () => {
      expect(isSubPath('/home/user/test', '/home/user')).toBe(true);
      expect(isSubPath('/home/user/test/file.txt', '/home/user')).toBe(true);
      expect(isSubPath('/home/user', '/home/user/test')).toBe(false);
      expect(isSubPath('/home/user1', '/home/user2')).toBe(false);
    });

    it('should handle Windows paths', () => {
      expect(isSubPath('c:/Users/test/file.txt', 'c:/Users')).toBe(true);
      expect(isSubPath('c:/Users/test', 'c:/Users/test2')).toBe(false);
    });
  });

  describe('getRelativePath', () => {
    it('should get relative paths correctly', () => {
      expect(getRelativePath('/home/user/test/file.txt', '/home/user')).toBe('test/file.txt');
      expect(getRelativePath('/home/user/test', '/home/user/test/file.txt')).toBe('..');
      expect(getRelativePath('/home/user1/test', '/home/user2/test')).toBe('../../user1/test');
    });

    it('should handle Windows paths', () => {
      expect(getRelativePath('c:/Users/test/file.txt', 'c:/Users')).toBe('test/file.txt');
      expect(getRelativePath('c:/Users/test', 'c:/Users/test2')).toBe('../test');
    });
  });
}); 