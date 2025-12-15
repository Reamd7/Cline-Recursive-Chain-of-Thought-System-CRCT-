# 变更日志

Cline递归思维链系统（CRCT）的所有重要变更都将记录在此文件中。

格式基于[Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
本项目遵循[语义化版本控制](https://semver.org/spec/v2.0.0.html)。

---

## [8.0.0] - 2025-12-02

> [!IMPORTANT]
> **重大版本** - 嵌入和依赖分析系统的重大架构变更。升级说明请参见[MIGRATION_v7.x_to_v8.0.md](MIGRATION_v7.x_to_v8.0.md)。

### 💥 重大变更

- **嵌入系统重写**: 从简单的基于内容的方式迁移到符号本质字符串（Symbol Essence String, SES）架构
  - 嵌入现在包括运行时类型信息、继承、装饰器和全面的符号元数据
  - **需要操作**: 使用`analyze-project --force-embeddings`重新生成所有嵌入

- **新增依赖**: 添加了`llama-cpp-python`和`huggingface_hub`
  - GGUF模型支持和自动模型下载所需
  - **需要操作**: 运行`pip install -r requirements.txt`

- **运行时符号检查**: 需要有效的、可导入的Python模块
  - 项目文件中的语法错误可能阻止符号提取
  - **需要操作**: 在运行`analyze-project`之前修复语法错误

- **CLI弃用**: `set_char`命令现在**不安全**并已弃用
  - 在过时的网格结构上操作，可能损坏跟踪器文件
  - **需要操作**: 使用带有`--source-key`和`--target-key`的`add-dependency`替代

### 🎯 主要特性

#### 符号本质字符串（SES）- 革命性的嵌入架构
- 从运行时 + AST分析构建丰富的、结构化的嵌入
- 包括：类型注解、继承层次、方法解析顺序、装饰器、文档字符串、导入图、调用关系
- 可配置最大长度（默认4000字符，支持最高32k）
- 显著提高依赖建议的语义理解

#### Qwen3重排序器集成 - AI驱动的依赖评分
- 集成ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0用于语义重排序
- 针对doc↔doc、doc↔code、code↔code关系类型的专门指令
- 自动模型下载，带进度跟踪（约600MB）
- 全局扫描限制器，用于性能控制
- 显存管理，自动卸载模型
- 分数缓存，7天TTL

#### 硬件自适应模型选择 - 智能资源管理
- 自动检测CUDA显存和系统内存
- 多模型支持：
  - **GGUF**: Qwen3-Embedding-4B-Q6_K（适用于≥8GB显存或≥16GB内存的系统）
  - **SentenceTransformer**: all-mpnet-base-v2（适用于低端系统）
- 动态批次大小优化（基于可用显存的32-256）
- 大文件的上下文长度最高32,768个令牌

#### 运行时符号检查 - 深度元数据提取
- **新模块**: `runtime_inspector.py` - 从活动Python模块中提取类型注解、继承、MRO、闭包、装饰器
- **新模块**: `symbol_map_merger.py` - 合并运行时数据与AST分析以获得全面的符号映射
- 生成`project_symbol_map.json`，结合两种方法的优点
- 带分类问题报告的验证

#### 增强依赖分析 - 更智能、更准确
- 高级调用过滤：过滤20+个通用方法，使用`_is_useful_call()`解析导入别名
- 内部与外部模块检测
- 调用结果去重和合并
- 提高准确性，减少误报
- AST验证的链接提取，带结构化元数据

### ✨ 增强

#### 用户体验
- **PhaseTracker**: 长时间运行操作的实时进度条和预计完成时间
  - 清晰的终端输出（不再滚动刷屏）
  - 基于处理速率的准确时间估计
  - 优雅的TTY与非TTY处理
- 减少控制台冗长度（常规操作从info → debug）
- 整个分析过程中更好的进度报告
- 详细的调试日志仍可通过详细模式获得

#### 性能
- 基于硬件的最佳批次大小（32-256）
- 建议后卸载重排序器模型以释放显存
- 重排序器分数的智能缓存（7天TTL）
- 并行处理，共享扫描计数器用于全局限制
- >1KB项目的缓存压缩，至少节省10%

#### 数据质量
- AST链接合并（合并重复链接，组合原因）
- 扩展的符号映射覆盖范围（16个符号类别 vs v7.x中的5个）
- 运行时 + AST合并以获得更丰富的元数据
- 仅存储非空符号数据
- 带分类报告的增强验证

#### 缓存系统（cache_manager.py）
- **新增**: 使用gzip压缩大型缓存项
- **新增**: 多种驱逐策略（LRU、LFU、FIFO、Random、Adaptive）
- **新增**: 使用CacheMetrics数据类的增强指标
  - 命中率计算
  - 访问计数跟踪
  - 内存使用估算
- **新增**: 使用JSON安全序列化的智能持久化
- 改进缓存条目的大小估算
- 压缩阈值：1KB最小值，需要节省10%

#### 配置系统（config_manager.py）
- **新增**: 重排序器阈值设置
  - `reranker_promotion_threshold`: 0.92（提升为`<`）
  - `reranker_strong_semantic_threshold`: 0.78（分配`S`）
  - `reranker_weak_semantic_threshold`: 0.65（分配`s`）
- **新增**: 嵌入配置选项
  - `batch_size`: 自动调整或手动覆盖
  - `max_context_length`: 最高32,768个令牌
  - `auto_select_model`: 硬件自适应选择
- **新增**: 资源管理设置
  - `min_memory_mb`、`recommended_memory_mb`
  - `min_disk_space_mb`、`min_free_space_mb`
  - `max_workers`、`cpu_threshold`
- **新增**: 分析控制
  - 二进制检测设置
  - 文档字符串提取切换
  - 最小函数/类长度
- **新增**: 资源验证方法
  - `perform_resource_validation_and_adjustments()`
  - 带建议的飞行前系统检查

### 🧪 测试与质量

- **新增**: 全面的测试套件（4个测试文件）
  - `test_functional_cache.py` - 缓存功能测试
  - `test_integration_cache.py` - 集成测试
  - `test_manual_tooling_cache.py` - 手动工具验证
  - `verify_rerank_caching.py` - 重排序器缓存验证
- 增强的异常处理系统（`exceptions_enhanced.py` - 261行 vs 旧`exceptions.py`的27行）
- 更具体、可操作的异常类型

### 🔧 开发者工具

- **新增**: `report_generator.py` - 基于AST的代码质量分析
  - 使用Tree-sitter检测不完整代码
  - 支持Python、JavaScript、TypeScript
  - 与Pyright集成进行类型检查
- **新增**: `resource_validator.py` - 分析前系统验证
  - 分析前验证内存、磁盘、CPU
  - 7天缓存，带TTL的验证结果
  - 生成优化建议
- **新增**: `phase_tracker.py` - 带预计完成时间的终端进度条
  - 用于清晰进度跟踪的上下文管理器
  - 实时预计完成时间计算
  - 改善长时间操作的用户体验
- 改进的错误消息，带详细上下文
- 合并符号映射的验证工具

### 📦 内部改进

- 使用锁的线程安全模型加载
- 带进度报告的优雅模型下载
- GGUF模型验证（大小检查、格式验证）
- 可配置的上下文长度和批次大小
- 全面更好的内存管理
- AST树的模块级缓存（ast_cache）
- 带结构化上下文的增强日志记录
- 解析器架构变更以实现线程安全（本地解析器 vs 全局）

### 📊 性能指标

- **嵌入生成**: 通过最佳批次大小快2-3倍
- **依赖建议**: 使用重排序器准确性提高5-10倍
- **分析时间**: 首次运行时相似或稍慢（运行时检查开销），后续运行更快（更好的缓存）
- **内存使用**: 重排序器操作期间峰值更高，通过卸载管理更好
- **缓存效率**: 大型项目通过压缩节省30-50%内存

### ⚠️ 已知问题

- 重排序器可能在非常大的依赖图（4000+边）上超时 - 谨慎使用可视化
- 运行时检查需要可导入的模块（首先修复语法错误）
- GGUF模型下载需要稳定的互联网连接（600MB）
- 首次运行分析较慢，因为模型下载和SES生成复杂性

### 🐛 错误修复

- 修复了使用本地解析器实例（vs 全局）的解析器状态冲突
- 改进了调用过滤以减少建议中的噪音
- 更好地处理Python中的相对导入
- 增强了运行时检查中的错误恢复
- 解决了通过改进哈希的缓存键冲突

### 🗑️ 移除

- **已弃用**: `exceptions.py` → 由`exceptions_enhanced.py`替换
  - 迁移：将导入从`core.exceptions`更新为`core.exceptions_enhanced`
  - 旧异常类仍可用于向后兼容

### 📝 文档

- **新增**: [MIGRATION_v7.x_to_v8.0.md](MIGRATION_v7.x_to_v8.0.md) - 全面的迁移指南
- 更新README，添加v8.0功能和系统要求
- 整个代码库中增强的内联文档

### 🔄 迁移说明

1. **安装新依赖**:
   ```bash
   pip install -r requirements.txt
   npm install  # 如果使用可视化，用于mermaid-cli
   ```

2. **重新生成嵌入**:
   ```bash
   python -m cline_utils.dependency_system.dependency_processor analyze-project --force-embeddings
   ```

3. **运行运行时检查器**（如果使用Python项目）:
   ```bash
   python -m cline_utils.dependency_system.analysis.runtime_inspector
   ```

4. **预期的首次运行行为**:
   - 自动下载Qwen3重排序器模型（约600MB）
   - 更长的初始嵌入生成（由于SES复杂性）
   - 运行时检查可能在有语法错误的文件上失败

5. **系统要求更新**:
   - **推荐**: 8GB+显存或16GB+内存以获得最佳性能
   - **最低**: 4GB内存用于仅CPU模式，批次大小减少

---

## [7.90] - 2024-11-XX

### 新增
- **依赖可视化**（`visualize-dependencies`命令）
  - 生成项目概览、模块聚焦和多键视图的Mermaid图表
  - `analyze-project`期间自动生成概览和模块图表
  - 集成mermaid-cli以将图表渲染为.svg文件
- 使用tree-sitter支持.js、.ts、.tsx、.html、.css增强依赖分析
- 策略阶段全面改进，采用迭代的、基于区域的工作流

### 变更
- 改进了Python文件的AST分析
- 完善了状态管理（`.clinerules` vs. `activeContext.md`）
- 将策略拆分为调度和工作提示

### 修复
- 图表渲染性能（在边数小于1000时表现良好，超过1500时吃力，超过4000时超时）

---

## [7.7] - 2024-XX-XX

### 新增
- 重构核心提示/插件
- `cleanup_consolidation_plugin.md`阶段（谨慎使用）
- `hdta_review_progress`和`hierarchical_task_checklist`模板

---

## [7.5] - 2024-XX-XX

### 新增
- 重大基础重构
- 核心架构建立
- 上下文键（`KeyInfo`）系统
- 分层依赖聚合
- 可配置嵌入设备
- 文件排除模式

### 变更
- 增强`show-dependencies`命令
- 改进缓存和批处理

---

[8.0.0]: https://github.com/your-repo/compare/v7.90...v8.0.0
[7.90]: https://github.com/your-repo/compare/v7.7...v7.90
[7.7]: https://github.com/your-repo/compare/v7.5...v7.7
[7.5]: https://github.com/your-repo/releases/tag/v7.5
