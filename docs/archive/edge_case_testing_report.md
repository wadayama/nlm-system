# NLM System Edge Case Testing Report

## Overview

This report summarizes detailed analysis results of edge case processing performance for various LLM models in the NLM system. Tests were conducted in August 2025 on MacBook Air environment.

## Execution Environment

- **Machine**: MacBook Air (August 2025)
- **OS**: macOS
- **NLM System**: Optimized with reasoning_effort='low' + verbosity='low'
- **Tested Models**:
  - gpt-5-mini (OpenAI Standard tier)
  - gpt-5-nano (OpenAI Economy tier) 
  - gpt-oss:20b (Local LMStudio)

## Test Methodology

### Test Categories

1. **Ambiguous Variable References**
   - Processing when variable names appear within text
   - Nested variable syntax handling

2. **Self-Reference Operations**
   - Counter increment processing
   - Variable swap operations

3. **Natural Language Complexity**
   - Homophone processing
   - Complex conditional branch processing

4. **Mathematical Operations**
   - Complex formula processing

5. **Extreme Cases**
   - Empty variable names
   - Unicode variables (🚀, Japanese)
   - Long variable names

### Evaluation Metrics

- **Success Rate**: Percentage of successful test items
- **Average Execution Time**: Mean execution time for successful tests
- **Quality Assessment**: Degree of match with expected results

## Test Results

### 1. GPT-5-MINI vs GPT-5-NANO Comparison

| Model | Success Rate | Avg Time | Quality Rating | Overall Rating |
|--------|--------------|----------|----------------|----------------|
| **gpt-5-mini** | **88.9%** | **5.3sec** | 🎯 Excellent | **🥇 Best** |
| **gpt-5-nano** | 100.0% | 7.1sec | 🎯 Excellent | 🥈 Excellent |

#### Detailed Analysis

**GPT-5-MINI Characteristics:**
- Practical success rate (88.9%) suitable for daily use
- 25% faster processing speed
- Good cost efficiency (Standard tier)
- Stability in edge cases

**GPT-5-NANO Characteristics:**
- Perfect success rate (100%)
- Superior in conditional branch processing
- Perfect Unicode support
- Slight speed tradeoff

### 2. ローカル vs OpenAI比較

#### gpt-oss:20b vs gpt-5-nano

| モデル | 成功率 | 平均時間 | コスト | プライバシー |
|--------|--------|----------|--------|------------|
| **gpt-oss:20b** | 87.5% | 9.7秒 | 🆓 無料 | 🔒 完全保護 |
| **gpt-5-nano** | **100.0%** | **7.1秒** | 💰 有料 | ⚠️ データ送信 |

**結論**: OpenAIが品質・速度で優位、ローカルはコスト・プライバシーで優位

#### gpt-oss:20b vs gpt-5-mini

| モデル | 成功率 | 平均時間 | 特記事項 |
|--------|--------|----------|----------|
| **gpt-oss:20b** | **100.0%** | 8.0秒 | 条件分岐処理で優位 |
| **gpt-5-mini** | 90.0% | **4.6秒** | 速度で優位 |

**驚きの結果**: ローカルLLMが品質でOpenAIを上回る場面を確認

## 推奨事項

### 用途別モデル選択

#### 🥇 GPT-5-MINI 推奨シナリオ
- **一般的な業務用途** (最適なバランス)
- **リアルタイム処理** (速度重視)
- **日常的なマクロ実行**
- **コスト効率重視**

#### 🥈 GPT-5-NANO 推奨シナリオ  
- **ミッションクリティカル** (100%品質必須)
- **複雑な条件分岐** (論理処理重視)
- **完璧性重視** (エラー許容度ゼロ)

#### 🏠 gpt-oss:20b 推奨シナリオ
- **コスト重視プロジェクト** (完全無料)
- **プライバシー重視** (データ外部送信なし)
- **複雑な論理処理** (一部でOpenAI超え)

### 最終推奨設定

```python
# 推奨構成 (最適バランス)
model = "gpt-5-mini"
reasoning_effort = "low"
verbosity = "low"
# 結果: 3.4秒、88.9%エッジケース成功率
```

