import { ConfigManager } from '../../utils/config-manager';
import fs from 'fs';
import path from 'path';
import os from 'os';

describe('Config Manager', () => {
  let configManager: ConfigManager;
  let tempConfigPath: string;

  beforeEach(() => {
    configManager = ConfigManager.getInstance();
    tempConfigPath = path.join(os.tmpdir(), 'test-config.json');
    process.env.CLINE_CONFIG_PATH = tempConfigPath;
  });

  afterEach(() => {
    if (fs.existsSync(tempConfigPath)) {
      fs.unlinkSync(tempConfigPath);
    }
    delete process.env.CLINE_CONFIG_PATH;
  });

  describe('Singleton Pattern', () => {
    it('should return the same instance', () => {
      const instance1 = ConfigManager.getInstance();
      const instance2 = ConfigManager.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('Configuration Loading', () => {
    it('should load default configuration when no config file exists', () => {
      const config = configManager.getConfig();
      expect(config).toBeDefined();
      expect(config.excluded_dirs).toBeDefined();
      expect(config.excluded_extensions).toBeDefined();
    });

    it('should load configuration from file when it exists', () => {
      const testConfig = {
        excluded_dirs: ['test-dir'],
        excluded_extensions: ['.test']
      };
      fs.writeFileSync(tempConfigPath, JSON.stringify(testConfig));
      
      const newConfigManager = ConfigManager.getInstance();
      const config = newConfigManager.getConfig();
      expect(config.excluded_dirs).toEqual(testConfig.excluded_dirs);
      expect(config.excluded_extensions).toEqual(testConfig.excluded_extensions);
    });
  });

  describe('Configuration Access', () => {
    it('should get excluded directories', () => {
      const excludedDirs = configManager.getExcludedDirs();
      expect(Array.isArray(excludedDirs)).toBe(true);
      expect(excludedDirs).toContain('__pycache__');
    });

    it('should get excluded extensions', () => {
      const excludedExtensions = configManager.getExcludedExtensions();
      expect(Array.isArray(excludedExtensions)).toBe(true);
      expect(excludedExtensions).toContain('.pyc');
    });

    it('should get threshold values', () => {
      expect(configManager.getThreshold('doc_similarity')).toBe(0.65);
      expect(configManager.getThreshold('code_similarity')).toBe(0.7);
      expect(configManager.getThreshold('unknown')).toBe(0.7); // Default value
    });
  });

  describe('Configuration Updates', () => {
    it('should update configuration', () => {
      const updates = {
        excluded_dirs: ['new-dir'],
        thresholds: {
          doc_similarity: 0.8
        }
      };

      const success = configManager.updateConfig(updates);
      expect(success).toBe(true);

      const config = configManager.getConfig();
      expect(config.excluded_dirs).toContain('new-dir');
      expect(config.thresholds.doc_similarity).toBe(0.8);
    });

    it('should reset to default configuration', () => {
      // First update with custom values
      configManager.updateConfig({
        excluded_dirs: ['custom-dir'],
        thresholds: { doc_similarity: 0.9 }
      });

      // Then reset
      const success = configManager.resetToDefaults();
      expect(success).toBe(true);

      const config = configManager.getConfig();
      expect(config.excluded_dirs).not.toContain('custom-dir');
      expect(config.thresholds.doc_similarity).toBe(0.65);
    });
  });

  describe('Error Handling', () => {
    it('should handle invalid JSON in config file', () => {
      fs.writeFileSync(tempConfigPath, 'invalid json');
      
      const newConfigManager = ConfigManager.getInstance();
      const config = newConfigManager.getConfig();
      expect(config).toBeDefined();
      expect(config.excluded_dirs).toBeDefined();
    });

    it('should handle invalid updates', () => {
      const success = configManager.updateConfig(null as any);
      expect(success).toBe(false);
    });
  });
}); 