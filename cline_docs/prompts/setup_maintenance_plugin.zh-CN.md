# **Cline 递归思维链系统 (CRCT) - 设置/维护插件**

**本插件为 CRCT 系统的设置/维护阶段提供详细指令和流程。应与核心系统提示词结合使用。**

## I. 进入和退出设置/维护阶段

**进入设置/维护阶段：**
1.  **初始状态**：对于新项目或如果 `.clinerules` 显示 `next_phase: "Set-up/Maintenance"`，从这里开始。
2.  **`.clinerules` 检查**：始终首先读取 `.clinerules`。如果 `[LAST_ACTION_STATE]` 指示 `current_phase: "Set-up/Maintenance"` 或 `next_phase: "Set-up/Maintenance"`，则按这些指令执行，如果指定了 `next_action`，则从中恢复。
3.  **新项目**：如果 `.clinerules` 缺失/为空，假定此阶段，创建 `.clinerules`（参见第 II 节），并初始化其他核心文件。

**退出设置/维护阶段：**
1.  **完成标准：**
    *   所有核心文件都存在并已初始化（第 II 节）。
    *   `.clinerules` 中的 `[CODE_ROOT_DIRECTORIES]` 和 `[DOC_DIRECTORIES]` 已填充（核心提示词第 X 和 XI 节）。
    *   `doc_tracker.md` 存在且没有剩余的 'p'、's' 或 'S' 占位符（通过第 III 节阶段 1 中的 `show-keys` 验证）。
    *   所有迷你追踪器（`*_module.md`）都存在且没有剩余的 'p'、's' 或 'S' 占位符（通过第 III 节阶段 2 中的 `show-keys` 验证）。
    *   `module_relationship_tracker.md` 存在且没有剩余的 'p'、's' 或 'S' 占位符（通过第 III 节阶段 3 中的 `show-keys` 验证）。
    *   **代码-文档交叉引用完成（第 III 节，阶段 4），确保添加了必要的 'd' 链接。**
    *   `system_manifest.md` 已创建并填充（至少从模板最低限度填充）。
    *   根据需要通过 `analyze-project` 创建/填充迷你追踪器。
2.  **`.clinerules` 更新（MUP）：** 一旦满足所有标准，按如下方式更新 `[LAST_ACTION_STATE]`：
    ```
    last_action: "Completed Set-up/Maintenance Phase"
    current_phase: "Set-up/Maintenance"
    next_action: "Phase Complete - User Action Required"
    next_phase: "Strategy"
    ```
3.  **用户操作**：更新 `.clinerules` 后，暂停以便用户触发下一个会话/阶段。参考核心系统提示词第 III 节的阶段过渡检查清单。

## II. 初始化核心必需文件和项目结构

**操作**：确保所有核心文件都存在，如果缺失，则根据核心系统提示词（第 II 节）中的规范触发它们的创建。

