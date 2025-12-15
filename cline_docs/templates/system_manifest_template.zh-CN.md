<!--
说明：填写以下占位符以创建系统清单。
本文档提供整个系统的高层级概览。
*请勿在创建的文件中包含这些注释。*
-->

# 系统：{SystemName}

## 目的
{描述系统目的的 1-2 句话}

## 架构
{系统模块的 ASCII 图表}

## 模块注册表
- [{ModuleName1} (`{path/to/ModuleName1_module.md}`)]：{简要描述}
- [{module_dir}/{module_dir2}]：{简要描述}
...

## 开发工作流程
1. {第一步}
2. {第二步}
...

## 版本：{version} | 状态：{status}

---

以下是一个假设库存管理系统的简约示例：

**系统清单：**

# 系统：库存管理系统

## 目的
跟踪电子商务平台的产品库存、订单和发货。

## 架构
[前端] <-> [api_gateway] <-> [服务] <-> [数据库]
  |                |             |            |
  |                |             |            +-- [数据模型]
  |                |             +-- [订单服务]
  |                |             +-- [库存服务]
  |                |             +-- [发货服务]
  |                +-- [认证]
  +-- [管理 UI]
  +-- [客户 UI]

## 模块注册表
- [前端 (`src/frontend/frontend_module.md`)]：用户界面
- [src/frontend/api_gateway]：请求路由
- [src/frontend/api_gateway/services]：业务逻辑
- [src/frontend/api_gateway/services/database]：数据存储

## 开发工作流程
1. 更新文档
2. 创建任务指令
3. 实现功能
4. 测试和验证
5. 记录变更

## 版本：0.2 | 状态：开发中
