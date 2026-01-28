#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出 xcstrings 中未翻译的条目
用法: python export_translations.py
"""

import json
import os
import sys
from datetime import datetime

# 需要完整翻译的目标语言列表（不包含源语言）
DEFAULT_TARGET_LOCALES = {
    "de",
    "en",
    "es",
    "fr",
    "id",  # 印尼语
    "it",
    "ja",
    "ko",  # 韩语
    "pt",
    "th",  # 泰语
    "vi",  # 越南语
    "zh-Hans",
    "zh-Hant",
}


def determine_target_locales(strings, source_language):
    """结合默认配置和文件内容确定需要翻译的语言集合。"""
    locales = set(DEFAULT_TARGET_LOCALES)
    for value in strings.values():
        localizations = value.get('localizations') or {}
        locales.update(localizations.keys())
    locales.discard(source_language)
    return sorted(locales)


def string_unit_translated(string_unit):
    if not isinstance(string_unit, dict):
        return False

    state = string_unit.get('state')
    value = string_unit.get('value')
    return state == 'translated' and value not in (None, "")


def variations_translated(variations):
    if not isinstance(variations, dict) or not variations:
        return False

    for option in variations.values():
        if isinstance(option, dict):
            if 'stringUnit' in option:
                if not string_unit_translated(option.get('stringUnit')):
                    return False
            elif 'variations' in option:
                if not variations_translated(option.get('variations')):
                    return False
            else:
                if not variations_translated(option):
                    return False
        else:
            return False

    return True


def locale_translated(locale_entry):
    if not isinstance(locale_entry, dict):
        return False

    if 'stringUnit' in locale_entry:
        return string_unit_translated(locale_entry.get('stringUnit'))

    if 'variations' in locale_entry:
        return variations_translated(locale_entry.get('variations'))

    return False


def export_translations(file_path):
    """
    导出 xcstrings 中未翻译的条目

    Args:
        file_path: xcstrings 文件的路径

    Returns:
        tuple: (处理是否成功, 未翻译条目数量, 未翻译条目字典)
    """
    try:
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            print(f"错误: 文件 '{file_path}' 不存在")
            return False, 0, {}

        # 读取xcstrings文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"解析JSON文件时出错: {e}")
            print("文件可能不是有效的JSON格式")
            return False, 0, {}

        # 获取字符串条目
        strings = data.get('strings', {})
        if not strings:
            print("警告: 文件中没有找到'strings'部分")
            return False, 0, {}

        source_language = data.get('sourceLanguage', 'en')
        target_locales = determine_target_locales(strings, source_language)

        # 分离未翻译和已翻译的条目，排除shouldTranslate为false的条目，并记录陈旧条目
        untranslated = {}
        untranslated_reasons = {}
        translated_count = 0
        excluded = 0
        stale_keys = []
        exported_keys = []

        for key, value in strings.items():
            if value.get('extractionState') == 'stale':
                stale_keys.append(key)
                continue

            if value.get('shouldTranslate') is False:
                excluded += 1
                continue

            localizations = value.get('localizations') or {}

            missing_locales = [locale for locale in target_locales if locale not in localizations]

            incomplete_locales = []
            for locale in target_locales:
                if locale in missing_locales:
                    continue

                if not locale_translated(localizations.get(locale)):
                    incomplete_locales.append(locale)

            # zh-Hans 缺失时依旧认定为未翻译
            needs_translation = bool(missing_locales or incomplete_locales or 'zh-Hans' not in localizations)

            if needs_translation:
                untranslated[key] = value
                untranslated_reasons[key] = {
                    'missing': missing_locales,
                    'incomplete': incomplete_locales,
                }
                exported_keys.append(key)
            else:
                translated_count += 1

        # 删除陈旧条目和已导出的待翻译条目
        file_changed = False
        for removal_key in stale_keys + exported_keys:
            if removal_key in strings:
                del strings[removal_key]
                file_changed = True

        if file_changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, separators=(',', ' : '))

        # 打印统计信息
        print(
            "分析完成: 共有"
            f" {len(untranslated)} 个未翻译条目，"
            f"{translated_count} 个已翻译条目，"
            f"{excluded} 个排除条目(shouldTranslate=false)，"
            f"{len(stale_keys)} 个陈旧条目已移除"
        )
        print("=" * 80)

        # 打印需要翻译的条目
        if untranslated:
            print("需要翻译的条目:")
            print("-" * 40)
            for i, (key, value) in enumerate(sorted(untranslated.items()), 1):
                comment = value.get('comment', '')
                source_value = value.get('localizations', {}).get('en', {}).get('stringUnit', {}).get('value', '')
                print(f"{i:3d}. Key: {key}")
                if comment:
                    print(f"     Comment: {comment}")
                if source_value:
                    print(f"     English: {source_value}")
                reason = untranslated_reasons.get(key, {})
                missing = reason.get('missing')
                incomplete = reason.get('incomplete')
                if missing:
                    print(f"     缺少语言: {', '.join(missing)}")
                if incomplete:
                    print(f"     待更新语言: {', '.join(incomplete)}")
                print()
        else:
            print("所有需要翻译的条目已完成翻译！")

        print("=" * 80)
        return True, len(untranslated), untranslated

    except Exception as e:
        print(f"处理过程中出错: {e}")
        return False, 0, {}

def save_untranslated_to_json(untranslated_data, output_file):
    """
    将未翻译的条目保存到JSON文件中

    Args:
        untranslated_data: 未翻译条目的字典
        output_file: 输出文件路径

    Returns:
        bool: 保存是否成功
    """
    try:
        # 准备要保存的数据
        output_data = {
            "generated_at": datetime.now().isoformat(),
            "total_untranslated": len(untranslated_data),
            "strings": untranslated_data
        }

        # 保存到JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"已保存 {len(untranslated_data)} 个未翻译条目到: {output_file}")
        return True

    except Exception as e:
        print(f"保存JSON文件时出错: {e}")
        return False

def main():
    if len(sys.argv) == 1:
        # 获取项目根目录
        # 获取项目根目录 (.agent/skills/localize/scripts -> kun-app)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

        # 默认处理的xcstrings文件路径 - kun-mac
        xcstrings_files = [
            os.path.join(project_root, "Apps/Kun-mac/Kun-mac", "Localizable.xcstrings"),
        ]

        print(f"项目根目录: {project_root}")
        print("=" * 80)

        # 收集所有未翻译的条目
        all_untranslated = {}
        total_count = 0

        for file_path in xcstrings_files:
            if os.path.isfile(file_path):
                print(f"正在处理: {file_path}")
                success, count, untranslated = export_translations(file_path)

                if success and count > 0:
                    # 保持原有key值，添加到总字典中（自动去重）
                    for key, value in untranslated.items():
                        if key in all_untranslated:
                            print(f"警告: 重复的key '{key}'，已跳过")
                        else:
                            all_untranslated[key] = value
                    total_count += len(untranslated)
                    print()
                elif success:
                    print("该文件所有需要翻译的条目已完成翻译！\n")
            else:
                print(f"警告: 文件 '{file_path}' 不存在，跳过处理\n")

        # 如果有待翻译条目，保存到JSON文件
        if total_count > 0:
            output_file = os.path.join(project_root, "untranslated_strings.json")
            if save_untranslated_to_json(all_untranslated, output_file):
                print(f"\n总计: {total_count} 个未翻译条目已保存到 {output_file}")

                # 打印输出文件的内容到终端
                print("\n" + "=" * 80)
                print("输出文件内容:")
                print("=" * 80)
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(content)
                except Exception as e:
                    print(f"读取输出文件时出错: {e}")
                print("=" * 80)
            else:
                print(f"\n总计: {total_count} 个未翻译条目，但保存JSON文件失败")
        else:
            print("\n总计: 所有需要翻译的条目已完成翻译！")

    elif len(sys.argv) == 2:
        arg = sys.argv[1].lower()

        # 获取项目根目录
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

        if arg == "-core":
            # 处理 KunCore 的 xcstrings 文件
            file_path = os.path.join(project_root, "Packages/KunCore/Sources/KunCore/Resources", "Localizable.xcstrings")
            print(f"正在处理 KunCore 本地化文件: {file_path}")
            print("=" * 80)

            if os.path.isfile(file_path):
                success, count, untranslated = export_translations(file_path)

                if success and count > 0:
                    output_file = os.path.join(project_root, "untranslated_strings.json")
                    if save_untranslated_to_json(untranslated, output_file):
                        print("\n脚本执行成功！")

                        # 打印输出文件的内容到终端
                        print("\n" + "=" * 80)
                        print("输出文件内容:")
                        print("=" * 80)
                        try:
                            with open(output_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                print(content)
                        except Exception as e:
                            print(f"读取输出文件时出错: {e}")
                        print("=" * 80)
                    else:
                        print("\n脚本执行失败！")
                        sys.exit(1)
                elif success:
                    print("\n脚本执行成功！所有需要翻译的条目已完成翻译！")
                else:
                    print("\n脚本执行失败！")
                    sys.exit(1)
            else:
                print(f"错误: KunCore 的 Localizable.xcstrings 文件不存在: {file_path}")
                sys.exit(1)

        elif arg == "-ui":
            # 处理 KunUI 的 xcstrings 文件
            file_path = os.path.join(project_root, "Packages/KunUI/Sources/KunUI/Resources", "Localizable.xcstrings")
            print(f"正在处理 KunUI 本地化文件: {file_path}")
            print("=" * 80)

            if os.path.isfile(file_path):
                success, count, untranslated = export_translations(file_path)

                if success and count > 0:
                    output_file = os.path.join(project_root, "untranslated_strings.json")
                    if save_untranslated_to_json(untranslated, output_file):
                        print("\n脚本执行成功！")

                        # 打印输出文件的内容到终端
                        print("\n" + "=" * 80)
                        print("输出文件内容:")
                        print("=" * 80)
                        try:
                            with open(output_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                print(content)
                        except Exception as e:
                            print(f"读取输出文件时出错: {e}")
                        print("=" * 80)
                    else:
                        print("\n脚本执行失败！")
                        sys.exit(1)
                elif success:
                    print("\n脚本执行成功！所有需要翻译的条目已完成翻译！")
                else:
                    print("\n脚本执行失败！")
                    sys.exit(1)
            else:
                print(f"错误: KunUI 的 Localizable.xcstrings 文件不存在: {file_path}")
                sys.exit(1)

    
        elif arg == "--all" or arg == "-a":
            # 处理所有本地化文件
            paths = [
                os.path.join(project_root, "Apps/Kun-mac/Kun-mac", "Localizable.xcstrings"),
                os.path.join(project_root, "Packages/KunCore/Sources/KunCore/Resources", "Localizable.xcstrings"),
                os.path.join(project_root, "Packages/KunUI/Sources/KunUI/Resources", "Localizable.xcstrings")
            ]
            
            print("正在处理所有本地化文件...")
            print("=" * 80)
            
            all_untranslated = {}
            total_count = 0
            
            for file_path in paths:
                if os.path.isfile(file_path):
                    print(f"正在处理: {file_path}")
                    success, count, untranslated = export_translations(file_path)

                    if success and count > 0:
                        for key, value in untranslated.items():
                            all_untranslated[key] = value
                        total_count += count
                        print()
                    elif success:
                        print("该文件已完成！\n")
                else:
                    print(f"警告: 文件不存在: {file_path}\n")
            
            if total_count > 0:
                output_file = os.path.join(project_root, "untranslated_strings.json")
                if save_untranslated_to_json(all_untranslated, output_file):
                    print(f"总计 {total_count} 个未翻译条目已保存。")
            else:
                print("所有文件的本地化已完成！")

        elif arg == "--help" or arg == "-h":
            # 显示帮助信息
            print("用法:")
            print(f"  {sys.argv[0]}                    # 处理主程序的 Localizable.xcstrings（默认）")
            print(f"  {sys.argv[0]} -core              # 处理 KunCore 的 Localizable.xcstrings")
            print(f"  {sys.argv[0]} -ui                # 处理 KunUI 的 Localizable.xcstrings")
            print(f"  {sys.argv[0]} --all              # 处理所有的 Localizable.xcstrings")
            print(f"  {sys.argv[0]} <文件路径>          # 处理指定的 xcstrings 文件")
            print("\n选项:")
            print("  -core             处理 KunCore 的本地化文件")
            print("  -ui               处理 KunUI 的本地化文件")
            print("  -a, --all         处理所有本地化文件")
            print("  -h, --help        显示此帮助信息")
            sys.exit(0)

        else:
            # 单文件模式 - 处理指定的文件路径
            file_path = sys.argv[1]

            # 处理文件
            success, count, untranslated = export_translations(file_path)

            if success and count > 0:
                # 保存到JSON文件
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
                output_file = os.path.join(project_root, "untranslated_strings.json")

                if save_untranslated_to_json(untranslated, output_file):
                    print("脚本执行成功！")

                    # 打印输出文件的内容到终端
                    print("\n" + "=" * 80)
                    print("输出文件内容:")
                    print("=" * 80)
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            print(content)
                    except Exception as e:
                        print(f"读取输出文件时出错: {e}")
                    print("=" * 80)
                else:
                    print("脚本执行失败！")
                    sys.exit(1)
            elif success:
                print("脚本执行成功！所有需要翻译的条目已完成翻译！")
            else:
                print("脚本执行失败！")
                sys.exit(1)

    else:
        print(f"使用方法: {sys.argv[0]} [选项] [文件路径]")
        print(f"使用 {sys.argv[0]} --help 查看详细帮助信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
