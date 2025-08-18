# パケットゲーム将来拡張設計書

## 概要

現在の固定3スロットシステムから、可変スロット数と将来予測を導入した高度なパケットスケジューリングシステムへの拡張設計。LLMが時系列推論と戦略的計画を行う研究プラットフォームとして発展させる。

## 現在のシステム状況

### 現在の制約
- **固定3スロット/ターン**: 毎回同じリソース制約
- **単一ターン最適化**: 現在状態のみを考慮した判断
- **決定論的環境**: 予測可能なシステム動作

### 拡張の動機
- **現実性の向上**: 無線チャネルの変動を反映
- **戦略的思考**: 将来を考慮した意思決定
- **複雑性増加**: より高度なAI推論の評価

## 拡張設計詳細

### 1. 可変スロットシステム

#### 1.1 チャネル状況モデル
```python
class ChannelCondition:
    """無線チャネル状況をモデル化"""
    
    def __init__(self):
        self.quality = 0.5        # チャネル品質 (0.0-1.0)
        self.noise_level = 0.3    # ノイズレベル (0.0-1.0)
        self.congestion = 0.4     # 混雑度 (0.0-1.0)
        self.weather_factor = 1.0 # 天候影響 (0.5-1.5)
    
    def update_markov_chain(self):
        """マルコフ連鎖による状態遷移"""
        # 品質の時系列変化（トレンド + ランダム）
        trend = random.uniform(-0.1, 0.1)
        noise = random.uniform(-0.05, 0.05)
        self.quality = max(0.0, min(1.0, self.quality + trend + noise))
        
        # 混雑度の日内変動パターン
        time_factor = math.sin(turn * 0.1) * 0.2  # 周期的変動
        self.congestion = max(0.0, min(1.0, 0.5 + time_factor + noise))
    
    def get_available_slots(self) -> int:
        """チャネル状況に基づくスロット数決定"""
        base_slots = 3
        
        # 品質による増減（0-2スロットのボーナス）
        quality_bonus = int(self.quality * 2)
        
        # 混雑による減少（0-2スロットのペナルティ）
        congestion_penalty = int(self.congestion * 2)
        
        # ノイズによるランダム変動
        noise_variation = random.randint(-1, 1) if self.noise_level > 0.7 else 0
        
        total_slots = base_slots + quality_bonus - congestion_penalty + noise_variation
        return max(1, min(6, total_slots))  # 1-6スロットの範囲制限
```

#### 1.2 動的スロット配分
- **最小保証**: 1スロット（システム継続性）
- **最大制限**: 6スロット（計算複雑性管理）
- **確率分布**: 2-4スロットが70%、1,5,6スロットが30%

### 2. 将来予測システム

#### 2.1 予測情報の種類
```python
class FuturePrediction:
    """将来状況の予測情報"""
    
    def __init__(self, horizon: int = 3):
        self.horizon = horizon  # 予測範囲（ターン数）
        self.slot_predictions = []    # スロット数予測
        self.confidence_levels = []   # 予測信頼度
        self.trend_analysis = ""      # トレンド分析
    
    def generate_predictions(self, current_channel: ChannelCondition):
        """現在状況から将来予測を生成"""
        predictions = []
        
        for t in range(1, self.horizon + 1):
            # マルコフ連鎖による確率的予測
            prob_dist = self._calculate_slot_probabilities(current_channel, t)
            predictions.append({
                'turn': t,
                'slot_distribution': prob_dist,
                'most_likely': max(prob_dist, key=prob_dist.get),
                'confidence': self._calculate_confidence(t)
            })
        
        return predictions
    
    def _calculate_slot_probabilities(self, channel, turns_ahead):
        """指定ターン後のスロット数確率分布"""
        # 現在品質からの確率的遷移
        base_quality = channel.quality
        uncertainty = 0.1 * turns_ahead  # 時間とともに不確実性増加
        
        probabilities = {}
        for slots in range(1, 7):
            # 品質ベースの確率計算
            optimal_quality = (slots - 1) / 5.0  # スロット数に対応する理想品質
            distance = abs(base_quality - optimal_quality)
            prob = math.exp(-distance / uncertainty)
            probabilities[slots] = prob
        
        # 正規化
        total = sum(probabilities.values())
        return {k: v/total for k, v in probabilities.items()}
```

#### 2.2 LLMへの予測情報提示
```
=== 将来予測情報 ===

現在チャネル状況:
  品質: 0.75 (良好)
  混雑: 0.40 (中程度)
  利用可能スロット: 4

次ターン予測 (信頼度: 85%):
  2スロット: 15%
  3スロット: 40%
  4スロット: 35%
  5スロット: 10%

2ターン後予測 (信頼度: 65%):
  1スロット: 10%
  2スロット: 25%
  3スロット: 35%
  4スロット: 25%
  5スロット: 5%

チャネルトレンド: 品質低下傾向、混雑増加予想
```

### 3. 段階的実装プラン

#### フェーズ1: シンプル可変スロット (実装期間: 1-2日)
**目標**: 基本的な可変性の導入
```python
# 実装項目
1. ChannelCondition基底クラス
2. LLMDirectScheduler.get_current_slots()メソッド
3. 可変スロット対応のLLMプロンプト修正
4. 基本的なスロット変動テスト

# 期待される変化
- LLMが利用可能スロット数に適応
- リソース制約下での選択パターン変化
- 新しい表示フォーマット対応
```

