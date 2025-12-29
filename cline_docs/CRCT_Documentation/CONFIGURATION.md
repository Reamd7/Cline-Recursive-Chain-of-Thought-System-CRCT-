# Configuration Reference

# 配置参考 | Configuration Reference

> [!TIP]
> This is a comprehensive reference for all configuration options in v8.0. Most users can use the defaults, but this guide helps fine-tune CRCT for specific needs.

> [!TIP]
> 这是 v8.0 版本所有配置选项的综合参考指南。大多数用户可以使用默认配置,但本指南有助于根据特定需求微调 CRCT。

## Configuration File

## 配置文件 | Configuration File

**Location**: `.clinerules.config.json` (project root)
**位置**: `.clinerules.config.json` (项目根目录)

**Format**: JSON
**格式**: JSON

**Auto-Created**: If missing, defaults are used
**自动创建**: 如果缺失,则使用默认值

---

## Quick Start

## 快速开始 | Quick Start

### Minimal Configuration

### 最小配置 | Minimal Configuration

```json
{
  "code_roots": ["src/", "lib/"],
  "excluded_dirs": ["node_modules", "__pycache__"]
}
```

### Recommended Configuration

### 推荐配置 | Recommended Configuration

```json
{
  "code_roots": ["src/", "lib/"],
  "excluded_dirs": ["node_modules", "__pycache__", "venv", "build"],
  "thresholds": {
    "reranker_promotion_threshold": 0.92,
    "reranker_strong_semantic_threshold": 0.78
  },
  "analysis": {
    "max_reranker_scans": 20,
    "reranker_enabled": true
  },
  "embedding": {
    "auto_select_model": true,
    "batch_size": "auto"
  }
}
```

---

## Core Settings

## 核心设置 | Core Settings

### code_roots

**Type**: `Array<string>`
**类型**: `Array<string>`

**Default**: Auto-detected from project structure
**默认值**: 从项目结构自动检测

**Description**: Directories containing source code to analyze
**描述**: 包含要分析的源代码的目录

```json
{
  "code_roots": [
    "src/",
    "lib/",
    "app/core/"
  ]
}
```

**Notes**:
**注意**:

- Paths relative to project root
- 路径相对于项目根目录

- Only files in these directories are analyzed
- 仅分析这些目录中的文件

- Subdirectories automatically included
- 自动包含子目录

### excluded_dirs

**Type**: `Array<string>`
**类型**: `Array<string>`

**Default**: See below
**默认值**: 见下文

**Description**: Directory names to skip during analysis
**描述**: 分析期间要跳过的目录名称

```json
{
  "excluded_dirs": [
    "__pycache__",
    ".git",
    "node_modules",
    "venv",
    "build",
    "dist",
    ".pytest_cache"
  ]
}
```

### excluded_extensions

**Type**: `Array<string>`
**类型**: `Array<string>`

**Default**: Binary and compiled file extensions
**默认值**: 二进制和编译文件扩展名

**Description**: File extensions to skip
**描述**: 要跳过的文件扩展名

```json
{
  "excluded_extensions": [
    ".pyc",
    ".exe",
    ".dll",
    ".so",
    ".o",
    ".jpg",
    ".png"
  ]
}
```

### excluded_file_patterns

**Type**: `Array<string>`
**类型**: `Array<string>`

**Default**: `[]`
**默认值**: `[]`

**Description**: Glob patterns for files to exclude
**描述**: 要排除的文件的 Glob 模式

```json
{
  "excluded_file_patterns": [
    "*_test.py",
    "test_*.py",
    "*debug.txt",
    "*/migrations/*"
  ]
}
```

---

## Threshold Settings

## 阈值设置 | Threshold Settings

### reranker_promotion_threshold

**Type**: `float` (0.0-1.0)
**类型**: `float` (0.0-1.0)

**Default**: `0.92`
**默认值**: `0.92`

**Description**: Score threshold for promoting to structural dependency (`<`)
**描述**: 提升为结构依赖的分数阈值 (`<`)

**Usage**:
**用法**:

```json
{
  "thresholds": {
    "reranker_promotion_threshold": 0.95  // Stricter
  }
}
```

**Recommendations**:
**推荐值**:

- **Strict** (fewer deps): `0.95-0.98`
- **严格** (更少依赖): `0.95-0.98`

- **Balanced**: `0.90-0.94` (default)
- **平衡**: `0.90-0.94` (默认)

- **Permissive** (more deps): `0.85-0.89`
- **宽松** (更多依赖): `0.85-0.89`

### reranker_strong_semantic_threshold

**Type**: `float` (0.0-1.0)
**类型**: `float` (0.0-1.0)

**Default**: `0.78`
**默认值**: `0.78`

