# **Cline Recursive Chain-of-Thought System (CRCT) - Cleanup/Consolidation Plugin**

# **Cline 递归思维链系统 (CRCT) - 清理/整合插件**

**This Plugin provides detailed instructions and procedures for the Cleanup/Consolidation phase of the CRCT system. It should be used in conjunction with the Core System Prompt.**

**本插件为 CRCT 系统的清理/整合阶段提供详细的说明和程序。它应与核心系统提示词结合使用。**

---

## I. Entering and Exiting Cleanup/Consolidation Phase

## I. 进入和退出清理/整合阶段

**Entering Cleanup/Consolidation Phase:**
**进入清理/整合阶段：**
1. **`.clinerules` Check**: Always read `.clinerules` first. If `[LAST_ACTION_STATE]` shows `next_phase: "Cleanup/Consolidation"`, proceed with these instructions. This phase typically follows the Execution phase.

1. **`.clinerules` 检查**：始终首先读取 `.clinerules`。如果 `[LAST_ACTION_STATE]` 显示 `next_phase: "Cleanup/Consolidation"`，则按照这些说明继续操作。此阶段通常跟在执行阶段之后。

2. **User Trigger**: Start a new session if the system is paused after Execution, awaiting this phase.

2. **用户触发**：如果系统在执行后暂停，等待此阶段，则启动新会话。

**Exiting Cleanup/Consolidation Phase:**
**退出清理/整合阶段：**
1. **Completion Criteria:**
   - Consolidation steps (Section III) are complete: relevant information integrated into persistent docs, changelog reorganized.

1. **完成标准**：
   - 整合步骤（第三节）已完成：相关信息已整合到持久化文档中，变更日志已重新组织。
   - Cleanup steps (Section IV) are complete: obsolete files identified and archived/removed.
   - 清理步骤（第四节）已完成：已识别过时文件并已归档/删除。
   - `activeContext.md` reflects the clean, consolidated state.
   - `activeContext.md` 反映了干净、整合的状态。
   - MUP is followed for all actions.
   - 所有操作都遵循了 MUP。

2. **`.clinerules` Update (MUP):**
   - Typically transition back to Set-up/Maintenance for verification or Strategy for next planning cycle:

2. **`.clinerules` 更新 (MUP)**：
   - 通常转换回设置/维护以进行验证，或转换到策略以进行下一个规划周期：

     ```
     [LAST_ACTION_STATE]
     last_action: "Completed Cleanup/Consolidation Phase"
     current_phase: "Cleanup/Consolidation"
     next_action: "Phase Complete - User Action Required"
     next_phase: "Set-up/Maintenance" # Or "Strategy" if planning next cycle immediately
     ```

     ```
     [LAST_ACTION_STATE]
     last_action: "Completed Cleanup/Consolidation Phase"
     current_phase: "Cleanup/Consolidation"
     next_action: "Phase Complete - User Action Required"
     next_phase: "Set-up/Maintenance" # 或 "Strategy"（如果立即规划下一个周期）
     ```

   - *Alternative: If the project is now considered fully complete:*

   - *备选方案：如果项目现在被认为完全完成：*

     ```
     [LAST_ACTION_STATE]
     last_action: "Completed Cleanup/Consolidation Phase - Project Finalized"
     current_phase: "Cleanup/Consolidation"
     next_action: "Project Completion - User Review"
     next_phase: "Project Complete"
     ```

3. **User Action**: After updating `.clinerules`, pause for user to trigger the next phase.

3. **用户操作**：更新 `.clinerules` 后，暂停等待用户触发下一阶段。

---

## II. Phase Objective

## II. 阶段目标

**Objective**: To systematically review the project state after a cycle of execution, consolidate essential information and learnings into persistent documentation (HDTA, core files), **reorganize the changelog for better readability**, and clean up temporary or obsolete files (like completed Task Instructions, session trackers, and temporary consolidation notes) to maintain a focused and relevant project context.

**目标**：在执行周期后系统性地审查项目状态，将重要信息和学习内容整合到持久化文档（HDTA、核心文件）中，**重新组织变更日志以提高可读性**，并清理临时或过时的文件（如已完成任务指令、会话跟踪器和临时整合笔记），以保持专注和相关的项目上下文。

**Workflow Order**: Consolidation MUST happen *before* Cleanup.

**工作流顺序**：整合*必须*在清理之前进行。

---

## III. Consolidation Workflow

## III. 整合工作流

**Goal**: Synthesize key information, decisions, and learnings from the recent execution cycle into the core project documentation, and reorganize the changelog by component/module.

**目标**：将最近执行周期中的关键信息、决策和学习内容综合到核心项目文档中，并按组件/模块重新组织变更日志。

<<<***CRITICAL WARNING***>>>
<<<***关键警告***>>>
*You **must** verify the base file's state by manually reading it to determine completion status. For code files read the actual code. For documentation, read the associated documents.*

*您**必须**通过手动读取基础文件来验证其状态以确定完成状态。对于代码文件，请阅读实际代码。对于文档，请阅读相关文档。*

**Procedure:**
**程序：**

1.  **Review and Verify All Relevant Project Documentation and Task States (CRITICAL)**:
    *   **a. Identify HDTA Document Structure and Other Strategic Trackers**:

1.  **审查和验证所有相关项目文档和任务状态（关键）**：
    *   **a. 识别 HDTA 文档结构和其他战略跟踪器**：

        *   **Action**: Review files in `cline_docs/templates/` to understand the standard structure and expected content for all HDTA document tiers (`system_manifest.md`, `*_module.md`, `implementation_plan_*.md`, `task_instruction.md`).

        *   **操作**：审查 `cline_docs/templates/` 中的文件，以了解所有 HDTA 文档层级的标准结构和预期内容（`system_manifest.md`、`*_module.md`、`implementation_plan_*.md`、`task_instruction.md`）。

        *   **Action**: Use `list_files` to search within `cline_docs/` (and potentially other relevant project documentation directories if custom locations are used) for any files matching patterns like `*roadmap*.md`, `*checklist*.md`, `*review_progress*.md`, or other strategic tracking documents.

        *   **操作**：使用 `list_files` 在 `cline_docs/` 中（以及如果使用自定义位置，可能还包括其他相关项目文档目录）搜索匹配模式的文件，如 `*roadmap*.md`、`*checklist*.md`、`*review_progress*.md` 或其他战略跟踪文档。

        *   **Purpose**: To ensure a complete understanding of the project's intended documentation structure and to identify all high-level tracking documents that need review and consolidation.

        *   **目的**：确保完全理解项目的预期文档结构，并识别所有需要审查和整合的高级跟踪文档。

    *   **b. List All Task Instruction Files**:
        *   **Action**: Use `list_files` recursively to identify all `*.md` files within the primary `tasks/` directory (and its subdirectories).

    *   **b. 列出所有任务指令文件**：
        *   **操作**：使用 `list_files` 递归识别主 `tasks/` 目录（及其子目录）中的所有 `*.md` 文件。

        *   **Action**: Use `list_files` recursively to identify all `*.md` files within the *entire* `cline_docs/archive/` directory (and its subdirectories) to locate any previously archived task files.

        *   **操作**：使用 `list_files` 递归识别*整个* `cline_docs/archive/` 目录（及其子目录）中的所有 `*.md` 文件，以定位任何先前归档的任务文件。

        *   **Purpose**: Create a comprehensive list of all available task instruction files, regardless of their current location (active or archived), for subsequent review in batches.

        *   **目的**：创建所有可用任务指令文件的全面列表，无论其当前位置（活动或已归档），以便后续批量审查。

    *   **c. List All Implementation Plan Files**:
        *   **Action**: For each directory listed in `[CODE_ROOT_DIRECTORIES]` (from `.clinerules`), use `list_files` recursively to identify all files matching the pattern `implementation_plan_*.md`. These are typically located within module directories (e.g., `src/module_name/implementation_plan_*.md`).

    *   **c. 列出所有实施计划文件**：
        *   **操作**：对于 `[CODE_ROOT_DIRECTORIES]`（来自 `.clinerules`）中列出的每个目录，使用 `list_files` 递归识别匹配模式 `implementation_plan_*.md` 的所有文件。这些通常位于模块目录内（例如，`src/module_name/implementation_plan_*.md`）。

        *   **Purpose**: Create a comprehensive list of all implementation plan files for subsequent review in batches.

        *   **目的**：创建所有实施计划文件的全面列表，以便后续批量审查。

    *   **d. Read Core Project State Files**:
        *   **Action**: Read `activeContext.md`: Identify key decisions, unresolved issues, and summaries of work done.

    *   **d. 读取核心项目状态文件**：
        *   **操作**：读取 `activeContext.md`：识别关键决策、未解决的问题和工作摘要。

        *   **Action**: Read `changelog.md`: Review all significant changes. **(Note: Will be reorganized in Step 3)**.

        *   **操作**：读取 `changelog.md`：审查所有重大变更。**（注：将在步骤 3 中重新组织）**。

        *   **Action**: Read `progress.md`: Check for all high-level milestones.

        *   **操作**：读取 `progress.md`：检查所有高级里程碑。

        *   **Purpose**: To gather current project state information that will inform the consolidation process.

        *   **目的**：收集当前项目状态信息，以指导整合过程。

    *   **e. Review All Identified Task Instruction Files in Batches (CRITICAL)**:
        *   **Purpose**: To identify significant implementation details, design choices, "gotchas," learnings, and to **CRITICALLY verify the actual completion status of tasks.** This review covers all task instruction files identified in step 1b, processed in batches to prevent context overload.

    *   **e. 批量审查所有已识别的任务指令文件（关键）**：
        *   **目的**：识别重要的实施细节、设计选择、"陷阱"、学习内容，并**关键性地验证任务的实际完成状态**。此审查涵盖步骤 1b 中识别的所有任务指令文件，分批处理以防止上下文过载。

        *   **Procedure**:
        *   **程序**：

            i. **Batch Creation**:
            i. **批次创建**：

                - **Action**: Divide the comprehensive list of Task Instruction files (from step 1b) into batches, with each batch containing **no more than 10 files**. If the total number of files is not evenly divisible by 10, the final batch may contain fewer than 10 files.

                - **操作**：将任务指令文件的全面列表（来自步骤 1b）分成批次，每批次包含**不超过 10 个文件**。如果文件总数不能被 10 整除，最后一批可能包含少于 10 个文件。

                - **Action**: Maintain a record of which files have been processed to ensure no files are missed or processed twice. This can be done internally or by updating a temporary tracking mechanism (e.g., a note in `activeContext.md` for the duration of this phase).

                - **操作**：维护已处理文件的记录，以确保没有文件被遗漏或重复处理。这可以内部完成，或通过更新临时跟踪机制（例如，在此阶段期间在 `activeContext.md` 中添加注释）来完成。

            ii. **Process Each Batch (Standalone Processing)**:
            ii. **处理每个批次（独立处理）**：

                - **Action**: For each batch of up to 10 Task Instruction files, **fully process the batch as a standalone task** before proceeding to the next batch. This means completing all verification, extraction, and updating actions for all files in the batch with no inter-batch dependencies for these actions.

                - **操作**：对于每批多达 10 个任务指令文件，在继续下一批次之前，**将批次完全作为独立任务处理**。这意味着完成批次中所有文件的所有验证、提取和更新操作，这些操作之间没有批次间依赖关系。

                - **Sub-Procedure (for each file in the batch)**:
                - **子程序（对于批次中的每个文件）**：

                    1. **Read the Task File**:
                    1. **读取任务文件**：

                        - **Action**: Use `read_file` to read the content of the task file.

                        - **操作**：使用 `read_file` 读取任务文件的内容。

                    2. **Verify Completion (Manual & CRITICAL)**:
                    2. **验证完成（手动和关键）**：

                        - **Verification Approach**:
                        - **验证方法**：

                            - For **Execution Tasks**: If the task file indicates a tangible action was taken on a project artifact (e.g., "applied x to y," "created file z," "modified function f in file w," "updated documentation q"), you **MUST** manually verify this outcome by examining the target artifact.

                            - 对于**执行任务**：如果任务文件指示对项目工件执行了具体操作（例如，"将 x 应用于 y"、"创建文件 z"、"修改文件 w 中的函数 f"、"更新文档 q"），您**必须**通过检查目标工件来手动验证此结果。

                            - For **Strategy Tasks**: Verification involves confirming that the planned output of the strategy task (e.g., a design document, a research summary, a set of defined requirements, a completed exploration) has been produced, is complete, and meets the task's objectives. This may involve reading the output document(s) or assessing the completeness of the strategic analysis presented in the task file itself.

                            - 对于**策略任务**：验证涉及确认策略任务的计划输出（例如，设计文档、研究摘要、一组定义的需求、已完成的探索）已产生、完整并满足任务目标。这可能涉及读取输出文档或评估任务文件本身中呈现的战略分析的完整性。

                        - **Action**: Use `read_file` to examine target artifacts or output documents, or use `list_files` to confirm existence/modification as appropriate. Consult `changelog.md` entries if they provide specific file modification details related to the task.

                        - **操作**：使用 `read_file` 检查目标工件或输出文档，或根据需要使用 `list_files` 确认存在/修改。如果 `changelog.md` 条目提供与任务相关的具体文件修改详细信息，请查阅它们。

                        - **If the outcome is NOT verified** (e.g., 'x' was not applied to 'y', file 'z' does not contain expected content, function 'f' was not modified as described):

                        - **如果结果未验证**（例如，'x' 未应用于 'y'，文件 'z' 不包含预期内容，函数 'f' 未按描述修改）：

                            - Clearly note this discrepancy for this task file.

                            - 明确记录此任务文件的差异。

                            - **Action (CRITICAL)**: If the task file has a "Status: Completed" marker (or all its internal steps are checked off implying completion), this status is now considered **invalid**. You **MUST** update the task file itself to remove or clearly mark the "Completed" status as incorrect/unverified (e.g., change to "Status: Pending Verification" or "Status: Incomplete - Outcome Not Verified").

                            - **操作（关键）**：如果任务文件有"状态：已完成"标记（或其所有内部步骤都已勾选，暗示完成），则此状态现在被视为**无效**。您**必须**更新任务文件本身，删除或清楚地将"已完成"状态标记为不正确/未验证（例如，更改为"状态：待验证"或"状态：未完成 - 结果未验证"）。

                            - **Action (CRITICAL)**: Identify ALL documents that reference this task as completed. This includes (but is not limited to) parent Implementation Plan(s), any `*checklist*.md` files, `*roadmap*.md` files, `progress.md`, and potentially `activeContext.md`. Update these referencing documents to reflect the task's true (unverified/incomplete) status.

                            - **操作（关键）**：识别将此任务引用为已完成的所有文档。这包括（但不限于）父实施计划、任何 `*checklist*.md` 文件、`*roadmap*.md` 文件、`progress.md` 以及可能的 `activeContext.md`。更新这些引用文档以反映任务的真实（未验证/未完成）状态。

                            - **Note**: This task file **MUST NOT** be archived as "complete" in Section IV. It may require a new task to be created in a subsequent phase to address the incompletion.

                            - **注**：此任务文件**不得**在第四节中作为"完整"归档。可能需要在后续阶段创建新任务来处理未完成的部分。

                    3. **Extract Consolidatable Information (CRITICAL)**:
                    3. **提取可整合信息（关键）**：

                        - Regardless of verified completion status, identify any design decisions, new information, important learnings, "gotchas," or deviations from original plans noted *within* the task file.

                        - 无论验证完成状态如何，识别任务文件中记录的任何设计决策、新信息、重要学习内容、"陷阱"或与原始计划的偏差。

                        - **Action**: Record this information in a temporary file, `consolidation_notes.md`, located in `cline_docs/`. Append each piece of information with a reference to the source file and batch number (e.g., "Batch 1, task_abc.md: Learned that algorithm X is suboptimal for large datasets"). Use `write_to_file` or `apply_diff` to update `consolidation_notes.md`.

                        - **操作**：将此信息记录在位于 `cline_docs/` 的临时文件 `consolidation_notes.md` 中。为每条信息附加源文件和批次的引用（例如，"批次 1，task_abc.md：了解到算法 X 对于大型数据集不是最优的"）。使用 `write_to_file` 或 `apply_diff` 更新 `consolidation_notes.md`。

                - **Action**: After fully processing all files in the current batch (i.e., all files have been read, verified, updated if necessary, and their consolidatable information recorded in `consolidation_notes.md`), document the completion of the batch in `activeContext.md` (e.g., "Completed verification and extraction for batch X containing files [file1, file2, ...]. Information recorded in `consolidation_notes.md`."). Only then proceed to the next batch.

                - **操作**：在完全处理当前批次中的所有文件后（即所有文件都已读取、验证、必要时更新，并且其可整合信息已记录在 `consolidation_notes.md` 中），在 `activeContext.md` 中记录批次的完成情况（例如，"完成了包含文件 [file1、file2、...] 的批次 X 的验证和提取。信息已记录在 `consolidation_notes.md` 中。"）。只有这样才继续下一批次。

                - **Purpose**: Processing each batch as a standalone task ensures that all critical actions are completed without relying on future batches, reducing context overload while maintaining comprehensive verification and extraction.

                - **目的**：将每个批次作为独立任务处理，确保在不依赖未来批次的情况下完成所有关键操作，减少上下文过载，同时保持全面的验证和提取。

    *   **f. Review All Identified Implementation Plan Files in Batches (CRITICAL)**:
        *   **Purpose**: To consolidate strategic decisions, outcomes, and ensure alignment with completed (and verified) tasks. This review covers all files identified in step 1c, processed in batches to prevent context overload.

    *   **f. 批量审查所有已识别的实施计划文件（关键）**：
        *   **目的**：整合战略决策和结果，并确保与已完成（和已验证）的任务保持一致。此审查涵盖步骤 1c 中识别的所有文件，分批处理以防止上下文过载。

        *   **Procedure**:
        *   **程序**：

            i. **Batch Creation**:
            i. **批次创建**：

                - **Action**: Divide the comprehensive list of Implementation Plan files (from step 1c) into batches, with each batch containing **no more than 10 files**. If the total number of files is not evenly divisible by 10, the final batch may contain fewer than 10 files.

                - **操作**：将实施计划文件的全面列表（来自步骤 1c）分成批次，每批次包含**不超过 10 个文件**。如果文件总数不能被 10 整除，最后一批可能包含少于 10 个文件。

                - **Action**: Maintain a record of which files have been processed to ensure no files are missed or processed twice.

                - **操作**：维护已处理文件的记录，以确保没有文件被遗漏或重复处理。

            ii. **Process Each Batch (Standalone Processing)**:
            ii. **处理每个批次（独立处理）**：

                - **Action**: For each batch of up to 10 Implementation Plan files, **fully process the batch as a standalone task** before proceeding to the next batch. This means completing all reading, analysis, updating, and extraction actions for all files in the batch with no inter-batch dependencies for these actions.

                - **操作**：对于每批多达 10 个实施计划文件，在继续下一批次之前，**将批次完全作为独立任务处理**。这意味着完成批次中所有文件的所有读取、分析、更新和提取操作，这些操作之间没有批次间依赖关系。

                - **Sub-Procedure (for each file in the batch)**:
                - **子程序（对于批次中的每个文件）**：

                    1. **Read the Implementation Plan**:
                    1. **读取实施计划**：

                        - **Action**: Use `read_file` to read the content of the implementation plan.

                        - **操作**：使用 `read_file` 读取实施计划的内容。

                    2. Identify any high-level strategic decisions, architectural changes, or overall outcomes described in the plan.

                    2. 识别计划中描述的任何高级战略决策、架构变更或整体结果。

                    3. Cross-reference the tasks listed within the plan against the verification status determined in step 1e. Update the Implementation Plan to accurately reflect the true completion status of its child tasks.

                    3. 根据步骤 1e 中确定的验证状态，交叉参考计划中列出的任务。更新实施计划以准确反映其子任务的真实完成状态。

                    4. **Extract Consolidatable Information**:
                    4. **提取可整合信息**：

                        - Earmark any significant strategic information not yet captured in higher-level HDTA documents (like `system_manifest.md` or `*_module.md` files).

                        - 标记尚未在更高级别 HDTA 文档（如 `system_manifest.md` 或 `*_module.md` 文件）中捕获的任何重要战略信息。

                        - **Action**: Record this information in `consolidation_notes.md` in `cline_docs/`, appending each piece with a reference to the source file and batch number (e.g., "Batch 2, implementation_plan_feature_y.md: Decision to use microservices for scalability").

                        - **操作**：将此信息记录在 `cline_docs/` 中的 `consolidation_notes.md` 中，为每条信息附加源文件和批次的引用（例如，"批次 2，implementation_plan_feature_y.md：决定使用微服务以提高可扩展性"）。

                - **Action**: After fully processing all files in the current batch (i.e., all files have been read, updated, and their consolidatable information recorded in `consolidation_notes.md`), document the completion of the batch in `activeContext.md` (e.g., "Completed verification and extraction for batch Y containing implementation plans [plan1, plan2, ...]. Information recorded in `consolidation_notes.md`."). Only then proceed to the next batch.

                - **操作**：在完全处理当前批次中的所有文件后（即所有文件都已读取、更新，并且其可整合信息已记录在 `consolidation_notes.md` 中），在 `activeContext.md` 中记录批次的完成情况（例如，"完成了包含实施计划 [plan1、plan2、...] 的批次 Y 的验证和提取。信息已记录在 `consolidation_notes.md` 中。"）。只有这样才继续下一批次。

                - **Purpose**: Processing each batch as a standalone task ensures manageable processing of Implementation Plans, maintaining alignment with verified task statuses.

                - **目的**：将每个批次作为独立任务处理，确保实施计划的可管理处理，保持与已验证任务状态的一致性。

    *   **g. Review Other Strategic Tracking Documents (Roadmaps, Checklists, etc.) in Batches (CRITICAL)**:
        *   **Purpose**: To ensure all high-level tracking documents are up-to-date, and that incomplete items from older versions are not lost. This review covers all files identified in step 1a (excluding HDTA templates), processed in batches to prevent context overload.

    *   **g. 批量审查其他战略跟踪文档（路线图、检查清单等）（关键）**：
        *   **目的**：确保所有高级跟踪文档都是最新的，并且不会丢失旧版本中的未完成项目。此审查涵盖步骤 1a 中识别的所有文件（不包括 HDTA 模板），分批处理以防止上下文过载。

        *   **Procedure**:
        *   **程序**：

            i. **Batch Creation**:
            i. **批次创建**：

                - **Action**: Divide the comprehensive list of Strategic Tracking documents (from step 1a, e.g., `*roadmap*.md`, `*checklist*.md`, `*review_progress*.md`) into batches, with each batch containing **no more than 10 files**. If the total number of files is not evenly divisible by 10, the final batch may contain fewer than 10 files.

                - **操作**：将战略跟踪文档的全面列表（来自步骤 1a，例如 `*roadmap*.md`、`*checklist*.md`、`*review_progress*.md`）分成批次，每批次包含**不超过 10 个文件**。如果文件总数不能被 10 整除，最后一批可能包含少于 10 个文件。

                - **Action**: Maintain a record of which files have been processed to ensure no files are missed or processed twice.

                - **操作**：维护已处理文件的记录，以确保没有文件被遗漏或重复处理。

            ii. **Process Each Batch (Standalone Processing)**:
            ii. **处理每个批次（独立处理）**：

                - **Action**: For each batch of up to 10 Strategic Tracking documents, **fully process the batch as a standalone task** before proceeding to the next batch. This means completing all reading, consolidation, updating, and extraction actions for all files in the batch with no inter-batch dependencies for these actions.

                - **操作**：对于每批多达 10 个战略跟踪文档，在继续下一批次之前，**将批次完全作为独立任务处理**。这意味着完成批次中所有文件的所有读取、整合、更新和提取操作，这些操作之间没有批次间依赖关系。

                - **Sub-Procedure (for each file in the batch)**:
                - **子程序（对于批次中的每个文件）**：

                    1. If multiple versions of the same conceptual tracker exist (e.g., `project_checklist_v1.md`, `project_checklist_v2.md`):
                    1. 如果同一概念跟踪器存在多个版本（例如，`project_checklist_v1.md`、`project_checklist_v2.md`）：

                        - **Action**: Read all versions within the batch.

                        - **操作**：读取批次中的所有版本。

                        - **Action (CRITICAL)**: Identify the *newest* version. Consolidate all incomplete or pending items from *older* versions into this newest version.

                        - **操作（关键）**：识别*最新*版本。将*较旧*版本中的所有未完成或待处理项目整合到此最新版本中。

                        - **Action (CRITICAL)**: Ensure all significant completed items and learnings noted in older versions are appropriately reflected in persistent project documentation (HDTA, changelog, etc.) or carried over to the newest tracker version if still relevant for context.

                        - **操作（关键）**：确保在旧版本中记录的所有重要完成项目和学习内容都适当地反映在持久化项目文档（HDTA、变更日志等）中，或者如果与上下文仍然相关，则转移到最新跟踪器版本。

                        - Once an older version is fully consolidated (all its unique, still-relevant information is transferred), it can be considered for archival in Section IV. The newest version becomes the active tracker.

                        - 一旦旧版本完全整合（其所有独特的、仍然相关的信息已转移），就可以考虑在第四节中将其归档。最新版本将成为活动跟踪器。

                    2. For the active/newest version of each tracker, review its items against the verified task statuses (from step 1e) and Implementation Plan reviews (step 1f). Update the tracker to accurately reflect project progress.

                    2. 对于每个跟踪器的活动/最新版本，根据已验证的任务状态（来自步骤 1e）和实施计划审查（步骤 1f）审查其项目。更新跟踪器以准确反映项目进度。

                    3. **Extract Consolidatable Information**:
                    3. **提取可整合信息**：

                        - Earmark any strategic insights or status updates for broader consolidation (e.g., into `activeContext.md` or `progress.md`).

                        - 标记用于更广泛整合的战略见解或状态更新（例如，进入 `activeContext.md` 或 `progress.md`）。

                        - **Action**: Record this information in `consolidation_notes.md` in `cline_docs/`, appending each piece with a reference to the source file and batch number (e.g., "Batch 3, roadmap_v3.md: Updated milestone priorities based on task delays").

                        - **操作**：将此信息记录在 `cline_docs/` 中的 `consolidation_notes.md` 中，为每条信息附加源文件和批次的引用（例如，"批次 3，roadmap_v3.md：根据任务延迟更新了里程碑优先级"）。

                - **Action**: After fully processing all files in the current batch (i.e., all files have been read, consolidated, updated, and their consolidatable information recorded in `consolidation_notes.md`), document the completion of the batch in `activeContext.md` (e.g., "Completed verification and extraction for batch Z containing trackers [tracker1, tracker2, ...]. Information recorded in `consolidation_notes.md`."). Only then proceed to the next batch.

                - **操作**：在完全处理当前批次中的所有文件后（即所有文件都已读取、整合、更新，并且其可整合信息已记录在 `consolidation_notes.md` 中），在 `activeContext.md` 中记录批次的完成情况（例如，"完成了包含跟踪器 [tracker1、tracker2、...] 的批次 Z 的验证和提取。信息已记录在 `consolidation_notes.md` 中。"）。只有这样才继续下一批次。

                - **Purpose**: Processing each batch as a standalone task ensures manageable processing of Strategic Trackers, maintaining comprehensive consolidation.

                - **目的**：将每个批次作为独立任务处理，确保战略跟踪器的可管理处理，保持全面整合。