**流程：**
1.  **检查是否存在**：检查核心提示词第 II 节中列出的每个必需文件（`.clinerules`、`system_manifest.md`、`activeContext.md`、`module_relationship_tracker.md`、`changelog.md`、`doc_tracker.md`、`userProfile.md`、`progress.md`）是否在其指定位置存在。
2.  **识别代码和文档目录**：如果 `.clinerules` 中的 `[CODE_ROOT_DIRECTORIES]` 或 `[DOC_DIRECTORIES]` 为空或缺失，**停止**其他初始化，并遵循核心提示词第 X 和 XI 节中的流程来首先识别和填充这些部分。更新 `.clinerules` 并执行 MUP。之后恢复初始化检查。
3.  **触发缺失文件的创建：**
    *   **手动创建文件**（`.clinerules`、`activeContext.md`、`changelog.md`、`userProfile.md`、`progress.md`）：如果缺失，使用 `write_to_file` 创建它们，并使用核心提示词第 II 节表中描述的最少占位符内容。说明："文件 `{file_path}` 缺失。使用占位符内容创建。"
        *   初始 `.clinerules` 示例（如果创建）：
            ```
            [LAST_ACTION_STATE]
            last_action: "System Initialized"
            current_phase: "Set-up/Maintenance"
            next_action: "Initialize Core Files" # 或者如果首先需要，则为 Identify Code/Doc Roots
            next_phase: "Set-up/Maintenance"

            [CODE_ROOT_DIRECTORIES]
            # 待识别

            [DOC_DIRECTORIES]
            # 待识别

            [LEARNING_JOURNAL]
            -
            ```
    *   **基于模板的文件**（`system_manifest.md`）：如果缺失，首先使用 `write_to_file` 在 `{memory_dir}/` 中创建一个名为 `system_manifest.md` 的空文件。说明："文件 `system_manifest.md` 缺失。创建空文件。" 然后，从 `cline_docs/templates/system_manifest_template.md` 读取模板内容，并再次使用 `write_to_file` 用模板内容*覆盖*空的 `system_manifest.md`。说明："使用模板内容填充 `system_manifest.md`。"
    *   **追踪器文件**（`module_relationship_tracker.md`、`doc_tracker.md` 和迷你追踪器 `*_module.md`）：
        *   **不要手动创建。**
        *   如果这些中的任何一个缺失，或者如果发生了重大项目更改，或者如果你正在开始验证，运行 `analyze-project`。此命令将根据当前项目结构和识别的代码/文档根目录创建或更新所有必要的追踪器。
        ```bash
        # 确保首先在 .clinerules 中设置代码/文档根目录！
        python -m cline_utils.dependency_system.dependency_processor analyze-project
        ```
        *   说明："追踪器文件缺失或需要更新。运行 `analyze-project` 以创建/更新追踪器。"
        *   *（运行 `analyze-project` 也是第 III 节中验证工作流程的第一步）*。
        *   *（如果需要，可选：添加 `--force-analysis` 或 `--force-embeddings`）*。
        *   *（模块目录中的迷你追踪器也由 `analyze-project` 创建/更新）*。
4.  **MUP**：在创建文件或运行 `analyze-project` 后，遵循核心提示词 MUP（第 VI 节）和下面的第 V 节添加。更新 `[LAST_ACTION_STATE]` 以反映进度（例如，`next_action: "Verify Tracker Dependencies"`）。

## III. 分析和验证追踪器依赖项（有序工作流程）

**不要在相关文件读取之前假设依赖项！！**

**目标**：通过系统地解析占位符（'p'）和验证建议（'s'、'S'），然后进行显式的代码到文档交叉引用步骤，确保追踪器准确反映项目依赖项。**此过程必须遵循特定顺序：**
1.  `doc_tracker.md`（占位符/建议解析）
2.  所有迷你追踪器（`*_module.md`）（占位符/建议解析）
3.  `module_relationship_tracker.md`（占位符/建议解析）
4.  **代码-文档交叉引用**（添加显式依赖项）

此顺序至关重要，因为迷你追踪器捕获模块内详细的跨目录依赖项，这对于准确确定 `module_relationship_tracker.md` 中更高级别的模块到模块关系至关重要。

**重要**：
*   **所有追踪器修改必须使用 `dependency_processor.py` 命令。** 参见核心提示词第 VIII 节的命令详细信息。
*   **不要直接读取追踪器文件**以获取依赖项信息；使用 `show-keys` 和 `show-dependencies`。
*   如果自上次运行以来发生了重大代码/文档更改，或者在进入此阶段时（如第 II 节所做），在开始此验证过程之前运行 `analyze-project`。

***关键强调***：*关键是文档要**详尽地**与代码交叉引用。如果未将定义代码的文档列为依赖项，则无法正确完成代码。以下验证阶段，特别是阶段 4，旨在实现这一目标。*

**此阶段不是关于效率，而是关于*准确性*。这是一项基础工作。如果此阶段的准确性低，整个项目都会受到影响。**

**流程：**

