# **Cline 递归思维链系统 (CRCT) - 设置/维护插件**

**本插件为 CRCT 系统的设置/维护阶段提供详细说明和程序。应与核心系统提示结合使用。**

## I. 进入和退出设置/维护阶段

**进入设置/维护阶段：**
1.  **初始状态**：对于新项目或如果 `.clinerules` 显示 `next_phase: "Set-up/Maintenance"` 时从此处开始。
2.  **`.clinerules` 检查**：始终先读取 `.clinerules`。如果 `[LAST_ACTION_STATE]` 指示 `current_phase: "Set-up/Maintenance"` 或 `next_phase: "Set-up/Maintenance"`，则继续执行这些说明，如果指定了 `next_action`，则从该处恢复。
3.  **新项目**：如果 `.clinerules` 缺失/为空，假定为此阶段，创建 `.clinerules`（见第 II 节），并初始化其他核心文件。

**退出设置/维护阶段：**
1.  **完成标准：**
    *   所有核心文件存在并已初始化（第 II 节）。
    *   `.clinerules` 中的 `[CODE_ROOT_DIRECTORIES]` 和 `[DOC_DIRECTORIES]` 已填充（核心提示第 X 和 XI 节）。
    *   `doc_tracker.md` 存在且没有剩余的 'p'、's' 或 'S' 占位符（通过第 III 节第 1 阶段中的 `show-keys` 验证）。
    *   所有迷你追踪器（`*_module.md`）存在且没有剩余的 'p'、's' 或 'S' 占位符（通过第 III 节第 2 阶段中的 `show-keys` 验证）。
    *   `module_relationship_tracker.md` 存在且没有剩余的 'p'、's' 或 'S' 占位符（通过第 III 节第 3 阶段中的 `show-keys` 验证）。
    *   **代码-文档交叉引用完成（第 III 节第 4 阶段），确保添加了必要的 'd' 链接。**
    *   `system_manifest.md` 已创建并填充（至少从模板中最低限度填充）。
    *   根据需要通过 `analyze-project` 创建/填充迷你追踪器。
2.  **`.clinerules` 更新（MUP）：** 一旦满足所有标准，按如下方式更新 `[LAST_ACTION_STATE]`：
    ```
    last_action: "Completed Set-up/Maintenance Phase"
    current_phase: "Set-up/Maintenance"
    next_action: "Phase Complete - User Action Required"
    next_phase: "Strategy"
    ```
3.  **用户操作**：更新 `.clinerules` 后，暂停等待用户触发下一个会话/阶段。参考核心系统提示第 III 节中的阶段转换检查清单。

## II. 初始化核心必需文件和项目结构

**操作**：确保所有核心文件存在，如果缺失则根据核心系统提示（第 II 节）中的规范触发其创建。