2.  **Identify All Information for Consolidation (CRITICAL)**:
    *   Based on the comprehensive review performed in Step 1 (covering all task instructions, implementation plans, strategic trackers, and core state files), **CRITICALLY** list all specific pieces of information that represent lasting design decisions, architectural changes, significant outcomes, refined requirements, important operational learnings, "gotchas," or any other vital knowledge that **MUST** be integrated into persistent project documentation. This list is not limited to findings from only the most recent operational cycle but encompasses the entire project history as reviewed. (Excluding changelog structural reorganization for this step, which is handled in Step 3b).

2.  **识别所有需要整合的信息（关键）**：
    *   基于在步骤 1 中执行的全面审查（涵盖所有任务指令、实施计划、战略跟踪器和核心状态文件），**关键性地**列出所有代表持久设计决策、架构变更、重要结果、精炼需求、重要运营学习内容、"陷阱"或任何其他关键知识的具体信息，这些信息**必须**整合到持久化项目文档中。此列表不仅限于最近操作周期的发现，还包括整个项目历史的审查内容。（不包括此步骤的变更日志结构重组，该重组在步骤 3b 中处理）。

3.  **Update Persistent Documentation & Reorganize Changelog**:

3.  **更新持久化文档并重新组织变更日志**：

    *   **a. Update Standard Documentation (HDTA, Core Files) (CRITICAL)**:
        *   **Purpose**: To ensure all persistent project documentation accurately reflects the consolidated knowledge gathered from `consolidation_notes.md` in Step 2. This is a **CRITICAL** step for maintaining an up-to-date and reliable knowledge base for the project.

    *   **a. 更新标准文档（HDTA、核心文件）（关键）**：
        *   **目的**：确保所有持久化项目文档准确反映在步骤 2 中从 `consolidation_notes.md` 收集的整合知识。这是维护项目最新和可靠知识库的**关键**步骤。

        *   **HDTA Documents**:
        *   **HDTA 文档**：

            *   **Action (CRITICAL)**: Update `system_manifest.md` if the overall architecture, core components, or project goals have evolved or been clarified at any point.

            *   **操作（关键）**：如果整体架构、核心组件或项目目标在任何时候发展或澄清，请更新 `system_manifest.md`。

            *   **Action (CRITICAL)**: Update relevant Domain Modules (`*_module.md`) to incorporate refined descriptions, interface changes, key implementation notes, or any other significant learnings discovered.

            *   **操作（关键）**：更新相关领域模块（`*_module.md`），以整合精炼的描述、接口变更、关键实施注释或发现的任何其他重要学习内容。

            *   **Action (CRITICAL)**: Update relevant Implementation Plans (`implementation_plan_*.md`) with notes on final outcomes, deviations from original plans, or significant decisions made during any implementation effort. Ensure they accurately reflect the verified completion status of their child tasks.

            *   **操作（关键）**：使用最终结果注释、与原始计划的偏差或任何实施过程中做出的重大决策来更新相关实施计划（`implementation_plan_*.md`）。确保它们准确反映其子任务的验证完成状态。

            *   **Procedure**: For each HDTA document requiring updates: Use `read_file` to load the target document, integrate the consolidated information logically and clearly, and use `write_to_file` to save changes. **State reasoning for each update, referencing the source of the consolidated information (e.g., specific task file, `activeContext.md` insight).** Example: "Consolidating final algorithm choice for module Y (from archived task `cline_docs/archive/tasks/task_abc.md`) into `src/module_y/module_y_module.md`."

            *   **程序**：对于每个需要更新的 HDTA 文档：使用 `read_file` 加载目标文档，逻辑清晰地整合整合信息，并使用 `write_to_file` 保存更改。**说明每次更新的理由，引用整合信息的来源（例如，特定任务文件、`activeContext.md` 见解）。** 例如："将模块 Y 的最终算法选择（来自已归档任务 `cline_docs/archive/tasks/task_abc.md`）整合到 `src/module_y/module_y_module.md` 中。"

        *   **Core Files**:
        *   **核心文件**：

            *   **Action (CRITICAL)**: Update `progress.md` to accurately mark all completed high-level checklist items based on verified outcomes.

            *   **操作（关键）**：根据验证结果准确更新 `progress.md`，标记所有已完成的高级检查清单项目。

            *   **Action (CRITICAL)**: Update `userProfile.md` with any newly observed or reinforced user preferences or interaction patterns.

            *   **操作（关键）**：使用任何新观察到的或强化的用户偏好或交互模式更新 `userProfile.md`。

            *   **Action (CRITICAL)**: Review and Consolidate `.clinerules` `[LEARNING_JOURNAL]`:
            *   **操作（关键）**：审查和整合 `.clinerules` `[LEARNING_JOURNAL]`：

                i.  **Action**: Read the current `[LEARNING_JOURNAL]` section from `.clinerules`.

                i.  **操作**：读取 `.clinerules` 中的当前 `[LEARNING_JOURNAL]` 部分。

                ii. **Purpose**: To refine the journal by grouping similar learnings, combining related entries for conciseness, removing entries that are not strategic or system-level learnings (e.g., very minor tactical notes better suited for `activeContext.md` during a specific task, or temporary observations that are no longer relevant), and ensuring entries are clearly articulated.

                ii. **目的**：通过分组类似的学习内容、合并相关条目以简化、删除不是战略或系统级别学习的条目（例如，更适合在特定任务期间的 `activeContext.md` 中的非常小的战术注释，或不再相关的临时观察），并确保条目清晰表达，来完善日志。

                iii. **Procedure**:
                iii. **程序**：

                    - Identify entries that are redundant or cover very similar points. Combine them into a single, more comprehensive entry.

                    - 识别冗余或覆盖非常相似点的条目。将它们合并为一个更全面的条目。

                    - Identify entries that are too granular or represent temporary states rather than lasting learnings. Consider removing these if their value is not persistent.

                    - 识别过于细化或代表临时状态而不是持久学习内容的条目。如果其价值不是持久的，请考虑删除它们。

                    - Identify entries that are not appropriate for the Learning Journal's purpose (e.g., simple reminders, task-specific notes that don't represent broader learning). Remove these.

                    - 识别不适合学习日志目的的条目（例如，简单提醒、不代表更广泛学习的任务特定注释）。删除这些条目。

                    - Ensure remaining entries are clear, concise, and genuinely reflect significant learnings about the CRCT process, project management, technical approaches, or user interactions.

                    - 确保剩余条目清晰、简洁，并真正反映关于 CRCT 过程、项目管理、技术方法或用户交互的重要学习内容。

                iv. **Action**: Add any *new* significant system-level learnings identified during the comprehensive review (from Step 1e, 1f, 1g) to the refined journal. Example: "Adding to Learning Journal: Comprehensive review during Cleanup/Consolidation revealed a recurring pattern of task underestimation when initial data definitions are incomplete, highlighting the need for more rigorous data strategy upfront."

                iv. **操作**：将在全面审查（来自步骤 1e、1f、1g）期间识别的任何*新的*重要系统级别学习内容添加到精炼的日志中。例如："添加到学习日志：清理/整合期间的全面审查显示，当初始数据定义不完整时，任务低估经常出现，突出了前期需要更严格的数据策略。"

                v.  **Action**: Use `write_to_file` (or `apply_diff` if more appropriate for `.clinerules` format) to update the `[LEARNING_JOURNAL]` section in `.clinerules` with the consolidated and newly added entries.

                v.  **操作**：使用 `write_to_file`（或 `apply_diff`，如果更适合 `.clinerules` 格式）用整合和新添加的条目更新 `.clinerules` 中的 `[LEARNING_JOURNAL]` 部分。

    *   **b. Consolidate and Reorganize Changelog (CRITICAL)**:
        *   **Purpose**: To transform the `changelog.md` into a more readable and maintainable format by structuring all historical entries by their primary component/module and then chronologically within each component. This provides a clear, organized history of changes for the entire project lifecycle. This is a **CRITICAL** step for long-term project understanding and maintainability.

    *   **b. 整合和重新组织变更日志（关键）**：
        *   **目的**：通过将所有历史条目按其主要组件/模块组织，然后在每个组件内按时间顺序组织，将 `changelog.md` 转换为更具可读性和可维护性的格式。这为整个项目生命周期提供了清晰、有组织的变更历史。这是长期项目理解和可维护性的**关键**步骤。

        *   **Goal**: Reformat `changelog.md` by grouping entries under component/module headings, sorted chronologically (newest first) within each group.

        *   **目标**：通过在组件/模块标题下对条目进行分组，并在每个组内按时间顺序（最新的在前）排序，重新格式化 `changelog.md`。

        *   **Action: Read**: Use `read_file` to load the current content of `changelog.md`.

        *   **操作：读取**：使用 `read_file` 加载 `changelog.md` 的当前内容。

        *   **Action: Process Internally**:
        *   **操作：内部处理**：

            1.  **Parse Entries**: Mentally (or by outlining the steps) parse the loaded text into individual changelog entries (likely delimited by `---` or `### Heading - Date`). Extract the Date, Summary, Files Modified list, and the full text block for each entry.

            1.  **解析条目**：在心理上（或通过概述步骤）将加载的文本解析为单独的变更日志条目（可能由 `---` 或 `### 标题 - 日期` 分隔）。提取每个条目的日期、摘要、修改文件列表和完整文本块。

            2.  **Determine Component**: For each entry, determine its primary component/module based on the `Files Modified` paths. Use heuristics:

            2.  **确定组件**：对于每个条目，根据 `修改的文件` 路径确定其主要组件/模块。使用启发式方法：

                *   If most/all files are in `src/module_name/`, component is `Module: module_name`.

                *   如果大多数/所有文件都在 `src/module_name/` 中，组件为 `Module: module_name`（模块：module_name）。

                *   If most/all files are in `docs/category/`, component is `Documentation: category`.

                *   如果大多数/所有文件都在 `docs/category/` 中，组件为 `Documentation: category`（文档：category）。

                *   If files are in `cline_utils/` or `cline_docs/`, component is `CRCT System`.

                *   如果文件在 `cline_utils/` 或 `cline_docs/` 中，组件为 `CRCT System`（CRCT 系统）。

                *   If files span multiple major areas, choose the most representative one or create a `Cross-Cutting` category.

                *   如果文件跨越多个主要区域，请选择最具代表性的一个或创建 `Cross-Cutting`（跨领域）类别。

                *   Use a default `General` category if no clear component is identifiable.

                *   如果无法识别清晰的组件，请使用默认的 `General`（常规）类别。

            3.  **Group Entries**: Create internal lists, grouping the parsed entries by their determined component.

            3.  **对条目进行分组**：创建内部列表，根据确定的组件对解析的条目进行分组。

            4.  **Sort Groups**: Within each component group, sort the entries strictly by Date (most recent date first).

            4.  **对组进行排序**：在每个组件组内，严格按日期对条目进行排序（最近的日期在前）。

            5.  **Format Output**: Construct the *entire new text content* for `changelog.md`.

            5.  **格式化输出**：为 `changelog.md` 构建*整个新文本内容*。

                *   Start with the main `# Changelog` heading.

                *   从主 `# Changelog`（变更日志）标题开始。

                *   For each component group:

                *   对于每个组件组：

                    *   Add a component heading (e.g., `## Component: Game Loop` or `## Documentation: Worldbuilding`).

                    *   添加组件标题（例如，`## Component: Game Loop` 或 `## Documentation: Worldbuilding`）。

                    *   List the sorted entries for that component, preserving their original `### Summary - Date`, `Description`, `Impact`, `Files Modified` structure.

                    *   列出该组件的排序条目，保留其原始的 `### 摘要 - 日期`、`描述`、`影响`、`修改的文件` 结构。

                    *   Use `---` between individual entries within the component group.

                    *   在组件组内的单个条目之间使用 `---`。

                *   *(Optional: Add a more distinct separator like `***` between different component groups if helpful for readability)*.

                *   *（可选：如果有助于可读性，在不同组件组之间添加更明显的分隔符，如 `***`）*。

        *   **Action: Write**: Use `write_to_file` to overwrite `changelog.md` with the *complete, reformatted content* generated in the previous step.

        *   **操作：写入**：使用 `write_to_file` 用上一步中生成的*完整的、重新格式化的内容*覆盖 `changelog.md`。

        *   **State**: "Reorganized `changelog.md`. Read existing content, parsed entries, grouped by component (e.g., Game Loop, Documentation, CRCT System), sorted entries by date within each group, and overwrote the file with the new structure."

        *   **状态**："重新组织了 `changelog.md`。读取现有内容，解析条目，按组件（例如，游戏循环、文档、CRCT 系统）分组，在每个组内按日期对条目进行排序，并用新结构覆盖文件。"

    *   **c. `activeContext.md` (Final Pass & CRITICAL Update)**:
        *   **Action (CRITICAL)**: After all other information has been consolidated into persistent documents (HDTA, core files) and the changelog has been reorganized, update `activeContext.md` one last time.

    *   **c. `activeContext.md`（最后通过和关键更新）**：
        *   **操作（关键）**：在所有其他信息已整合到持久化文档（HDTA、核心文件）中并且变更日志已重新组织之后，最后更新一次 `activeContext.md`。

        *   **Goal**: To ensure `activeContext.md` accurately reflects the *current, fully consolidated baseline state of the entire project*. This involves removing any transient details specific to *any previously completed work cycles or outdated project states* (e.g., step-by-step execution logs from past tasks, outdated considerations, resolved issues that are now documented elsewhere). The file should retain only the current high-level project status, truly outstanding issues that require immediate or near-term attention, and clear pointers to where detailed, persistent information now resides (e.g., "Final design details for feature Y documented in `implementation_plan_feature_y.md`. Changelog comprehensively reorganized. Next focus: Phase X based on `roadmap_v3.md`.").

        *   **目标**：确保 `activeContext.md` 准确反映*整个项目的当前、完全整合的基线状态*。这涉及删除特定于*任何先前完成的工作周期或过时项目状态*的任何临时细节（例如，过去任务的逐步执行日志、过时的考虑、现在已在其他地方记录的已解决问题）。该文件应仅保留当前的高级项目状态、真正需要立即或近期关注的未解决问题，以及指向详细、持久信息所在之处的清晰指针（例如，"功能 Y 的最终设计细节记录在 `implementation_plan_feature_y.md` 中。变更日志已全面重新组织。下一个重点：基于 `roadmap_v3.md` 的阶段 X。"）。