1.  **运行项目分析（初始和更新）**：
    *   使用 `analyze-project` 自动生成/更新键、分析文件、建议依赖项（'p'、's'、'S'），并更新*所有*追踪器（`module_relationship_tracker.md`、`doc_tracker.md` 和迷你追踪器）。此命令如果追踪器不存在则创建它们，并根据当前代码/文档和配置填充/更新网格。
    ```bash
    python -m cline_utils.dependency_system.dependency_processor analyze-project
    ```
    *   *（如果需要，可选：添加 `--force-analysis` 或 `--force-embeddings`，例如，如果配置更改或缓存似乎过时）*。
    *   **审查日志（`debug.txt`、`suggestions.log`）** 以获取分析详细信息和建议的更改，但优先考虑下面的验证工作流程。说明："运行 analyze-project。审查日志并继续有序验证。"

2.  **阶段 1：验证 `doc_tracker.md`**：
    *   **A. 识别需要验证的键**：
        *   为 `doc_tracker.md` 运行 `show-keys`：
          ```bash
          python -m cline_utils.dependency_system.dependency_processor show-keys --tracker <path_to_doc_tracker.md>
          ```
          *（使用实际路径，根据配置可能是 `{memory_dir}/doc_tracker.md`）*
        *   检查输出。列出的键可能是基础键（例如，"1A1"）或全局实例化键（例如，"2B1#1"），如果它们的基础键字符串用于项目中的多个不同路径。识别所有以 `(checks needed: ...)` 结尾的行。这表示该键在*此追踪器内*的行中存在未解析的 'p'、's' 或 'S' 字符。
        *   为 `doc_tracker.md` 创建这些需要验证的键的列表。如果没有，说明这一点并继续阶段 2。
    *   **B. 验证已识别键的占位符/建议**：
        *   遍历步骤 2.A 中的键列表。
        *   对于每个 `key_string`（行键）：
            *   **获取上下文**：运行 `show-placeholders`，针对当前追踪器和键。此命令专门列出给定键*在此追踪器内*的 'p'、's' 和 'S' 关系，提供验证的目标列表。
            ```bash
            python -m cline_utils.dependency_system.dependency_processor show-placeholders --tracker <path_to_doc_tracker.md> --key <key_string>
            ```
            *   **计划读取**：识别源文件（对于 `key_string`）和相关的目标文件（对于需要验证的列键）。为了提高效率，计划在下一步中一起读取源文件和*多个*相关目标文件。如果文件位于同一位置，建议批量读取（例如，"建议读取源文件 X 和来自同一目录的目标文件 Y、Z。你能提供文件夹内容还是我应该使用 `read_file` 单独读取？"）。注意上下文限制。
            *   **检查文件**：使用 `read_file` 检查源文件和识别的相关目标文件/文件夹的内容。
            *   **确定关系（关键步骤）**：根据文件内容，确定源（`key_string`）和每个正在验证的目标键之间的**真实功能或本质概念关系**。
                *   **超越相似性**：建议（'s'、'S'）可能只表示相关主题，而不是操作或理解所*必需*的依赖项。
            *   **关注功能依赖**：询问：
                *   *行文件*中的代码是否直接**从***列文件*中的代码导入、调用或继承？（导致 '<' 或 'x'）。
                *   *列文件*中的代码是否直接**从***行文件*中的代码导入、调用或继承？（导致 '>' 或 'x'）。
                *   *行文件*中的文档是否**需要***列文件*中*仅*存在的信息或定义才能完整或准确？（导致 '<' 或 'd'）。
                *   *行文件*是否是理解或实现*列文件*中的概念/代码的**必要文档**？（导致 'd' 或可能 '>'）。
                *   是否存在**深刻、直接的概念链接**，其中理解或修改一个文件*需要*理解另一个文件，即使没有直接的代码导入？（根据链接的性质考虑 '<'、'>'、'x' 或 'd'）。
            *   **依赖项的目的**：记住，这些已验证的依赖项指导**策略阶段**（确定任务顺序）和**执行阶段**（加载最少必要的上下文）。依赖项应该意味着"你*需要*考虑/加载相关文件才能有效地处理此文件。"
            *   **如果没有真实依赖项，分配 'n'**：如果关系仅仅是主题性的、使用类似术语的或间接的，分配 'n'（已验证无依赖项）。*标记 'n' 总比创建弱依赖项好。*
            *   **说明推理（强制性）**：在使用 `add-dependency` 之前，根据你的直接文件分析和功能依赖标准，**清楚地说明你为*每个特定关系*选择的依赖项字符（`<`、`>`、`x`、`d` 或 `n`）的推理**。
        *   **更正/确认依赖项**：使用 `add-dependency`，指定 `--tracker <path_to_doc_tracker.md>`。`--source-key` 始终是你正在迭代的 `key_string`。`--target-key` 是你确定其关系的列键。根据你的推理分析设置 `--dep-type`。如果它们共享*相同的新依赖项类型*，则为*相同的源键*批量处理多个目标。
              ```bash
              # 示例：在 doc_tracker.md 中将 '>' 从 1A2（源）设置为 2B1#3（目标）
              # 推理：docs/setup.md（1A2）详细说明了在使用 docs/api/users.md（2B1）中描述的 API 之前所需的步骤。因此，2B1 依赖于 1A2。
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key 1A2 --target-key 2B1#3 --dep-type ">"

              # 示例：在 doc_tracker.md 中将 'n' 从 1A2（源）设置为 3C1 和 3C2（目标）
              # 推理：文件 3C1 和 3C2 是无关的示例；与设置指南 1A2 没有功能依赖关系。
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key 1A2 --target-key 3C1 3C2 --dep-type "n"
              ```
        *   对步骤 2.A 中识别的所有键重复步骤 2.B。
    *   **C. 最终检查**：再次运行 `show-keys --tracker <path_to_doc_tracker.md>` 以确认没有剩余的 `(checks needed: ...)`。
    *   **MUP**：执行 MUP。更新 `last_action`。说明："完成 doc_tracker.md 的验证。继续查找和验证迷你追踪器。"

