# Cline Recursive Chain-of-Thought System (CRCT) - v8.0

## Cline 递归思维链系统 (CRCT) - v8.0

Welcome to the **Cline Recursive Chain-of-Thought System (CRCT)**, a framework designed to manage context, dependencies, and tasks in large-scale Cline projects within VS Code. Built for the Cline extension, CRCT leverages a recursive, file-based approach with a modular dependency tracking system to maintain project state and efficiency as complexity increases.

欢迎使用 **Cline 递归思维链系统 (CRCT)**,这是一个为在 VS Code 中管理大规模 Cline 项目的上下文、依赖和任务而设计的框架。专为 Cline 扩展构建,CRCT 采用递归的、基于文件的方法,结合模块化依赖跟踪系统,在复杂度增加时保持项目状态和效率。

- Version **v8.0**: 🚀 **MAJOR RELEASE** - Embedding & analysis system overhaul
    - **Symbol Essence Strings (SES)**: Revolutionary embedding architecture combining runtime + AST metadata for 10x better accuracy
    - **Qwen3 Reranker**: AI-powered semantic dependency scoring with automatic model download
    - **Hardware-Adaptive Models**: Automatically selects between GGUF (Qwen3-4B) and SentenceTransformer based on available resources
    - **Runtime Symbol Inspection**: Deep metadata extraction from live Python modules (types, inheritance, decorators)
    - **PhaseTracker UX**: Real-time progress bars with ETA for all long-running operations
    - **Enhanced Analysis**: Advanced call filtering, deduplication, internal/external detection
    - **Breaking Changes**: `set_char` deprecated, `exceptions.py` removed, new dependencies (`llama-cpp-python`), requires re-run of `analyze-project`. See [MIGRATION_v7.x_to_v8.0.md](MIGRATION_v7.x_to_v8.0.md)

- 版本 **v8.0**: 🚀 **主要版本发布** - 嵌入 (Embedding) 和分析系统全面升级
    - **符号本质字符串 (SES)**: 革命性的嵌入架构,结合运行时和 AST 元数据,准确率提升 10 倍
    - **Qwen3 重排序器 (Reranker)**: AI 驱动的语义依赖评分,支持自动模型下载
    - **硬件自适应模型**: 根据可用资源自动在 GGUF (Qwen3-4B) 和 SentenceTransformer 之间选择
    - **运行时符号检查**: 从活跃 Python 模块深度提取元数据 (类型、继承、装饰器)
    - **PhaseTracker 用户体验**: 为所有长时间运行的操作提供实时进度条和预计完成时间 (ETA)
    - **增强分析**: 高级调用过滤、去重、内部/外部检测
    - **重大变更**: `set_char` 已弃用,`exceptions.py` 已移除,新增依赖 (`llama-cpp-python`),需要重新运行 `analyze-project`。参见 [MIGRATION_v7.x_to_v8.0.md](MIGRATION_v7.x_to_v8.0.md)
- Version **v7.90**: Introduces dependency visualization, overhauls the Strategy phase for iterative roadmap planning, and refines Hierarchical Design Token Architecture (HDTA) templates.
    - **Dependency Visualization (`visualize-dependencies`)**:
        - Added a new command to generate Mermaid diagrams visualizing project dependencies.
        - Supports project overview, module-focused (internal + interface), and multi-key focused views.
        - Auto-generates overview and module diagrams during `analyze-project` (configurable).
        - Diagrams saved by default to `<memory_dir>/dependency_diagrams/`.
        - **NEW** integrated mermaid-cli to render dependency diagrams as .svg files. (experimental stage, subject to change in rendering process)
            - Performs well under 1000 edges to render, struggles with more than 1500 edges. Will reliably time-out with large 4000+ edge diagrams.
            - Requires additional dependency installation, should work via `npm install`
    - **Dependency Analysis and Suggestions**
        - Enhanced with python AST (for python)
        - Enhanced with tree-sitter (for .js, .ts, .tsx, .html, .css)
        - More to come!
    - **Strategy Phase Overhaul (`strategy_plugin.md`):**
        - Replaced monolithic planning with an **iterative, area-based workflow** focused on minimal context loading, making it more robust for LLM execution.
        - Clarified primary objective as **hierarchical project roadmap construction and maintenance** using HDTA.
        - Integrated instructions for leveraging dependency diagrams (auto-generated or on-demand) to aid analysis.
        - Refined state management (`.clinerules` vs. `activeContext.md`).
        - Split into Dispatch and Worker prompts to take advantage of new_task
    - **HDTA Template Updates**:
        - Reworked `implementation_plan_template.md` for objective/feature focus.
        - Added clarifying instructions to `module_template.md` and `task_template.md`.
        - Created new `roadmap_summary_template.md` for unified cycle plans.