**程序：**
1.  **检查存在性**：检查核心提示第 II 节中列出的每个所需文件（`.clinerules`、`system_manifest.md`、`activeContext.md`、`module_relationship_tracker.md`、`changelog.md`、`doc_tracker.md`、`userProfile.md`、`progress.md`）是否存在于其指定位置。
2.  **识别代码和文档目录**：如果 `.clinerules` 中的 `[CODE_ROOT_DIRECTORIES]` 或 `[DOC_DIRECTORIES]` 为空或缺失，**停止**其他初始化并遵循核心提示第 X 和 XI 节中的程序，首先识别并填充这些部分。更新 `.clinerules` 并执行 MUP。之后恢复初始化检查。
3.  **触发创建缺失文件：**
    *   **手动创建文件**（`.clinerules`、`activeContext.md`、`changelog.md`、`userProfile.md`、`progress.md`）：如果缺失，使用 `write_to_file` 创建它们，内容为核心提示第 II 节表格中描述的最小占位符内容。声明："文件 `{file_path}` 缺失。使用占位符内容创建。"
        *   示例初始 `.clinerules`（如果创建）：
            ```
            [LAST_ACTION_STATE]
            last_action: "System Initialized"
            current_phase: "Set-up/Maintenance"
            next_action: "Initialize Core Files" # 或如果需要，首先识别代码/文档根目录
            next_phase: "Set-up/Maintenance"

            [CODE_ROOT_DIRECTORIES]
            # 待识别

            [DOC_DIRECTORIES]
            # 待识别

            [LEARNING_JOURNAL]
            -
            ```
    *   **基于模板的文件**（`system_manifest.md`）：如果缺失，首先使用 `write_to_file` 在 `{memory_dir}/` 中创建一个名为 `system_manifest.md` 的空文件。声明："文件 `system_manifest.md` 缺失。创建空文件。" 然后，从 `cline_docs/templates/system_manifest_template.md` 读取模板内容，并再次使用 `write_to_file` 用模板内容*覆盖*空的 `system_manifest.md`。声明："用模板内容填充 `system_manifest.md`。"
    *   **追踪器文件**（`module_relationship_tracker.md`、`doc_tracker.md` 和迷你追踪器 `*_module.md`）：
        *   **不要手动创建。**
        *   如果这些文件中有任何缺失，或者如果发生了重大项目更改，或者如果您正在开始验证，请运行 `analyze-project`。此命令将根据当前项目结构和识别的代码/文档根目录创建或更新所有必要的追踪器。
        ```bash
        # 首先确保在 .clinerules 中设置了代码/文档根目录！
        python -m cline_utils.dependency_system.dependency_processor analyze-project
        ```
        *   声明："追踪器文件缺失或需要更新。运行 `analyze-project` 以创建/更新追踪器。"
        *   *（运行 `analyze-project` 也是第 III 节验证工作流程的第一步）*。
        *   *（可选：如果需要，添加 `--force-analysis` 或 `--force-embeddings`）*。
        *   *（模块目录中的迷你追踪器也由 `analyze-project` 创建/更新）*。
4.  **MUP**：创建文件或运行 `analyze-project` 后，遵循核心提示 MUP（第 VI 节）和下面的第 V 节添加内容。更新 `[LAST_ACTION_STATE]` 以反映进度（例如，`next_action: "Verify Tracker Dependencies"`）。

## III. 分析和验证追踪器依赖项（有序工作流）

**在读取相关文件之前不要假设依赖关系！！**

**目标**：通过系统地解决占位符（'p'）和验证建议（'s'、'S'），然后进行明确的代码到文档交叉引用步骤，确保追踪器准确反映项目依赖关系。**此过程必须遵循特定顺序：**
1.  `doc_tracker.md`（占位符/建议解决）
2.  所有迷你追踪器（`*_module.md`）（占位符/建议解决）
3.  `module_relationship_tracker.md`（占位符/建议解决）
4.  **代码-文档交叉引用**（添加明确依赖关系）

此顺序至关重要，因为迷你追踪器捕获模块内详细的跨目录依赖关系，这对于准确确定 `module_relationship_tracker.md` 中更高级别的模块到模块关系至关重要。

**重要**：
*   **所有追踪器修改必须使用 `dependency_processor.py` 命令。** 有关命令详细信息，请参见核心提示第 VIII 节。
*   **不要直接读取追踪器文件**以获取依赖信息；使用 `show-keys` 和 `show-dependencies`。
*   如果自上次运行以来发生了重大代码/文档更改，或进入此阶段时（如第 II 节所做），请在开始此验证过程*之前*运行 `analyze-project`。

***关键强调***：*文档必须与代码**详尽地**交叉引用，这一点至关重要。如果未将定义代码的文档列为依赖项，则无法正确完成代码。以下验证阶段，尤其是第 4 阶段，旨在实现这一目标。*

**这个阶段不是关于效率，而是关于*准确性*。这是一项基础工作。如果这个阶段的准确性很低，整个项目将受到影响。**

**程序：**

1.  **运行项目分析（初始和更新）**：
    *   使用 `analyze-project` 自动生成/更新键、分析文件、建议依赖关系（'p'、's'、'S'），并更新*所有*追踪器（`module_relationship_tracker.md`、`doc_tracker.md` 和迷你追踪器）。此命令创建追踪器（如果它们不存在）并根据当前代码/文档和配置填充/更新网格。
    ```bash
    python -m cline_utils.dependency_system.dependency_processor analyze-project
    ```
    *   *（可选：如果需要，添加 `--force-analysis` 或 `--force-embeddings`，例如，如果配置已更改或缓存似乎过时）*。
    *   **查看日志（`debug.txt`、`suggestions.log`）**以了解分析详细信息和建议的更改，但优先考虑下面的验证工作流程。声明："运行了 analyze-project。查看日志并继续有序验证。"

