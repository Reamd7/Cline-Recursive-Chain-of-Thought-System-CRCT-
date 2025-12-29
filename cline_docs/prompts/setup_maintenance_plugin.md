# **Cline Recursive Chain-of-Thought System (CRCT) - Set-up/Maintenance Plugin**
# **Cline 递归思维链系统 (CRCT) - 设置/维护插件**

**This Plugin provides detailed instructions and procedures for the Set-up/Maintenance phase of the CRCT system. It should be used in conjunction with the Core System Prompt.**
**此插件为 CRCT 系统的设置/维护阶段提供详细的说明和程序。应与核心系统提示结合使用。**

## I. Entering and Exiting Set-up/Maintenance Phase
## I. 进入和退出设置/维护阶段

**Entering Set-up/Maintenance Phase:**
**进入设置/维护阶段:**
1.  **Initial State**: Start here for new projects or if `.clinerules` shows `next_phase: "Set-up/Maintenance"`.
    1.  **初始状态**: 从这里开始新项目,或者如果 `.clinerules` 显示 `next_phase: "Set-up/Maintenance"`。
2.  **`.clinerules` Check**: Always read `.clinerules` first. If `[LAST_ACTION_STATE]` indicates `current_phase: "Set-up/Maintenance"` or `next_phase: "Set-up/Maintenance"`, proceed with these instructions, resuming from the `next_action` if specified.
    2.  **`.clinerules` 检查**: 始终首先读取 `.clinerules`。如果 `[LAST_ACTION_STATE]` 指示 `current_phase: "Set-up/Maintenance"` 或 `next_phase: "Set-up/Maintenance"`,则按照这些说明继续,如果指定了则从 `next_action` 恢复。
3.  **New Project**: If `.clinerules` is missing/empty, assume this phase, create `.clinerules` (see Section II), and initialize other core files.
    3.  **新项目**: 如果 `.clinerules` 缺失/为空,则假定此阶段,创建 `.clinerules`(见第二节),并初始化其他核心文件。

**Exiting Set-up/Maintenance Phase:**
**退出设置/维护阶段:**
1.  **Completion Criteria:**
    1.  **完成标准:**
    *   All core files exist and are initialized (Section II).
        - 所有核心文件都存在并已初始化(第二节)。
    *   `[CODE_ROOT_DIRECTORIES]` and `[DOC_DIRECTORIES]` are populated in `.clinerules` (Core Prompt Sections X & XI).
        - `.clinerules` 中填充了 `[CODE_ROOT_DIRECTORIES]` 和 `[DOC_DIRECTORIES]`(核心提示第 X 和 XI 节)。
    *   `doc_tracker.md` exists and has no 'p', 's', or 'S' placeholders remaining (verified via `show-keys` in Section III, Stage 1).
        - `doc_tracker.md` 存在且没有剩余的 'p'、's' 或 'S' 占位符(通过第三节第一阶段中的 `show-keys` 验证)。
    *   All mini-trackers (`*_module.md`) exist and have no 'p', 's', or 'S' placeholders remaining (verified via `show-keys` in Section III, Stage 2).
        - 所有小型跟踪器(`*_module.md`)存在且没有剩余的 'p'、's' 或 'S' 占位符(通过第三节第二阶段中的 `show-keys` 验证)。
    *   `module_relationship_tracker.md` exists and has no 'p', 's', or 'S' placeholders remaining (verified via `show-keys` in Section III, Stage 3).
        - `module_relationship_tracker.md` 存在且没有剩余的 'p'、's' 或 'S' 占位符(通过第三节第三阶段中的 `show-keys` 验证)。
    *   **Code-Documentation Cross-Reference completed (Section III, Stage 4), ensuring essential 'd' links are added.**
        - **代码-文档交叉引用已完成(第三节第四阶段),确保添加了必要的 'd' 链接。**
    *   `system_manifest.md` is created and populated (at least minimally from template).
        - `system_manifest.md` 已创建并填充(至少从模板中基本填充)。
    *   Mini-trackers are created/populated as needed via `analyze-project`.
        - 小型跟踪器根据需要通过 `analyze-project` 创建/填充。
2.  **`.clinerules` Update (MUP):** Once all criteria are met, update `[LAST_ACTION_STATE]` as follows:
    2.  **`.clinerules` 更新(MUP):** 一旦满足所有标准,按如下方式更新 `[LAST_ACTION_STATE]`:
    ```
    last_action: "Completed Set-up/Maintenance Phase"
    current_phase: "Set-up/Maintenance"
    next_action: "Phase Complete - User Action Required"
    next_phase: "Strategy"
    ```
3.  **User Action**: After updating `.clinerules`, pause for user to trigger the next session/phase. Refer to Core System Prompt, Section III for the phase transition checklist.
    3.  **用户操作**: 更新 `.clinerules` 后,暂停以等待用户触发下一个会话/阶段。请参阅核心系统提示第三节,了解阶段转换检查清单。

## II. Initializing Core Required Files & Project Structure
## II. 初始化核心必需文件和项目结构

**Action**: Ensure all core files exist, triggering their creation if missing according to the specifications in the Core System Prompt (Section II).
**操作**: 确保所有核心文件都存在,如果缺少则根据核心系统提示(第二节)中的规范触发其创建。

**Procedure:**
**程序:**
1.  **Check for Existence**: Check if each required file listed in Core Prompt Section II (`.clinerules`, `system_manifest.md`, `activeContext.md`, `module_relationship_tracker.md`, `changelog.md`, `doc_tracker.md`, `userProfile.md`, `progress.md`) exists in its specified location.
    1.  **检查存在性**: 检查核心提示第二节中列出的每个必需文件(`.clinerules`、`system_manifest.md`、`activeContext.md`、`module_relationship_tracker.md`、`changelog.md`、`doc_tracker.md`、`userProfile.md`、`progress.md`)是否存在于其指定位置。
2.  **Identify Code and Documentation Directories**: If `[CODE_ROOT_DIRECTORIES]` or `[DOC_DIRECTORIES]` in `.clinerules` are empty or missing, **stop** other initialization and follow the procedures in Core Prompt Sections X and XI to identify and populate these sections first. Update `.clinerules` and perform MUP. Resume initialization checks afterwards.
    2.  **识别代码和文档目录**: 如果 `.clinerules` 中的 `[CODE_ROOT_DIRECTORIES]` 或 `[DOC_DIRECTORIES]` 为空或缺失,**停止**其他初始化,并遵循核心提示第 X 和 XI 节中的程序首先识别和填充这些部分。更新 `.clinerules` 并执行 MUP。之后恢复初始化检查。