- 版本 **v7.90**: 引入依赖可视化,重构策略阶段以支持迭代路线图规划,并完善分层设计令牌架构 (HDTA) 模板。
    - **依赖可视化 (`visualize-dependencies`)**:
        - 新增命令,用于生成可视化项目依赖的 Mermaid 图表。
        - 支持项目概览、模块聚焦 (内部 + 接口) 和多键聚焦视图。
        - 在 `analyze-project` 期间自动生成概览和模块图表 (可配置)。
        - 图表默认保存到 `<memory_dir>/dependency_diagrams/`。
        - **新增** 集成 mermaid-cli 将依赖图表渲染为 .svg 文件 (实验阶段,渲染过程可能发生变化)。
            - 渲染少于 1000 条边时性能良好,超过 1500 条边时较为吃力。超过 4000+ 条边的大型图表将超时。
            - 需要安装额外的依赖,应通过 `npm install` 安装
    - **依赖分析和建议**
        - 使用 Python AST 增强 (用于 Python)
        - 使用 tree-sitter 增强 (用于 .js, .ts, .tsx, .html, .css)
        - 更多功能敬请期待!
    - **策略阶段重构 (`strategy_plugin.md`)**:
        - 用 **迭代的、基于区域的工作流** 替换了单体规划,专注于最小上下文加载,使 LLM 执行更加稳健。
        - 明确主要目标为使用 HDTA **构建和维护分层项目路线图**。
        - 集成利用依赖图表 (自动生成或按需) 的指令以辅助分析。
        - 完善状态管理 (`.clinerules` vs. `activeContext.md`)。
        - 拆分为调度器和工作器提示词以利用 new_task
    - **HDTA 模板更新**:
        - 重新设计 `implementation_plan_template.md` 以聚焦目标/功能。
        - 为 `module_template.md` 和 `task_template.md` 添加了说明性指令。
        - 创建新的 `roadmap_summary_template.md` 用于统一周期计划。
- Version **v7.7**: Restructured core prompt/plugins, introduced `cleanup_consolidation_plugin.md` phase (use with caution due to file operations), added `hdta_review_progress` and `hierarchical_task_checklist` templates.
- Version **v7.5**: Significant baseline restructuring, establishing core architecture, Contextual Keys (`KeyInfo`), Hierarchical Dependency Aggregation, enhanced `show-dependencies`, configurable embedding device, file exclusion patterns, improved caching & batch processing.

- 版本 **v7.7**: 重构核心提示词/插件,引入 `cleanup_consolidation_plugin.md` 阶段 (由于涉及文件操作,请谨慎使用),添加 `hdta_review_progress` 和 `hierarchical_task_checklist` 模板。
- 版本 **v7.5**: 重要的基线重构,建立核心架构、上下文键 (`KeyInfo`)、分层依赖聚合、增强的 `show-dependencies`、可配置的嵌入设备、文件排除模式、改进的缓存和批处理。

---

## System Requirements

## 系统要求

### Recommended (v8.0+)
- **VRAM**: 8GB+ (NVIDIA GPU) for optimal Qwen3-4B model performance
- **RAM**: 16GB+ for large projects
- **Disk**: 2GB+ for models and embeddings
- **Python**: 3.8+
- **Node.js**: 16+ (for mermaid-cli visualization)

### 推荐配置 (v8.0+)
- **VRAM**: 8GB+ (NVIDIA GPU) 以获得最佳的 Qwen3-4B 模型性能
- **RAM**: 16GB+ 用于大型项目
- **磁盘**: 2GB+ 用于模型和嵌入
- **Python**: 3.8+
- **Node.js**: 16+ (用于 mermaid-cli 可视化)

### Minimum
- **RAM**: 4GB (CPU-only mode with reduced batch sizes)
- **Disk**: 500MB+ (lightweight models)
- **Python**: 3.8+

*The system automatically adapts to available hardware.*

### 最低配置
- **RAM**: 4GB (仅 CPU 模式,批处理大小降低)
- **磁盘**: 500MB+ (轻量级模型)
- **Python**: 3.8+

