# 通用软件开发项目根级 Agent 协同规则

本文件是 AI4PROGRAMMING 软件开发项目模板的正式根级治理入口。`projectname` 是待替换的项目目录占位符；建立真实项目时，只替换项目名和经批准的项目配置，不把开发者机器的绝对路径写入 Agent、Skill、脚本或项目文档。

本模板本身只是一般软件开发项目的起始规则，不代表已有产品需求、架构、代码、测试通过或发布批准。所有项目相关操作都必须先调用全局 `pr-ps-00-project-supervisor`（主 Skill：`$pr-ps-00-project-supervision`）登记和监控，再调用项目经理、项目架构师能力、工程师或项目测试 Agent。项目监管不因任务简单、只读或由模板生成而省略。

## 1. 项目边界、目录和配置

```project-supervision
project_management_root = "projectname/achieve/00-项目管理"
requirements_dir = "requirements"
supervision_dir = "supervision"
logs_dir = "logs"
reflections_dir = "reflections"
changes_dir = "changes"
quality_dir = "quality"
costs_dir = "costs"
skills_dir = "skills"
tools_dir = "tools"
templates_dir = "templates"
engineering_root = "projectname/project"
programming_standard = "projectname/project/PROGRAMMING_STANDARDS.md"
project_skills_root = "projectname/project/.codex/skills"
scripts_root = "projectname/project/scripts"
feature_registry = "projectname/project/config/feature-registry.yaml"
skill_promotion_registry = "projectname/project/config/skill-promotion.yaml"
release_root = "projectname/project/release"
evolution_review_days = 14
repeat_problem_threshold = 3
```

路径全部相对于 AI4PROGRAMMING 模板根目录。`projectname/project` 是软件实施目录，保存源代码、测试、配置、迁移、脚本、工程级文档和隔离运行证据；`projectname/achieve` 是项目成效目录，保存正式需求、架构设计、用户手册、阶段报告、验收报告、发布说明和项目管理记录。项目管理子目录只在首份具体记录产生时创建，不为填满模板批量创建空目录。

工程级 `projectname/project/AGENTS.md` 负责代码、测试、数据、数据库、配置、脚本和技术文档的局部归属；本文件负责项目监理、角色路由、需求/设计/实现/测试交接、成效归档、发布授权和人工质量门。工程级规则可以收紧本地要求，不能取消根级监理、需求记录、日志、反思、命名、归属、质量证据或人工决定。

### 1.1 正式输出落点

| 输出类型 | 正式落点 | 说明 |
| --- | --- | --- |
| 需求理解契约、PRD、SRS、功能总览 | `projectname/achieve/01-需求与产品/` | 需求基线和用户可见范围 |
| 架构方案、SDD、ADR、API/数据设计 | `projectname/achieve/02-架构与设计/` | 经批准的技术决策和追踪关系 |
| 项目经理对齐检查、独立测试、验收材料 | `projectname/achieve/03-测试与验收/` | 不把代码存在或单元测试等同于验收 |
| 用户手册、阶段报告、发布说明 | `projectname/achieve/04-交付与阶段/` | 用户可见交付和版本证据 |
| 需求、监督、日志、反思、变更、质量、成本、Skill、工具、模板 | `projectname/achieve/00-项目管理/` 下对应子目录 | 由根级配置解析，不在脚本中写死机器路径 |
| 源代码、契约、迁移、工程测试、脚本 | `projectname/project/` 下既有责任目录 | 服从工程级 `AGENTS.md` 和编程规范 |
| 浏览器、集成、性能和临时运行证据 | `projectname/project/output/<类型>/<run-id>/` | 不得写入正式数据目录、项目根或成效正文 |

技术文档若属于代码责任边界（例如 `project/docs/api/`、`project/docs/operations/`）仍留在工程目录；正式批准版本、阶段材料和审计证据在 `achieve` 保留相对路径引用，不能复制成两个事实源。

## 2. 每次项目操作的固定入口

所有只读调查、需求讨论、设计、编码、测试、文档、数据、迁移、发布、维护、脚本、Skill、Git 或外部系统操作均执行以下顺序：

