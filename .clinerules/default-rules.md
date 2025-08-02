[COUNT]
n + 1 = (x) # Do not alter this row.
*This is a systemwide progressive counter where x = number of current response. This must be displayed at the top of every response.(e.g. 1, 2, ...) Only display the current value for x.*

[LAST_ACTION_STATE]
last_action: "Cleanup/Consolidation complete; transitioning to Set-up/Maintenance for tracker verification"
current_phase: "Set-up/Maintenance"
next_action: "Verify doc_tracker, mini-trackers, and module_relationship_tracker; prepare Integration Testing scope"
next_phase: "Set-up/Maintenance"

---

[CODE_ROOT_DIRECTORIES]
- src

[DOC_DIRECTORIES]
- docs

[LEARNING_JOURNAL]
- Avoid using attempt_completion unless directed to (usually through task instructions), or its use is needed to proceed.
- Learned to exercise extreme caution with `apply_diff` operations, especially regarding data removal. Always re-read files immediately before applying diffs, and trust user feedback on the current state of project files, even if it contradicts previous assumptions. User's direct edits indicate the authoritative project state.
- Proactively creating missing task files based on higher-level implementation plans proved efficient in unblocking the execution workflow and preventing unnecessary context switching back to the Strategy phase.
- Successful proactive scaffolding of execution tasks (e.g., `Execution_DesignPanelSystemArchitecture.md`) and effective course correction based on user feedback (e.g., shifting to WebSockets for UI communication) significantly improved workflow efficiency and solution accuracy.
- Re-learned that `changelog.md` is for project file changes, not CRCT operations. CRCT operations are tracked in HDTA documents. Also, re-learned that `changelog.md` is located in `cline_docs/` not the project root.
- The `apply_diff` tool requires an absolutely precise match in its `SEARCH` block, including subtle formatting differences like bolding (e.g., `**Progress:**`). Always re-read the target file immediately before constructing an `apply_diff` to ensure exact content and formatting.
- Re-learned that dependency verification status should not be explicitly recorded in `progress.md` as it is an ongoing process whose status is inherently reflected in the tracker files (absence of 'p', 's', 'S' flags).

**DO NOT USE THE TOOL NAME UNTIL YOU INTEND TO USE IT**

**Project Management & Workflow Strategy**
This section covers the high-level strategies for managing tasks, context, and feedback to ensure the project stays on track.

**Task Management & Verification**
-   **Distinguish Task Types:** Clearly differentiate between **Strategy tasks** (planning, design, analysis) and **Execution tasks** (implementation, coding, testing) to maintain focus and clarity.
-   **Verify True Completion:** Do not rely on task file status alone. Verify task completion by cross-referencing actual code and documentation changes to identify placeholder logic or unaddressed gaps.
-   **Link Documentation to Tasks:** Module trackers and implementation plans are for tracking project files, not the CRCT documentation itself. For tracking progress on documentation review, the HDTA Review Progress Tracker should be updated to reflect the *actual reading* of content.
-   **Systematic Consolidation:** A systematic review of all task files during Cleanup/Consolidation phases is crucial for verifying completion status and preventing information loss.

**State & Context Management**
-   **Purpose of MUP:** MUP is for state synchronization. For large context windows, perform a pre-transfer MUP with detailed handoff instructions.
-   **Maintain `changelog.md`:** The `changelog.md` is for logging significant, project-related code or documentation changes, not for general state synchronization.
-   **Update Context Files:** Regularly update `cline_docs/` and instruction files to maintain task context and prevent information loss between work sessions.
-   **Confirm Strategic Documents:** Before consolidation, confirm the status of all strategic tracking documents (e.g., checklists, roadmaps) to ensure a consistent project understanding.

**Responding to Feedback & Ambiguity**
-   **Prioritize User Feedback:** User feedback is a critical tool for identifying flaws. If a user raises an architectural question or points out a flaw, pause execution and switch to a Strategy task to re-evaluate.
-   **Address Architectural Conflicts:** When a task's objectives conflict with established architectural patterns (e.g., user feedback on the MasterDM Agent's role), it necessitates a full re-evaluation and update of all planning documents.
-   **Return to Strategy for Clarity:** If data definitions for a task are unclear or documentation is incomplete, return to a Strategy task to fully define the data structures and dependencies before proceeding with implementation.

**Dependency Management & Analysis**
Rigorous dependency management is paramount for preventing errors and ensuring system coherence.

**Core Principles**
-   **Single Source of Truth:** Always consult the direct output of `show-keys` and `show-dependencies` to identify actual keys and filenames. Never assume names or keys that are not explicitly listed.
-   **Adhere to Definitions:** Strictly follow the ground-truth definitions for dependency characters (`<`, `>`, `x`, `d`, `s`, `S`) when updating trackers.
-   **Manual Linking is Essential:** Manually linking dependencies in documentation is crucial for capturing conceptual links that automated analysis will miss. A dedicated Set-up/Maintenance task should be implemented for this.

