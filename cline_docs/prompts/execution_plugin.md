# **Cline Recursive Chain-of-Thought System (CRCT) - Execution Plugin**
# **Cline 递归思维链系统 (CRCT) - 执行插件**

**This Plugin provides detailed instructions and procedures for the Execution phase of the CRCT system. It should be used in conjunction with the Core System Prompt.**
**此插件为 CRCT 系统的执行阶段提供详细的说明和程序。应与核心系统提示结合使用。**

---

## I. Entering and Exiting Execution Phase
## I. 进入和退出执行阶段

**Entering Execution Phase:**
**进入执行阶段:**
1.  **`.clinerules` Check**: Always read `.clinerules` first. If `[LAST_ACTION_STATE]` shows `current_phase: "Execution"` or `next_phase: "Execution"`, proceed with these instructions, resuming from `next_action` if specified.
    1.  **`.clinerules` 检查**: 始终首先读取 `.clinerules`。如果 `[LAST_ACTION_STATE]` 显示 `current_phase: "Execution"` 或 `next_phase: "Execution"`,则按照这些说明继续,如果指定了则从 `next_action` 恢复。
2.  **Transition from Strategy**: The `project_roadmap.md` file, updated by the Strategy phase, now contains the definitive, sequenced list of `Execution_*` tasks for the current cycle. This list is the primary input for this phase.
    2.  **从策略转换**: 由策略阶段更新的 `project_roadmap.md` 文件现在包含当前周期的确定的、按顺序排列的 `Execution_*` 任务列表。此列表是该阶段的主要输入。
3.  **User Trigger**: Start a new session post-Strategy or to resume execution if paused.
    3.  **用户触发**: 在策略后开始新会话或如果暂停则恢复执行。

**Exiting Execution Phase:**
**退出执行阶段:**
1. **Completion Criteria:**
    1. **完成标准:**
   - **All `Execution_*` tasks listed in the current cycle's "Unified Execution Sequence" within `project_roadmap.md` have been marked as complete (`[x]`).**
       - **`project_roadmap.md` 中当前周期的"统一执行序列"中列出的所有 `Execution_*` 任务都已标记为完成(`[x]`)。**
   - Expected outputs for all tasks are generated and verified.
       - 所有任务的预期输出已生成并验证。
   - Results and observations are documented.
       - 结果和观察已记录。
   - MUP is followed for all actions.
       - 所有操作都遵循 MUP。
2. **`.clinerules` Update (MUP):**
    2. **`.clinerules` 更新(MUP):**
   - To proceed to cleanup and consolidation:
       - 继续进行清理和整合:
     ```
     [LAST_ACTION_STATE]
     last_action: "Completed Execution Phase - Tasks Executed"
     current_phase: "Execution"
     next_action: "Phase Complete - User Action Required"
     next_phase: "Cleanup/Consolidation"
     ```
   - *Alternative: If transitioning back to Set-up/Maintenance for re-verification (less common after standard execution)*:
       - *替代方案: 如果转换回设置/维护以进行重新验证(标准执行后不太常见)*:
     ```
     [LAST_ACTION_STATE]
     last_action: "Completed Execution Phase - Tasks Executed, Needs Verification"
     current_phase: "Execution"
     next_action: "Phase Complete - User Action Required"
     next_phase: "Set-up/Maintenance"
     ```
   - For project completion:
       - 对于项目完成:
     ```
     [LAST_ACTION_STATE]
     last_action: "Completed Execution Phase - Project Objectives Achieved"
     current_phase: "Execution"
     next_action: "Project Completion - User Review"
     next_phase: "Project Complete"
     ```
   *Note: "Project Complete" pauses the system; define further actions if needed.*
   *注意: "Project Complete" 暂停系统;如果需要,定义进一步的操作。*