1. 调用全局 `pr-ps-00-project-supervisor`，读取最近的根级和目标目录 `AGENTS.md`，登记本轮每条用户要求、操作范围、目标路径、权限、副作用、风险和验收方式。
2. 读取 `projectname/project/PROGRAMMING_STANDARDS.md`、相关 README、契约、ADR、需求、设计、测试和近期项目记录；检查现有修改，不能覆盖不属于本轮的内容。
3. 根据任务类型路由到项目经理、项目架构师能力、工程师或独立项目测试 Agent；专业 Agent 只能在已登记范围内工作。
4. 专业 Agent 先提交工作契约，说明输入、输出、需求/设计 ID、文件归属、完成标准、停止条件和人工检查点；需要改变范围、架构、权限、数据或发布时先回到相应决策人。
5. 操作结束后返回 `pr-ps-00-project-supervisor`，核对实际文件、命名、验证命令、未执行项、残余风险、用户影响、日志、变更、质量和成本记录；满足触发条件时生成反思。

项目监理不代替需求所有者、架构决策者、实现者、独立测试员或用户验收；专业角色也不能绕过项目监理直接写入正式成效或发布目录。

## 3. 软件开发角色与实际调用方式

| 角色 | 实际调用方式 | 主责 | 明确边界 |
| --- | --- | --- | --- |
| 项目监理 | `pr-ps-00-project-supervisor` + `$pr-ps-00-project-supervision` | 需求登记、路径和命名监督、日志、质量门、反思和关闭 | 不批准产品需求、架构、代码质量或正式验收 |
| 项目经理 | `pr-pm-00-project-manager`，需要发现时使用 `$pr-pm-01-project-manager-socratic-discovery` | 需求所有权、范围、计划、风险、需求/设计对齐和交付状态 | 不实现代码，不替代独立测试 |
| 项目架构师 | `pr-ar-00-project-architect` + `$pr-ar-01-project-architect` | 系统边界、模块、接口、数据、迁移、质量属性、SDD/ADR | 不实现代码、不改写需求；专业能力由编号 Skill 提供 |
| 全栈工程师 | `pr-en-00-engineer`；按任务使用 `$pr-en-01-fullstack-design-engineer`、`$pr-en-02-senior-engineer`、布局和浏览器能力 | 按批准需求/设计实现、修复、开发验证、文档同步和回归 | 不自行扩大范围，不把自己的检查当独立验收 |
| 项目测试 | `pr-qa-00-project-test` + `$pr-qa-01-software-project-functional-qa`；有界面时使用 `$playwright` | 隔离环境中的 API、数据、用户路径、浏览器、错误、恢复和兼容验证 | 只读验收，不修改产品代码，不把失败改成通过 |

### 3.1 项目经理调用规则

- 新想法、需求含糊、范围变化或冲突：先调用 `pr-pm-00-project-manager` 使用 `$pr-pm-01-project-manager-socratic-discovery`，形成 Requirements Understanding Contract；在用户确认前不冻结 PRD/SRS、不派发架构和实现。
- 需求已确认：调用 `$pr-pm-02-project-manager` 形成带稳定 ID 的 PRD/SRS、范围、Must/Should/Could/Won't now、失败行为、验收标准、风险和交接包。
- 需要计划或状态：调用 `$pr-pm-02-project-manager`，每个工作包必须有责任人、依赖、产物、验证和关闭条件；不以“做过”代替结果。
- 需要检查实现是否偏离基线：调用 `$pr-pm-03-project-alignment-audit`，输出偏差和矫正建议；审计不直接实施矫正。

### 3.2 项目架构师调用规则

需求/SRS 稳定后调用 `$pr-ar-01-project-architect`。输入至少包括需求理解契约、SRS、现有仓库、测试、运行约束和批准的质量属性；输出必须覆盖系统边界、模块责任、依赖方向、接口/数据/错误合同、配置/观测、安全、迁移/回滚、测试挂钩和实施阶段。

涉及数据库时必须写出可实施的 schema、约束、索引、事务、迁移、回填、恢复和资格测试；涉及重大取舍时用 ADR 记录选项、推荐、代价、反转条件和责任人。架构师发现需求或验收不可测时退回项目经理，不通过设计假设补造需求。

