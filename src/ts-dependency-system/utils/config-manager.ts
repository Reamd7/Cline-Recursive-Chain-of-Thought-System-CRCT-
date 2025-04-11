/**
 * 配置管理模块
 * 提供配置的加载、保存、验证和通知功能，以及访问特定配置设置的便捷方法
 */

import { existsSync, readFileSync, writeFileSync, statSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { cacheManager } from './cache-manager';
import { normalizePath, getProjectRoot } from './path-utils';

// 默认配置
export const DEFAULT_CONFIG = {
    excluded_dirs: [
        "__pycache__",
        ".git",
        ".svn",
        ".hg",
        ".vscode",
        ".idea",
        "__MACOSX",
        "venv",
        "env",
        ".venv",
        "node_modules",
        "bower_components",
        "build",
        "dist",
        "target",
        "out",
        "tmp",
        "temp",
        "tests",
        "examples",
        "embeddings",
        "cline_utils/dependency_system/analysis/embeddings",
    ],
    excluded_extensions: [
        ".pyc",
        ".pyo",
        ".pyd",
        ".dll",
        ".exe",
        ".so",
        ".o",
        ".a",
        ".lib",
        ".dll",
        ".pdb",
        ".sdf",
        ".suo",
        ".user",
        ".swp",
        ".log",
        ".tmp",
        ".bak",
        ".d",
        ".DS_Store",
        ".jar",
        ".war",
        ".ear",
        ".zip",
        ".tar.gz",
        ".tar",
        ".tgz",
        ".rar",
        ".7z",
        ".dmg",
        ".iso",
        ".img",
        ".bin",
        ".dat",
        ".db",
        ".sqlite",
        ".sqlite3",
        ".dbf",
        ".mdb",
        ".sav",
        ".eot",
        ".ttf",
        ".woff",
        ".woff2",
        ".otf",
        ".swf",
        ".bak",
        ".old",
        ".orig",
        ".embedding",
        ".npy"
    ],
    thresholds: {
        doc_similarity: 0.65,
        code_similarity: 0.7
    },
    models: {
        doc_model_name: "all-mpnet-base-v2",
        code_model_name: "all-mpnet-base-v2",
    },
    compute: {
        embedding_device: "auto" // Options: "auto", "cuda", "mps", "cpu"
    },
    paths: {
        doc_dir: "docs",
        memory_dir: "cline_docs",
        embeddings_dir: "cline_utils/dependency_system/analysis/embeddings",
        backups_dir: "cline_docs/backups",
    },
    excluded_paths: [
        "src/node_modules",
        "src/client/node_modules"
    ],
    allowed_dependency_chars: ['<', '>', 'x', 'd', 's', 'S'],
    excluded_file_patterns: [
        "*_module.md",
        "implementation_plan_*.md",
        "*_task.md"
    ]
};

// 字符优先级
export const CHARACTER_PRIORITIES: Record<string, number> = {
    'x': 5,
    '<': 4, '>': 4,
    'S': 3,
    's': 2, 'd': 2,
    'n': 1, 'p': 1, 'o': 1,
    '-': 0,
    ' ': 0
};
export const DEFAULT_PRIORITY = 0;

// 配置接口定义
export interface Config {
    [key: string]: any;
    excluded_dirs?: string[];
    excluded_extensions?: string[];
    thresholds?: {
        [key: string]: number;
        doc_similarity: number;
        code_similarity: number;
    };
    models?: {
        [key: string]: string;
        doc_model_name: string;
        code_model_name: string;
    };
    compute?: {
        [key: string]: any;
        embedding_device: string;
    };
    paths?: {
        [key: string]: string;
        doc_dir: string;
        memory_dir: string;
        embeddings_dir: string;
        backups_dir: string;
    };
    excluded_paths?: string[];
    allowed_dependency_chars?: string[];
    excluded_file_patterns?: string[];
}

// 配置验证器接口
export interface ConfigValidator {
    validate(config: Config): boolean;
    getErrors(): string[];
}

// 配置监听器接口
export interface ConfigListener {
    onConfigChanged(newConfig: Config, oldConfig: Config): void;
}

/**
 * 配置管理器
 * 处理配置设置的读取和写入，并提供访问特定设置的便捷方法
 */
export class ConfigManager {
    private static _instance: ConfigManager | null = null;
    private _initialized: boolean = false;
    private _config: Config | null = null;
    private _configPath: string | null = null;
    private validators: ConfigValidator[] = [];
    private listeners: ConfigListener[] = [];
    private configCache: any;

    /**
     * 单例模式实现
     */
    public static getInstance(): ConfigManager {
        if (!ConfigManager._instance) {
            ConfigManager._instance = new ConfigManager();
        }
        return ConfigManager._instance;
    }

    private constructor() {
        if (this._initialized) {
            return;
        }

        this.configCache = cacheManager.getCache('config');
        this._loadConfig();

        // 设置默认排除项（如果不存在）
        if (!this._config?.excluded_dirs) {
            this._config!.excluded_dirs = DEFAULT_CONFIG.excluded_dirs;
        }
        if (!this._config?.excluded_extensions) {
            this._config!.excluded_extensions = DEFAULT_CONFIG.excluded_extensions;
        }

        this._initialized = true;
    }

    /**
     * 获取计算设置
     * @param settingName 设置名称
     * @param defaultValue 默认值
     */
    public getComputeSetting(settingName: string, defaultValue: any = null): any {
        const computeSettings = this.config.compute || {} as Record<string, any>;
        return computeSettings[settingName] !== undefined ? computeSettings[settingName] : defaultValue;
    }

    /**
     * 获取配置对象
     */
    public get config(): Config {
        if (this._config === null) {
            this._loadConfig();
        }
        return this._config as Config;
    }

    /**
     * 获取配置文件路径
     */
    public get configPath(): string {
        if (this._configPath === null) {
            const projectRoot = getProjectRoot();
            this._configPath = normalizePath(join(projectRoot, '.clinerules.config.json'));
        }
        return this._configPath;
    }

    /**
     * 加载配置
     */
    private _loadConfig(): void {
        try {
            const cachedConfig = this.configCache.get(`config:${existsSync(this.configPath) ? 
                statSync(this.configPath).mtimeMs : 'missing'}`);
                
            if (cachedConfig !== null) {
                this._config = cachedConfig;
                return;
            }
            
            if (existsSync(this.configPath)) {
                const configData = readFileSync(this.configPath, 'utf-8');
                this._config = JSON.parse(configData);
            } else {
                this._config = { ...DEFAULT_CONFIG };
                this._saveConfig();
            }
            
            this.configCache.set(`config:${existsSync(this.configPath) ? 
                statSync(this.configPath).mtimeMs : 'missing'}`, this._config);
        } catch (error) {
            console.error(`Error loading configuration from ${this.configPath}:`, error);
            this._config = { ...DEFAULT_CONFIG };
        }
    }

    /**
     * 保存配置
     */
    private _saveConfig(): boolean {
        try {
            const dirPath = dirname(this.configPath);
            if (!existsSync(dirPath)) {
                // 创建目录
                mkdirSync(dirPath, { recursive: true });
            }
            
            const configData = JSON.stringify(this._config, null, 2);
            writeFileSync(this.configPath, configData, 'utf-8');
            this.configCache.invalidate(`config:${existsSync(this.configPath) ? 
                statSync(this.configPath).mtimeMs : 'missing'}`);
            return true;
        } catch (error) {
            console.error(`Error writing configuration file ${this.configPath}:`, error);
            return false;
        }
    }

    /**
     * 更新配置设置
     * @param key 配置键
     * @param value 配置值
     */
    public updateConfigSetting(key: string, value: string | number | boolean | any[] | Config): boolean {
        if (!this._config) {
            this._loadConfig();
        }
        
        try {
            const keyParts = key.split('.');
            let current = this._config as any;
            
            // 遍历嵌套对象直到倒数第二级
            for (let i = 0; i < keyParts.length - 1; i++) {
                if (!current[keyParts[i]]) {
                    current[keyParts[i]] = {};
                }
                current = current[keyParts[i]];
            }
            
            // 设置最后一级的值
            current[keyParts[keyParts.length - 1]] = value;
            return this._saveConfig();
        } catch (error) {
            console.error(`Error updating config setting ${key}:`, error);
            return false;
        }
    }

    /**
     * 获取排除的目录
     */
    public getExcludedDirs(): string[] {
        const cachedDirs = this.configCache.get(`excluded_dirs:${existsSync(this.configPath) ? 
            statSync(this.configPath).mtimeMs : 'missing'}`);
            
        if (cachedDirs !== null) {
            return cachedDirs;
        }
        
        const excludedDirs = this.config.excluded_dirs || DEFAULT_CONFIG.excluded_dirs;
        this.configCache.set(`excluded_dirs:${existsSync(this.configPath) ? 
            statSync(this.configPath).mtimeMs : 'missing'}`, excludedDirs);
        return excludedDirs;
    }

    /**
     * 获取排除的扩展名
     */
    public getExcludedExtensions(): string[] {
        const cachedExts = this.configCache.get(`excluded_extensions:${existsSync(this.configPath) ? 
            statSync(this.configPath).mtimeMs : 'missing'}`);
            
        if (cachedExts !== null) {
            return cachedExts;
        }
        
        const excludedExts = this.config.excluded_extensions || DEFAULT_CONFIG.excluded_extensions;
        this.configCache.set(`excluded_extensions:${existsSync(this.configPath) ? 
            statSync(this.configPath).mtimeMs : 'missing'}`, excludedExts);
        return excludedExts;
    }

    /**
     * 获取排除的路径
     */
    public getExcludedPaths(): string[] {
        const cachedPaths = this.configCache.get(`excluded_paths:${existsSync(this.configPath) ? 
            statSync(this.configPath).mtimeMs : 'missing'}`);
            
        if (cachedPaths !== null) {
            return cachedPaths;
        }
        
        // 获取排除路径，如果不存在则使用默认值
        const excludedPaths = this.config.excluded_paths || DEFAULT_CONFIG.excluded_paths;
        
        // 缓存结果
        this.configCache.set(`excluded_paths:${existsSync(this.configPath) ? 
            statSync(this.configPath).mtimeMs : 'missing'}`, excludedPaths);
        
        return excludedPaths;
    }

    /**
     * 获取阈值设置
     * @param thresholdType 阈值类型
     */
    public getThreshold(thresholdType: string): number {
        const thresholds = this.config.thresholds || {};
        
        if (thresholds[thresholdType as keyof typeof thresholds] !== undefined) {
            return thresholds[thresholdType as keyof typeof thresholds];
        }
        
        const defaultThresholds = DEFAULT_CONFIG.thresholds;
        return defaultThresholds[thresholdType as keyof typeof defaultThresholds] || 0.7;
    }

    /**
     * 获取模型名称
     * @param modelType 模型类型
     */
    public getModelName(modelType: string): string {
        const models = this.config.models || {};
        
        if (models[modelType as keyof typeof models] !== undefined) {
            return models[modelType as keyof typeof models];
        }
        
        const defaultModels = DEFAULT_CONFIG.models;
        return defaultModels[modelType as keyof typeof defaultModels] || "all-mpnet-base-v2";
    }

    /**
     * 获取路径设置
     * @param pathType 路径类型
     * @param defaultPath 默认路径
     */
    public getPath(pathType: string, defaultPath: string | null = null): string {
        const paths = this.config.paths || {};
        
        if (paths[pathType as keyof typeof paths] !== undefined) {
            return paths[pathType as keyof typeof paths];
        }
        
        const defaultPaths = DEFAULT_CONFIG.paths;
        if (defaultPath) {
            return defaultPath;
        }
        
        return defaultPaths[pathType as keyof typeof defaultPaths] || "";
    }

    /**
     * 获取代码根目录
     */
    public getCodeRootDirectories(): string[] {
        const cachedRoots = this.configCache.get(`code_roots:${existsSync(join(getProjectRoot(), '.clinerules')) ? 
            statSync(join(getProjectRoot(), '.clinerules')).mtimeMs : 'missing'}`);
            
        if (cachedRoots !== null) {
            return cachedRoots;
        }
        
        try {
            // 从.clinerules文件中读取CODE_ROOT_DIRECTORIES部分
            const clinerules = readFileSync(join(getProjectRoot(), '.clinerules'), 'utf-8');
            const codeRootSection = clinerules.match(/\[CODE_ROOT_DIRECTORIES\]\s*((?:[-\s]*[^\[\]\r\n]+[\r\n]*)+)/i);
            
            if (codeRootSection && codeRootSection[1]) {
                // 从部分中提取目录名
                const codeRoots = codeRootSection[1]
                    .split('\n')
                    .map(line => line.trim())
                    .filter(line => line.startsWith('-'))
                    .map(line => line.replace(/^-\s*/, '').trim())
                    .filter(dir => dir.length > 0);
                
                if (codeRoots.length > 0) {
                    this.configCache.set(`code_roots:${existsSync(join(getProjectRoot(), '.clinerules')) ? 
                        statSync(join(getProjectRoot(), '.clinerules')).mtimeMs : 'missing'}`, codeRoots);
                    return codeRoots;
                }
            }
        } catch (error) {
            console.error("Error reading code root directories:", error);
        }
        
        // 默认为空数组
        return [];
    }

    /**
     * 获取文档目录
     */
    public getDocDirectories(): string[] {
        const cachedDocs = this.configCache.get(`doc_dirs:${existsSync(join(getProjectRoot(), '.clinerules')) ? 
            statSync(join(getProjectRoot(), '.clinerules')).mtimeMs : 'missing'}`);
            
        if (cachedDocs !== null) {
            return cachedDocs;
        }
        
        try {
            // 从.clinerules文件中读取DOC_DIRECTORIES部分
            const clinerules = readFileSync(join(getProjectRoot(), '.clinerules'), 'utf-8');
            const docSection = clinerules.match(/\[DOC_DIRECTORIES\]\s*((?:[-\s]*[^\[\]\r\n]+[\r\n]*)+)/i);
            
            if (docSection && docSection[1]) {
                // 从部分中提取目录名
                const docDirs = docSection[1]
                    .split('\n')
                    .map(line => line.trim())
                    .filter(line => line.startsWith('-'))
                    .map(line => line.replace(/^-\s*/, '').trim())
                    .filter(dir => dir.length > 0);
                
                if (docDirs.length > 0) {
                    this.configCache.set(`doc_dirs:${existsSync(join(getProjectRoot(), '.clinerules')) ? 
                        statSync(join(getProjectRoot(), '.clinerules')).mtimeMs : 'missing'}`, docDirs);
                    return docDirs;
                }
            }
        } catch (error) {
            console.error("Error reading doc directories:", error);
        }
        
        // 默认为空数组
        return [];
    }

    /**
     * 获取允许的依赖字符
     */
    public getAllowedDependencyChars(): string[] {
        return this.config.allowed_dependency_chars || DEFAULT_CONFIG.allowed_dependency_chars;
    }

    /**
     * 更新配置
     * @param updates 更新对象
     */
    public updateConfig(updates: Config): boolean {
        if (!this._config) {
            this._loadConfig();
        }
        
        try {
            this._deepUpdate(this._config as Config, updates);
            return this._saveConfig();
        } catch (error) {
            console.error("Error updating config:", error);
            return false;
        }
    }

    /**
     * 深度更新对象
     */
    private _deepUpdate(target: Config, source: Config): void {
        for (const key in source) {
            if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key]) && 
                typeof target[key] === 'object' && target[key] !== null && !Array.isArray(target[key])) {
                this._deepUpdate(target[key], source[key]);
            } else {
                target[key] = source[key];
            }
        }
    }

    /**
     * 重置为默认配置
     */
    public resetToDefaults(): boolean {
        try {
            this._config = { ...DEFAULT_CONFIG };
            return this._saveConfig();
        } catch (error) {
            console.error("Error resetting config to defaults:", error);
            return false;
        }
    }

    /**
     * 获取字符优先级
     * @param char 字符
     */
    public getCharPriority(char: string): number {
        return CHARACTER_PRIORITIES[char] !== undefined ? CHARACTER_PRIORITIES[char] : DEFAULT_PRIORITY;
    }

    /**
     * 获取配置值
     * @param key 配置键
     * @param defaultValue 默认值
     */
    public get<T>(key: string, defaultValue?: T): T {
        const keyParts = key.split('.');
        let current: any = this.config;
        
        for (const part of keyParts) {
            if (current === undefined || current === null || typeof current !== 'object') {
                return defaultValue as T;
            }
            current = current[part];
        }
        
        return (current === undefined || current === null) ? (defaultValue as T) : (current as T);
    }

    /**
     * 设置配置值
     * @param key 配置键
     * @param value 配置值
     */
    public set(key: string, value: any): void {
        const oldConfig = { ...this.config };
        const keyParts = key.split('.');
        let current = this._config as any;
        
        // 遍历嵌套对象直到倒数第二级
        for (let i = 0; i < keyParts.length - 1; i++) {
            if (!current[keyParts[i]]) {
                current[keyParts[i]] = {};
            }
            current = current[keyParts[i]];
        }
        
        // 设置最后一级的值
        current[keyParts[keyParts.length - 1]] = value;
        
        if (this.validateConfig()) {
            this._saveConfig();
            this.notifyListeners(this.config, oldConfig);
        } else {
            this._config = oldConfig;
            throw new Error('Configuration validation failed');
        }
    }

    /**
     * 添加配置验证器
     * @param validator 配置验证器
     */
    public addValidator(validator: ConfigValidator): void {
        this.validators.push(validator);
    }

    /**
     * 添加配置监听器
     * @param listener 配置监听器
     */
    public addListener(listener: ConfigListener): void {
        this.listeners.push(listener);
    }

    /**
     * 移除配置监听器
     * @param listener 配置监听器
     */
    public removeListener(listener: ConfigListener): void {
        this.listeners = this.listeners.filter(l => l !== listener);
    }

    /**
     * 验证配置
     */
    private validateConfig(): boolean {
        return this.validators.every(validator => validator.validate(this.config));
    }

    /**
     * 通知监听器配置变更
     */
    private notifyListeners(newConfig: Config, oldConfig: Config): void {
        this.listeners.forEach(listener => {
            try {
                listener.onConfigChanged(newConfig, oldConfig);
            } catch (error) {
                console.error('Error in config listener:', error);
            }
        });
    }
}

// 默认配置验证器实现
export class DefaultConfigValidator implements ConfigValidator {
    private errors: string[] = [];

    validate(config: Config): boolean {
        this.errors = [];
        // 这里可以添加具体的验证逻辑
        return this.errors.length === 0;
    }

    getErrors(): string[] {
        return this.errors;
    }
}

// 导出默认配置管理器实例
export const configManager = ConfigManager.getInstance(); 