3. **User Action**: After updating `.clinerules`, pause for user to trigger the next phase. See Core System Prompt, Section III for a phase transition checklist.
    3. **用户操作**: 更新 `.clinerules` 后,暂停以等待用户触发下一阶段。请参阅核心系统提示第三节,了解阶段转换检查清单。

---

## II. Loading Context for Execution
## II. 为执行加载上下文

**Action**: Load necessary context for the selected Task Instruction, respecting the planning hierarchy and dependencies.
**操作**: 为选定的任务说明加载必要的上下文,尊重规划层次和依赖关系。

**Procedure:**
**程序:**
**Load the Master Plan (MANDATORY FIRST STEP)**:
**加载主计划(强制的第一步)**:
    *   `read_file` the `project_roadmap.md`.
        *   `read_file` `project_roadmap.md`。
    *   State: "Reading `project_roadmap.md` to identify the execution sequence for the current cycle."
        - 状态: "正在读取 `project_roadmap.md` 以识别当前周期的执行序列。"

1.  **Identify Next Task from Unified Sequence**:
    1.  **从统一序列中识别下一个任务**:
    *   Locate the "Unified Execution Sequence" checklist for the current cycle within the roadmap.
        - 定位路线图中当前周期的"统一执行序列"检查清单。
    *   Scan the list for the **first task that is not marked as complete** (i.e., the first `[ ]`). This is the `[Current_Task_File_Path]`.
        - 扫描列表中的**第一个未标记为完成的任务**(即第一个 `[ ]`)。这是 `[Current_Task_File_Path]`。
    *   **If no incomplete tasks are found**: The execution for this cycle is complete. State: "All tasks in the project roadmap's execution sequence are complete. Proceeding to exit phase." **Go to Section I, Exiting Execution Phase.**
        - **如果未找到未完成的任务**: 此周期的执行已完成。状态:"项目路线图的执行序列中的所有任务都已完成。正在退出阶段。"**转到第一节,退出执行阶段。**
    *   **If a task is found**: State: "Next task identified from roadmap: `[Current_Task_File_Path]`."
        - **如果找到任务**: 状态:"从路线图中识别的下一个任务:`[Current_Task_File_Path]`。"

2.  **Load Parent Plan (Context)**: Read the parent `implementation_plan_*.md` file (or relevant section of `*_module.md`) that contains the task. This provides higher-level objectives and context. State: "Reading parent plan `{plan_name}.md` for task context."
    2.  **加载父计划(上下文)**: 读取包含任务的父 `implementation_plan_*.md` 文件(或 `*_module.md` 的相关部分)。这提供了更高级别的目标和上下文。状态:"正在为任务上下文读取父计划 `{plan_name}.md`。"
3.  **Load Task Instruction**: Read the specific `Execution_{task_name}.md` file.
    3.  **加载任务说明**: 读取特定的 `Execution_{task_name}.md` 文件。
4.  **Load Dependencies (MANDATORY PRE-EXECUTION STEP)**:
    4.  **加载依赖关系(强制执行前步骤)**:
    *   **Identify Dependencies**: Review the `Context/Dependencies` section of the Task Instruction file *and* run `show-dependencies --key <key>` for the primary file(s) being modified by this task. (Find the key using `analyze-project` output or by convention if unsure). State: "Checking dependencies for task target(s) using `show-dependencies`."
        - **识别依赖关系**: 审查任务说明文件的 `Context/Dependencies` 部分*并*为此任务修改的主要文件运行 `show-dependencies --key <key>`。(使用 `analyze-project` 输出或约定(如果不确定)来查找键)。状态:"正在使用 `show-dependencies` 检查任务目标的依赖关系。"
    *   **Read Dependent Files**: **Crucially, use `read_file` to load the content of files identified as direct dependencies** ('<', '>', 'x', 'd' relationships relevant to the task) from `show-dependencies` output and the task's explicit context list. **Failure to gather context from dependent files before coding/modification is a HIGH RISK for introducing errors and logical inconsistencies.** State: "Reading content of dependent files: `{file_path_1}`, `{file_path_2}`..."
        - **读取依赖文件**: **至关重要的是,使用 `read_file` 加载从 `show-dependencies` 输出和任务的显式上下文列表中识别为直接依赖**('<'、'>'、'x'、'd' 关系与任务相关)**的文件的内容。**在编码/修改之前未能从依赖文件收集上下文是引入错误和逻辑不一致的高风险。** 状态:"正在读取依赖文件的内容:`{file_path_1}`, `{file_path_2}`..."
    *   **Load Other Explicit Context**: Use `read_file` to load any other specific Task Instructions, documentation files, or code snippets explicitly listed as required context in the current task file.
        - **加载其他显式上下文**: 使用 `read_file` 加载当前任务文件中明确列为所需上下文的任何其他特定任务说明、文档文件或代码片段。