2.  **阶段 1：验证 `doc_tracker.md`**：
    *   **A. 识别需要验证的键**：
        *   为 `doc_tracker.md` 运行 `show-keys`：
          ```bash
          python -m cline_utils.dependency_system.dependency_processor show-keys --tracker <path_to_doc_tracker.md>
          ```
          *（使用实际路径，可能是基于配置的 `{memory_dir}/doc_tracker.md`）*
        *   检查输出。列出的键可能是基本键（例如，"1A1"）或全局实例键（例如，"2B1#1"），如果它们的基本键字符串在项目中用于多个不同的路径。识别所有以 `(checks needed: ...)` 结尾的行。这表示该键的行*在此追踪器内*有未解决的 'p'、's' 或 'S' 字符。
        *   创建这些需要验证的 `doc_tracker.md` 键列表。如果没有，声明此情况并继续第 2 阶段。
    *   **B. 验证识别的键的占位符/建议**：
        *   遍历步骤 2.A 中的键列表。
        *   对于每个 `key_string`（行键）：
            *   **获取上下文**：运行 `show-placeholders` 针对当前追踪器和键。此命令专门列出给定键*在此追踪器内*的 'p'、's' 和 'S' 关系，提供用于验证的目标列表。
            ```bash
            python -m cline_utils.dependency_system.dependency_processor show-placeholders --tracker <path_to_doc_tracker.md> --key <key_string>
            ```
            *   **计划读取**：识别源文件（对于 `key_string`）和相关目标文件（对于需要验证的列键）。为了提高效率，计划在下一步中一起读取源文件和*多个*相关目标文件。如果文件位于同一位置，建议批量读取（例如，"建议从同一目录读取源文件 X 和目标文件 Y、Z。您可以提供文件夹内容还是我应该使用 `read_file` 单独读取？"）。注意上下文限制。
            *   **检查文件**：使用 `read_file` 检查源文件和识别的相关目标文件/文件夹的内容。
            *   **确定关系（关键步骤）**：基于文件内容，确定源（`key_string`）与每个正在验证的目标键之间的**真正功能或基本概念关系**。
                *   **超越相似性**：建议（'s'、'S'）可能仅表示相关主题，而不是操作或理解的*必要*依赖关系。
            *   **关注功能依赖**：询问：
                *   *行文件*中的代码是否直接**导入、调用或继承自***列文件*中的代码？（导致 '<' 或 'x'）。
                *   *列文件*中的代码是否直接**导入、调用或继承自***行文件*中的代码？（导致 '>' 或 'x'）。
                *   *行文件*中的文档是否**需要***列文件*中*仅*存在的信息或定义才能完整或准确？（导致 '<' 或 'd'）。
                *   *行文件*是否是**基本文档**用于理解或实现*列文件*中的概念/代码？（导致 'd' 或可能 '>'）。
                *   是否存在**深层的、直接的概念联系**，即使没有直接的代码导入，理解或修改一个文件也*需要*理解另一个文件？（根据链接的性质考虑 '<'、'>'、'x' 或 'd'）。
            *   **依赖关系的目的**：请记住，这些经过验证的依赖关系指导**策略阶段**（确定任务顺序）和**执行阶段**（加载最少的必要上下文）。依赖关系应该意味着"您*需要*考虑/加载相关文件才能有效地处理此文件。"
            *   **如果没有真正的依赖关系，分配 'n'**：如果关系仅仅是主题性的、使用相似术语或间接的，分配 'n'（已验证无依赖关系）。*标记 'n' 总比创建弱依赖关系好。*
            *   **陈述推理（强制性）**：在使用 `add-dependency` 之前，**清楚地陈述您的推理**，说明您打算设置的依赖关系字符（`<`、`>`、`x`、`d` 或 `n`）的选择，基于您的直接文件分析和功能依赖标准，针对*每个特定关系*。
        *   **更正/确认依赖关系**：使用 `add-dependency`，指定 `--tracker <path_to_doc_tracker.md>`。`--source-key` 始终是您正在迭代的 `key_string`。`--target-key` 是您确定其关系的列键。根据您的推理分析设置 `--dep-type`。如果多个目标*对于同一源键*共享*相同的新依赖类型*，则批量处理它们。
              ```bash
              # 示例：在 doc_tracker.md 中从 1A2（源）到 2B1#3（目标）设置 '>'
              # 推理：docs/setup.md (1A2) 详细说明了在使用 docs/api/users.md (2B1) 中描述的 API 之前所需的步骤。因此，2B1 依赖于 1A2。
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key 1A2 --target-key 2B1#3 --dep-type ">"

              # 示例：在 doc_tracker.md 中从 1A2（源）到 3C1 和 3C2（目标）设置 'n'
              # 推理：文件 3C1 和 3C2 是不相关的示例；与设置指南 1A2 没有功能依赖关系。
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key 1A2 --target-key 3C1 3C2 --dep-type "n"
              ```
        *   对步骤 2.A 中识别的所有键重复步骤 2.B。
    *   **C. 最终检查**：再次运行 `show-keys --tracker <path_to_doc_tracker.md>` 以确认没有剩余的 `(checks needed: ...)`。
    *   **MUP**：执行 MUP。更新 `last_action`。声明："完成了 doc_tracker.md 的验证。继续查找和验证迷你追踪器。"

