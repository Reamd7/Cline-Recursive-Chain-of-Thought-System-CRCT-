# INSTRUCTIONS.md

## Cline Recursive Chain-of-Thought System (CRCT) - v7.5 Instructions

## Cline 递归思维链系统 (CRCT) - v7.5 指南 | Cline Recursive Chain-of-Thought System (CRCT) - v7.5 Instructions

These instructions provide a guide to setting up and using the Cline Recursive Chain-of-Thought System (CRCT) v7.5. This system is designed to enhance the Cline extension in VS Code by providing robust context and dependency management for complex projects.

这些指令提供了设置和使用 Cline 递归思维链系统 (CRCT) v7.5 的指南。该系统旨在通过为复杂项目提供强大的上下文和依赖管理来增强 VS Code 中的 Cline 扩展。

---

## Prerequisites

## 前置要求 | Prerequisites

- **VS Code**: Installed with the Cline extension.
- **VS Code**: 已安装,并安装了 Cline 扩展。 | Installed with the Cline extension.

- **Python**: 3.8+ with `pip`.
- **Python**: 3.8 或更高版本,并已安装 `pip`。 | 3.8+ with `pip`.

- **Git**: To clone the repo.
- **Git**: 用于克隆代码仓库。 | To clone the repo.

---

## Step 1: Setup

## 步骤 1: 设置 | Step 1: Setup

1. **Clone the Repository**:
1. **克隆代码仓库**: | Clone the Repository:

   ```bash
   git clone https://github.com/RPG-fan/Cline-Recursive-Chain-of-Thought-System-CRCT-.git
   cd Cline-Recursive-Chain-of-Thought-System-CRCT-
   ```

   克隆仓库并进入项目目录。 | Clone the repository and enter the project directory.

2. **Install Dependencies**:
2. **安装依赖项**: | Install Dependencies:

   ```bash
   pip install -r requirements.txt
   ```
   *Includes `sentence-transformers` for embeddings.*
   *包含用于嵌入 (embeddings) 的 `sentence-transformers` 库。* | Includes `sentence-transformers` for embeddings.

3. **Open in VS Code**:
3. **在 VS Code 中打开**: | Open in VS Code:

   - Launch VS Code and open the `cline/` folder.
   - 启动 VS Code 并打开 `cline/` 文件夹。 | Launch VS Code and open the `cline/` folder.

4. **Configure Cline**:
4. **配置 Cline**: | Configure Cline:

   - Open the Cline extension settings.
   - 打开 Cline 扩展设置。 | Open the Cline extension settings.

   - Paste the contents of `cline_docs/prompts/core_prompt(put this in Custom Instructions).md` into the "Custom Instructions" field.
   - 将 `cline_docs/prompts/core_prompt(put this in Custom Instructions).md` 的内容粘贴到"自定义指令"字段中。 | Paste the contents of `cline_docs/prompts/core_prompt(put this in Custom Instructions).md` into the "Custom Instructions" field.

---

## Step 2: Initialize the System (v7.5+)

## 步骤 2: 初始化系统 (v7.5+) | Step 2: Initialize the System (v7.5+)

1. **Start the System**:
1. **启动系统**: | Start the System:

   - In the Cline input, type `Start.` and run it.
   - 在 Cline 输入框中输入 `Start.` 并运行。 | In the Cline input, type `Start.` and run it.

   - The LLM will perform these initialization steps:
   - LLM 将执行以下初始化步骤: | The LLM will perform these initialization steps:

     - Read `.clinerules` to determine the current phase.
     - 读取 `.clinerules` 以确定当前阶段。 | Read `.clinerules` to determine the current phase.

     - Load the corresponding phase plugin (e.g., `Set-up/Maintenance`).
     - 加载相应的阶段插件 (例如 `Set-up/Maintenance`)。 | Load the corresponding phase plugin (e.g., `Set-up/Maintenance`).

     - Initialize core files in `cline_docs/`, including tracker files and context documents.
     - 初始化 `cline_docs/` 中的核心文件,包括跟踪器文件和上下文文档。 | Initialize core files in `cline_docs/`, including tracker files and context documents.

2. **Follow Prompts**:
2. **遵循提示**: | Follow Prompts:

   - The LLM may ask for input (e.g., project goals for `projectbrief.md`).
   - LLM 可能会要求输入 (例如 `projectbrief.md` 的项目目标)。 | The LLM may ask for input (e.g., project goals for `projectbrief.md`).

   - Provide concise answers to help it populate files.
   - 提供简洁的答案以帮助它填充文件。 | Provide concise answers to help it populate files.

3. **Verify Setup**:
3. **验证设置**: | Verify Setup:

   - Check `cline_docs/` for new files (e.g., `dependency_tracker.md`).
   - 检查 `cline_docs/` 中的新文件 (例如 `dependency_tracker.md`)。 | Check `cline_docs/` for new files (e.g., `dependency_tracker.md`).

   - Ensure `[CODE_ROOT_DIRECTORIES]` in `.clinerules` lists `src/` (edit manually if needed).
   - 确保 `.clinerules` 中的 `[CODE_ROOT_DIRECTORIES]` 列出了 `src/` (如需要可手动编辑)。 | Ensure `[CODE_ROOT_DIRECTORIES]` in `.clinerules` lists `src/` (edit manually if needed).

---

## Step 3: Populate Dependency Trackers

## 步骤 3: 填充依赖跟踪器 | Step 3: Populate Dependency Trackers

1. **Run Initial Setup**:
1. **运行初始设置**: | Run Initial Setup:

   - Input: `Perform initial setup and populate dependency trackers.`
   - 输入: `Perform initial setup and populate dependency trackers.` | Input: `Perform initial setup and populate dependency trackers.`

   - The LLM will:
   - LLM 将: | The LLM will:

     - Identify code root directories (e.g., `src/`).
     - 识别代码根目录 (例如 `src/`)。 | Identify code root directories (e.g., `src/`).

     - Identify documentation directories (e.g., `docs/`)
     - 识别文档目录 (例如 `docs/`) | Identify documentation directories (e.g., `docs/`)

     - Generate `module_relationship_tracker.md`, `doc_tracker.md`, and all mini-trackers using `dependency_processor.py`.
     - 使用 `dependency_processor.py` 生成 `module_relationship_tracker.md`、`doc_tracker.md` 和所有迷你跟踪器。 | Generate `module_relationship_tracker.md`, `doc_tracker.md`, and all mini-trackers using `dependency_processor.py`.

     - Suggest and validate module dependencies.
     - 建议并验证模块依赖关系。 | Suggest and validate module dependencies.