4.  **MUP**: Perform Core MUP and Section V additions after completing the consolidation steps (including changelog). Update `last_action` in `.clinerules` to indicate consolidation is finished and cleanup is next.

4.  **MUP**：在完成整合步骤（包括变更日志）后执行核心 MUP 和第五节添加。更新 `.clinerules` 中的 `last_action` 以指示整合已完成，下一步是清理。

---

## IV. Cleanup Workflow

## IV. 清理工作流

**Goal**: Remove or archive obsolete files and data to reduce clutter and keep the project context focused on active work. **Proceed only after Consolidation (Section III) is complete.**

**目标**：删除或归档过时文件和数据以减少混乱，并使项目上下文专注于活动工作。**仅在整合（第三节）完成后继续。**

**Procedure:**
**程序：**

1.  **Identify Cleanup Targets (CRITICAL)**:
    *   **CRITICAL Pre-condition**: This step relies entirely on the comprehensive review and verification performed in Section III. Only files confirmed as fully completed, verified, and whose essential information has been consolidated into persistent documentation are eligible for cleanup.

1.  **识别清理目标（关键）**：
    *   **关键前提条件**：此步骤完全依赖于第三节中执行的全面审查和验证。只有被确认为完全完成、已验证且其重要信息已整合到持久化文档中的文件才有资格进行清理。

    *   **a. Identify Completed and Consolidated Task Instruction Files**:
        *   Refer to the outcomes of Section III, Step 1e. Task Instruction files that were:

    *   **a. 识别已完成和整合的任务指令文件**：
        *   参考第三节步骤 1e 的结果。任务指令文件符合以下条件：

            i.  Verified as genuinely completed.

            i.  已验证为真正完成。

            ii. Had all their critical information (learnings, design choices, "gotchas") successfully consolidated into persistent HDTA documents or the Learning Journal.

            ii. 其所有关键信息（学习内容、设计选择、"陷阱"）已成功整合到持久化 HDTA 文档或学习日志中。

        *   These files are primary candidates for archival. **Task files that were found to be unverified or incomplete in Section III, Step 1e, MUST NOT be targeted for cleanup as "complete" items.**

        *   这些文件是归档的主要候选者。**在第三节步骤 1e 中被发现为未验证或未完成的任务文件不得作为"完整"项目成为清理目标。**

    *   **b. Identify Fulfilled Strategy Task Files**:
        *   Refer to the outcomes of Section III, Step 1f and 1g. Strategy task files whose objectives have been fully met by downstream Execution tasks (which themselves are verified complete and consolidated) and whose own content has been fully consolidated are candidates for archival.

    *   **b. 识别已履行的策略任务文件**：
        *   参考第三节步骤 1f 和 1g 的结果。策略任务文件，其目标已由下游执行任务完全满足（其本身已验证完成和整合），且其自己的内容已完全整合，是归档的候选者。

    *   **c. Identify Obsolete Temporary Session Files and Trackers**:
        *   Refer to the outcomes of Section III, Step 1g. Older versions of strategic tracking documents (roadmaps, checklists, review progress files) that have had all their pending items and unique valuable information consolidated into a newer active version (or into persistent HDTA documents) are candidates for archival.

    *   **c. 识别过时的临时会话文件和跟踪器**：
        *   参考第三节步骤 1g 的结果。旧版本的战略跟踪文档（路线图、检查清单、审查进度文件），其所有待处理项目和独特有价值的信息已整合到更新的活动版本（或持久化 HDTA 文档）中，是归档的候选者。

        *   Identify any other temporary session-specific files (e.g., ad-hoc notes from a past phase that are now fully processed and consolidated) that are no longer relevant to the current project state.

        *   识别任何其他临时会话特定文件（例如，过去阶段的临时笔记，现已完全处理和整合），这些文件与当前项目状态不再相关。

    *   **d. Identify Temporary Consolidation Notes File**:
        *   **Action**: Identify `consolidation_notes.md` in `cline_docs/` as a temporary file created during the Consolidation Workflow (Section III). Since its contents have been fully processed and integrated into persistent documentation in Section III, Step 3, it is now obsolete and a candidate for archival.

    *   **d. 识别临时整合笔记文件**：
        *   **操作**：将 `cline_docs/` 中的 `consolidation_notes.md` 识别为在整合工作流（第三节）期间创建的临时文件。由于其内容已在第三节步骤 3 中完全处理并整合到持久化文档中，现在它已过时，是归档的候选者。

    *   **e. Identify Other Obsolete Files**:
        *   Consider other temporary files or logs if any were created during any project phase and are confirmed to be no longer relevant and their information (if any) has been consolidated.

    *   **e. 识别其他过时文件**：
        *   考虑其他临时文件或日志（如果任何项目阶段创建的这些文件），并确认它们不再相关且其信息（如果有）已整合。

