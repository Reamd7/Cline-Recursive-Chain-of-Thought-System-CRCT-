# Cline递归思维链系统（CRCT）- v8.0

欢迎使用**Cline递归思维链系统（CRCT）**，这是一个专为VS Code中的Cline扩展设计的框架，用于管理大型项目中的上下文、依赖关系和任务。CRCT基于递归的、基于文件的方法构建，采用模块化依赖跟踪系统，随着复杂性增加而维护项目状态和效率。

- 版本 **v8.0**: 🚀 **重大版本** - 嵌入与分析系统全面升级
    - **符号本质字符串（Symbol Essence Strings, SES）**: 革命性的嵌入架构，结合运行时 + AST元数据，准确性提升10倍
    - **Qwen3重排序器（Qwen3 Reranker）**: AI驱动的语义依赖评分，支持自动模型下载
    - **硬件自适应模型（Hardware-Adaptive Models）**: 根据可用资源自动在GGUF（Qwen3-4B）和SentenceTransformer之间选择
    - **运行时符号检查（Runtime Symbol Inspection）**: 从实时Python模块深度提取元数据（类型、继承、装饰器）
    - **阶段跟踪器用户体验（PhaseTracker UX）**: 为所有长时间运行的操作提供实时进度条和预计完成时间
    - **增强分析（Enhanced Analysis）**: 高级调用过滤、去重、内部/外部检测
    - **重大变更（Breaking Changes）**: `set_char`已弃用，`exceptions.py`已移除，新增依赖（`llama-cpp-python`），需要重新运行`analyze-project`。详见[MIGRATION_v7.x_to_v8.0.md](MIGRATION_v7.x_to_v8.0.md)
- 版本 **v7.90**: 引入依赖可视化，全面改进策略阶段以实现迭代路线图规划，并完善分层设计令牌架构（Hierarchical Design Token Architecture, HDTA）模板。
    - **依赖可视化（`visualize-dependencies`）**:
        - 新增命令以生成Mermaid图表，可视化项目依赖关系。
        - 支持项目概览、模块聚焦（内部+接口）和多键聚焦视图。
        - `analyze-project`期间自动生成概览和模块图表（可配置）。
        - 图表默认保存到`<memory_dir>/dependency_diagrams/`。
        - **新增**集成mermaid-cli以将依赖图表渲染为.svg文件（实验阶段，渲染过程可能变更）
            - 在边数少于1000时表现良好，超过1500条边会很吃力。大型4000+边图表会可靠超时。
            - 需要额外安装依赖，应通过`npm install`完成
    - **依赖分析和建议**
        - 使用Python AST增强（针对Python）
        - 使用tree-sitter增强（针对.js、.ts、.tsx、.html、.css）
        - 更多功能即将推出！
    - **策略阶段全面改进（`strategy_plugin.md`）：**
        - 将整体规划替换为**迭代的、基于区域的工作流**，专注于最小化上下文加载，使其更适合LLM执行。
        - 明确主要目标为使用HDTA进行**分层项目路线图构建和维护**。
        - 集成利用依赖图表（自动生成或按需生成）以辅助分析的指令。
        - 完善状态管理（`.clinerules` vs. `activeContext.md`）。
        - 拆分为调度和工作提示，以利用new_task
    - **HDTA模板更新**:
        - 重新设计`implementation_plan_template.md`，专注于目标/特性。
        - 为`module_template.md`和`task_template.md`添加说明性指令。
        - 创建新的`roadmap_summary_template.md`用于统一周期计划。
- 版本 **v7.7**: 重构核心提示/插件，引入`cleanup_consolidation_plugin.md`阶段（由于文件操作请谨慎使用），添加`hdta_review_progress`和`hierarchical_task_checklist`模板。
- 版本 **v7.5**: 重大基础重构，建立核心架构、上下文键（Contextual Keys，`KeyInfo`）、分层依赖聚合（Hierarchical Dependency Aggregation）、增强`show-dependencies`、可配置嵌入设备、文件排除模式、改进缓存和批处理。

---

## 系统要求

### 推荐配置（v8.0+）
- **显存（VRAM）**: 8GB+（NVIDIA GPU）以获得最佳Qwen3-4B模型性能
- **内存（RAM）**: 16GB+（大型项目）
- **磁盘空间**: 2GB+（模型和嵌入）
- **Python**: 3.8+
- **Node.js**: 16+（用于mermaid-cli可视化）

### 最低配置
- **内存（RAM）**: 4GB（仅CPU模式，批次大小减少）
- **磁盘空间**: 500MB+（轻量级模型）
- **Python**: 3.8+

*系统会自动适配可用硬件。*

---

## 主要特性