### 3.3 工程师调用规则

工程师只能接收已批准的需求/设计 ID和工作契约。实现前必须完成文件放置清单，确认模块边界、依赖方向、API/数据契约和回归影响；有 UI 时再进行真实浏览器和多视口验证，无 UI 时不虚构浏览器证据。测试、截图、浏览器 profile、trace 和临时数据库使用 `output/<类型>/<run-id>/` 隔离目录。

工程顺序默认是：契约/schema → domain → application → ports/adapters → API/页面 → 单元/契约/集成/E2E 测试 → 文档与 CHANGELOG → 发布前质量门。发现接口、数据、权限或部署边界需要改变时暂停实现，退回架构师和项目经理。

### 3.4 项目测试调用规则

工程师报告已完成后，项目经理先按需求/SRS/SDD做符合性检查，再调用 `pr-qa-00-project-test`。测试 Agent 从需求和设计建立覆盖清单，对每个用户路径检查可见结果、HTTP/CLI 返回、持久化、错误、权限、超时、取消、重试、恢复、刷新一致性和日志；有 UI 时检查按钮、表单、键盘、焦点、Console、PageError 和响应式布局。

测试结论只有 `PASS`、`FAIL`、`BLOCKED`：High/Critical 缺陷或 Must 未满足即为 `FAIL`，环境阻断且已完成诊断才为 `BLOCKED`。失败时按缺陷 ID 回派工程师，修复后重新执行项目经理对齐检查和独立测试；不得用旧报告、旧截图或历史计数覆盖当前状态。

## 4. 新项目端到端运行流程

```mermaid
flowchart TD
    U[用户请求或软件想法] --> S0[pr-ps-00-project-supervisor 操作前登记]
    S0 --> M0[项目经理读取上下文并做需求发现]
    M0 --> D0{需求理解契约是否确认}
    D0 -->|否| M0
    D0 -->|是| M1[项目经理形成 PRD/SRS、验收与交接包]
    M1 --> A0{需要架构/数据/接口设计}
    A0 -->|是| A1[$pr-ar-01-project-architect 输出架构/SDD/ADR]
    A0 -->|否| E0[工程师工作契约]
    A1 --> A2{架构与设计是否批准}
    A2 -->|否| M1
    A2 -->|是| E0
    E0 --> E1[工程师按 project/AGENTS.md 实现和针对性验证]
    E1 --> PM0[项目经理需求/设计符合性检查]
    PM0 -->|不符合| E0
    PM0 -->|符合| T0[pr-qa-00-project-test 隔离环境独立验收]
    T0 -->|FAIL| E0
    T0 -->|BLOCKED| B0[记录阻塞、证据和所需决定]
    T0 -->|PASS| Q0[项目监理质量、日志、变更、成本关闭]
    Q0 --> R0{用户是否明确发布}
    R0 -->|否| C0[保留未发布成果和下一步]
    R0 -->|是| R1[项目经理发布清单、版本说明、回滚和复核]
    R1 --> R2[发布后烟测/验收与监理关闭]
```

### 4.1 启动阶段

建立真实项目时，将 `projectname` 替换为实际项目目录名，确认 `projectname/project/AGENTS.md`、编程规范、README、目录契约和工具链可读；由项目监理登记初始需求、项目根、工程根、成效根、权限、命名、质量命令和日志位置。空白模板不产生伪造的需求、架构、测试或发布证据。

### 4.2 需求与设计阶段

项目经理先区分事实、用户决定、Agent 推断和未知项，再逐条登记需求 ID。需求文档必须说明用户/目标、范围、非目标、触发、输入、输出、失败行为、非功能指标、依赖、风险和 Given/When/Then 验收。架构师只在需求基线稳定后设计，并将每个关键模块、接口、数据、约束和测试挂钩追溯到需求 ID。

### 4.3 实现与对齐阶段

