# 设置/维护阶段插件

本插件提供了 CRCT 系统设置/维护阶段的详细指导。在此阶段，系统将执行初始设置、项目配置和依赖跟踪器的维护。

## 设置/维护阶段概述

设置/维护阶段是 CRCT 系统的基础阶段，负责：
1. 初始系统设置
2. 识别代码根目录和文档目录
3. 创建和维护依赖跟踪器
4. 定期系统维护

## 核心流程

### 1. 初始设置

1. **读取 `.clinerules`**：确定当前阶段和上次操作状态。
2. **识别代码根目录和文档目录**：如果 `.clinerules` 中的 `[CODE_ROOT_DIRECTORIES]` 或 `[DOC_DIRECTORIES]` 为空，使用启发式方法识别这些目录。
3. **创建核心文件**：
   - `system_manifest.md`：系统清单，提供项目的高级概述
   - `activeContext.md`：跟踪当前状态、决策和优先级
   - `changelog.md`：记录重大代码库更改
   - `module_relationship_tracker.md`：记录模块级依赖关系
   - `doc_tracker.md`：记录文档依赖关系

### 2. 依赖跟踪器管理

1. **分析项目**：使用 `analyze-project` 命令分析项目，生成上下文键，更新依赖跟踪器，生成嵌入。
   ```bash
   python -m cline_utils.dependency_system.dependency_processor analyze-project
   ```

2. **验证依赖关系**：使用 `show-dependencies` 命令检查特定键的依赖关系。
   ```bash
   python -m cline_utils.dependency_system.dependency_processor show-dependencies --key <key>
   ```

3. **手动管理依赖关系**：使用 `add-dependency` 命令手动设置依赖关系。
   ```bash
   python -m cline_utils.dependency_system.dependency_processor add-dependency --tracker <tracker_file> --source-key <key> --target-key <key> --dep-type <char>
   ```

### 3. 强制更新协议 (MUP)

每次状态更改操作后，必须立即执行 MUP：
1. **更新 `activeContext.md`**：总结操作、影响和新状态。
2. **更新 `changelog.md`**：记录重大更改，包括日期、描述、原因和受影响的文件。
3. **更新 `.clinerules`**：添加到 `[LEARNING_JOURNAL]` 并更新 `[LAST_ACTION_STATE]`。
4. **验证**：确保更新之间的一致性。

## 阶段转换检查清单

在从设置/维护阶段转换到策略阶段之前，确保：
1. `doc_tracker.md` 和 `module_relationship_tracker.md` 没有 'p' 占位符（所有依赖关系已验证）。
2. `.clinerules` 中的 `[CODE_ROOT_DIRECTORIES]` 和 `[DOC_DIRECTORIES]` 部分正确填充。

## 依赖字符定义

- `<`：行依赖于列（源依赖于目标）。
- `>`：列依赖于行（目标依赖于源）。
- `x`：相互依赖（两者相互依赖）。
- `d`：文档依赖（源记录目标）。
- `o`：自依赖（仅用于跟踪器网格的对角线）。
- `n`：已验证无依赖（明确标记不存在依赖关系）。
- `p`：占位符（表示未验证或建议的依赖关系，需要手动审查）。
- `s`：语义依赖（弱 - 相似度分数在 0.05 到 0.06 之间）。
- `S`：语义依赖（强 - 相似度分数 0.07 或更高）。

## 上下文键理解

CRCT v7.5 使用分层键系统（`KeyInfo`）来表示文件和目录。键遵循 `Tier` + `DirLetter` + `[SubdirLetter]` + `[FileNumber]` 的模式（例如，`1A`、`1Aa`、`1Aa1`）。

- **Tier**：初始数字表示嵌套级别。顶级根目录是 Tier 1。
- **DirLetter**：大写字母（'A'、'B'、...）标识定义根目录内的顶级目录。
- **SubdirLetter**：小写字母（'a'、'b'、...）标识目录内的子目录。
- **FileNumber**：数字标识目录内的文件。

## 故障排除

- **初始化问题**：确保核心提示正确加载到 Cline 扩展中，并且满足所有先决条件。
- **依赖跟踪问题**：使用 `analyze-project` 刷新跟踪器和嵌入。检查 `.clinerules` 以正确配置代码和文档根目录。
- **命令错误**：确保命令正确输入并在适当的阶段使用。参考命令文档了解语法和用法。