3.  **Trigger Creation of Missing Files**:
    3.  **触发创建缺失的文件**:
    *   **Manual Creation Files** (`.clinerules`, `activeContext.md`, `changelog.md`, `userProfile.md`, `progress.md`): If missing, use `write_to_file` to create them with minimal placeholder content as described in Core Prompt Section II table. State: "File `{file_path}` missing. Creating with placeholder content."
        - **手动创建文件** (`.clinerules`、`activeContext.md`、`changelog.md`、`userProfile.md`、`progress.md`): 如果缺失,使用 `write_to_file` 创建它们,包含核心提示第二节表中描述的最少占位符内容。状态:"文件 `{file_path}` 缺失。正在使用占位符内容创建。"
        *   Example Initial `.clinerules` (if creating):
            - 初始 `.clinerules` 示例(如果创建):
            ```
            [LAST_ACTION_STATE]
            last_action: "System Initialized"
            current_phase: "Set-up/Maintenance"
            next_action: "Initialize Core Files" # Or Identify Code/Doc Roots if needed first
            next_phase: "Set-up/Maintenance"

            [CODE_ROOT_DIRECTORIES]
            # To be identified

            [DOC_DIRECTORIES]
            # To be identified

            [LEARNING_JOURNAL]
            -
            ```
            ```
            [LAST_ACTION_STATE]
            last_action: "System Initialized"
            current_phase: "Set-up/Maintenance"
            next_action: "Initialize Core Files" # 或首先识别代码/文档根目录(如果需要)
            next_phase: "Set-up/Maintenance"

            [CODE_ROOT_DIRECTORIES]
            # 待识别

            [DOC_DIRECTORIES]
            # 待识别

            [LEARNING_JOURNAL]
            -
            ```
    *   **Template-Based File** (`system_manifest.md`): If missing, first use `write_to_file` to create an empty file named `system_manifest.md` in `{memory_dir}/`. State: "File `system_manifest.md` missing. Creating empty file." Then, read the template content from `cline_docs/templates/system_manifest_template.md` and use `write_to_file` again to *overwrite* the empty `system_manifest.md` with the template content. State: "Populating `system_manifest.md` with template content."
        - **基于模板的文件** (`system_manifest.md`): 如果缺失,首先使用 `write_to_file` 在 `{memory_dir}/` 中创建名为 `system_manifest.md` 的空文件。状态:"文件 `system_manifest.md` 缺失。正在创建空文件。"然后,从 `cline_docs/templates/system_manifest_template.md` 读取模板内容,并再次使用 `write_to_file` 用模板内容*覆盖*空的 `system_manifest.md`。状态:"正在用模板内容填充 `system_manifest.md`。"
    *   **Tracker Files** (`module_relationship_tracker.md`, `doc_tracker.md`, and mini-trackers `*_module.md`):
        - **跟踪器文件** (`module_relationship_tracker.md`、`doc_tracker.md` 和小型跟踪器 `*_module.md`):
        *   **DO NOT CREATE MANUALLY.**
            - **请勿手动创建。**
        *   If any of these are missing, or if significant project changes have occurred, or if you are starting verification, run `analyze-project`. This command will create or update all necessary trackers based on the current project structure and identified code/doc roots.
            - 如果其中任何一个缺失,或者如果发生了重大的项目更改,或者如果您正在开始验证,请运行 `analyze-project`。此命令将根据当前项目结构和识别的代码/文档根目录创建或更新所有必要的跟踪器。
        ```bash
        # Ensure code/doc roots are set in .clinerules first!
        python -m cline_utils.dependency_system.dependency_processor analyze-project
        ```
        ```bash
        # 首先确保在 .clinerules 中设置了代码/文档根目录!
        python -m cline_utils.dependency_system.dependency_processor analyze-project
        ```
        *   State: "Tracker file(s) missing or update needed. Running `analyze-project` to create/update trackers."
            - 状态:"跟踪器文件缺失或需要更新。正在运行 `analyze-project` 来创建/更新跟踪器。"
        *   *(Running `analyze-project` is also the first step in the verification workflow in Section III).*
            - *(运行 `analyze-project` 也是第三节中验证工作流程的第一步。)*
        *   *(Optional: Add `--force-analysis` or `--force-embeddings` if needed)*.
            - *(可选: 如果需要,添加 `--force-analysis` 或 `--force-embeddings`)*。

        *   *(Mini-trackers in module directories are also created/updated by `analyze-project`)*.
            - *(模块目录中的小型跟踪器也由 `analyze-project` 创建/更新)*。
4.  **MUP**: Follow Core Prompt MUP (Section VI) and Section V additions below after creating files or running `analyze-project`. Update `[LAST_ACTION_STATE]` to reflect progress (e.g., `next_action: "Verify Tracker Dependencies"`).
    4.  **MUP**: 在创建文件或运行 `analyze-project` 之后遵循核心提示 MUP(第六节)和下面的第五节附加内容。更新 `[LAST_ACTION_STATE]` 以反映进度(例如,`next_action: "Verify Tracker Dependencies"`)。

## III. Analyzing and Verifying Tracker Dependencies (Ordered Workflow)
## III. 分析和验证跟踪器依赖关系(有序工作流)

**DO NOT ASSUME A DEPENDENCY BEFORE THE RELATED FILES HAVE BEEN READ!!**
**在阅读相关文件之前不要假设依赖关系!!**

**Objective**: Ensure trackers accurately reflect project dependencies by systematically resolving placeholders ('p') and verifying suggestions ('s', 'S'), followed by an explicit code-to-documentation cross-referencing step. **This process MUST follow a specific order:**
**目标**: 通过系统地解决占位符('p')和验证建议('s'、'S'),确保跟踪器准确反映项目依赖关系,然后是显式的代码-文档交叉引用步骤。**此过程必须遵循特定顺序:**
1.  `doc_tracker.md` (Placeholder/Suggestion Resolution)
    1.  `doc_tracker.md`(占位符/建议解决)
2.  All Mini-Trackers (`*_module.md`) (Placeholder/Suggestion Resolution)
    2.  所有小型跟踪器(`*_module.md`)(占位符/建议解决)
3.  `module_relationship_tracker.md` (Placeholder/Suggestion Resolution)
    3.  `module_relationship_tracker.md`(占位符/建议解决)
4.  **Code-Documentation Cross-Reference** (Adding explicit dependencies)
    4.  **代码-文档交叉引用**(添加显式依赖关系)

This order is crucial because Mini-Trackers capture detailed cross-directory dependencies within modules, which are essential for accurately determining the higher-level module-to-module relationships in `module_relationship_tracker.md`.
这个顺序至关重要,因为小型跟踪器捕获模块内详细的跨目录依赖关系,这对于准确确定 `module_relationship_tracker.md` 中更高级别的模块到模块关系至关重要。

**IMPORTANT**
**重要提示**
*   **All tracker modifications MUST use `dependency_processor.py` commands.** See Core Prompt Section VIII for command details.
    - **所有跟踪器修改必须使用 `dependency_processor.py` 命令。** 请参阅核心提示第八节了解命令详细信息。
*   **Do NOT read tracker files directly** for dependency information; use `show-keys` and `show-dependencies`.
    - **请勿直接读取跟踪器文件**以获取依赖信息;使用 `show-keys` 和 `show-dependencies`。
*   Run `analyze-project` *before* starting this verification process if significant code/doc changes have occurred since the last run, or upon entering this phase (as done in Section II).
    - 如果自上次运行以来发生了重大的代码/文档更改,或在进入此阶段时(如第二节中所做),在开始此验证过程之前*运行* `analyze-project`。

