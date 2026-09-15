# Web Project Template

<!--
Replace the project name, links, badges, screenshots, and commands before the
first public release. This repository is intentionally a blank scaffold.
-->

[![CI](https://img.shields.io/badge/CI-not_configured-lightgrey)](#开发)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> 一个面向开源网页工程的模块化 monorepo 空白模板。

**项目状态：** 规划中。本模板只提供目录、边界和开发规则，尚未实现业务功能、页面、API、数据库表或部署环境。

## 项目简介

这个模板适合需要同时维护前端、后端、数据库迁移、共享契约、文档、测试、日志配置和 release 资产的网页项目。默认采用模块化单体 monorepo：应用可以共享契约和工具，但通过依赖方向保持边界清晰。

### 主要能力边界

- `apps/web`：浏览器端应用。
- `apps/api`：HTTP/API 应用、用例编排和基础设施适配。
- `apps/worker`：可选的异步任务进程。
- `packages/`：前后端共享的契约、UI、工具配置和 SDK。
- `database/`：schema、migration、种子数据和数据库维护脚本。
- `config/`：不含秘密的环境、日志、功能开关和策略模板。
- `docs/`：架构、API、开发、运维和 ADR。
- `tests/`：跨应用的契约、集成、E2E、性能和安全测试。
- `release/`：发布清单、容器、编排、签名、校验和回滚脚本。

## 快速开始

### 前置条件

- Git
- Bun 或项目批准的 JavaScript/TypeScript 运行时
- 具体数据库、缓存、对象存储和部署平台在项目立项后补充

### 获取代码

```bash
git clone <REPOSITORY_URL>
cd web-project-template
```

### 安装与启动

当前模板没有运行时依赖和业务入口。实现第一条业务链路前，请先：

1. 在 `package.json`、各应用和共享包中声明实际依赖。
2. 复制 `.env.example` 为本地环境配置，并只填入本地秘密。
3. 在 `database/README.md` 中确定数据库和迁移命令。
4. 在 `docs/development/` 中补充可复制的启动步骤。
5. 更新本 README 的安装、启动和测试命令。

## 常用命令

模板阶段只保留命令入口，不宣称命令已经实现：

```bash
bun install
bun run check
bun test
```

应用实现后，命令必须至少覆盖格式检查、类型检查、单元测试、契约测试、集成测试和构建。命令的真实结果以 CI 为准，不能在 README 中提前声称通过。

## 项目结构

```text
.
├── apps/
│   ├── web/                       # 前端 Web 应用
│   │   ├── src/{app,features,components,data,state,styles}/
│   │   ├── public/
│   │   ├── tests/
│   │   └── e2e/
│   ├── api/                       # 后端 API 应用
│   │   ├── src/{api,application,domain,ports,adapters,config,observability}/
│   │   └── tests/
│   └── worker/                    # 可选异步任务进程
├── packages/
│   ├── contracts/                 # OpenAPI、JSON Schema、事件契约
│   ├── ui/                        # 跨应用共享 UI
│   ├── config/                    # lint、format、TypeScript 等工具配置
│   └── sdk/                       # 由契约生成或维护的客户端 SDK
├── database/{schema,migrations,seeds,scripts}/
├── config/{environments,logging,feature-flags,policies}/
├── docs/{architecture,api,operations,development,adr}/
├── tests/{contract,integration,e2e,performance,security,fixtures}/
├── scripts/                       # 仓库级开发、检查和生成脚本
├── release/{manifests,containers,compose,helm,terraform,migrations,scripts}/
├── logs/                          # 运行时目录，不提交真实日志
└── storage/                       # 上传和临时文件目录，不提交真实数据
```

依赖方向固定为：`web -> contracts/sdk -> api -> application -> domain`；基础设施通过 `ports -> adapters` 接入。前端不得直连数据库，`domain` 不得依赖 HTTP、ORM、环境变量或具体供应商 SDK。详见 [AGENTS.md](AGENTS.md) 和 [PROGRAMMING_STANDARDS.md](PROGRAMMING_STANDARDS.md)。

## 配置与秘密

- 可提交的默认值放在 `config/environments/*.example`。
- 真实秘密通过环境变量或 Secret Manager 注入。
- `.env`、生产连接串、token、私钥、用户导出数据和真实日志不得提交。
- 配置加载器必须在启动时校验类型和必填项，错误中只显示变量名，不显示秘密值。

## API 与数据库

公共 API 默认使用 `/api/v1` 前缀，并以 `packages/contracts` 中的 OpenAPI 或等价机器可读契约为单一事实来源。每个公共接口必须同时有实现、错误契约、契约测试和使用文档。

数据库结构只能通过 `database/migrations/` 演进。迁移进入共享环境后不得原地改写；需要兼容旧应用时使用 expand -> migrate/backfill -> switch -> contract 流程。当前模板没有任何产品表，不能把占位表当作已批准的数据模型。

## 开发

开始编码前必须先阅读：

1. [PROGRAMMING_STANDARDS.md](PROGRAMMING_STANDARDS.md)
2. [AGENTS.md](AGENTS.md)
3. [docs/architecture/](docs/architecture/)
4. 与任务相关的 API、数据库、运维和 ADR 文档

推荐开发顺序：契约/需求 -> 领域规则 -> 应用用例 -> 适配器 -> API/页面 -> 测试 -> 文档 -> release 资产。

### 测试要求

- 单元测试验证领域和应用规则，不测试实现细节。
- 契约测试验证前后端、SDK 和事件兼容性。
- 集成测试使用真实的数据库/队列适配器验证事务、迁移和错误映射。
- E2E 测试覆盖关键用户旅程、权限失败和恢复路径。
- CI 还应执行类型检查、依赖扫描、secret scan、构建烟测和迁移兼容性检查。

## 部署与发布

`release/` 只保存声明式发布资产和可审计脚本，不复制业务实现。目标流水线为：

```text
format/typecheck/test
  -> build immutable artifacts
  -> dependency/image/secret scan
  -> migration compatibility check
  -> staging smoke/e2e
  -> promote the same artifact
  -> publish checksum, SBOM and provenance
```

应用回滚、配置回滚、数据库恢复和对象数据恢复是不同流程，必须在 [docs/operations/](docs/operations/) 中分别说明并演练。

## 贡献

请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，确认需求、边界和验收标准，再创建分支。任何公共 API、数据库 schema、配置、日志、用户行为或部署行为变化，都必须在同一个变更中更新对应文档和测试。

## 安全

请阅读 [SECURITY.md](SECURITY.md)。不要在公开 issue、日志、截图、测试 fixture 或 commit 中提交秘密和未脱敏数据。

## 许可证

本模板采用 [MIT License](LICENSE)。派生项目发布前仍须确认其第三方依赖、数据集和交付物的许可边界。

## 路线图

- [ ] 确认产品范围、支持环境和技术栈
- [ ] 确认数据库、认证、对象存储和队列策略
- [ ] 定义第一条 API/前端用户旅程及其契约测试
- [ ] 配置 CI 的格式、类型、测试、安全和构建闸门
- [ ] 编写 staging、发布、回滚和恢复 runbook

## 文档索引

- [架构说明](docs/architecture/README.md)
- [API 说明](docs/api/README.md)
- [开发说明](docs/development/README.md)
- [运维说明](docs/operations/README.md)
- [数据库说明](database/README.md)
- [编程规范](PROGRAMMING_STANDARDS.md)
- [编码代理规则](AGENTS.md)