3.  **阶段 2：查找和验证迷你追踪器（`*_module.md`）**：
    *   **A. 查找迷你追踪器文件**：
        *   **目标**：在项目的代码目录中找到所有 `*_module.md` 文件。
        *   **获取代码根目录**：从 `.clinerules` 读取 `[CODE_ROOT_DIRECTORIES]` 列表。如果为空，说明这一点，此阶段无法继续。
        *   **扫描目录**：对于每个代码根目录，使用 `list_files` 或类似的目录遍历逻辑递归扫描其内容。
        *   **识别并验证**：识别匹配模式 `{dirname}_module.md` 的文件，其中 `{dirname}` 与包含该文件的目录的名称完全匹配（例如，`src/user_auth/user_auth_module.md`）。
        *   **创建列表**：编译所有找到的有效迷你追踪器文件的完整、规范化路径列表。
        *   **报告**：说明找到的迷你追踪器路径列表。如果没有找到但代码根目录存在，说明这一点并确认 `analyze-project` 成功运行（因为如果模块存在，它应该创建它们）。如果没有找到，继续阶段 3。
    *   **B. 遍历迷你追踪器**：如果找到迷你追踪器：
        *   从列表中选择下一个迷你追踪器路径。说明你正在处理哪一个。
        *   **重复验证步骤**：遵循与阶段 1 相同的子流程（步骤 2.A 和 2.B），但在所有命令（`show-keys`、`add-dependency`）中将当前迷你追踪器路径替换为 `<path_to_doc_tracker.md>`。
            *   **识别键**：使用 `show-keys --tracker <mini_tracker_path>`。列出需要检查的键。
            *   **验证键**：遍历需要检查的键。使用 `show-placeholders` 获取*此迷你追踪器内*未验证依赖项的目标列表。检查源/目标文件（`read_file`）。根据功能/概念依赖说明推理。使用 `add-dependency --tracker <mini_tracker_path> --source-key <key_string> --target-key <target_key> --dep-type <char>`。
            ```bash
            python -m cline_utils.dependency_system.dependency_processor show-placeholders --tracker <mini_tracker_path> --key <key_string>
            ```
            *   **外键**：记住，当在迷你追踪器上使用 `add-dependency` 时，如果 `--target-key` 全局存在（核心提示词第 VIII 节），则可以是外部（外键）键。如果在分析期间识别，使用此方法将内部代码链接到其他模块中的外部文档或代码。清楚地说明推理。
              ```bash
              # 示例：在 agents_module.md 中将 'd' 从内部代码文件 1Ba2 设置为外部文档 1Aa6
              # 推理：combat_agent.py（1Ba2）实现了 Multi-Agent_Collaboration.md（1Aa6）中定义的概念，使文档成为必要的。
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker src/agents/agents_module.md --source-key 1Ba2 --target-key 1Aa6 --dep-type "d"
              ```
            *   **主动外部链接**：在分析文件内容时，主动寻找对自动化遗漏的*外部*文件（文档或其他模块）的显式引用或清晰的概念依赖。如果存在真实依赖项，使用外键功能使用 `add-dependency` 添加这些。说明推理。
        *   **C. 最终检查（迷你追踪器）**：再次运行 `show-keys --tracker <mini_tracker_path>` 以确认*此*迷你追踪器没有剩余的 `(checks needed: ...)`。
        *   对步骤 3.A 中找到的列表中的所有迷你追踪器重复步骤 3.B 和 3.C。
    *   **MUP**：验证所有找到的迷你追踪器后执行 MUP。更新 `last_action`。说明："完成所有已识别迷你追踪器的验证。继续 module_relationship_tracker.md。"