***CRITICAL EMPHASIS***: *It is critical that the documentation is **Exhaustively** cross-referenced against the code. The code cannot be completed properly if the docs that define it are not listed as a dependency. The following verification stages, especially Stage 4, are designed to achieve this.*
***关键强调***:*文档必须**详尽地**与代码交叉引用,这一点至关重要。如果定义代码的文档未列为依赖关系,则无法正确完成代码。以下验证阶段,特别是第四阶段,旨在实现这一目标。*

**This phase isn't about efficiency, it's about *accuracy*. This is a foundational job. If the accuracy in this phase is low, the entire project will suffer.**
**这个阶段不是关于效率,而是关于*准确性*。这是一项基础工作。如果这个阶段的准确性低,整个项目将受到影响。**

**Procedure:**
**程序:**

1.  **Run Project Analysis (Initial & Updates)**:
    1.  **运行项目分析(初始和更新)**:
    *   Use `analyze-project` to automatically generate/update keys, analyze files, suggest dependencies ('p', 's', 'S'), and update *all* trackers (`module_relationship_tracker.md`, `doc_tracker.md`, and mini-trackers). This command creates trackers if they don't exist and populates/updates the grid based on current code/docs and configuration.
        - 使用 `analyze-project` 自动生成/更新键、分析文件、建议依赖关系('p'、's'、'S')并更新*所有*跟踪器(`module_relationship_tracker.md`、`doc_tracker.md` 和小型跟踪器)。此命令创建跟踪器(如果不存在)并根据当前代码/文档和配置填充/更新网格。
    ```bash
    python -m cline_utils.dependency_system.dependency_processor analyze-project
    ```
    *   *(Optional: Add `--force-analysis` or `--force-embeddings` if needed, e.g., if configuration changed or cache seems stale)*.
        - *(可选: 如果需要,添加 `--force-analysis` 或 `--force-embeddings`,例如如果配置更改或缓存似乎过时)*。
    *   **Review logs (`debug.txt`, `suggestions.log`)** for analysis details and suggested changes, but prioritize the verification workflow below. State: "Ran analyze-project. Reviewing logs and proceeding with ordered verification."
        - **审查日志(`debug.txt`、`suggestions.log`)**以获取分析详细信息和建议的更改,但优先考虑下面的验证工作流程。状态:"运行了 analyze-project。正在审查日志并继续进行有序验证。"

