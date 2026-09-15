# AI4PROGRAMMING

面向通用软件项目的可治理开发模板。它提供项目监管、需求到发布的 Agent 协作规则、工程目录边界和可追溯的质量闭环，帮助团队从一个空白项目开始建立可审计的软件交付方式。

> **模板状态：** `v0.1.0` 已作为本地模板发行版准备；它不包含业务需求、产品代码、可运行服务或已配置 CI。不要把本仓库中的占位目录和治理示例当作已实现产品功能。

## 适用范围

适用于需要前端、API、数据迁移、共享契约、自动化测试、运维文档与受控发布的软件项目，尤其适合在 Codex Agent 协作下推进的网页或服务端项目。

不适用于跳过需求确认、架构决策、独立测试或用户发布授权的快速原型流程。具体技术栈、云服务、数据库、许可证和部署策略必须由派生项目自行确认。

## 核心约束

- **先监理，后执行：** 每一次项目相关操作先调用全局 `pr-ps-00-project-supervisor`，登记需求、范围、文件落点、权限、风险和验收方式。
- **需求可追溯：** 项目经理确认需求后才进入架构和工程；需求、设计、实现、测试和交付以稳定 ID 相互关联。
- **职责分离：** 工程师不自定范围，项目经理不替代独立测试，监理不代替用户批准。
- **证据分层：** 代码、单元测试、独立验收、正式验收与发布是不同证据状态，不能互相替代。
- **默认不发布：** 打包、部署、上传、重启服务或写入外部系统，均须用户明确授权。

完整约束以[根级 Agent 协同规则](AGENTS.md)为准。

## 快速开始

### 1. 创建派生项目

以模板为基础创建真实项目时，将 `projectname` 替换为经批准的项目名称；不要把本机绝对路径、真实秘密或未经确认的产品事实写入模板规则。

```text
AI4PROGRAMMING/
└── <实际项目名>/
    ├── project/    # 软件实施：代码、测试、配置、迁移、脚本和工程文档
    └── achieve/    # 正式成果：需求、设计、测试、交付和项目管理记录
```

首次操作前，确认以下文件可读：

1. [根级 Agent 协同规则](AGENTS.md)
2. [工程级 Agent 规则](projectname/project/AGENTS.md)
3. [编程规范](projectname/project/PROGRAMMING_STANDARDS.md)
4. [工程模板 README](projectname/project/README.md)

### 2. 发起第一项工作

```text
调用 pr-ps-00-project-supervisor 登记需求、范围、权限、目标路径和验证方式
  -> 调用 pr-pm-00-project-manager 形成需求理解契约
  -> 用户确认后形成 PRD/SRS 与验收标准
  -> 按需要调用 pr-ar-01-project-architect 形成 SDD/ADR
  -> 调用 pr-en-00-engineer 在 project/ 中实现并验证
  -> 项目经理检查需求/设计符合性
  -> 调用 pr-qa-00-project-test 独立验收
  -> pr-ps-00-project-supervisor 写入日志、质量、变更和关闭记录
```