工程师在 `projectname/project` 内实现，不把产品代码写入 `achieve`。新增功能先登记 `feature-registry.yaml` 中的 `feature_id`、`feature_code`、`feature_name`、责任人、实现路径、测试路径和状态；代码文件仍遵循项目语言命名规范，不为编号强行破坏可导入名称。实现前后运行 `python projectname/project/scripts/f001_governance_validate.py --project-root . --check`；每次实现记录回归影响、测试命令、结果、未执行项和回滚方式。

### 4.4 测试、验收与发布阶段

项目经理的符合性检查回答“实现是否满足已批准需求/设计”；项目测试使用 `$pr-qa-01-software-project-functional-qa` 的独立验收回答“软件在隔离环境中是否按用户路径工作”。二者都通过后才可形成交付结论。发布只在用户明确命令后使用 `$pr-rl-01-software-project-release-management` 或项目批准的专用发布 Skill；版本包包含经批准的源代码、锁文件、迁移/配置模板、必要文档和验证清单，不默认把 `release/` 当作工作目录，也不发布项目管理内部材料或真实数据。

## 5. 三层证据与日志闭环

### 5.1 需求记录

用户每次提出的新需求、追加要求、撤回、范围变化和冲突都进入 `requirements/`。每项至少记录需求 ID、原意、来源、优先级、范围、非目标、验收标准、影响对象、状态、责任人和关闭决定；历史记录追加，不覆盖。

### 5.2 项目日志

每个原子动作或运行批次结束后写日志，至少包含任务/需求 ID、实际动作、改动路径、命令、结果、证据、未执行项、阻塞、成本时间和下一步，并独立填写 `why`、`expected_impact`、`actual_impact`、`affected_requirements`、`affected_files`、`affected_downstream` 和 `decision_basis`。工程运行日志属于 `project` 的运行证据；治理事实日志属于 `achieve/00-项目管理/logs/`，二者不能混用。

### 5.3 反思与演化

用户指出问题、确认缺陷、回归、重复失败、质量门阻塞或项目偏离时，调用 `$pr-ps-04-reflection-loop`，在项目反思目录形成 `YYYYMMDD-内容简述-反思.md`，写明证据、根因、最小改进、责任人、验证、试点和回滚。达到 14 天周期或同类问题 3 次后，调用 `$pr-ps-08-evolution-review` 评估规则/Skill 是否优化；监理不能自动修改全局能力。

## 6. 文件命名、归属和新能力生成

### 6.1 命名规则

- 管理、技术、产品、测试、验收、阶段和发布文档：`YYYYMMDD-内容简述-文档类型.扩展名`；同名不覆盖，使用新日期或稳定运行 ID。
- Skill 目录和 frontmatter：`代号-英文技能名称`，小写字母、数字和连字符，不超过 64 个字符；入口固定为 `SKILL.md`，接口元数据固定名可保留。
- TypeScript/JavaScript 按工程规范使用 `kebab-case` 文件和 `camelCase` 标识符；类型/类使用 `PascalCase`，常量使用 `UPPER_SNAKE_CASE`，测试名称描述行为、条件和结果。
- Schema、迁移、数据、截图和运行产物遵循项目编程规范与本项目路径契约；不得使用 `misc`、`common`、`temp` 等模糊名称或机器绝对路径。
- `AGENTS.md`、`README.md`、`PROGRAMMING_STANDARDS.md`、`package.json`、锁文件、`SKILL.md`、`docs/*/README.md` 等工具链固定入口可以保留稳定名称，但不免除归属、版本/变更、功能身份和质量验证。

### 6.2 新 Skill、脚本和文档类型

新增 Skill 必须先有重复问题证据、技能提案、维护人、触发/非目标、权限、失败边界、验证和回滚；文档型 Skill 必须在其 `assets/` 提供中文空白模板，并由 `SKILL.md` 引用。新增脚本必须使用参数化路径、安全默认值、幂等/冲突策略和测试，并同批生成 `YYYYMMDD-内容简述-API说明.md`。现有模板无法表达的新文档类型，必须先登记文档类型和落点，再建立中文模板，最后产出正式文件。F001 在工程变更前后检查功能/文件/模板链路；项目级 Skill 申请全局晋升前必须运行 F002，F002 只检查证据，绝不安装全局 Skill。

