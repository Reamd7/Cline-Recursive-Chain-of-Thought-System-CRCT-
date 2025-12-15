# 配置参考

> [!TIP]
> 这是v8.0中所有配置选项的综合参考。大多数用户可以使用默认值，但本指南有助于针对特定需求微调CRCT。

## 配置文件

**位置**: `.clinerules.config.json`（项目根目录）

**格式**: JSON

**自动创建**: 如果缺失，使用默认值

---

## 快速开始

### 最小配置

```json
{
  "code_roots": ["src/", "lib/"],
  "excluded_dirs": ["node_modules", "__pycache__"]
}
```

### 推荐配置

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

## 核心设置

### code_roots

**类型**: `Array<string>`
**默认值**: 从项目结构自动检测
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

**注意事项**:
- 相对于项目根目录的路径
- 仅分析这些目录中的文件
- 自动包含子目录

### excluded_dirs

**类型**: `Array<string>`
**默认值**: 见下文
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

**类型**: `Array<string>`
**默认值**: 二进制和编译文件扩展名
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

**类型**: `Array<string>`
**默认值**: `[]`
**描述**: 要排除的文件的glob模式

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

## 阈值设置

### reranker_promotion_threshold

**类型**: `float` (0.0-1.0)
**默认值**: `0.92`
**描述**: 提升为结构依赖（`<`）的分数阈值

**用法**:
```json
{
  "thresholds": {
    "reranker_promotion_threshold": 0.95  // 更严格
  }
}
```

**建议**:
- **严格**（更少依赖）: `0.95-0.98`
- **平衡**: `0.90-0.94`（默认）
- **宽松**（更多依赖）: `0.85-0.89`

### reranker_strong_semantic_threshold

**类型**: `float` (0.0-1.0)
**默认值**: `0.78`
**描述**: 强语义依赖（`S`）的阈值

**建议**:
- **严格**: `0.85+`
- **平衡**: `0.75-0.82`（默认）
- **宽松**: `0.65-0.74`

### reranker_weak_semantic_threshold

**类型**: `float` (0.0-1.0)
**默认值**: `0.65`
**描述**: 弱语义依赖（`s`）的阈值

**建议**:
- **严格**: `0.75+`
- **平衡**: `0.60-0.70`（默认）
- **宽松**: `0.50-0.59`

---

## 分析设置

### max_reranker_scans

**类型**: `integer`
**默认值**: `20`
**描述**: 每个文件要重排序的最大文件对数

```json
{
  "analysis": {
    "max_reranker_scans": 10  // 更快，不够彻底
  }
}
```

**影响**:
- 更高 = 更准确，更慢
- 更低 = 更快，可能错过依赖关系

### reranker_enabled

**类型**: `boolean`
**默认值**: `true`
**描述**: 启用/禁用重排序器

```json
{
  "analysis": {
    "reranker_enabled": false  // 禁用以提高速度
  }
}
```

### runtime_inspection_enabled

**类型**: `boolean`
**默认值**: `true`
**描述**: 启用运行时符号检查

```json
{
  "analysis": {
    "runtime_inspection_enabled": true
  }
}
```

### runtime_inspection_timeout

**类型**: `integer`（秒）
**默认值**: `30`
**描述**: 每个模块运行时检查的最大时间

```json
{
  "analysis": {
    "runtime_inspection_timeout": 10  // 更严格的超时
  }
}
```

---

## 嵌入设置

### auto_select_model

**类型**: `boolean`
**默认值**: `true`
**描述**: 自动选择最佳嵌入模型

```json
{
  "embedding": {
    "auto_select_model": true  // 推荐
  }
}
```

### batch_size

**类型**: `integer | "auto"`
**默认值**: `"auto"`
**描述**: 嵌入生成的批次大小

```json
{
  "embedding": {
    "batch_size": 128  // 固定大小
  }
}
```

**自动调整**（推荐）:
- 6GB+ 显存: 256
- 4GB+ 显存: 128
- 2GB+ 显存: 64
- CPU/低显存: 32

### max_context_length

**类型**: `integer`
**默认值**: `32768`
**描述**: 嵌入的最大令牌数

```json
{
  "embedding": {
    "max_context_length": 16384  // 更短以提高速度
  }
}
```

### ses_max_chars

**类型**: `integer`
**默认值**: `4000`
**描述**: 符号本质字符串的最大字符数

```json
{
  "embedding": {
    "ses_max_chars": 8000  // 更大以容纳非常详细的符号
  }
}
```

---

## 计算设置

### embedding_device

**类型**: `"auto" | "cuda" | "mps" | "cpu"`
**默认值**: `"auto"`
**描述**: 嵌入计算的设备

```json
{
  "compute": {
    "embedding_device": "cuda"  // 强制使用CUDA
  }
}
```

**选项**:
- `"auto"`: 检测最佳可用设备
- `"cuda"`: NVIDIA GPU
- `"mps"`: Apple Silicon GPU
- `"cpu"`: 仅CPU

