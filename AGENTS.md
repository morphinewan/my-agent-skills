# Agent Skills 资产库

本仓库包含了用于增强 Agent 能力的专用技能（Skills），旨在自动化特定的开发和发布流程。

## 已集成技能列表

| 技能名称 | 描述 | 核心功能 |
| :--- | :--- | :--- |
| [**asc-cli**](./asc-cli/SKILL.md) | App Store Connect 自动化工具 | 管理 TestFlight、App 元数据、证书、设备注册以及下载销售/财务报告。 |
| [**localize**](./localize/SKILL.md) | iOS/mac 国际化本地化专家 | 自动提取 `.xcstrings` 未翻译条目，利用 AI 进行高质量多语言翻译，并安全回写。 |

## 使用指南

1. **激活技能**: 在与 Agent 对话时，可以通过 `activate_skill` 工具调用对应的技能名称（如 `asc-cli`）。
2. **遵循规范**: 每个技能文件夹内均包含 `SKILL.md`，详细定义了操作流程、约束条件和环境要求。
3. **安全第一**: 涉及 API 密钥和敏感信息的技能（如 `asc-cli`）应确保环境变量配置正确。

## 目录结构

- `asc-cli/`: 包含 `asc` 工具的操作指南及命令参考。
- `localize/`: 包含本地化处理脚本（Python/Shell）及详细的翻译质量控制流程。
