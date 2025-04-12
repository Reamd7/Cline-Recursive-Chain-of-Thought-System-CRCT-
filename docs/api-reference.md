# TypeScript依赖处理系统API参考

## 目录
- [核心模块](#核心模块)
  - [Exceptions](#exceptions)
  - [Key Manager](#key-manager)
  - [Dependency Grid](#dependency-grid)
- [工具模块](#工具模块)
  - [Path Utils](#path-utils)
  - [Config Manager](#config-manager)
  - [Cache Manager](#cache-manager)
- [IO模块](#io模块)
  - [Tracker IO](#tracker-io)
  - [Update Doc Tracker](#update-doc-tracker)
  - [Update Main Tracker](#update-main-tracker)
  - [Update Mini Tracker](#update-mini-tracker)
- [分析模块](#分析模块)
  - [Dependency Analyzer](#dependency-analyzer)
  - [Dependency Suggester](#dependency-suggester)
  - [Embedding Manager](#embedding-manager)
  - [Project Analyzer](#project-analyzer)
- [命令行接口](#命令行接口)

## 核心模块

### Exceptions

```typescript
class DependencySystemError extends Error {}
```

基础错误类，所有系统错误的父类。

```typescript
class TrackerError extends DependencySystemError {}
```

处理跟踪器相关错误的异常类。

```typescript
class EmbeddingError extends DependencySystemError {}
```

处理嵌入向量生成和管理相关错误的异常类。

```typescript
class AnalysisError extends DependencySystemError {}
```

处理分析过程中出现的错误的异常类。

```typescript
class ConfigurationError extends DependencySystemError {}
```

处理配置加载和管理相关错误的异常类。

```typescript
class CacheError extends DependencySystemError {}
```

处理缓存操作相关错误的异常类。

```typescript
class KeyGenerationError extends DependencySystemError {}
```

处理键生成和管理相关错误的异常类。

```typescript
class GridValidationError extends DependencySystemError {}
```

处理依赖网格验证相关错误的异常类。

### Key Manager

```typescript
interface KeyInfo {
    key: string;
    path: string;
}
```

表示键和对应文件路径的接口。

```typescript
function generateKeys(
    filePaths: string[], 
    rootPaths: string[] = [], 
    regenerate: boolean = false
): KeyInfo[]
```

为提供的文件路径生成层次化键。

**参数:**
- `filePaths`: 需要生成键的文件路径数组
- `rootPaths`: 根路径数组，用于生成层次化键
- `regenerate`: 是否重新生成键，即使它们已经存在

**返回:**
- `KeyInfo[]`: 包含生成的键和对应路径的数组

```typescript
function validateKey(key: string): boolean
```

验证键的格式是否有效。

**参数:**
- `key`: 要验证的键

**返回:**
- `boolean`: 如果键格式有效则返回true，否则返回false

```typescript
function getPathFromKey(key: string, keys: Record<string, string>): string | null
```

从键映射中获取与键对应的路径。

**参数:**
- `key`: 要查找的键
- `keys`: 键到路径的映射记录

**返回:**
- `string | null`: 与键对应的路径，如果找不到则返回null

```typescript
function getKeyFromPath(path: string, keys: Record<string, string>): string | null
```

从键映射中获取与路径对应的键。

**参数:**
- `path`: 要查找的路径
- `keys`: 键到路径的映射记录

**返回:**
- `string | null`: 与路径对应的键，如果找不到则返回null

```typescript
function sortKeyStringsHierarchically(keys: string[]): string[]
```

按层次顺序排序键字符串数组。

**参数:**
- `keys`: 要排序的键字符串数组

**返回:**
- `string[]`: 排序后的键字符串数组

```typescript
function sortKeys(keys: KeyInfo[]): KeyInfo[]
```

按层次顺序排序KeyInfo对象数组。

**参数:**
- `keys`: 要排序的KeyInfo对象数组

**返回:**
- `KeyInfo[]`: 排序后的KeyInfo对象数组

```typescript
function regenerateKeys(keys: Record<string, string>): Record<string, string>
```

重新生成所有键。

**参数:**
- `keys`: 当前的键到路径的映射

**返回:**
- `Record<string, string>`: 更新后的键到路径的映射

### Dependency Grid

```typescript
interface Dependency {
    char: string;
    description?: string;
}
```

表示依赖关系的接口。

```typescript
interface DependencyGrid {
    keys: string[];
    grid: string[][];
}
```

表示依赖网格的接口。

```typescript
function createGrid(keys: string[]): DependencyGrid
```

为给定的键创建一个空的依赖网格。

**参数:**
- `keys`: 网格中使用的键数组

**返回:**
- `DependencyGrid`: 新创建的依赖网格

```typescript
function validateGrid(grid: DependencyGrid): boolean
```

验证依赖网格的格式和内容是否有效。

**参数:**
- `grid`: 要验证的依赖网格

**返回:**
- `boolean`: 如果网格有效则返回true，否则返回false

```typescript
function getDependenciesForKey(
    grid: DependencyGrid, 
    key: string
): { inputs: string[], outputs: string[] }
```

获取特定键的输入和输出依赖关系。

**参数:**
- `grid`: 依赖网格
- `key`: 要查询的键

**返回:**
- 包含输入和输出依赖关系的对象

```typescript
function setDependency(
    grid: DependencyGrid, 
    sourceKey: string, 
    targetKey: string, 
    dependencyChar: string
): boolean
```

在网格中设置两个键之间的依赖关系。

**参数:**
- `grid`: 依赖网格
- `sourceKey`: 源键
- `targetKey`: 目标键
- `dependencyChar`: 依赖关系字符

**返回:**
- `boolean`: 如果设置成功则返回true，否则返回false

```typescript
function removeDependency(
    grid: DependencyGrid, 
    sourceKey: string, 
    targetKey: string
): boolean
```

移除网格中两个键之间的依赖关系。

**参数:**
- `grid`: 依赖网格
- `sourceKey`: 源键
- `targetKey`: 目标键

**返回:**
- `boolean`: 如果移除成功则返回true，否则返回false

```typescript
function compressGrid(grid: DependencyGrid): string
```

将依赖网格压缩为字符串格式。

**参数:**
- `grid`: 要压缩的依赖网格

**返回:**
- `string`: 压缩后的网格字符串

```typescript
function decompressGrid(compressedGrid: string, keys: string[]): DependencyGrid
```

将压缩的网格字符串解压缩为依赖网格。

**参数:**
- `compressedGrid`: 压缩的网格字符串
- `keys`: 网格中使用的键数组

**返回:**
- `DependencyGrid`: 解压缩后的依赖网格 