---

## III. Executing Tasks from Instruction Files
## III. 从说明文件执行任务

**Action**: Execute the step-by-step plan detailed in the loaded Task Instruction file, maintaining awareness of its place in the hierarchy and its dependencies.
**操作**: 执行加载的任务说明文件中详述的逐步计划,保持对其在层次中的位置及其依赖关系的认识。

**Procedure:**
**程序:**
1.  **Iterate Through Steps:** For each numbered step in the Task Instruction file:
    1.  **迭代步骤**: 对于任务说明文件中的每个编号步骤:
    *   **A. Understand the Step**: Read the step's description. Clarify the specific action required, considering the overall task objective and the context from the parent Implementation Plan (loaded in Section II).
        - **A. 理解步骤**: 阅读步骤描述。澄清所需的特定操作,考虑整体任务目标和来自父实施计划的上下文(在第二节中加载)。
    *   **B. Review Dependencies & Context (MANDATORY REINFORCEMENT)**: **Before generating or modifying *any* code or significant file content for this specific step:**
        - **B. 审查依赖关系和上下文(强制加强)**: **在为此特定步骤生成或修改*任何*代码或重要文件内容之前**:
        *   Re-check dependencies using `show-dependencies --key <target_file_key>` if the step involves complex interactions or if context might be stale.
            - 如果步骤涉及复杂交互或上下文可能过时,请使用 `show-dependencies --key <target_file_key>` 重新检查依赖关系。
        *   **CRITICAL**: Ensure you have **read and understood the relevant content (`read_file`) of the directly dependent files** identified in Section II.4. How does this step interact with those dependencies (e.g., calling functions, using data structures, implementing interfaces)? State: "Confirming understanding of interaction with dependencies `{key_1}`, `{key_2}` based on previously read files before proceeding with step."
            - **关键**: 确保您已**阅读并理解第二节.4 中识别的直接依赖文件的相关内容(`read_file`)**。此步骤如何与这些依赖关系交互(例如,调用函数、使用数据结构、实现接口)? 状态:"正在根据之前读取的文件确认对依赖关系 `{key_1}`, `{key_2}` 的交互理解,然后再继续执行步骤。"
    *   **C. Pre-Action Verification (MANDATORY for File Modifications)**: Before using tools that modify files (`replace_in_file`, `write_to_file` on existing files, `execute_command` that changes files):
        - **C. 操作前验证(文件修改强制)**: 在使用修改文件的工具(`replace_in_file`、对现有文件的 `write_to_file`、更改文件的 `execute_command`)之前:
        *   Re-read the specific target file(s) for this step using `read_file`.
            - 使用 `read_file` 重新读取此步骤的特定目标文件。
        *   Generate a "Pre-Action Verification" Chain-of-Thought:
            - 生成"操作前验证"思维链:
            1.  **Intended Change**: Clearly state the modification planned for this step (e.g., "Insert function X at line Y in file Z").
                1.  **预期更改**: 清楚地说明为此步骤计划的修改(例如,"在文件 Z 的第 Y 行插入函数 X")。
            2.  **Dependency Context Summary**: Briefly summarize how the intended change relates to the critical dependencies reviewed in III.1.B (e.g., "Function X implements interface defined in dependent file A", "Change adheres to data format expected by dependent function B").
                2.  **依赖上下文摘要**: 简要总结预期更改如何与第三节.1.B 中审查的关键依赖关系相关(例如,"函数 X 实现依赖文件 A 中定义的接口","更改遵循依赖函数 B 预期的数据格式")。
            3.  **Expected Current State**: Describe the specific part of the file you expect to see before the change (e.g., "Expect line Y to be empty", "Expect function signature Z to be present").
                3.  **预期当前状态**: 描述您希望在更改之前看到的文件的特定部分(例如,"期望第 Y 行为空","期望存在函数签名 Z")。
            4.  **Actual Current State**: Note the actual state observed from the `read_file` output.
                4.  **实际当前状态**: 注意从 `read_file` 输出中观察到的实际状态。
            5.  **Validation**: Compare expected and actual state. Proceed **only if** they match reasonably AND the intended change is consistent with the dependency context summary. If validation fails, **STOP**, state the discrepancy, and re-evaluate the step, plan, or dependencies. Ask for clarification if needed.
                5.  **验证**: 比较预期和实际状态。**仅在**它们合理匹配并且预期更改与依赖上下文摘要一致时才继续。如果验证失败,**停止**,说明差异,并重新评估步骤、计划或依赖关系。如果需要,请求澄清。
        *   Example:
            *   示例:
            ```
            Pre-Action Verification:
            1. Intended Change: Replace line 55 in `game_logic.py` (Key: 2Ca1) with `new_score = calculate_score(data, multipliers)`.
            2. Dependency Context Summary: `calculate_score` is imported from `scoring_utils.py` (Key: 2Cb3, dependency confirmed via show-dependencies & read_file). It expects `data` (dict) and `multipliers` (list). `game_logic.py` has access to these variables in scope.
            3. Expected Current State: Line 55 contains the old calculation `new_score = data['base'] * 1.1`.
            4. Actual Current State: Line 55 is `new_score = data['base'] * 1.1`.
            5. Validation: Match confirmed. Change is consistent with dependency context. Proceeding with `replace_in_file`.
            ```
            ```
            操作前验证:
            1. 预期更改: 将 `game_logic.py`(键: 2Ca1)中的第 55 行替换为 `new_score = calculate_score(data, multipliers)`。
            2. 依赖上下文摘要: `calculate_score` 从 `scoring_utils.py`(键: 2Cb3,通过 show-dependencies 和 read_file 确认依赖关系)导入。它期望 `data`(dict)和 `multipliers`(list)。`game_logic.py` 可以访问作用域内的这些变量。
            3. 预期当前状态: 第 55 行包含旧的计算 `new_score = data['base'] * 1.1`。
            4. 实际当前状态: 第 55 行是 `new_score = data['base'] * 1.1`。
            5. 验证: 匹配确认。更改与依赖上下文一致。正在继续使用 `replace_in_file`。
            ```
    *   **D. Perform Action**: Execute the action described in the step using the appropriate tool (`write_to_file`, `execute_command`, `replace_in_file`, etc.).
        - **D. 执行操作**: 使用适当的工具(`write_to_file`、`execute_command`、`replace_in_file` 等)执行步骤中描述的操作。
    *   **E. Document Results (Mini-CoT)**: Immediately after the action, record the outcome:
        - **E. 记录结果(Mini-CoT)**: 在操作后立即记录结果:
        *   **Action Taken**: Briefly restate the action performed.
            - **执行的操作**: 简要重申执行的操作。
        *   **Result**: Success, failure, command output, generated content snippet.
            - **结果**: 成功、失败、命令输出、生成的内容片段。
        *   **Observations**: Any unexpected behavior, potential issues, or insights gained.
            - **观察**: 任何意外行为、潜在问题或获得的见解。
        *   **Next**: Confirm moving to the next step or handling an error.
            - **下一步**: 确认移动到下一步或处理错误。
    *   **F. MUP**: Follow Core MUP (Section VI of Core Prompt) and Section IV additions below. **Perform MUP after each step.**
        - **F. MUP**: 遵循核心 MUP(核心提示第六节)和下面的第四节附加内容。**在每一步后执行 MUP。**