---

## 资源设置

### min_memory_mb

**类型**: `integer`
**默认值**: `512`
**描述**: 所需的最小RAM（低于此值会发出警告）

```json
{
  "resources": {
    "min_memory_mb": 1024
  }
}
```

### recommended_memory_mb

**类型**: `integer`
**默认值**: `2048`
**描述**: 最佳性能的推荐RAM

### max_workers

**类型**: `integer | "auto"`
**默认值**: `"auto"`（cpu_count * 4，最大64）
**描述**: 最大并行工作线程数

```json
{
  "resources": {
    "max_workers": 8  // 限制并行度
  }
}
```

---

## 输出设置

### auto_generate_diagrams

**类型**: `boolean`
**默认值**: `true`
**描述**: 自动生成依赖图表

```json
{
  "output": {
    "auto_generate_diagrams": true
  }
}
```

### diagram_output_dir

**类型**: `string`
**默认值**: `"dependency_diagrams"`
**描述**: 生成图表的目录

```json
{
  "output": {
    "diagram_output_dir": "docs/diagrams"
  }
}
```

### max_diagram_nodes

**类型**: `integer`
**默认值**: `100`
**描述**: 生成图表中的最大节点数

```json
{
  "output": {
    "max_diagram_nodes": 50  // 更简单的图表
  }
}
```

---

## 路径设置

### doc_dir

**类型**: `string`
**默认值**: `"docs"`
**描述**: 文档目录

### memory_dir

**类型**: `string`
**默认值**: `"cline_docs"`
**描述**: 系统内存/状态目录

### embeddings_dir

**类型**: `string`
**默认值**: `"cline_utils/dependency_system/analysis/embeddings"`
**描述**: 嵌入存储目录

---

## 可视化设置

### auto_diagram_output_dir

**类型**: `string | null`
**默认值**: `null`
**描述**: 自动图表输出位置

```json
{
  "visualization": {
    "auto_diagram_output_dir": "cline_docs/dependency_diagrams"
  }
}
```

### max_edges_for_visualization

**类型**: `integer`
**默认值**: `1500`
**描述**: 发出警告前的最大边数

```json
{
  "visualization": {
    "max_edges_for_visualization": 1000
  }
}
```

---

## 缓存设置

### cache_ttl_seconds

**类型**: `integer`
**默认值**: `300`（5分钟）
**描述**: 默认缓存生存时间

```json
{
  "caching": {
    "cache_ttl_seconds": 600  // 10分钟
  }
}
```

### enable_compression

**类型**: `boolean`
**默认值**: `true`
**描述**: 启用缓存压缩

### compression_threshold

**类型**: `integer`
**默认值**: `1024`（1KB）
**描述**: 压缩的最小大小

---

## 环境变量

CRCT还支持通过环境变量进行配置：

### EMBEDDING_MODEL

覆盖自动模型选择：
```bash
export EMBEDDING_MODEL="all-mpnet-base-v2"
```

### EMBEDDING_DEVICE

强制使用特定设备：
```bash
export EMBEDDING_DEVICE="cuda"
```

### MAX_WORKERS

设置工作线程数：
```bash
export MAX_WORKERS=16
```

### USE_STREAMING

启用流式模式：
```bash
export USE_STREAMING=true
```

### DEBUG

启用调试日志：
```bash
export DEBUG=true
```

---

## 完整示例

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

## 配置提示

### 1. 从默认值开始

默认值适用于大多数项目。仅在需要时自定义。

### 2. 积极排除

排除测试文件、迁移、生成的代码：
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

### 3. 逐步调整阈值

以小增量（±0.05）调整并测试：
```json
{
  "thresholds": {
    "reranker_promotion_threshold": 0.90  // 原为0.92
  }
}
```

### 4. 监控资源使用

检查日志以查看是否达到限制：
```bash
grep "memory" cline_docs/debug.txt
grep "workers" cline_docs/debug.txt
```

### 5. 使用环境变量进行测试

```bash
# 使用不同设置进行测试
DEBUG=true MAX_WORKERS=4 python -m cline_utils.dependency_system.dependency_processor analyze-project
```

---

## 验证

CRCT在启动时验证配置：

```
INFO: Loading configuration from .clinerules.config.json
INFO: Validating settings...
WARNING: max_reranker_scans > 50 may be slow
ERROR: Invalid embedding_device: 'invalid'
INFO: Configuration loaded successfully
```

在继续之前修复错误。

---

## 参考资料

- [默认配置](cline_utils/dependency_system/utils/config_manager.py#L20)
- [迁移指南](MIGRATION_v7.x_to_v8.0.md)
- [硬件优化](HARDWARE_OPTIMIZATION.md)

---

**正确的配置可确保CRCT针对您的特定项目和硬件进行最佳性能。** 从默认值开始，根据分析结果根据需要进行调整。