*系统会自动适应可用的硬件。*

---

## Key Features

## 主要特性

- **Recursive Decomposition**: Breaks tasks into manageable subtasks, organized via directories and files for isolated context management.
- **递归分解**: 将任务分解为可管理的子任务,通过目录和文件组织,实现隔离的上下文管理。
- **Minimal Context Loading**: Loads only essential data, expanding via dependency trackers as needed.
- **最小上下文加载**: 仅加载必要数据,根据需要通过依赖跟踪器扩展。
- **Persistent State**: Uses the VS Code file system to store context, instructions, outputs, and dependencies. State integrity is rigorously maintained via a **Mandatory Update Protocol (MUP)** applied after actions and periodically during operation.
- **持久化状态**: 使用 VS Code 文件系统存储上下文、指令、输出和依赖。通过在操作后和运行期间定期应用的 **强制性更新协议 (MUP)** 严格维护状态完整性。
- **Modular Dependency System**: Fully modularized dependency tracking system.
- **模块化依赖系统**: 完全模块化的依赖跟踪系统。
- **Contextual Keys**: Introduces `KeyInfo` for context-rich keys, enabling more accurate and hierarchical dependency tracking.
- **上下文键**: 引入 `KeyInfo` 以实现上下文丰富的键,支持更准确和分层的依赖跟踪。
- **Hierarchical Dependency Aggregation**: Implements hierarchical rollup and foreign dependency aggregation for the main tracker, providing a more comprehensive view of project dependencies.
- **分层依赖聚合**: 为主跟踪器实现分层汇总和外部依赖聚合,提供更全面的项目依赖视图。
- **Enhanced Dependency Workflow**: A refined workflow simplifies dependency management.
    - `show-keys` identifies keys needing attention ('p', 's', 'S') within a specific tracker.
    - `show-dependencies` aggregates dependency details (inbound/outbound, paths) from *all* trackers for a specific key, eliminating manual tracker deciphering.
    - `add-dependency` resolves placeholder ('p') or suggested ('s', 'S') relationships identified via this process. **Crucially, when targeting a mini-tracker (`*_module.md`), `add-dependency` now allows specifying a `--target-key` that doesn't exist locally, provided the target key is valid globally (known from `analyze-project`). The system automatically adds the foreign key definition and updates the grid, enabling manual linking to external dependencies.**
      *   **Tip:** This is especially useful for manually linking relevant documentation files (e.g., requirements, design specs, API descriptions) to code files within a mini-tracker, even if the code file is incomplete or doesn't trigger an automatic suggestion. This provides the LLM with crucial context during code generation or modification tasks, guiding it towards the intended functionality described in the documentation (`doc_key < code_key`).
   - **Dependency Visualization (`visualize-dependencies`)**: **(NEW in v7.8)**
    - Generates Mermaid diagrams for project overview, module scope (internal + interface), or specific key focus.
    - Auto-generates overview/module diagrams via `analyze-project`.
    - **NEW in v7.90** Now generates .svg image files for diagram visualization if the mermaid-cli dependency is installed.
- **增强的依赖工作流**: 精简的工作流程简化了依赖管理。
    - `show-keys` 识别特定跟踪器中需要注意的键 ('p', 's', 'S')。
    - `show-dependencies` 聚合特定键来自 *所有* 跟踪器的依赖详细信息 (入站/出站、路径),消除手动解读跟踪器的需要。
    - `add-dependency` 解决通过此过程识别的占位符 ('p') 或建议 ('s', 'S') 关系。**关键是,当针对小型跟踪器 (`*_module.md`) 时,`add-dependency` 现在允许指定本地不存在的 `--target-key`,只要目标键在全局有效 (通过 `analyze-project` 已知)。系统会自动添加外部键定义并更新网格,实现与外部依赖的手动链接。**
      *   **提示:** 这对于将相关文档文件 (如需求、设计规范、API 描述) 手动链接到小型跟踪器中的代码文件特别有用,即使代码文件不完整或未触发自动建议。这为 LLM 在代码生成或修改任务期间提供了关键上下文,引导其实现文档中描述的预期功能 (`doc_key < code_key`)。
   - **依赖可视化 (`visualize-dependencies`)**: **(v7.8 新增)**
    - 为项目概览、模块范围 (内部 + 接口) 或特定键聚焦生成 Mermaid 图表。
    - 通过 `analyze-project` 自动生成概览/模块图表。
    - **v7.90 新增** 现在生成 .svg 图像文件以进行图表可视化 (如果安装了 mermaid-cli 依赖)。