4.  **阶段 3：验证 `module_relationship_tracker.md`**：
    *   遵循与阶段 1 相同的验证子流程（步骤 2.A、2.B、2.C），针对 `<path_to_module_relationship_tracker.md>`（可能是 `{memory_dir}/module_relationship_tracker.md`）。
        *   **识别键**：使用 `show-keys --tracker <path_to_module_relationship_tracker.md>`。列出需要检查的键。如果没有，说明这一点，验证完成。
        *   **验证键**：遍历需要检查的键。
            *   **上下文**：使用 `show-placeholders` 获取未验证的模块级依赖项列表。在这里确定关系时，严重依赖于在阶段 2 期间*在*迷你追踪器内建立的已验证依赖项，以及整体系统架构（`system_manifest.md`）。模块级依赖项通常出现是因为模块 A *内的某个文件*依赖于模块 B *内的某个文件*。仅当迷你追踪器上下文不足时，才读取关键模块文件/文档（`read_file`）。
            ```bash
            python -m cline_utils.dependency_system.dependency_processor show-placeholders --tracker <path_to_module_relationship_tracker.md> --key <key_string>
            ```
            *   **确定关系并说明推理**：基于来自迷你追踪器的聚合依赖项和高级设计意图做出决策。
            *   **更正/确认**：使用 `add-dependency --tracker <path_to_module_relationship_tracker.md>` 和适当的参数。
        *   **最终检查**：再次运行 `show-keys --tracker <path_to_module_relationship_tracker.md>` 以确认没有剩余的需要检查。
    *   **MUP**：验证 `module_relationship_tracker.md` 后执行 MUP。更新 `last_action`。说明："完成 module_relationship_tracker.md 的验证。继续代码-文档交叉引用。"

*必须从每个角度设置键，因为每个*行*都有自己的依赖项列表。*

