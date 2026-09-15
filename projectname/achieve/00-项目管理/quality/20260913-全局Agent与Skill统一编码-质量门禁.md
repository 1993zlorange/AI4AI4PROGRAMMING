---
title: "全局Agent与Skill统一编码质量门禁"
document_id: "QG-20260913-AGENT-SKILL-CODE"
produced_at: "2026-09-13"
status: "已完成"
owner: "项目监理"
---

# 全局Agent与Skill统一编码质量门禁

| 层级 | 检查项 | 命令/方法 | 环境/样本 | 结果 | 证据 | 处置 |
|---|---|---|---|---|---|---|
| L1 | Agent/Skill 名称、路径、frontmatter、配置和引用 | PowerShell、Python tomllib、quick_validate | 全局配置与项目文档 | 通过 | 5 个 Agent 注册；8 个 Skill 校验通过；AI4PROGRAMMING 无未编码调用 | 无 |
| L2 | F001/F002 治理链路与既有回归 | Python unittest、F001、F002 | AI4PROGRAMMING 工程模板 | 通过 | 2/2 tests passed；ERROR=0 | 真实条目再扩展失败用例 |
| L3 | 外部项目调用兼容 | 静态扫描 | AI4SCIENCE 现行入口 | 带条件通过 | 现行入口已同步，历史材料未改写 | 新项目启动时验证 |

## 结论

- 门禁结论：通过（带历史调用迁移条件）
- 未执行项及原因：未做全局实际会话调用和外部项目全量回归。
- 残余风险：用户级缓存或外部文档可能保留旧标识；需要按新项目入口逐项验证。
- 下一步：在真实项目启动时执行新编码的端到端调用验证。
