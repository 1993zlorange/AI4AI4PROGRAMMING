---
title: "Axiom-reporter项目安装质量门禁"
document_id: "QG-20261012-AXIOM-INSTALL"
produced_at: "2026-10-12"
status: "完成，带已登记限制"
owner: "项目监理"
writing_level: "C"
---

# Axiom-reporter项目安装质量门禁

| 层级 | 检查项 | 命令/方法 | 环境/样本 | 结果 | 证据 | 处置 |
|---|---|---|---|---|---|---|
| L1 | 规则、路径和范围 | 来源 AGENTS/README/安装器人工检视；项目经理范围检查 | 来源版本 ab624f98da6cb9bf162a4dbf66e175976cd3acce | 目标为当前根；安装器无网络、子进程和凭据访问 | 来源仓库；项目经理回传 | 仅按已登记安装范围执行 |
| L1 | 安全扫描 | skill-scanner 2.0.13 的 static_analyzer、bytecode、pipeline、behavioral_analyzer、trigger_analyzer | 来源 skills/Axiom-reporter | Critical/High/Medium=0；LOW=1；INFO=1 | projectname/project/output/skill-install/20261012-axiom-reporter/skill-scanner.md | LOW 为中文描述按空格仅计 1 词，实际描述清晰；INFO 为官方大小写身份，按用户安装来源保留兼容例外；不宣称零发现或安全保证 |
| L1 | 项目检查 | python projectname/project/scripts/f001_governance_validate.py --project-root . --check | 当前项目根 | 前置 exit=0，ERROR=0；后置 ERROR=0 | 前置为主线程实际工具输出，不事后伪造文件；后置 projectname/project/output/skill-install/20261012-axiom-reporter/f001-after.txt | 错误为零；最终记录后再复核 |
| L1 | 通用技能格式 | skill-creator quick_validate.py .codex/skills/Axiom-reporter | 官方原版 name | exit=1；Name Axiom-reporter should be hyphen-case | projectname/project/output/skill-install/20261012-axiom-reporter/quick-validate.txt | 已知命名限制，非安装失败；按用户指定官方安装身份保留，不能说该检查通过 |
| L1 | 管理文档写作结构 | ps_04_validate_management_document.py <文档> --strict | 本批需求/监督/日志/变更/质量/成本共 6 份文档 | 最终状态更新后均 errors=0 warnings=0；QA=pass | 监理最终实际工具输出 | 通过 |
| L1 | 最终项目复核 | python projectname/project/scripts/f001_governance_validate.py --project-root . --check | 全部安装与治理记录完成后 | exit=0，ERROR=0 | 监理最终实际工具输出 | 通过 |
| L2 | 上游安装器正常、备份、预览、重复执行、旧标记升级、技能同步 | unittest | 指定版本上游测试 | Ran 9 tests in 0.018s；OK | projectname/project/output/skill-install/20261012-axiom-reporter/upstream-unittest.txt | 通过 |
| L3 | 当前项目实际安装 | 官方安装器预览与 --write --with-skill；再次写入；完整性核对 | 当前根现有 AGENTS | 标记各 1 组；原文保留；备份与原字节一致；技能副本与源字节一致；二次两个 unchanged | projectname/project/output/skill-install/20261012-axiom-reporter/install-preview.txt；install-write.txt；install-idempotence.txt；integrity-check.json | 安装及幂等通过 |
| L4 | 当前项目用户安装路径 | 项目经理符合性及独立 QA | 原规则保留、标记唯一、技能一致、重复 unchanged | 项目经理通过；独立 QA PASS；独立 preview exit=0，目标哈希无变化 | projectname/project/output/skill-install/20261012-axiom-reporter/qa-integrity.json；qa-preview.txt；projectname/achieve/03-测试与验收/20261012-Axiom-reporter项目安装-功能测试报告.md | 安装范围通过；不声明实际加载和用户正式验收 |
| L5 | 发布/全局技能晋升 | 不适用 | 用户只授权当前项目安装 | 未执行 | 本批需求与监督记录 | 无发布或全局晋升范围，不运行 F002 |

## 结论

- 门禁结论：带条件通过；本地安装已完成，项目经理符合性和独立安装 QA 均通过。
- 未执行项及原因：没有业务 UI/API/数据库变更，不执行业务端到端测试；没有发布或技能全局晋升授权，不执行发布或 F002。未来自动加载与实际沟通效果未独立验证。
- 残余风险：保留官方大小写名称，并在项目需求/监督/变更中记录必要兼容例外。上游技能只规定对话输出，不产生持久报告模板，因此不新增空白报告模板。
- 下一步：下一轮观察实际加载，不把静态安装成功等同于自动触发验证。
