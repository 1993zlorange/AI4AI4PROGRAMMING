# Web Project Template Agent Guide

本文件是编码代理和新贡献者在本模板中的执行规则。**开始编程前必须先阅读并遵守 [PROGRAMMING_STANDARDS.md](PROGRAMMING_STANDARDS.md)**；本文件不能降低编程规范的要求。

## 根级治理协同

开始任何项目相关操作前，必须先回读上级 [AI4PROGRAMMING/AGENTS.md](../../AGENTS.md)，并调用全局 `pr-ps-00-project-supervisor`（主 Skill：`$pr-ps-00-project-supervision`）登记需求、范围、目标文件、权限、风险、验收和日志路径。根级文件负责项目经理、架构师能力、工程师、项目测试 Agent 的调用顺序、`projectname/achieve` 成效归档、人工 Gate 和项目管理记录；本文件只负责 `projectname/project` 的软件工程边界。

工程 Agent 只能实现已经由项目经理确认、由架构师能力形成或审核过的需求/设计契约，不得自行扩大产品范围、改变公共 API、数据库 schema、权限、部署方式或验收标准。任何架构冲突先回到 `$pr-ar-01-project-architect` 和项目经理；工程完成后由项目经理做需求/设计符合性检查，再由独立 `pr-qa-00-project-test` Agent 隔离验收。失败、阻塞和未执行项必须真实回传根级项目监理。

代码、测试、配置、迁移和工程技术文档留在本目录；正式需求、架构成果、测试/验收报告、用户手册、阶段报告和发布说明写入 `../achieve` 的责任目录。临时数据库、浏览器 profile、截图、trace 和测试输出使用 `output/<类型>/<run-id>/`，不得写入正式数据或项目根。任何新文件先完成放置清单；任何新脚本必须配套中文 API 说明，任何文档型 Skill 必须配套中文空白模板。

新增功能、公共接口、数据库迁移、配置能力和用户路径先在 [`config/feature-registry.yaml`](config/feature-registry.yaml) 登记 `feature_id`、`feature_code`、`feature_name`、责任人、实现路径、测试路径和状态，再开始编码；代码文件仍遵循语言命名规范，不为功能编号破坏导入规则。工程变更前后运行 `python scripts/f001_governance_validate.py --project-root ../.. --check` 并把结果写入项目管理质量记录。项目 Skill 晋升全局前还必须运行 `python scripts/f002_skill_promotion_audit.py --project-root ../.. --check`；两个工具只读，不能代替人工批准。

## 1. 项目状态

这是依据 `docs/notes/open-source-web-project-layout.zh-CN.md` 创建的空白网页工程模板。当前没有产品需求、业务数据库表、可用 API、真实前端页面或生产部署。不要把占位文件描述为已实现功能，也不要在没有批准的需求和 ADR 时补造产品范围。

## 2. 开始任务前

1. 阅读 `PROGRAMMING_STANDARDS.md`，确认命名、依赖、测试、安全和 Definition of Done。
2. 阅读根 `README.md` 和任务相关的 `docs/`、ADR、契约和数据库说明。
3. 把用户请求拆成可验证的行为、接口、数据、错误、配置和运维影响。
4. 检查现有目录和文件，保持已有用户改动，不覆盖无关内容。
5. 如果需求会改变模块边界、数据模型、API 兼容性、权限或部署方式，先补充 ADR 或请求架构确认。

## 3. 文件应该放在哪里