- **Iterative Strategy Phase**: **(NEW in v7.8)**
    - Plans the project roadmap iteratively, focusing on one area (module/feature) at a time.
    - Explicitly integrates dependency analysis (textual + visual) into planning.
- **迭代策略阶段**: **(v7.8 新增)**
    - 迭代规划项目路线图,每次专注于一个区域 (模块/功能)。
    - 明确将依赖分析 (文本 + 可视化) 集成到规划中。
- **Refined HDTA Templates**: **(NEW in v7.8)**
    - Improved templates for Implementation Plans, Modules, and Tasks.
    - New template for Roadmap Summaries.
- **改进的 HDTA 模板**: **(v7.8 新增)**
    - 改进实施计划、模块和任务的模板。
    - 新增路线图摘要模板。
- **Configurable Embedding Device**: Allows users to configure the embedding device (`cpu`, `cuda`, `mps`) via `.clinerules.config.json` for optimized performance on different hardware. (Note: *the system does not yet install the requirements for cuda or mps automatically, please install the requirements manually or with the help of the LLM.*)
- **可配置的嵌入设备**: 允许用户通过 `.clinerules.config.json` 配置嵌入设备 (`cpu`, `cuda`, `mps`) 以在不同硬件上优化性能。(注意: *系统尚不会自动安装 cuda 或 mps 的要求,请手动安装或在 LLM 的帮助下安装。*)
- **File Exclusion Patterns**: Users can now define file exclusion patterns in `.clinerules.config.json` to customize project analysis.
- **文件排除模式**: 用户现在可以在 `.clinerules.config.json` 中定义文件排除模式以自定义项目分析。
- **Code Quality Analysis**: **(NEW in v8.0)**
    - **Report Generator**: A new tool (`report_generator.py`) that performs AST-based code quality analysis.
    - **Incomplete Code Detection**: Identifies `TODO`, `FIXME`, empty functions/classes, and `pass` statements using robust Tree-sitter parsing for Python, JavaScript, and TypeScript.
    - **Unused Item Detection**: Integrates with Pyright to report unused variables, imports, and functions.
    - **Actionable Reports**: Generates a detailed `code_analysis/issues_report.md` to guide cleanup efforts.
- **代码质量分析**: **(v8.0 新增)**
    - **报告生成器**: 一个新工具 (`report_generator.py`),执行基于 AST 的代码质量分析。
    - **不完整代码检测**: 使用强大的 Tree-sitter 解析识别 Python、JavaScript 和 TypeScript 中的 `TODO`、`FIXME`、空函数/类和 `pass` 语句。
    - **未使用项检测**: 与 Pyright 集成以报告未使用的变量、导入和函数。
    - **可操作报告**: 生成详细的 `code_analysis/issues_report.md` 以指导清理工作。
- **Caching and Batch Processing**: Significantly improves performance.
- **缓存和批处理**: 显著提高性能。
- **Modular Dependency Tracking**:
    - Utilizes main trackers (`module_relationship_tracker.md`, `doc_tracker.md`) and module-specific mini-trackers (`{module_name}_module.md`).
    - Mini-tracker files also serve as the HDTA Domain Module documentation for their respective modules.
    - Employs hierarchical keys and RLE compression for efficiency.
- **模块化依赖跟踪**:
    - 利用主跟踪器 (`module_relationship_tracker.md`, `doc_tracker.md`) 和特定于模块的小型跟踪器 (`{module_name}_module.md`)。
    - 小型跟踪器文件也作为各自模块的 HDTA 域模块文档。
    - 采用分层键和 RLE 压缩以提高效率。
- **Automated Operations**: System operations are now largely automated and condensed into single commands, streamlining workflows and reducing manual command execution.
- **自动化操作**: 系统操作现在已基本自动化并浓缩为单命令,简化工作流程并减少手动命令执行。
- **Phase-Based Workflow**: Operates in distinct phases: Set-up/Maintenance -> Strategy -> Execution -> Cleanup/Consolidation, controlled by `.clinerules`.
- **基于阶段的工作流**: 在不同的阶段运行: 设置/维护 -> 策略 -> 执行 -> 清理/合并,由 `.clinerules` 控制。
- **Chain-of-Thought Reasoning**: Ensures transparency with step-by-step reasoning and reflection.
- **思维链推理**: 通过逐步推理和反思确保透明度。

