---
title: "AI4PROGRAMMING 模板 v0.1.0 发布说明"
document_id: "REL-AI4PROGRAMMING-TEMPLATE-0.1.0"
produced_at: "2026-09-13"
version: "v0.1.0"
status: "已发布（本地）"
owner: "发布管理"
baseline: "REL-001；AI4PROGRAMMING 根级与工程级模板基线"
---

# AI4PROGRAMMING 模板 v0.1.0 发布说明

## 1. 授权、范围与状态

- 用户发布授权：用户明确要求发布“模板发行版”到 `AI4PROGRAMMING/release/`，并确认采用 MIT 许可证。
- 发布目标和副作用：本地目录 `release/ai4programming-template-v0.1.0/`；未上传、部署、重启、推送、签名或写入外部系统。
- 版本范围和非目标：仅发布通用软件项目模板、工程规则、脚本、测试、配置示例、文档和声明式发布骨架；不发布产品功能、真实数据、秘密、运行日志、内部项目管理材料或产品验收结论。
- 当前状态：已发布（本地模板发行版）。

## 2. 版本内容

| 类型 | 资产/变更 | 来源 | 校验/版本 | 是否纳入 |
| --- | --- | --- | --- | --- |
| 模板规则 | 根级 `AGENTS.md`、`README.md` | AI4PROGRAMMING 根目录 | v0.1.0 | 是 |
| 工程模板 | `projectname/project/` | 工程模板基线 | v0.1.0 | 是 |
| 许可证 | 根级与工程级 `LICENSE` | 用户选择 MIT | MIT | 是 |
| 发布清单与回滚 | `RELEASE-MANIFEST.md`、`ROLLBACK.md`、`MANIFEST.sha256` | 本次受控发布 | v0.1.0 | 是 |
| 内部治理材料 | `projectname/achieve/00-项目管理/` | 项目管理目录 | 不适用 | 否 |

## 3. 验证与烟测

| 项目 | 命令/方法 | 结果 | 证据 | 未执行原因 |
| --- | --- | --- | --- | --- |
| 治理静态检查 | `python projectname/project/scripts/f001_governance_validate.py --project-root . --check` | 通过，退出码 0 | 项目管理质量记录 | 不适用 |
| 包内容审阅 | 核对版本目录、排除项与发行清单 | 通过 | `release/ai4programming-template-v0.1.0/RELEASE-MANIFEST.md` | 不适用 |
| 完整性校验 | 核对 `MANIFEST.sha256`、ZIP 内容与 ZIP SHA-256 | 通过；包内 81 个文件均已列入清单，ZIP 含 91 个目录/文件条目 | `release/ai4programming-template-v0.1.0/MANIFEST.sha256`、`ai4programming-template-v0.1.0.zip.sha256` | 仅适用于本地包 |
| 产品测试/部署烟测 | 不适用 | 未执行 | 模板无产品运行入口 | 模板不包含产品功能或部署目标 |

## 4. 回滚、限制与交接

- 回滚触发条件和步骤：发现包中含秘密、真实数据、内部治理材料、来源不明文件或错误版本时，停止分发，保留现有目录作审计，并以新版本目录发布修正包；详见 `ROLLBACK.md`。
- 已知限制与未验证项：模板没有业务功能、产品构建物、锁文件、CI、产品独立 QA 或部署验证；不得据此声明任何产品已可用。
- 外部写入、部署或重启记录：无。
- 项目监理关闭记录：REL-001 已按本地模板发行关闭；监督、质量、日志、变更和成本记录位于 `achieve/00-项目管理/` 对应目录。
