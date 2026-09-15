---
title: "全局Agent与Skill统一编码变更记录"
document_id: "CHG-20260913-AGENT-SKILL-CODE"
produced_at: "2026-09-13"
status: "已完成"
owner: "项目监理"
---

# 全局Agent与Skill统一编码变更记录

| 变更 ID | 类型 | 变更对象 | 原因 | 用户/下游影响 | 兼容性 | 验证状态 | 回滚/迁移 |
|---|---|---|---|---|---|---|---|
| CHG-CODE-01 | 变更 | 5 个全局 Agent 文件、配置段和 name | 统一职责代号 | 后续调用使用 PS/PM/AR/EN/QA | 旧文件名不再存在；历史材料保留 | 通过 | 按映射表反向重命名并恢复配置 |
| CHG-CODE-02 | 变更 | 8 个通用软件 Skill 目录、frontmatter 和内部链接 | 统一技能代号 | AI4PROGRAMMING 调用改用 PM/AR/EN/QA/RL 编码 | PS、外部 Skill 和科研专用 Skill 保持不变 | 通过 | 按映射表恢复目录和 name |
| CHG-CODE-03 | 变更 | AI4PROGRAMMING、AI4SCIENCE 现行入口 | 防止全局路由断链 | 项目入口使用新 Agent/Skill 标识 | 历史记录不作为运行基线 | 通过 | 从版本化文档恢复旧引用 |

## 关联材料

- 需求/问题：REQ-20260913-AGENT-SKILL-CODE
- 实现/设计：全局 `.codex/config.toml`、Agent TOML、Skill 目录
- 测试/证据：全局配置解析、8 个 quick_validate、F001/F002、2/2 回归测试
- 发布/验收状态：未发布；本地治理变更已关闭
