# Analysis 模块详细中文文档
# Analysis Modules - Detailed Chinese Documentation

> **创建日期**: 2025-12-15
> **文档版本**: 1.0.0
> **适用系统**: Cline Recursive Chain-of-Thought System (CRCT)

---

## 📋 目录 (Table of Contents)

1. [模块概述](#模块概述)
2. [project_analyzer.py - 项目分析器](#1-project_analyzerpy---项目分析器)
3. [embedding_manager.py - 嵌入管理器](#2-embedding_managerpy---嵌入管理器)
4. [dependency_analyzer.py - 依赖分析器](#3-dependency_analyzerpy---依赖分析器)
5. [dependency_suggester.py - 依赖建议器](#4-dependency_suggesterpy---依赖建议器)
6. [数据流程图](#数据流程图)
7. [最佳实践](#最佳实践)

---

## 模块概述

### 系统架构 (System Architecture)

分析模块是整个CRCT依赖系统的核心,由四个主要模块组成:

```
┌─────────────────────────────────────────────────────────┐
│                   PROJECT ANALYZER                       │
│                  (项目分析器 - 总协调器)                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   EMBEDDING  │  │  DEPENDENCY  │  │  DEPENDENCY  │  │
│  │   MANAGER    │  │   ANALYZER   │  │  SUGGESTER   │  │
│  │  (嵌入管理器)  │  │  (依赖分析器) │  │  (依赖建议器) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
         ↓                  ↓                  ↓
    ┌─────────┐      ┌──────────┐      ┌───────────┐
    │ Vectors │      │ AST Tree │      │ Suggested │
    │ Embeddings│    │ Analysis │      │Dependencies│
    └─────────┘      └──────────┘      └───────────┘
```

### 核心职责分工

| 模块 | 职责 | 输入 | 输出 |
|-----|------|------|------|
| **project_analyzer** | 总协调器,编排整个分析流程 | 项目路径, 配置 | 完整分析结果 |
| **embedding_manager** | 生成和管理文件嵌入向量 | 文件内容, 符号映射 | 向量表示 |
| **dependency_analyzer** | 解析文件,提取依赖信息 | 源文件 | AST分析结果 |
| **dependency_suggester** | 建议依赖关系 | 分析结果, 嵌入 | 依赖建议列表 |

---

## 1. project_analyzer.py - 项目分析器

### 📖 模块说明

**文件**: `cline_utils/dependency_system/analysis/project_analyzer.py`
**行数**: ~1,409 行
**核心功能**: 整个依赖分析系统的总协调器和入口点

### 🎯 核心功能

#### 1.1 主函数: `analyze_project()`

**函数签名**:
```python
def analyze_project(
    force_analysis: bool = False,
    force_embeddings: bool = False
) -> Dict[str, Any]:
```

**完整工作流程**:

```
1. 初始化设置
   ├─ 重置统计信息
   ├─ 加载配置
   └─ 确定项目根目录

2. 密钥生成阶段
   ├─ 为所有文件/目录生成唯一密钥
   ├─ 处理路径迁移
   └─ 检测新增密钥

3. 文件识别与过滤
   ├─ 应用排除规则
   ├─ 识别代码根目录
   └─ 构建文件列表

4. 文件分析阶段 (并行)
   ├─ Python: AST + Tree-sitter
   ├─ JavaScript/TypeScript: Tree-sitter
   ├─ HTML/CSS: Tree-sitter
   └─ Markdown: Regex

5. 符号映射生成
   ├─ 收集所有符号定义
   ├─ 合并运行时符号
   ├─ 验证符号完整性
   └─ 保存符号映射文件

6. 嵌入向量生成
   ├─ 生成SES (Symbol Essence String)
   ├─ 选择最佳模型
   ├─ 批量编码
   └─ 持久化向量

7. 依赖建议阶段 (并行)
   ├─ 结构化依赖识别
   ├─ 语义相似度计算
   ├─ AST验证链接
   └─ 字符标记分配

8. 跟踪器更新
   ├─ Mini跟踪器 (模块级)
   ├─ Doc跟踪器 (文档)
   └─ Main跟踪器 (项目级)

9. 模板生成
   └─ 最终审查清单

10. 自动可视化
    ├─ 项目概览图
    └─ 模块级详细图
```

#### 1.2 关键数据结构

**分析结果字典 (analysis_results)**:
```python
{
    "status": str,              # success/warning/error/skipped
    "message": str,             # 状态消息
    "warnings": List[str],      # 警告列表
    "key_generation": {
        "count": int,           # 生成的密钥总数
        "new_count": int,       # 新生成的密钥数量
    },
    "embedding_generation": {
        "status": str,          # 嵌入生成状态
    },
    "dependency_suggestion": {
        "status": str,          # 依赖建议状态
        "suggestion_count": int,  # 建议总数
        "ast_link_count": int,   # AST验证链接数量
    },
    "tracker_updates": {
        "mini": Dict,           # Mini跟踪器更新结果
        "doc": str,             # Doc跟踪器更新状态
        "main": str,            # Main跟踪器更新状态
    },
    "file_analysis": Dict,      # 文件分析结果映射
    "template_generation": Dict, # 模板生成结果
    "auto_visualization": Dict,  # 可视化结果
    "symbol_map_generation": {
        "status": str,          # 符号映射生成状态
        "path": str,            # 符号映射文件路径
        "count": int,           # 符号映射条目数量
        "validation_summary": Dict,  # 验证摘要
    },
    "ast_verified_links_generation": {
        "status": str,          # AST链接生成状态
        "path": str,            # AST链接文件路径
        "count": int,           # AST链接数量
    }
}
```

#### 1.3 关键函数详解

##### `_is_empty_dir(dir_path, tracker_filename_to_ignore)`

**功能**: 检查目录是否为空(用于跟踪器创建)

**逻辑**:
```python
def _is_empty_dir(dir_path, tracker_filename_to_ignore=None):
    """
    检查逻辑:
    1. 列出目录内容
    2. 如果完全为空 -> True
    3. 如果只包含跟踪器文件本身 -> True
    4. 如果包含其他文件 -> False
    5. 错误情况(不存在/权限) -> True (安全起见)
    """
```

#### 1.4 配置文件常量

```python
# 符号映射文件
PROJECT_SYMBOL_MAP_FILENAME = "project_symbol_map.json"
OLD_PROJECT_SYMBOL_MAP_FILENAME = "project_symbol_map_old.json"

# AST验证链接文件
AST_VERIFIED_LINKS_FILENAME = "ast_verified_links.json"
OLD_AST_VERIFIED_LINKS_FILENAME = "ast_verified_links_old.json"
```

### 🔄 工作流程详细说明

#### 阶段1: 密钥生成
```python
# 调用key_manager生成密钥
path_to_key_info, newly_generated_keys = key_manager.generate_keys(
    all_roots_rel,                    # 所有根目录
    excluded_dirs=excluded_dirs_rel,  # 排除目录
    excluded_extensions=excluded_extensions,  # 排除扩展名
    precomputed_excluded_paths=all_excluded_paths_abs_set  # 预计算的排除路径
)
```

**返回值**:
- `path_to_key_info`: Dict[str, KeyInfo] - 路径到密钥信息的映射
- `newly_generated_keys`: List[KeyInfo] - 新生成的密钥列表

#### 阶段2: 路径迁移映射
```python
# 构建路径迁移映射(处理密钥变更)
path_migration_info = tracker_io.build_path_migration_map(
    old_global_map,      # 旧的密钥映射
    path_to_key_info     # 新的密钥映射
)
```

#### 阶段3: 文件分析(并行)
```python
# 使用批处理器并行分析文件
analysis_results_list = process_items(
    files_to_analyze_abs,  # 文件列表
    analyze_file,          # 分析函数
    force=force_analysis   # 强制分析标志
)
```

#### 阶段4: 符号映射合并
```python
# 加载运行时符号
runtime_symbols = load_runtime_symbols(project_root)

# 合并运行时(优先)和AST(增强)
merged_symbol_map = merge_runtime_and_ast(
    runtime_symbols,      # 主要来源
    project_symbol_data   # 增强来源
)

# 验证合并输出
validation_results = validate_merged_output(merged_symbol_map)
```

#### 阶段5: 嵌入生成
```python
# 确定最佳批次大小
optimal_batch = get_optimal_batch_size()

# 生成嵌入
success = generate_embeddings(
    all_roots_rel,        # 根目录列表
    path_to_key_info,     # 密钥信息映射
    force=force_embeddings,  # 强制重新生成标志
    batch_size=optimal_batch  # 批次大小
)
```

#### 阶段6: 依赖建议(并行+共享计数器)
```python
import multiprocessing

# 创建共享计数器(线程安全)
shared_scan_counter = multiprocessing.Value("i", 0)

# 包装器函数
def _suggest_wrapper(single_file_path, ...):
    suggs, ast_links = suggest_dependencies(
        single_file_path,
        path_to_key_info_map,
        project_root_abs,
        file_analysis_blob,
        doc_similarity_threshold,
        shared_scan_counter=shared_scan_counter  # 共享计数器
    )
    return (single_file_path, suggs, ast_links)

# 并行处理
suggestion_results = suggestion_batcher.process_items(
    analyzed_file_paths,
    _suggest_wrapper,
    ...
)
```

#### 阶段7: 路径基础建议转换为密钥格式
```python
# 转换路径基础建议为KEY#global_instance格式
for src_path, path_deps_list in combined_path_suggestions.items():
    src_ki = current_global_map.get(src_path)
    src_key_global_instance_str = get_key_global_instance_string(
        src_ki,
        current_global_map,
        cache
    )
    # ...处理每个目标依赖
```

#### 阶段8: 跟踪器更新

**Mini跟踪器** (模块级):
```python
# 识别所有模块目录
for ki_obj in path_to_key_info.values():
    if ki_obj.is_directory and is_module_dir:
        # 更新mini跟踪器
        tracker_io.update_tracker(
            output_file_suggestion=mini_tracker_path,
            path_to_key_info=path_to_key_info,
            tracker_type="mini",
            suggestions_external=all_global_instance_suggestions,
            force_apply_suggestions=True  # 强制应用建议
        )
```

**Doc跟踪器**:
```python
if doc_tracker_path:
    tracker_io.update_tracker(
        output_file_suggestion=doc_tracker_path,
        tracker_type="doc",
        ...
    )
```

**Main跟踪器** (使用聚合):
```python
tracker_io.update_tracker(
    output_file_suggestion=main_tracker_path,
    tracker_type="main",  # 会触发内部聚合
    ...
)
```

#### 阶段9: 自动可视化
```python
if auto_generate_enabled:
    # 1. 预聚合依赖(一次性,所有图共享)
    project_aggregated_links = aggregate_all_dependencies(
        set(current_tracker_paths),
        path_migration_info,
        path_to_key_info
    )

    # 2. 生成项目概览图
    overview_mermaid_code = generate_mermaid_diagram(
        focus_keys_list_input=[],  # 空列表=概览
        global_path_to_key_info_map=path_to_key_info,
        pre_aggregated_links=project_aggregated_links
    )

    # 3. 为每个顶级模块生成详细图
    for module_key_str in module_keys_unique:
        module_mermaid_code = generate_mermaid_diagram(
            focus_keys_list_input=[module_key_str],
            pre_aggregated_links=project_aggregated_links
        )
```

### 📊 性能优化策略

#### 1. 批处理 (Batching)
```python
# 文件分析: 并行批处理
analysis_results_list = process_items(
    files_to_analyze_abs,
    analyze_file,
    force=force_analysis
)

# 嵌入生成: 按token数排序,动态批次
processing_queue.sort(key=lambda x: x["tokens"])
```

#### 2. 缓存策略
```python
# 文件级缓存 (基于mtime)
@cached("file_analysis",
    key_func=lambda file_path, force=False:
        f"analyze_file:{normalize_path(file_path)}:"
        f"{os.path.getmtime(file_path)}:{force}"
)

# 清除缓存
if force_analysis:
    clear_all_caches()
```

#### 3. 内存管理
```python
# AST缓存清理(在分析结束时)
ast_cache_instance = cache_manager.get_cache("ast_cache")
ast_cache_instance.data.clear()
logger.info("Cleared in-memory AST cache")
```

#### 4. 共享资源
```python
# 共享扫描计数器(避免全局变量竞态)
shared_scan_counter = multiprocessing.Value("i", 0)

# 共享预聚合结果(避免重复聚合)
project_aggregated_links = aggregate_all_dependencies(...)
# 所有图共享这个结果
```

### ⚠️ 错误处理

#### 1. 分级错误处理
```python
try:
    # 关键操作
except SpecificError as e:
    # 特定错误处理
    analysis_results["status"] = "error"
    return analysis_results
except Exception as e:
    # 通用错误处理
    logger.exception(f"Unexpected error: {e}")
    analysis_results["status"] = "error"
    return analysis_results
```

#### 2. 部分失败容忍
```python
# 允许部分文件失败
for file_path, analysis_result in ...:
    if "error" in analysis_result:
        error_count += 1  # 计数但继续
    else:
        analyzed_count += 1
```

#### 3. 状态降级
```python
# 警告不阻止流程
if not success:
    analysis_results["warnings"].append("Embedding generation partial failure")
    analysis_results["status"] = "warning"  # 降级,不是error
```

---

## 2. embedding_manager.py - 嵌入管理器

### 📖 模块说明

**文件**: `cline_utils/dependency_system/analysis/embedding_manager.py`
**行数**: ~1,704 行
**核心功能**: 管理文件嵌入向量的生成、存储和相似度计算

### 🎯 核心功能

#### 2.1 模型选择系统

**支持的模型**:

| 模型名 | 类型 | 维度 | 最小VRAM | 最小RAM | 上下文长度 |
|-------|------|------|----------|---------|-----------|
| **Qwen3-4B** | GGUF (Q6_K量化) | 2560 | 3.5GB | 6.0GB | 32768 |
| **all-mpnet-base-v2** | SentenceTransformer | 384 | 0.5GB | 2.0GB | 512 |

**自动选择逻辑**:
```python
def _select_best_model() -> Dict[str, Any]:
    """
    选择逻辑:
    1. 检查配置指定: model_selection = "qwen3-4b" / "mpnet" / "auto"
    2. 如果auto:
       a. 检测设备(CUDA/MPS/CPU)
       b. 测量可用内存
       c. 如果内存足够 -> Qwen3-4B
       d. 否则 -> all-mpnet-base-v2
    3. 下载模型(如果不存在)
    4. 验证模型完整性
    """
```

**设备选择**:
```python
def _get_best_device() -> str:
    """
    设备优先级:
    1. CUDA (最高优先级,如果可用)
       - 测试张量创建
       - 清空缓存
    2. MPS (Apple Silicon)
       - 检查平台和可用性
       - 测试张量创建
    3. CPU (后备)
    """
```

#### 2.2 Symbol Essence String (SES) 生成

**SES结构**:
```
[FILE: 相对路径 | TYPE: 文件类型 | MOD: 修改时间]

CLASS: ClassName
  BASES: BaseClass1, BaseClass2
  DECORATORS: @decorator1, @decorator2
  DOC: 类文档字符串
  METHOD: method_name(param1, param2)
    DOC: 方法文档字符串
    TYPES: param1=str, param2=int
    GLOBALS: global_var1, global_var2
    ACCESSES: attr1, attr2

FUNCTIONS:
  function_name(param1, param2)
    DOC: 函数文档字符串
    TYPES: param1=List[str], return=Dict
    GLOBALS: config, logger

CALLS: func1, module.func2, ClassName.method

CALLED_BY: file1.py, file2.py, package/file3.py
```

**生成函数**:
```python
def generate_symbol_essence_string(
    file_path: str,
    symbol_data: Dict[str, Any],
    max_chars: int = 4000,
    symbol_map: Optional[Dict[str, Any]] = None
) -> str:
    """
    生成策略:
    1. 文件头部 (路径,类型,修改时间)
    2. 类定义 (运行时增强)
       - 继承层次
       - 装饰器链
       - 类型注解
    3. 方法/函数 (运行时签名优先)
       - 完整签名
       - 作用域引用
       - 属性访问模式
    4. 调用图 (AST提取)
    5. 反向引用 (CALLED_BY)
    6. 截断至max_chars
    """
```

#### 2.3 Qwen3 Reranker 集成

**Reranker模型配置**:
```python
RERANKER_REPO_ID = "ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0-Safetensors"
RERANKER_FILES = [
    "model.safetensors",
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
]
```

**Reranking流程**:
```python
def rerank_candidates_with_qwen3(
    query_text: str,
    candidate_texts: List[str],
    top_k: int = 10,
    source_file_path: Optional[str] = None,
    instruction: Optional[str] = None
) -> List[Tuple[int, float]]:
    """
    Reranking流程:
    1. 加载Tokenizer和模型
    2. 构建Prompt (系统指令格式):
       <|im_start|>system
       Judge whether the Document meets the requirements...
       <|im_end|>
       <|im_start|>user
       <Instruct>: [指令]
       <Query>: [查询]
       <Document>: [文档]
       <|im_end|>
       <|im_start|>assistant
       <think>

       </think>

    3. Tokenize所有候选
    4. 按长度排序(短的先处理)
    5. 动态批处理:
       - 计算可用内存
       - 根据上下文长度调整批次大小
       - 按批次处理
    6. 提取yes/no token logits
    7. 计算概率分数
    8. 排序返回top_k
    """
```

**动态批次大小计算**:
```python
def _calculate_dynamic_batch_size(
    available_mem_gb: float,
    context_length: int,
    device: str
) -> int:
    """
    经验公式 (基于RTX 4060 8GB实测):
    - 模型占用: ~1.1GB
    - Context=1000: ~0.3GB/样本 -> Batch=15
    - Context=4000: ~0.5GB/样本 -> Batch=8
    - Context=8000: ~0.8GB/样本 -> Batch=5
    - Context=16000: ~1.5GB/样本 -> Batch=3
    - Context=32000: ~2.5GB/样本 -> Batch=2

    公式:
    MB_per_sample = 175 + (context_length/1000) * 80
    usable_mem = available_mem * 0.8  # 保留20%缓冲
    batch_size = min(50, max(1, usable_mem / GB_per_sample))
    """
```

#### 2.4 嵌入生成主流程

```python
def generate_embeddings(
    project_paths: List[str],
    path_to_key_info: Dict[str, KeyInfo],
    force: bool = False,
    batch_size: Optional[int] = None,
    symbol_map: Optional[Dict[str, Any]] = None
) -> bool:
    """
    嵌入生成流程:

    1. 准备阶段:
       ├─ 加载符号映射
       ├─ 识别需要处理的文件
       └─ 检查现有嵌入(mtime比较)

    2. 预处理阶段:
       ├─ 生成SES或预处理文档
       ├─ 计算token数
       ├─ 按token数排序(递增)
       └─ 构建处理队列

    3. 模型加载:
       ├─ 选择最佳模型
       ├─ 确定设备
       └─ 根据需要动态调整上下文窗口

    4. 批处理编码:
       ├─ 按批次大小分组
       ├─ 编码批次
       ├─ 归一化向量
       └─ 保存到.npy文件

    5. 元数据更新:
       ├─ 更新metadata.json
       ├─ 记录模型版本
       └─ 记录文件mtime

    6. 缓存失效:
       └─ 清除相似度计算缓存
    """
```

**文件处理优先级**:
```python
# 策略: 符号映射 -> 文档结构 -> 原始后备
if file_path in symbol_map:
    text_to_embed = generate_symbol_essence_string(
        file_path,
        symbol_map[file_path],
        symbol_map=symbol_map
    )
else:
    # 文档文件
    if ext in [".md", ".txt", ".rst"]:
        text_to_embed = preprocess_doc_structure(content)
    else:
        # 原始后备
        text_to_embed = f"[FILE: {rel_path}]\n{content[:32000]}"
```

#### 2.5 相似度计算

```python
@cached("similarity_calculation",
        key_func=_get_similarity_cache_key,
        ttl=SIM_CACHE_TTL_SEC)
def calculate_similarity(
    key1_str: str,
    key2_str: str,
    embeddings_dir: str,
    path_to_key_info: Dict[str, KeyInfo],
    project_root: str,
    code_roots: List[str],
    doc_roots: List[str]
) -> float:
    """
    相似度计算流程:
    1. 验证密钥存在
    2. 定位.npy文件
    3. 加载向量
    4. 计算点积(向量已归一化)
    5. Clamp到[0, 1]
    6. 缓存结果(7天TTL)
    """
```

**缓存策略**:
```python
SIM_CACHE_MAXSIZE = 100_000      # 最大缓存条目数
SIM_CACHE_TTL_SEC = 7 * 24 * 60 * 60  # 7天TTL
SIM_CACHE_NEGATIVE_RESULTS = True     # 缓存负结果

# 缓存键生成(确定性)
def _get_similarity_cache_key(key1, key2):
    k1, k2 = sorted((key1, key2))  # 排序确保(A,B) == (B,A)
    return f"sim_ses:{k1}:{k2}"
```

### 🔧 高级特性

#### 1. Flash Attention 2 优化 (Qwen3 Reranker)

```python
# CUDA设备上自动启用Flash Attention 2
if device == "cuda":
    RERANKER_MODEL = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        dtype=torch.float16,  # FP16提升性能
        attn_implementation="flash_attention_2",  # Flash Attention 2
        trust_remote_code=True
    )

# 验证Flash Attention启用
if hasattr(RERANKER_MODEL.config, "_attn_implementation"):
    attn_impl = RERANKER_MODEL.config._attn_implementation
    if attn_impl == "flash_attention_2":
        logger.info("Flash Attention 2 is active!")
```

**性能提升**:
- 内存使用减少 ~40%
- 推理速度提升 ~2-3x
- 支持更长的上下文

#### 2. 模型自动下载与验证

```python
def _download_qwen3_model(model_path: str) -> bool:
    """
    下载流程:
    1. 检查现有模型
    2. 验证完整性(GGUF header + load test)
    3. 如果无效,删除并重新下载
    4. 使用PhaseTracker显示进度
    5. 最终验证
    """
    # 验证GGUF文件
    with open(model_path, "rb") as f:
        header = f.read(4)
        if header != b"GGUF":
            return False

    # Load test
    test_model = Llama(
        model_path=model_path,
        embedding=True,
        n_ctx=16384,
        verbose=False
    )
```

#### 3. 上下文窗口动态调整

```python
def _load_model(n_ctx: int = 8192):
    """
    动态调整策略:
    1. 如果模型已加载:
       - 检查当前上下文窗口
       - 如果不足,卸载并重新加载
       - 如果足够,复用
    2. 如果是SentenceTransformer:
       - 直接更新max_seq_length
       - 无需重新加载
    """
    if MODEL_INSTANCE is not None:
        if SELECTED_MODEL_CONFIG["type"] == "gguf":
            current_n_ctx = MODEL_INSTANCE.n_ctx()
            if current_n_ctx < n_ctx:
                _unload_model()
                # 重新加载
```

### 📊 性能指标

#### Qwen3-4B模型 (Q6_K量化)

**内存占用** (RTX 4060 8GB):
```
模型本体: ~1.1GB
上下文=1000: +0.3GB
上下文=4000: +0.5GB
上下文=8000: +0.8GB
上下文=16000: +1.5GB
上下文=32000: +2.5GB
```

**推理速度** (批次大小自适应):
```
上下文=1000: ~15样本/批次, ~50样本/秒
上下文=4000: ~8样本/批次, ~25样本/秒
上下文=8000: ~5样本/批次, ~15样本/秒
上下文=16000: ~3样本/批次, ~8样本/秒
上下文=32000: ~2样本/批次, ~5样本/秒
```

#### all-mpnet-base-v2模型

**内存占用**:
```
模型本体: ~400MB
批次大小=32: +100MB
批次大小=64: +200MB
```

**推理速度**:
```
CPU: ~100样本/秒
CUDA: ~500样本/秒
```

### ⚠️ 注意事项

1. **GGUF模型日志抑制**:
```python
# 使用no-op callback抑制C++库输出
import ctypes
LogCallback = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)

def noop_log_callback(level, text, user_data):
    pass

_C_LOG_CALLBACK_REF = LogCallback(noop_log_callback)
llama_cpp.llama_log_set(_C_LOG_CALLBACK_REF, ctypes.c_void_p())
```

2. **内存清理**:
```python
# 及时删除张量和清空缓存
del padded_batch
del logits
if device == "cuda":
    torch.cuda.empty_cache()
```

3. **Reranker卸载**:
```python
# 分析完成后卸载reranker释放VRAM
try:
    embedding_manager.unload_reranker_model()
except Exception as e:
    logger.warning(f"Error during reranker unload: {e}")
```

---

## 3. dependency_analyzer.py - 依赖分析器

### 📖 模块说明

**文件**: `cline_utils/dependency_system/analysis/dependency_analyzer.py`
**行数**: ~2,160 行
**核心功能**: 解析源代码文件,提取依赖关系和符号信息

### 🎯 核心功能

#### 3.1 多语言分析支持

| 语言 | 分析方法 | 提取信息 |
|------|---------|---------|
| **Python** | AST + Tree-sitter | imports, functions, classes, calls, attributes, inheritance, type_refs, decorators, exceptions, with_contexts |
| **JavaScript** | Tree-sitter | imports, exports, functions, classes, calls |
| **TypeScript** | Tree-sitter | imports, exports, functions, classes, calls, type_refs |
| **TSX** | Tree-sitter | imports, exports, functions, classes, calls, type_refs, JSX elements |
| **HTML** | Tree-sitter | links (<a>), scripts (<script>), stylesheets (<link>), images (<img>) |
| **CSS** | Tree-sitter | @import statements |
| **Markdown** | Regex | links [text](url), code blocks ```lang``` |

#### 3.2 主函数: `analyze_file()`

**函数签名**:
```python
@cached("file_analysis",
    key_func=lambda file_path, force=False:
        f"analyze_file:{normalize_path(file_path)}:"
        f"{os.path.getmtime(file_path)}:{force}"
)
def analyze_file(file_path: str, force: bool = False) -> Dict[str, Any]:
```

**完整流程**:
```
1. 预检查
   ├─ 验证文件存在
   ├─ 检查排除列表
   └─ 二进制文件检测

2. 读取文件内容
   └─ UTF-8编码,错误处理

3. 根据文件类型分发
   ├─ .py -> _analyze_python_file() + _analyze_python_file_ts()
   ├─ .js -> _analyze_javascript_file_ts()
   ├─ .ts -> _analyze_typescript_file_ts()
   ├─ .tsx -> _analyze_tsx_file_ts()
   ├─ .md -> _analyze_markdown_file()
   ├─ .html -> _analyze_html_file_ts()
   └─ .css -> _analyze_css_file_ts()

4. 合并分析结果
   └─ _merge_analysis_results() (AST优先)

5. 整合与去重
   └─ _consolidate_list_of_dicts()

6. 生成摘要
   └─ symbol_summary, ast_verified_links

7. 缓存树对象
   ├─ AST -> "ast_cache"
   └─ Tree-sitter -> "ts_ast_cache"
```

#### 3.3 Python文件分析

##### AST分析 (`_analyze_python_file`)

**两遍扫描策略**:

```python
# 第一遍: 遍历tree.body (顶级定义)
for node in tree.body:
    if isinstance(node, ast.Import):
        # 处理import语句
    elif isinstance(node, ast.ImportFrom):
        # 处理from...import语句
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        # 收集顶级函数
    elif isinstance(node, ast.ClassDef):
        # 收集顶级类
    elif isinstance(node, (ast.Assign, ast.AnnAssign)):
        # 收集全局变量定义

# 第二遍: ast.walk (所有节点,包括嵌套)
for node in ast.walk(tree):
    # 处理装饰器、类型引用、调用、属性访问等
```

**提取的信息**:

1. **Import语句**:
```python
# import module
{"name": "module"}

# from package import item as alias
{"name": "item", "from": "package", "alias": "alias"}
```

2. **函数定义**:
```python
{
    "name": "function_name",
    "line": 42,
    "params": ["arg1", "arg2", "*args", "**kwargs"],
    "docstring": "First line of docstring",
    "async": True  # 如果是async def
}
```

3. **类定义**:
```python
{
    "name": "ClassName",
    "line": 10,
    "docstring": "Class documentation",
    "methods": [
        {
            "name": "method_name",
            "line": 15,
            "params": ["self", "param1"],
            "docstring": "Method documentation"
        }
    ]
}
```

4. **继承关系**:
```python
{
    "class_name": "DerivedClass",
    "base_class_name": "BaseClass",
    "potential_source": "BaseClass",  # 完整名称(可能包含模块)
    "line": 20
}
```

5. **类型引用**:
```python
{
    "type_name_str": "List",
    "context": "arg_annotation",  # 或 return_annotation, variable_annotation等
    "target_name": "my_list",
    "line": 25
}
```

6. **函数调用**:
```python
{
    "target_name": "function_name",  # 或 "obj.method_name"
    "potential_source": "obj",  # 调用来源对象
    "line": 30
}
```

7. **装饰器使用**:
```python
{
    "name": "decorator_name",
    "target_type": "function",  # 或 class, method
    "target_name": "decorated_function",
    "line": 12
}
```

8. **异常处理**:
```python
{
    "type_name_str": "ValueError",
    "line": 50
}
```

9. **with上下文**:
```python
{
    "context_expr_str": "open('file.txt')",
    "line": 60
}
```

##### Tree-sitter增强 (`_analyze_python_file_ts`)

**查询模式**:
```python
# Imports
imports_query_str = """
[
    (import_statement
        name: (dotted_name) @import_name)
    (import_from_statement
        module_name: (dotted_name) @module_name)
]
"""

# Functions
functions_query_str = """
(function_definition
    name: (identifier) @func_name) @function
"""

# Classes
classes_query_str = """
(class_definition
    name: (identifier) @class_name) @class
"""

# Calls
calls_query_str = """
[
  (call
      function: (identifier) @call_func
  )
  (call
      function: (attribute
          object: (_) @call_obj
          attribute: (identifier) @call_attr
      )
  )
]
"""
```

**合并策略**:
```python
def _merge_analysis_results(primary, secondary):
    """
    合并规则:
    1. AST结果优先(primary)
    2. Tree-sitter补充(secondary)
    3. 基于name+line去重
    4. 对于imports/calls,基于path/target_name去重
    """
```

#### 3.4 JavaScript/TypeScript文件分析

##### JavaScript分析 (`_analyze_javascript_file_ts`)

**查询模式**:
```python
# Imports (ESM和require)
imports_query = """
[
  (import_statement source: (string) @path)
  (call_expression
    function: (identifier) @req.fn
    arguments: (arguments (string) @path)
  ) @require
    (#match? @req.fn "^(require|import)$")
]
"""

# Exports
exports_query = """
[
  (export_statement
      (export_clause (export_specifier name: (identifier) @export.name))
  )
  (export_statement
      (export_clause (export_specifier
          name: (identifier) @export.orig
          alias: (identifier) @export.alias))
  )
  (export_statement
      declaration: (variable_declaration
      (variable_declarator
          name: (identifier) @export.default))
  ) @default.export
  (export_statement
      declaration: (function_declaration name: (identifier) @export.func.name)
  )
  (export_statement
      declaration: (class_declaration name: (identifier) @export.class.name)
  )
]
"""
```

**导出信息提取**:
```python
# export const x = 1
{"name": "x", "line": 10}

# export { x as y }
{"name": "x", "alias": "y", "line": 15}

# export default MyComponent
{"name": "default", "alias": "MyComponent", "line": 20}

# export { x } from './module'
{"from": "./module", "line": 25}
```

##### TypeScript/TSX分析

**额外类型引用提取**:
```python
# Type annotations
type_ann_query = "(type_annotation (type_identifier) @type.name)"

# Generic types
generic_type_query = "(generic_type (type_identifier) @type.name)"

# 示例:
# let x: MyType<T> = ...
# ->
# {"type_name_str": "MyType", "context": "type_annotation", "line": 30}
# {"type_name_str": "T", "context": "generic_type", "line": 30}
```

#### 3.5 HTML文件分析 (`_analyze_html_file_ts`)

**提取的链接类型**:

```python
# <script src="path/to/script.js">
scripts: [{"url": "path/to/script.js", "line": 10}]

# <link href="styles.css" rel="stylesheet">
stylesheets: [{"url": "styles.css", "line": 15}]

# <img src="image.png">
images: [{"url": "image.png", "line": 20}]

# <a href="page.html">
links: [{"url": "page.html", "line": 25}]
```

**Tree-sitter查询**:
```python
queries = {
    "scripts": '(script_element (start_tag (attribute (attribute_name) @name (#eq? @name "src") (quoted_attribute_value (attribute_value) @path))))',
    "stylesheets": '(element (start_tag (tag_name) @tag (#eq? @tag "link") (attribute (attribute_name) @name (#eq? @name "href") (quoted_attribute_value (attribute_value) @path))))',
    "images": '(element (start_tag (tag_name) @tag (#eq? @tag "img") (attribute (attribute_name) @name (#eq? @name "src") (quoted_attribute_value (attribute_value) @path))))',
    "links": '(element (start_tag (tag_name) @tag (#eq? @tag "a") (attribute (attribute_name) @name (#eq? @name "href") (quoted_attribute_value (attribute_value) @path))))',
}
```

#### 3.6 CSS文件分析 (`_analyze_css_file_ts`)

**@import提取**:
```python
# @import "styles.css";
# @import url("styles.css");
imports: [{"url": "styles.css", "line": 5}]

# Tree-sitter查询
query_str = """
(import_statement (string_value) @path)
"""
```

#### 3.7 Markdown文件分析 (`_analyze_markdown_file`)

**正则表达式提取**:

```python
# [链接文本](url)
MARKDOWN_LINK_PATTERN = re.compile(r"\[(?:[^\]]+)\]\(([^)]+)\)")
links: [{"url": "path/to/file.md", "line": 10}]

# ```language
# code
# ```
code_block_pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
code_blocks: [
    {
        "language": "python",
        "line": 15,
        "content": "def example():\n    pass"
    }
]
```

### 🔧 高级特性

#### 1. 调用过滤 (`_is_useful_call`)

**过滤策略**:
```python
def _is_useful_call(target_name, potential_source, imports_map):
    """
    过滤逻辑:
    1. 手动黑名单检查 (logger, console等)
    2. 路径解析过滤:
       - 如果是导入的模块,检查是否为内部模块
       - 如果是外部库,过滤掉
    3. 通用方法名过滤 (get, set, append等)
    4. 内置类型方法过滤 (str.split等)
    """
```

**黑名单**:
```python
# 忽略的调用源
IGNORED_CALL_SOURCES = {
    "logger", "logging", "os", "sys", "json", "re",
    "math", "datetime", "time", "random", "subprocess",
    "shutil", "pathlib", "typing", "argparse", ...
}

# 通用调用名
GENERIC_CALL_NAMES = {
    "get", "set", "update", "append", "extend", "pop",
    "remove", "clear", "copy", "keys", "values", "items",
    "split", "join", "strip", "replace", "format", ...
}
```

#### 2. 内部模块识别 (`_is_internal_module`)

```python
@cached("is_internal_module",
        key_func=lambda module_name: f"is_internal:{module_name}")
def _is_internal_module(module_name: str) -> bool:
    """
    检查逻辑:
    1. 检查是否为内置模块 -> False
    2. 获取顶级包名 (psycopg.sql -> psycopg)
    3. 遍历代码根目录:
       - 检查是否存在同名目录(包)
       - 检查是否存在同名.py文件(模块)
    4. 存在 -> True, 否则 -> False
    """
```

#### 3. 合并与去重 (`_consolidate_list_of_dicts`)

```python
def _consolidate_list_of_dicts(items, group_by_keys):
    """
    合并策略:
    1. 按指定键分组 (name, target_name等)
    2. 合并line字段为列表
    3. 保留第一次出现的其他字段
    4. 对line列表去重并排序

    示例:
    [
        {"name": "func", "line": 10, "params": ["x"]},
        {"name": "func", "line": 15, "params": ["x"]}
    ]
    ->
    [{"name": "func", "line": [10, 15], "params": ["x"]}]
    """
```

**各字段的合并键**:
```python
consolidation_map = {
    "calls": ["target_name", "potential_source"],
    "functions": ["name"],
    "classes": ["name"],
    "globals_defined": ["name"],
    "attribute_accesses": ["target_name", "potential_source"],
    "inheritance": ["class_name", "base_class_name"],
    "type_references": ["type_name_str", "context", "target_name"],
    "decorators_used": ["name", "target_type", "target_name"],
    "exceptions_handled": ["type_name_str"],
    "with_contexts_used": ["context_expr_str"],
    "code_blocks": ["language", "content"],
    "links": ["url"],
    "scripts": ["url"],
    "stylesheets": ["url"],
    "images": ["url"],
}
```

#### 4. 二进制文件检测

```python
# 启发式检测: 检查前1024字节是否包含null字节
with open(file_path, "rb") as f:
    if b"\0" in f.read(1024):
        return {"skipped": True, "reason": "Binary file detected"}
```

#### 5. Tree-sitter线程安全

**重要修复**:
```python
# 错误做法(全局Parser,非线程安全):
# JS_PARSER = Parser(JS_LANGUAGE)  # 模块级全局

# 正确做法(局部Parser,线程安全):
def _analyze_javascript_file_ts(...):
    parser = Parser(JS_LANGUAGE)  # 每次调用创建新实例
    tree = parser.parse(content_bytes)
```

### 📊 返回数据结构

**完整分析结果**:
```python
{
    "file_path": str,              # 规范化绝对路径
    "file_type": str,              # py/js/ts/tsx/html/css/md
    "size": int,                   # 文件大小(字节)

    # 通用字段
    "imports": List[Dict],         # 导入语句
    "exports": List[Dict],         # 导出语句(JS/TS)
    "links": List[Dict],           # 链接(HTML/MD)
    "functions": List[Dict],       # 函数定义
    "classes": List[Dict],         # 类定义
    "calls": List[Dict],           # 函数调用

    # Python特有
    "attribute_accesses": List[Dict],  # 属性访问
    "inheritance": List[Dict],         # 继承关系
    "type_references": List[Dict],     # 类型引用
    "globals_defined": List[Dict],     # 全局变量定义
    "decorators_used": List[Dict],     # 装饰器使用
    "exceptions_handled": List[Dict],  # 异常处理
    "with_contexts_used": List[Dict],  # with上下文

    # HTML特有
    "scripts": List[Dict],         # <script>标签
    "stylesheets": List[Dict],     # <link>样式表
    "images": List[Dict],          # <img>图片

    # Markdown特有
    "code_blocks": List[Dict],     # 代码块

    # 内部使用(不导出)
    "_ast_tree": Optional[ast.AST],      # Python AST树(缓存到ast_cache)
    "_ts_tree": Optional[Tree],          # Tree-sitter树(缓存到ts_ast_cache)

    # 摘要
    "symbol_summary": Dict,        # 跨语言标准化摘要
    "ast_verified_links": List[Dict],  # AST验证的链接

    # 错误/跳过
    "error": Optional[str],        # 错误信息
    "skipped": Optional[bool],     # 是否跳过
    "reason": Optional[str],       # 跳过原因
}
```

### ⚠️ 注意事项

1. **AST树缓存管理**:
```python
# 分析完成后,AST树被缓存到单独的"ast_cache"
# 不再包含在analysis_result中,避免序列化问题
ast_cache = cache_manager.get_cache("ast_cache")
ast_cache.set(norm_file_path, ast_object)
```

2. **编码错误处理**:
```python
# UTF-8解码失败时优雅降级
try:
    content = f.read()
except UnicodeDecodeError as e:
    return {
        "error": "Encoding error",
        "details": str(e),
        "file_path": norm_file_path
    }
```

3. **符号冲突解决**:
```python
# Python: 同名函数/类在不同行
# 使用 name+line 作为唯一标识
unique_key = f"{item['name']}:{line}"
```

---

## 4. dependency_suggester.py - 依赖建议器

### 📖 模块说明

**文件**: `cline_utils/dependency_system/analysis/dependency_suggester.py`
**行数**: ~2,000+ 行
**核心功能**: 基于文件分析结果和嵌入向量,建议潜在的依赖关系

### 🎯 核心功能

#### 4.1 依赖字符系统

**字符定义**:
```
< : Row depends on column (行依赖列)
> : Column depends on row (列依赖行)
x : Mutual dependency (相互依赖)
d : Documentation dependency (文档依赖)
o : Self dependency (自我依赖,仅对角线)
n : Verified no dependency (验证无依赖)
p : Placeholder (占位符,未验证)
s : Semantic dependency (weak, .06-.07) (弱语义依赖)
S : Semantic dependency (strong, .07+) (强语义依赖)
```

**字符优先级** (从高到低):
```
1. < (结构化依赖 - 最高优先级)
2. > (反向结构化依赖)
3. x (相互依赖)
4. d (文档依赖)
5. S (强语义依赖)
6. s (弱语义依赖)
7. p (占位符 - 最低优先级)
```

#### 4.2 主函数: `suggest_dependencies()`

**函数签名**:
```python
def suggest_dependencies(
    file_path: str,
    path_to_key_info: Dict[str, KeyInfo],
    project_root: str,
    file_analysis_results: Dict[str, Any],
    threshold: float = 0.7,
    shared_scan_counter: Any = None
) -> Tuple[List[Tuple[str, str]], List[Dict[str, str]]]:
```

**返回值**:
```python
(
    [
        (target_path, char),  # 路径基础的依赖建议
        ...
    ],
    [
        {  # AST验证的链接
            "source_path": str,
            "target_path": str,
            "char": str,
            "reason": str
        },
        ...
    ]
)
```

**文件类型分发**:
```python
if file_ext == ".py":
    char_suggestions, py_ast_links = suggest_python_dependencies(...)
elif file_ext in (".js", ".ts", ".tsx", ".mjs", ".cjs"):
    char_suggestions, js_ast_links = suggest_javascript_dependencies(...)
elif file_ext in (".md", ".rst"):
    char_suggestions = suggest_documentation_dependencies(...)
elif file_ext in (".html", ".htm"):
    char_suggestions = suggest_html_dependencies(...)
elif file_ext == ".css":
    char_suggestions = suggest_css_dependencies(...)
else:
    char_suggestions = suggest_generic_dependencies(...)
```

#### 4.3 Python依赖建议

##### 结构化依赖识别 (`_identify_structural_dependencies`)

**处理流程**:
```
1. 构建导入映射
   ├─ 解析import语句
   ├─ 使用AST树(从ast_cache获取)
   └─ 映射: local_name -> absolute_module_path

2. 处理各类依赖源
   ├─ 函数调用 (calls)
   ├─ 属性访问 (attribute_accesses)
   ├─ 继承关系 (inheritance)
   ├─ 类型引用 (type_references)
   ├─ 装饰器使用 (decorators_used)
   ├─ 异常处理 (exceptions_handled)
   └─ with上下文 (with_contexts_used)

3. 符号解析
   ├─ 查找符号定义位置
   ├─ 优先使用项目符号映射
   └─ 回退到路径解析

4. 生成建议
   ├─ 分配字符(</>)
   └─ 创建AST验证链接
```

**导入映射构建** (`_build_import_map`):
```python
def _build_import_map(current_source_path, tree):
    """
    示例:
    import my_module.sub
    -> {"my_module.sub": "/abs/path/to/my_module/sub.py"}

    import my_module.sub as s
    -> {"s": "/abs/path/to/my_module/sub.py"}

    from my_package import specific_item
    -> {"specific_item": "/abs/path/to/my_package/__init__.py"}

    from my_package.another_module import specific_item as si
    -> {"si": "/abs/path/to/my_package/another_module.py"}
    """
```

**Python导入路径转换** (`_convert_python_import_to_paths`):
```python
def _convert_python_import_to_paths(
    import_name: str,
    source_file_dir: str,
    project_root: str,
    path_to_key_info: Dict[str, KeyInfo],
    project_symbol_map: Dict[str, Dict[str, Any]],
    specific_item_name: Optional[str] = None,
    relative_level: int = 0
) -> List[Tuple[str, bool]]:
    """
    转换流程:
    1. 处理相对导入 (from . import x)
       - 根据relative_level计算基础目录
    2. 处理绝对导入
       - 从各个代码根目录搜索
    3. 包/模块解析
       - 检查__init__.py
       - 检查.py文件
    4. 符号验证 (如果指定specific_item_name)
       - 在符号映射中查找
       - 检查是否为子模块

    返回: [(resolved_path, item_verified), ...]
    """
```

**调用解析示例**:
```python
# 源文件: /project/module_a/file1.py
# 代码: result = utils.process_data(x)

# 步骤1: 在导入映射中查找"utils"
# import_map = {"utils": "/project/module_b/utils.py"}

# 步骤2: 在utils.py的符号映射中查找"process_data"
# symbol_map["/project/module_b/utils.py"]["functions"]
# = [{"name": "process_data", "line": 42, ...}]

# 步骤3: 生成依赖建议
# ("/project/module_b/utils.py", "<")  # file1依赖utils

# 步骤4: 生成AST验证链接
# {
#     "source_path": "/project/module_a/file1.py",
#     "target_path": "/project/module_b/utils.py",
#     "char": "<",
#     "reason": "call:process_data"
# }
```

##### 语义依赖建议 (`_suggest_semantic_dependencies_python`)

**流程**:
```python
def _suggest_semantic_dependencies_python(...):
    """
    1. 加载嵌入元数据
    2. 过滤候选文件
       - 同类型优先(.py -> .py)
       - 排除自身
       - 排除已有结构化依赖
    3. 计算相似度
       - 使用calculate_similarity()
       - 批量计算
    4. 过滤低于阈值的结果
    5. Reranking (可选,如果启用)
       - 使用Qwen3 Reranker
       - 全局扫描限制(性能优化)
    6. 分配字符
       - >= 0.07: 'S' (强语义)
       - >= 0.06: 's' (弱语义)
    """
```

**Reranker使用**:
```python
# 全局扫描限制
MAX_RERANKER_SCANS = 100  # 整个项目最多重排序100次

# 每个文件的重排序逻辑
if shared_scan_counter is not None:
    with shared_scan_counter.get_lock():
        current_count = shared_scan_counter.value
        if current_count < MAX_RERANKER_SCANS:
            shared_scan_counter.value += 1
            # 执行reranking
            reranked_results = rerank_candidates_with_qwen3(
                query_text=source_ses,
                candidate_texts=candidate_ses_list,
                top_k=10,
                source_file_path=source_path
            )
```

#### 4.4 JavaScript/TypeScript依赖建议

##### 导入解析 (`suggest_javascript_dependencies`)

**特殊处理**:
```python
# 1. tsconfig.json / jsconfig.json 解析
config_data = _find_and_parse_tsconfig(source_file_dir, project_root)

# 2. 路径别名解析
if config_data and "compilerOptions" in config_data:
    paths = config_data["compilerOptions"].get("paths", {})
    # 示例: "@/*" -> "./src/*"

# 3. 导入路径解析
for imp in imports:
    import_path_str = imp.get("path")

    # 相对路径
    if import_path_str.startswith('.'):
        resolved = _resolve_js_relative_import(...)

    # 别名路径
    elif import_path_str.startswith('@'):
        resolved = _resolve_ts_path_alias(...)

    # 包导入
    else:
        # 检查node_modules(通常跳过外部依赖)
        pass
```

**符号验证**:
```python
# 检查导入的符号是否在目标文件的exports中
target_exports = symbol_map.get(target_path, {}).get("exports", [])
is_verified = any(
    exp.get("name") == symbol_name
    for exp in target_exports
)
```

#### 4.5 文档依赖建议 (`suggest_documentation_dependencies`)

**流程**:
```python
def suggest_documentation_dependencies(...):
    """
    1. 加载嵌入元数据
    2. 识别文档文件
       - .md, .rst优先
    3. 识别代码文件
       - .py, .js, .ts等
    4. 计算文档->代码相似度
       - 使用文档特定的预处理
       - 计算向量相似度
    5. Reranking
       - 使用文档特定的instruction
    6. 分配'd'字符
    """
```

**文档预处理**:
```python
def preprocess_doc_structure(content: str) -> str:
    """
    返回完整内容(截断至32k字符)以保留上下文
    不进行过度清理,保留结构信息
    """
    return content[:32000]
```

#### 4.6 建议合并与去重

##### 字符优先级合并 (`combine_suggestions_path_based_with_char_priority`)

```python
def combine_suggestions_path_based_with_char_priority(
    path_suggestions: List[Tuple[str, str]],
    source_path: str
) -> List[Tuple[str, str]]:
    """
    合并规则:
    1. 按target_path分组
    2. 收集所有字符
    3. 应用优先级:
       '<' > '>' > 'x' > 'd' > 'S' > 's' > 'p'
    4. 选择最高优先级字符
    5. 自依赖特殊处理 -> 'o'

    示例:
    [
        ("/path/to/file.py", "<"),  # 结构化依赖
        ("/path/to/file.py", "s"),  # 弱语义依赖
        ("/path/to/file.py", "S"),  # 强语义依赖
    ]
    ->
    [("/path/to/file.py", "<")]  # 结构化优先
    """
```

**字符优先级映射**:
```python
CHAR_PRIORITY_MAP = {
    '<': 7,  # 最高优先级
    '>': 6,
    'x': 5,
    'd': 4,
    'S': 3,
    's': 2,
    'p': 1,  # 最低优先级
    'o': 8,  # 自依赖特殊优先级
    'n': 0,  # 验证无依赖
}
```

#### 4.7 TypeScript配置解析

##### tsconfig.json / jsconfig.json 支持

**查找策略**:
```python
@cached("tsconfig_data", ...)
def _find_and_parse_tsconfig(start_dir, project_root):
    """
    向上遍历目录树查找配置文件:
    1. 从start_dir开始
    2. 查找tsconfig.json或jsconfig.json
    3. 如果找到,解析(支持JSONC)
    4. 向上到project_root
    5. 缓存结果
    """
```

**路径别名解析**:
```python
# tsconfig.json:
{
  "compilerOptions": {
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@components/*": ["components/*"],
      "@utils/*": ["utils/*"]
    }
  }
}

# 导入: import { Button } from '@components/Button'
# 解析: ./src/components/Button.ts
```

**解析逻辑**:
```python
def _resolve_ts_path_alias(...):
    for alias_pattern, targets in paths.items():
        if import_spec.startswith(alias_pattern.rstrip('/*')):
            for target_pattern in targets:
                # 替换别名为实际路径
                # 尝试各种扩展名(.ts, .tsx, .js等)
                # 检查文件存在性
```

### 🔧 高级特性

#### 1. 项目符号映射加载

```python
@cached("project_symbol_map_data",
        key_func=lambda: f"project_symbol_map:{mtime}")
def load_project_symbol_map() -> Dict[str, Dict[str, Any]]:
    """
    加载project_symbol_map.json:
    1. 确定路径(相对于key_manager.py)
    2. 加载JSON
    3. 缓存(基于mtime)
    4. 返回映射

    结构:
    {
        "/abs/path/to/file.py": {
            "file_type": "py",
            "functions": [...],
            "classes": [...],
            "globals_defined": [...],
            "imports": [...],
            "calls": [...],
            ...
        },
        ...
    }
    """
```

#### 2. 符号查找优化

**函数符号查找**:
```python
def _find_symbol_in_project(
    symbol_name: str,
    symbol_type: str,  # "function", "class", "global"
    project_symbol_map: Dict[str, Dict[str, Any]],
    hint_paths: Optional[List[str]] = None
) -> List[str]:
    """
    查找策略:
    1. 如果有hint_paths,优先搜索这些文件
    2. 否则遍历整个符号映射
    3. 匹配symbol_name和symbol_type
    4. 返回所有匹配的文件路径

    优化:
    - 使用hint_paths缩小搜索范围
    - 早停(找到第一个匹配)
    """
```

#### 3. 相对导入处理

**Python相对导入**:
```python
# from .. import module (level=2)
# from . import module (level=1)
# from .subpackage import module (level=1, module_name="subpackage")

# 计算基础目录
base_dir = current_source_dir
for _ in range(level):
    base_dir = os.path.dirname(base_dir)
    if not base_dir.startswith(project_root):
        # 超出项目范围,回退到项目根目录
        base_dir = project_root
        break
```

**JavaScript/TypeScript相对导入**:
```python
# import { x } from './utils'
# import { y } from '../helpers/utils'

def _resolve_js_relative_import(...):
    # 1. 组合路径
    raw_path = os.path.join(source_file_dir, import_path)

    # 2. 规范化
    resolved = normalize_path(raw_path)

    # 3. 尝试各种扩展名
    for ext in ['.ts', '.tsx', '.js', '.jsx', '']:
        candidate = resolved + ext
        if os.path.exists(candidate):
            return candidate

    # 4. 尝试index文件
    for ext in ['.ts', '.tsx', '.js', '.jsx']:
        index_file = os.path.join(resolved, f'index{ext}')
        if os.path.exists(index_file):
            return index_file
```

#### 4. 缓存管理

**多级缓存**:
```python
# 模块级缓存
_structural_import_map_cache: Dict[str, Dict[str, str]] = {}
_structural_resolved_path_cache: Dict[Tuple[str, Optional[str]], Optional[str]] = {}

# 装饰器缓存
@cached("tsconfig_data", ...)
@cached("project_symbol_map_data", ...)
@cached("is_internal_module", ...)

# 清除所有缓存
def clear_caches():
    clear_all_caches()  # 装饰器缓存
    _find_and_parse_tsconfig._cache.clear()
    _structural_import_map_cache.clear()
    _structural_resolved_path_cache.clear()
    load_project_symbol_map._cache.clear()
```

### 📊 性能优化

#### 1. 共享扫描计数器

```python
# 防止过度使用Reranker
import multiprocessing
shared_scan_counter = multiprocessing.Value("i", 0)

# 全局限制
MAX_RERANKER_SCANS = 100

# 使用
with shared_scan_counter.get_lock():
    current_count = shared_scan_counter.value
    if current_count < MAX_RERANKER_SCANS:
        shared_scan_counter.value += 1
        # 执行reranking
```

#### 2. 批量相似度计算

```python
# 收集所有需要计算的键对
similarity_tasks = [
    (source_key, candidate_key)
    for candidate_key in candidate_keys
]

# 并行计算
with ThreadPoolExecutor() as executor:
    similarities = list(executor.map(
        lambda pair: calculate_similarity(*pair, ...),
        similarity_tasks
    ))
```

#### 3. 符号映射预加载

```python
# 一次性加载,所有文件共享
project_symbol_map = load_project_symbol_map()

# 传递给每个建议函数
suggest_python_dependencies(..., project_symbol_map)
suggest_javascript_dependencies(..., project_symbol_map)
```

### ⚠️ 注意事项

1. **AST树获取**:
```python
# 必须从专用的ast_cache获取,不在analysis_result中
ast_cache = cache_manager.get_cache("ast_cache")
tree = ast_cache.get(norm_source_path)

if not tree:
    logger.error("AST tree not found in 'ast_cache'")
    return {}  # 无法构建导入映射
```

2. **路径规范化**:
```python
# 始终使用normalize_path确保一致性
norm_path = normalize_path(raw_path)

# 路径比较
if norm_path1 == norm_path2:  # 可靠
if raw_path1 == raw_path2:    # 不可靠
```

3. **符号验证容错**:
```python
# 即使符号验证失败,仍然创建依赖建议
# 但标记为未验证
(target_path, '<', False)  # item_verified=False
```

4. **外部依赖过滤**:
```python
# 跳过node_modules, site-packages等外部依赖
if 'node_modules' in candidate_path:
    continue
if 'site-packages' in candidate_path:
    continue
```

---

## 数据流程图

### 完整分析流程

```
┌─────────────────────────────────────────────────────────────┐
│                   analyze_project()                         │
│                  (project_analyzer.py)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│Key Generation│ │File Analysis│ │Symbol Map   │
│(key_manager) │ │(analyzer)   │ │Generation   │
└──────┬───────┘ └──────┬──────┘ └──────┬──────┘
       │                │               │
       │                │               │
       ▼                ▼               ▼
┌─────────────────────────────────────────────┐
│         Path Migration Info                 │
│    (old_key -> new_key mapping)             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Embedding Generation                   │
│    (embedding_manager.py)                   │
│                                             │
│  1. Load Symbol Map                         │
│  2. Generate SES                            │
│  3. Select Best Model                       │
│  4. Batch Encode                            │
│  5. Save Vectors (.npy)                     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│    Dependency Suggestion (Parallel)         │
│   (dependency_suggester.py)                 │
│                                             │
│  1. Structural Dependencies                 │
│     ├─ Import Resolution                    │
│     ├─ Call Analysis                        │
│     └─ Symbol Verification                  │
│                                             │
│  2. Semantic Dependencies                   │
│     ├─ Vector Similarity                    │
│     ├─ Reranking (Qwen3)                    │
│     └─ Threshold Filtering                  │
│                                             │
│  3. Character Assignment                    │
│     └─ Priority-based Selection             │
└──────────────────┬──────────────────────────┘
                   │
       ┌───────────┼───────────────┐
       │           │               │
       ▼           ▼               ▼
┌───────────┐ ┌─────────┐ ┌──────────────┐
│Mini       │ │Doc      │ │Main Tracker  │
│Trackers   │ │Tracker  │ │(Aggregated)  │
│(Module)   │ │(Docs)   │ │              │
└─────┬─────┘ └────┬────┘ └──────┬───────┘
      │            │             │
      └────────────┼─────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         Visualization                       │
│   (visualize_dependencies.py)               │
│                                             │
│  1. Aggregate Dependencies                  │
│  2. Generate Mermaid Code                   │
│     ├─ Project Overview                     │
│     └─ Per-Module Diagrams                  │
└─────────────────────────────────────────────┘
```

### 数据流转

```
源文件 (.py, .js, .ts, .html, ...)
    │
    ├─> [analyze_file] ────────────────┐
    │   (dependency_analyzer.py)       │
    │                                  │
    │   • AST / Tree-sitter Parsing    │
    │   • Symbol Extraction            │
    │   • Dependency Identification    │
    │                                  │
    ▼                                  │
分析结果 (analysis_result)              │
    ├─ imports: List[Dict]             │
    ├─ functions: List[Dict]           │
    ├─ classes: List[Dict]             │
    ├─ calls: List[Dict]               │
    ├─ type_references: List[Dict]     │
    └─ ...                             │
    │                                  │
    ├─> [符号映射合并] ─────────────────┤
    │   (symbol_map_merger.py)         │
    │                                  │
    │   • Runtime Symbols (Primary)    │
    │   • AST Symbols (Enhancement)    │
    │   • Validation                   │
    │                                  │
    ▼                                  │
符号映射 (project_symbol_map.json)      │
    {                                  │
      "/path/file.py": {               │
        "file_type": "py",             │
        "functions": [...],            │
        "classes": [...],              │
        ...                            │
      }                                │
    }                                  │
    │                                  │
    ├─> [generate_embeddings] ────────┤
    │   (embedding_manager.py)         │
    │                                  │
    │   • Generate SES                 │
    │   • Encode to Vectors            │
    │   • Save to .npy                 │
    │                                  │
    ▼                                  │
嵌入向量 (.npy files)                   │
    │                                  │
    ├─> [suggest_dependencies] ───────┘
    │   (dependency_suggester.py)
    │
    │   • Structural Analysis
    │   • Semantic Similarity
    │   • Reranking
    │   • Character Assignment
    │
    ▼
依赖建议 (suggestions)
    [
      (target_path, char),
      ...
    ]
    │
    ├─> [路径->密钥转换]
    │
    ▼
KEY#instance格式建议
    {
      "KEY1#1": [
        ("KEY2#1", "<"),
        ("KEY3#1", "S"),
        ...
      ]
    }
    │
    ├─> [update_tracker]
    │   (tracker_io.py)
    │
    ▼
跟踪器文件 (.md)
    • <module>_module.md (Mini)
    • documentation.md (Doc)
    • dependencies_main.md (Main)
```

---

## 最佳实践

### 1. 性能优化

#### 使用批处理
```python
# 好的做法: 批量处理
analysis_results = process_items(
    files_to_analyze,
    analyze_file,
    force=force_analysis
)

# 差的做法: 顺序处理
analysis_results = [
    analyze_file(f) for f in files_to_analyze
]
```

#### 启用缓存
```python
# 好的做法: 利用缓存
result = analyze_file(file_path)  # 自动缓存

# 差的做法: 总是强制重新分析
result = analyze_file(file_path, force=True)
```

#### 共享预计算结果
```python
# 好的做法: 预聚合,所有图共享
aggregated = aggregate_all_dependencies(...)
for module in modules:
    generate_mermaid_diagram(..., pre_aggregated_links=aggregated)

# 差的做法: 每次重新聚合
for module in modules:
    # 内部重复聚合,浪费
    generate_mermaid_diagram(...)
```

### 2. 内存管理

#### 及时清理缓存
```python
# 分析结束后清理AST缓存
ast_cache = cache_manager.get_cache("ast_cache")
ast_cache.data.clear()

# 如果force_analysis,清除所有缓存
if force_analysis:
    clear_all_caches()
```

#### 卸载大模型
```python
# 分析完成后卸载Reranker
try:
    embedding_manager.unload_reranker_model()
except Exception as e:
    logger.warning(f"Reranker unload error: {e}")
```

### 3. 错误处理

#### 分级错误处理
```python
try:
    # 关键操作
    result = critical_operation()
except SpecificError as e:
    # 特定错误,记录详细信息
    logger.error(f"Specific error: {e}")
    return {"error": str(e)}
except Exception as e:
    # 通用错误,记录堆栈跟踪
    logger.exception(f"Unexpected error: {e}")
    return {"error": "Unexpected error"}
```

#### 部分失败容忍
```python
# 收集错误,不中断流程
errors = []
for item in items:
    try:
        process(item)
    except Exception as e:
        errors.append((item, str(e)))
        # 继续处理其他项

# 最后报告所有错误
if errors:
    logger.warning(f"Partial failures: {len(errors)}")
```

### 4. 配置管理

#### 使用配置阈值
```python
# 好的做法: 从配置读取
config = ConfigManager()
threshold = config.get_threshold("doc_similarity")

# 差的做法: 硬编码
threshold = 0.7
```

#### 尊重排除规则
```python
# 检查所有排除条件
if (
    path in excluded_paths
    or any(is_subpath(path, d) for d in excluded_dirs)
    or ext in excluded_extensions
    or any(fnmatch(name, p) for p in excluded_patterns)
):
    skip_file()
```

### 5. 日志记录

#### 分级日志
```python
logger.debug("Detailed information for debugging")
logger.info("Normal operation information")
logger.warning("Warning about potential issues")
logger.error("Error that doesn't stop execution")
logger.critical("Critical error, cannot continue")
```

#### 上下文信息
```python
# 好的做法: 包含上下文
logger.error(f"Failed to analyze {file_path}: {error}")

# 差的做法: 缺少上下文
logger.error(str(error))
```

### 6. 类型安全

#### 使用类型注解
```python
def analyze_file(
    file_path: str,
    force: bool = False
) -> Dict[str, Any]:
    ...
```

#### 验证数据结构
```python
# 验证必需字段
if "imports" not in analysis_result:
    analysis_result["imports"] = []
```

---

## 总结

### 模块关系总览

```
project_analyzer (协调器)
    │
    ├─ 调用 key_manager (密钥生成)
    ├─ 调用 dependency_analyzer (文件分析)
    │   └─ 返回 analysis_results
    │
    ├─ 调用 symbol_map_merger (符号合并)
    │   └─ 生成 project_symbol_map.json
    │
    ├─ 调用 embedding_manager (嵌入生成)
    │   ├─ 使用 project_symbol_map
    │   ├─ 生成 SES
    │   └─ 保存 .npy 文件
    │
    ├─ 调用 dependency_suggester (依赖建议)
    │   ├─ 使用 analysis_results
    │   ├─ 使用 embeddings
    │   ├─ 使用 symbol_map
    │   └─ 返回 suggestions + ast_links
    │
    ├─ 调用 tracker_io (跟踪器更新)
    │   └─ 写入 .md 跟踪器文件
    │
    └─ 调用 visualize_dependencies (可视化)
        └─ 生成 .mermaid 图文件
```

### 核心数据流

```
源代码文件
    ↓
[AST/Tree-sitter分析]
    ↓
分析结果 (imports, functions, classes, calls, ...)
    ↓
[符号映射合并]
    ↓
项目符号映射 (统一符号索引)
    ↓
[嵌入向量生成]
    ↓
向量表示 (.npy文件)
    ↓
[依赖建议]
    ├─ 结构化依赖 (< / >)
    ├─ 语义依赖 (s / S)
    └─ 文档依赖 (d)
    ↓
[字符优先级合并]
    ↓
最终依赖建议
    ↓
[路径->密钥转换]
    ↓
KEY#instance格式
    ↓
[跟踪器更新]
    ↓
Markdown跟踪器文件
    ↓
[可视化]
    ↓
Mermaid依赖图
```

### 关键技术点

1. **多语言支持**: AST (Python) + Tree-sitter (JS/TS/HTML/CSS)
2. **双重分析**: 结构化(AST) + 语义化(Embeddings)
3. **智能模型选择**: 根据硬件自动选择Qwen3-4B或mpnet
4. **Reranker增强**: Qwen3-Reranker提升语义匹配精度
5. **三级跟踪器**: Mini(模块) + Doc(文档) + Main(项目)
6. **字符优先级**: 明确的依赖类型层次
7. **性能优化**: 批处理、缓存、并行、共享计数器
8. **路径迁移**: 支持密钥变更时的平滑迁移

---

**文档维护者**: Claude Code
**最后更新**: 2025-12-15
**版本**: 1.0.0