5.  **阶段 4：代码-文档交叉引用（添加 'd' 链接）**：
    *   **目标**：系统地审查代码组件，并确保它们具有指向其理解或实现所需的所有必要文档的显式依赖项。这发生在阶段 1-3 中解析初始占位符/建议（'p'、's'、'S'）*之后*。
    *   **A. 识别代码和文档键**：
        *   在相关追踪器（迷你追踪器、主追踪器）上使用 `show-keys` 来获取代码键列表。
        *   使用 `show-keys --tracker <path_to_doc_tracker.md>` 获取文档键列表。
        *输出键可能是 `KEY` 或 `KEY#GI`。你需要将这些解析为它们特定的全局 `KeyInfo` 对象（路径和基础键）以执行概念匹配。*
        *   *（或者，如果更高效，基于 `ConfigManager` 和全局键映射使用内部逻辑）*。
    *   **B. 遍历代码键**：
        *   选择一个代码键（例如，表示特定代码文件的 `code_key_string`）。
        *   **识别潜在文档**：确定哪些文档键（`doc_key_string`）可能与 `code_key_string` 相关。考虑：
            *   代码所属的模块。
            *   代码文件中描述的功能（`read_file <code_file_path>`）。
            *   `show-dependencies --key <code_key_string>` 显示的现有依赖项。
            *   在代码中查找引用特定文档的注释。
            *   问这样的问题，"此文档是否为理解代码的预期操作方式提供了有价值或有用的信息？"，以及"代码是否需要了解此信息才能执行其预期功能？"。
            *    也应考虑概念链接和未来计划的方向。可用于告知代码如何与系统相关操作的信息越多，最终结果的质量就越高。
        *   **检查相关文档**：使用 `read_file` 检查潜在相关文档文件的内容。
        *   **确定必要的文档**：对于每个潜在的 `doc_key_string`，决定它是否提供*必要*的上下文、定义、规范或解释，这些是理解、实现或正确使用由 `code_key_string` 表示的代码所必需的。这不仅仅是关键字相似性。
        *   **添加依赖项（双向）**：如果 `doc_key_string` 对 `code_key_string` 是必要的：
            *   **说明推理（强制性）**：解释*为什么*文档对代码是必要的。
            *   **添加代码 -> 文档链接**：使用 `add-dependency`，针对与*代码文件*最相关的追踪器。
                ```bash
                # 推理：[解释为什么 doc_key_string 对 code_key_string 是必要的]
                python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <code_file_tracker_path> --source-key <code_key_string> --target-key <doc_key_string> --dep-type "<dep_char>"
                ```
            *   **添加文档 -> 代码链接**：使用 `add-dependency`，针对 `doc_tracker.md`。
                ```bash
                # 推理：[与上述相同的推理，从文档的角度]
                python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key <doc_key_string> --target-key <code_key_string> --dep-type "<dep_char>"
                ```
        *   对当前 `code_key_string` 的所有相关文档键重复。
    *   **C. 对所有代码键重复**：继续步骤 5.B，直到所有相关代码键都已根据文档语料库进行了审查。
    *   **MUP**：执行 MUP。更新 `last_action`。说明："完成代码-文档交叉引用。"

6.  **完成**：一旦所有四个阶段都完成，并且 `show-keys` 报告 `doc_tracker.md`、所有迷你追踪器和 `module_relationship_tracker.md` 没有 `(checks needed: ...)`，追踪器验证部分的设置/维护就完成了。检查是否满足所有其他阶段退出标准（第 I 节）（例如，核心文件存在、代码/文档根目录已识别、系统清单已填充）。如果是，通过按照第 I 节更新 `.clinerules` 准备退出阶段。

*如果在**任一**方向检测到依赖项，则不应使用 'n'。选择最佳字符来表示方向依赖项，或者如果它是更一般的文档依赖项，则选择 'd'。*

## IV. 设置/维护依赖项工作流程图