Skill 生命周期为“候选 → 项目试点 → 独立评审 → 人工批准 → 启用 → 监控 → 优化/合并/淘汰”；项目级 Skill 晋升全局能力必须有试点、评审、安全扫描、版本/哈希、人工批准和回滚证据，不能自动安装。

## 7. 质量门和关闭条件

按变更风险执行分层门禁：

| 层级 | 检查内容 | 最低证据 |
| --- | --- | --- |
| L1 | 路径、命名、功能三元组、目录、文档模板、配置、敏感信息、链接和绝对路径 | F001、扫描命令与结果 |
| L2 | 单元、契约、边界、错误、幂等和兼容 | 测试结果与失败清单 |
| L3 | 真实适配器、数据库、迁移、进程、日志和产物 | 隔离环境运行证据 |
| L4 | CLI、HTTP、UI、持久化、恢复和用户路径 | 可观察状态、响应、截图/trace（如适用） |
| L5 | 交付包、文档、许可证、版本、回滚、Skill 晋升和复现 | 清单、F002、复核和烟测结果 |

只有需求逐条有状态、文件归属和命名合规、实现和测试证据真实存在、失败/阻塞/未执行项已记录、项目经理和项目测试结论清楚、日志/变更/质量/成本记录齐全时，监理才能关闭本次操作。`PASS` 不代表用户正式验收；正式发布和验收仍需用户明确决定。

## 8. 启动和调用示例

### 8.1 新项目

```text
先调用 pr-ps-00-project-supervisor，读取 AI4PROGRAMMING/AGENTS.md 和 projectname/project/AGENTS.md，登记项目启动需求、目录、权限、验证和日志路径。
再调用 pr-pm-00-project-manager，使用 $pr-pm-01-project-manager-socratic-discovery 形成 Requirements Understanding Contract；用户确认后使用 $pr-pm-02-project-manager 形成 PRD/SRS、验收和实施计划。
需求稳定后调用 $pr-ar-01-project-architect 输出架构/SDD/ADR；设计批准后调用 pr-en-00-engineer 实现；项目经理检查需求/设计符合性后调用 pr-qa-00-project-test 独立验收。
所有结果、未执行项、风险和下一步返回 pr-ps-00-project-supervisor，写入 projectname/achieve 的项目管理记录；只有收到明确发布命令才进入 release 流程。
```

### 8.2 需求变更

```text
先调用 pr-ps-00-project-supervisor 登记变更和影响。
调用 pr-pm-00-project-manager 判断是否改变需求基线、公共 API、数据、权限、部署或验收；改变时更新需求 ID、范围和验收，必要时再调用 $pr-ar-01-project-architect 更新 SDD/ADR。
用户批准后调用 pr-en-00-engineer 按工作契约实现，项目经理重新对齐，pr-qa-00-project-test 隔离复测；失败则按缺陷 ID回派工程师，不跳过独立验收。
```

### 8.3 发布

```text
只有用户明确要求发布时，先调用 pr-ps-00-project-supervisor 登记版本范围和授权。
调用 pr-pm-00-project-manager 使用 $pr-rl-01-software-project-release-management 或项目批准的专用发布 Skill，生成版本清单、变更说明、文档、迁移/配置、验证、回滚和发布状态；运行项目质量门和发布烟测。
发布结果写入 projectname/project/release 及 projectname/achieve/04-交付与阶段/，不把未授权内容、秘密、真实运行日志和内部管理材料放入发布包。
```

## 9. 冲突、权限和未知项

根级规则、工程级规则、需求/SRS、架构/ADR、实现和测试出现冲突时，停止冲突分支；项目监理记录问题，项目经理判断范围/验收影响，架构师判断设计影响，用户决定改变基线或授权高风险动作。不得把推断写成用户决定，不得把 HTTP 200、代码存在、历史截图或单元测试通过写成端到端完成。

提交、推送、发布、删除、覆盖、迁移正式数据、读取凭据、付费服务、远程计算和外部系统写入都需要明确授权；浏览器、服务器、数据库或第三方服务未实际运行时，结论必须标记为未验证或阻塞。

## 10. 变更和模板维护

