<!--
Instructions: Fill in the placeholders below to create an Implementation Plan.
This document details the plan for a specific feature, refactor, or significant
change, potentially spanning multiple files/components within a Domain Module.
It forms a key segment of the project roadmap defined during the Strategy phase.
*Do NOT include these comments in the created file.*

说明: 填写以下占位符以创建实施计划。
本文档详细说明了特定功能、重构或重大变更的计划,
可能跨越领域模块内的多个文件/组件。
它构成了在 Strategy - 策略阶段定义的项目路线图的关键部分。
*请勿在创建的文件中包含这些注释。*
-->

# Implementation Plan: {Brief Objective or Feature Name}

# 实施计划: {简短目标或功能名称}

**Parent Module(s)**: [{Module1Name}_module.md], [{Module2Name}_module.md] <!-- Link to relevant Domain Module(s) -->
**父模块**: [{Module1Name}_module.md], [{Module2Name}_module.md] <!-- 链接到相关的领域模块 -->
**Status**: [ ] Proposed / [ ] Planned / [ ] In Progress / [ ] Completed / [ ] Deferred
**状态**: [ ] 已提议 / [ ] 已规划 / [ ] 进行中 / [ ] 已完成 / [ ] 已推迟

## 1. Objective / Goal

## 1. 目标 / 目的

<!-- Clearly state the specific goal this plan aims to achieve. What user story, feature, or refactoring is being addressed? -->
<!-- 清楚地说明此计划旨在实现的特定目标。正在解决什么用户故事、功能或重构? -->

{Describe the primary goal of this implementation plan.}

{描述此实施计划的主要目标。}

## 2. Affected Components / Files

## 2. 受影响的组件 / 文件

<!-- List the key code files, documentation files, modules, or data structures expected to be created or modified by this plan. Link keys where possible. -->
<!-- 列出由此计划预期创建或修改的关键代码文件、文档文件、模块或数据结构。尽可能链接键。 -->

*   **Code:** / **代码:**
    *   `{path/to/file1.py}` (Key: `{key1}`) - {Brief reason for involvement} / {参与的简要原因}
    *   `{path/to/moduleA/}` (Key: `{keyA}`) - {Brief reason for involvement} / {参与的简要原因}
*   **Documentation:** / **文档:**
    *   `{docs/path/doc1.md}` (Key: `{keyD1}`) - {Brief reason for involvement} / {参与的简要原因}
*   **Data Structures / Schemas:** / **数据结构 / 模式:**
    *   {Schema Name / Data Structure} - {Brief reason for involvement} / {参与的简要原因}

## 3. High-Level Approach / Design Decisions

## 3. 高层级方法 / 设计决策

<!-- Describe the overall strategy for achieving the objective. Outline key design choices, algorithms, or patterns to be used. -->
<!-- 描述实现目标的总体策略。概述关键设计选择、算法或要使用的模式。 -->

*   **Approach:** {Describe the sequence or method.} / **方法:** {描述序列或方法。}
*   **Design Decisions:** / **设计决策:**
    *   {Decision 1}: {Rationale} / {理由}
    *   {Decision 2}: {Rationale} / {理由}
*   **Algorithms (if applicable):** / **算法 (如适用):**
    *   `{Algorithm Name}`: {Brief description and relevance} / {简要描述和相关性}
*   **Data Flow (if significant):** / **数据流 (如重要):**
    *   {Brief description or link to a diagram/section} / {简要描述或链接到图表/部分}

## 4. Task Decomposition (Roadmap Steps)

## 4. 任务分解 (路线图步骤)

<!-- List the atomic Task Instructions required to execute this plan. Tasks should have Strategy_* or Execution_* prefixes. -->
<!-- 列出执行此计划所需的原子任务指令。任务应具有 Strategy_* 或 Execution_* 前缀。 -->

*   [ ] [Task 1 File](path/to/Strategy_Task1.md) (`{task1_key}`): {Brief description of task objective} / {任务目标的简要描述}
*   [ ] [Task 2 File](path/to/Execution_Task2.md) (`{task2_key}`): {Brief description of task objective} / {任务目标的简要描述}
*   [ ] [Task 3 File](path/to/Execution_Task3.md) (`{task3_key}`): {Brief description of task objective} / {任务目标的简要描述}
*   ...

## 5. Task Sequence / Build Order

## 5. 任务序列 / 构建顺序

<!-- Define the required execution order for the tasks listed above, based on dependency analysis. Provide rationale if needed. -->
<!-- 根据依赖分析定义上述任务所需的执行顺序。如需要,提供理由。 -->

1.  Task 2 (`{task2_key}`) - *Reason: Prerequisite for Task 3.* / *原因: 任务 3 的前置条件。*
2.  Task 3 (`{task3_key}`)
3.  Task 1 (`{task1_key}`) - *Reason: Can be done after core logic.* / *原因: 可以在核心逻辑完成后完成。*
4.  ...

## 6. Prioritization within Sequence

## 6. 序列内的优先级

<!-- Indicate the priority of tasks within the determined sequence (e.g., P1, P2, P3, or High/Medium/Low). -->
<!-- 指示在确定序列中任务的优先级 (例如,P1、P2、P3 或 高/中/低)。 -->

*   Task 2 (`{task2_key}`): P1 (Critical Path) / P1 (关键路径)
*   Task 3 (`{task3_key}`): P1
*   Task 1 (`{task1_key}`): P2
*   ...

## 7. Open Questions / Risks

## 7. 未解决的问题 / 风险

<!-- Document any unresolved questions or potential risks associated with this plan. -->
<!-- 记录与此计划相关的任何未解决的问题或潜在风险。 -->

*   {Question/Risk 1} / {问题/风险 1}
*   {Question/Risk 2} / {问题/风险 2}
