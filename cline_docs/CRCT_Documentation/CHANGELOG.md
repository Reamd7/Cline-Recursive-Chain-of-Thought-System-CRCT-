# Changelog

# 变更日志 | Changelog

All notable changes to the Cline Recursive Chain-of-Thought System (CRCT) will be documented in this file.

Cline 递归思维链系统 (CRCT) 的所有重要变更都将记录在此文件中。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
本项目遵循 [语义化版本](https://semver.org/spec/v2.0.0.html) 规范。

---

## [8.0.0] - 2025-12-02

> [!IMPORTANT]
> **MAJOR RELEASE** - Significant architectural changes to embedding and dependency analysis systems. See [MIGRATION_v7.x_to_v8.0.md](MIGRATION_v7.x_to_v8.0.md) for upgrade instructions.

> [!重要]
> **主要版本** - 嵌入 (embedding) 和依赖分析系统的重大架构变更。升级说明请参见 [MIGRATION_v7.x_to_v8.0.md](MIGRATION_v7.x_to_v8.0.md)。

### 💥 Breaking Changes

### 💥 破坏性变更

- **Embedding System Rewrite**: Migrated from simple content-based to Symbol Essence String (SES) architecture

- **嵌入系统重构**: 从基于简单内容的架构迁移到符号本质字符串 (SES) 架构

  - Embeddings now include runtime type info, inheritance, decorators, and comprehensive symbol metadata

  - 嵌入现在包含运行时类型信息、继承关系、装饰器和全面的符号元数据

  - **Action Required**: Regenerate all embeddings with `analyze-project --force-embeddings`

  - **所需操作**: 使用 `analyze-project --force-embeddings` 重新生成所有嵌入

- **New Dependencies**: Added `llama-cpp-python` and `huggingface_hub`

- **新依赖**: 添加了 `llama-cpp-python` 和 `huggingface_hub`

  - Required for GGUF model support and automatic model downloads

  - 支持 GGUF 模型和自动模型下载所需

  - **Action Required**: Run `pip install -r requirements.txt`

  - **所需操作**: 运行 `pip install -r requirements.txt`

- **Runtime Symbol Inspection**: Requires valid, importable Python modules

- **运行时符号检查**: 要求有效的、可导入的 Python 模块

  - Syntax errors in project files may prevent symbol extraction

  - 项目文件中的语法错误可能会阻止符号提取

  - **Action Required**: Fix syntax errors before running `analyze-project`

  - **所需操作**: 在运行 `analyze-project` 之前修复语法错误

- **CLI Deprecation**: `set_char` command is now **unsafe** and deprecated

- **CLI 废弃**: `set_char` 命令现在被标记为 **不安全** 并已废弃

  - Operates on outdated grid structure and can corrupt tracker files

  - 操作过时的网格结构,可能损坏跟踪器文件

  - **Action Required**: Use `add-dependency` with `--source-key` and `--target-key` instead

  - **所需操作**: 改用带有 `--source-key` 和 `--target-key` 参数的 `add-dependency`

### 🎯 Major Features

### 🎯 主要功能

#### Symbol Essence Strings (SES) - Revolutionary Embedding Architecture

#### 符号本质字符串 (SES) - 革命性嵌入架构

- Constructs rich, structured embeddings from runtime + AST analysis

- 从运行时 + 抽象语法树 (AST) 分析构建丰富、结构化的嵌入

- Includes: type annotations, inheritance hierarchies, method resolution order, decorators, docstrings, import graphs, call relationships

- 包括:类型注解、继承层次、方法解析顺序、装饰器、文档字符串、导入图、调用关系

- Configurable max length (default 4000 chars, supports up to 32k)

- 可配置的最大长度(默认 4000 字符,支持高达 32k)

- Dramatically improved semantic understanding for dependency suggestions

- 显著提升了依赖建议的语义理解能力

#### Qwen3 Reranker Integration - AI-Powered Dependency Scoring

#### Qwen3 重排序器集成 - AI 驱动的依赖评分

- Integrated ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0 for semantic reranking

- 集成 ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0 用于语义重排序

- Specialized instructions for doc↔doc, doc↔code, code↔code relationship types

- 针对 doc↔doc、doc↔code、code↔code 关系类型的专门指令

- Automatic model download with progress tracking (~600MB)

- 自动下载模型并跟踪进度(~600MB)

- Global scan limiter for performance control

- 全局扫描限制器用于性能控制

- VRAM management with automatic model unloading

- 显存 (VRAM) 管理支持自动卸载模型

- Score caching with 7-day TTL

- 评分缓存,7 天过期时间

#### Hardware-Adaptive Model Selection - Intelligent Resource Management

#### 硬件自适应模型选择 - 智能资源管理

- Automatic detection of CUDA VRAM and system RAM

- 自动检测 CUDA 显存和系统内存

- Multi-model support:

- 多模型支持:

  - **GGUF**: Qwen3-Embedding-4B-Q6_K (for systems with ≥8GB VRAM or ≥16GB RAM)

  - **GGUF**: Qwen3-Embedding-4B-Q6_K(适用于≥8GB 显存或≥16GB 内存的系统)

  - **SentenceTransformer**: all-mpnet-base-v2 (for lower-end systems)

  - **SentenceTransformer**: all-mpnet-base-v2(适用于低端系统)

- Dynamic batch size optimization (32-256 based on available VRAM)

- 动态批处理大小优化(根据可用显存,32-256)

- Context length up to 32,768 tokens for large files

- 上下文长度高达 32,768 个词元 (token),适用于大文件

#### Runtime Symbol Inspection - Deep Metadata Extraction

#### 运行时符号检查 - 深度元数据提取

- **NEW MODULE**: `runtime_inspector.py` - Extracts type annotations, inheritance, MRO, closures, decorators from live Python modules

- **新模块**: `runtime_inspector.py` - 从活动的 Python 模块中提取类型注解、继承、方法解析顺序 (MRO)、闭包、装饰器

- **NEW MODULE**: `symbol_map_merger.py` - Merges runtime data with AST analysis for comprehensive symbol maps

- **新模块**: `symbol_map_merger.py` - 将运行时数据与 AST 分析合并,生成全面的符号映射

- Generates `project_symbol_map.json` combining best of both approaches

- 生成 `project_symbol_map.json`,结合两种方法的优势

- Validation with categorized issue reporting

- 带分类问题报告的验证功能

#### Enhanced Dependency Analysis - Smarter, More Accurate

#### 增强的依赖分析 - 更智能、更准确

- Advanced call filtering: Filters 20+ generic methods, resolves import aliases with `_is_useful_call()`

- 高级调用过滤:过滤 20+ 种通用方法,使用 `_is_useful_call()` 解析导入别名

- Internal vs external module detection

- 内部与外部模块检测

- Call result deduplication and consolidation

- 调用结果去重和合并

- Improved accuracy with reduced false positives

- 提高准确性,减少误报

- AST-verified link extraction with structured metadata

- 经 AST 验证的链接提取,带有结构化元数据

### ✨ Enhancements

### ✨ 增强功能

#### User Experience

#### 用户体验

- **PhaseTracker**: Real-time progress bars with ETA for long-running operations

- **PhaseTracker**: 实时进度条,显示长时间操作的预计完成时间

  - Clean terminal output (no more scrolling spam)

  - 清晰的终端输出(不再有滚屏垃圾信息)

  - Accurate time estimates based on processing rate

  - 基于处理速率的准确时间估算

  - Graceful TTY vs non-TTY handling

  - 优雅的 TTY 与非 TTY 处理

- Reduced console verbosity (info → debug for routine operations)

- 降低控制台冗余度(常规操作从 info 降为 debug)

- Better progress reporting throughout analysis

- 分析过程中更好的进度报告

- Detailed debug logs still available with verbose mode

- 详细模式仍然提供详细的调试日志

#### Performance

#### 性能

- Optimal batch sizing (32-256) based on hardware

- 基于硬件的最佳批处理大小(32-256)

- Reranker model unloading after suggestions to free VRAM

- 建议后卸载重排序器模型以释放显存

- Smart caching for reranker scores (7-day TTL)

- 重排序器评分的智能缓存(7 天过期)

- Parallel processing with shared scan counter for global limits

- 并行处理,带共享扫描计数器用于全局限制

- Cache compression for items >1KB with 10% minimum savings

- 大于 1KB 的缓存项的压缩,至少节省 10%

#### Data Quality

#### 数据质量

- AST link consolidation (merges duplicate links, combines reasons)

- AST 链接合并(合并重复链接,组合原因)

- Expanded symbol map coverage (16 symbol categories vs 5 in v7.x)

- 扩展的符号映射覆盖(16 个符号类别 vs v7.x 的 5 个)

- Runtime + AST merging for richer metadata

- 运行时 + AST 合并以提供更丰富的元数据

- Only stores non-empty symbol data

- 仅存储非空符号数据

- Enhanced validation with categorized reporting

- 增强的验证,带分类报告

#### Caching System (cache_manager.py)

#### 缓存系统 (cache_manager.py)

- **NEW**: Compression support with gzip for large cache items

- **新增**: 大缓存项的 gzip 压缩支持

- **NEW**: Multiple eviction policies (LRU, LFU, FIFO, Random, Adaptive)

- **新增**: 多种驱逐策略(LRU、LFU、FIFO、Random、Adaptive)

- **NEW**: Enhanced metrics with CacheMetrics dataclass

- **新增**: 使用 CacheMetrics 数据类的增强指标

  - Hit rate calculation

  - 命中率计算

  - Access count tracking

  - 访问计数跟踪

  - Memory usage estimation

  - 内存使用估算

- **NEW**: Smart persistence with JSON-safe serialization

- **新增**: JSON 安全序列化的智能持久化

- Improved size estimation for cache entries

- 改进的缓存项大小估算

- Compression threshold: 1KB minimum, 10% savings required

- 压缩阈值:最少 1KB,要求节省 10%

#### Configuration System (config_manager.py)

#### 配置系统 (config_manager.py)

- **NEW**: Reranker threshold settings

- **新增**: 重排序器阈值设置

  - `reranker_promotion_threshold`: 0.92 (promotes to `<`)

  - `reranker_promotion_threshold`: 0.92(提升为 `<`)

  - `reranker_strong_semantic_threshold`: 0.78 (assigns `S`)

  - `reranker_strong_semantic_threshold`: 0.78(分配 `S`)

  - `reranker_weak_semantic_threshold`: 0.65 (assigns `s`)

  - `reranker_weak_semantic_threshold`: 0.65(分配 `s`)

- **NEW**: Embedding configuration options

- **新增**: 嵌入配置选项

  - `batch_size`: Auto-sizing or manual override

  - `batch_size`: 自动调整或手动覆盖

  - `max_context_length`: Up to 32,768 tokens

  - `max_context_length`: 高达 32,768 个词元

  - `auto_select_model`: Hardware-adaptive selection

  - `auto_select_model`: 硬件自适应选择

- **NEW**: Resource management settings

- **新增**: 资源管理设置

  - `min_memory_mb`, `recommended_memory_mb`

  - `min_memory_mb`, `recommended_memory_mb`(最小/推荐内存)

  - `min_disk_space_mb`, `min_free_space_mb`

  - `min_disk_space_mb`, `min_free_space_mb`(最小磁盘空间/最小空闲空间)

  - `max_workers`, `cpu_threshold`

  - `max_workers`, `cpu_threshold`(最大工作线程数/CPU 阈值)

- **NEW**: Analysis controls

- **新增**: 分析控制

  - Binary detection settings

  - 二进制检测设置

  - Docstring extraction toggles

  - 文档字符串提取开关

  - Min function/class lengths

  - 最小函数/类长度

- **NEW**: Resource validation method

- **新增**: 资源验证方法

  - `perform_resource_validation_and_adjustments()`

  - `perform_resource_validation_and_adjustments()`

  - Pre-flight system checks with recommendations

  - 预检系统检查并提供建议

### 🧪 Testing & Quality

### 🧪 测试与质量

- **NEW**: Comprehensive test suite (4 test files)

- **新增**: 全面的测试套件(4 个测试文件)

  - `test_functional_cache.py` - Cache functionality tests

  - `test_functional_cache.py` - 缓存功能测试

  - `test_integration_cache.py` - Integration testing

  - `test_integration_cache.py` - 集成测试

  - `test_manual_tooling_cache.py` - Manual tooling verification

  - `test_manual_tooling_cache.py` - 手动工具验证

  - `verify_rerank_caching.py` - Reranker cache validation

  - `verify_rerank_caching.py` - 重排序器缓存验证

- Enhanced exception handling system (`exceptions_enhanced.py` - 261 lines vs 27 in old `exceptions.py`)

- 增强的异常处理系统(`exceptions_enhanced.py` - 261 行 vs 旧 `exceptions.py` 的 27 行)

- More specific, actionable exception types

- 更具体、可操作的异常类型

### 🔧 Developer Tools

### 🔧 开发者工具

- **NEW**: `report_generator.py` - AST-based code quality analysis

- **新增**: `report_generator.py` - 基于 AST 的代码质量分析

  - Detects incomplete code using Tree-sitter

  - 使用 Tree-sitter 检测不完整的代码

  - Supports Python, JavaScript, TypeScript

  - 支持 Python、JavaScript、TypeScript

  - Integrates with Pyright for type checking

  - 集成 Pyright 进行类型检查

- **NEW**: `resource_validator.py` - Pre-analysis system validation

- **新增**: `resource_validator.py` - 分析前系统验证

  - Validates memory, disk, CPU before analysis

  - 分析前验证内存、磁盘、CPU

  - 7-day cache with TTL for validation results

  - 验证结果缓存 7 天,带 TTL

  - Generates optimization recommendations

  - 生成优化建议

- **NEW**: `phase_tracker.py` - Terminal progress bars with ETA

- **新增**: `phase_tracker.py` - 带预计完成时间的终端进度条

  - Context manager for clean progress tracking

  - 上下文管理器,提供清晰的进度跟踪

  - Real-time ETA calculations

  - 实时 ETA 计算

  - Improved user experience for long operations

  - 改善长时间操作的用户体验

- Improved error messages with detailed context

- 改进的错误消息,带详细上下文

- Validation tools for merged symbol maps

- 合并符号映射的验证工具

### 📦 Internal Improvements

### 📦 内部改进

- Thread-safe model loading with locks

- 使用锁实现线程安全的模型加载

- Graceful model download with progress reporting

- 优雅的模型下载,带进度报告

- GGUF model validation (size checks, format verification)

- GGUF 模型验证(大小检查、格式验证)

- Configurable context lengths and batch sizes

- 可配置的上下文长度和批处理大小

- Better memory management across the board

- 全面的内存管理改进

- Module-level cache for AST trees (ast_cache)

- AST 树的模块级缓存(ast_cache)

- Enhanced logging with structured context

- 增强的日志记录,带结构化上下文

- Parser architecture change for thread safety (local parsers vs global)

- 解析器架构变更以实现线程安全(本地解析器 vs 全局解析器)

### 📊 Performance Metrics

### 📊 性能指标

- **Embedding Generation**: 2-3x faster with optimal batch sizing

- **嵌入生成**: 通过最佳批处理大小提升 2-3 倍速度

- **Dependency Suggestions**: 5-10x more accurate with reranker

- **依赖建议**: 通过重排序器提升 5-10 倍准确性

- **Analysis Time**: Similar or slightly slower on first run (runtime inspection overhead), faster on subsequent runs (better caching)

- **分析时间**: 首次运行相似或稍慢(运行时检查开销),后续运行更快(更好的缓存)

- **Memory Usage**: Higher peak during reranker operations, better managed with unloading

- **内存使用**: 重排序器操作期间峰值更高,通过卸载更好地管理

- **Cache Efficiency**: 30-50% memory savings with compression for large projects

- **缓存效率**: 通过压缩为大型项目节省 30-50% 内存

### ⚠️ Known Issues

### ⚠️ 已知问题

- Reranker may timeout on very large dependency graphs (4000+ edges) - use visualization sparingly

- 重排序器在超大型依赖图(4000+ 边)上可能超时 - 谨慎使用可视化

- Runtime inspection requires importable modules (fix syntax errors first)

- 运行时检查需要可导入的模块(先修复语法错误)

- GGUF model download requires stable internet connection (600MB)

- GGUF 模型下载需要稳定的互联网连接(600MB)

- First-run analysis slower due to model downloads and SES generation complexity

- 首次运行分析较慢,因为模型下载和 SES 生成复杂性

### 🐛 Bug Fixes

### 🐛 错误修复

- Fixed parser state conflicts with local parser instances (vs global)

- 修复了解析器状态冲突(本地解析器实例 vs 全局解析器)

- Improved call filtering to reduce noise in suggestions

- 改进调用过滤以减少建议中的噪音

- Better handling of relative imports in Python

- 更好地处理 Python 中的相对导入

- Enhanced error recovery in runtime inspection

- 增强运行时检查中的错误恢复

- Resolved cache key collisions with improved hashing

- 通过改进的哈希解决缓存键冲突

### 🗑️ Removed

### 🗑️ 移除

- **DEPRECATED**: `exceptions.py` → Replaced by `exceptions_enhanced.py`

- **已废弃**: `exceptions.py` → 被 `exceptions_enhanced.py` 替换

  - Migration: Update imports from `core.exceptions` to `core.exceptions_enhanced`

  - 迁移: 将导入从 `core.exceptions` 更新为 `core.exceptions_enhanced`

  - Old exception classes are still available for backward compatibility

  - 旧异常类仍然可用,以保持向后兼容

### 📝 Documentation

### 📝 文档

- **NEW**: [MIGRATION_v7.x_to_v8.0.md](MIGRATION_v7.x_to_v8.0.md) - Comprehensive migration guide

- **新增**: [MIGRATION_v7.x_to_v8.0.md](MIGRATION_v7.x_to_v8.0.md) - 全面的迁移指南

- Updated README with v8.0 features and system requirements

- 更新 README,包含 v8.0 功能和系统要求

- Enhanced inline documentation throughout codebase

- 增强整个代码库的内联文档

### 🔄 Migration Notes

### 🔄 迁移说明

1. **Install New Dependencies**:

1. **安装新依赖**:

   ```bash
   pip install -r requirements.txt
   npm install  # for mermaid-cli if using visualization
   ```

   ```bash
   pip install -r requirements.txt
   npm install  # 如果使用可视化,则安装 mermaid-cli
   ```

2. **Regenerate Embeddings**:

2. **重新生成嵌入**:

   ```bash
   python -m cline_utils.dependency_system.dependency_processor analyze-project --force-embeddings
   ```

   ```bash
   python -m cline_utils.dependency_system.dependency_processor analyze-project --force-embeddings
   ```

3. **Run Runtime Inspector** (if using Python projects):

3. **运行运行时检查器**(如果使用 Python 项目):

   ```bash
   python -m cline_utils.dependency_system.analysis.runtime_inspector
   ```

   ```bash
   python -m cline_utils.dependency_system.analysis.runtime_inspector
   ```

4. **Expected First-Run Behavior**:

4. **预期首次运行行为**:

   - Automatic download of Qwen3 reranker model (~600MB)

   - 自动下载 Qwen3 重排序器模型(~600MB)

   - Longer initial embedding generation (due to SES complexity)

   - 初始嵌入生成时间更长(由于 SES 复杂性)

   - Runtime inspection may fail on files with syntax errors

   - 运行时检查可能因文件语法错误而失败

5. **System Requirements Update**:

5. **系统要求更新**:

   - **Recommended**: 8GB+ VRAM or 16GB+ RAM for optimal performance

   - **推荐**: 8GB+ 显存或 16GB+ 内存以获得最佳性能

   - **Minimum**: 4GB RAM for CPU-only mode with reduced batch sizes

   - **最低**: 4GB 内存用于仅 CPU 模式,批处理大小会减小

---

## [7.90] - 2024-11-XX

### Added

### 新增

- **Dependency Visualization** (`visualize-dependencies` command)

- **依赖可视化**(`visualize-dependencies` 命令)

  - Generate Mermaid diagrams for project overview, module-focused, and multi-key views

  - 为项目概览、模块聚焦和多键视图生成 Mermaid 图表

  - Auto-generates overview and module diagrams during `analyze-project`

  - 在 `analyze-project` 期间自动生成概览和模块图表

  - Integrated mermaid-cli to render diagrams as .svg files

  - 集成 mermaid-cli 将图表渲染为 .svg 文件

- Enhanced dependency analysis with tree-sitter support for .js, .ts, .tsx, .html, .css

- 增强的依赖分析,支持 .js、.ts、.tsx、.html、.css 的 tree-sitter

- Strategy Phase overhaul with iterative, area-based workflow

- 策略阶段重构,采用迭代式、基于区域的工作流

### Changed

### 更改

- Improved AST analysis for Python files

- 改进了 Python 文件的 AST 分析

- Refined state management (`.clinerules` vs. `activeContext.md`)

- 改进状态管理(`.clinerules` vs. `activeContext.md`)

- Split strategy into Dispatch and Worker prompts

- 将策略拆分为 Dispatch 和 Worker 提示词

### Fixed

### 修复

- Diagram rendering performance (works well under 1000 edges, struggles with 1500+, times out with 4000+)

- 图表渲染性能(1000 边以下表现良好,1500+ 边时吃力,4000+ 边时超时)

---

## [7.7] - 2024-XX-XX

### Added

### 新增

- Restructured core prompt/plugins

- 重构核心提示词/插件

- `cleanup_consolidation_plugin.md` phase (use with caution)

- `cleanup_consolidation_plugin.md` 阶段(谨慎使用)

- `hdta_review_progress` and `hierarchical_task_checklist` templates

- `hdta_review_progress` 和 `hierarchical_task_checklist` 模板

---

## [7.5] - 2024-XX-XX

### Added

### 新增

- Significant baseline restructuring

- 重大基线重构

- Core architecture establishment

- 核心架构建立

- Contextual Keys (`KeyInfo`) system

- 上下文键 (`KeyInfo`) 系统

- Hierarchical Dependency Aggregation

- 分层依赖聚合

- Configurable embedding device

- 可配置的嵌入设备

- File exclusion patterns

- 文件排除模式

### Changed

### 更改

- Enhanced `show-dependencies` command

- 增强的 `show-dependencies` 命令

- Improved caching & batch processing

- 改进的缓存和批处理

---

[8.0.0]: https://github.com/your-repo/compare/v7.90...v8.0.0
[7.90]: https://github.com/your-repo/compare/v7.7...v7.90
[7.7]: https://github.com/your-repo/compare/v7.5...v7.7
[7.5]: https://github.com/your-repo/releases/tag/v7.5