2.  **Stage 1: Verify `doc_tracker.md`**:
    2.  **第一阶段:验证 `doc_tracker.md`**:
    *   **A. Identify Keys Needing Verification**:
        - **A. 识别需要验证的键**:
        *   Run `show-keys` for `doc_tracker.md`:
            - 为 `doc_tracker.md` 运行 `show-keys`:
          ```bash
          python -m cline_utils.dependency_system.dependency_processor show-keys --tracker <path_to_doc_tracker.md>
          ```
          *(Use actual path, likely `{memory_dir}/doc_tracker.md` based on config)*
          *(使用实际路径,可能基于配置为 `{memory_dir}/doc_tracker.md`)*
        *   Examine the output. Keys listed might be base keys (e.g., "1A1") or globally instanced keys (e.g., "2B1#1") if their base key string is used for multiple different paths in the project. Identify all lines ending with `(checks needed: ...)`. This indicates unresolved 'p', 's', or 'S' characters in that key's row *within this tracker*.
            - 检查输出。列出的键可能是基础键(例如 "1A1")或全局实例键(例如 "2B1#1"),如果它们的基础键字符串用于项目中的多个不同路径。识别所有以 `(checks needed: ...)` 结尾的行。这表示该键的行*在此跟踪器内*中有未解决的 'p'、's' 或 'S' 字符。
        *   Create a list of these keys needing verification for `doc_tracker.md`. If none, state this and proceed to Stage 2.
            - 创建这些需要验证的键的列表以用于 `doc_tracker.md`。如果没有,说明这一点并继续进行第二阶段。
    *   **B. Verify Placeholders/Suggestions for Identified Keys**:
        - **B. 验证已识别键的占位符/建议**:
        *   Iterate through the list of keys from Step 2.A.
            - 遍历步骤 2.A 中的键列表。
        *   For each `key_string` (row key):
            - 对于每个 `key_string`(行键):
            *   **Get Context**: Run `show-placeholders` targeting the current tracker and key. This command specifically lists the 'p', 's', and 'S' relationships for the given key *within this tracker*, providing a targeted list for verification.
                - **获取上下文**: 针对当前跟踪器和键运行 `show-placeholders`。此命令专门列出给定键*在此跟踪器内*的 'p'、's' 和 'S' 关系,提供用于验证的有针对性的列表。
            ```bash
            python -m cline_utils.dependency_system.dependency_processor show-placeholders --tracker <path_to_doc_tracker.md> --key <key_string>
            ```
            *   **Plan Reading**: Identify the source file (for `key_string`) and relevant target files (for column keys needing verification). To improve efficiency, plan to read the source file and *multiple* relevant target files together in the next step. Suggest batch reading if files are co-located (e.g., "Suggest reading source file X and target files Y, Z from the same directory. Can you provide folder contents or should I read individually using `read_file`?"). Be mindful of context limits.
                - **规划阅读**: 识别源文件(用于 `key_string`)和相关目标文件(用于需要验证的列键)。为了提高效率,计划在下一步中一起读取源文件和*多个*相关目标文件。如果文件位于同一位置,建议批量阅读(例如,"建议从同一目录读取源文件 X 和目标文件 Y、Z。您可以提供文件夹内容还是我应该使用 `read_file` 单独读取?")。注意上下文限制。
            *   **Examine Files**: Use `read_file` to examine the content of the source file and the relevant target files/folders identified.
                - **检查文件**: 使用 `read_file` 检查识别的源文件和相关目标文件/文件夹的内容。
            *   **Determine Relationship (CRITICAL STEP)**: Based on file contents, determine the **true functional or essential conceptual relationship** between the source (`key_string`) and each target key being verified.
                - **确定关系(关键步骤)**: 根据文件内容,确定源(`key_string`)和正在验证的每个目标键之间的**真实功能或基本概念关系**。
                *   **Go Beyond Similarity**: Suggestions ('s', 'S') might only indicate related topics, not a *necessary* dependency for operation or understanding.
                    - **超越相似性**: 建议('s'、'S')可能仅表示相关主题,而不是操作或理解的*必要*依赖关系。
                *   **Focus on Functional Reliance**: Ask:
                    - **关注功能依赖**: 问:
                    *   Does the code in the *row file* directly **import, call, or inherit from** code in the *column file*? (Leads to '<' or 'x').
                        - *行文件*中的代码是否直接**从**列文件*中的代码**导入、调用或继承**?(导致 '<' 或 'x')。
                    *   Does the code in the *column file* directly **import, call, or inherit from** code in the *row file*? (Leads to '>' or 'x').
                        - *列文件*中的代码是否直接**从**行文件*中的代码**导入、调用或继承**?(导致 '>' 或 'x')。
                    *   Does the documentation in the *row file* **require information or definitions** present *only* in the *column file* to be complete or accurate? (Leads to '<' or 'd').
                        - *行文件*中的文档是否需要*仅*在*列文件*中存在的**信息或定义**才能完整或准确?(导致 '<' 或 'd')。
                    *   Is the *row file* **essential documentation** for understanding or implementing the concepts/code in the *column file*? (Leads to 'd' or potentially '>').
                        - *行文件*是否是理解或实现*列文件*中的概念/代码的**基本文档**?(导致 'd' 或潜在的 '>')。
                    *   Is there a **deep, direct conceptual link** where understanding or modifying one file *necessitates* understanding the other, even without direct code imports? (Consider '<', '>', 'x', or 'd' based on the nature of the link).
                        - 是否存在**深度、直接的概念链接**,即理解或修改一个文件*需要*理解另一个文件,即使没有直接的代码导入?(根据链接的性质考虑 '<'、'>'、'x' 或 'd')。
                *   **Purpose of Dependencies**: Remember, these verified dependencies guide the **Strategy phase** (determining task order) and the **Execution phase** (loading minimal necessary context). A dependency should mean "You *need* to consider/load the related file to work effectively on this one."
                    - **依赖关系的目的**: 请记住,这些经过验证的依赖关系指导**策略阶段**(确定任务顺序)和**执行阶段**(加载最小必要的上下文)。依赖关系应该意味着"您*需要*考虑/加载相关文件才能有效地处理此文件。"
                *   **Assign 'n' if No True Dependency**: If the relationship is merely thematic, uses similar terms, or is indirect, assign 'n' (verified no dependency). *It is better to mark 'n' than to create a weak dependency.*
                    - **如果没有真实依赖关系,则分配 'n'**: 如果关系仅仅是主题性的、使用相似的术语或是间接的,则分配 'n'(已验证无依赖)。*标记 'n' 比创建弱依赖关系更好。*
                *   **State Reasoning (MANDATORY)**: Before using `add-dependency`, **clearly state your reasoning** for the chosen dependency character (`<`, `>`, `x`, `d`, or `n`) for *each specific relationship* you intend to set, based on your direct file analysis and the functional reliance criteria.
                    - **陈述推理(强制)**: 在使用 `add-dependency` 之前,**清楚地陈述您为每个特定关系选择的依赖字符(`<`、`>`、`x`、`d` 或 `n`)的推理**,基于您的直接文件分析和功能依赖标准。
            *   **Correct/Confirm Dependencies**: Use `add-dependency`, specifying `--tracker <path_to_doc_tracker.md>`. The `--source-key` is always the `key_string` you are iterating on. The `--target-key` is the column key whose relationship you determined. Set the `--dep-type` based on your reasoned analysis. Batch multiple targets *for the same source key* if they share the *same new dependency type*.
                - **更正/确认依赖关系**: 使用 `add-dependency`,指定 `--tracker <path_to_doc_tracker.md>`。`--source-key` 始终是您正在迭代的 `key_string`。`--target-key` 是您确定其关系的列键。根据您的推理分析设置 `--dep-type`。如果多个目标共享*相同的新依赖类型*,则将它们批处理*用于同一源键*。
              ```bash
              # Example: Set '>' from 1A2 (source) to 2B1#3 (target) in doc_tracker.md
              # Reasoning: docs/setup.md (1A2) details steps required BEFORE using API described in docs/api/users.md (2B1). Thus, 2B1 depends on 1A2.
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key 1A2 --target-key 2B1#3 --dep-type ">"

              # Example: Set 'n' from 1A2 (source) to 3C1 and 3C2 (targets) in doc_tracker.md
              # Reasoning: Files 3C1 and 3C2 are unrelated examples; no functional dependency on setup guide 1A2.
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key 1A2 --target-key 3C1 3C2 --dep-type "n"
              ```
              ```bash
              # 示例: 在 doc_tracker.md 中从 1A2(源)到 2B1#3(目标)设置 '>'
              # 推理: docs/setup.md (1A2) 详细说明了使用 docs/api/users.md (2B1) 中描述的 API 之前所需的步骤。因此,2B1 依赖于 1A2。
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key 1A2 --target-key 2B1#3 --dep-type ">"

              # 示例: 在 doc_tracker.md 中从 1A2(源)到 3C1 和 3C2(目标)设置 'n'
              # 推理: 文件 3C1 和 3C2 是不相关的示例;对设置指南 1A2 没有功能依赖。
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key 1A2 --target-key 3C1 3C2 --dep-type "n"
              ```
        *   Repeat Step 2.B for all keys identified in Step 2.A.
            - 对步骤 2.A 中识别的所有键重复步骤 2.B。
    *   **C. Final Check**: Run `show-keys --tracker <path_to_doc_tracker.md>` again to confirm no `(checks needed: ...)` remain.
        - **C. 最终检查**: 再次运行 `show-keys --tracker <path_to_doc_tracker.md>` 以确认没有剩余 `(checks needed: ...)`。
    *   **MUP**: Perform MUP. Update `last_action`. State: "Completed verification for doc_tracker.md. Proceeding to find and verify mini-trackers."
        - **MUP**: 执行 MUP。更新 `last_action`。状态:"完成了 doc_tracker.md 的验证。正在继续查找和验证小型跟踪器。"

