---
title: "AI4PROGRAMMING 模板 v0.1.0 质量门禁"
document_id: "QG-AI4PROGRAMMING-TEMPLATE-0.1.0"
produced_at: "2026-09-13"
status: "通过（本地模板发行）"
owner: "项目监理、发布管理"
---

# AI4PROGRAMMING 模板 v0.1.0 质量门禁

| 层级 | 检查项 | 命令/方法 | 环境/样本 | 结果 | 证据 | 处置 |
|---|---|---|---|---|---|---|
| L1 | 治理、命名、路径与功能登记 | `python projectname/project/scripts/f001_governance_validate.py --project-root . --check` | 本地源项目 | 通过，退出码 0 | 本批命令输出 | 已记录 |
| L2 | 模板治理脚本回归 | `python -m unittest discover -s tests -v` | `projectname/project` | 通过，2/2 | `test_f001_governance_validate`、`test_f002_skill_promotion_audit` | 已记录 |
| L3 | 构建、迁移、集成 | 适用性审阅 | 空白模板 | 不适用 | 模板无构建、锁文件、迁移或运行服务 | 不虚构结果 |
| L4 | 产品用户路径/部署烟测 | 适用性审阅 | 空白模板 | 不适用 | 模板无产品 API、UI 或部署目标 | 不虚构结果 |
| L5 | 许可证、清单、归档、回滚、ZIP 内容与完整性 | 复核 MIT、`MANIFEST.sha256`、`ROLLBACK.md`、ZIP 条目和 ZIP SHA-256 | 本地发布目录 | 通过 | 81 个包文件均在清单中；ZIP 91 个目录/文件条目；`389f8f576b3006329b892fa410f6c65c2a71ff3c533480107c64975a94bd5d6b` | 已归档 |

## 结论

- 门禁结论：通过（仅限本地模板发行）。
- 未执行项及原因：产品构建、产品 QA、部署烟测和外部发布均不适用且未获授权。
- 残余风险：MIT 中的版权声明采用“AI4PROGRAMMING Contributors”；实际贡献者/权利人应在后续贡献和公开发布前维护其署名与第三方许可。
- 下一步：派生项目在产生产品功能后，按其需求、架构、测试和发布流程建立独立版本。
