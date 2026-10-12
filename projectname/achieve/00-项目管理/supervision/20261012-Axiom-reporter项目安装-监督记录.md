---
title: "Axiom-reporter项目安装监督记录"
document_id: "SUP-20261012-AXIOM-INSTALL"
produced_at: "2026-10-12"
status: "完成，带已登记限制"
owner: "项目监理"
governing_baseline: "AGENTS.md；projectname/project/AGENTS.md；projectname/project/PROGRAMMING_STANDARDS.md"
writing_level: "B"
---

# Axiom-reporter项目安装监督记录

## 1. 操作登记

| 项目 | 内容 |
|---|---|
| 关联需求/任务 ID | REQ-20261012-AXIOM-INSTALL；AXIOM-INSTALL-01/02/03 |
| 专业执行角色 | pr-en-00-engineer 安装；项目经理检查符合性；pr-qa-00-project-test 独立验证；项目监理登记与核验 |
| 目标与非目标 | 读取指定来源 AGENTS，按上游安装说明安装当前 cwd 根；不改业务实现，不建立真实业务项目，不发布、不提交、不推送、不全局安装 |
| 输入与目标产物 | 用户指定仓库与来源 AGENTS/README/安装器；根 AGENTS 标记块、原文件备份、.codex/skills/Axiom-reporter/SKILL.md |
| 权限与副作用 | 用户明确安装请求覆盖官方安装器必要的本地写入和备份；新沟通规则将影响后续项目内报告表达 |
| 验收和验证 | 代码检视、安全扫描、官方安装器预览/写入/重复执行、原规则保留与哈希核对、F001 前后检查、项目经理符合性与独立 QA |
| 停止条件 | 来源异常或试图访问凭据/外部写入；覆盖已有无关改动；安装范围超出登记；校验错误未处置 |

## 2. 文件放置与命名

| 产物 | 负责人 | 生命周期 | 最终路径 | 命名检查 | 引用影响 | 清理/归档 |
|---|---|---|---|---|---|---|
| 项目沟通标记块 | 工程师 | 项目使用期 | AGENTS.md | 工具链固定入口 | 后续 Agent 项目沟通 | 回滚只移除本次标记块或恢复备份 |
| 官方技能副本 | 工程师 | 上游版本绑定 | .codex/skills/Axiom-reporter/SKILL.md | 官方身份必要兼容例外，用户明确按来源说明安装 | Codex 项目技能加载 | 回滚移除本次新增副本，不触碰其他技能 |
| 安装器备份 | 工程师 | 回滚证据 | AGENTS.md.bak-20261012-222209 | 上游自动备份名；不自行改名 | 原规则恢复 | 保留直到用户不再需要回滚 |
| 隔离运行证据 | 工程师/测试员 | 运行记录 | projectname/project/output/skill-install/20261012-axiom-reporter/ | 既有 output 合同 | 不写入业务或正式数据目录 | 按运行证据保留策略管理 |
| 需求、监督、日志、变更、质量、成本 | 项目监理 | 项目审计记录 | projectname/achieve/00-项目管理/ 对应现存目录 | 20261012-Axiom-reporter项目安装-文档类型.md | 相对引用与事实追踪 | 不覆写历史记录 |

补充：本次导入既有上游 Skill，不创建或演化新 Skill，不把单次安装升级为全局能力。文档按 PS-00 中文空白模板生成。根配置的管理目录已有同类模板维护记录，本次复用该目录，不替换占位配置。上游规则明确只约束表达，不改变专业方法、安全或批准模板；工程级 AGENTS 的既有约束继续适用，无需复制表达规则。

## 3. 执行证据

| 动作 | 实际结果 | 命令/证据路径 | 状态 | 偏差 |
|---|---|---|---|---|
| 读取当前治理规则和模板 | 已读取根/工程 AGENTS、编程规范、PS-00 主技能和相关管理规范/中文模板 | 上述 governing_baseline；PS-00 references/assets | 完成 | 无 |
| 来源与执行边界检查 | 项目经理已读来源 AGENTS/README，官方安装根为当前 cwd | https://github.com/1993zlorange/Axiom-reporter，ab624f98da6cb9bf162a4dbf66e175976cd3acce | 完成 | 无 |
| 安装前检查 | 主执行者执行 F001，exit=0，ERROR=0 | 主线程实际工具输出；不伪造历史输出文件 | 完成 | 无 |
| 安装与幂等 | 官方写入、原文保留、备份字节一致、技能副本与源字节一致、标记各 1 组；重复运行两个 unchanged | projectname/project/output/skill-install/20261012-axiom-reporter/install-write.txt；install-idempotence.txt；integrity-check.json | 完成 | 无 |
| 项目经理符合性检查 | 用户三项要求已满足，范围限于登记对象 | 项目经理读取实际写入、幂等和完整性结果 | 完成 | 不等同正式用户验收 |
| 通用技能格式检查 | quick_validate exit=1，仅官方 Axiom-reporter 大小写不符合小写命名 | projectname/project/output/skill-install/20261012-axiom-reporter/quick-validate.txt | 完成，已知限制 | 保留用户指定官方副本身份，不静默改上游 |
| 独立 QA | 安装范围 PASS；来源/正文/备份/技能一致；独立 preview exit=0、两个 unchanged、前后目标哈希无变化 | projectname/project/output/skill-install/20261012-axiom-reporter/qa-integrity.json；qa-preview.txt；projectname/achieve/03-测试与验收/20261012-Axiom-reporter项目安装-功能测试报告.md | 完成 | 实际自动加载未验证 |
| 最终复核 | 6 份完成状态管理文档 strict 全部 errors=0 warnings=0；F001 exit=0，ERROR=0；正式 QA 报告已核对 | 监理最终实际工具输出；本批质量记录 | 完成 | 无 |

## 4. 结论与闭环

- 监理结论：带条件通过，安装范围已完成；项目经理符合性通过，独立 QA PASS。
- 未执行项：下一轮 Codex 实际自动加载与技能触发未验证；本次没有业务实现、发布和全局晋升范围。
- 问题与反思：通用格式检查失败和扫描提示作为已知兼容限制登记；不改上游身份。未发现安装缺陷，不据本次成功生成新规则或全局优化。
- 残余风险：上游正式身份不符合本项目自建 Skill 小写代号规范，按用户明确指定来源和安装说明保留兼容例外；不据此扩大其他命名例外。
- 人工决定：用户已明确授权安装；无新增发布、提交、推送或全局能力授权。
- 下一步：用户下一轮可验证实际加载；如发现加载失败，按该新证据处理官方名称兼容性。