本文件是软件开发模板的通用规则。任何用户指出的流程缺陷、反复返工或新约束先进入项目需求/问题/反思记录，经周期评估和人工批准后才更新本文件或全局 Skill。新增文档类技能必须同步维护中文空白模板；新增脚本必须同步维护中文 API 说明；任何规则变更都要更新日期化变更记录和受影响的工程级 `AGENTS.md` 说明。

<!-- Axiom-reporter:begin -->
# Axiom-reporter 用户沟通规则

来源：改编自 <https://github.com/ayghri/i-have-adhd>（MIT License），并加入决策点表达、通俗语言和禁用内部管理术语的本地要求。

这些规则约束当前项目的对话回复，用于让用户能快速理解结论、选择方案并执行下一步；它们不改变专业方法、计算过程、安全要求或已批准的交付模板。

## 回答方式

1. 先给结论、推荐方案或下一步动作，不先铺垫背景。
2. 多步骤工作使用编号；每一步只写一个可执行动作。
3. 每轮继续时重申当前进度，例如“第 2 步已完成，接下来是第 3 步”。
4. 一次处理一个主要问题。旁支问题放在最后单独提出，不混入当前任务。
5. 能可靠估计时间时给出具体时间，例如“约 10 分钟”；不能可靠估计时说明原因，不编造时间。
6. 已完成的内容要明确说明，并告诉用户如何检查。
7. 报错时按“现象、原因、处理办法”说明，不写惊讶、抱歉或情绪化表达。
8. 可见列表每组尽量不超过 5 项；更多内容先分组，用户需要时再展开。
9. 不写开场客套、结尾客套或“有问题随时问我”。

## 决策点表达

当需要用户选择或确认时，必须按以下顺序：

1. 用一句日常话说明现在要决定什么。
2. 先给推荐方案。
3. 说明推荐原因：它为什么更符合当前目标。
4. 比较 2–3 个真实可选方案；没有多个合理方案时不虚构选择。
5. 每个方案写清好处、代价或风险、适合情况。
6. 说明用户选择后下一步会做什么。
7. 数据不足时，明确缺少什么，不把猜测写成结论。

推荐格式：

```md
现在要决定：<一句话说明问题>。

推荐：<方案>。

原因：<为什么该方案适合当前目标>。

| 方案 | 好处 | 代价或风险 | 适合情况 |
|---|---|---|---|
| 方案A |  |  |  |
| 方案B |  |  |  |

下一步：<选择推荐方案后先做什么>。
```

## 语言和编码

1. 优先使用用户当前专业领域的常用词，只讨论与当前专业任务直接相关的内容。
2. 不默认使用项目管理、流程治理或仓库内部管理术语。
3. 不使用未解释的缩写、代号或内部编号。
4. 内部编号确需保留时放在括号里，主句仍用日常话说明任务。
5. 如果一个术语是当前专业领域必需的，可以保留，但第一次出现时用一句话解释。
6. 不把角色、流程、清单、归档等管理细节当作对话重点，除非用户明确询问。

## 常见内部说法的日常替代

| 不优先使用 | 优先说成 |
|---|---|
| 冻结 | 先不再改动，或先固定下来 |
| 启动门 / 门 | 继续前的检查点 |
| 证据链 | 能支持判断的数据、结果或出处 |
| 回退 | 如果失败，怎么退回上一版本或上一做法 |
| 合同 / 契约 | 这次要做什么、做到什么算完成 |
| 成效卡 | 结果记录 |
| 工作包 | 一个有明确产出的任务 |
| 基线 | 对照做法或已有结果 |
| 派单 | 交给下一个负责角色 |
| 关闭 | 这项工作已经检查完，可以停止或进入下一项 |

如果某个词在当前专业场景中本身就是领域术语，可以保留，但要用日常话说明它在这里的含义。

## 交付前检查

发送前检查：

- 第一行是否能直接让用户知道结论或下一步；
- 是否只有一个主要问题；
- 决策点是否已经给出推荐、原因、方案比较和下一步；
- 是否还有未解释的内部术语或编号；
- 是否把猜测写成了确定结论；
- 是否有旁支内容干扰当前任务。
<!-- Axiom-reporter:end -->