3.  **Stage 2: Find and Verify Mini-Trackers (`*_module.md`)**:
    3.  **第二阶段:查找和验证小型跟踪器(`*_module.md`)**:
    *   **A. Find Mini-Tracker Files**:
        - **A. 查找小型跟踪器文件**:
        *   **Goal**: Locate all `*_module.md` files within the project's code directories.
            - **目标**: 在项目的代码目录中定位所有 `*_module.md` 文件。
        *   **Get Code Roots**: Read the `[CODE_ROOT_DIRECTORIES]` list from `.clinerules`. If empty, state this and this stage cannot proceed.
            - **获取代码根**: 从 `.clinerules` 读取 `[CODE_ROOT_DIRECTORIES]` 列表。如果为空,说明这一点,此阶段无法继续。
        *   **Scan Directories**: For each code root directory, recursively scan its contents using `list_files` or similar directory traversal logic.
            - **扫描目录**: 对于每个代码根目录,使用 `list_files` 或类似的目录遍历逻辑递归扫描其内容。
        *   **Identify & Verify**: Identify files matching the pattern `{dirname}_module.md` where `{dirname}` exactly matches the name of the directory containing the file (e.g., `src/user_auth/user_auth_module.md`).
            - **识别和验证**: 识别匹配模式 `{dirname}_module.md` 的文件,其中 `{dirname}` 完全匹配包含文件的目录名称(例如 `src/user_auth/user_auth_module.md`)。
        *   **Create List**: Compile a list of the full, normalized paths to all valid mini-tracker files found.
            - **创建列表**: 编译找到的所有有效小型跟踪器文件的完整、规范化路径列表。
        *   **Report**: State the list of found mini-tracker paths. If none are found but code roots exist, state this and confirm that `analyze-project` ran successfully (as it should create them if modules exist). If none are found, proceed to Stage 3.
            - **报告**: 说明找到的小型跟踪器路径列表。如果没有找到但代码根目录存在,说明这一点并确认 `analyze-project` 成功运行(因为如果模块存在,它应该创建它们)。如果没有找到,继续进行第三阶段。
    *   **B. Iterate Through Mini-Trackers**: If mini-trackers were found:
        - **B. 遍历小型跟踪器**: 如果找到了小型跟踪器:
        *   Select the next mini-tracker path from the list. State which one you are processing.
            - 从列表中选择下一个小型跟踪器路径。说明您正在处理哪一个。
        *   **Repeat Verification Steps**: Follow the same sub-procedure as in Stage 1 (Steps 2.A and 2.B), but substitute the current mini-tracker path for `<path_to_doc_tracker.md>` in all commands (`show-keys`, `add-dependency`).
            - **重复验证步骤**: 遵循与第一阶段(步骤 2.A 和 2.B)相同的子程序,但在所有命令(`show-keys`、`add-dependency`)中用当前小型跟踪器路径替换 `<path_to_doc_tracker.md>`。
            *   **Identify Keys**: Use `show-keys --tracker <mini_tracker_path>`. List keys needing checks.
                - **识别键**: 使用 `show-keys --tracker <mini_tracker_path>`。列出需要检查的键。
            *   **Verify Keys**: Iterate through keys needing checks. Use `show-placeholders` to get a targeted list of unverified dependencies *within this mini-tracker*. Examine source/target files (`read_file`). State reasoning based on functional/conceptual reliance. Use `add-dependency --tracker <mini_tracker_path> --source-key <key_string> --target-key <target_key> --dep-type <char>`.
                - **验证键**: 遍历需要检查的键。使用 `show-placeholders` 获取*在此小型跟踪器内*的未验证依赖关系的有针对性列表。检查源/目标文件(`read_file`)。基于功能/概念依赖陈述推理。使用 `add-dependency --tracker <mini_tracker_path> --source-key <key_string> --target-key <target_key> --dep-type <char>`。
            ```bash
            python -m cline_utils.dependency_system.dependency_processor show-placeholders --tracker <mini_tracker_path> --key <key_string>
            ```
            *   **Foreign Keys**: Remember, when using `add-dependency` on a mini-tracker, the `--target-key` can be an external (foreign) key if it exists globally (Core Prompt Section VIII). Use this to link internal code to external docs or code in other modules if identified during analysis. State reasoning clearly.
                - **外部键**: 请记住,当在小型跟踪器上使用 `add-dependency` 时,如果 `--target-key` 在全局中存在(核心提示第八节),则可以是外部(外来)键。使用此键将内部代码链接到分析期间识别的其他模块中的外部文档或代码。清楚地陈述推理。
              ```bash
              # Example: Set 'd' from internal code file 1Ba2 to external doc 1Aa6 in agents_module.md
              # Reasoning: combat_agent.py (1Ba2) implements concepts defined in Multi-Agent_Collaboration.md (1Aa6), making doc essential.
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker src/agents/agents_module.md --source-key 1Ba2 --target-key 1Aa6 --dep-type "d"
              ```
              ```bash
              # 示例: 在 agents_module.md 中从内部代码文件 1Ba2 到外部文档 1Aa6 设置 'd'
              # 推理: combat_agent.py (1Ba2) 实现了 Multi-Agent_Collaboration.md (1Aa6) 中定义的概念,使文档变得重要。
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker src/agents/agents_module.md --source-key 1Ba2 --target-key 1Aa6 --dep-type "d"
              ```
            *   **Proactive External Links**: While analyzing file content, actively look for explicit references or clear conceptual reliance on *external* files (docs or other modules) missed by automation. Add these using `add-dependency` with the foreign key capability if a true dependency exists. State reasoning.
                - **主动外部链接**: 在分析文件内容时,主动查找对自动化遗漏的*外部*文件(文档或其他模块)的显式引用或明确的概念依赖。如果存在真实依赖关系,请使用外部键功能使用 `add-dependency` 添加这些链接。陈述推理。
        *   **C. Final Check (Mini-Tracker)**: Run `show-keys --tracker <mini_tracker_path>` again to confirm no `(checks needed: ...)` remain for *this mini-tracker*.
            - **C. 最终检查(小型跟踪器)**: 再次运行 `show-keys --tracker <mini_tracker_path>` 以确认*此小型跟踪器*没有剩余 `(checks needed: ...)`。
        *   Repeat Step 3.B and 3.C for all mini-trackers in the list found in Step 3.A.
            - 对步骤 3.A 中找到的列表中的所有小型跟踪器重复步骤 3.B 和 3.C。
    *   **MUP**: Perform MUP after verifying all mini-trackers found. Update `last_action`. State: "Completed verification for all identified mini-trackers. Proceeding to module_relationship_tracker.md."
        - **MUP**: 在验证所有找到的小型跟踪器后执行 MUP。更新 `last_action`。状态:"完成了所有识别的小型跟踪器的验证。正在继续处理 module_relationship_tracker.md。"

4.  **Stage 3: Verify `module_relationship_tracker.md`**:
    4.  **第三阶段:验证 `module_relationship_tracker.md`**:
    *   Follow the same verification sub-procedure as in Stage 1 (Steps 2.A, 2.B, 2.C), targeting `<path_to_module_relationship_tracker.md>` (likely `{memory_dir}/module_relationship_tracker.md`).
        - 遵循与第一阶段(步骤 2.A、2.B、2.C)相同的验证子程序,针对 `<path_to_module_relationship_tracker.md>`(可能是 `{memory_dir}/module_relationship_tracker.md`)。
        *   **Identify Keys**: Use `show-keys --tracker <path_to_module_relationship_tracker.md>`. List keys needing checks. If none, state this and verification is complete.
            - **识别键**: 使用 `show-keys --tracker <path_to_module_relationship_tracker.md>`。列出需要检查的键。如果没有,说明这一点,验证完成。
        *   **Verify Keys**: Iterate through keys needing checks.
            - **验证键**: 遍历需要检查的键。
            *   **Context**: Use `show-placeholders` to get the list of unverified module-level dependencies. When determining relationships here, rely heavily on the verified dependencies established *within* the mini-trackers during Stage 2, as well as the overall system architecture (`system_manifest.md`). A module-level dependency often arises because *some file within* module A depends on *some file within* module B. Read key module files/docs (`read_file`) only if mini-tracker context is insufficient.
                - **上下文**: 使用 `show-placeholders` 获取未验证的模块级依赖关系列表。在此处确定关系时,大量依赖第二阶段在小型跟踪器内建立的已验证依赖关系以及整体系统架构(`system_manifest.md`)。模块级依赖关系通常产生的原因是模块 A *内的某个文件*依赖于模块 B *内的某个文件*。仅在小型跟踪器上下文不足时读取关键模块文件/文档(`read_file`)。
            ```bash
            python -m cline_utils.dependency_system.dependency_processor show-placeholders --tracker <path_to_module_relationship_tracker.md> --key <key_string>
            ```
            *   **Determine Relationship & State Reasoning**: Base decision on aggregated dependencies from mini-trackers and high-level design intent.
                - **确定关系和陈述推理**: 基于来自小型跟踪器的聚合依赖关系和高级设计意图做出决定。
            *   **Correct/Confirm**: Use `add-dependency --tracker <path_to_module_relationship_tracker.md>` with appropriate arguments.
                - **更正/确认**: 使用带有适当参数的 `add-dependency --tracker <path_to_module_relationship_tracker.md>`。
        *   **Final Check**: Run `show-keys --tracker <path_to_module_relationship_tracker.md>` again to confirm no checks needed remain.
            - **最终检查**: 再次运行 `show-keys --tracker <path_to_module_relationship_tracker.md>` 以确认不再需要检查。
    *   **MUP**: Perform MUP after verifying `module_relationship_tracker.md`. Update `last_action`. State: "Completed verification for module_relationship_tracker.md. Proceeding to Code-Documentation Cross-Reference."
        - **MUP**: 在验证 `module_relationship_tracker.md` 后执行 MUP。更新 `last_action`。状态:"完成了 module_relationship_tracker.md 的验证。正在继续进行代码-文档交叉引用。"