2.  **Error Handling:** If an action fails or produces unexpected results:
    2.  **错误处理**: 如果操作失败或产生意外结果:
    *   Document the error message and the Mini-CoT leading up to it.
        - 记录错误消息和导致它的 Mini-CoT。
    *   Diagnose the cause: Check command syntax, file paths, permissions, dependency conflicts (referencing context from III.1.B), or logical errors in generated code/instructions. Consult Core Prompt Section VIII for dependency command error details if applicable.
        - 诊断原因: 检查命令语法、文件路径、权限、依赖冲突(引用第三节.1.B 的上下文)或生成代码/说明中的逻辑错误。如果适用,请参阅核心提示第八节了解依赖命令错误详细信息。
    *   Propose a resolution: Correct the command, revise the code logic based on dependency understanding, adjust the task instructions, or query the user if the plan seems flawed.
        - 提出解决方案: 更正命令,根据依赖理解修改代码逻辑,调整任务说明,或如果计划似乎有缺陷则查询用户。
    *   Execute the fix.
        - 执行修复。
    *   Document the resolution process.
        - 记录解决过程。
    *   Apply MUP post-resolution before continuing.
        - 在继续之前应用解决后 MUP。

3.  **Code Generation and Modification Guidelines:**
    3.  **代码生成和修改指南:**
    *(Reminder: Before generating/modifying code, ensure Step III.1.B 'Review Dependencies & Context' including reading dependent files was performed)*
    *(提醒: 在生成/修改代码之前,确保已执行步骤 III.1.B "审查依赖关系和上下文",包括读取依赖文件)*
    When performing actions that involve writing or changing code, adhere strictly to the following:
    在执行涉及编写或更改代码的操作时,严格遵守以下内容:
    1.  **Context-Driven**:
        1.  **上下文驱动**:
     - Code **must** align with the interactions, interfaces, data formats, and requirements identified during dependency review (III.1.B) and pre-action verification (III.1.C).
         - 代码**必须**与依赖关系审查(III.1.B)和操作前验证(III.1.C)期间识别的交互、接口、数据格式和要求保持一致。
    2.  **Modularity**:
        2.  **模块化**:
     - Write small, focused functions/methods/classes. Aim for high cohesion and low coupling.
         - 编写小型、专注的函数/方法/类。以高内聚和低耦合为目标。
     - Design reusable components to enhance maintainability.
         - 设计可重用的组件以增强可维护性。
    3.  **Clarity and Readability**:
        3.  **清晰性和可读性**:
     - Use meaningful names for variables, functions, and classes.
         - 为变量、函数和类使用有意义的名称。
     - Follow language-specific formatting conventions (e.g., PEP 8 for Python).
         - 遵循特定语言的格式约定(例如 Python 的 PEP 8)。
     - Add comments only for complex logic or intent, avoiding redundant explanations of *what* the code does.
         - 仅对复杂逻辑或意图添加注释,避免对代码*做*什么进行冗余解释。
     - Provide complete, runnable code blocks or snippets as appropriate for the task step.
         - 根据任务步骤提供完整的、可运行的代码块或片段。
    4.  **Error Handling**:
        4.  **错误处理**:
     - Anticipate errors (e.g., invalid inputs, file not found) and implement robust handling (e.g., try-except, return value checks).
         - 预见错误(例如无效输入、文件未找到)并实现强大的处理(例如 try-except、返回值检查)。
     - Validate inputs and assumptions to prevent errors early.
         - 验证输入和假设以尽早防止错误。
    5.  **Efficiency**:
        5.  **效率**:
     - Prioritize clarity and correctness but be mindful of algorithmic complexity for performance-critical tasks.
         - 优先考虑清晰性和正确性,但要注意性能关键任务的算法复杂性。
    6.  **Documentation**:
        6.  **文档**:
     - Add docstrings or comments for public APIs or complex functions, detailing purpose, parameters, and return values.
         - 为公共 API 或复杂函数添加文档字符串或注释,详细说明目的、参数和返回值。
     - Keep documentation concise and synchronized with code changes.
         - 保持文档简洁并与代码更改同步。
    7.  **Testing**:
        7.  **测试**:
     - Write testable code and, where applicable, suggest or include unit tests for new functionality or fixes.
         - 编写可测试的代码,并在适用时建议或包含新功能或修复的单元测试。
    8.  **Dependency Management**:
        8.  **依赖管理**:
     - Use existing dependencies where possible. Avoid adding new external libraries unless explicitly planned.
         - 尽可能使用现有依赖。避免添加新的外部库,除非明确计划。
     - If code changes introduce *new functional dependencies* between project files, prepare to update the relevant mini-tracker (see MUP Additions, Section IV).
         - 如果代码更改在项目文件之间引入*新的功能依赖*,准备更新相关的小型跟踪器(见 MUP 附加内容,第四节)。
    9.  **Security**:
        9.  **安全性**:
   - Follow secure coding practices to mitigate vulnerabilities (e.g., avoid injection risks, secure credential handling).
     - 遵循安全编码实践以减轻漏洞(例如避免注入风险、安全凭证处理)。

