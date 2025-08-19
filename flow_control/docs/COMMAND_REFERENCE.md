# Command Reference

Flow Control Network Systemのインタラクティブモニターで使用可能なコマンドの完全リファレンスです。

## 目次

- [表示コマンド](#表示コマンド)
- [制御コマンド](#制御コマンド) ⭐ 新機能追加
- [情報コマンド](#情報コマンド) ⭐ NEW
- [エッジ操作](#エッジ操作)
- [サンプル管理](#サンプル管理)
- [ファイル操作](#ファイル操作) ⭐ NEW
- [可視化コマンド](#可視化コマンド)
- [システムコマンド](#システムコマンド)
- [CLI機能](#CLI機能) ⭐ NEW

---

## 表示コマンド

ネットワークの状態を表示するコマンド群です。

### `status` / `s`

ネットワークの完全な状態を表示します。

**表示内容:**
- システム概要（ノード数、エッジ数、パス数）
- スループットサマリー
- パス詳細（フロー、容量、利用率）
- エッジ状態

**使用例:**
```
flow_control> status
```

**出力例:**
```
📊 System Overview
   Nodes: 4 | Edges: 4 | Paths: 2
   Total Throughput: 9.0

📊 s-t Path Details
Path ID  Route        Flow    Capacity  Utilization  Status
P1       e0→e2        5.0     8.0       62.5%        🟢 NORMAL
P2       e1→e3        4.0     6.0       66.7%        🟢 NORMAL
```

### `compact` / `c`

コンパクトな1行状態表示をします。

**使用例:**
```
flow_control> compact
```

**出力例:**
```
Throughput:   9.0 | P1:63% P2:67%
```

### `observe` / `o`

ネットワークの完全な観測可能状態を詳細表示します。

**表示内容:**
- システムメトリクス（効率、理論最大フロー）
- 全エッジの詳細状態
- 全パスの詳細状態
- ボトルネック情報

**使用例:**
```
flow_control> observe
```

---

## 制御コマンド

パスフローを制御するコマンド群です。

### `set <path> <flow>`

指定パスのフローを絶対値で設定します。

**引数:**
- `path`: パスID（P1, P2等）
- `flow`: 設定するフロー値（小数可）

**使用例:**
```
flow_control> set P1 6.0
✅ Updated path P1 flow by 1.00

flow_control> set P2 10.0
❌ Cannot update flow: Flow increase of 6.00 would exceed capacity by 4.00 at edge e3
```

### `adjust <path> <delta>`

パスのフローを相対値で調整します。

**引数:**
- `path`: パスID
- `delta`: 変化量（+で増加、-で減少）

**使用例:**
```
flow_control> adjust P1 +2.0
✅ Updated path P1 flow by 2.00

flow_control> adjust P2 -1.5
✅ Updated path P2 flow by -1.50
```

### `clear`

全てのフローをゼロにリセットします。

**使用例:**
```
flow_control> clear
✅ All flows cleared to zero
```

### `saturate <path>` ⭐ NEW

指定パスを自動的にボトルネック容量まで飽和させます。

**引数:**
- `path`: パスID（大文字小文字区別なし: P1, p1）

**機能:**
- パスのボトルネックエッジを自動検出
- 現在フローからボトルネック容量まで一気に設定
- 既に飽和済みの場合は適切にメッセージ表示

**使用例:**
```
flow_control> saturate P1
✅ Path P1 saturated: 0.0 → 7.0 (bottleneck: e2)

flow_control> saturate p2  # 小文字でも動作
✅ Path P2 saturated: 2.0 → 6.0 (bottleneck: e1)

flow_control> saturate P1  # 既に飽和済み
✅ Path P1 already saturated at 7.0 (bottleneck: e2)
```

### `distribute <total>`

指定した総フローを全パスに均等分配します。

**引数:**
- `total`: 分配する総フロー量

**使用例:**
```
flow_control> distribute 12.0
✅ Successfully distributed 12.00 flow equally among 2 paths
# 各パスに6.0ずつ分配される
```

### `maxflow <path>`

指定パスの最大安全フローと詳細情報を表示します。

**引数:**
- `path`: パスID

**使用例:**
```
flow_control> maxflow P1
```

**出力例:**
```
📊 Path Flow Analysis: P1
──────────────────────────────────────────────────
📈 Current State:
   Current flow: 5.0
   Available capacity: 3.0

🎯 Flow Limits:
   Maximum safe flow: 8.0
   Suggested flow: 8.0

🔗 Bottleneck Information:
   Bottleneck edge: e2
   Bottleneck capacity: 8.0
   Path edges: e0 → e2

📊 Utilization:
   Current: 62.5%
   [████████████░░░░░░░░] 5.0/8.0
```

---

## エッジ操作

エッジの有効/無効を制御するコマンド群です。

### `disable <edge>`

エッジを無効化します（容量を0に設定）。影響を受けるパスのフローは自動的にクリアされます。

**引数:**
- `edge`: エッジID（e1, e2等）

**使用例:**
```
flow_control> disable e1
✅ Edge e1 disabled (cleared flows: P2)
```

### `enable <edge>`

無効化されたエッジを有効化します（元の容量に復元）。

**引数:**
- `edge`: エッジID

**使用例:**
```
flow_control> enable e1
✅ Edge e1 enabled (capacity: 6.0)
```

### `edges`

全エッジの状態を一覧表示します。

**使用例:**
```
flow_control> edges
```

**出力例:**
```
🔗 EDGE STATUS
======================================================================
Edge   From   To     Capacity   Flow     Util%    Status
----------------------------------------------------------------------
e0     s      a      8.0        5.0      63%      🟢 OK
e1     s      b      0.0        0.0      0%       🔴 DISABLED
e2     a      t      7.0        5.0      71%      🟢 OK
e3     b      t      9.0        0.0      0%       🟢 OK

📊 Summary: 4 total edges, 1 disabled
```

---

## 情報コマンド ⭐ NEW

個別のパスやエッジの詳細情報を取得するコマンド群です。

### `info path <path_id>`

指定パスの包括的な情報を表示します。

**引数:**
- `path_id`: パスID（大文字小文字区別なし: P1, p1）

**表示内容:**
- 基本情報（ルート、エッジ構成、状態）
- フロー情報（現在フロー、最大容量、利用率）
- ボトルネック分析（制限エッジと容量）
- エッジ詳細（各エッジの利用状況）
- 関連性（他パスとの共有エッジ）

**使用例:**
```
flow_control> info path P1
📊 PATH INFORMATION: P1
============================================================
🛤️  Route: s → a → t
📏 Edges: e0 → e2 (2 total)
🟢 Status: NORMAL

💧 Flow Information:
   Current flow: 5.0
   Maximum capacity: 7.0
   Available capacity: 2.0
   Utilization: 71.4%

🔗 Bottleneck:
   Limiting edge: e2
   Bottleneck capacity: 7.0

🔗 Edge Details:
Edge   From   To     Capacity   Flow     Util%    Bottleneck
------------------------------------------------------------
e0     s      a      8.0        5.0      62%      
e2     a      t      7.0        5.0      71%      🔴 YES

🔗 No edge sharing with other paths
============================================================
```

### `info edge <edge_id>`

指定エッジの詳細情報を表示します。

**引数:**
- `edge_id`: エッジID（大文字小文字区別なし: e1, E1）

**表示内容:**
- 基本情報（接続ノード、容量、状態）
- 利用状況（現在フロー、利用率、残余容量）
- パス利用（このエッジを使用するパス一覧）
- 重要度（ボトルネックとなるパス、クリティカル判定）

**使用例:**
```
flow_control> info edge e2
🔗 EDGE INFORMATION: e2
============================================================
🔗 Connection: a → t
📊 Capacity: 7.0
🟢 Status: NORMAL
⚠️  Critical: Bottleneck for 1 path(s)

💧 Flow Information:
   Current flow: 5.0
   Available capacity: 2.0
   Utilization: 71.4%

🛤️  Used by 1 path(s):
Path   Flow     Position   Total Edges
----------------------------------------
P1     5.0      2/2        2

🔴 Bottleneck for paths: P1
============================================================
```

---

## ファイル操作 ⭐ NEW

外部YAML ファイルからカスタムネットワークを読み込むコマンド群です。

### `loadfile <path>`

YAML ファイルからネットワークを読み込みます。

**引数:**
- `path`: YAMLファイルのパス

**機能:**
- 完全なバリデーション（ノード、エッジ、接続性チェック）
- 自動パス列挙（全s-t パス検出）
- ネットワーク情報表示

**使用例:**
```
flow_control> loadfile examples/star_network.yaml
✅ Loaded: Star Network
   Description: Hub-and-spoke topology with central bottleneck
   File: examples/star_network.yaml
   Topology: 7 nodes, 9 edges, 4 paths

flow_control> loadfile custom/my_network.yaml
❌ File not found: custom/my_network.yaml

flow_control> loadfile invalid.yaml
❌ Invalid network definition: No paths found from source to sink - network is disconnected
```

### YAML ファイル形式

**基本構造:**
```yaml
name: カスタムネットワーク
description: ネットワークの説明

nodes:
  s: source      # 単一のソースノード（必須）
  a: intermediate # 中間ノード
  b: intermediate
  t: sink        # 単一のシンクノード（必須）

edges:
  e1: {from: s, to: a, capacity: 10.0}
  e2: {from: s, to: b, capacity: 8.0}
  e3: {from: a, to: t, capacity: 7.0}
  e4: {from: b, to: t, capacity: 9.0}
```

**ノードタイプ:**
- `source`: ソースノード（1つのみ）
- `intermediate`: 中間ノード（任意個数）
- `sink`: シンクノード（1つのみ）

**エッジ形式:**
- `from`/`to`: ノードID（nodes セクションに存在必須）
- `capacity`: エッジ容量（正の数値）

---

## サンプル管理

事前定義されたネットワークサンプルを管理するコマンド群です。

### `samples`

利用可能な全サンプルネットワークを一覧表示します。

**使用例:**
```
flow_control> samples
```

**出力例:**
```
🏛️  AVAILABLE NETWORK SAMPLES
======================================================================

🔸 DIAMOND: Simple Diamond
   Basic 2-path diamond topology (4 nodes)
   Size: 4 nodes, 4 edges, 2 paths
   Features: Simple topology, 2 parallel paths, Good for beginners

🔸 COMPLEX: Complex Multi-Path
   Multi-layer network with 4 overlapping paths (6 nodes)
   Size: 6 nodes, 8 edges, 4 paths
   Features: 4 paths, Shared edges, Flow interaction analysis

[他のサンプル...]

💡 Current sample: DIAMOND
💡 Use 'load <sample_name>' to switch networks
```

### `load <name>`

指定したサンプルネットワークを読み込みます。

**引数:**
- `name`: サンプルID（diamond, complex, grid, star, layered, linear, parallel, bottleneck）

**使用例:**
```
flow_control> load complex
✅ Loaded: Complex Multi-Path
   Topology: 6 nodes, 8 edges, 4 paths
   Features: 4 paths, Shared edges, Flow interaction analysis
💡 Use 'suggest' to apply recommended flows
```

### `info [name]`

サンプルの詳細情報を表示します。引数なしの場合、現在のサンプルの情報を表示。

**引数（オプション）:**
- `name`: サンプルID

**使用例:**
```
flow_control> info star
```

**出力例:**
```
📊 SAMPLE INFO: STAR
============================================================
Name: Star Network
Description: Hub-and-spoke topology (8 nodes, 5 paths)
Topology: 8 nodes, 10 edges, 5 paths
Features:
  • Hub bottleneck
  • Parallel spokes
  • CDN-like structure
Suggested flows:
  • P1: 2.0
  • P2: 3.0
  • P3: 2.5
  • P4: 1.5
  • P5: 2.8

💡 Use 'load star' to switch to this sample
```

### `suggest`

現在のサンプルに対して推奨フロー値を適用します。

**使用例:**
```
flow_control> suggest
✅ Suggested flows applied successfully
Throughput:   9.0 | P1:63% P2:67%
📈 Flow Analysis:
   Current throughput: 9.00
   Theoretical max: 14.00
   Utilization: 64.3%
```

---

## 可視化コマンド

ネットワークグラフを可視化するコマンド群です。

### `display` / `d`

ネットワークグラフを表示します（デフォルトでs-t最適化レイアウト）。

**使用例:**
```
flow_control> display
🎨 Displaying network graph...
✅ Graph visualization displayed
```

### `display <path1> [path2] ...`

指定したパスをハイライト表示します。

**引数:**
- `path1, path2, ...`: ハイライトするパスID

**使用例:**
```
flow_control> display P1 P2
🎨 Displaying network graph...
   Highlighting paths: ['P1', 'P2']
✅ Graph visualization displayed
```

### `display layout <type>`

グラフレイアウトを変更します。

**引数:**
- `type`: レイアウトタイプ
  - `planar_st`: s-t最適化平面配置（デフォルト）
  - `planar`: 平面グラフ配置
  - `spring`: バネモデル配置
  - `grid`: グリッド配置
  - `hierarchical`: 階層配置

**使用例:**
```
flow_control> display layout spring
🎨 Displaying network graph...
   Using layout: spring
✅ Graph visualization displayed
```

### `display save <filename>`

グラフを画像ファイルとして保存します。

**引数:**
- `filename`: 保存先ファイル名（.png推奨）

**使用例:**
```
flow_control> display save network_state.png
🎨 Displaying network graph...
   Saving to: network_state.png
✅ Graph visualization displayed
```

### 複合使用例

複数のオプションを組み合わせて使用できます：

```
flow_control> display P1 P3 layout planar_st save result.png
🎨 Displaying network graph...
   Highlighting paths: ['P1', 'P3']
   Using layout: planar_st
   Saving to: result.png
✅ Graph visualization displayed
```

---

## システムコマンド

システム制御用のコマンド群です。

### `help` / `h`

ヘルプ情報を表示します。

**使用例:**
```
flow_control> help
```

### `quit` / `q` / `exit`

インタラクティブモニターを終了します。

**使用例:**
```
flow_control> quit
🏁 Interactive monitor session ended.
```

---

## CLI機能 ⭐ NEW

インタラクティブモニターの使いやすさを向上するコマンドライン機能です。

### コマンドヒストリ

**機能:**
- 過去に実行したコマンドを記憶
- セッション間で永続化（`~/.flow_control_history`）
- 最大1000コマンド保存

**操作方法:**
- `↑` / `Ctrl+P`: 前のコマンド
- `↓` / `Ctrl+N`: 次のコマンド
- 空のプロンプトで`↑`押下で最後のコマンドを呼び出し

**使用例:**
```
flow_control> set P1 5.0
✅ Updated path P1 flow by 5.00

flow_control> [↑を押下]
flow_control> set P1 5.0  # 前のコマンドが表示される
```

### コマンドライン編集

**機能:**
- カーソル移動、文字削除、行編集が可能
- 長いコマンドの修正が簡単

**キーバインド:**
- `Ctrl+A`: 行頭に移動
- `Ctrl+E`: 行末に移動  
- `Ctrl+B` / `←`: カーソルを左に移動
- `Ctrl+F` / `→`: カーソルを右に移動
- `Ctrl+D`: カーソル位置の文字を削除
- `Ctrl+K`: カーソル以降を削除
- `Ctrl+U`: 行全体を削除

**使用例:**
```
flow_control> set P1 10.0
             ↑ここでCtrl+A押下してカーソルを行頭に移動
flow_control> set P1 10.0
         ↑ここに移動、数値部分だけ編集可能
```

### Tab補完

**機能:**
- コマンド名、パスID、エッジID、ファイルパスの自動補完
- 入力途中で`Tab`キーで候補を表示/選択

**補完対象:**

1. **コマンド名**
   ```
   flow_control> s[Tab]
   status  set  saturate  samples
   
   flow_control> sat[Tab]
   flow_control> saturate
   ```

2. **パスID** (set, adjust, saturate, maxflow, info path)
   ```
   flow_control> set P[Tab]
   P1  P2
   
   flow_control> info path p[Tab]  # 大文字小文字区別なし
   P1  P2
   ```

3. **エッジID** (disable, enable, info edge)
   ```
   flow_control> disable e[Tab]
   e0  e1  e2  e3
   
   flow_control> info edge E[Tab]  # 大文字小文字区別なし
   e0  e1  e2  e3
   ```

4. **サンプル名** (load, info)
   ```
   flow_control> load c[Tab]
   complex
   
   flow_control> load [Tab]
   diamond  complex  grid  star  layered  linear  parallel  bottleneck
   ```

5. **ファイルパス** (loadfile)
   ```
   flow_control> loadfile examples/[Tab]
   examples/simple_diamond.yaml    examples/star_network.yaml
   examples/complex_network.yaml   examples/bottleneck_network.yaml
   examples/grid_3x3.yaml
   ```

6. **infoコマンドのサブタイプ**
   ```
   flow_control> info [Tab]
   path  edge
   
   flow_control> info p[Tab]
   flow_control> info path
   ```

### 大文字小文字インセンシティブ

**機能:**
- パス名、エッジ名、ノード名で大文字小文字を区別しない
- コマンド名は従来通り大文字小文字を区別

**対応コマンド:**
- `set p1 5.0` ≡ `set P1 5.0`
- `info edge E2` ≡ `info edge e2`  
- `disable E1` ≡ `disable e1`
- `saturate p2` ≡ `saturate P2`

**使用例:**
```
flow_control> set p1 5.0      # 小文字入力
✅ Updated path P1 flow by 5.00  # P1として認識

flow_control> info edge E2    # 大文字入力  
🔗 EDGE INFORMATION: e2         # e2として認識

flow_control> saturate P1
flow_control> saturate p1     # どちらも同じ動作
```

---

## エラーメッセージと対処法

### よくあるエラー

#### 容量超過エラー
```
❌ Cannot update flow: Flow increase of 5.00 would exceed capacity by 2.00 at edge e3
```
**対処法:** `maxflow`コマンドで利用可能容量を確認し、適切な値を設定

#### パス/エッジが見つからない
```
❌ Path P5 not found
```
**対処法:** `status`コマンドで利用可能なパス/エッジIDを確認

#### エッジ既に無効化
```
❌ Edge e1 is already disabled
```
**対処法:** `edges`コマンドで現在の状態を確認

---

## 実践的なワークフロー

### 1. 基本的な実験フロー

```bash
# 1. ネットワークを選択
flow_control> load diamond

# 2. 推奨フローを適用
flow_control> suggest

# 3. 状態を確認
flow_control> status

# 4. 可視化
flow_control> display

# 5. エッジ故障をシミュレート
flow_control> disable e1

# 6. 影響を確認
flow_control> observe

# 7. 復旧
flow_control> enable e1
```

### 2. 最適化実験フロー

```bash
# 1. 複雑なネットワークを読み込み
flow_control> load complex

# 2. 各パスの最大容量を確認
flow_control> maxflow P1
flow_control> maxflow P2
flow_control> maxflow P3
flow_control> maxflow P4

# 3. 最適なフロー配分を設定
flow_control> set P1 6.0
flow_control> set P2 7.0
flow_control> set P3 5.0
flow_control> set P4 8.0

# 4. ネットワーク効率を確認
flow_control> observe
```

### 3. 視覚的分析フロー

```bash
# 1. グリッドネットワークを読み込み
flow_control> load grid

# 2. 初期状態を保存
flow_control> display save initial.png

# 3. フローを設定
flow_control> distribute 15.0

# 4. フロー経路をハイライト表示
flow_control> display P1 P2 P3 save with_flow.png

# 5. ボトルネックパスを特定
flow_control> maxflow P1
flow_control> display P1 save bottleneck.png
```

---

## Tips & Tricks

1. **Tab補完**: 多くのターミナルでTabキーによるコマンド補完が使用可能
2. **コマンド履歴**: 上下矢印キーで過去のコマンドを参照
3. **パイプライン処理**: 複数のコマンドを順次実行する場合は、各コマンドの成功を確認
4. **状態保存**: 重要な状態は`display save`で画像として記録を推奨