2.  **Determine Cleanup Strategy (Archive vs. Delete)**:
    *   **Recommendation**: Archiving is generally safer than permanent deletion.

2.  **确定清理策略（归档与删除）**：
    *   **建议**：归档通常比永久删除更安全。

    *   **Determine Project Root**: Identify the absolute path to the project's root workspace directory from your current environment context. Let's refer to this as `{WORKSPACE_ROOT}`. **Do not hardcode paths.**

    *   **确定项目根目录**：从当前环境上下文中识别项目根工作区目录的绝对路径。让我们将其称为 `{WORKSPACE_ROOT}`。**不要硬编码路径。**

    *   **Proposal**: Propose creating an archive structure if it doesn't exist, using **absolute paths**.

    *   **建议**：建议创建归档结构（如果不存在），使用**绝对路径**。

        *   Example absolute paths for archive dirs: `{WORKSPACE_ROOT}/cline_docs/archive/tasks/`, `{WORKSPACE_ROOT}/cline_docs/archive/session_trackers/`.

        *   归档目录的示例绝对路径：`{WORKSPACE_ROOT}/cline_docs/archive/tasks/`、`{WORKSPACE_ROOT}/cline_docs/archive/session_trackers/`。

    *   **Action**: First, use `list_files` to check if the proposed archive directories (e.g., `{WORKSPACE_ROOT}/cline_docs/archive/tasks/`, `{WORKSPACE_ROOT}/cline_docs/archive/session_trackers/`) already exist if you have not already done so in a previous step. If they do not, then propose creating them using `execute_command`. Propose the appropriate OS-specific command (e.g., `mkdir -p` for Unix-like, `New-Item -ItemType Directory -Force` for PowerShell, `mkdir` for CMD which might require checking for existence first or handling an error if it already exists) using the absolute path. **Use `ask_followup_question` to confirm this specific command** or allow the user to provide an alternative. Prioritize using the environment details to determine the user's shell for more accurate initial suggestions. If the directories already exist, this creation step can be skipped.

    *   **操作**：首先，使用 `list_files` 检查提议的归档目录（例如，`{WORKSPACE_ROOT}/cline_docs/archive/tasks/`、`{WORKSPACE_ROOT}/cline_docs/archive/session_trackers/`）是否已存在（如果您在上一步中尚未这样做）。如果它们不存在，则建议使用 `execute_command` 创建它们。建议使用操作系统特定的适当命令（例如，Unix-like 系统使用 `mkdir -p`，PowerShell 使用 `New-Item -ItemType Directory -Force`，CMD 使用 `mkdir`，这可能需要首先检查存在性或如果已存在则处理错误）使用绝对路径。**使用 `ask_followup_question` 确认此特定命令**或允许用户提供替代方案。优先使用环境详细信息来确定用户的 shell，以提供更准确的初始建议。如果目录已存在，则可以跳过此创建步骤。

        ```xml
        <!-- Determine Workspace Root as {WORKSPACE_ROOT} -->
        <!-- Proposing command to create archive directories. -->
        <ask_followup_question>
          <question>Create archive directories? Proposed command (uses absolute paths, tailored to detected OS/shell):
          `[Proposed Command Here]`
          Is this command correct for your OS/shell?</question>
          <follow_up>
            <suggest>Yes, execute this command</suggest>
            <suggest>No, I will provide the correct command</suggest>
          </follow_up>
        </ask_followup_question>
        ```

        ```xml
        <!-- 将工作区根目录确定为 {WORKSPACE_ROOT} -->
        <!-- 建议创建归档目录的命令。 -->
        <ask_followup_question>
          <question>创建归档目录？建议的命令（使用绝对路径，根据检测到的操作系统/shell 定制）：
          `[此处为建议的命令]`
          此命令对您的操作系统/shell 是否正确？</question>
          <follow_up>
            <suggest>是，执行此命令</suggest>
            <suggest>否，我将提供正确的命令</suggest>
          </follow_up>
        </ask_followup_question>
        ```

        *   If user selects "Yes", proceed with `execute_command` using the proposed command.

        *   如果用户选择"是"，则使用建议的命令继续执行 `execute_command`。

        *   If user selects "No", wait for their input and use that in `execute_command`.

        *   如果用户选择"否"，等待其输入并在 `execute_command` 中使用该输入。

        *(Note: Quoting paths is good practice, especially if the root path might contain spaces. Be mindful of shell-specific syntax for multiple directories or force options.)*

        *（注：引用路径是一种良好的做法，特别是如果根路径可能包含空格。请注意多个目录或强制选项的特定 shell 语法。）*