4.  **Execution Flowchart**
    4.  **执行流程图**

```mermaid
flowchart TD
    subgraph Task Selection
        Start_Exec[Start Execution Phase] --> Load_Roadmap[Load project_roadmap.md]
        Load_Roadmap --> Find_Next_Task{Find Next Incomplete Task in Sequence}
        Find_Next_Task -- Task Found --> Load_Task_File[Load Task Instruction File]
        Find_Next_Task -- No Tasks Left --> End_Phase[Exit Execution Phase]
    end

    subgraph Task Execution
        Load_Task_File --> Load_Context[Load Parent Plan & Dependencies]
        Load_Context --> A[Start Step] --> B[Understand Step]
        B --> C[Review Dependencies & Read Context Files<br>MANDATORY]
        C --> D{File Modification?}
        D -- Yes --> E[Pre-Action Verification<br> with Context]
        D -- No --> G[Perform Action]
        E -- Match & Valid --> G
        E -- No Match or Invalid --> F[Re-evaluate Plan/Context]
        F --> B
        G --> H[Document Results]
        H --> I{Error?}
        I -- Yes --> J[Handle Error]
        I -- No --> K[MUP]
        J --> K
        K --> L{Next Step in Task?}
        L -- Yes --> A
        L -- No --> M[End Task - Update Roadmap]
    end

    M --> Find_Next_Task
```
代码说明: This flowchart illustrates the execution phase workflow, showing how tasks are selected from the roadmap, context is loaded, dependencies are reviewed, actions are performed with verification, and errors are handled.
代码说明: 此流程图说明了执行阶段工作流程,显示了如何从路线图选择任务、加载上下文、审查依赖关系、通过验证执行操作以及处理错误。

