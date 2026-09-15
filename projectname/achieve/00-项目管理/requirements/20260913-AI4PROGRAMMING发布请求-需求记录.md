---
title: "AI4PROGRAMMING 发布请求需求记录"
document_id: "REQ-20260913-RELEASE-001"
produced_at: "2026-09-13"
status: "已完成"
owner: "用户、项目发布管理"
---

# AI4PROGRAMMING 发布请求需求记录

## 1. 来源与背景

- 用户原意摘要：调用相关技能，将 AI4PROGRAMMING 项目发布到 `AI4PROGRAMMING/release` 中。
- 来源轮次/证据：2026-09-13 当前对话；用户已明确授权执行本地发布准备。
- 当前问题与影响：用户指定的根目录 `release/` 与项目根级规则规定的发布资产目录 `projectname/project/release/` 不一致；工程仍明确标识为无产品功能的空白模板。

## 2. 原子需求

| 需求 ID | 要求 | 优先级 | 范围 | 非目标 | 验收标准 | 状态 |
|---|---|---|---|---|---|---|
| REL-001 | 准备 AI4PROGRAMMING 的本地模板发行包 | P0 | 根目录 `release/` 中的模板包、版本清单、发布说明、验证与回滚记录 | 不上传、部署、重启、推送或覆盖既有文件 | 发布目录、版本、许可证和质量门均已确认，包内仅含获准资产 | 已完成：本地模板 v0.1.0 已发布 |

## 3. 约束与决定

| 类型 | 内容 | 来源 | 决策人 | 状态 |
|---|---|---|---|---|
| 用户决定 | 发布“模板发行版”，并明确指定根目录 `AI4PROGRAMMING/release/` | 当前对话 | 用户 | 已确认；本批目录例外 |
| 用户决定 | 采用 MIT 许可证 | 当前对话 | 用户 | 已确认 |
| 事实 | 项目规则的 `release_root` 是 `projectname/project/release`，不是根目录 `release` | 根级 `AGENTS.md` | 项目监理 | 已确认 |
| 事实 | 根目录 `release/` 为空；工程 `project/release/` 只有空的部署资产骨架 | 目录检查 | 项目监理 | 已确认 |
| 事实 | 工程为 `private: true` 的 `web-project-template`；无业务实现、测试或锁文件 | `README.md`、`package.json`、目录检查 | 项目监理 | 已确认 |
| 事实 | `LICENSE` 为待决定占位内容，CI 未配置 | `LICENSE`、`README.md` | 项目监理 | 已确认 |
| 事实 | 采用现有工程版本 `0.1.0`，发行包标识为 `v0.1.0` | `package.json` 与本批发布清单 | 发布管理 | 已执行 |

## 4. 追溯与关闭

| 需求 ID | 设计/实现 | 测试/证据 | 日志/变更 | 关闭决定 |
|---|---|---|---|---|
| REL-001 | `release/ai4programming-template-v0.1.0/` 与同名 ZIP；仅为模板发行版 | F001、2 项模板测试、清单和 ZIP 内容复核 | 本批发布日志、质量门禁、变更和成本记录 | 已关闭（本地发布） |
