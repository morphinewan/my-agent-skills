# My Agent Skills

本仓库收集了专为增强 AI Agent 能力而设计的定制化技能（Skills）。这些技能旨在标准化和自动化开发工作流中的特定任务，通过 `activate_skill` 机制赋能 Agent 高效、准确地执行复杂操作。

## 📦 Skills 列表

| 技能名称 | 目录 | 描述 |
| :--- | :--- | :--- |
| **App Store Connect CLI** | [`asc-cli`](./asc-cli/SKILL.md) | 自动化 App Store Connect 任务。支持 TestFlight 管理（测试员/构建）、元数据配置、证书管理及销售/财务报告下载。 |
| **Localization Expert** | [`localize`](./localize/SKILL.md) | 自动化 iOS/macOS 项目 (`.xcstrings`) 的国际化流程。包含未翻译条目提取、多语言智能翻译及安全回写脚本，确保 JSON 结构完整性。 |

## 🚀 如何使用

1. **浏览技能**: 查看上述列表，点击链接进入对应技能目录阅读 `SKILL.md`。
2. **激活技能**: 在与 Agent 交互时，根据任务需求指示 Agent 激活特定技能（例如："请激活 `asc-cli` 技能帮我管理 TestFlight"）。
3. **遵循规范**: Agent 将加载对应的 `SKILL.md` 作为系统指令，严格按照定义的流程和约束执行操作。

## 📂 索引文档

更多详细信息，请参阅 [AGENTS.md](./AGENTS.md)。