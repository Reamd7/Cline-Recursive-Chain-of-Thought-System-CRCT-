# Phase 3 Mermaid 图表任务详细设计 - 分形方法论

**Date**: 2025-12-29
**基于**: dependency_system 代码深度分析
**方法论**: 分形架构 (Fractal Architecture) - 多层完整视图,仅抽象程度不同

---

## 一、代码分析总结

### 1.1 核心发现

通过深入分析 `dependency_system` 代码结构,发现以下关键内在联系:

**数据流主线**:
```
CLI Command
  ↓
dependency_processor (命令分发)
  ↓
project_analyzer (9阶段分析流程)
  ↓
[核心分析管道]
  Phase 3: Key Generation (key_manager)
  Phase 4: Symbol Mapping (symbol_map_merger)
  Phase 5: Embedding Generation (embedding_manager + Qwen3 Reranker)
  Phase 6: Dependency Suggestion (dependency_suggester)
  ↓
[持久化]
  mini/doc/main 三级跟踪器 (tracker_io)
  ↓
[输出]
  Mermaid 可视化 (visualize_dependencies)
```

**核心数据结构转换链**:
```
源文件 (Source Files)
  ↓ [AST 解析]
符号表 (Symbol Map)
  ↓ [向量化]
嵌入向量 (Embeddings)
  ↓ [语义匹配]
依赖网格 (DependencyGrid)
  ↓ [RLE 压缩]
跟踪器数据 (Tracker Data)
```

### 1.2 四个子系统协同