3.  **阶段 2：查找和验证迷你追踪器（`*_module.md`）**：
    *   **A. 查找迷你追踪器文件**：
        *   **目标**：在项目的代码目录中定位所有 `*_module.md` 文件。
        *   **获取代码根目录**：从 `.clinerules` 读取 `[CODE_ROOT_DIRECTORIES]` 列表。如果为空，声明此情况且此阶段无法继续。
        *   **扫描目录**：对于每个代码根目录，使用 `list_files` 或类似的目录遍历逻辑递归扫描其内容。
        *   **识别和验证**：识别与模式 `{dirname}_module.md` 匹配的文件，其中 `{dirname}` 与包含该文件的目录名称完全匹配（例如，`src/user_auth/user_auth_module.md`）。
        *   **创建列表**：编译找到的所有有效迷你追踪器文件的完整、规范化路径列表。
        *   **报告**：声明找到的迷你追踪器路径列表。如果没有找到但代码根目录存在，声明此情况并确认 `analyze-project` 成功运行（因为如果存在模块，它应该创建它们）。如果没有找到，继续第 3 阶段。
    *   **B. 遍历迷你追踪器**：如果找到迷你追踪器：
        *   从列表中选择下一个迷你追踪器路径。声明您正在处理哪一个。
        *   **重复验证步骤**：遵循与阶段 1（步骤 2.A 和 2.B）相同的子程序，但在所有命令（`show-keys`、`add-dependency`）中将当前迷你追踪器路径替换为 `<path_to_doc_tracker.md>`。
            *   **识别键**：使用 `show-keys --tracker <mini_tracker_path>`。列出需要检查的键。
            *   **验证键**：遍历需要检查的键。使用 `show-placeholders` 获取*此迷你追踪器内*未验证依赖关系的目标列表。检查源/目标文件（`read_file`）。基于功能/概念依赖陈述推理。使用 `add-dependency --tracker <mini_tracker_path> --source-key <key_string> --target-key <target_key> --dep-type <char>`。
            ```bash
            python -m cline_utils.dependency_system.dependency_processor show-placeholders --tracker <mini_tracker_path> --key <key_string>
            ```
            *   **外键**：请记住，在迷你追踪器上使用 `add-dependency` 时，如果 `--target-key` 全局存在（核心提示第 VIII 节），则它可以是外部（外键）键。如果在分析期间识别，使用此功能将内部代码链接到其他模块中的外部文档或代码。清楚地陈述推理。
              ```bash
              # 示例：在 agents_module.md 中从内部代码文件 1Ba2 到外部文档 1Aa6 设置 'd'
              # 推理：combat_agent.py (1Ba2) 实现 Multi-Agent_Collaboration.md (1Aa6) 中定义的概念，使文档至关重要。
              python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker src/agents/agents_module.md --source-key 1Ba2 --target-key 1Aa6 --dep-type "d"
              ```
            *   **主动外部链接**：在分析文件内容时，主动查找对*外部*文件（文档或其他模块）的明确引用或清晰的概念依赖，这些是自动化遗漏的。如果存在真正的依赖关系，使用带有外键功能的 `add-dependency` 添加这些。陈述推理。
        *   **C. 最终检查（迷你追踪器）**：再次运行 `show-keys --tracker <mini_tracker_path>` 以确认*此*迷你追踪器没有剩余的 `(checks needed: ...)`。
        *   对步骤 3.A 中找到的列表中的所有迷你追踪器重复步骤 3.B 和 3.C。
    *   **MUP**：验证所有找到的迷你追踪器后执行 MUP。更新 `last_action`。声明："完成了所有识别的迷你追踪器的验证。继续 module_relationship_tracker.md。"