---

## IV. Execution Plugin - MUP Additions
## IV. 执行插件 - MUP 附加内容

After Core MUP steps (Section VI of Core Prompt), performed *after each step* of the Task Instruction:
在核心 MUP 步骤(核心提示第六节)之后,在任务说明的*每一步*之后执行:
1.  **Update Task Instruction File**:
    1.  **更新任务说明文件**:
    *   Mark the just-completed step (e.g., add `[DONE]` or similar marker).
        - 标记刚刚完成的步骤(例如,添加 `[DONE]` 或类似标记)。
    *   Save any significant observations or results from the Mini-CoT directly into the task file as notes for the relevant step, if useful for context later. Avoid changing the core instructions unless correcting an error found during execution.
        - 将 Mini-CoT 中的任何重要观察或结果直接保存到任务文件中作为相关步骤的注释,如果对以后的上下文有用。除非更正在执行期间发现的错误,否则避免更改核心说明。
    *   If the task is now fully complete, update its overall status section.
        - 如果任务现在完全完成,则更新其整体状态部分。
    *   Use `write_to_file` to save changes.
        - 使用 `write_to_file` 保存更改。
2.  **Update Mini-Trackers (If New Functional Dependency Created)**:
    2.  **更新小型跟踪器(如果创建了新的功能依赖)**:
    *   **Condition**: If the executed step modified code in file A (key `key_A`) such that it *now* directly imports, calls, or functionally relies on code/data in file B (key `key_B`) *within the same module*, and this dependency didn't exist before or wasn't accurately reflected.
        - **条件**: 如果执行的步骤修改了文件 A(键 `key_A`)中的代码,使其*现在*直接导入、调用或在功能上依赖同一模块内文件 B(键 `key_B`)中的代码/数据,并且这种依赖关系以前不存在或未准确反映。
    *   **Action**: Use `add-dependency` on the relevant `{module_name}_module.md` mini-tracker.
        - **操作**: 在相关的 `{module_name}_module.md` 小型跟踪器上使用 `add-dependency`。
    *   **Reasoning (Mandatory)**: Clearly state why the dependency is being added/updated based *specifically* on the code change made in this step.
        - **推理(强制)**: 根据*具体*在此步骤中所做的代码更改,清楚地说明为什么添加/更新依赖关系。
    *   Example (adding dependency from function/file 2Ca1 to 2Ca3 within module 'C' after adding an import):
        - 示例(在添加导入后,在模块 'C' 中从函数/文件 2Ca1 添加到 2Ca3 的依赖):
        ```bash
        # MUP Trigger: Step X added 'from .file3 import specific_func' to file associated with key 2Ca1.
        # Reasoning: This creates a new functional dependency where 2Ca1 now requires 2Ca3 for specific_func.
        python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker path/to/module_C/module_C_module.md --source-key 2Ca1 --target-key 2Ca3 --dep-type "<"
        ```
        ```bash
        # MUP 触发器: 步骤 X 在与键 2Ca1 关联的文件中添加了 'from .file3 import specific_func'。
        # 推理: 这创建了一个新的功能依赖,其中 2Ca1 现在需要 2Ca3 来使用 specific_func。
        python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker path/to/module_C/module_C_module.md --source-key 2Ca1 --target-key 2Ca3 --dep-type "<"
        ```
        *(Use correct dep-type: '<' if A calls B, '>' if B calls A, 'x' if mutual, 'd' if essential doc link)*
        *(使用正确的 dep-type: '<' 如果 A 调用 B,'>' 如果 B 调用 A,'x' 如果相互,'d' 如果是重要的文档链接)*