1. **core/** - 核心数据结构
   - KeyInfo: 唯一标识符系统
   - DependencyGrid: 依赖关系矩阵 (RLE 压缩)
   - 路径迁移机制

2. **analysis/** - 分析引擎
   - 6 个分析器流水线
   - AST + 语义双轨分析
   - Qwen3 Reranker 重排序

3. **utils/** - 工具集
   - BatchProcessor: 并行处理
   - CacheManager: 三级缓存
   - PhaseTracker: 实时进度

4. **io/** - 持久化
   - 三级跟踪器 (mini/doc/main)
   - 序列化/反序列化

---

## 二、分形架构设计

### 2.1 分形层级定义

遵循分形思想: **每个层级都是完整、独立的视图,仅抽象程度不同**

```
层级 1: 系统级 (System Level)
  视角: 黑盒系统
  抽象程度: 最高
  完整性: 展示端到端数据流
  独立性: 无需了解内部实现即可理解

层级 2: 模块级 (Module Level)
  视角: 子系统交互
  抽象程度: 高
  完整性: 展示模块间调用关系
  独立性: 无需了解模块内部即可理解协作

层级 3: 组件级 (Component Level)
  视角: 类和函数
  抽象程度: 中
  完整性: 展示模块内部结构
  独立性: 无需了解函数细节即可理解组件职责

层级 4: 函数级 (Function Level)
  视角: 算法逻辑
  抽象程度: 低
  完整性: 展示关键算法执行流程
  独立性: 每个函数流程图自包含

层级 5: 数据流级 (Data Flow Level)
  视角: 数据转换
  抽象程度: 最低
  完整性: 展示数据在各层级的转换过程
  独立性: 追踪单个数据项的完整生命周期
```

### 2.2 分形自相似性

每个层级都包含:
- **输入 → 处理 → 输出** 的完整流程
- **数据转换**的清晰标注
- **错误处理**路径
- **并行机会**的标识

---

## 三、详细任务设计 (28个 Mermaid 图表)

### 层级 1: 系统级 (2个任务)

#### T088: 系统级数据流图
**文件**: ARCHITECTURE.md
**标题**: Level 1: System-Level Data Flow (系统级数据流)
**图表类型**: flowchart LR (左到右流程图)

**节点**:
- CLI Input (命令输入)
- dependency_processor (命令处理器)
- Analysis Engine (分析引擎)
- Three-Tier Trackers (三级跟踪器)
- Visualization (可视化输出)
- Report Generation (报告生成)

**数据流标注**:
```
CLI Input --命令--> dependency_processor
dependency_processor --配置--> Analysis Engine
Analysis Engine --分析结果--> Three-Tier Trackers
Three-Tier Trackers --依赖数据--> Visualization
Three-Tier Trackers --统计信息--> Report Generation
```

**关键转换节点** (用特殊颜色标注):
1. 命令解析节点 (Command Parsing)
2. 文件扫描节点 (File Scanning)
3. 符号提取节点 (Symbol Extraction)
4. 嵌入生成节点 (Embedding Generation)
5. 依赖更新节点 (Dependency Updates)

#### T089: 系统级错误处理流程图
**文件**: ARCHITECTURE.md
**标题**: Level 1: Error Handling Flow (错误处理流程)
**图表类型**: flowchart TD

**展示内容**:
- 异常捕获点
- 错误恢复机制
- 缓存失效策略
- 用户提示输出

---

### 层级 2: 模块级 (8个任务)

#### T090: dependency_processor 命令调度流程
**文件**: ARCHITECTURE.md
**图表类型**: flowchart TD

**展示内容**:
```
argparse 解析
  ↓
命令分发
  ├── analyze-project → analyze_project()
  ├── show-dependencies → tracker_io + visualize
  ├── update-tracker → tracker_io.update_tracker()
  ├── export → tracker_io.export_tracker()
  └── clear-cache → cache_manager.clear_all_caches()
```

**子系统接口标注**:
- core/ 接口: KeyInfo, DependencyGrid
- analysis/ 接口: analyze_project, analyze_file
- utils/ 接口: ConfigManager, PhaseTracker
- io/ 接口: tracker_io 所有函数

#### T091: project_analyzer 9阶段分析管道
**文件**: ARCHITECTURE.md
**图表类型**: flowchart TB (自上而下)

**完整流程**:
```
Phase 1: 初始化
  ├─ ConfigManager 加载配置
  ├─ PhaseTracker 初始化
  └─ 清除缓存 (可选)
  ↓
Phase 2: 文件识别
  ├─ 扫描项目目录
  ├─ 应用排除规则
  └─ 过滤文件类型
  ↓
Phase 3: 密钥生成
  ├─ key_manager 为每个文件生成 KeyInfo
  └─ 构建全局键映射
  ↓
Phase 4: 符号映射
  ├─ runtime_inspector 提取运行时符号
  ├─ symbol_map_merger 合并符号表
  └─ 构建项目级符号映射
  ↓
Phase 5: 嵌入生成
  ├─ embedding_manager 批量生成嵌入
  ├─ Qwen3 Reranker 语义重排序
  └─ 持久化嵌入向量
  ↓
Phase 6: 依赖建议
  ├─ dependency_analyzer AST 分析
  ├─ dependency_suggester 语义匹配
  └─ 合并结构+语义依赖
  ↓
Phase 7: 跟踪器更新
  ├─ 更新 mini-tracker (单个文件)
  ├─ 更新 doc-tracker (文档级)
  └─ 更新 main-tracker (项目级)
  ↓
Phase 8: 模板生成
  └─ template_generator 生成审查清单
  ↓
Phase 9: 可视化
  └─ visualize_dependencies 自动生成 Mermaid 图
```

**数据流转标注**:
- Phase 3 输出 → Phase 4 输入
- Phase 4 输出 → Phase 5 输入
- Phase 5 输出 → Phase 6 输入
- Phase 6 输出 → Phase 7 输入

#### T092: 四个子系统交互关系图
**文件**: ARCHITECTURE.md
**图表类型**: graph LR

**节点和关系**:
```
dependency_processor (中心调度器)
  ↓ 调用
project_analyzer (分析编排器)
  ↓ 使用
├─ core/ (数据结构)
│   ├── KeyInfo
│   └── DependencyGrid
├─ analysis/ (分析器)
│   ├── dependency_analyzer
│   ├── symbol_map_merger
│   ├── embedding_manager
│   └── dependency_suggester
├─ utils/ (工具)
│   ├── BatchProcessor
│   ├── CacheManager
│   └── PhaseTracker
└─ io/ (持久化)
    ├── tracker_io
    └── 三级跟踪器
```

**关键数据结构流转**:
```
KeyInfo (core/)
  ↓ 传递给
symbol_map_merger (analysis/)
  ↓ 结合
Embedding (analysis/)
  ↓ 匹配生成
DependencyGrid (core/)
  ↓ 压缩存储
TrackerData (io/)
```

#### T093-T097: 其他模块级流程图
(按照相同模式设计,每个都展示完整的模块交互和数据流)

---

### 层级 3: 组件级 (10个任务)

#### T096: core/ 核心数据结构类图
**文件**: ARCHITECTURE.md
**图表类型**: classDiagram

**类和关系**:
```
class KeyInfo {
  +key: str
  +global_instance: int
  +path: str
  +get_sortable_parts()
  +to_tracker_string()
}

class DependencyGrid {
  +grid: Dict[str, str]
  +compress()
  +decompress()
  +get_char_at()
}

class PathMigrationInfo {
  +old_key: Optional[str]
  +new_key: Optional[str]
}

KeyInfo --> DependencyGrid : 依赖
KeyInfo --> PathMigrationInfo : 迁移
```

#### T097: DependencyGrid RLE 压缩算法
**文件**: ARCHITECTURE.md
**图表类型**: flowchart TD

**算法流程**:
```
原始网格 (Grid)
  ↓ 扫描
识别连续字符
  ↓ 计数
生成 (字符 + 计数) 对
  ↓ 组合
压缩字符串 (RLE)
```

**示例**:
```
原始: "....X.."
压缩: "4.1X2."
```

#### T098: analysis/ 分析流水线
**文件**: ARCHITECTURE.md
**图表类型**: flowchart LR

**6个分析器协作**:
```
源文件
  ↓
[1] dependency_analyzer (AST 解析)
  ↓ 符号
[2] runtime_inspector (运行时提取)
  ↓ 符号
[3] symbol_map_merger (符号合并)
  ↓ 符号表
[4] embedding_manager (向量化)
  ↓ 嵌入
[5] dependency_suggester (语义匹配)
  ↓ 候选依赖
[6] re-ranking (Qwen3 Reranker)
  ↓ 最终依赖
```

#### T099: dependency_analyzer AST 分析流程
**文件**: ARCHITECTURE.md
**图表类型**: flowchart TD

**详细流程**:
```
Python 源文件
  ↓
AST 解析器 (ast.parse)
  ↓
遍历 AST 节点
  ├─ Import 节点 → 提取导入依赖
  ├─ FunctionDef 节点 → 提取函数定义
  ├─ ClassDef 节点 → 提取类定义
  └─ Call 节点 → 提取调用关系
  ↓
构建依赖关系
  ↓
返回: imports + defines + calls
```

#### T100: embedding_manager 嵌入生成流程
**文件**: ARCHITECTURE.md
**图表类型**: flowchart TD

**完整流程**:
```
符号列表
  ↓ 批处理
BatchProcessor (并行)
  ↓
生成初始嵌入
  ├─ 硬件检测 (GPU/CPU)
  ├─ 模型选择 (Qwen3-4B/SentenceTransformer)
  └─ 批量推理
  ↓
Qwen3 Reranker 重排序
  ├─ 计算相似度矩阵
  ├─ Top-K 选择
  └─ 结果重排
  ↓
持久化嵌入向量
```

#### T101-T105: 其他组件级流程图
(按照相同模式设计)

---

### 层级 4: 函数级 (6个任务)

#### T106: analyze_project() 主函数详细执行流程
**文件**: ARCHITECTURE.md
**图表类型**: flowchart TD

**完整逻辑**:
```
开始 analyze_project()
  ↓
Phase 1: 初始化
  ├─ 加载配置
  ├─ 初始化 PhaseTracker
  └─ 清除缓存 (如果 force_analysis)
  ↓
Phase 2: 扫描文件
  ├─ 应用排除规则
  └─ 过滤文件类型
  ↓
[... 9个阶段完整展示 ...]
  ↓
返回 analysis_results
```

**错误处理**:
```
每个阶段
  ↓
try:
    执行逻辑
except Exception as e:
    记录错误
    添加到 warnings
    继续执行 (不中断)
```

#### T107: suggest_dependencies() 依赖建议算法
**文件**: ARCHITECTURE.md
**图表类型**: flowchart TD

**算法流程**:
```
输入: 符号列表 + 嵌入向量
  ↓
阶段 1: 结构匹配 (AST)
  ├─ 查找已定义符号
  └─ 匹配导入/调用
  ↓
阶段 2: 语义匹配 (嵌入)
  ├─ 计算向量相似度
  └─ Top-K 候选
  ↓
阶段 3: 合并结果
  ├─ 结构依赖 + 语义依赖
  └─ 去重
  ↓
阶段 4: 阈值过滤
  ├─ 相似度 > threshold
  └─ 返回最终依赖列表
```

#### T108-T111: 其他函数级流程图
(按照相同模式设计)

---

### 层级 5: 数据流级 (2个任务)

#### T112: 源文件到嵌入向量的数据流追踪
**文件**: ARCHITECTURE.md
**图表类型**: flowchart LR

**完整追踪**:
```
源文件 (example.py)
  ↓ [AST 解析]
抽象语法树 (AST)
  ↓ [符号提取]
符号表 (Symbol Map)
  ↓ [向量化]
嵌入向量 (Embedding: [0.23, -0.45, ...])
  ↓ [持久化]
磁盘存储 (embeddings.npy)
```

**每个节点标注**:
- 输入数据格式
- 输出数据格式
- 处理时间估算
- 缓存策略

#### T113: 依赖分析到跟踪器更新的数据流
**文件**: ARCHITECTURE.md
**图表类型**: flowchart LR

**完整追踪**:
```
分析结果
  ↓ [构建]
DependencyGrid (未压缩)
  ↓ [RLE 压缩]
压缩字符串 (Compressed String)
  ↓ [序列化]
Tracker Data (JSON)
  ↓ [写入]
mini-tracker / doc-tracker / main-tracker
```

---

## 四、实施顺序建议

### Sprint 1: 层级 1 + 层级 2 (宏观视图)
**任务**: T088-T095
**时间**: 2-3天
**价值**: 提供系统整体架构理解

### Sprint 2: 层级 3 (组件视图)
**任务**: T096-T105
**时间**: 3-4天
**价值**: 理解各子系统内部结构

### Sprint 3: 层级 4 + 层级 5 (微观视图)
**任务**: T106-T115
**时间**: 2-3天
**价值**: 理解关键算法和数据流

---

## 五、质量标准

### 5.1 分形完整性检查清单

每个层级必须满足:
- [ ] **独立性**: 该层级图可以独立理解,无需查看其他层级
- [ ] **完整性**: 展示该抽象级别的所有关键组件
- [ ] **数据流**: 标注数据在组件间的流转
- [ ] **双语标签**: 所有节点使用中英双语

### 5.2 Mermaid 语法标准

- [ ] 使用正确的图表类型 (flowchart/graph/classDiagram)
- [ ] 节点 ID 使用驼峰命名 (PascalCase)
- [ ] 标签使用中文为主,英文为辅
- [ ] 箭头和关系清晰标注
- [ ] 子图使用 subgraph 语法

### 5.3 可视化效果标准

- [ ] 使用 Mermaid Live Editor 验证渲染效果
- [ ] 图表在 GitHub/GitLab 中正确显示
- [ ] 节点布局合理,避免交叉箭头
- [ ] 使用样式区分不同类型节点 (颜色/形状)

---

## 六、任务依赖关系

```
T088 (系统级数据流) → T089 (错误处理)
  ↓
T090 (命令调度) + T091 (9阶段管道) + T092 (子系统交互)
  ↓
T096-T105 (组件级详细图)
  ↓
T106-T115 (函数级+数据流级)
```

**并行机会**:
- 层级 2 的 T090/T091/T092 可以并行
- 层级 3 的 core/、analysis/、utils/、io/ 可以并行
- 层级 4 的函数流程图可以并行

---

**设计版本**: 1.0
**总任务数**: 28 个 Mermaid 图表
**生成日期**: 2025-12-29
**预计工作量**: 8-10 个工作日