4.  **阶段 3：验证 `module_relationship_tracker.md`**：
    *   遵循与阶段 1（步骤 2.A、2.B、2.C）相同的验证子程序，针对 `<path_to_module_relationship_tracker.md>`（可能是 `{memory_dir}/module_relationship_tracker.md`）。
        *   **识别键**：使用 `show-keys --tracker <path_to_module_relationship_tracker.md>`。列出需要检查的键。如果没有，声明此情况且验证完成。
        *   **验证键**：遍历需要检查的键。
            *   **上下文**：使用 `show-placeholders` 获取未验证的模块级依赖关系列表。在确定此处的关系时，严重依赖于在阶段 2 期间*在*迷你追踪器内建立的已验证依赖关系，以及总体系统架构（`system_manifest.md`）。模块级依赖关系通常是因为*模块 A 中的某个文件*依赖于*模块 B 中的某个文件*。仅当迷你追踪器上下文不足时，才读取关键模块文件/文档（`read_file`）。
            ```bash
            python -m cline_utils.dependency_system.dependency_processor show-placeholders --tracker <path_to_module_relationship_tracker.md> --key <key_string>
            ```
            *   **确定关系并陈述推理**：基于来自迷你追踪器的聚合依赖关系和高级设计意图做出决定。
            *   **更正/确认**：使用带有适当参数的 `add-dependency --tracker <path_to_module_relationship_tracker.md>`。
        *   **最终检查**：再次运行 `show-keys --tracker <path_to_module_relationship_tracker.md>` 以确认没有剩余的需要检查的内容。
    *   **MUP**：验证 `module_relationship_tracker.md` 后执行 MUP。更新 `last_action`。声明："完成了 module_relationship_tracker.md 的验证。继续代码-文档交叉引用。"

*必须从每个角度设置键，因为每个*行*都有自己的依赖关系列表。*

5.  **阶段 4：代码-文档交叉引用（添加 'd' 链接）**：
    *   **目标**：系统地审查代码组件，并确保它们具有指向理解或实现所需的所有基本文档的明确依赖关系。这发生在阶段 1-3 中解决初始占位符/建议（'p'、's'、'S'）*之后*。
    *   **A. 识别代码和文档键**：
        *   在相关追踪器（迷你追踪器、主追踪器）上使用 `show-keys` 获取代码键列表。
        *   使用 `show-keys --tracker <path_to_doc_tracker.md>` 获取文档键列表。
        *输出键可能是 `KEY` 或 `KEY#GI`。您需要将这些解析为其特定的全局 `KeyInfo` 对象（路径和基本键）以执行概念匹配。*
        *   *（或者，如果更有效，基于 `ConfigManager` 和全局键映射使用内部逻辑）*。
    *   **B. 遍历代码键**：
        *   选择一个代码键（例如，代表特定代码文件的 `code_key_string`）。
        *   **识别潜在文档**：确定哪些文档键（`doc_key_string`）可能与 `code_key_string` 相关。考虑：
            *   代码所属的模块。
            *   代码文件中描述的功能（`read_file <code_file_path>`）。
            *   `show-dependencies --key <code_key_string>` 显示的现有依赖关系。
            *   在代码中查找引用特定文档的注释。
            *   提出这样的问题："此文档是否提供了有价值或有用的信息来理解代码的预期操作方式？"以及"代码是否需要了解此信息才能执行其预期功能？"。
            *    也应考虑概念链接和未来计划的方向。可用于告知代码如何相对于系统运行的信息越多，最终结果的质量就越高。
        *   **检查相关文档**：使用 `read_file` 检查潜在相关文档文件的内容。
        *   **确定基本文档**：对于每个潜在的 `doc_key_string`，决定它是否提供*基本*上下文、定义、规范或解释，这些对于理解、实现或正确使用 `code_key_string` 表示的代码是必需的。这不仅仅是关键词相似性。
        *   **添加依赖关系（双向）**：如果 `doc_key_string` 对 `code_key_string` 至关重要：
            *   **陈述推理（强制性）**：解释*为什么*文档对代码至关重要。
            *   **添加代码 -> 文档链接**：使用 `add-dependency` 针对与*代码文件*最相关的追踪器。
                ```bash
                # 推理：[解释为什么 doc_key_string 对 code_key_string 至关重要]
                python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <code_file_tracker_path> --source-key <code_key_string> --target-key <doc_key_string> --dep-type "<dep_char>"
                ```
            *   **添加文档 -> 代码链接**：使用 `add-dependency` 针对 `doc_tracker.md`。
                ```bash
                # 推理：[与上述相同的推理，从文档的角度]
                python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <path_to_doc_tracker.md> --source-key <doc_key_string> --target-key <code_key_string> --dep-type "<dep_char>"
                ```
        *   对当前 `code_key_string` 的所有相关文档键重复。
    *   **C. 对所有代码键重复**：继续步骤 5.B，直到所有相关代码键都已针对文档语料库进行审查。
    *   **MUP**：执行 MUP。更新 `last_action`。声明："完成了代码-文档交叉引用。"