3.  **Update Domain Module / Implementation Plan Documents (If Significant)**: If the task execution led to a significant design change or outcome not captured in the original plan, briefly note this in the relevant Domain Module (`*_module.md`) or Implementation Plan (`implementation_plan_*.md`).
    3.  **更新域模块/实施计划文档(如果重要)**: 如果任务执行导致原始计划中未捕获的重大设计变更或结果,请在相关的域模块(`*_module.md`)或实施计划(`implementation_plan_*.md`)中简要说明。
4.  **Update `.clinerules` [LAST_ACTION_STATE]:** Update `last_action`, `current_phase`, `next_action`, `next_phase`.
    4.  **更新 `.clinerules` [LAST_ACTION_STATE]**: 更新 `last_action`、`current_phase`、`next_action`、`next_phase`。
    *   After a step:
        - 在一步之后:
        ```
        [LAST_ACTION_STATE]
        last_action: "Completed Step {N} in Execution_{task_name}.md"
        current_phase: "Execution"
        next_action: "Execute Step {N+1} in Execution_{task_name}.md"
        next_phase: "Execution"
        ```
        ```
        [LAST_ACTION_STATE]
        last_action: "Completed Step {N} in Execution_{task_name}.md"
        current_phase: "Execution"
        next_action: "Execute Step {N+1} in Execution_{task_name}.md"
        next_phase: "Execution"
        ```
    *   After completing the last step in a task:
        - 在完成任务中的最后一步之后:
        ```
        [LAST_ACTION_STATE]
        last_action: "Completed all steps in Execution_{task_name}.md"
        current_phase: "Execution"
        next_action: "Select next Execution task or transition phase"
        next_phase: "Execution" # Default, change only when *all* planned tasks are done.
        ```
        ```
        [LAST_ACTION_STATE]
        last_action: "Completed all steps in Execution_{task_name}.md"
        current_phase: "Execution"
        next_action: "Select next Execution task or transition phase"
        next_phase: "Execution" # 默认,仅在*所有*计划任务完成时更改。
        ```
    *   Upon exiting the phase (as defined in Section I): Use the appropriate state from Section I.
        - 退出阶段时(如第一节所定义): 使用第一节中的适当状态。

