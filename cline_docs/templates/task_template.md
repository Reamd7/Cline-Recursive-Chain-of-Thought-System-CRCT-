<!--
Instructions: Fill in the placeholders below to create a Task Instruction document.
This document provides detailed, procedural guidance for a specific task. Provide ONLY the MINIMAL necessary context for THIS task.
- Use precise links to specific definitions/sections (e.g., `file.py#MyClass.my_method`, `doc_key#Section Title`).
- Link to prerequisite Task keys ONLY if they produce a direct, necessary input for THIS task.
*Do NOT include these comments in the created file.*

说明: 填写以下占位符以创建任务指令文档。
本文档为特定任务提供详细的程序性指导。仅提供此任务所需的最少必要上下文。
- 使用精确链接指向特定定义/部分 (例如,`file.py#MyClass.my_method`、`doc_key#Section Title`)。
- 仅当前置任务键为此任务产生直接的必要输入时,才链接到它们。
*请勿在创建的文件中包含这些注释。*
-->

# Task: {TaskName}

# 任务: {TaskName}

   **Parent:** `implementation_plan_{filename}.md` or {ParentTask} / **父级:** `implementation_plan_{filename}.md` 或 {ParentTask}
   **Children:** {Optional: Links to specific, separate .md task files generated or delegated by this task} / **子级:** {可选: 链接到由此任务生成或委托的特定、独立的 .md 任务文件}
<!-- Use sparingly. For pre-planned decomposition, nest tasks under an Implementation Plan. This field is for tasks that dynamically spawn other distinct, trackable .md tasks during their execution/planning. -->
<!-- 谨慎使用。对于预先计划的分解,将任务嵌套在实施计划下。此字段适用于在其执行/规划期间动态生成其他不同、可跟踪的 .md 任务的任务。 -->

## Objective

## 目标

[Clear, specific goal statement]

[清晰、具体的目标陈述]

## Context

## 上下文

[What the LLM needs to know about the current state]

[LLM 需要了解的关于当前状态的信息]

## Steps

## 步骤

1. {Step 1} / {步骤 1}
2. {Step 2} / {步骤 2}
   - {Substep 2.1} / {子步骤 2.1}
   - {Substep 2.2} / {子步骤 2.2}
3. {Step 3} / {步骤 3}
...

## Dependencies **This *MUST* include dependencies from tracker files**

## 依赖关系 **必须包括来自跟踪器文件的依赖关系**

- Requires: [{Task1}], [{Module2}]  *(Manually manage these)* / (手动管理这些)
- Blocks: [{Task3}], [{Task4}]   *(Manually manage these)* / (手动管理这些)

## Expected Output

## 预期输出

{Description of expected results}

{预期结果的描述}
