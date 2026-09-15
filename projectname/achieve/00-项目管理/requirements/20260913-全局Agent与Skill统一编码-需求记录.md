---
title: "全局Agent与Skill统一编码需求记录"
document_id: "REQ-20260913-AGENT-SKILL-CODE"
produced_at: "2026-09-13"
status: "已完成"
owner: "项目监理"
---

# 全局Agent与Skill统一编码需求记录

## 1. 来源与背景

- 用户原意摘要：统一全局 `.codex` 中与 AI4PROGRAMMING 相关的 Agent/Skill 编码，并同步项目引用。
- 来源轮次/证据：2026-09-13 用户请求；AI4PROGRAMMING 根级与工程级规则。
- 当前问题与影响：原标识无统一代号；改名会影响全局配置、Skill 路径和项目调用链。

## 2. 原子需求

| 需求 ID | 要求 | 优先级 | 范围 | 非目标 | 验收标准 | 状态 |
|---|---|---|---|---|---|---|
| REQ-CODE-01 | 为软件项目 Agent 使用职责代号并统一文件名 | P0 | 全局 Agent 与 AI4PROGRAMMING 调用面 | 不改科研专用 Agent 编码 | 配置可解析且调用引用一致 | 已完成 |
| REQ-CODE-02 | 为软件项目 Skill 使用代号前缀并同步 frontmatter/路径 | P0 | 8 个通用软件 Skill | 不改 PS 与外部浏览器 Skill | 8 个 Skill 通过结构校验 | 已完成 |
| REQ-CODE-03 | 同步全局配置、AI4PROGRAMMING 文档和受影响现行项目入口 | P0 | `.codex/config.toml`、Agent TOML、项目现行文档 | 不重写历史事实日志 | 无旧调用路径，配置和门禁通过 | 已完成 |

## 3. 约束与决定

| 类型 | 内容 | 来源 | 决策人 | 状态 |
|---|---|---|---|---|
| 用户决定 | 使用 PS/PM/AR/EN/QA/RL 职责代号；保留 PS-00 至 PS-09 | 用户 | 用户 | 已确认 |
| 事实 | 架构师 Agent 需补充全局注册，专业能力由 AR-01 Skill 提供 | 配置检查 | 项目监理 | 已完成 |
| 约束 | 科研专用 Skill 不纳入本次软件编码迁移 | 范围控制 | 项目监理 | 已执行 |

## 4. 追溯与关闭

| 需求 ID | 设计/实现 | 测试/证据 | 日志/变更 | 关闭决定 |
|---|---|---|---|---|
| REQ-CODE-01~03 | 全局配置、Agent TOML、Skill 目录、项目入口文档 | TOML 解析、Skill 校验、F001/F002、回归测试 | 本批日志、本批变更和质量门禁 | 已关闭 |
