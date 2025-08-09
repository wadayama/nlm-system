# NLM System Edge Case Testing Report

## 概要

このレポートは、NLMシステムにおける様々なLLMモデルのエッジケース処理性能を詳細に分析した結果をまとめています。テストは2025年8月に MacBook Air 環境で実施されました。

## 実行環境

- **マシン**: MacBook Air (2025年8月)
- **OS**: macOS
- **NLMシステム**: reasoning_effort='low' + verbosity='low' 最適化済み
- **テスト対象モデル**:
  - gpt-5-mini (OpenAI Standard tier)
  - gpt-5-nano (OpenAI Economy tier) 
  - gpt-oss:20b (Local LMStudio)

## テスト方法論

### テスト項目

1. **あいまいな変数参照**
   - 変数名が文中に出現する場合の処理
   - ネストした変数構文の処理

2. **自己参照操作**
   - カウンター増分処理
   - 変数スワップ操作

3. **自然言語の複雑さ**
   - 同音異義語の処理
   - 複雑な条件分岐処理

4. **数学的操作**
   - 複雑な計算式の処理

5. **極端なケース**
   - 空の変数名
   - Unicode変数 (🚀, 日本語)
   - 長い変数名

### 評価指標

- **成功率**: テスト項目に対する成功の割合
- **平均実行時間**: 成功したテストの平均実行時間
- **品質評価**: 期待される結果との一致度

## テスト結果

### 1. GPT-5-MINI vs GPT-5-NANO 比較

| モデル | 成功率 | 平均時間 | 品質評価 | 総合評価 |
|--------|--------|----------|----------|----------|
| **gpt-5-mini** | **88.9%** | **5.3秒** | 🎯 優秀 | **🥇 最優秀** |
| **gpt-5-nano** | 100.0% | 7.1秒 | 🎯 優秀 | 🥈 優秀 |

#### 詳細分析

**GPT-5-MINI の特徴:**
- 実用的な成功率 (88.9%) で日常使用に適している
- 25%高速な処理速度
- コスト効率が良好 (Standard tier)
- エッジケースでの安定性

**GPT-5-NANO の特徴:**
- 完璧な成功率 (100%) 
- 条件分岐処理に優位性
- Unicode対応が完璧
- 若干の速度トレードオフあり

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