---

## Quickstart

## 快速入门

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/RPG-fan/Cline-Recursive-Chain-of-Thought-System-CRCT-.git
   cd Cline-Recursive-Chain-of-Thought-System-CRCT-
   ```

1. **克隆仓库**:
   ```bash
   git clone https://github.com/RPG-fan/Cline-Recursive-Chain-of-Thought-System-CRCT-.git
   cd Cline-Recursive-Chain-of-Thought-System-CRCT-
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   npm install  # For mermaid-cli visualization
   ```

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   npm install  # 用于 mermaid-cli 可视化
   ```

3. **Set Up Cline or RooCode Extension**:
   - Open the project in VS Code with the Cline or RooCode extension installed.
   - Copy `cline_docs/prompts/core_prompt(put this in Custom Instructions).md` into the Cline Custom Instructions field. (new process to be updated)

3. **设置 Cline 或 RooCode 扩展**:
   - 在安装了 Cline 或 RooCode 扩展的 VS Code 中打开项目。
   - 将 `cline_docs/prompts/core_prompt(put this in Custom Instructions).md` 复制到 Cline 自定义指令字段 (新流程待更新)。

4. **Start the System**:
   - Type `Start.` in the Cline input to initialize the system.
   - The LLM will bootstrap from `.clinerules`, creating missing files and guiding you through setup if needed.

4. **启动系统**:
   - 在 Cline 输入中键入 `Start.` 以初始化系统。
   - LLM 将从 `.clinerules` 引导,创建缺失的文件并在需要时指导您完成设置。

*Note*: The Cline extension's LLM automates most commands and updates to `cline_docs/`. Minimal user intervention is required (in theory!)

*注意*: Cline 扩展的 LLM 自动化大多数命令和对 `cline_docs/` 的更新。(理论上!) 需要最少的用户干预

---

## Project Structure

## 项目结构

```
Cline-Recursive-Chain-of-Thought-System-CRCT-/
│   .clinerules/
│   .clinerules.config.json       # Configuration for dependency system
│   .gitignore
│   CHANGELOG.md                  # Version history <NEW in v8.0>
│   INSTRUCTIONS.md
│   LICENSE
│   MIGRATION_v7.x_to_v8.0.md     # Upgrade guide <NEW in v8.0>
│   README.md
│   requirements.txt
│
├───cline_docs/                   # Operational memory
│   │  activeContext.md           # Current state and priorities
│   │  changelog.md               # Logs significant changes
│   │  userProfile.md             # User profile and preferences
│   │  progress.md                # High-level project checklist
│   │
│   ├──backups/                   # Backups of tracker files
│   ├──dependency_diagrams/       # Default location for auto-generated Mermaid diagrams <NEW>
│   ├──prompts/                   # System prompts and plugins
│   │    core_prompt.md           # Core system instructions
|   |    cleanup_consolidation_plugin.md <NEWer>
│   │    execution_plugin.md
│   │    setup_maintenance_plugin.md
│   │    strategy_plugin.md         <REVISED>
│   ├──templates/                 # Templates for HDTA documents
│   │    hdta_review_progress_template.md <NEWer>
│   │    hierarchical_task_checklist_template.md <NEWer>
│   │    implementation_plan_template.md <REVISED>
│   │    module_template.md         <Minor Update>
│   │    roadmap_summary_template.md  <NEW>
│   │    system_manifest_template.md
│   │    task_template.md           <Minor Update>
│
├───cline_utils/                  # Utility scripts
│   └─dependency_system/
│     │ dependency_processor.py   # Dependency management script <REVISED>
│     ├──analysis/                # Analysis modules <MAJOR UPDATES in v8.0>
│     │    dependency_analyzer.py   <2x growth>
│     │    dependency_suggester.py  <1.9x growth>
│     │    embedding_manager.py     <3.4x growth>
│     │    project_analyzer.py      <1.7x growth>
│     │    reranker_history_tracker.py <NEW>
│     │    runtime_inspector.py     <NEW>
│     ├──core/                    # Core modules <REVISED key_manager.py>
│     │    exceptions_enhanced.py  <NEW - replaces exceptions.py>
│     ├──io/                      # IO modules
│     └──utils/                   # Utility modules
│          batch_processor.py      <Enhanced with PhaseTracker>
│          cache_manager.py        <2x growth - compression, policies>
│          config_manager.py       <2x growth - extensive new config>
│          phase_tracker.py        <NEW - progress bars>
│          resource_validator.py   <NEW - system checks>
│          symbol_map_merger.py    <NEW - runtime+AST merge>
│          visualize_dependencies.py <NEW>
│
├───docs/                         # Project documentation
├───models/                       # AI models (auto-downloaded) <NEW>
└───src/                          # Source code root

```
*(Added/Updated relevant files/dirs)*