6.  **完成**：一旦所有四个阶段都完成，并且 `show-keys` 报告 `doc_tracker.md`、所有迷你追踪器和 `module_relationship_tracker.md` 没有 `(checks needed: ...)`，则设置/维护的追踪器验证部分完成。检查是否满足所有其他阶段退出标准（第 I 节）（例如，核心文件存在，识别了代码/文档根目录，填充了系统清单）。如果满足，则按照第 I 节准备退出阶段，更新 `.clinerules`。

*如果在**任一**方向检测到依赖关系，则不应使用 'n'。选择最能代表方向依赖关系的字符，或者如果是更一般的文档依赖关系，则选择 'd'。*

## IV. 设置/维护依赖工作流程图

```mermaid
graph TD
    A[开始设置/维护验证] --> B(运行 analyze-project);
    B --> C[阶段 1：验证 doc_tracker.md];

    subgraph Verify_doc_tracker [阶段 1：doc_tracker.md]
        C1[使用 show-keys --tracker doc_tracker.md] --> C2{需要检查？};
        C2 -- 是 --> C3[识别键];
        C3 --> C4[对于每个需要检查的键：];
        C4 --> C5(运行 show-placeholders --tracker doc_tracker.md --key [key]);
        C5 --> C6(计划读取 / 建议批处理);
        C6 --> C7(读取源文件 + 目标文件);
        C7 --> C8(确定关系并陈述推理);
        C8 --> C9(使用 add-dependency --tracker doc_tracker.md);
        C9 --> C4;
        C4 -- 所有键完成 --> C10[最终检查：show-keys];
        C2 -- 否 --> C10[doc_tracker 已验证];
    end

    C --> Verify_doc_tracker;
    C10 --> D[阶段 1 后 MUP];

    D --> E[阶段 2：查找并验证迷你追踪器];
    subgraph Find_Verify_Minis [阶段 2：迷你追踪器 (`*_module.md`)]
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
        E11 --> E12(计划读取 / 建议批处理);
        E12 --> E13(读取源文件 + 目标文件);
        E13 --> E14(确定关系并陈述推理 - 考虑外键/外部);
        E14 --> E15(使用 add-dependency --tracker <mini_tracker>);
        E15 --> E10;
        E10 -- 所有键完成 --> E16[最终检查：show-keys];
        E8 -- 否 --> E16[迷你追踪器已验证];
        E16 --> E17{所有迷你追踪器都检查了？};
        E17 -- 否 --> E6;
        E17 -- 是 --> E18[所有迷你追踪器已验证];
        E5 -- 否 --> E18; // 如果没有找到迷你追踪器则跳过
    end

    E --> Find_Verify_Minis;
    E18 --> F[阶段 2 后 MUP];

    F --> G[阶段 3：验证 module_relationship_tracker.md];
    subgraph Verify_main_tracker [阶段 3：module_relationship_tracker.md]
        G1[使用 show-keys --tracker module_relationship_tracker.md] --> G2{需要检查？};
        G2 -- 是 --> G3[识别键];
        G3 --> G4[对于每个需要检查的键：];
        G4 --> G5(运行 show-placeholders --tracker module_relationship_tracker.md --key [key]);
        G5 --> G6(计划读取 / 使用迷你追踪器上下文 / 读取关键模块文件);
        G6 --> G7(确定关系并陈述推理 - 模块级别);
        G7 --> G8(使用 add-dependency --tracker module_relationship_tracker.md);
        G8 --> G4;
        G4 -- 所有键完成 --> G9[最终检查：show-keys];
        G2 -- 否 --> G9[主追踪器已验证];
    end

    G --> Verify_main_tracker;
    G9 --> H[阶段 3 后 MUP];

    H --> J[阶段 4：代码-文档交叉引用];
    subgraph CodeDocRef [阶段 4：代码-文档交叉引用]
        J1[识别代码和文档键] --> J2[对于每个代码键：];
        J2 --> J3(识别潜在文档);
        J3 --> J4(读取代码和文档);
        J4 --> J5(确定基本文档并推理);
        J5 -- 是 --> J6(add-dependency -> tracker);
        J6 --> J2;
        J5 -- 否 --> J2;
        J2 -- 所有代码键完成 --> J7[阶段 4 完成];
    end

    J --> CodeDocRef;
    J7 --> K[阶段 4 后 MUP];
    K --> L[结束验证过程 - 检查所有退出标准（第 I 节）];

    style Verify_doc_tracker fill:#e6f7ff,stroke:#91d5ff
    style Find_Verify_Minis fill:#f6ffed,stroke:#b7eb8f
    style Verify_main_tracker fill:#fffbe6,stroke:#ffe58f
```