*Keys must be set from each perspective, as each *row* has its own dependency list.*
*必须从每个角度设置键,因为每个*行*都有自己的依赖列表。*

5.  **Stage 4: Code-Documentation Cross-Reference (Adding 'd' links)**:
    5.  **第四阶段:代码-文档交叉引用(添加 'd' 链接)**:
    *   **Objective**: Systematically review code components and ensure they have explicit dependencies pointing to all essential documentation required for their understanding or implementation. This happens *after* initial placeholders/suggestions ('p', 's', 'S') are resolved in Stages 1-3.
        - **目标**: 系统地审查代码组件,并确保它们具有指向理解或实现所需的所有基本文档的显式依赖关系。这在第一至第三阶段中解决了初始占位符/建议('p'、's'、'S')*之后*发生。
    *   **A. Identify Code and Doc Keys**:
        - **A. 识别代码和文档键**:
        *   Use `show-keys` on relevant trackers (mini-trackers, main tracker) to get lists of code keys.
            - 在相关跟踪器(小型跟踪器、主跟踪器)上使用 `show-keys` 获取代码键列表。
        *   Use `show-keys --tracker <path_to_doc_tracker.md>` to get a list of documentation keys.
            - 使用 `show-keys --tracker <path_to_doc_tracker.md>` 获取文档键列表。
        *The output keys might be `KEY` or `KEY#GI`. You need to resolve these to their specific global `KeyInfo` objects (paths and base keys) to perform the conceptual matching.*
        *输出键可能是 `KEY` 或 `KEY#GI`。您需要将这些解析为其特定的全局 `KeyInfo` 对象(路径和基础键)以执行概念匹配。*
        *   *(Alternatively, use internal logic based on `ConfigManager` and the global key map if more efficient)*.
            - *(或者,如果更有效,则使用基于 `ConfigManager` 和全局键映射的内部逻辑)*。
    *   **B. Iterate Through Code Keys**:
        - **B. 遍历代码键**:
        *   Select a code key (e.g., `code_key_string` representing a specific code file).
            - 选择一个代码键(例如,代表特定代码文件的 `code_key_string`)。
        *   **Identify Potential Docs**: Determine which documentation keys (`doc_key_string`) are potentially relevant to `code_key_string`. Consider:
            - **识别潜在文档**: 确定哪些文档键(`doc_key_string`)可能与 `code_key_string` 相关。考虑:
            *   The module the code belongs to.
                - 代码所属的模块。
            *   Functionality described in the code file (`read_file <code_file_path>`).
                - 代码文件中描述的功能(`read_file <code_file_path>`)。
            *   Existing dependencies shown by `show-dependencies --key <code_key_string>`.
                - `show-dependencies --key <code_key_string>` 显示的现有依赖关系。
            *   Look for comments in the code referencing specific documentation.
                - 查找引用特定文档的代码注释。
            *   Ask questions like, "Does this documentation provide valuable or useful information for understanding how the code is intended to operate?", and "Does the code need to be aware of this information to perform its intended function?".
                - 问诸如"此文档是否为理解代码的预期运行方式提供有价值或有用的信息?"以及"代码是否需要了解这些信息才能执行其预期功能?"之类的问题。
            *    Conceptual links and future planned directions should be considered as well. The more information available to inform how the code operates in relation to the systems, the higher quality the end result will be.
                - 还应考虑概念链接和未来计划方向。更多的可用信息来说明代码如何与系统相关运行,最终结果的质量就越高。
        *   **Examine Relevant Docs**: Use `read_file` to examine the content of the potentially relevant documentation files.
            - **检查相关文档**: 使用 `read_file` 检查可能相关的文档文件的内容。
        *   **Determine Essential Documentation**: For each potential `doc_key_string`, decide if it provides *essential* context, definitions, specifications, or explanations required to understand, implement, or correctly use the code represented by `code_key_string`. This is more than just keyword similarity.
            - **确定基本文档**: 对于每个潜在的 `doc_key_string`,确定它是否提供理解、实现或正确使用 `code_key_string` 表示的代码所需的*基本*上下文、定义、规范或解释。这不仅仅是关键字相似性。
        *   **Add Dependencies (Bi-directionally)**: If `doc_key_string` is essential for `code_key_string`:
            - **添加依赖关系(双向)**: 如果 `doc_key_string` 对 `code_key_string` 是基本的:
            *   **State Reasoning (Mandatory)**: Explain *why* the documentation is essential for the code.
                - **陈述推理(强制)**: 解释*为什么*文档对代码是必要的。
            *   **Add Code -> Doc Link**: Use `add-dependency` targeting the tracker most relevant to the *code file*.
                - **添加代码 -> 文档链接**: 使用 `add-dependency` 定位到与*代码文件*最相关的跟踪器。
                ```bash
                # Reasoning: [Explain why doc_key_string is essential for code_key_string]
                python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <code_file_tracker_path> --source-key <code_key_string> --target-key <doc_key_string> --dep-type "<dep_char>"
                ```
                ```bash
                # 推理: [解释为什么 doc_key_string 对 code_key_string 是必要的]
                python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <code_file_tracker_path> --source-key <code_key_string> --target-key <doc_key_string> --dep-type "<dep_char>"
                ```
            *   **Add Doc -> Code Link**: Use `add-dependency` targeting `doc_tracker.md`.
                - **添加文档 -> 代码链接**: 使用 `add-dependency` 定位到 `doc_tracker.md`。
                ```bash
                # Reasoning: [Same reasoning as above, from doc's perspective]
                python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key <doc_key_string> --target-key <code_key_string> --dep-type "<dep_char>"
                ```
                ```bash
                # 推理: [与上述相同的推理,从文档的角度]
                python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key <doc_key_string> --target-key <code_key_string> --dep-type "<dep_char>"
                ```
        *   Repeat for all relevant documentation keys for the current `code_key_string`.
            - 对当前 `code_key_string` 的所有相关文档键重复此操作。
    *   **C. Repeat for All Code Keys**: Continue Step 5.B until all relevant code keys have been reviewed against the documentation corpus.
        - **C. 对所有代码键重复**: 继续步骤 5.B,直到所有相关代码键都已根据文档语料库进行了审查。
    *   **MUP**: Perform MUP. Update `last_action`. State: "Completed Code-Documentation Cross-Reference."
        - **MUP**: 执行 MUP。更新 `last_action`。状态:"完成了代码-文档交叉引用。"