```mermaid
graph TD
    A[开始设置/维护验证] --> B(运行 analyze-project);
    B --> C[阶段 1：验证 doc_tracker.md];

    subgraph Verify_doc_tracker [阶段 1：doc_tracker.md]
        C1[使用 show-keys --tracker doc_tracker.md] --> C2{需要检查？};
        C2 -- 是 --> C3[识别键];
        C3 --> C4[对于每个需要检查的键：];
        C4 --> C5(运行 show-placeholders --tracker doc_tracker.md --key [key]);
        C5 --> C6(计划读取 / 建议批量);
        C6 --> C7(读取源 + 目标文件);
        C7 --> C8(确定关系并说明推理);
        C8 --> C9(使用 add-dependency --tracker doc_tracker.md);
        C9 --> C4;
        C4 -- 所有键完成 --> C10[最终检查：show-keys];
        C2 -- 否 --> C10[doc_tracker 已验证];
    end

    C --> Verify_doc_tracker;
    C10 --> D[阶段 1 后的 MUP];

    D --> E[阶段 2：查找并验证迷你追踪器];
    subgraph Find_Verify_Minis [阶段 2：迷你追踪器（`*_module.md`）]
        E1[从 .clinerules 识别代码根目录] --> E2[递归扫描代码根目录];
        E2 --> E3[查找并验证 *_module.md 文件];
        E3 --> E4[编译迷你追踪器路径列表];
        E4 --> E5{找到任何迷你追踪器？};
        E5 -- 是 --> E6[选择下一个迷你追踪器];
        E6 --> E7[使用 show-keys --tracker <mini_tracker>];
        E7 --> E8{需要检查？};
        E8 -- 是 --> E9[识别键];
        E9 --> E10[对于每个需要检查的键：];
        E10 --> E11(运行 show-placeholders --tracker [mini_tracker] --key [key]);
        E11 --> E12(计划读取 / 建议批量);
        E12 --> E13(读取源 + 目标文件);
        E13 --> E14(确定关系并说明推理 - 考虑外键/外部);
        E14 --> E15(使用 add-dependency --tracker <mini_tracker>);
        E15 --> E10;
        E10 -- 所有键完成 --> E16[最终检查：show-keys];
        E8 -- 否 --> E16[迷你追踪器已验证];
        E16 --> E17{所有迷你追踪器已检查？};
        E17 -- 否 --> E6;
        E17 -- 是 --> E18[所有迷你追踪器已验证];
        E5 -- 否 --> E18; // 如果没有找到迷你追踪器则跳过
    end

    E --> Find_Verify_Minis;
    E18 --> F[阶段 2 后的 MUP];

    F --> G[阶段 3：验证 module_relationship_tracker.md];
    subgraph Verify_main_tracker [阶段 3：module_relationship_tracker.md]
        G1[使用 show-keys --tracker module_relationship_tracker.md] --> G2{需要检查？};
        G2 -- 是 --> G3[识别键];
        G3 --> G4[对于每个需要检查的键：];
        G4 --> G5(运行 show-placeholders --tracker module_relationship_tracker.md --key [key]);
        G5 --> G6(计划读取 / 使用迷你追踪器上下文 / 读取关键模块文件);
        G6 --> G7(确定关系并说明推理 - 模块级别);
        G7 --> G8(使用 add-dependency --tracker module_relationship_tracker.md);
        G8 --> G4;
        G4 -- 所有键完成 --> G9[最终检查：show-keys];
        G2 -- 否 --> G9[主追踪器已验证];
    end

    G --> Verify_main_tracker;
    G9 --> H[阶段 3 后的 MUP];

    H --> J[阶段 4：代码-文档交叉引用];
    subgraph CodeDocRef [阶段 4：代码-文档交叉引用]
        J1[识别代码和文档键] --> J2[对于每个代码键：];
        J2 --> J3(识别潜在文档);
        J3 --> J4(读取代码和文档);
        J4 --> J5(确定必要的文档并推理);
        J5 -- 是 --> J6(add-dependency -> tracker);
        J6 --> J2;
        J5 -- 否 --> J2;
        J2 -- 所有代码键完成 --> J7[阶段 4 完成];
    end

    J --> CodeDocRef;
    J7 --> K[阶段 4 后的 MUP];
    K --> L[结束验证流程 - 检查所有退出标准（第 I 节）];

    style Verify_doc_tracker fill:#e6f7ff,stroke:#91d5ff
    style Find_Verify_Minis fill:#f6ffed,stroke:#b7eb8f
    style Verify_main_tracker fill:#fffbe6,stroke:#ffe58f
```