## V. 定位和理解迷你追踪器

**目的**：迷你追踪器（`{dirname}_module.md`）具有双重作用：
1.  **HDTA 域模块**：它们包含模块的描述性文本（目的、组件等），在策略期间手动管理。
2.  **依赖追踪器**：它们跟踪*该*模块内以及潜在*到外部*文件/文档的文件/函数级依赖关系。依赖关系网格通过 `dependency_processor.py` 命令管理。

**定位迷你追踪器：**
1.  **获取代码根目录**：从 `.clinerules` 读取 `[CODE_ROOT_DIRECTORIES]` 列表。这些是包含项目源代码的顶级目录。
2.  **扫描代码根目录**：对于 `[CODE_ROOT_DIRECTORIES]` 中列出的每个目录：
    *   递归扫描其内容。
    *   查找与模式 `{dirname}_module.md` 匹配的文件，其中 `{dirname}` 是包含该文件的目录的确切名称。
    *   示例：在 `src/auth/` 中，查找 `auth_module.md`。在 `src/game/state/` 中，查找 `state_module.md`。
3.  **编译列表**：创建找到的所有有效迷你追踪器文件的完整、规范化路径列表。此列表将在第 III 节中需要验证迷你追踪器时使用。

**创建和验证**：
*   **创建/更新**：`analyze-project` 命令（在第 II.4 节中运行，并可能在第 III 节之前运行）自动为检测到的模块创建 `{dirname}_module.md` 文件（如果它们不存在），或者如果它们存在则更新其中的依赖关系网格。它用键和初始占位符/建议填充网格。
*   **验证**：**第 III 节**中的详细验证过程用于在*验证 `doc_tracker.md` 之后*和*验证 `module_relationship_tracker.md` 之前*解决这些迷你追踪器内的占位符（'p'、's'、'S'）。使用上面编译的列表在该阶段迭代迷你追踪器。

## VI. 设置/维护插件 - MUP 添加

执行核心 MUP 步骤（核心提示第 VI 节）后：
1.  **更新 `system_manifest.md`（如果已更改）**：如果设置操作显著修改了项目结构（例如，添加需要迷你追踪器的主要模块），请确保 `system_manifest.md` 反映此情况，可能添加新模块。
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
