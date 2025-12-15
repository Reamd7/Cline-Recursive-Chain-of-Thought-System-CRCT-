# Worker 子任务输出日志

**区域名称：** [区域名称]
**具体子任务指令：** [引用或准确总结来自 Dispatcher 的具体说明]
**执行日期：** [YYYY-MM-DD HH:MM]
**状态：** [ ] 进行中 | [ ] 已完成 | [ ] 失败 | [ ] 需要修订

## 考虑的背景

[记录 Worker 为此子任务明确考虑的特定文件读取、用于分析的命令运行（例如，show-dependencies）或其他背景。]

## 采取的行动

[总结 Worker 为完成此子任务执行的关键操作，参考策略插件的步骤或应用的特定逻辑。]

## 生成的输出

[列出此子任务创建或更新的特定文件（例如，新建/更新的 `_module.md`、`implementation_plan_*.md`、`task_*.md` 文件）。描述添加到其他文档的内容（例如，更新了 `activeContext.md` 部分，修改了清单条目）。]
*   **如果任何创建的任务指令文件列出"子级"（即，由此子任务动态生成的其他 `.md` 任务文件）：**
    *   父任务文件：`[path/to/parent_task.md]`
    *   子任务文件 1：`[path/to/child_task1.md]` - 简要目标：{child_task1 的目标}
    *   子任务文件 2：`[path/to/child_task2.md]` - 简要目标：{child_task2 的目标}
    *   ...（确保在此处列出所有此类子任务以便 Dispatcher 了解）

## Worker 观察和备注

[包括与此特定子任务相关的任何观察、遇到的挑战或 Dispatcher 应该了解的备注。]