## V. 定位和理解迷你追踪器

**目的**：迷你追踪器（`{dirname}_module.md`）具有双重作用：
1.  **HDTA 领域模块**：它们包含模块的描述性文本（目的、组件等），在策略期间手动管理。
2.  **依赖项追踪器**：它们跟踪*该模块内*以及可能*到外部*文件/文档的文件/函数级依赖项。依赖项网格通过 `dependency_processor.py` 命令管理。

**定位迷你追踪器：**
1.  **获取代码根目录**：从 `.clinerules` 读取 `[CODE_ROOT_DIRECTORIES]` 列表。这些是包含项目源代码的顶级目录。
2.  **扫描代码根目录**：对于 `[CODE_ROOT_DIRECTORIES]` 中列出的每个目录：
    *   递归扫描其内容。
    *   查找匹配模式 `{dirname}_module.md` 的文件，其中 `{dirname}` 是包含该文件的目录的确切名称。
    *   示例：在 `src/auth/` 中，查找 `auth_module.md`。在 `src/game/state/` 中，查找 `state_module.md`。
3.  **编译列表**：创建所有找到的有效迷你追踪器文件的完整、规范化路径列表。此列表将在第 III 节中用于验证迷你追踪器时使用。

**创建和验证**：
*   **创建/更新**：`analyze-project` 命令（在第 II.4 节和第 III 节之前可能运行）自动为检测到的模块创建 `{dirname}_module.md` 文件（如果它们不存在），或者如果它们存在则更新其中的依赖项网格。它使用键和初始占位符/建议填充网格。
*   **验证**：**第 III 节**中的详细验证过程用于在验证 `doc_tracker.md` *之后*和验证 `module_relationship_tracker.md` *之前*解析这些迷你追踪器内的占位符（'p'、's'、'S'）。使用上面编译的列表在该阶段遍历迷你追踪器。

## VI. 设置/维护插件 - MUP 添加

在执行核心 MUP 步骤（核心提示词第 VI 节）之后：
1.  **更新 `system_manifest.md`（如果更改）**：如果设置操作显著修改了项目结构（例如，添加了需要迷你追踪器的主要模块），确保 `system_manifest.md` 反映这一点，可能添加新模块。
2.  **更新 `.clinerules` [LAST_ACTION_STATE]：** 更新 `last_action`、`current_phase`、`next_action`、`next_phase` 以反映此阶段内完成的特定步骤。示例：
    *   识别根目录后：
        ```
        last_action: "Identified Code and Doc Roots"
        current_phase: "Set-up/Maintenance"
        next_action: "Initialize Core Files / Run analyze-project"
        next_phase: "Set-up/Maintenance"
        ```
    *   初始 `analyze-project` 后：
        ```
        last_action: "Ran analyze-project, Initialized Trackers"
        current_phase: "Set-up/Maintenance"
        next_action: "Verify doc_tracker.md Dependencies"
        next_phase: "Set-up/Maintenance"
        ```
    *   验证 `doc_tracker.md` 后：
        ```
        last_action: "Verified doc_tracker.md"
        current_phase: "Set-up/Maintenance"
        next_action: "Verify Mini-Trackers"
        next_phase: "Set-up/Maintenance"
        ```
    *   验证最后一个追踪器后：
        ```
        last_action: "Completed All Tracker Verification"
        current_phase: "Set-up/Maintenance"
        next_action: "Perform Code-Documentation Cross-Reference"
        next_phase: "Set-up/Maintenance"
        ```
    *   完成代码-文档交叉引用后：
        ```
        last_action: "Completed Code-Documentation Cross-Reference ('d' links added)"
        current_phase: "Set-up/Maintenance"
        next_action: "Phase Complete - User Action Required"
        next_phase: "Strategy"
        ```