**Description**: Threshold for strong semantic dependency (`S`)
**描述**: 强语义依赖的阈值 (`S`)

**Recommendations**:
**推荐值**:

- **Strict**: `0.85+`
- **严格**: `0.85+`

- **Balanced**: `0.75-0.82` (default)
- **平衡**: `0.75-0.82` (默认)

- **Permissive**: `0.65-0.74`
- **宽松**: `0.65-0.74`

### reranker_weak_semantic_threshold

**Type**: `float` (0.0-1.0)
**类型**: `float` (0.0-1.0)

**Default**: `0.65`
**默认值**: `0.65`

**Description**: Threshold for weak semantic dependency (`s`)
**描述**: 弱语义依赖的阈值 (`s`)

**Recommendations**:
**推荐值**:

- **Strict**: `0.75+`
- **严格**: `0.75+`

- **Balanced**: `0.60-0.70` (default)
- **平衡**: `0.60-0.70` (默认)

- **Permissive**: `0.50-0.59`
- **宽松**: `0.50-0.59`

---

## Analysis Settings

## 分析设置 | Analysis Settings

### max_reranker_scans

**Type**: `integer`
**类型**: `integer`

**Default**: `20`
**默认值**: `20`

**Description**: Maximum file pairs to rerank per file
**描述**: 每个文件要重新排序的最大文件对数

```json
{
  "analysis": {
    "max_reranker_scans": 10  // Faster, less thorough
  }
}
```

**Impact**:
**影响**:

- Higher = More accurate, slower
- 更高 = 更准确,更慢

- Lower = Faster, may miss dependencies
- 更低 = 更快,可能遗漏依赖

### reranker_enabled

**Type**: `boolean`
**类型**: `boolean`

**Default**: `true`
**默认值**: `true`

**Description**: Enable/disable reranker
**描述**: 启用/禁用重排序器

```json
{
  "analysis": {
    "reranker_enabled": false  // Disable for speed
  }
}
```

### runtime_inspection_enabled

**Type**: `boolean`
**类型**: `boolean`

**Default**: `true`
**默认值**: `true`

**Description**: Enable runtime symbol inspection
**描述**: 启用运行时符号检查

```json
{
  "analysis": {
    "runtime_inspection_enabled": true
  }
}
```

### runtime_inspection_timeout

**Type**: `integer` (seconds)
**类型**: `integer` (秒)

**Default**: `30`
**默认值**: `30`

**Description**: Max time per module for runtime inspection
**描述**: 运行时检查每个模块的最大时间

```json
{
  "analysis": {
    "runtime_inspection_timeout": 10  // Stricter timeout
  }
}
```

---

## Embedding Settings

## 嵌入设置 | Embedding Settings

### auto_select_model

**Type**: `boolean`
**类型**: `boolean`

**Default**: `true`
**默认值**: `true`

**Description**: Automatically select best embedding model
**描述**: 自动选择最佳嵌入模型

```json
{
  "embedding": {
    "auto_select_model": true  // Recommended
  }
}
```

### batch_size

**Type**: `integer | "auto"`
**类型**: `integer | "auto"`

**Default**: `"auto"`
**默认值**: `"auto"`

**Description**: Batch size for embedding generation
**描述**: 嵌入生成的批次大小

```json
{
  "embedding": {
    "batch_size": 128  // Fixed size
  }
}
```

**Auto-sizing** (recommended):
**自动调整** (推荐):

- 6GB+ VRAM: 256
- 4GB+ VRAM: 128
- 2GB+ VRAM: 64
- CPU/low VRAM: 32

### max_context_length

**Type**: `integer`
**类型**: `integer`

**Default**: `32768`
**默认值**: `32768`

**Description**: Maximum tokens for embeddings
**描述**: 嵌入的最大词元数

```json
{
  "embedding": {
    "max_context_length": 16384  // Shorter for speed
  }
}
```

### ses_max_chars

**Type**: `integer`
**类型**: `integer`

**Default**: `4000`
**默认值**: `4000`

**Description**: Maximum characters for Symbol Essence Strings
**描述**: 符号本质字符串的最大字符数

```json
{
  "embedding": {
    "ses_max_chars": 8000  // Larger for very detailed symbols
  }
}
```

---

## Compute Settings

## 计算设置 | Compute Settings

### embedding_device

**Type**: `"auto" | "cuda" | "mps" | "cpu"`
**类型**: `"auto" | "cuda" | "mps" | "cpu"`

**Default**: `"auto"`
**默认值**: `"auto"`

**Description**: Device for embedding computations
**描述**: 嵌入计算的设备

```json
{
  "compute": {
    "embedding_device": "cuda"  // Force CUDA
  }
}
```

**Options**:
**选项**:

- `"auto"`: Detect best available
- `"auto"`: 检测最佳可用设备