2. **Validate Dependencies (if prompted)**:
2. **验证依赖关系 (如果提示)**: | Validate Dependencies (if prompted):

   - The LLM will use the `show-dependencies` command to inspect and validate suggested dependencies, confirming or adjusting characters (`<`, `>`, `x`, etc.) as needed.
   - LLM 将使用 `show-dependencies` 命令来检查和验证建议的依赖关系,根据需要确认或调整字符 (`<`, `>`, `x` 等)。 | The LLM will use the `show-dependencies` command to inspect and validate suggested dependencies, confirming or adjusting characters (`<`, `>`, `x`, etc.) as needed.

   - It is recommended to watch the LLM to ensure the logic it is using makes sense for any dependencies it adds or changes.
   - 建议观察 LLM,以确保其使用的逻辑对于添加或更改的任何依赖关系都是合理的。 | It is recommended to watch the LLM to ensure the logic it is using makes sense for any dependencies it adds or changes.

---

## Step 4: Plan and Execute

## 步骤 4: 规划和执行 | Step 4: Plan and Execute

1. **Enter Strategy Phase**:
1. **进入策略阶段**: | Enter Strategy Phase:

   - Once trackers are populated, the LLM will transition to `Strategy` (check `.clinerules`).
   - 一旦跟踪器填充完成,LLM 将转换到 `Strategy` 阶段 (检查 `.clinerules`)。 | Once trackers are populated, the LLM will transition to `Strategy` (check `.clinerules`).

   - Input: `Plan the next steps for my project.`
   - 输入: `Plan the next steps for my project.` | Input: `Plan the next steps for my project.`

   - Output: New instruction files in `strategy_tasks/` or `src/`.
   - 输出: `strategy_tasks/` 或 `src/` 中的新指令文件。 | Output: New instruction files in `strategy_tasks/` or `src/`.

2. **Execute Tasks**:
2. **执行任务**: | Execute Tasks:

   - Input: `Execute the planned tasks.`
   - 输入: `Execute the planned tasks.` | Input: `Execute the planned tasks.`

   - The LLM will follow instruction files, update files, and apply the MUP.
   - LLM 将遵循指令文件,更新文件并应用 MUP。 | The LLM will follow instruction files, update files, and apply the MUP.

---

## Tips

## 提示 | Tips

- **Monitor `activeContext.md`**: Tracks current state and priorities.
- **监控 `activeContext.md`**: 跟踪当前状态和优先级。 | Tracks current state and priorities.

- **Check `.clinerules`**: Shows the current phase and next action.
- **检查 `.clinerules`**: 显示当前阶段和下一步操作。 | Shows the current phase and next action.

- **Debugging**: If stuck, try `Review the current state and suggest next steps.`
- **调试**: 如果卡住,请尝试 `Review the current state and suggest next steps.` | If stuck, try `Review the current state and suggest next steps.`

---

## Using CRCT v7.5

## 使用 CRCT v7.5 | Using CRCT v7.5

1. **Understanding Phases**:
1. **理解阶段**: | Understanding Phases:

   - CRCT operates in three distinct phases, controlled by the `.clinerules` file:
   - CRCT 在三个不同的阶段运行,由 `.clinerules` 文件控制: | CRCT operates in three distinct phases, controlled by the `.clinerules` file:

     - **Set-up/Maintenance**: For initial setup, project configuration, and ongoing maintenance of the system's operational files and dependency trackers. Key operations in this phase include identifying code and documentation roots, and running `analyze-project` for initial setup and after significant codebase changes.
     - **设置/维护 (Set-up/Maintenance)**: 用于初始设置、项目配置以及系统操作文件和依赖跟踪器的持续维护。此阶段的关键操作包括识别代码和文档根目录,以及在初始设置和重大代码库更改后运行 `analyze-project`。 | For initial setup, project configuration, and ongoing maintenance of the system's operational files and dependency trackers. Key operations in this phase include identifying code and documentation roots, and running `analyze-project` for initial setup and after significant codebase changes.

     - **Strategy**: Phase focused on planning, task decomposition, and creating detailed instructions. This phase leverages dependency information gathered in the Set-up/Maintenance phase to inform strategic planning.
     - **策略 (Strategy)**: 专注于规划、任务分解和创建详细指令的阶段。此阶段利用在设置/维护阶段收集的依赖信息来指导战略规划。 | Phase focused on planning, task decomposition, and creating detailed instructions. This phase leverages dependency information gathered in the Set-up/Maintenance phase to inform strategic planning.

     - **Execution**: For carrying out tasks, modifying code, and implementing planned strategies. This phase relies on the context and plans developed in the Strategy phase.
     - **执行 (Execution)**: 用于执行任务、修改代码和实施计划策略的阶段。此阶段依赖于策略阶段开发的上下文和计划。 | For carrying out tasks, modifying code, and implementing planned strategies. This phase relies on the context and plans developed in the Strategy phase.

   - The `current_phase` in `.clinerules` dictates the active operational mode and the plugin loaded by the system.
   - `.clinerules` 中的 `current_phase` 决定了当前的操作模式和系统加载的插件。 | The `current_phase` in `.clinerules` dictates the active operational mode and the plugin loaded by the system.

   *Note: The initial Set-up phase will likely take quite some time if used with a large pre-existing project, as the LLM will need to create the necessary support documentation for all files and folders and populate them with your project specific details. It is suggested that you divide the workload among multiple tasks that concentrate on creating/populating the documentation in a single system in a time. Perform a validation pass to confirm all details are sufficiently covered.*
   *注意: 如果在大型现有项目上使用,初始设置阶段可能需要相当长的时间,因为 LLM 需要为所有文件和文件夹创建必要的支持文档,并用项目特定的详细信息填充它们。建议您将工作量分散到多个任务中,每次专注于在单个系统中创建/填充文档。执行验证步骤以确认所有细节都得到充分覆盖。* | The initial Set-up phase will likely take quite some time if used with a large pre-existing project, as the LLM will need to create the necessary support documentation for all files and folders and populate them with your project specific details. It is suggested that you divide the workload among multiple tasks that concentrate on creating/populating the documentation in a single system at a time. Perform a validation pass to confirm all details are sufficiently covered.

  **Phase Transition Checklists:**

  **阶段转换检查清单:** | Phase Transition Checklists:

  Before transitioning between phases, ensure the following checklists are complete:

  在阶段之间转换之前,确保完成以下检查清单:

  - **Set-up/Maintenance → Strategy**:
  - **设置/维护 → 策略**: | Set-up/Maintenance → Strategy:

    - Confirm `doc_tracker.md` and `module_relationship_tracker.md` in `cline_docs/` have no 'p' placeholders (all dependencies verified).
    - 确认 `cline_docs/` 中的 `doc_tracker.md` 和 `module_relationship_tracker.md` 没有 'p' 占位符 (所有依赖已验证)。 | Confirm `doc_tracker.md` and `module_relationship_tracker.md` in `cline_docs/` have no 'p' placeholders (all dependencies verified).

    - Verify that `[CODE_ROOT_DIRECTORIES]` and `[DOC_DIRECTORIES]` sections in `.clinerules` are correctly populated and list all relevant directories.
    - 验证 `.clinerules` 中的 `[CODE_ROOT_DIRECTORIES]` 和 `[DOC_DIRECTORIES]` 部分已正确填充并列出了所有相关目录。 | Verify that `[CODE_ROOT_DIRECTORIES]` and `[DOC_DIRECTORIES]` sections in `.clinerules` are correctly populated and list all relevant directories.

  - **Strategy → Execution**:
  - **策略 → 执行**: | Strategy → Execution:

    - Ensure all instruction files created in the Strategy phase (e.g., in `strategy_tasks/` or `src/`) contain complete "Steps" and "Dependencies" sections, providing clear guidance for the Execution phase.
    - 确保在策略阶段创建的所有指令文件 (例如在 `strategy_tasks/` 或 `src/` 中) 包含完整的"步骤"和"依赖关系"部分,为执行阶段提供清晰的指导。 | Ensure all instruction files created in the Strategy phase (e.g., in `strategy_tasks/` or `src/`) contain complete "Steps" and "Dependencies" sections, providing clear guidance for the Execution phase.

  Completing these checklists helps ensure a smooth and effective transition between CRCT phases, maintaining system integrity and task continuity.

  完成这些检查清单有助于确保 CRCT 阶段之间的平稳有效转换,保持系统完整性和任务连续性。

