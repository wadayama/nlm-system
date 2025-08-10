# NLM Standard Prompt Writing Guide

## Overview

This guide defines standard writing conventions for natural language macro prompts in the NLM system. These conventions improve prompt readability, maintainability, and consistency.

## Basic Structure

### Template

```python
prompt = """
# [Main Task Name]

[Brief task description]

## [Section Name 1]
[Section content]

## [Section Name 2] 
[Section content]

## Output
[Output format specification]
""".strip()
```

### Required Elements

1. **Main Heading (`#`)** - Clearly indicate the task name
2. **セクション見出し (`##`)** - 論理的な区分け
3. **`.strip()`** - 先頭・末尾の余分な空白除去
4. **適切なインデント** - 視覚的階層構造

## 推奨セクション構成

### 基本セクション

- **Requirements** - タスク要件
- **Instructions** - 詳細な実行指示
- **Examples** - 具体例（必要に応じて）
- **Output** - 出力形式・保存先

### 応用セクション

- **Quality Guidelines** - 品質基準
- **Constraints** - 制約条件
- **Context** - 背景情報
- **Format** - フォーマット指定

## 実装例

### テーマ生成エージェント

```python
theme_prompt = """
# Theme Generation Task

Generate 4 diverse and evocative themes for haiku poetry.

## Theme Requirements
Create themes that are:
- Unusual and unexpected, avoiding clichéd topics
- Rich in sensory potential (visual, auditory, tactile imagery)
- 2-4 words that immediately evoke a specific scene or feeling

## Quality Guidelines
Each theme should spark vivid imagery and emotional resonance.

## Examples
Excellent themes: "morning frost patterns", "distant thunder"

## Output Instructions
Save the themes as global variables:
- Save the first theme to {{@theme_1}}
- Save the second theme to {{@theme_2}}
""".strip()
```

### 俳句生成エージェント

```python
haiku_prompt = f"""
# Haiku Generation Task

Create a beautiful haiku poem based on the theme in {{{{@theme_{self.theme_number}}}}}.

## Traditional Haiku Principles
- 5-7-5 syllable structure
- Focus on a single moment or image
- Include vivid, concrete imagery

## Instructions
Create an authentic haiku that captures the essence and mood of the theme.

## Output
Save the completed haiku to {{{{@haiku_{self.theme_number}}}}}
""".strip()
```

## スタイルガイドライン

### DO（推奨）

✅ **明確な見出し**: `# Task Name`, `## Section Name`  
✅ **論理的なセクション分け**: Requirements → Instructions → Output  
✅ **一貫したインデント**: 4スペースまたは適切な階層  
✅ **`.strip()`の使用**: 余分な空白の除去  
✅ **具体的な例示**: 理解を助ける実例を含める  

### DON'T（非推奨）

❌ **見出しなしの長文**: 構造化されていないプロンプト  
❌ **不適切なインデント**: 読みにくい階層構造  
❌ **曖昧な指示**: 抽象的で不明確な要求  
❌ **余分な空白**: `.strip()`なしの不整形文字列  

## 技術的考慮事項

### LLMへの影響

- **機能面**: Markdown見出しは実行に影響しない
- **理解面**: 構造化により指示理解が向上する可能性
- **互換性**: OpenAI API、Local LLM共に問題なし

### 変数展開

NLM変数展開は通常通り機能します：

```python
# プロンプト内での変数展開
{{variable_name}}           # ローカル変数
{{@global_variable}}        # グローバル変数
{{{{nested_expansion}}}}    # ネスト展開
```

### グローバル変数の標準書法

SystemSessionでのグローバル変数操作時は`@`プレフィックス付きを標準とします：

```python
# 推奨: @プレフィックス付きで統一
system_session.get_global("@theme_1")
system_session.set_global("@haiku_1", value)

# 動作するが非推奨: プレフィックスなし
system_session.get_global("theme_1")  # 一貫性なし
```

## 導入効果

### 開発者にとって

- **可読性向上**: プロンプト構造が一目で理解可能
- **保守性向上**: 修正・更新が容易
- **一貫性確保**: チーム開発での統一感

### システムにとって

- **実行影響なし**: 機能的動作は完全に保持
- **品質向上**: 構造化により指示精度が向上
- **デバッグ支援**: 問題箇所の特定が容易

## まとめ

この標準プロンプト書法により、NLMシステムのプロンプト品質が大幅に向上します。新しいエージェントや機能を実装する際は、必ずこの書法に従ってプロンプトを作成してください。

---

*最終更新: 2025-08-10*  
*適用開始: multi-haikuシステムより*