- `"cuda"`: NVIDIA GPU
- `"cuda"`: NVIDIA GPU

- `"mps"`: Apple Silicon GPU
- `"mps"`: Apple Silicon GPU

- `"cpu"`: CPU only
- `"cpu"`: 仅 CPU

---

## Resource Settings

## 资源设置 | Resource Settings

### min_memory_mb

**Type**: `integer`
**类型**: `integer`

**Default**: `512`
**默认值**: `512`

**Description**: Minimum RAM required (warnings if below)
**描述**: 所需的最小 RAM (如果低于此值则发出警告)

```json
{
  "resources": {
    "min_memory_mb": 1024
  }
}
```

### recommended_memory_mb

**Type**: `integer`
**类型**: `integer`

**Default**: `2048`
**默认值**: `2048`

**Description**: Recommended RAM for optimal performance
**描述**: 获得最佳性能的推荐 RAM

### max_workers

**Type**: `integer | "auto"`
**类型**: `integer | "auto"`

**Default**: `"auto"` (cpu_count * 4, max 64)
**默认值**: `"auto"` (cpu_count * 4, 最大 64)

**Description**: Maximum parallel workers
**描述**: 最大并行工作线程数

```json
{
  "resources": {
    "max_workers": 8  // Limit parallelism
  }
}
```

---

## Output Settings

## 输出设置 | Output Settings

### auto_generate_diagrams

**Type**: `boolean`
**类型**: `boolean`

**Default**: `true`
**默认值**: `true`

**Description**: Auto-generate dependency diagrams
**描述**: 自动生成依赖关系图

```json
{
  "output": {
    "auto_generate_diagrams": true
  }
}
```

### diagram_output_dir

**Type**: `string`
**类型**: `string`

**Default**: `"dependency_diagrams"`
**默认值**: `"dependency_diagrams"`

**Description**: Directory for generated diagrams
**描述**: 生成图表的目录

```json
{
  "output": {
    "diagram_output_dir": "docs/diagrams"
  }
}
```

### max_diagram_nodes

**Type**: `integer`
**类型**: `integer`

**Default**: `100`
**默认值**: `100`

**Description**: Maximum nodes in generated diagrams
**描述**: 生成图表中的最大节点数

```json
{
  "output": {
    "max_diagram_nodes": 50  // Simpler diagrams
  }
}
```

---

## Path Settings

## 路径设置 | Path Settings

### doc_dir

**Type**: `string`
**类型**: `string`

**Default**: `"docs"`
**默认值**: `"docs"`

**Description**: Documentation directory
**描述**: 文档目录

### memory_dir

**Type**: `string`
**类型**: `string`

**Default**: `"cline_docs"`
**默认值**: `"cline_docs"`

**Description**: System memory/state directory
**描述**: 系统内存/状态目录

### embeddings_dir

**Type**: `string`
**类型**: `string`

**Default**: `"cline_utils/dependency_system/analysis/embeddings"`
**默认值**: `"cline_utils/dependency_system/analysis/embeddings"`

**Description**: Embeddings storage directory
**描述**: 嵌入存储目录

---

## Visualization Settings

## 可视化设置 | Visualization Settings

### auto_diagram_output_dir

**Type**: `string | null`
**类型**: `string | null`

**Default**: `null`
**默认值**: `null`

**Description**: Auto-diagram output location
**描述**: 自动图表输出位置

```json
{
  "visualization": {
    "auto_diagram_output_dir": "cline_docs/dependency_diagrams"
  }
}
```

### max_edges_for_visualization

**Type**: `integer`
**类型**: `integer`

**Default**: `1500`
**默认值**: `1500`

**Description**: Maximum edges before warning
**描述**: 警告前的最大边数

```json
{
  "visualization": {
    "max_edges_for_visualization": 1000
  }
}
```

---

## Cache Settings

## 缓存设置 | Cache Settings

### cache_ttl_seconds

**Type**: `integer`
**类型**: `integer`

**Default**: `300` (5 minutes)
**默认值**: `300` (5 分钟)

**Description**: Default cache time-to-live
**描述**: 默认缓存生存时间

```json
{
  "caching": {
    "cache_ttl_seconds": 600  // 10 minutes
  }
}
```

### enable_compression

**Type**: `boolean`
**类型**: `boolean`

**Default**: `true`
**默认值**: `true`

**Description**: Enable cache compression
**描述**: 启用缓存压缩

### compression_threshold

**Type**: `integer`
**类型**: `integer`

**Default**: `1024` (1KB)
**默认值**: `1024` (1KB)

**Description**: Minimum size for compression
**描述**: 压缩的最小大小

---

## Environment Variables

## 环境变量 | Environment Variables

