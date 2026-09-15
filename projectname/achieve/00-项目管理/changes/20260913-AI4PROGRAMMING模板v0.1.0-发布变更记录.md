---
title: "AI4PROGRAMMING 模板 v0.1.0 发布变更记录"
document_id: "CHG-AI4PROGRAMMING-TEMPLATE-0.1.0"
produced_at: "2026-09-13"
status: "已完成"
owner: "发布管理"
---

# AI4PROGRAMMING 模板 v0.1.0 发布变更记录

| 变更 ID | 类型 | 变更对象 | 原因 | 用户/下游影响 | 兼容性 | 验证状态 | 回滚/迁移 |
|---|---|---|---|---|---|---|---|
| CHG-TEMPLATE-RELEASE-001 | 新增 | 本地 v0.1.0 模板目录包、ZIP、清单、回滚说明和发布说明 | 用户授权模板发行并采用 MIT | 可用于派生项目；不代表产品可用 | 无产品 API/数据变化 | F001、2 项模板测试、清单与 ZIP 复核通过 | 保留版本目录；以新版本目录替代，不覆盖 |
| CHG-TEMPLATE-LICENSE-001 | 变更 | 根级与工程 `LICENSE`、README 许可证声明 | 用户采用 MIT | 派生项目需遵守 MIT 并确认自身第三方许可 | 不改变产品运行行为 | L5 许可证复核通过 | 后续变更须以新发布版本记录 |

## 关联材料

- 需求/问题：`../requirements/20260913-AI4PROGRAMMING发布请求-需求记录.md`。
- 实现/设计：`../../../04-交付与阶段/20260913-AI4PROGRAMMING模板v0.1.0-发布说明.md`。
- 测试/证据：`../quality/20260913-AI4PROGRAMMING模板v0.1.0-质量门禁.md`。
- 发布/验收状态：本地模板发行完成；未进行外部发布或产品验收。