- **递归分解（Recursive Decomposition）**: 将任务分解为可管理的子任务，通过目录和文件组织，实现隔离的上下文管理。
- **最小上下文加载（Minimal Context Loading）**: 仅加载必要数据，根据需要通过依赖跟踪器扩展。
- **持久状态（Persistent State）**: 使用VS Code文件系统存储上下文、指令、输出和依赖关系。通过**强制更新协议（Mandatory Update Protocol, MUP）**在操作后和操作期间定期严格维护状态完整性。
- **模块化依赖系统（Modular Dependency System）**: 完全模块化的依赖跟踪系统。
- **上下文键（Contextual Keys）**: 引入`KeyInfo`用于上下文丰富的键，实现更准确的分层依赖跟踪。
- **分层依赖聚合（Hierarchical Dependency Aggregation）**: 为主跟踪器实现分层汇总和外部依赖聚合，提供更全面的项目依赖视图。
- **增强依赖工作流（Enhanced Dependency Workflow）**: 简化的工作流简化了依赖管理。
    - `show-keys`识别特定跟踪器中需要注意的键（'p'、's'、'S'）。
    - `show-dependencies`聚合*所有*跟踪器中特定键的依赖详细信息（入站/出站、路径），消除手动解析跟踪器的需要。
    - `add-dependency`解析通过此过程识别的占位符（'p'）或建议（'s'、'S'）关系。**关键是，当针对微跟踪器（`*_module.md`）时，`add-dependency`现在允许指定本地不存在的`--target-key`，只要目标键在全局范围内有效（从`analyze-project`已知）。系统会自动添加外部键定义并更新网格，实现手动链接到外部依赖。**
      *   **提示：** 这对于在微跟踪器中手动链接相关文档文件（例如需求、设计规范、API描述）到代码文件特别有用，即使代码文件不完整或未触发自动建议。这为LLM在代码生成或修改任务期间提供关键上下文，引导其朝着文档中描述的预期功能发展（`doc_key < code_key`）。
   - **依赖可视化（`visualize-dependencies`）**: **（v7.8新增）**
    - 生成Mermaid图表，用于项目概览、模块范围（内部+接口）或特定键聚焦。
    - 通过`analyze-project`自动生成概览/模块图表。
    - **v7.90新增** 现在如果安装了mermaid-cli依赖，可生成.svg图像文件用于图表可视化。
- **迭代策略阶段（Iterative Strategy Phase）**: **（v7.8新增）**
    - 迭代规划项目路线图，一次专注于一个区域（模块/特性）。
    - 明确将依赖分析（文本+可视化）集成到规划中。
- **完善的HDTA模板（Refined HDTA Templates）**: **（v7.8新增）**
    - 改进的实施计划、模块和任务模板。
    - 新增路线图摘要模板。
- **可配置嵌入设备（Configurable Embedding Device）**: 允许用户通过`.clinerules.config.json`配置嵌入设备（`cpu`、`cuda`、`mps`），以在不同硬件上优化性能。（注意：*系统尚未自动安装cuda或mps的要求，请手动安装要求或借助LLM帮助。*）
- **文件排除模式（File Exclusion Patterns）**: 用户现在可以在`.clinerules.config.json`中定义文件排除模式，以自定义项目分析。
- **代码质量分析（Code Quality Analysis）**: **（v8.0新增）**
    - **报告生成器（Report Generator）**: 新工具（`report_generator.py`）执行基于AST的代码质量分析。
    - **不完整代码检测（Incomplete Code Detection）**: 使用强大的Tree-sitter解析识别`TODO`、`FIXME`、空函数/类和`pass`语句，支持Python、JavaScript和TypeScript。
    - **未使用项检测（Unused Item Detection）**: 与Pyright集成以报告未使用的变量、导入和函数。
    - **可操作报告（Actionable Reports）**: 生成详细的`code_analysis/issues_report.md`以指导清理工作。
- **缓存和批处理（Caching and Batch Processing）**: 显著提高性能。
- **模块化依赖跟踪（Modular Dependency Tracking）**:
    - 使用主跟踪器（`module_relationship_tracker.md`、`doc_tracker.md`）和模块特定的微跟踪器（`{module_name}_module.md`）。
    - 微跟踪器文件也作为其各自模块的HDTA领域模块文档。
    - 采用分层键和RLE压缩以提高效率。
- **自动化操作（Automated Operations）**: 系统操作现在在很大程度上自动化并浓缩为单个命令，简化工作流并减少手动命令执行。
- **基于阶段的工作流（Phase-Based Workflow）**: 在不同阶段运行：设置/维护 -> 策略 -> 执行 -> 清理/整合，由`.clinerules`控制。
- **思维链推理（Chain-of-Thought Reasoning）**: 通过逐步推理和反思确保透明度。

---

## 快速开始

