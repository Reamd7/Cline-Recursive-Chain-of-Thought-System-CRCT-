import { ConfigManager, ConfigValidator, ConfigListener, DEFAULT_CONFIG } from '../../utils/config-manager';
import { existsSync, readFileSync, writeFileSync, unlinkSync } from 'fs';
import { join } from 'path';

describe('ConfigManager', () => {
    let configManager: ConfigManager;
    let testConfigPath: string;
    const defaultTestConfig = {
        testKey: 'testValue',
        nested: {
            key: 'value'
        }
    };

    beforeEach(() => {
        testConfigPath = join(process.cwd(), 'test.config.json');
        // 获取单例实例
        configManager = ConfigManager.getInstance();
        // 直接设置测试配置值
        configManager.set('testKey', 'testValue');
        configManager.set('nested', {
            key: 'value'
        });
    });

    afterEach(() => {
        if (existsSync(testConfigPath)) {
            unlinkSync(testConfigPath);
        }
        // 重置为默认配置
        configManager.resetToDefaults();
    });

    describe('config operations', () => {
        it('应该正确获取配置值', () => {
            expect(configManager.get('testKey')).toBe('testValue');
            expect(configManager.get('nonexistent', 'default')).toBe('default');
        });
        
        it('应该正确设置配置值', () => {
            configManager.set('testKey', 'newValue');
            expect(configManager.get('testKey')).toBe('newValue');
        });
    });

    describe('updateConfig', () => {
        it('应该正确更新多个配置值', () => {
            const updates = {
                testKey: 'newValue',
                newKey: 'newValue'
            };
            configManager.updateConfig(updates);
            
            expect(configManager.get('testKey')).toBe('newValue');
            expect(configManager.get('newKey')).toBe('newValue');
        });
    });

    describe('validation', () => {
        it('应该验证配置变更', () => {
            const validator: ConfigValidator = {
                validate: (config) => config.testKey !== 'invalid',
                getErrors: () => []
            };
            configManager.addValidator(validator);
            
            expect(() => configManager.set('testKey', 'invalid')).toThrow();
            // 由于验证失败，值应该保持不变
            expect(configManager.get('testKey')).toBe('testValue');
        });
    });

    describe('listeners', () => {
        it('应该通知监听器配置变更', () => {
            let notified = false;
            const listener: ConfigListener = {
                onConfigChanged: () => {
                    notified = true;
                }
            };
            configManager.addListener(listener);
            
            configManager.set('testKey', 'newValue');
            expect(notified).toBe(true);
        });

        it('应该移除监听器', () => {
            let notified = false;
            const listener: ConfigListener = {
                onConfigChanged: () => {
                    notified = true;
                }
            };
            configManager.addListener(listener);
            configManager.removeListener(listener);
            
            configManager.set('testKey', 'newValue');
            expect(notified).toBe(false);
        });
    });
    
    describe('excluded settings', () => {
        it('应该返回排除的目录', () => {
            const dirs = configManager.getExcludedDirs();
            expect(Array.isArray(dirs)).toBe(true);
            expect(dirs.length).toBeGreaterThan(0);
        });
        
        it('应该返回排除的扩展名', () => {
            const exts = configManager.getExcludedExtensions();
            expect(Array.isArray(exts)).toBe(true);
            expect(exts.length).toBeGreaterThan(0);
        });
    });
}); 