## テストスクリプト情報

### 実行可能なテストスクリプト

以下のスクリプトは `tests/` ディレクトリに配置されており、Mac Studio環境でも同様のテストが実行可能です：

#### 1. モデル比較テスト

```bash
# GPT-5-MINI エッジケーステスト
uv run tests/test_gpt5_mini_edge_cases.py

# GPT-5-MINI vs GPT-5-NANO 最終性能比較
uv run tests/test_gpt5_mini_final.py

# ローカル vs OpenAI 比較テスト
uv run test_local_vs_nano_edge_cases.py
uv run test_local_vs_mini_edge_cases.py
```

#### 2. パフォーマンス最適化テスト

```bash
# reasoning_effort最適化テスト
uv run tests/performance/test_reasoning_effort.py
uv run tests/performance/test_reasoning_comparison.py

# verbosity最適化テスト  
uv run tests/performance/test_verbosity_parameter.py

# 最終最適化テスト
uv run tests/performance/test_final_optimization.py
```

#### 3. 品質検証テスト

```bash
# 品質検証 (reasoning_effort='low')
uv run tests/performance/test_low_quality.py

# 変数操作正確性テスト
uv run tests/performance/test_variable_correctness.py
```

### Mac Studio環境での実行手順

#### 前提条件
1. **Python環境**: Python 3.8+ と uv パッケージマネージャー
2. **ローカルLLM**: LMStudio または Ollama (gpt-oss:20b)
3. **OpenAI API**: API키 설정 (.openai_key ファイル)

#### セットアップ

```bash
# リポジトリクローン
git clone https://github.com/wadayama/nlm-system.git
cd nlm-system

# 依存関係インストール
uv sync

# OpenAI APIキー設定
uv run setup_openai.py

# ローカルLLMセットアップ (LMStudio)
# 1. LMStudio起動
# 2. gpt-oss:20b モデル読み込み  
# 3. サーバー開始 (localhost:1234)
```

#### 実行例

```bash
# 環境確認テスト
uv run tests/performance/test_all_models_improved.py

# フルエッジケーステスト実行
uv run test_local_vs_mini_edge_cases.py

# 結果の比較分析
uv run tests/test_gpt5_mini_final.py
```

## パフォーマンス最適化の詳細

### 実装された最適化

1. **reasoning_effort='low'**
   - 全モデル対応 (OpenAI + Local)
   - 品質を維持しつつ大幅高速化

2. **verbosity='low'**  
   - OpenAIモデル専用
   - 応答の簡潔化によるレイテンシー削減

3. **max_tokens削除**
   - 不要パラメータの除去
   - API互換性の向上

### 最適化効果

| モデル | 最適化前 | 最適化後 | 改善率 |
|--------|----------|----------|--------|
| **gpt-5-mini** | 11.3秒 | **3.4秒** | **70.0%向上** |
| **gpt-5-nano** | 11.3秒 | 4.1秒 | 63.8%向上 |
| **gpt-oss:20b** | ~11.0秒 | ~8.0秒 | 約27%向上 |

## 今後の計画

### Mac Studio環境での追加テスト

1. **ハイエンドハードウェア性能評価**
   - M2 Ultra/M3 Max での gpt-oss:20b 性能
   - メモリ32GB+ での大規模モデル評価

2. **追加モデルテスト**
   - より大きなローカルモデル (70B+)
   - 最新OpenAIモデルとの比較

3. **スケーラビリティテスト**
   - 同時セッション処理性能
   - 長時間実行安定性

### 実行予定テスト

```bash
# Mac Studio専用テスト (予定)
uv run tests/performance/test_mac_studio_performance.py
uv run tests/performance/test_large_model_comparison.py
uv run tests/performance/test_concurrent_sessions.py
```

## 参考資料

- [NLMシステム基本ドキュメント](../README.md)
- [OpenAI API設定ガイド](../GITHUB_SETUP.md)
- [エージェントアーキテクチャ計画](../AGENT_ARCHITECTURE_IMPLEMENTATION_PLAN.md)

---

*このレポートは2025年8月時点での結果です。将来のモデル更新やシステム変更により結果が変わる可能性があります。*