2. **Key CRCT Operations**:

2. **关键 CRCT 操作**: | Key CRCT Operations:

   - **Project Analysis**:
   - **项目分析**: | Project Analysis:

     - The LLM will use `analyze-project` command to fully analyze the project, generate **contextual keys**, update dependency trackers (main, doc, and mini-trackers), and generate embeddings. This command is central to maintaining up-to-date dependency information and should be run in the Set-up/Maintenance phase and after significant code changes.
     - LLM 将使用 `analyze-project` 命令来完全分析项目,生成**上下文键 (contextual keys)**,更新依赖跟踪器 (主跟踪器、文档跟踪器和迷你跟踪器),并生成嵌入 (embeddings)。此命令是保持最新依赖信息的核心,应在设置/维护阶段和重大代码更改后运行。 | The LLM will use `analyze-project` command to fully analyze the project, generate **contextual keys**, update dependency trackers (main, doc, and mini-trackers), and generate embeddings. This command is central to maintaining up-to-date dependency information and should be run in the Set-up/Maintenance phase and after significant code changes.

   - **Dependency Inspection**:
   - **依赖检查**: | Dependency Inspection:

     - The LLM will utilize the `show-dependencies --key <key>` command to inspect dependencies for a specific **contextual key**. Replace `<key>` with the desired file or module key. This command aggregates dependency information from all trackers and provides a comprehensive view of inbound and outbound dependencies, significantly simplifying dependency analysis.
     - LLM 将使用 `show-dependencies --key <key>` 命令来检查特定**上下文键**的依赖关系。将 `<key>` 替换为所需的文件或模块键。此命令聚合来自所有跟踪器的依赖信息,并提供入站和出站依赖关系的综合视图,显著简化依赖分析。 | The LLM will utilize the `show-dependencies --key <key>` command to inspect dependencies for a specific **contextual key**. Replace `<key>` with the desired file or module key. This command aggregates dependency information from all trackers and provides a comprehensive view of inbound and outbound dependencies, significantly simplifying dependency analysis.

   - **Manual Dependency Management**:
   - **手动依赖管理**: | Manual Dependency Management:

     - The LLM will use `add-dependency --tracker <tracker_file> --source-key <key> --target-key <key1> [<key2>...] --dep-type <char>` to manually set dependency relationships in tracker files. This is useful for correcting or verifying suggested dependencies and for marking verified relationships. **Ensure you are using contextual keys when using this command.**
     - LLM 将使用 `add-dependency --tracker <tracker_file> --source-key <key> --target-key <key1> [<key2>...] --dep-type <char>` 在跟踪器文件中手动设置依赖关系。这对于纠正或验证建议的依赖关系以及标记已验证的关系很有用。**使用此命令时请确保使用上下文键。** | The LLM will use `add-dependency --tracker <tracker_file> --source-key <key> --target-key <key1> [<key2>...] --dep-type <char>` to manually set dependency relationships in tracker files. This is useful for correcting or verifying suggested dependencies and for marking verified relationships. **Ensure you are using contextual keys when using this command.**

       *(Note: --target-key accepts multiple keys. The specified `--dep-type` is applied to *all* targets.)*
       *(注意: --target-key 接受多个键。指定的 `--dep-type` 将应用于*所有*目标。)* | Note: --target-key accepts multiple keys. The specified `--dep-type` is applied to *all* targets.

       *(Recommendation: Specify no more than five target keys at once for clarity.)*
       *(建议: 为清晰起见,一次指定不超过五个目标键。)* | Recommendation: Specify no more than five target keys at once for clarity.

     - The LLM will use `remove-key --tracker <tracker_file> --key <key>` to remove a key and its associated data from a tracker file, typically used when files are deleted or refactored. **Ensure you are using contextual keys when using this command.**
     - LLM 将使用 `remove-key --tracker <tracker_file> --key <key>` 从跟踪器文件中删除键及其关联数据,通常在删除或重构文件时使用。**使用此命令时请确保使用上下文键。** | The LLM will use `remove-key --tracker <tracker_file> --key <key>` to remove a key and its associated data from a tracker file, typically used when files are deleted or refactored. **Ensure you are using contextual keys when using this command.**

   **Dependency Characters for Manual Management:**

   **手动管理的依赖字符:** | Dependency Characters for Manual Management:

   When manually managing dependencies using `add-dependency`, you need to specify the dependency type using a character code. Here's a breakdown of the available characters, as defined in the `[Character_Definitions]` section of `.clinerules`:

   当使用 `add-dependency` 手动管理依赖关系时,您需要使用字符代码指定依赖类型。以下是可用字符的详细说明,如 `.clinerules` 的 `[Character_Definitions]` 部分所定义:

   - `<`: Row depends on column (Source depends on Target).
   - `<`: 行依赖于列 (源依赖于目标)。 | Row depends on column (Source depends on Target).

   - `>`: Column depends on row (Target depends on Source).
   - `>`: 列依赖于行 (目标依赖于源)。 | Column depends on row (Target depends on Source).

   - `x`: Mutual dependency (Both depend on each other).
   - `x`: 相互依赖 (双方相互依赖)。 | Mutual dependency (Both depend on each other).

   - `d`: Documentation dependency (Source documents Target).
   - `d`: 文档依赖 (源记录目标)。 | Documentation dependency (Source documents Target).

   - `o`: Self dependency (Used only on the diagonal of tracker grids, indicating a file's dependency on itself - usually for structural elements).
   - `o`: 自依赖 (仅用于跟踪器网格的对角线,表示文件对自身的依赖 - 通常用于结构元素)。 | Self dependency (Used only on the diagonal of tracker grids, indicating a file's dependency on itself - usually for structural elements).

   - `n`: Verified no dependency (Explicitly marks that no dependency exists).
   - `n`: 已验证无依赖 (明确标记不存在依赖关系)。 | Verified no dependency (Explicitly marks that no dependency exists).

   - `p`: Placeholder (Indicates an unverified or suggested dependency, needs manual review).
   - `p`: 占位符 (表示未验证或建议的依赖关系,需要手动审查)。 | Placeholder (Indicates an unverified or suggested dependency, needs manual review).

   - `s`: Semantic dependency (weak - similarity score between 0.05 and 0.06).
   - `s`: 语义依赖 (弱 - 相似度得分在 0.05 到 0.06 之间)。 | Semantic dependency (weak - similarity score between 0.05 and 0.06).

   - `S`: Semantic dependency (strong - similarity score 0.07 or higher).
   - `S`: 语义依赖 (强 - 相似度得分 0.07 或更高)。 | Semantic dependency (strong - similarity score 0.07 or higher).

   **Example Scenarios:**

   **示例场景:** | Example Scenarios:

   - If `moduleA.py` imports `moduleB.py`, you would use `>` to indicate that `moduleB.py` (Target/Column) depends on `moduleA.py` (Source/Row).
   - 如果 `moduleA.py` 导入 `moduleB.py`,您将使用 `>` 来表示 `moduleB.py` (目标/列) 依赖于 `moduleA.py` (源/行)。 | If `moduleA.py` imports `moduleB.py`, you would use `>` to indicate that `moduleB.py` (Target/Column) depends on `moduleA.py` (Source/Row).

   - If `docs_about_moduleA.md` documents `moduleA.py`, use `d`.
   - 如果 `docs_about_moduleA.md` 记录 `moduleA.py`,使用 `d`。 | If `docs_about_moduleA.md` documents `moduleA.py`, use `d`.

   - If you have manually verified that there is no dependency between two modules, use `n` to explicitly mark it as such and prevent future suggestions.
   - 如果您已手动验证两个模块之间不存在依赖关系,请使用 `n` 明确标记并防止将来的建议。 | If you have manually verified that there is no dependency between two modules, use `n` to explicitly mark it as such and prevent future suggestions.

   Using these characters correctly ensures accurate and meaningful dependency tracking within the CRCT system. Remember to use contextual keys for all manual dependency management operations.

   正确使用这些字符可确保在 CRCT 系统内进行准确且有意义的依赖跟踪。请记住在所有手动依赖管理操作中使用上下文键。

  **Understanding Contextual Keys:**

  **理解上下文键:** | Understanding Contextual Keys:

  CRCT v7.5 uses a hierarchical key system (`KeyInfo`) to represent files and directories. Keys follow a pattern like `Tier` + `DirLetter` + `[SubdirLetter]` + `[FileNumber]` (e.g., `1A`, `1Aa`, `1Aa1`).

  CRCT v7.5 使用分层键系统 (`KeyInfo`) 来表示文件和目录。键遵循类似 `Tier` + `DirLetter` + `[SubdirLetter]` + `[FileNumber]` 的模式 (例如 `1A`、`1Aa`、`1Aa1`)。

  - **Tier:** The initial number indicates the nesting level. Top-level roots are Tier 1.
  - **层级 (Tier):** 初始数字表示嵌套级别。顶级根目录为第 1 层。 | The initial number indicates the nesting level. Top-level roots are Tier 1.

  - **DirLetter:** An uppercase letter ('A', 'B', ...) identifies top-level directories within defined roots.
  - **目录字母 (DirLetter):** 大写字母 ('A'、'B'、...) 识别定义根目录中的顶级目录。 | An uppercase letter ('A', 'B', ...) identifies top-level directories within defined roots.

  - **SubdirLetter:** A lowercase letter ('a', 'b', ...) identifies subdirectories within a directory.
  - **子目录字母 (SubdirLetter):** 小写字母 ('a'、'b'、...) 识别目录中的子目录。 | A lowercase letter ('a', 'b', ...) identifies subdirectories within a directory.

  - **FileNumber:** A number identifies files within a directory.
  - **文件编号 (FileNumber):** 数字识别目录中的文件。 | A number identifies files within a directory.

  **Tier Promotion:** To keep keys manageable in deeply nested projects, CRCT uses "tier promotion". When a directory *already represented by a subdirectory key* (e.g., `1Ba`) contains further subdirectories requiring keys, those sub-subdirectories will start a *new tier*. For example, a directory inside `1Ba` might get the key `2Ca` (Tier 2, promoted Dir 'C', Subdir 'a'), instead of `1Baa`. This prevents excessively long keys.

  **层级提升:** 为了在深度嵌套的项目中保持键的可管理性,CRCT 使用"层级提升"。当一个*已经由子目录键表示*的目录 (例如 `1Ba`) 包含需要键的更多子目录时,这些子子目录将启动一个*新层级*。例如,`1Ba` 内的目录可能会获得键 `2Ca` (第 2 层,提升的目录 'C',子目录 'a'),而不是 `1Baa`。这可以防止键过长。 | To keep keys manageable in deeply nested projects, CRCT uses "tier promotion". When a directory *already represented by a subdirectory key* (e.g., `1Ba`) contains further subdirectories requiring keys, those sub-subdirectories will start a *new tier*. For example, a directory inside `1Ba` might get the key `2Ca` (Tier 2, promoted Dir 'C', Subdir 'a'), instead of `1Baa`. This prevents excessively long keys.

   **Understanding Dependency Trackers:**

   **理解依赖跟踪器:** | Understanding Dependency Trackers:

   CRCT uses three types of tracker files to manage dependencies:

   CRCT 使用三种类型的跟踪器文件来管理依赖关系:

   - **`module_relationship_tracker.md` (Main Tracker):** Located in `cline_docs/`, this tracker provides a high-level view of dependencies *between modules*. Modules typically correspond to the top-level directories defined in `[CODE_ROOT_DIRECTORIES]` within `.clinerules`. Dependencies shown here are *aggregated* from lower-level trackers; if a file in `moduleA` depends on a file in `moduleB`, this dependency is "rolled up" and represented as a dependency from `moduleA` to `moduleB` in this main tracker.
   - **`module_relationship_tracker.md` (主跟踪器):** 位于 `cline_docs/` 中,此跟踪器提供模块*之间*依赖关系的高级视图。模块通常对应于 `.clinerules` 中 `[CODE_ROOT_DIRECTORIES]` 定义的顶级目录。此处显示的依赖关系是从较低级别跟踪器*聚合*的;如果 `moduleA` 中的文件依赖于 `moduleB` 中的文件,则此依赖关系将"汇总"并在此主跟踪器中表示为从 `moduleA` 到 `moduleB` 的依赖关系。 | Located in `cline_docs/`, this tracker provides a high-level view of dependencies *between modules*. Modules typically correspond to the top-level directories defined in `[CODE_ROOT_DIRECTORIES]` within `.clinerules`. Dependencies shown here are *aggregated* from lower-level trackers; if a file in `moduleA` depends on a file in `moduleB`, this dependency is "rolled up" and represented as a dependency from `moduleA` to `moduleB` in this main tracker.

   - **`doc_tracker.md`:** Located in `cline_docs/`, this tracks dependencies between documentation files found within the directories specified in `[DOC_DIRECTORIES]` in `.clinerules`.
   - **`doc_tracker.md`:** 位于 `cline_docs/` 中,跟踪 `.clinerules` 中 `[DOC_DIRECTORIES]` 指定的目录中的文档文件之间的依赖关系。 | Located in `cline_docs/`, this tracks dependencies between documentation files found within the directories specified in `[DOC_DIRECTORIES]` in `.clinerules`.

   - **Mini-Trackers (`{module_name}_module.md`):** Located within each module directory (as defined in `[CODE_ROOT_DIRECTORIES]`), these files track dependencies *between files within that specific module* and also dependencies from internal files to *external* files (files outside the module or in documentation roots). The tracker data is embedded within the module's documentation file between `---mini_tracker_start---` and `---mini_tracker_end---` markers.
   - **迷你跟踪器 (`{module_name}_module.md`):** 位于每个模块目录中 (如 `[CODE_ROOT_DIRECTORIES]` 所定义),这些文件跟踪*特定模块内文件之间*的依赖关系,以及从内部文件到*外部*文件 (模块外或文档根目录中的文件) 的依赖关系。跟踪器数据嵌入在模块文档文件的 `---mini_tracker_start---` 和 `---mini_tracker_end---` 标记之间。 | Located within each module directory (as defined in `[CODE_ROOT_DIRECTORIES]`), these files track dependencies *between files within that specific module* and also dependencies from internal files to *external* files (files outside the module or in documentation roots). The tracker data is embedded within the module's documentation file between `---mini_tracker_start---` and `---mini_tracker_end---` markers.

   **Suggestion Priority:** When different analysis methods (e.g., explicit import vs. semantic similarity) suggest conflicting dependencies between the same two files, CRCT uses a priority system to decide which dependency character (`<`, `>`, `x`, `d`, `S`, `s`, `p`) to record. The approximate priority order (highest first) is: `x` (mutual), `<`/`>` (direct structural/import), `d` (documentation link), `S` (strong semantic), `s` (weak semantic), `n`/`p`/`o` (no/placeholder/self). Explicit dependencies generally override semantic ones.

   **建议优先级:** 当不同的分析方法 (例如显式导入与语义相似度) 对相同的两个文件建议冲突的依赖关系时,CRCT 使用优先级系统来决定记录哪个依赖字符 (`<`、`>`、`x`、`d`、`S`、`s`、`p`)。近似优先级顺序 (从高到低) 为: `x` (相互)、`<`/`>` (直接结构/导入)、`d` (文档链接)、`S` (强语义)、`s` (弱语义)、`n`/`p`/`o` (无/占位符/自)。显式依赖通常覆盖语义依赖。

3.  **Mandatory Update Protocol (MUP)**:
3.  **强制更新协议 (MUP)**: | Mandatory Update Protocol (MUP):

    - CRCT employs a Mandatory Update Protocol (MUP) to ensure system state consistency. The LLM will perform a full MUP regularly (every 5 turns) to update `activeContext.md`, `changelog.md`, and `.clinerules`, and to clean up completed tasks. **The MUP is crucial for maintaining system integrity and should not be skipped.**
    - CRCT 采用强制更新协议 (MUP) 以确保系统状态一致性。LLM 将定期 (每 5 轮) 执行完整的 MUP,以更新 `activeContext.md`、`changelog.md` 和 `.clinerules`,并清理已完成的任务。**MUP 对于保持系统完整性至关重要,不应跳过。** | CRCT employs a Mandatory Update Protocol (MUP) to ensure system state consistency. The LLM will perform a full MUP regularly (every 5 turns) to update `activeContext.md`, `changelog.md`, and `.clinerules`, and to clean up completed tasks. **The MUP is crucial for maintaining system integrity and should not be skipped.**

    - If the LLM does not perform this step within a reasonable number of turns, prompt it to follow the MUP protocol. Remember that the context window is limited and LLMs quickly lose track of what the have and haven't done as the context window grows. *Be very wary of LLM hallucinations and mis-steps, especially in context sizes above 100k*
    - 如果 LLM 在合理数量的轮次内未执行此步骤,请提示它遵循 MUP 协议。请记住上下文窗口是有限的,随着上下文窗口的增长,LLM 很快就会忘记它们做了什么和没做什么。*请非常警惕 LLM 的幻觉和错误步骤,尤其是在上下文大小超过 100k 时* | If the LLM does not perform this step within a reasonable number of turns, prompt it to follow the MUP protocol. Remember that the context window is limited and LLMs quickly lose track of what the have and haven't done as the context window grows. *Be very wary of LLM hallucinations and mis-steps, especially in context sizes above 100k*

4. **Configuration**:
4. **配置**: | Configuration:

   - **`.clinerules.config.json`**: Configure system settings in this file.
   - **`.clinerules.config.json`**: 在此文件中配置系统设置。 | Configure system settings in this file.

     - `embedding_device`:  Set the embedding device (`cpu`, `cuda`, `mps`) to optimize performance based on your hardware.
     - `embedding_device`:  设置嵌入设备 (`cpu`、`cuda`、`mps`) 以根据您的硬件优化性能。 | Set the embedding device (`cpu`, `cuda`, `mps`) to optimize performance based on your hardware.

     - `excluded_file_patterns`: Define file exclusion patterns (glob patterns) to customize project analysis and exclude specific files or directories from dependency tracking.
     - `excluded_file_patterns`: 定义文件排除模式 (glob 模式) 以自定义项目分析,并从依赖跟踪中排除特定文件或目录。 | Define file exclusion patterns (glob patterns) to customize project analysis and exclude specific files or directories from dependency tracking.

   - *Note: Other settings like specific path exclusions (`excluded_paths`) and system directory locations (`memory_dir`, `embeddings_dir`, `backups_dir`, etc.) are also configurable in `.clinerules.config.json`. Refer to the file or defaults for more details.*
   - *注意: 其他设置如特定路径排除 (`excluded_paths`) 和系统目录位置 (`memory_dir`、`embeddings_dir`、`backups_dir` 等) 也可以在 `.clinerules.config.json` 中配置。有关更多详细信息,请参阅文件或默认值。* | Note: Other settings like specific path exclusions (`excluded_paths`) and system directory locations (`memory_dir`, `embeddings_dir`, `backups_dir`, etc.) are also configurable in `.clinerules.config.json`. Refer to the file or defaults for more details.

   - **`.clinerules`**:  Manage core system settings directly in the `.clinerules` file.
   - **`.clinerules`**:  直接在 `.clinerules` 文件中管理核心系统设置。 | Manage core system settings directly in the `.clinerules` file.

     - `current_phase`: Set the current operational phase of CRCT.
     - `current_phase`: 设置 CRCT 的当前操作阶段。 | Set the current operational phase of CRCT.

     - `[CODE_ROOT_DIRECTORIES]`: Define directories considered as code roots for project analysis. **Modify this section to specify directories containing source code that should be analyzed for dependencies.**
     - `[CODE_ROOT_DIRECTORIES]`: 定义被视为项目分析代码根目录的目录。**修改此部分以指定包含应分析依赖关系的源代码的目录。** | Define directories considered as code roots for project analysis. **Modify this section to specify directories containing source code that should be analyzed for dependencies.**

     - `[DOC_DIRECTORIES]`: Define directories considered as documentation roots. **Modify this section to specify directories containing project documentation that should be tracked.**
     - `[DOC_DIRECTORIES]`: 定义被视为文档根目录的目录。**修改此部分以指定包含应跟踪的项目文档的目录。** | Define directories considered as documentation roots. **Modify this section to specify directories containing project documentation that should be tracked.**

     - `[LEARNING_JOURNAL]`: Review the learning journal for insights into system operations and best practices.
     - `[LEARNING_JOURNAL]`: 查看学习日志以了解系统操作和最佳实践的见解。 | Review the learning journal for insights into system operations and best practices.

---

## Hierarchical Design Token Architecture (HDTA)

## 分层设计令牌架构 (HDTA) | Hierarchical Design Token Architecture (HDTA)

CRCT utilizes the Hierarchical Design Token Architecture (HDTA) to organize project documentation and planning. HDTA provides a structured approach to manage system-level information, broken down into four tiers of documents:

CRCT 利用分层设计令牌架构 (HDTA) 来组织项目文档和规划。HDTA 提供了一种结构化的方法来管理系统级信息,分为四个文档层级:

1. **System Manifest (`system_manifest.md` in `cline_docs/`)**: Provides a top-level overview of the entire project, its goals, architecture, and key components. This document is created during the Set-up/Maintenance phase and serves as the central point of reference for the project.
1. **系统清单 (`cline_docs/` 中的 `system_manifest.md`)**: 提供整个项目的顶层概述,包括其目标、架构和关键组件。此文档在设置/维护阶段创建,作为项目的中心参考点。 | Provides a top-level overview of the entire project, its goals, architecture, and key components. This document is created during the Set-up/Maintenance phase and serves as the central point of reference for the project.

2. **Domain Modules (`{module_name}_module.md` in `cline_docs/`)**: Describes major functional areas or modules within the project. Each module document details its purpose, functionalities, and relationships with other modules. These are also created during Set-up/Maintenance.
2. **域模块 (`cline_docs/` 中的 `{module_name}_module.md`)**: 描述项目内的主要功能区域或模块。每个模块文档详细说明其目的、功能以及与其他模块的关系。这些也在设置/维护阶段创建。 | Describes major functional areas or modules within the project. Each module document details its purpose, functionalities, and relationships with other modules. These are also created during Set-up/Maintenance.

3. **Implementation Plans (Files within modules)**: Contains detailed plans for specific implementations within a module. These documents outline the steps, dependencies, and considerations for implementing particular features or functionalities. Implementation plans are typically created during the Strategy phase.
3. **实施计划 (模块内的文件)**: 包含模块内特定实施的详细计划。这些文档概述了实施特定功能或功能的步骤、依赖关系和注意事项。实施计划通常在策略阶段创建。 | Contains detailed plans for specific implementations within a module. These documents outline the steps, dependencies, and considerations for implementing particular features or functionalities. Implementation plans are typically created during the Strategy phase.

4. **Task Instructions (`{task_name}.md` in `strategy_tasks/` or `src/`)**: Provides procedural guidance for individual tasks. Task instructions break down complex tasks into smaller, manageable steps, ensuring clarity and efficient execution. Task instructions are created during the Strategy phase to guide the Execution phase.
4. **任务指令 (`strategy_tasks/` 或 `src/` 中的 `{task_name}.md`)**: 为单个任务提供程序指导。任务指令将复杂的任务分解为更小、可管理的步骤,确保清晰和高效执行。任务指令在策略阶段创建以指导执行阶段。 | Provides procedural guidance for individual tasks. Task instructions break down complex tasks into smaller, manageable steps, ensuring clarity and efficient execution. Task instructions are created during the Strategy phase to guide the Execution phase.

HDTA helps maintain a clear and organized project documentation structure, facilitating better understanding, collaboration, and management of complex projects within CRCT. The templates for HDTA documents are located in `cline_docs/templates/`.

HDTA 有助于维护清晰有序的项目文档结构,促进 CRCT 内复杂项目的更好理解、协作和管理。HDTA 文档的模板位于 `cline_docs/templates/` 中。

---

## Troubleshooting

## 故障排除 | Troubleshooting

- **Initialization Issues**: If the system fails to initialize, ensure that the core prompt is correctly loaded into the Cline extension and that all prerequisites are met. **Double-check that you have copied the content of `cline_docs/prompts/core_prompt(put this in Custom Instructions).md` into the Cline custom instructions field.**
- **初始化问题**: 如果系统无法初始化,请确保核心提示已正确加载到 Cline 扩展中,并且满足所有前置要求。**请仔细检查您是否已将 `cline_docs/prompts/core_prompt(put this in Custom Instructions).md` 的内容复制到 Cline 自定义指令字段中。** | If the system fails to initialize, ensure that the core prompt is correctly loaded into the Cline extension and that all prerequisites are met. **Double-check that you have copied the content of `cline_docs/prompts/core_prompt(put this in Custom Instructions).md` into the Cline custom instructions field.**

- **Dependency Tracking Problems**: If you encounter issues with dependency tracking, use `analyze-project` to refresh the trackers and embeddings. Check `.clinerules` for correct configuration of code and documentation roots. **Ensure that the `[CODE_ROOT_DIRECTORIES]` and `[DOC_DIRECTORIES]` sections in `.clinerules` are correctly populated.**
- **依赖跟踪问题**: 如果遇到依赖跟踪问题,请使用 `analyze-project` 刷新跟踪器和嵌入。检查 `.clinerules` 以正确配置代码和文档根目录。**确保 `.clinerules` 中的 `[CODE_ROOT_DIRECTORIES]` 和 `[DOC_DIRECTORIES]` 部分已正确填充。** | If you encounter issues with dependency tracking, use `analyze-project` to refresh the trackers and embeddings. Check `.clinerules` for correct configuration of code and documentation roots. **Ensure that the `[CODE_ROOT_DIRECTORIES]` and `[DOC_DIRECTORIES]` sections in `.clinerules` are correctly populated.**

  - You may need to manually delete the module_relationship_tracker and doc_tracker in cline_docs.
  - 您可能需要手动删除 cline_docs 中的 module_relationship_tracker 和 doc_tracker。 | You may need to manually delete the module_relationship_tracker and doc_tracker in cline_docs.

  - For mini-trackers I suggest manually deleting the content between the mini-tracker start and end markers. *IMPORTANT: do not remove the mini-tracker start and end markers, this will cause the entire file content to be overwritten, losing any information previously recorded.*
  - 对于迷你跟踪器,我建议手动删除迷你跟踪器开始和结束标记之间的内容。*重要: 请勿删除迷你跟踪器的开始和结束标记,这将导致整个文件内容被覆盖,丢失之前记录的任何信息。* | For mini-trackers I suggest manually deleting the content between the mini-tracker start and end markers. *IMPORTANT: do not remove the mini-tracker start and end markers, this will cause the entire file content to be overwritten, losing any information previously recorded.*

- **Command Errors**: Ensure commands are typed correctly and used in the appropriate phase. Refer to command documentation for syntax and usage. **Pay close attention to the required arguments for each command, especially when using `show-dependencies`, `add-dependency`, and `remove-key`.**
- **命令错误**: 确保命令输入正确并在适当的阶段使用。请参阅命令文档以了解语法和用法。**请密切注意每个命令所需的参数,尤其是在使用 `show-dependencies`、`add-dependency` 和 `remove-key` 时。** | Ensure commands are typed correctly and used in the appropriate phase. Refer to command documentation for syntax and usage. **Pay close attention to the required arguments for each command, especially when using `show-dependencies`, `add-dependency`, and `remove-key`.**

- **Key Generation Limit (`KeyGenerationError`)**: The key system supports up to 26 direct subdirectories ('a' through 'z') within any single directory before requiring "tier promotion". If you have a directory structure exceeding this limit (e.g., 27+ immediate subfolders needing keys), the `analyze-project` command may fail with a `KeyGenerationError`. To resolve this, either restructure the directory or add some of the problematic subdirectory paths to the `"excluded_paths"` list in `.clinerules.config.json`.
- **键生成限制 (`KeyGenerationError`)**: 键系统在需要"层级提升"之前支持任何单个目录中最多 26 个直接子目录 ('a' 到 'z')。如果您的目录结构超过此限制 (例如 27+ 个需要键的直接子文件夹),`analyze-project` 命令可能会因 `KeyGenerationError` 而失败。要解决此问题,请重新构建目录或将一些有问题的子目录路径添加到 `.clinerules.config.json` 中的 `"excluded_paths"` 列表中。 | The key system supports up to 26 direct subdirectories ('a' through 'z') within any single directory before requiring "tier promotion". If you have a directory structure exceeding this limit (e.g., 27+ immediate subfolders needing keys), the `analyze-project` command may fail with a `KeyGenerationError`. To resolve this, either restructure the directory or add some of the problematic subdirectory paths to the `"excluded_paths"` list in `.clinerules.config.json`.

---

## Advanced Usage & Troubleshooting

## 高级使用和故障排除 | Advanced Usage & Troubleshooting

- **Semantic Analysis Details:** Semantic similarity analysis (leading to 's' or 'S' dependencies) relies on the `sentence-transformers` library (specifically the `"sentence-transformers/all-mpnet-base-v2"` model by default). Embeddings are stored as `.npy` files in a mirrored structure within the directory configured by `embeddings_dir` in `.clinerules.config.json` (default: `cline_utils/dependency_system/analysis/embeddings/`). The system avoids regenerating embeddings for unchanged files by checking file modification times (mtime) against a `metadata.json` file.
- **语义分析详情:** 语义相似度分析 (导致 's' 或 'S' 依赖关系) 依赖于 `sentence-transformers` 库 (默认情况下为 `"sentence-transformers/all-mpnet-base-v2"` 模型)。嵌入 (embeddings) 作为 `.npy` 文件存储在 `.clinerules.config.json` 中 `embeddings_dir` 配置的目录中的镜像结构内 (默认: `cline_utils/dependency_system/analysis/embeddings/`)。系统通过对照 `metadata.json` 文件检查文件修改时间 (mtime) 来避免为未更改的文件重新生成嵌入。 | Semantic similarity analysis (leading to 's' or 'S' dependencies) relies on the `sentence-transformers` library (specifically the `"sentence-transformers/all-mpnet-base-v2"` model by default). Embeddings are stored as `.npy` files in a mirrored structure within the directory configured by `embeddings_dir` in `.clinerules.config.json` (default: `cline_utils/dependency_system/analysis/embeddings/`). The system avoids regenerating embeddings for unchanged files by checking file modification times (mtime) against a `metadata.json` file.

- **Tracker Backups:** Before overwriting tracker files (`module_relationship_tracker.md`, `doc_tracker.md`, `*_module.md`) during updates (e.g., via `analyze-project`), the system automatically creates a timestamped backup in the directory configured by `backups_dir` (default: `cline_docs/backups/`). The two most recent backups for each tracker are kept.
- **跟踪器备份:** 在更新期间 (例如通过 `analyze-project`) 覆盖跟踪器文件 (`module_relationship_tracker.md`、`doc_tracker.md`、`*_module.md`) 之前,系统会自动在 `backups_dir` 配置的目录中创建带时间戳的备份 (默认: `cline_docs/backups/`)。保留每个跟踪器的两个最新备份。 | Before overwriting tracker files (`module_relationship_tracker.md`, `doc_tracker.md`, `*_module.md`) during updates (e.g., via `analyze-project`), the system automatically creates a timestamped backup in the directory configured by `backups_dir` (default: `cline_docs/backups/`). The two most recent backups for each tracker are kept.

- **Batch Processing Tuning:** The system uses parallel batch processing for tasks like file analysis (`analyze-project`). While it attempts adaptive tuning, performance might vary. For very large projects or specific hardware, if analysis seems slow or uses excessive resources, you can instruct the LLM to try specific parameters for the `BatchProcessor` by suggesting values for `max_workers` (number of threads) or `batch_size` when invoking relevant commands.
- **批处理调优:** 系统使用并行批处理来执行文件分析 (`analyze-project`) 等任务。虽然它会尝试自适应调优,但性能可能会有所不同。对于非常大的项目或特定硬件,如果分析似乎缓慢或使用过多资源,您可以通过在调用相关命令时建议 `max_workers` (线程数) 或 `batch_size` 的值来指示 LLM 尝试 `BatchProcessor` 的特定参数。 | The system uses parallel batch processing for tasks like file analysis (`analyze-project`). While it attempts adaptive tuning, performance might vary. For very large projects or specific hardware, if analysis seems slow or uses excessive resources, you can instruct the LLM to try specific parameters for the `BatchProcessor` by suggesting values for `max_workers` (number of threads) or `batch_size` when invoking relevant commands.

- **Additional Utility Commands:** The `dependency_processor.py` script provides several utility commands beyond the main workflow ones. These might be useful for advanced inspection or manual intervention (ask the LLM to use them if needed):
- **其他实用命令:** `dependency_processor.py` 脚本提供了几个超出主要工作流程的实用命令。这些可能对高级检查或手动干预有用 (如果需要,请让 LLM 使用它们): | The `dependency_processor.py` script provides several utility commands beyond the main workflow ones. These might be useful for advanced inspection or manual intervention (ask the LLM to use them if needed):

    - `python -m cline_utils.dependency_system.dependency_processor analyze-file <file_path> [--output <json_path>]`: Analyzes a single file and outputs detailed findings (imports, calls, etc.) as JSON.
    - `python -m cline_utils.dependency_system.dependency_processor analyze-file <file_path> [--output <json_path>]`: 分析单个文件并将详细发现 (导入、调用等) 输出为 JSON。 | Analyzes a single file and outputs detailed findings (imports, calls, etc.) as JSON.

    - `python -m cline_utils.dependency_system.dependency_processor merge-trackers <primary_path> <secondary_path> [--output <out_path>]`: Merges two tracker files, with the primary taking precedence. Useful for combining tracker data, though typically managed automatically.
    - `python -m cline_utils.dependency_system.dependency_processor merge-trackers <primary_path> <secondary_path> [--output <out_path>]`: 合并两个跟踪器文件,以主跟踪器为优先。用于组合跟踪器数据,尽管通常自动管理。 | Merges two tracker files, with the primary taking precedence. Useful for combining tracker data, though typically managed automatically.

    - `python -m cline_utils.dependency_system.dependency_processor export-tracker <tracker_path> [--format <json|csv|dot>] [--output <out_path>]`: Exports tracker data into different formats for external analysis or visualization (e.g., DOT format for Graphviz).
    - `python -m cline_utils.dependency_system.dependency_processor export-tracker <tracker_path> [--format <json|csv|dot>] [--output <out_path>]`: 将跟踪器数据导出为不同格式以进行外部分析或可视化 (例如 Graphviz 的 DOT 格式)。 | Exports tracker data into different formats for external analysis or visualization (e.g., DOT format for Graphviz).

    - `python -m cline_utils.dependency_system.dependency_processor update-config <key_path> <value>`: Updates a specific setting in `.clinerules.config.json` (e.g., `python -m cline_utils.dependency_system.dependency_processor update-config thresholds.code_similarity 0.75`).
    - `python -m cline_utils.dependency_system.dependency_processor update-config <key_path> <value>`: 更新 `.clinerules.config.json` 中的特定设置 (例如 `python -m cline_utils.dependency_system.dependency_processor update-config thresholds.code_similarity 0.75`)。 | Updates a specific setting in `.clinerules.config.json` (e.g., `python -m cline_utils.dependency_system.dependency_processor update-config thresholds.code_similarity 0.75`).

    - `python -m cline_utils.dependency_system.dependency_processor reset-config`: Resets `.clinerules.config.json` to its default settings.
    - `python -m cline_utils.dependency_system.dependency_processor reset-config`: 将 `.clinerules.config.json` 重置为其默认设置。 | Resets `.clinerules.config.json` to its default settings.

    - `python -m cline_utils.dependency_system.dependency_processor clear-caches`: Clears internal caches used by the dependency system (embeddings metadata, analysis results, etc.). Useful if you suspect stale cache data is causing issues.
    - `python -m cline_utils.dependency_system.dependency_processor clear-caches`: 清除依赖系统使用的内部缓存 (嵌入元数据、分析结果等)。如果您怀疑过时的缓存数据导致问题,这很有用。 | Clears internal caches used by the dependency system (embeddings metadata, analysis results, etc.). Useful if you suspect stale cache data is causing issues.

---

## Notes

## 注意事项 | Notes

- CRCT v7.5 represents a significant restructuring and stabilization of the system. While ongoing refinements and optimizations are planned, v7.5 is considered a stable and feature-rich release.
- CRCT v7.5 代表了系统的重大重构和稳定化。虽然计划进行持续的改进和优化,但 v7.5 被认为是一个稳定且功能丰富的版本。 | CRCT v7.5 represents a significant restructuring and stabilization of the system. While ongoing refinements and optimizations are planned, v7.5 is considered a stable and feature-rich release.

- The LLM automates most dependency management and system commands (e.g., `analyze-project`, `show-dependencies`, etc.).
- LLM 自动化大多数依赖管理和系统命令 (例如 `analyze-project`、`show-dependencies` 等)。 | The LLM automates most dependency management and system commands (e.g., `analyze-project`, `show-dependencies`, etc.).

- For custom projects, ensure `src/` and `docs/` directories are populated before initializing the system.
- 对于自定义项目,请在初始化系统之前确保填充 `src/` 和 `docs/` 目录。 | For custom projects, ensure `src/` and `docs/` directories are populated before initializing the system.

  - `src/` and `docs/` are the default directories used for quick-start.
  - `src/` 和 `docs/` 是用于快速入门的默认目录。 | `src/` and `docs/` are the default directories used for quick-start.

  - The system supports custom code and documentation directory structures, so feel free to create your own if you feel comfortable.
  - 系统支持自定义代码和文档目录结构,因此如果您感到舒适,请随意创建您自己的结构。 | The system supports custom code and documentation directory structures, so feel free to create your own if you feel comfortable.

  (if any issues arise let me know and I will do my best to offer assistance or modify the system to support your unique project structure)
  (如果出现任何问题,请告诉我,我将尽力提供帮助或修改系统以支持您独特的项目结构) | (if any issues arise let me know and I will do my best to offer assistance or modify the system to support your unique project structure)

## Getting Help

## 获取帮助 | Getting Help

For further assistance, questions, or bug reports, please refer to the project's GitHub repository and issue tracker.

如需进一步帮助、问题或错误报告,请参阅项目的 GitHub 仓库和问题跟踪器。

---

Thank you for using CRCT v7.5! I hope it enhances your Cline project workflows.

感谢您使用 CRCT v7.5! 希望它能增强您的 Cline 项目工作流程。