只有用户明确要求发布，才可进入版本清单、发布资产、烟测和交付归档流程。完整流程和角色边界见[根级 Agent 协同规则](AGENTS.md#4-新项目端到端运行流程)。

## 项目结构

```text
AI4PROGRAMMING/
├── AGENTS.md                         # 模板级治理入口、角色路由和发布授权
├── README.md                          # 模板入口说明（本文件）
├── projectname/
│   ├── project/                       # 工程实施目录
│   │   ├── apps/                      # Web、API 和 Worker 应用
│   │   ├── packages/                  # 契约、SDK、共享 UI 和工具配置
│   │   ├── database/                  # Schema、迁移、种子与维护脚本
│   │   ├── config/                    # 非敏感配置和功能登记
│   │   ├── docs/                      # 工程级架构、API、开发和运维文档
│   │   ├── tests/                     # 契约、集成、E2E、性能和安全测试
│   │   ├── scripts/                   # 仓库级检查和生成脚本
│   │   └── release/                   # 受控发布资产、清单和回滚材料
│   └── achieve/                       # 正式项目成果与项目管理记录
│       ├── 00-项目管理/               # 需求、监督、日志、反思、质量和变更
│       ├── 01-需求与产品/             # PRD、SRS 和功能总览
│       ├── 02-架构与设计/             # SDD、ADR、API 与数据设计
│       ├── 03-测试与验收/             # 对齐检查、独立测试和验收材料
│       └── 04-交付与阶段/             # 用户手册、阶段报告和发布说明
└── reference/                          # 日期化历史参考和 Agent 使用说明
```

工程目录的更细粒度归属，例如前端页面、领域规则、适配器、数据库迁移和临时运行证据的位置，见[工程级 Agent 规则](projectname/project/AGENTS.md#3-文件应该放在哪里)。

## 开发与质量门

新功能、公共接口、迁移、配置能力与用户路径必须先登记到 `projectname/project/config/feature-registry.yaml`，其中包含功能编号、代码、名称、责任人、实现路径、测试路径和状态。

工程变更前后运行：

```bash
python projectname/project/scripts/f001_governance_validate.py --project-root . --check
```

该检查确认文件归属、功能三元组与模板/配置链路；它不替代类型检查、单元测试、集成测试、浏览器验证、独立验收或人工发布批准。项目级 Skill 申请晋升到全局前，还必须运行 F002 审计并取得人工批准。

派生项目应在工程 README 中提供可复制的真实安装、格式化、类型检查、测试、构建和本地运行命令。在这些命令与运行环境未建立前，本模板不会宣称其已通过。

## 文档与记录

| 内容 | 位置 | 规则 |
| --- | --- | --- |
| 项目治理记录 | `achieve/00-项目管理/` | 每次操作记录需求、监督、日志、质量、变更和成本；缺陷、阻塞或重复问题触发反思。 |
| 正式需求与设计 | `achieve/01-需求与产品/`、`achieve/02-架构与设计/` | 经项目经理/架构决策后归档，并与实现和测试 ID 追溯。 |
| 测试与交付材料 | `achieve/03-测试与验收/`、`achieve/04-交付与阶段/` | 独立测试报告、用户手册、阶段报告和发布说明。 |
| 工程技术文档 | `project/docs/` | API、运维、开发和与代码同生命周期的技术说明。 |

管理与技术文档使用 `YYYYMMDD-内容简述-文档类型.扩展名` 命名。`README.md`、`AGENTS.md`、`SKILL.md`、`package.json` 等工具链入口保留固定名称，但仍受归属、变更和质量规则约束。

## 贡献方式

1. 先阅读根级和工程级 `AGENTS.md`，确认本次变更的需求、边界和验收方式。
2. 通过项目监理登记操作；涉及需求、接口、数据、权限、部署或验收变化时，先由项目经理和架构师完成相应决策。
3. 在责任目录内实现，补充对应测试、文档和变更说明；不要提交秘密、真实日志、构建产物或机器绝对路径。
4. 如实记录命令、结果、未执行项、风险和回滚方式，接受项目经理符合性检查与独立测试。

任何新增文档型 Skill 都必须携带中文空白模板；新增脚本工具必须有中文 API 说明、参数化路径、安全默认值和验证证据。详细规则见[根级 Agent 协同规则](AGENTS.md#6-文件命名归属和新能力生成)。

## 文档索引

- [根级 Agent 协同规则](AGENTS.md)
- [工程级 Agent 规则](projectname/project/AGENTS.md)
- [编程规范](projectname/project/PROGRAMMING_STANDARDS.md)
- [工程模板 README](projectname/project/README.md)
- [架构文档入口](projectname/project/docs/architecture/README.md)
- [API 文档入口](projectname/project/docs/api/README.md)
- [开发文档入口](projectname/project/docs/development/README.md)
- [运维文档入口](projectname/project/docs/operations/README.md)
- [数据库文档入口](projectname/project/database/README.md)

## 许可证与发布

本模板采用 [MIT License](LICENSE)。派生项目仍须确认其自身的第三方依赖、数据和交付物许可边界；模板发行版不代表任何产品功能已经批准或验收。发布须遵循[发布调用规则](AGENTS.md#83-发布)并获得用户明确授权。