| 任务内容                   | 目录                                       | 规则                                                       |
| -------------------------- | ------------------------------------------ | ---------------------------------------------------------- |
| 页面、路由、feature 交互   | `apps/web/src/`                            | 按 feature 组织；页面通过 API/SDK 调用后端                 |
| Web 静态资源               | `apps/web/public/`                         | 只放可公开发布的资源，不放秘密和运行时上传文件             |
| API 路由和 DTO             | `apps/api/src/api/`                        | 只做协议转换、校验、认证、授权、错误映射和用例调用         |
| 业务规则                   | `apps/api/src/domain/`                     | 不依赖 HTTP、ORM、环境变量和具体供应商                     |
| 用例编排                   | `apps/api/src/application/`                | 管理事务边界和业务流程，通过 ports 使用外部能力            |
| 数据库/队列/外部服务接口   | `apps/api/src/ports/`                      | 定义能力和稳定错误，不绑定具体实现                         |
| 数据库/缓存/外部 API 实现  | `apps/api/src/adapters/`                   | 所有 I/O 在这里，必须有集成测试和超时/重试策略             |
| 日志、指标、追踪、审计     | `apps/api/src/observability/`              | 结构化、脱敏、可关联 request/trace/version                 |
| 异步任务                   | `apps/worker/`                             | 只放独立任务生命周期；任务必须幂等、可重试、可取消和可恢复 |
| OpenAPI、JSON Schema、事件 | `packages/contracts/`                      | 契约是公共接口的单一事实来源                               |
| 共享 UI                    | `packages/ui/`                             | 只放跨应用稳定复用的组件和设计令牌                         |
| 共享工具配置               | `packages/config/`                         | 不放业务逻辑和秘密                                         |
| 客户端 SDK                 | `packages/sdk/`                            | 由契约生成或按契约维护，变更需有兼容性测试                 |
| 数据库结构和变更           | `database/schema/`、`database/migrations/` | 迁移只新增不改写，记录兼容和恢复方案                       |
| 本地/测试种子              | `database/seeds/`                          | 不得放真实数据、默认秘密或生产账号                         |
| 非敏感配置模板             | `config/`                                  | 真实值由环境或 Secret Manager 注入                         |
| 架构/API/开发/运维文档     | `docs/`                                    | 与代码、迁移、配置和发布变化同一 PR 更新                   |
| 跨应用测试                 | `tests/`                                   | 按 contract、integration、e2e、performance、security 分类  |
| 仓库级脚本                 | `scripts/`                                 | 可编排命令，不复制业务逻辑                                 |
| 发布和部署资产             | `release/`                                 | 只放声明式资产、清单、校验、签名、promote 和 rollback      |
| 运行时日志                 | `logs/`                                    | 只保留 `.gitignore` 和说明，禁止提交真实日志               |
| 上传/缓存/临时文件         | `storage/`                                 | 只保留 `.gitignore`，使用显式挂载点或对象存储              |

## 4. 推荐实施顺序

1. 先确认需求、边界、验收标准和是否需要 ADR。
2. 先写或更新 `packages/contracts/` 的接口/schema，再写应用用例和领域规则。
3. 为领域规则、契约和迁移添加测试。
4. 实现数据库、队列和外部服务 adapter，并验证失败、超时、重试和恢复。
5. 接入 API 路由和前端 feature；不要把业务逻辑塞进路由或组件。
6. 更新日志字段、配置模板、API/运维文档和 CHANGELOG。
7. 更新 release 清单和部署烟测，确认同一 artifact 可晋级和回滚。
8. 按 README 和项目工具链运行格式、类型、lint、测试、构建和安全检查。

## 5. 变更前后检查

开始前回答：

- 这项改动解决哪个需求，成功和失败如何被观察？
- 会不会改变公共 API、数据库 schema、配置、权限、日志或发布行为？
- 哪个目录拥有这项逻辑，依赖方向是否允许？
- 需要哪些单元、契约、集成、E2E、性能或安全测试？

完成前确认：

- 新文件放在责任边界内，没有创建平行的 `frontend/`、`backend/` 或业务副本；
- 没有提交秘密、真实日志、构建产物、机器绝对路径或临时调试代码；
- migration 可在空库和上一版本快照上验证；
- API/SDK/前端/文档/CHANGELOG 已同步；
- 测试不仅覆盖成功路径，还覆盖非法输入、权限、依赖失败、超时、取消和恢复；
- PR 中记录了命令、结果、风险和回滚方式。

## 6. 不确定或发现冲突时

- 不要通过新建模糊目录、复制代码或关闭检查来绕过边界问题。
- 行为、需求、优先级或验收标准不清楚时，先记录问题并请求确认。
- 架构、数据所有权、接口兼容性、安全边界或部署方案冲突时，先写 ADR/设计问题，不要静默重构。
- 发现已有用户改动时，与其兼容；除非用户明确要求，不能回滚或覆盖。

## 7. 代理交付格式

完成任务时应说明：变更目标、实际修改的文件、需求/ADR 关联、运行的检查命令及结果、未验证项、残余风险和后续决策。不得把“文件已创建”当成“功能已实现”，也不得声称未运行的测试已经通过。
