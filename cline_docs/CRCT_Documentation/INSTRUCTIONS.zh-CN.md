# INSTRUCTIONS.md

## Cline递归思维链系统（CRCT）- v7.5 使用说明

本说明提供了设置和使用Cline递归思维链系统（CRCT）v7.5的指南。该系统旨在通过为复杂项目提供强大的上下文和依赖管理来增强VS Code中的Cline扩展。

---

## 前置要求

- **VS Code**: 已安装Cline扩展。
- **Python**: 3.8+，带有`pip`。
- **Git**: 用于克隆仓库。

---

## 步骤1：设置

1. **克隆仓库**:
   ```bash
   git clone https://github.com/RPG-fan/Cline-Recursive-Chain-of-Thought-System-CRCT-.git
   cd Cline-Recursive-Chain-of-Thought-System-CRCT-
   ```

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```
   *包括`sentence-transformers`用于嵌入。*

3. **在VS Code中打开**:
   - 启动VS Code并打开`cline/`文件夹。

4. **配置Cline**:
   - 打开Cline扩展设置。
   - 将`cline_docs/prompts/core_prompt(put this in Custom Instructions).md`的内容粘贴到"自定义指令（Custom Instructions）"字段中。

---

## 步骤2：初始化系统（v7.5+）

1. **启动系统**:
   - 在Cline输入中，输入`Start.`并运行。
   - LLM将执行以下初始化步骤：
     - 读取`.clinerules`以确定当前阶段。
     - 加载相应的阶段插件（例如`Set-up/Maintenance`）。
     - 初始化`cline_docs/`中的核心文件，包括跟踪器文件和上下文文档。

2. **遵循提示**:
   - LLM可能会请求输入（例如，为`projectbrief.md`提供项目目标）。
   - 提供简洁的答案以帮助其填充文件。

3. **验证设置**:
   - 检查`cline_docs/`中的新文件（例如`dependency_tracker.md`）。
   - 确保`.clinerules`中的`[CODE_ROOT_DIRECTORIES]`列出了`src/`（如有需要手动编辑）。

---

## 步骤3：填充依赖跟踪器

1. **运行初始设置**:
   - 输入: `Perform initial setup and populate dependency trackers.`（执行初始设置并填充依赖跟踪器。）
   - LLM将：
     - 识别代码根目录（例如`src/`）。
     - 识别文档目录（例如`docs/`）
     - 使用`dependency_processor.py`生成`module_relationship_tracker.md`、`doc_tracker.md`和所有微跟踪器。
     - 建议并验证模块依赖关系。

2. **验证依赖关系（如果提示）**:
   - LLM将使用`show-dependencies`命令检查和验证建议的依赖关系，根据需要确认或调整字符（`<`、`>`、`x`等）。
   - 建议观察LLM确保其添加或更改的任何依赖关系使用的逻辑合理。

---

## 步骤4：规划和执行

1. **进入策略阶段**:
   - 一旦跟踪器填充完成，LLM将过渡到`Strategy`（检查`.clinerules`）。
   - 输入: `Plan the next steps for my project.`（为我的项目规划下一步。）
   - 输出: 在`strategy_tasks/`或`src/`中创建新的指令文件。

2. **执行任务**:
   - 输入: `Execute the planned tasks.`（执行计划的任务。）
   - LLM将遵循指令文件，更新文件并应用MUP。

---

## 提示

- **监控`activeContext.md`**: 跟踪当前状态和优先级。
- **检查`.clinerules`**: 显示当前阶段和下一步操作。
- **调试**: 如果卡住，尝试`Review the current state and suggest next steps.`（审查当前状态并建议下一步。）

---

## 使用CRCT v7.5

1. **理解阶段**:
   - CRCT在三个不同阶段运行，由`.clinerules`文件控制：
     - **设置/维护（Set-up/Maintenance）**: 用于初始设置、项目配置和系统操作文件及依赖跟踪器的持续维护。此阶段的关键操作包括识别代码和文档根目录，以及在初始设置和重大代码库变更后运行`analyze-project`。
     - **策略（Strategy）**: 专注于规划、任务分解和创建详细指令的阶段。此阶段利用设置/维护阶段收集的依赖信息来指导战略规划。
     - **执行（Execution）**: 用于执行任务、修改代码和实施计划策略。此阶段依赖于策略阶段开发的上下文和计划。
   - `.clinerules`中的`current_phase`决定了活动的操作模式和系统加载的插件。
   *注意：如果用于大型现有项目，初始设置阶段可能需要相当长的时间，因为LLM需要为所有文件和文件夹创建必要的支持文档，并使用项目特定的详细信息填充它们。建议将工作负载划分为多个任务，集中于一次创建/填充一个系统中的文档。执行验证以确认所有详细信息都得到充分覆盖。*

  **阶段转换清单：**

  在阶段之间转换前，请确保完成以下清单：

  - **设置/维护 → 策略**:
    - 确认`cline_docs/`中的`doc_tracker.md`和`module_relationship_tracker.md`没有'p'占位符（所有依赖关系已验证）。
    - 验证`.clinerules`中的`[CODE_ROOT_DIRECTORIES]`和`[DOC_DIRECTORIES]`部分已正确填充并列出所有相关目录。

  - **策略 → 执行**:
    - 确保在策略阶段创建的所有指令文件（例如在`strategy_tasks/`或`src/`中）包含完整的"步骤（Steps）"和"依赖关系（Dependencies）"部分，为执行阶段提供清晰的指导。

  完成这些清单有助于确保CRCT阶段之间的平稳有效转换，维护系统完整性和任务连续性。


2. **关键CRCT操作**:

   - **项目分析**:
     - LLM将使用`analyze-project`命令完全分析项目，生成**上下文键**，更新依赖跟踪器（主跟踪器、文档跟踪器和微跟踪器），并生成嵌入。此命令是维护最新依赖信息的核心，应在设置/维护阶段和重大代码更改后运行。
   - **依赖检查**:
     - LLM将使用`show-dependencies --key <key>`命令检查特定**上下文键**的依赖关系。将`<key>`替换为所需的文件或模块键。此命令聚合所有跟踪器的依赖信息，并提供入站和出站依赖关系的全面视图，显著简化依赖分析。
   - **手动依赖管理**:
     - LLM将使用`add-dependency --tracker <tracker_file> --source-key <key> --target-key <key1> [<key2>...] --dep-type <char>`在跟踪器文件中手动设置依赖关系。这对于纠正或验证建议的依赖关系以及标记已验证的关系很有用。**使用此命令时请确保使用上下文键。**
       *（注意：--target-key接受多个键。指定的`--dep-type`应用于*所有*目标。）*
       *（建议：为清晰起见，一次最多指定五个目标键。）*
     - LLM将使用`remove-key --tracker <tracker_file> --key <key>`从跟踪器文件中删除键及其关联数据，通常在文件被删除或重构时使用。**使用此命令时请确保使用上下文键。**

   **手动管理的依赖字符：**

   使用`add-dependency`手动管理依赖关系时，需要使用字符代码指定依赖类型。以下是可用字符的详细说明，如`.clinerules`的`[Character_Definitions]`部分所定义：

   - `<`: 行依赖于列（源依赖于目标）。
   - `>`: 列依赖于行（目标依赖于源）。
   - `x`: 相互依赖（彼此依赖）。
   - `d`: 文档依赖（源记录目标）。
   - `o`: 自依赖（仅用于跟踪器网格的对角线，表示文件对自身的依赖 - 通常用于结构元素）。
   - `n`: 已验证无依赖（明确标记不存在依赖）。
   - `p`: 占位符（表示未验证或建议的依赖，需要手动审查）。
   - `s`: 语义依赖（弱 - 相似度分数在0.05到0.06之间）。
   - `S`: 语义依赖（强 - 相似度分数0.07或更高）。

   **示例场景：**

   - 如果`moduleA.py`导入`moduleB.py`，您将使用`>`表示`moduleB.py`（目标/列）依赖于`moduleA.py`（源/行）。
   - 如果`docs_about_moduleA.md`记录`moduleA.py`，使用`d`。
   - 如果您已手动验证两个模块之间没有依赖关系，使用`n`明确标记，防止未来建议。

   正确使用这些字符可确保CRCT系统内准确且有意义的依赖跟踪。记住对所有手动依赖管理操作使用上下文键。

  **理解上下文键：**

  CRCT v7.5使用分层键系统（`KeyInfo`）来表示文件和目录。键遵循`Tier` + `DirLetter` + `[SubdirLetter]` + `[FileNumber]`的模式（例如`1A`、`1Aa`、`1Aa1`）。

  - **层级（Tier）**: 初始数字表示嵌套级别。顶级根是层级1。
  - **目录字母（DirLetter）**: 大写字母（'A'、'B'、...）标识定义根内的顶级目录。
  - **子目录字母（SubdirLetter）**: 小写字母（'a'、'b'、...）标识目录内的子目录。
  - **文件编号（FileNumber）**: 数字标识目录内的文件。

  **层级提升（Tier Promotion）**: 为了在深度嵌套的项目中保持键的可管理性，CRCT使用"层级提升"。当*已由子目录键表示*的目录（例如`1Ba`）包含需要键的更深层子目录时，这些子子目录将开始*新层级*。例如，`1Ba`内的目录可能获得键`2Ca`（层级2，提升的目录'C'，子目录'a'），而不是`1Baa`。这防止了过长的键。

   **理解依赖跟踪器：**

   CRCT使用三种类型的跟踪器文件来管理依赖关系：

   - **`module_relationship_tracker.md`（主跟踪器）**: 位于`cline_docs/`，此跟踪器提供*模块之间*依赖关系的高级视图。模块通常对应于`.clinerules`中`[CODE_ROOT_DIRECTORIES]`定义的顶级目录。此处显示的依赖关系是从低级跟踪器*聚合*的；如果`moduleA`中的文件依赖于`moduleB`中的文件，此依赖关系会"汇总"并在此主跟踪器中表示为从`moduleA`到`moduleB`的依赖关系。
   - **`doc_tracker.md`**: 位于`cline_docs/`，跟踪`.clinerules`中`[DOC_DIRECTORIES]`指定目录内找到的文档文件之间的依赖关系。
   - **微跟踪器（`{module_name}_module.md`）**: 位于每个模块目录（如`[CODE_ROOT_DIRECTORIES]`中定义），这些文件跟踪*该特定模块内文件之间*的依赖关系，以及从内部文件到*外部*文件（模块外或文档根中的文件）的依赖关系。跟踪器数据嵌入在模块文档文件的`---mini_tracker_start---`和`---mini_tracker_end---`标记之间。

   **建议优先级**: 当不同分析方法（例如显式导入 vs. 语义相似性）对同一两个文件之间的依赖关系提出冲突建议时，CRCT使用优先级系统来决定记录哪个依赖字符（`<`、`>`、`x`、`d`、`S`、`s`、`p`）。近似优先级顺序（从高到低）为：`x`（相互）、`<`/`>`（直接结构/导入）、`d`（文档链接）、`S`（强语义）、`s`（弱语义）、`n`/`p`/`o`（无/占位符/自身）。显式依赖通常会覆盖语义依赖。

3.  **强制更新协议（MUP）**:
    - CRCT采用强制更新协议（MUP）以确保系统状态一致性。LLM将定期（每5轮）执行完整的MUP，以更新`activeContext.md`、`changelog.md`和`.clinerules`，并清理已完成的任务。**MUP对于维护系统完整性至关重要，不应跳过。**
    - 如果LLM在合理的轮数内未执行此步骤，请提示其遵循MUP协议。记住上下文窗口是有限的，随着上下文窗口增长，LLM很快就会忘记他们做过和没做过的事情。*对LLM的幻觉和错误步骤要非常警惕，特别是在上下文大小超过100k时*

4. **配置**:
   - **`.clinerules.config.json`**: 在此文件中配置系统设置。
     - `embedding_device`: 设置嵌入设备（`cpu`、`cuda`、`mps`）以根据您的硬件优化性能。
     - `excluded_file_patterns`: 定义文件排除模式（glob模式）以自定义项目分析并从依赖跟踪中排除特定文件或目录。
   - *注意：其他设置如特定路径排除（`excluded_paths`）和系统目录位置（`memory_dir`、`embeddings_dir`、`backups_dir`等）也可在`.clinerules.config.json`中配置。有关详细信息，请参阅文件或默认值。*
   - **`.clinerules`**: 直接在`.clinerules`文件中管理核心系统设置。
     - `current_phase`: 设置CRCT的当前操作阶段。
     - `[CODE_ROOT_DIRECTORIES]`: 定义被视为项目分析代码根的目录。**修改此部分以指定包含应分析依赖关系的源代码的目录。**
     - `[DOC_DIRECTORIES]`: 定义被视为文档根的目录。**修改此部分以指定包含应跟踪的项目文档的目录。**
     - `[LEARNING_JOURNAL]`: 查看学习日志以获取有关系统操作和最佳实践的见解。

---

## 分层设计令牌架构（HDTA）

CRCT利用分层设计令牌架构（HDTA）来组织项目文档和规划。HDTA提供了结构化的方法来管理系统级信息，分解为四层文档：

1. **系统清单（`system_manifest.md` 在 `cline_docs/`）**: 提供整个项目的顶级概览、其目标、架构和关键组件。此文档在设置/维护阶段创建，作为项目的中心参考点。

2. **领域模块（`{module_name}_module.md` 在 `cline_docs/`）**: 描述项目内的主要功能区域或模块。每个模块文档详细说明其目的、功能以及与其他模块的关系。这些也在设置/维护期间创建。

3. **实施计划（模块内的文件）**: 包含模块内特定实施的详细计划。这些文档概述了实施特定功能或功能的步骤、依赖关系和考虑因素。实施计划通常在策略阶段创建。

4. **任务指令（`{task_name}.md` 在 `strategy_tasks/` 或 `src/`）**: 为单个任务提供程序化指导。任务指令将复杂任务分解为更小、可管理的步骤，确保清晰和高效执行。任务指令在策略阶段创建以指导执行阶段。

HDTA有助于维护清晰和有组织的项目文档结构，促进CRCT内复杂项目的更好理解、协作和管理。HDTA文档的模板位于`cline_docs/templates/`。

---

## 故障排除

- **初始化问题**: 如果系统初始化失败，请确保核心提示已正确加载到Cline扩展中，并且满足所有前置要求。**仔细检查您是否已将`cline_docs/prompts/core_prompt(put this in Custom Instructions).md`的内容复制到Cline自定义指令字段。**
- **依赖跟踪问题**: 如果遇到依赖跟踪问题，使用`analyze-project`刷新跟踪器和嵌入。检查`.clinerules`以确保代码和文档根的正确配置。**确保`.clinerules`中的`[CODE_ROOT_DIRECTORIES]`和`[DOC_DIRECTORIES]`部分已正确填充。**
  - 您可能需要手动删除cline_docs中的module_relationship_tracker和doc_tracker。
  - 对于微跟踪器，我建议手动删除微跟踪器开始和结束标记之间的内容。*重要：不要删除微跟踪器开始和结束标记，这将导致整个文件内容被覆盖，丢失先前记录的任何信息。*
- **命令错误**: 确保命令拼写正确并在适当的阶段使用。有关语法和用法，请参阅命令文档。**特别注意每个命令所需的参数，特别是在使用`show-dependencies`、`add-dependency`和`remove-key`时。**
- **键生成限制（`KeyGenerationError`）**: 键系统在需要"层级提升"之前支持任何单个目录内最多26个直接子目录（'a'到'z'）。如果您的目录结构超过此限制（例如27+个需要键的直接子文件夹），`analyze-project`命令可能会失败并显示`KeyGenerationError`。要解决此问题，请重新构建目录或将一些有问题的子目录路径添加到`.clinerules.config.json`中的`"excluded_paths"`列表。

---

## 高级用法与故障排除

- **语义分析细节**: 语义相似性分析（导致's'或'S'依赖）依赖于`sentence-transformers`库（默认情况下特别是`"sentence-transformers/all-mpnet-base-v2"`模型）。嵌入作为`.npy`文件存储在`.clinerules.config.json`中`embeddings_dir`配置的目录内的镜像结构中（默认：`cline_utils/dependency_system/analysis/embeddings/`）。系统通过对照`metadata.json`文件检查文件修改时间（mtime）来避免为未更改的文件重新生成嵌入。
- **跟踪器备份**: 在更新期间（例如通过`analyze-project`）覆盖跟踪器文件（`module_relationship_tracker.md`、`doc_tracker.md`、`*_module.md`）之前，系统会自动在`backups_dir`配置的目录（默认：`cline_docs/backups/`）中创建带时间戳的备份。每个跟踪器保留最近两个备份。
- **批处理调整**: 系统对文件分析（`analyze-project`）等任务使用并行批处理。虽然它尝试自适应调整，但性能可能会有所不同。对于非常大的项目或特定硬件，如果分析似乎缓慢或使用过多资源，您可以通过在调用相关命令时为`BatchProcessor`建议`max_workers`（线程数）或`batch_size`的具体值来指示LLM尝试特定参数。
- **其他实用命令**: `dependency_processor.py`脚本提供了超出主工作流命令的几个实用命令。这些可能对高级检查或手动干预有用（如有需要请让LLM使用它们）：
    - `python -m cline_utils.dependency_system.dependency_processor analyze-file <file_path> [--output <json_path>]`: 分析单个文件并将详细发现（导入、调用等）输出为JSON。
    - `python -m cline_utils.dependency_system.dependency_processor merge-trackers <primary_path> <secondary_path> [--output <out_path>]`: 合并两个跟踪器文件，主跟踪器优先。用于合并跟踪器数据，虽然通常自动管理。
    - `python -m cline_utils.dependency_system.dependency_processor export-tracker <tracker_path> [--format <json|csv|dot>] [--output <out_path>]`: 将跟踪器数据导出为不同格式以进行外部分析或可视化（例如用于Graphviz的DOT格式）。
    - `python -m cline_utils.dependency_system.dependency_processor update-config <key_path> <value>`: 更新`.clinerules.config.json`中的特定设置（例如`python -m cline_utils.dependency_system.dependency_processor update-config thresholds.code_similarity 0.75`）。
    - `python -m cline_utils.dependency_system.dependency_processor reset-config`: 将`.clinerules.config.json`重置为默认设置。
    - `python -m cline_utils.dependency_system.dependency_processor clear-caches`: 清除依赖系统使用的内部缓存（嵌入元数据、分析结果等）。如果您怀疑陈旧的缓存数据导致问题，这很有用。

---

## 注意事项

- CRCT v7.5代表了系统的重大重构和稳定化。虽然计划进行持续的改进和优化，但v7.5被认为是一个稳定且功能丰富的版本。
- LLM自动化大多数依赖管理和系统命令（例如`analyze-project`、`show-dependencies`等）。
- 对于自定义项目，请确保在初始化系统之前填充`src/`和`docs/`目录。
  - `src/`和`docs/`是用于快速启动的默认目录。
  - 系统支持自定义代码和文档目录结构，因此如果您感觉舒适，请随意创建自己的目录。
  （如果出现任何问题，请告诉我，我将尽力提供帮助或修改系统以支持您独特的项目结构）

## 获取帮助

如需进一步的帮助、问题或错误报告，请参阅项目的GitHub仓库和问题跟踪器。

---

感谢您使用CRCT v7.5！希望它能增强您的Cline项目工作流程。
