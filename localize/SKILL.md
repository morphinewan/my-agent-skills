---
name: localize
description: 自动化处理 iOS/mac 项目中 .xcstrings 文件的翻译工作，包括提取、翻译和回写。
---

# 国际化本地化技能 (Localization Skill)

本技能用于自动化处理 iOS/mac 项目中 .xcstrings 文件的翻译工作，确保所有目标语言的翻译完整性与质量。

**注意**: 此 Skill 为本项目 (kun-app) 特制，脚本封装在 Skill 目录内。

## 角色定义
你是一名精通多国语言的本地化专家和资深 iOS 开发者。你负责提取未翻译文本、进行高质量翻译并正确回写数据结构。

### 核心约束:
- **结构扁平化**: 写入 `.xcstrings` 的条目必须直接位于 `strings` 根对象下，严禁产生冗余嵌套。
- **元数据识别**: 必须正确处理导出的 JSON 结构，避免将 `generated_at` 等统计信息误写入翻译条目。
- **语言纯净度**: 严禁在翻译结果中出现中英文夹杂或其他语言混杂的情况（例如在中文句中使用英文单词 "or", "and" 等）。除非是专有名词、品牌名称或特定的技术术语，否则必须保证翻译的彻底性。
- **工具依赖**: 本 Skill 使用 `jq` 进行高效、安全的 JSON 合并操作，请确保系统已安装。

## 前置环境检查
在执行任务前，请先运行环境检查脚本以确保 Python 环境满足要求且 `jq` 已安装。
```bash
python3 .agent/skills/localize/scripts/check_env.py
```

## 目标语言列表
`de`, `en`, `es`, `fr`, `id`, `it`, `ja`, `ko`, `pt`, `th`, `vi`, `zh-Hans`, `zh-Hant`

## 执行步骤

### 步骤 1: 提取未翻译条目
运行 Skill 自带的提取脚本，识别并导出指定 `.xcstrings` 文件中缺失翻译的 Key。

**操作指令**:
1. 确定 `.xcstrings` 文件的绝对路径 (例如 `Apps/Kun-mac/Kun-mac/Localizable.xcstrings`)。
2. 运行提取命令:
   ```bash
   python3 .agent/skills/localize/scripts/export_translations.py <目标xcstrings文件绝对路径>
   ```

**预期产物**:
- 在项目根目录（或脚本执行目录）生成 `untranslated_strings.json`。
- **注意**: 请读取此 JSON 文件的内容以便进行下一步翻译。

### 步骤 2: 智能翻译与语言自检
读取 `untranslated_strings.json`，针对每个 Key 的所有目标语言进行翻译。

**执行规范**:
- **风格对齐**: 必须参考 `.xcstrings` 中已有的翻译风格，保持用词、语调一致。
- **彻底本地化**: 严禁机械直译。**严禁在翻译后的句子中保留未翻译的虚词、连词（如 "or", "and", "by"）**。
- **占位符安全**: 严格保留 `%@`, `%d`, `${variable}` 等占位符，不得修改其格式。
- **变体处理**: 若条目包含 variations（如复数形式 plural），须针对所有 option 进行完整翻译。
- **二次校对**: 在生成 `translated_strings.json` 之前，必须对所有条目进行双重检查，确保没有任何非预期的语言混杂。

**产出格式**:
你需要生成一个新的 JSON 文件（例如 `translated_strings.json`），结构应与 `untranslated_strings.json` 类似，但包含所有语言的翻译结果。

### 步骤 3: 回写至 .xcstrings
使用 `jq` 将翻译完成的 JSON 内容高效合并回原始的 `.xcstrings` 文件中。

**操作指令**:
运行 Skill 自带的合并脚本（基于 `jq`）。

```bash
.agent/skills/localize/scripts/merge_translations.sh <目标xcstrings文件绝对路径> <翻译好的JSON文件路径>
```

**验证**:
回写完成后，可以通过 `git diff` 检查 `.xcstrings` 文件的变更。**关键检查点**:
- 是否出现了名为 `"strings": {` 的新增 Key（这通常意味着发生了非法嵌套）？
- 翻译内容是否正确填充到了 `stringUnit` 结构中？
- 文件的 JSON 结构是否依然扁平且合法？
- **内容审查**: 抽查翻译内容，确保没有中英混杂的情况，特别是连词。

## 文件清理与版本控制
- **禁止提交**: 过程中产生的中间文件（如 `untranslated_strings.json`, `translated_strings.json` 等）及任何临时生成的 Python 脚本，**严禁**添加到 Git 仓库中。
- **清理要求**: 任务完成后，**必须**删除上述所有临时文件，保持工作区整洁。

## 质量核验 (Checklist)
在任务结束前，请确认：
- [ ] 是否翻译了所有目标语言？
- [ ] **是否彻底检查并消除了所有语言混杂（如中文里保留了英文 "or" 等）？**
- [ ] 翻译内容是否与原本的翻译风格一致？
- [ ] 占位符是否完好无损且位置正确？
- [ ] 回写后的 `.xcstrings` 文件是否依然是有效的 JSON 且能被 Xcode 识别？
- [ ] 中间临时文件是否已全部删除？

## 异常处理
- 若脚本报错，请优先检查 Python 路径和依赖。
- 若翻译中遇到语境模糊的 Key，请搜索源码确认语境。