3.  **Execute Cleanup (Using `execute_command` with User Confirmation via `ask_followup_question`) (CRITICAL)**:
    *   **Input**: This step processes the list of files deemed eligible for cleanup (archival or deletion) as determined by the rigorous verification and consolidation checks in Section IV, Step 1, including `consolidation_notes.md`.

3.  **执行清理（使用 `execute_command` 并通过 `ask_followup_question` 进行用户确认）（关键）**：
    *   **输入**：此步骤处理根据第四节步骤 1 中的严格验证和整合检查确定有资格进行清理（归档或删除）的文件列表，包括 `consolidation_notes.md`。

    *   **List Files**: Use `list_files` (which uses relative paths based on workspace) to confirm the current existence and *relative paths* of files targeted for cleanup *from the eligible list*.

    *   **列出文件**：使用 `list_files`（使用基于工作区的相对路径）确认有资格列表中被定为清理目标的文件的当前存在和*相对路径*。

    *   **Construct Absolute Paths**: For each relative path identified for cleanup (e.g., `tasks/some_task.md`), construct its corresponding **absolute path** by prepending the determined `{WORKSPACE_ROOT}` (e.g., `{WORKSPACE_ROOT}/tasks/some_task.md`). Do the same for target archive locations.

    *   **构建绝对路径**：对于为清理识别的每个相对路径（例如，`tasks/some_task.md`），通过在前面添加确定的 `{WORKSPACE_ROOT}` 来构建其对应的**绝对路径**（例如，`{WORKSPACE_ROOT}/tasks/some_task.md`）。对目标归档位置执行相同操作。

    *   **Propose Actions and Get Command Confirmation (MANDATORY `ask_followup_question` Step)**:
    *   **建议操作并获得命令确认（强制性 `ask_followup_question` 步骤）**：

        *   For each file or group of files to be cleaned up:
        *   对于要清理的每个文件或文件组：

            1.  Clearly formulate the **question** stating the intended action (archive/delete) and the full absolute path(s) involved.

            1.  清楚地表述**问题**，说明预期操作（归档/删除）和涉及的完整绝对路径。

            2.  Generate **suggested commands** (as `<suggest>` options) for common OS/shell combinations (Linux/macOS/Git Bash, Windows CMD, Windows PowerShell), using the determined `{WORKSPACE_ROOT}` and appropriate path separators (`/` or `\`) for each suggestion. **Prioritize the suggestion matching the detected shell.**

            2.  为常见操作系统/shell 组合（Linux/macOS/Git Bash、Windows CMD、Windows PowerShell）生成**建议的命令**（作为 `<suggest>` 选项），使用确定的 `{WORKSPACE_ROOT}` 和每个建议的适当路径分隔符（`/` 或 `\`）。**优先选择与检测到的 shell 匹配的建议。**

            3.  Include a final `<suggest>` option like: `Provide alternative command`.

            3.  包括最后一个 `<suggest>` 选项，如：`提供替代命令`。

            4.  Use the `ask_followup_question` tool with the question and these suggestions.

            4.  使用 `ask_followup_question` 工具以及问题和建议。

    *   **Note on Shell Accuracy**: Be aware that the detected shell might not always be the active one. If command execution fails, re-verify the user's active shell or ask for explicit confirmation.

    *   **关于 Shell 准确性的说明**：请注意，检测到的 shell 可能并不总是活动的 shell。如果命令执行失败，请重新验证用户的活动 shell 或请求明确确认。

    *   **Example Interaction Flow**: (Examples remain relevant, but suggestions should be tailored and prioritize detected shell)
    *   **示例交互流程**：（示例仍然相关，但建议应根据检测到的 shell 定制并优先考虑）

        *   **LLM**: *(Constructs absolute paths internally based on `{WORKSPACE_ROOT}`)*
        *   **LLM**：*（根据 `{WORKSPACE_ROOT}` 在内部构建绝对路径）*

          ```xml
          <ask_followup_question>
            <question>Archive completed task file "{WORKSPACE_ROOT}/tasks/Execution_integrate_input_handler_game_loop_task.md" to "{WORKSPACE_ROOT}/cline_docs/archive/tasks/"? Select the correct command for your system:</question>
            <follow_up>
              <suggest>mv "{WORKSPACE_ROOT}/tasks/Execution_integrate_input_handler_game_loop_task.md" "{WORKSPACE_ROOT}/cline_docs/archive/tasks/"</suggest> <!-- Prioritize if Linux/macOS detected -->
              <suggest>move "{WORKSPACE_ROOT}\tasks\Execution_integrate_input_handler_game_loop_task.md" "{WORKSPACE_ROOT}\cline_docs\archive\tasks\"</suggest> <!-- Prioritize if Windows detected -->
              <suggest>Provide alternative command</suggest>
            </follow_up>
          </ask_followup_question>
          ```

          ```xml
          <ask_followup_question>
            <question>将已完成任务文件 "{WORKSPACE_ROOT}/tasks/Execution_integrate_input_handler_game_loop_task.md" 归档到 "{WORKSPACE_ROOT}/cline_docs/archive/tasks/"？为您的系统选择正确的命令：</question>
            <follow_up>
              <suggest>mv "{WORKSPACE_ROOT}/tasks/Execution_integrate_input_handler_game_loop_task.md" "{WORKSPACE_ROOT}/cline_docs/archive/tasks/"</suggest> <!-- 如果检测到 Linux/macOS 则优先 -->
              <suggest>move "{WORKSPACE_ROOT}\tasks\Execution_integrate_input_handler_game_loop_task.md" "{WORKSPACE_ROOT}\cline_docs\archive\tasks\"</suggest> <!-- 如果检测到 Windows 则优先 -->
              <suggest>提供替代命令</suggest>
            </follow_up>
          </ask_followup_question>
          ```

        *   **User**: *(Selects a command or provides alternative)*
        *   **用户**：*（选择命令或提供替代方案）*

        *   **LLM**: "Okay, executing the selected command:"
        *   **LLM**："好的，执行选定的命令："

          ```xml
          <execute_command>
          <command>[User Confirmed or Provided Command]</command>
          </execute_command>
          ```
          ```xml
          <execute_command>
          <command>[用户确认或提供的命令]</command>
          </execute_command>
          ```

        *   *(Wait for tool result, document action, then proceed to next file)*
        *   *（等待工具结果，记录操作，然后继续下一个文件）*

    *   **Document Actions**: After successful execution (based on tool output), clearly log which files were archived or deleted using the confirmed commands and absolute paths.

    *   **记录操作**：成功执行后（基于工具输出），清楚地记录使用确认的命令和绝对路径归档或删除了哪些文件。

4.  **Final Verification (CRITICAL)**:
    *   **Action (CRITICAL)**: If any archive or delete operations were performed in Step 3, use `list_files` again with the original *relative* locations of the processed files to verify they are no longer present in those locations.

4.  **最终验证（关键）**：
    *   **操作（关键）**：如果在步骤 3 中执行了任何归档或删除操作，请再次使用 `list_files` 和已处理文件的原始*相对*位置，以验证它们不再存在于这些位置。

    *   **Action (CRITICAL)**: Ensure `activeContext.md` is clean and does not reference the removed/archived files unless it is explicitly pointing to their new archive location for historical reference. All other pointers should be to active, persistent documentation.

    *   **操作（关键）**：确保 `activeContext.md` 是干净的，并且不引用已删除/归档的文件，除非它明确指向它们的新归档位置以供历史参考。所有其他指针应指向活动、持久化的文档。

5.  **MUP**: Perform Core MUP and Section V additions after completing cleanup. Update `last_action` and `next_phase` in `.clinerules` to signify the end of this phase.

5.  **MUP**：在完成清理后执行核心 MUP 和第五节添加。更新 `.clinerules` 中的 `last_action` 和 `next_phase` 以表示此阶段的结束。

**Cleanup Flowchart**
**清理流程图**
```mermaid
flowchart TD
    A[Start Cleanup (Post-Consolidation)] --> B[Identify Cleanup Targets]
    B --> B1[Determine Absolute Workspace Root `{WORKSPACE_ROOT}`]
    B1 --> C{Archive Structure Exists?}
    C -- No --> D[Use `ask_followup_question` to Confirm `mkdir` command w/ Absolute Paths]
    D -- Confirmed --> D1[Execute Confirmed `mkdir` command]
    C -- Yes --> E
    D1 --> E
    E --> F[List Target Files]
    F --> G[For each file/group:]
    G --> G1[Construct Absolute Paths for Source & Target]
    G1 --> H[1. State Intent<br>Archive/Delete]
    H --> I[2. Generate OS-specific command suggestions w/ Absolute Paths]
    I --> J[3. Use `ask_followup_question` w/ suggestions + "Provide Alternative"]
    J -- User Selects Suggested Command --> K[Execute Selected Command via `execute_command`]
    J -- User Selects "Provide Alternative" --> J1[Wait for User Command Input]
    J1 --> K2[Execute User-Provided Command via `execute_command`]
    K --> L[Document Action]
    K2 --> L
    L --> M{More files?}
    M -- Yes --> G
    M -- No --> N[Verify Files Moved/Removed]
    N --> O[MUP & Update .clinerules to Exit Phase]
    O --> P[End Cleanup]

    style J fill:#f9f,stroke:#f6f,stroke-width:2px,color:#000
    style B1 fill:#e6f7ff,stroke:#91d5ff
    style G1 fill:#fffbe6,stroke:#ffe58f
```
```mermaid
flowchart TD
    A[开始清理（整合后）] --> B[识别清理目标]
    B --> B1[确定绝对工作区根目录 `{WORKSPACE_ROOT}`]
    B1 --> C{归档结构是否存在？}
    C -- 否 --> D[使用 `ask_followup_question` 确认 `mkdir` 命令 w/ 绝对路径]
    D -- 已确认 --> D1[执行确认的 `mkdir` 命令]
    C -- 是 --> E
    D1 --> E
    E --> F[列出目标文件]
    F --> G[对于每个文件/组：]
    G --> G1[为源和目标构建绝对路径]
    G1 --> H[1. 说明意图<br>归档/删除]
    H --> I[2. 生成特定于操作系统的命令建议 w/ 绝对路径]
    I --> J[3. 使用 `ask_followup_question` w/ 建议 + "提供替代方案"]
    J -- 用户选择建议的命令 --> K[通过 `execute_command` 执行选定的命令]
    J -- 用户选择"提供替代方案" --> J1[等待用户命令输入]
    J1 --> K2[通过 `execute_command` 执行用户提供的命令]
    K --> L[记录操作]
    K2 --> L
    L --> M{更多文件？}
    M -- 是 --> G
    M -- 否 --> N[验证文件已移动/删除]
    N --> O[MUP 和更新 .clinerules 以退出阶段]
    O --> P[结束清理]

    style J fill:#f9f,stroke:#f6f,stroke-width:2px,color:#000
    style B1 fill:#e6f7ff,stroke:#91d5ff
    style G1 fill:#fffbe6,stroke:#ffe58f
```

---

## V. Cleanup/Consolidation Plugin - MUP Additions (CRITICAL)

## V. 清理/整合插件 - MUP 添加（关键）

**CRITICAL**: These steps **MUST** be performed in addition to Core MUP steps at the appropriate junctures.

**关键**：这些步骤**必须**在适当的时机在核心 MUP 步骤之外执行。

1.  **Verify `activeContext.md` State (CRITICAL)**: After any significant consolidation or cleanup action, and especially at the MUP points defined in Section III.4 and IV.5, **CRITICALLY** verify that `activeContext.md` accurately reflects the current, clean, and consolidated state. Ensure it points to persistent documents for details and that all transient information from now-completed cycles or outdated states has been removed.

1.  **验证 `activeContext.md` 状态（关键）**：在任何重要的整合或清理操作之后，特别是在第三节第 4 步和第四节第 5 步中定义的 MUP 点，**关键性地**验证 `activeContext.md` 是否准确反映当前、干净和整合的状态。确保它指向持久化文档以获取详细信息，并且已删除来自现已完成周期或过时状态的所有临时信息。

2.  **Verify `changelog.md` Structure (CRITICAL)**: After the changelog reorganization (Section III.3b), and at the MUP point in Section III.4, **CRITICALLY** verify that the `changelog.md` structure correctly reflects the component grouping and chronological sorting as intended.

2.  **验证 `changelog.md` 结构（关键）**：在变更日志重组（第三节第 3b 步）之后，以及在第三节第 4 步的 MUP 点，**关键性地**验证 `changelog.md` 结构是否正确反映了预期的组件分组和时间顺序排序。

3.  **Update `.clinerules` [LAST_ACTION_STATE] (CRITICAL)**:
    *   **After Consolidation step is fully completed (including changelog reorganization - as per Section III.4)**:

3.  **更新 `.clinerules` [LAST_ACTION_STATE]（关键）**：
    *   **整合步骤完全完成后（包括变更日志重组 - 根据第三节第 4 步）**：

      ```
      [LAST_ACTION_STATE]
      last_action: "Completed ALL Consolidation Steps (incl. Changelog Reorg)"
      current_phase: "Cleanup/Consolidation"
      next_action: "Begin Cleanup Workflow"
      next_phase: "Cleanup/Consolidation"
      ```

      ```
      [LAST_ACTION_STATE]
      last_action: "Completed ALL Consolidation Steps (incl. Changelog Reorg)"
      current_phase: "Cleanup/Consolidation"
      next_action: "Begin Cleanup Workflow"
      next_phase: "Cleanup/Consolidation"
      ```

    *   **After Cleanup step is fully completed (exiting phase - as per Section IV.5)**:
    *   **清理步骤完全完成后（退出阶段 - 根据第四节第 5 步）**：

      ```
      [LAST_ACTION_STATE]
      last_action: "Completed Cleanup/Consolidation Phase (All Steps)"
      current_phase: "Cleanup/Consolidation"
      next_action: "Phase Complete - User Action Required to transition to next phase"
      next_phase: "Set-up/Maintenance" # Or "Strategy" or "Project Complete"
      ```

      ```
      [LAST_ACTION_STATE]
      last_action: "Completed Cleanup/Consolidation Phase (All Steps)"
      current_phase: "Cleanup/Consolidation"
      next_action: "Phase Complete - User Action Required to transition to next phase"
      next_phase: "Set-up/Maintenance" # 或 "Strategy" 或 "Project Complete"
      ```

---

## VI. Quick Reference (All Steps are CRITICAL)

## VI. 快速参考（所有步骤都是关键）

- **Objective**: **CRITICALLY** and comprehensively review the **entire project state**. Consolidate all verified learnings, outcomes, and essential information into persistent documentation. **Reorganize `changelog.md` by component/date for the entire project history.** Archive or remove obsolete files based on rigorous verification and consolidation.

- **目标**：**关键性地**和全面地审查**整个项目状态**。将所有验证的学习内容、结果和重要信息整合到持久化文档中。**按组件/日期为整个项目历史重新组织 `changelog.md`。** 基于严格的验证和整合归档或删除过时文件。

- **Order**: Consolidation (Section III) MUST be fully completed BEFORE Cleanup (Section IV).

- **顺序**：整合（第三节）必须完全完成于清理（第四节）之前。

- **Consolidation (Section III)**:
- **整合（第三节）**：

    - **Inputs (Comprehensive Review)**:
    - **输入（全面审查）**：

        - HDTA Templates (`cline_docs/templates/`)
        - HDTA 模板（`cline_docs/templates/`）
        - All Task Instruction files (from `tasks/` and `cline_docs/archive/`)
        - 所有任务指令文件（来自 `tasks/` 和 `cline_docs/archive/`）
        - All Implementation Plan files (from Code Root directories)
        - 所有实施计划文件（来自代码根目录）
        - All Strategic Tracking documents (roadmaps, checklists from `cline_docs/`, etc.)
        - 所有战略跟踪文档（来自 `cline_docs/` 的路线图、检查清单等）
        - Core state files: `activeContext.md`, `changelog.md` (entire history), `progress.md`
        - 核心状态文件：`activeContext.md`、`changelog.md`（整个历史）、`progress.md`

    - **Actions (All Mandatory & CRITICAL)**:
    - **操作（所有强制性和关键）**：

        1.  Review HDTA templates; List all Task Instructions, Impl. Plans, Strategic Trackers. Process in batches of ≤10 files; **Fully process each batch as a standalone task**.
        1.  审查 HDTA 模板；列出所有任务指令、实施计划、战略跟踪器。分批处理 ≤10 个文件；**将每个批次完全作为独立任务处理**。
        2.  For ALL Task Instructions: Read, **MANUALLY VERIFY OUTCOMES** (if outcome unverified, update task file & all references to show NOT complete; unverified tasks are NOT archived as complete). Extract ALL learnings/design choices.
        2.  对于所有任务指令：读取、**手动验证结果**（如果结果未验证，更新任务文件和所有引用以显示未完成；未验证的任务不作为完整归档）。提取所有学习内容/设计选择。
        3.  For ALL Impl. Plans: Read, cross-reference task verification, update plan status, extract strategic info.
        3.  对于所有实施计划：读取、交叉参考任务验证、更新计划状态、提取战略信息。
        4.  For ALL Strategic Trackers: Review, consolidate older versions into newest, update status based on verified tasks.
        4.  对于所有战略跟踪器：审查、将旧版本整合到最新版本、根据已验证的任务更新状态。
        5.  Identify ALL information for consolidation from the above reviews.
        5.  从上述审查中识别所有需要整合的信息。
        6.  Update HDTA docs (`system_manifest.md`, `*_module.md`, `implementation_plan_*.md`).
        6.  更新 HDTA 文档（`system_manifest.md`、`*_module.md`、`implementation_plan_*.md`）。
        7.  Update Core Files: `progress.md`, `userProfile.md`.
        7.  更新核心文件：`progress.md`、`userProfile.md`。
        8.  Review, Refine, & Update `.clinerules` `[LEARNING_JOURNAL]` (group, combine, remove inappropriate, add new).
        8.  审查、精炼和更新 `.clinerules` `[LEARNING_JOURNAL]`（分组、组合、删除不适当的、添加新的）。
        9.  Reorganize ENTIRE `changelog.md` (Parse->Group by Component->Sort by Date->Format->Write).
        9.  重新组织整个 `changelog.md`（解析 -> 按组件分组 -> 按日期排序 -> 格式化 -> 写入）。
        10. Update `activeContext.md` to reflect fully consolidated project baseline.
        10. 更新 `activeContext.md` 以反映完全整合的项目基线。

    - **Tools**: `list_files`, `read_file`, `write_to_file`, `apply_diff`.
    - **工具**：`list_files`、`read_file`、`write_to_file`、`apply_diff`。

- **Cleanup (Section IV)**:
- **清理（第四节）**：

    - **Inputs (Derived from Section III)**: Verified list of fully completed & consolidated Task Instructions; Fulfilled Strategy Tasks; Obsolete (fully consolidated) session files/trackers; Other confirmed obsolete files.
    - **输入（来自第三节）**：完全完成和整合的任务指令的验证列表；已履行的策略任务；过时的（完全整合的）会话文件/跟踪器；其他确认的过时文件。

    - **Actions (All Mandatory & CRITICAL)**:
    - **操作（所有强制性和关键）**：

        1.  Identify cleanup targets **based on Section III's verified outputs.**
        1.  根据第三节的验证输出**识别清理目标**。
        2.  Determine archive strategy (archive preferred); Check/Create archive dirs (confirm command with `ask_followup_question`).
        2.  确定归档策略（首选归档）；检查/创建归档目录（使用 `ask_followup_question` 确认命令）。
        3.  For each eligible file: Construct absolute paths, confirm archive/delete command with `ask_followup_question`, execute, document.
        3.  对于每个符合条件的文件：构建绝对路径，使用 `ask_followup_question` 确认归档/删除命令，执行，记录。
        4.  Verify files moved/removed (use `list_files`); Ensure `activeContext.md` is clean.
        4.  验证文件已移动/删除（使用 `list_files`）；确保 `activeContext.md` 是干净的。

    - **Tools**: `list_files`, `execute_command`, `ask_followup_question`.
    - **工具**：`list_files`、`execute_command`、`ask_followup_question`。

- **MUP Additions (Section V) (CRITICAL)**:
- **MUP 添加（第五节）（关键）**：

    - After Consolidation: Verify `activeContext.md`, `changelog.md`; Update `.clinerules` (last_action: "Completed ALL Consolidation...", next_action: "Begin Cleanup...").
    - 整合后：验证 `activeContext.md`、`changelog.md`；更新 `.clinerules`（last_action："Completed ALL Consolidation..."，next_action："Begin Cleanup..."）。
    - After Cleanup (Exiting Phase): Verify `activeContext.md`; Update `.clinerules` (last_action: "Completed Cleanup/Consolidation Phase (All Steps)...", next_action: "Phase Complete...").
    - 清理后（退出阶段）：验证 `activeContext.md`；更新 `.clinerules`（last_action："Completed Cleanup/Consolidation Phase (All Steps)..."，next_action："Phase Complete..."）。
