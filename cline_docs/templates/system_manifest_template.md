<!--
Instructions:  Fill in the placeholders below to create the System Manifest.
This document provides a high-level overview of the entire system.
*Do NOT include these comments in the created file.*

说明: 填写以下占位符以创建系统清单。
本文档提供整个系统的高层级概览。
*请勿在创建的文件中包含这些注释。*
-->

# System: {SystemName}

# 系统: {SystemName}

## Purpose

## 目的

{1-2 sentences describing system purpose}

{描述系统目的的 1-2 句话}

## Architecture

## 架构

{ASCII diagram of system Modules}

{系统模块的 ASCII 图}

## Module Registry

## 模块注册表

- [{ModuleName1} (`{path/to/ModuleName1_module.md}`)]: {brief description} / {简要描述}
- [{module_dir}/{module_dir2}]: {brief description} / {简要描述}
...

## Development Workflow

## 开发工作流程

1. {First step} / {第一步}
2. {Second step} / {第二步}
...

## Version: {version} | Status: {status}

## 版本: {version} | 状态: {status}

---

Here's a minimalist example for a hypothetical inventory management system:

以下是一个假设性库存管理系统的极简示例:

**System Manifest:** / **系统清单:**

# System: Inventory Management System

# 系统: 库存管理系统

## Purpose

## 目的

Tracks product inventory, orders, and shipments for e-commerce platform.

跟踪电子商务平台的产品库存、订单和发货。

## Architecture

## 架构

[frontend] <-> [api_gateway] <-> [services] <-> [database]
  |                |             |            |
  |                |             |            +-- [Data Models] / [数据模型]
  |                |             +-- [Order Service] / [订单服务]
  |                |             +-- [Inventory Service] / [库存服务]
  |                |             +-- [Shipping Service] / [发货服务]
  |                +-- [Auth] / [认证]
  +-- [Admin UI] / [管理界面]
  +-- [Customer UI] / [客户界面]

## Module Registry

## 模块注册表

- [frontend (`src/frontend/frontend_module.md`)]: User interfaces / 用户界面
- [src/frontend/api_gateway]: Request routing / 请求路由
- [src/frontend/api_gateway/services]: Business logic / 业务逻辑
- [src/frontend/api_gateway/services/database]: Data storage / 数据存储

## Development Workflow

## 开发工作流程

1. Update documentation / 更新文档
2. Create task instructions / 创建任务指令
3. Implement features / 实施功能
4. Test and validate / 测试和验证
5. Document changes / 记录变更

## Version: 0.2 | Status: Development

## 版本: 0.2 | 状态: 开发中