6.  **Completion**: Once all four stages are complete and `show-keys` reports no `(checks needed: ...)` for `doc_tracker.md`, all mini-trackers, and `module_relationship_tracker.md`, the tracker verification part of Set-up/Maintenance is done. Check if all other phase exit criteria (Section I) are met (e.g., core files exist, code/doc roots identified, system manifest populated). If so, prepare to exit the phase by updating `.clinerules` as per Section I.
    6.  **完成**: 当所有四个阶段都完成,并且 `show-keys` 报告 `doc_tracker.md`、所有小型跟踪器和 `module_relationship_tracker.md` 没有 `(checks needed: ...)`,则设置/维护阶段的跟踪器验证部分完成。检查是否满足所有其他阶段退出标准(第一节)(例如,核心文件存在,代码/文档根目录已识别,系统清单已填充)。如果是这样,请按照第一节更新 `.clinerules` 准备退出阶段。

*If a dependency is detected in **either** direction 'n' should not be used. Choose the best character to represent the directional dependency or 'd' if it is a more general documentation dependency.*
*如果在**任一**方向检测到依赖关系,则不应使用 'n'。选择最佳字符来表示方向依赖关系,如果是更通用的文档依赖关系,则使用 'd'。*

## IV. Set-up/Maintenance Dependency Workflow Diagram
## IV. 设置/维护依赖工作流程图

```mermaid
graph TD
    A[Start Set-up/Maintenance Verification] --> B(Run analyze-project);
    B --> C[Stage 1: Verify doc_tracker.md];

    subgraph Verify_doc_tracker [Stage 1: doc_tracker.md]
        C1[Use show-keys --tracker doc_tracker.md] --> C2{Checks Needed?};
        C2 -- Yes --> C3[Identify Key(s)];
        C3 --> C4[For Each Key needing check:];
        C4 --> C5(Run show-placeholders --tracker doc_tracker.md --key [key]);
        C5 --> C6(Plan Reading / Suggest Batch);
        C6 --> C7(Read Source + Target Files);
        C7 --> C8(Determine Relationship & State Reasoning);
        C8 --> C9(Use add-dependency --tracker doc_tracker.md);
        C9 --> C4;
        C4 -- All Keys Done --> C10[Final Check: show-keys];
        C2 -- No --> C10[doc_tracker Verified];
    end

    C --> Verify_doc_tracker;
    C10 --> D[MUP after Stage 1];

    D --> E[Stage 2: Find & Verify Mini-Trackers];
    subgraph Find_Verify_Minis [Stage 2: Mini-Trackers (`*_module.md`)]
        E1[Identify Code Roots from .clinerules] --> E2[Scan Code Roots Recursively];
        E2 --> E3[Find & Verify *_module.md Files];
        E3 --> E4[Compile List of Mini-Tracker Paths];
        E4 --> E5{Any Mini-Trackers Found?};
        E5 -- Yes --> E6[Select Next Mini-Tracker];
        E6 --> E7[Use show-keys --tracker <mini_tracker>];
        E7 --> E8{Checks Needed?};
        E8 -- Yes --> E9[Identify Key(s)];
        E9 --> E10[For Each Key needing check:];
        E10 --> E11(Run show-placeholders --tracker [mini_tracker] --key [key]);
        E11 --> E12(Plan Reading / Suggest Batch);
        E12 --> E13(Read Source + Target Files);
        E13 --> E14(Determine Relationship & State Reasoning - Consider Foreign Keys/External);
        E14 --> E15(Use add-dependency --tracker <mini_tracker>);
        E15 --> E10;
        E10 -- All Keys Done --> E16[Final Check: show-keys];
        E8 -- No --> E16[Mini-Tracker Verified];
        E16 --> E17{All Mini-Trackers Checked?};
        E17 -- No --> E6;
        E17 -- Yes --> E18[All Mini-Trackers Verified];
        E5 -- No --> E18; // Skip if no minis found
    end

    E --> Find_Verify_Minis;
    E18 --> F[MUP after Stage 2];

    F --> G[Stage 3: Verify module_relationship_tracker.md];
    subgraph Verify_main_tracker [Stage 3: module_relationship_tracker.md]
        G1[Use show-keys --tracker module_relationship_tracker.md] --> G2{Checks Needed?};
        G2 -- Yes --> G3[Identify Key(s)];
        G3 --> G4[For Each Key needing check:];
        G4 --> G5(Run show-placeholders --tracker module_relationship_tracker.md --key [key]);
        G5 --> G6(Plan Reading / Use Mini-Tracker Context / Read Key Module Files);
        G6 --> G7(Determine Relationship & State Reasoning - Module Level);
        G7 --> G8(Use add-dependency --tracker module_relationship_tracker.md);
        G8 --> G4;
        G4 -- All Keys Done --> G9[Final Check: show-keys];
        G2 -- No --> G9[Main Tracker Verified];
    end

    G --> Verify_main_tracker;
    G9 --> H[MUP after Stage 3];

    H --> J[Stage 4: Code-Documentation Cross-Ref];
    subgraph CodeDocRef [Stage 4: Code-Doc Cross-Ref]
        J1[Identify Code & Doc Keys] --> J2[For Each Code Key:];
        J2 --> J3(Identify Potential Docs);
        J3 --> J4(Read Code & Docs);
        J4 --> J5(Determine Essential Docs & Reason);
        J5 -- Yes --> J6(add-dependency -> tracker);
        J6 --> J2;
        J5 -- No --> J2;
        J2 -- All Code Keys Done --> J7[Stage 4 Complete];
    end

    J --> CodeDocRef;
    J7 --> K[MUP after Stage 4];
    K --> L[End Verification Process - Check All Exit Criteria (Section I)];

    style Verify_doc_tracker fill:#e6f7ff,stroke:#91d5ff
    style Find_Verify_Minis fill:#f6ffed,stroke:#b7eb8f
    style Verify_main_tracker fill:#fffbe6,stroke:#ffe58f
```
代码说明: This workflow diagram illustrates the Set-up/Maintenance verification process, showing the four stages of tracker verification (doc_tracker, mini-trackers, module_relationship_tracker, and code-document cross-reference) with their specific steps and MUP checkpoints.
代码说明: 此工作流程图说明了设置/维护验证过程,显示了跟踪器验证的四个阶段(doc_tracker、小型跟踪器、module_relationship_tracker 和代码-文档交叉引用)及其特定步骤和 MUP 检查点。

## V. Locating and Understanding Mini-Trackers
## V. 定位和理解小型跟踪器