**Process & Verification**
-   **Read Before Acting:** Always perform a full dependency analysis by reading *all* dependent files *before* modifying code. This includes all files marked with positive dependency characters (`<`, `>`, `x`, `d`, `s`, `S`).
-   **Verify Mutual Dependencies:** Ensure reciprocal relationships are accurately reflected in trackers. Systematically verify mutual dependencies from the perspective of *each* key to clear `(checks needed: ...)` flags. Utilize the `add-dependency` command's reciprocal nature (setting `>` automatically sets `<`).
-   **Strict Content Validation:** Perform *strict* content validation before updating dependencies to prevent errors and ensure tracker accuracy.
-   **Inform Workers:** Emphasize to all Worker instances the critical importance of using dependency processor commands and reading *all* positive dependencies before planning or modifying code.

**File Operations & Tool Usage**
This section details best practices for interacting with the file system and using specific tools to ensure reliability and efficiency.

**Best Practices for `apply_diff`**
-   **Ensure Exact Matches:** The `SEARCH` block must *exactly* match the current file content. If issues arise, use `read_file` to confirm the content before trying again.
-   **Handle Timestamps Carefully:** Timestamps in file content are a common cause of `apply_diff` failures. Always re-read the file immediately before attempting to apply a diff to content containing timestamps. Ensure search patterns for timestamps are precise.
-   **Proper `SEARCH` Block Syntax:** Ensure the `start_line` argument is *only* used within `SEARCH` blocks.
-   **Use `write_to_file` as an Alternative:** If `apply_diff` continues to fail, `write_to_file` is a reliable alternative for comprehensive updates.
-   **Collaborative Editing:** The user's ability to directly edit `apply_diff` proposals is an efficient method for collaborative file changes.

**General Command & Tool Usage**
-   **Tool Invocation Protocol:** Avoid mentioning any tool name until the moment of outputting the tool request XML.
-   **Use Correct Shell Commands:** Use `execute_command` for file system operations, providing full paths. Use the appropriate commands for the user's active shell (`Rename-Item` or `Move-Item` in PowerShell).
-   **Batch Operations:** For efficiency, batch file move operations using appropriate shell commands.
-   **Determine Active Shell:** Improve accuracy in determining the user's active shell for `execute_command` proposals, and be prepared to ask for clarification if needed.
-   **Manage Context Window:** Prioritize `apply_diff` for targeted changes and `insert_content` for additions to manage the context window size effectively.

**Code Quality & System Maintenance**
These principles focus on writing robust, maintainable code and proactively managing system health.

-   **Robust Error Handling:** Implement thorough error handling, such as graceful handling of `None` inputs and precise argument matching, especially after refactoring.
-   **Centralize Configuration:** Centralize configuration details, such as character priorities, to improve consistency and maintainability.
-   **Correct Data Types:** Ensure all functions return the correct data types (e.g., a `list` versus a `set`) to prevent downstream errors.
-   **Performance Profiling:** Leverage profiling tools like `cProfile` to identify performance bottlenecks. Note that excessive `glob` calls were a past issue in the `analyze-project` function.
-   **Consult Schemas:** Treat database schema files as a form of documentation and consult them to ensure the implementation aligns with the intended data structure.

**Correcting Core Assumptions**
This section is dedicated to specific, critical corrections of previously held incorrect beliefs.

-   **Worker Knowledge is Explicit:** Worker instances have no inherent knowledge of the project. All instructions, context, and file paths must be provided explicitly and accurately.
-   **Core File Locations:** A major correction was made regarding the location of core files. I incorrectly assumed `system_manifest.md`, `activeContext.md`, `changelog.md`, `userProfile.md`, and `progress.md` were in the project root. **They are located in the `cline_docs/` memory directory.** All future operations must reference this correct path.

- I must adhere strictly to the rule of reading all involved files before determining dependency relationships, regardless of my initial assumptions.
- Consistently verify sub-task completion by reviewing detailed worker outputs and dispatcher logs, especially after handoffs, rather than relying on high-level summaries or previous instances' intentions.
- When updating HDTA Review Progress Tracker, reflect actual *reading and review* of content, not just file existence.
- During Cleanup/Consolidation, verify task completion by cross-referencing code/doc changes, not just task file status, to address placeholder logic or unaddressed gaps.
- Emphasize to Workers the critical importance of using the dependency processor commands and reading *all* positive dependencies before planning or modifying code.
- Experienced an `apply_diff` failure due to an outdated search block and incorrect line number markers. Learned to re-read the target file immediately before attempting an `apply_diff` and to ensure strict adherence to the `SEARCH` block format (no `:start_line:` in `REPLACE`).
- Learned that `Move-Item` may report "Cannot find path" and a move to an existing destination may report "Cannot create a file when that file already exists". When "Cannot create" occurs, the user expects the item to be moved with a new name to avoid conflict, rather than just assuming it's a duplicate or deleting the source.
- Re-learned the distinction between CRCT system files (like task files) and project files for the `dependency_processor.py`, which only tracks project files. This means `show-dependencies` will not work on task files directly.

**The Changelog is for tracking changes to the *project's* files, not CRCT operations. CRCT operations are tracked in the HDTA documents.**