CRCT also supports configuration via environment variables:
CRCT 还支持通过环境变量进行配置:

### EMBEDDING_MODEL

Override automatic model selection:
覆盖自动模型选择:

```bash
export EMBEDDING_MODEL="all-mpnet-base-v2"
```

### EMBEDDING_DEVICE

Force specific device:
强制使用特定设备:

```bash
export EMBEDDING_DEVICE="cuda"
```

### MAX_WORKERS

Set worker count:
设置工作线程数:

```bash
export MAX_WORKERS=16
```

### USE_STREAMING

Enable streaming mode:
启用流式模式:

```bash
export USE_STREAMING=true
```

### DEBUG

Enable debug logging:
启用调试日志:

```bash
export DEBUG=true
```

---

## Complete Example

## 完整示例 | Complete Example

```json
{
  "code_roots": ["src/", "lib/", "app/"],

  "excluded_dirs": [
    "__pycache__",
    ".git",
    "node_modules",
    "venv",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache"
  ],

  "excluded_file_patterns": [
    "*_test.py",
    "test_*.py",
    "*debug.txt",
    "*/migrations/*"
  ],

  "thresholds": {
    "reranker_promotion_threshold": 0.92,
    "reranker_strong_semantic_threshold": 0.78,
    "reranker_weak_semantic_threshold": 0.65
  },

  "analysis": {
    "max_reranker_scans": 20,
    "reranker_enabled": true,
    "runtime_inspection_enabled": true,
    "runtime_inspection_timeout": 30,
    "strict_binary_detection": true
  },

  "embedding": {
    "auto_select_model": true,
    "batch_size": "auto",
    "max_context_length": 32768,
    "ses_max_chars": 4000
  },

  "compute": {
    "embedding_device": "auto"
  },

  "resources": {
    "min_memory_mb": 512,
    "recommended_memory_mb": 2048,
    "max_workers": "auto",
    "resource_check_enabled": true
  },

  "output": {
    "auto_generate_diagrams": true,
    "diagram_output_dir": "dependency_diagrams",
    "max_diagram_nodes": 100
  },

  "caching": {
    "cache_ttl_seconds": 300,
    "enable_compression": true,
    "compression_threshold": 1024
  }
}
```

---

## Configuration Tips

## 配置技巧 | Configuration Tips

### 1. Start with Defaults

### 1. 从默认值开始

Defaults work well for most projects. Only customize if needed.
默认值适用于大多数项目。仅在需要时进行自定义。

### 2. Exclude Aggressively

### 2. 积极排除

Exclude test files, migrations, generated code:
排除测试文件、迁移文件、生成的代码:

```json
{
  "excluded_file_patterns": [
    "test_*.py",
    "*_test.py",
    "*/migrations/*",
    "*/generated/*"
  ]
}
```

### 3. Tune Thresholds Gradually

### 3. 逐步调整阈值

Adjust in small increments (±0.05) and test:
以小幅度 (±0.05) 调整并测试:

```json
{
  "thresholds": {
    "reranker_promotion_threshold": 0.90  // Was 0.92
  }
}
```

### 4. Monitor Resource Usage

### 4. 监控资源使用

Check logs to see if limits are being hit:
检查日志以查看是否达到限制:

```bash
grep "memory" cline_docs/debug.txt
grep "workers" cline_docs/debug.txt
```

### 5. Use Environment Variables for Testing

### 5. 使用环境变量进行测试

```bash
# Test with different settings
# 使用不同设置进行测试
DEBUG=true MAX_WORKERS=4 python -m cline_utils.dependency_system.dependency_processor analyze-project
```

---

## Validation

## 验证 | Validation

CRCT validates configuration on startup:
CRCT 在启动时验证配置:

```
INFO: Loading configuration from .clinerules.config.json
INFO: Validating settings...
WARNING: max_reranker_scans > 50 may be slow
ERROR: Invalid embedding_device: 'invalid'
INFO: Configuration loaded successfully
```

Fix errors before proceeding.
在继续之前修复错误。

---

## References

## 参考 | References

- [Default Configuration](cline_utils/dependency_system/utils/config_manager.py#L20)
- [默认配置](cline_utils/dependency_system/utils/config_manager.py#L20)

- [Migration Guide](MIGRATION_v7.x_to_v8.0.md)
- [迁移指南](MIGRATION_v7.x_to_v8.0.md)

- [Hardware Optimization](HARDWARE_OPTIMIZATION.md)
- [硬件优化](HARDWARE_OPTIMIZATION.md)

---

**Proper configuration ensures CRCT performs optimally for your specific project and hardware.** Start with defaults and tune as needed based on analysis results.

**适当的配置确保 CRCT 针对您的特定项目和硬件实现最佳性能。** 从默认值开始,并根据分析结果进行调整。