---

## V. Quick Reference
## V. 快速参考
- **Objective**: Execute planned `Execution_*` tasks step-by-step, modifying files/code according to instructions, dependencies, and quality guidelines.
    - **目标**: 逐步执行计划的 `Execution_*` 任务,根据说明、依赖关系和质量指南修改文件/代码。
- **Key Actions**:
    - **关键操作**:
    - Load context: Parent Plan -> Task Instruction -> Dependencies (`show-dependencies` + `read_file`).
        - 加载上下文: 父计划 -> 任务说明 -> 依赖关系(`show-dependencies` + `read_file`)。
    - Execute steps sequentially.
        - 按顺序执行步骤。
    - **MANDATORY**: Review dependencies & **read context files** before coding/modification.
        - **强制**: 在编码/修改之前审查依赖关系并**读取上下文文件**。
    - **MANDATORY**: Perform pre-action verification for file modifications.
        - **强制**: 对文件修改执行操作前验证。
    - Follow code quality guidelines.
        - 遵循代码质量指南。
    - Document results (Mini-CoT) after each action.
        - 在每次操作后记录结果(Mini-CoT)。
    - Perform MUP after each action.
        - 在每次操作后执行 MUP。
    - Update mini-trackers (`add-dependency`) if new functional dependencies are created.
        - 如果创建了新的功能依赖,更新小型跟踪器(`add-dependency`)。
- **Key Inputs**: Prioritized Task list (from Strategy), `implementation_plan_*.md`, `Execution_*.md`, dependency tracker info (`show-dependencies`), content of dependent files (`read_file`).
    - **关键输入**: 优先级任务列表(来自策略)、`implementation_plan_*.md`、`Execution_*.md`、依赖跟踪器信息(`show-dependencies`)、依赖文件的内容(`read_file`)。
- **Key Outputs**: Modified project files (code, docs), updated `activeContext.md`, updated task instruction files, potentially updated mini-trackers, updated `.clinerules`.
    - **关键输出**: 修改的项目文件(代码、文档)、更新的 `activeContext.md`、更新的任务说明文件、可能更新的小型跟踪器、更新的 `.clinerules`。
- **MUP Additions**: Update instruction files (step completion, notes), mini-trackers (if needed), potentially Plans/Modules, and `.clinerules`.
    - **MUP 附加内容**: 更新说明文件(步骤完成、注释)、小型跟踪器(如果需要)、可能的计划/模块和 `.clinerules`。