**Purpose**: Mini-trackers (`{dirname}_module.md`) serve a dual role:
**目的**: 小型跟踪器(`{dirname}_module.md`)具有双重作用:
1.  **HDTA Domain Module**: They contain the descriptive text for the module (purpose, components, etc.), managed manually during Strategy.
    1.  **HDTA 域模块**: 它们包含模块的描述性文本(目的、组件等),在策略期间手动管理。
2.  **Dependency Tracker**: They track file/function-level dependencies *within* that module and potentially *to external* files/docs. The dependency grid is managed via `dependency_processor.py` commands.
    2.  **依赖跟踪器**: 它们跟踪该模块*内*以及潜在*到外部*文件/文档的文件/函数级依赖关系。依赖网格通过 `dependency_processor.py` 命令管理。

**Locating Mini-Trackers:**
**定位小型跟踪器:**
1.  **Get Code Roots**: Read the `[CODE_ROOT_DIRECTORIES]` list from `.clinerules`. These are the top-level directories containing project source code.
    1.  **获取代码根**: 从 `.clinerules` 读取 `[CODE_ROOT_DIRECTORIES]` 列表。这些是包含项目源代码的顶级目录。
2.  **Scan Code Roots**: For each directory listed in `[CODE_ROOT_DIRECTORIES]`:
    2.  **扫描代码根**: 对于 `[CODE_ROOT_DIRECTORIES]` 中列出的每个目录:
    *   Recursively scan its contents.
        - 递归扫描其内容。
    *   Look for files matching the pattern `{dirname}_module.md`, where `{dirname}` is the exact name of the directory containing the file.
        - 查找匹配模式 `{dirname}_module.md` 的文件,其中 `{dirname}` 是包含文件的目录的确切名称。
    *   Example: In `src/auth/`, look for `auth_module.md`. In `src/game/state/`, look for `state_module.md`.
        - 示例: 在 `src/auth/` 中,查找 `auth_module.md`。在 `src/game/state/` 中,查找 `state_module.md`。
3.  **Compile List**: Create a list of the full, normalized paths to all valid mini-tracker files found. This list will be used in Section III when it's time to verify mini-trackers.
    3.  **编译列表**: 创建找到的所有有效小型跟踪器文件的完整、规范化路径列表。此列表将在第三节验证小型跟踪器时使用。

**Creation and Verification**:
**创建和验证:**
*   **Creation/Update**: The `analyze-project` command (run in Section II.4 and potentially before Section III) automatically creates `{dirname}_module.md` files for detected modules if they don't exist, or updates the dependency grid within them if they do. It populates the grid with keys and initial placeholders/suggestions.
    - **创建/更新**: `analyze-project` 命令(在第二节.4 中运行,并可能在第三节之前运行)会自动为检测到的模块创建 `{dirname}_module.md` 文件(如果不存在),或更新其中的依赖网格(如果存在)。它使用键和初始占位符/建议填充网格。
*   **Verification**: The detailed verification process in **Section III** is used to resolve placeholders ('p', 's', 'S') within these mini-trackers *after* `doc_tracker.md` is verified and *before* `module_relationship_tracker.md` is verified. Use the list compiled above to iterate through the mini-trackers during that stage.
    - **验证**: **第三节**中的详细验证过程用于在验证 `doc_tracker.md` *之后*和验证 `module_relationship_tracker.md` *之前*解决这些小型跟踪器中的占位符('p'、's'、'S')。使用上面编译的列表在该阶段遍历小型跟踪器。

## VI. Set-up/Maintenance Plugin - MUP Additions
## VI. 设置/维护插件 - MUP 附加内容

After performing the Core MUP steps (Core Prompt Section VI):
在执行核心 MUP 步骤(核心提示第六节)后:
1.  **Update `system_manifest.md` (If Changed)**: If Set-up actions modified the project structure significantly (e.g., adding a major module requiring a mini-tracker), ensure `system_manifest.md` reflects this, potentially adding the new module.
    1.  **更新 `system_manifest.md`(如果更改)**: 如果设置操作显著修改了项目结构(例如,添加需要小型跟踪器的主要模块),确保 `system_manifest.md` 反映这一点,可能添加新模块。
2.  **Update `.clinerules` [LAST_ACTION_STATE]:** Update `last_action`, `current_phase`, `next_action`, `next_phase` to reflect the specific step completed within this phase. Examples:
    2.  **更新 `.clinerules` [LAST_ACTION_STATE]**: 更新 `last_action`、`current_phase`、`next_action`、`next_phase` 以反映在此阶段内完成的特定步骤。示例:
    *   After identifying roots:
        - 识别根目录之后:
        ```
        last_action: "Identified Code and Doc Roots"
        current_phase: "Set-up/Maintenance"
        next_action: "Initialize Core Files / Run analyze-project"
        next_phase: "Set-up/Maintenance"
        ```
        ```
        last_action: "Identified Code and Doc Roots"
        current_phase: "Set-up/Maintenance"
        next_action: "Initialize Core Files / Run analyze-project"
        next_phase: "Set-up/Maintenance"
        ```
    *   After initial `analyze-project`:
        - 初始 `analyze-project` 之后:
        ```
        last_action: "Ran analyze-project, Initialized Trackers"
        current_phase: "Set-up/Maintenance"
        next_action: "Verify doc_tracker.md Dependencies"
        next_phase: "Set-up/Maintenance"
        ```
        ```
        last_action: "Ran analyze-project, Initialized Trackers"
        current_phase: "Set-up/Maintenance"
        next_action: "Verify doc_tracker.md Dependencies"
        next_phase: "Set-up/Maintenance"
        ```
    *   After verifying `doc_tracker.md`:
        - 验证 `doc_tracker.md` 之后:
        ```
        last_action: "Verified doc_tracker.md"
        current_phase: "Set-up/Maintenance"
        next_action: "Verify Mini-Trackers"
        next_phase: "Set-up/Maintenance"
        ```
        ```
        last_action: "Verified doc_tracker.md"
        current_phase: "Set-up/Maintenance"
        next_action: "Verify Mini-Trackers"
        next_phase: "Set-up/Maintenance"
        ```
    *   After verifying the last tracker:
        - 验证最后一个跟踪器之后:
        ```
        last_action: "Completed All Tracker Verification"
        current_phase: "Set-up/Maintenance"
        next_action: "Perform Code-Documentation Cross-Reference"
        next_phase: "Set-up/Maintenance"
        ```
        ```
        last_action: "Completed All Tracker Verification"
        current_phase: "Set-up/Maintenance"
        next_action: "Perform Code-Documentation Cross-Reference"
        next_phase: "Set-up/Maintenance"
        ```
    *   After completing Code-Documentation Cross-Reference:
        - 完成代码-文档交叉引用后:
        ```
        last_action: "Completed Code-Documentation Cross-Reference ('d' links added)"
        current_phase: "Set-up/Maintenance"
        next_action: "Phase Complete - User Action Required"
        next_phase: "Strategy"
        ```
        ```
        last_action: "Completed Code-Documentation Cross-Reference ('d' links added)"
        current_phase: "Set-up/Maintenance"
        next_action: "Phase Complete - User Action Required"
        next_phase: "Strategy"
        ```