*(添加/更新了相关文件/目录)*

---

## Current Status & Future Plans

## 当前状态和未来计划

- **v8.0**: 🚀 **Major architecture evolution** - Symbol Essence Strings, Qwen3 reranker, hardware-adaptive models, runtime symbol inspection, enhanced UX with PhaseTracker. See [CHANGELOG.md](CHANGELOG.md) for complete details.
- **v7.8**: Focus on **visual comprehension and planning robustness**. Introduced Mermaid dependency diagrams (`visualize-dependencies`, auto-generation via `analyze-project`). Overhauled the Strategy phase (`strategy_plugin.md`) for iterative, area-based roadmap planning, explicitly using visualizations. Refined HDTA templates, including a new `roadmap_summary_template.md`.
- **v7.7**: Introduced `cleanup_consolidation` phase, added planning/review tracker templates.
- **v7.5**: Foundational restructure: Contextual Keys, Hierarchical Aggregation, `show-dependencies`, configuration enhancements, performance improvements (cache/batch).

- **v8.0**: 🚀 **主要架构演进** - 符号本质字符串、Qwen3 重排序器、硬件自适应模型、运行时符号检查、使用 PhaseTracker 增强用户体验。有关完整详细信息,请参阅 [CHANGELOG.md](CHANGELOG.md)。
- **v7.8**: 专注于 **视觉理解和规划稳健性**。引入 Mermaid 依赖图表 (`visualize-dependencies`,通过 `analyze-project` 自动生成)。彻底改革策略阶段 (`strategy_plugin.md`) 以实现迭代、基于区域的路线图规划,明确使用可视化。完善 HDTA 模板,包括新的 `roadmap_summary_template.md`。
- **v7.7**: 引入 `cleanup_consolidation` 阶段,添加规划/审查跟踪器模板。
- **v7.5**: 基础重构:上下文键、分层聚合、`show-dependencies`、配置增强、性能改进 (缓存/批处理)。

**Future Focus**: Continue refining performance, usability, and robustness. v8.x series will focus on optimizing the new reranking and SES systems based on real-world usage. Future versions may include MCP-based tool use and transition from filesystem to database-focused operations.

**未来重点**: 继续改进性能、可用性和稳健性。v8.x 系列将专注于根据实际使用情况优化新的重排序和 SES 系统。未来版本可能包括基于 MCP 的工具使用以及从文件系统到数据库操作的转换。

Feedback is welcome! Please report bugs or suggestions via GitHub Issues.

欢迎反馈!请通过 GitHub Issues 报告错误或提出建议。

---

## Getting Started (Optional - Existing Projects)

## 入门指南 (可选 - 现有项目)

To test on an existing project:
1. Copy your project into `src/`.
2. Use these prompts to kickstart the LLM:
   - `Perform initial setup and populate dependency trackers.`
   - `Review the current state and suggest next steps.`

要在现有项目上进行测试:
1. 将项目复制到 `src/`。
2. 使用这些提示词启动 LLM:
   - `执行初始设置并填充依赖跟踪器。`
   - `审查当前状态并建议下一步操作。`

The system will analyze your codebase, initialize trackers, and guide you forward.

系统将分析您的代码库,初始化跟踪器,并引导您前进。

---

## Thanks!

## 致谢!

A big Thanks to https://github.com/biaomingzhong for providing detailed instructions that were integrated into the core prompt and plugins! (PR #25)

非常感谢 https://github.com/biaomingzhong 提供的详细说明,这些说明已集成到核心提示词和插件中! (PR #25)

This is a labor of love to make Cline projects more manageable. I'd love to hear your thoughts—try it out and let me know what works (or doesn't)!

这是一项使 Cline 项目更易于管理的心血之作。我很想听听您的想法 - 试试看,让我知道哪些有效 (或无效)!