1. **克隆仓库**:
   ```bash
   git clone https://github.com/RPG-fan/Cline-Recursive-Chain-of-Thought-System-CRCT-.git
   cd Cline-Recursive-Chain-of-Thought-System-CRCT-
   ```

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   npm install  # 用于mermaid-cli可视化
   ```

3. **设置Cline或RooCode扩展**:
   - 在VS Code中打开项目，确保已安装Cline或RooCode扩展。
   - 将`cline_docs/prompts/core_prompt(put this in Custom Instructions).md`的内容复制到Cline自定义指令字段。（新流程待更新）

4. **启动系统**:
   - 在Cline输入中输入`Start.`以初始化系统。
   - LLM将从`.clinerules`引导，创建缺失的文件，并在需要时指导您完成设置。

*注意*: Cline扩展的LLM会自动执行大多数命令和对`cline_docs/`的更新。理论上需要最少的用户干预！

---

## 项目结构

```
Cline-Recursive-Chain-of-Thought-System-CRCT-/
│   .clinerules/
│   .clinerules.config.json       # 依赖系统配置
│   .gitignore
│   CHANGELOG.md                  # 版本历史 <v8.0新增>
│   INSTRUCTIONS.md
│   LICENSE
│   MIGRATION_v7.x_to_v8.0.md     # 升级指南 <v8.0新增>
│   README.md
│   requirements.txt
│
├───cline_docs/                   # 操作记忆
│   │  activeContext.md           # 当前状态和优先级
│   │  changelog.md               # 记录重大变更
│   │  userProfile.md             # 用户配置文件和偏好
│   │  progress.md                # 高级项目清单
│   │
│   ├──backups/                   # 跟踪器文件备份
│   ├──dependency_diagrams/       # 自动生成的Mermaid图表默认位置 <新增>
│   ├──prompts/                   # 系统提示和插件
│   │    core_prompt.md           # 核心系统指令
│   |    cleanup_consolidation_plugin.md <较新>
│   │    execution_plugin.md
│   │    setup_maintenance_plugin.md
│   │    strategy_plugin.md         <已修订>
│   ├──templates/                 # HDTA文档模板
│   │    hdta_review_progress_template.md <较新>
│   │    hierarchical_task_checklist_template.md <较新>
│   │    implementation_plan_template.md <已修订>
│   │    module_template.md         <小更新>
│   │    roadmap_summary_template.md  <新增>
│   │    system_manifest_template.md
│   │    task_template.md           <小更新>
│
├───cline_utils/                  # 实用脚本
│   └─dependency_system/
│     │ dependency_processor.py   # 依赖管理脚本 <已修订>
│     ├──analysis/                # 分析模块 <v8.0重大更新>
│     │    dependency_analyzer.py   <2倍增长>
│     │    dependency_suggester.py  <1.9倍增长>
│     │    embedding_manager.py     <3.4倍增长>
│     │    project_analyzer.py      <1.7倍增长>
│     │    reranker_history_tracker.py <新增>
│     │    runtime_inspector.py     <新增>
│     ├──core/                    # 核心模块 <已修订key_manager.py>
│     │    exceptions_enhanced.py  <新增 - 替换exceptions.py>
│     ├──io/                      # IO模块
│     └──utils/                   # 实用模块
│          batch_processor.py      <使用PhaseTracker增强>
│          cache_manager.py        <2倍增长 - 压缩、策略>
│          config_manager.py       <2倍增长 - 大量新配置>
│          phase_tracker.py        <新增 - 进度条>
│          resource_validator.py   <新增 - 系统检查>
│          symbol_map_merger.py    <新增 - 运行时+AST合并>
│          visualize_dependencies.py <新增>
│
├───docs/                         # 项目文档
├───models/                       # AI模型（自动下载）<新增>
└───src/                          # 源代码根目录

```
*（已添加/更新相关文件/目录）*

---

## 当前状态与未来计划

- **v8.0**: 🚀 **重大架构演进** - 符号本质字符串（Symbol Essence Strings）、Qwen3重排序器、硬件自适应模型、运行时符号检查、使用PhaseTracker增强的用户体验。详见[CHANGELOG.md](CHANGELOG.md)了解完整详情。
- **v7.8**: 专注于**视觉理解和规划稳健性**。引入Mermaid依赖图表（`visualize-dependencies`，通过`analyze-project`自动生成）。全面改进策略阶段（`strategy_plugin.md`），实现迭代的、基于区域的路线图规划，明确使用可视化。完善HDTA模板，包括新的`roadmap_summary_template.md`。
- **v7.7**: 引入`cleanup_consolidation`阶段，添加规划/审查跟踪器模板。
- **v7.5**: 基础重构：上下文键、分层聚合、`show-dependencies`、配置增强、性能改进（缓存/批处理）。

**未来重点**: 继续完善性能、可用性和稳健性。v8.x系列将专注于基于实际使用优化新的重排序和SES系统。未来版本可能包括基于MCP的工具使用，以及从文件系统向数据库聚焦操作的过渡。

欢迎反馈！请通过GitHub Issues报告错误或建议。

---

## 入门指南（可选 - 现有项目）

要在现有项目上测试：
1. 将您的项目复制到`src/`中。
2. 使用这些提示启动LLM：
   - `Perform initial setup and populate dependency trackers.`（执行初始设置并填充依赖跟踪器。）
   - `Review the current state and suggest next steps.`（审查当前状态并建议下一步。）

系统将分析您的代码库，初始化跟踪器，并引导您前进。

---

## 致谢！

非常感谢 https://github.com/biaomingzhong 提供的详细指令，这些指令已集成到核心提示和插件中！（PR #25）

这是一项热爱之作，旨在使Cline项目更易于管理。我很想听听您的想法——试试看，让我知道什么有效（或无效）！