#### フェーズ2: 予測システム統合 (実装期間: 2-3日)
**目標**: 将来情報を考慮した判断
```python
# 実装項目
1. FuturePredictionクラス完全実装
2. マルコフ連鎖ベース予測アルゴリズム
3. 予測情報のLLMプロンプト統合
4. 時系列データの管理システム

# 期待される変化
- 戦略的判断の出現（待機vs即座実行）
- 不確実性への対応パターン
- リスク管理行動の観察
```

#### フェーズ3: 高度な戦略分析 (実装期間: 3-4日)
**目標**: 複雑な時系列推論の評価
```python
# 実装項目
1. 多期間パフォーマンス評価システム
2. 予測精度と判断品質の相関分析
3. 複数シナリオ比較機能
4. 戦略パターン自動検出

# 期待される変化
- 長期最適化戦略の確立
- 予測情報活用度の定量化
- 適応学習パターンの発見
```

### 4. 技術実装詳細

#### 4.1 新しいクラス構造
```python
# 拡張後のメインクラス
class AdvancedLLMScheduler(LLMDirectScheduler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channel = ChannelCondition()
        self.predictor = FuturePrediction(horizon=3)
        self.strategy_history = []  # 戦略決定履歴
    
    def get_dynamic_context(self):
        """動的コンテキスト情報の生成"""
        current_slots = self.channel.get_available_slots()
        predictions = self.predictor.generate_predictions(self.channel)
        return {
            'current_slots': current_slots,
            'predictions': predictions,
            'trend': self.channel.get_trend_analysis()
        }
```

#### 4.2 拡張LLMプロンプト設計
```python
def create_strategic_prompt(self, context):
    return f"""
=== 戦略的パケット選択タスク ===

現在状況:
利用可能スロット: {context['current_slots']}
{self.format_state_for_llm()}

将来予測:
{self.format_predictions(context['predictions'])}

戦略的考慮事項:
1. 現在送信 vs 将来の良条件待ち
2. 確実性 vs 最適性のトレードオフ
3. デッドライン制約下でのリスク管理

あなたのタスク:
現在の{context['current_slots']}スロットで送信するパケットを選択してください。
将来予測を考慮し、短期・長期両方の観点から最適な判断を行ってください。

判断理由に以下を含めてください:
- なぜこの選択をしたか
- 将来予測をどう活用したか
- 代替案と比較した理由
"""
```

#### 4.3 新しい評価指標
```python
class AdvancedMetrics:
    """拡張評価指標"""
    
    def calculate_adaptation_score(self, decisions, slot_variations):
        """可変条件への適応度スコア"""
        # スロット変動に対する判断の柔軟性を評価
        pass
    
    def calculate_prediction_utilization(self, decisions, predictions):
        """予測情報活用度スコア"""
        # 将来予測を実際の判断にどの程度反映したか
        pass
    
    def calculate_risk_management_score(self, decisions, uncertainties):
        """リスク管理品質スコア"""
        # 不確実性下での判断の妥当性を評価
        pass
    
    def calculate_temporal_optimization(self, multi_turn_performance):
        """時系列最適化スコア"""
        # 複数ターンにわたる戦略的判断の効果を評価
        pass
```

### 5. 期待される効果

#### 5.1 LLM行動パターンの進化
**現在の行動**:
- 緊急性優先（deadline ≤ 3）
- オーバーフロー管理
- 単発価値最大化

**拡張後の予想行動**:
- **条件的延期**: 「次ターンの6スロット時まで高価値パケット保持」
- **リスクヘッジ**: 「不確実性が高いので安全確実な選択を実行」
- **タイミング最適化**: 「3ターン後の良条件を狙って現在は控えめに」
- **複合戦略**: 「確実分と投機分のポートフォリオ構築」

#### 5.2 研究価値
- **時系列推論能力**: LLMの将来予測活用パターン分析
- **不確実性処理**: 確率情報に基づく判断品質評価
- **適応学習**: 動的環境での戦略修正プロセス観察
- **説明可能性**: 複雑な判断の解釈可能性維持

#### 5.3 技術的挑戦
**複雑性管理**:
- LLM理解可能な情報量制限
- 計算コスト vs 予測精度のバランス
- リアルタイム処理要件

**評価システム**:
- 単一指標から多次元評価への移行
- 長期戦略の短期評価方法
- 予測精度と判断品質の分離

## 実装開始手順

### 即座開始可能項目
1. **ChannelCondition基底実装**: 30分
2. **基本可変スロット機能**: 1時間
3. **LLMプロンプト適応**: 30分
4. **簡単な動作テスト**: 30分

### 段階的発展項目
1. **予測アルゴリズム実装**: 2-3時間
2. **戦略分析システム**: 4-5時間
3. **包括的評価フレームワーク**: 6-8時間

## まとめ

この拡張により、パケットゲームシステムは単純なスケジューリングから高度な戦略的AI判断プラットフォームへと発展します。LLMの時系列推論、リスク管理、適応学習能力を総合的に評価できる貴重な研究環境となることが期待されます。

段階的実装により、各フェーズで新しい洞察を得ながら、最終的に非常に興味深いAI行動パターンの観察が可能になるでしょう。

---
*作成日時: 2025年8月17日*  
*次回セッション開始時に即座実装可能*