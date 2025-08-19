# Flow Control System - CUI (Command Line Interface) Guide

## 🖥️ **CUI機能の概要**

フロー制御システムには、以下のCUI機能が用意されています：

### 📊 **1. ネットワーク状態表示**
- **スループット表示**: 総量とバー表示
- **アラート一覧**: 過負荷・故障の詳細
- **パス詳細**: 各s-tパスの流量・容量・利用率
- **エッジ状態**: 全エッジの状態確認

### 🎛️ **2. 手動制御機能**
- **フロー設定**: パス別流量の直接設定
- **フロー調整**: 増減による微調整
- **最適化実行**: グリーディ最適化
- **負荷分散**: パス間の自動バランシング

### ⏰ **3. 時間進行・監視**
- **ステップ実行**: 指定ステップ数の進行
- **ライブ監視**: リアルタイム状態表示
- **コンパクト表示**: 1行での状態確認

## 🚀 **起動コマンド**

### **対話的監視モード**
```bash
uv run python interactive_monitor.py
```
- フルインタラクティブ制御
- リアルタイム監視
- 手動フロー調整

### **デモンストレーション**
```bash
uv run python cui_demo.py
```
- CUI機能のデモ
- 5段階のシナリオ表示

### **クイック状態確認**
```bash
uv run python cui_demo.py --quick
```
- 瞬時の状態確認
- ランダムシナリオ

### **基本CUI表示**
```bash
uv run python network_display.py
```
- 基本表示機能のテスト

## 📋 **対話コマンド一覧**

### **表示コマンド**
| コマンド | 説明 |
|----------|------|
| `status`, `s` | フル状態表示 |
| `compact`, `c` | コンパクト表示 |
| `help`, `h` | ヘルプ表示 |

### **制御コマンド**
| コマンド | 例 | 説明 |
|----------|-----|------|
| `set <path> <flow>` | `set P1 8.0` | パス流量を直接設定 |
| `adjust <path> <delta>` | `adjust P2 +2.0` | パス流量を増減調整 |
| `clear` | `clear` | 全流量をゼロにリセット |
| `balance` | `balance` | 利用率均等化 |
| `optimize` | `optimize` | グリーディ最適化 |

### **時間制御コマンド**
| コマンド | 例 | 説明 |
|----------|-----|------|
| `step [n]` | `step 3` | n ステップ進行（省略時1） |
| `run <n>` | `run 10` | n ステップの自動実行 |
| `monitor <n>` | `monitor 20` | n ステップのライブ監視 |

## 📊 **表示内容の読み方**

### **パス利用率バー**
```
P1: [████████████🔴🔴🔴🔴🔴🔴░░░░░░░] 12.0/8.0
     ↑正常領域    ↑過負荷    ↑余裕
```

### **エッジ状態アイコン**
- 🟢 `OK`: 正常状態
- 🟡 `HIGH`: 高利用率（80%以上）
- 🔴 `OVER`: 過負荷状態
- ⚫ `FAILED`: 故障状態

### **コンパクト表示**
```
t=  5 | Throughput:  15.0 | Alerts: 2 | P1:150% P2:50%
↑時刻   ↑総スループット    ↑アラート数 ↑パス別利用率
```

## 💡 **使用シナリオ例**

### **1. 基本監視**
```bash
flow_control> status              # 現在状況確認
flow_control> monitor 10          # 10ステップ監視
```

### **2. 過負荷対応**
```bash
flow_control> status              # 過負荷検出
flow_control> adjust P1 -5.0      # P1負荷軽減
flow_control> adjust P2 +3.0      # P2に振替
flow_control> status              # 結果確認
```

### **3. 最適化実行**
```bash
flow_control> clear               # リセット
flow_control> optimize            # 最適化実行
flow_control> run 20              # 20ステップ自動実行
```

### **4. 実験シナリオ**
```bash
flow_control> set P1 10.0         # 実験設定
flow_control> set P2 5.0          
flow_control> step 5              # 5ステップ進行
flow_control> balance             # バランス調整
flow_control> run 15              # 結果確認
```

## 🔧 **トラブルシューティング**

### **よくあるエラー**

**❌ Unknown command**
→ `help`でコマンド一覧を確認

**❌ Path not found**  
→ パスID（P1, P2）を正確に入力

**❌ Invalid flow value**
→ 数値形式を確認（例：8.0, +2.5, -1.0）

### **制御のヒント**

- **過負荷状態**: 高利用率パスから低利用率パスへ移行
- **最適化**: `optimize`で自動的に最大スループットを実現
- **監視**: `compact`表示で効率的な状態追跡
- **実験**: `clear`→`set`→`run`のパターンで様々な設定をテスト

## 🎯 **Phase 2でのLLM統合**

現在のCUI機能は、**Phase 2のLLM制御**の基盤となります：

```python
# LLMが自然言語で状況理解
situation = cui_display.get_network_description()

# LLMが制御判断
decision = llm_controller.decide_action(situation)  

# CUIコマンドとして実行
execute_cui_command(decision)
```

CUIでの手動制御体験により、LLM制御の効果的なパターンを発見できます！