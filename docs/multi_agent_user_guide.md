# マルチエージェントシステム ユーザーガイド

## 📖 概要

NLMシステムのマルチエージェント機能は、複数のエージェントを協調して動作させることで、複雑なタスクを効率的に処理できます。各エージェントは独立したNLMセッション（名前空間）を持ち、グローバル変数を通じて通信・協調します。

## 🚀 クイックスタート

### 基本的な使用方法

```python
from multi_agent_system import MultiAgentSystem
from agent_examples import DataCollectorAgent, ResearchAgent

# システム作成
system = MultiAgentSystem("my_project")

# エージェント作成・追加
collector = DataCollectorAgent("collector1", "database_source")
researcher = ResearchAgent("researcher1", "AI trends")

system.add_agent(collector)
system.add_agent(researcher)

# 順次実行
results = system.run_sequential()
print(f"実行結果: {results['successful']}件成功, {results['failed']}件失敗")
```

## 🔧 エージェントタイプ

### 1. DataCollectorAgent（データ収集エージェント）
一回実行型。指定されたソースからデータを収集して完了します。

```python
from agent_examples import DataCollectorAgent

# データ収集エージェント作成
collector = DataCollectorAgent(
    agent_id="collector_1",
    data_source="顧客データベース"
)

# 単独実行
result = collector.run()
```

**用途**: 
- データベースからの情報取得
- APIからのデータ収集
- ファイル処理

### 2. MonitorAgent（監視エージェント）
継続実行型。定期的にシステムを監視し、異常を検出します。

```python
from agent_examples import MonitorAgent

# 監視エージェント作成（5秒間隔）
monitor = MonitorAgent(
    agent_id="monitor_1",
    check_interval=5.0
)

# バックグラウンドで実行
import threading
monitor_thread = threading.Thread(target=monitor.run)
monitor_thread.start()

# 停止する場合
monitor.session.save("stop_monitoring", "true")
```

**用途**:
- システム監視
- リソース使用量チェック
- ログ監視

### 3. ResearchAgent（研究エージェント）
段階実行型。複数のフェーズを経て研究タスクを実行します。

```python
from agent_examples import ResearchAgent

# 研究エージェント作成
researcher = ResearchAgent(
    agent_id="researcher_1",
    research_topic="機械学習の最新動向"
)

# 5段階で実行（文献調査→データ収集→分析→統合→報告）
result = researcher.run()

# 最終レポート取得
final_report = researcher.session.get("final_report")
```

**研究フェーズ**:
1. 文献調査 (literature_review)
2. データ収集 (data_collection)
3. 分析 (analysis)
4. 統合 (synthesis)
5. 報告 (reporting)

### 4. CoordinatorAgent（調整エージェント）
他のエージェントを調整・管理するエージェントです。

```python
from agent_examples import CoordinatorAgent

# 調整エージェント作成
coordinator = CoordinatorAgent(
    agent_id="coordinator_1",
    team_agents=["collector_1", "researcher_1", "monitor_1"]
)

# チーム調整開始
coordinator.run()
```

**機能**:
- チームメンバーの状態監視
- タスク割り当て
- アラート処理
- 進捗管理

## 🎯 実行モード

### 1. 順次実行 (Sequential)
エージェントを一つずつ順番に実行します。

```python
# 安全で予測可能な実行
results = system.run_sequential()
```

**特徴**:
- エラーが発生しても他のエージェントは実行される
- 実行順序が保証される
- デバッグが容易

### 2. 並列実行 (Parallel)
エージェントを同時に実行します。

```python
# 高速実行（最大3つ同時）
results = system.run_parallel(max_concurrent=3)
```

**特徴**:
- 実行時間を大幅短縮
- CPU使用率が高い
- エラーハンドリングが重要

### 3. 監視実行 (Monitored)
システム管理下でエージェントを実行します。

```python
# 5秒間隔でチェック、最大300秒実行
results = system.run_monitored(
    check_interval=5.0,
    max_runtime=300.0
)
```

**特徴**:
- タイムアウト制御
- リアルタイム監視
- 自動停止機能

## 🔄 エージェント間通信

### メッセージ送信

```python
# エージェント間でメッセージ送信
agent1.send_message("researcher_1", "データ収集完了")

# メッセージ確認
messages = researcher.check_messages()
for msg in messages:
    print(f"{msg['from']}から: {msg['message']}")
```

### グローバル変数での情報共有

```python
# グローバル情報設定
collector.session.save("@shared_data", "収集済みデータ")

# 他のエージェントから参照
shared_data = researcher.session.get("@shared_data")
```

### アラート機能

```python
# アラート送信
monitor.send_alert("CPU使用率90%超過")

# システム全体に通知される
alert = researcher.session.get("@system_alert")
```

## 📊 システム管理

### システム情報取得

```python
# システム状態確認
info = system.get_system_info()
print(f"システムID: {info['system_id']}")
print(f"エージェント数: {info['agent_count']}")
print(f"実行状態: {info['running']}")

# エージェント詳細
for agent_info in info['agents']:
    print(f"- {agent_info['agent_id']}: {agent_info['status']}")
```

### ブロードキャスト

```python
# 全エージェントにメッセージ送信
system.send_broadcast("システム定期メンテナンス開始")
```

### システム停止

```python
# 緊急停止
system.stop_system()

# または
system.system_session.save("@system_shutdown", "true")
```

## 🛠 カスタムエージェント作成

### 基本構造

```python
from agent_base import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, agent_id: str, custom_param: str = None):
        super().__init__(agent_id)
        self.custom_param = custom_param
        self.session.save("custom_param", custom_param)
    
    def run(self):
        """メインロジックを実装"""
        self.set_status("working")
        self.log_activity("カスタム処理開始")
        
        # 自然言語マクロ実行
        result = self.execute_macro(
            f"Custom task with parameter: {self.custom_param}. "
            "Save result to {{custom_result}}"
        )
        
        self.set_status("completed")
        return result
```

### 継続実行型エージェント

```python
class ContinuousAgent(BaseAgent):
    def run(self):
        self.running = True
        self.set_status("monitoring")
        
        while self.running:
            # 定期処理
            self.perform_task()
            
            # 停止条件チェック
            if self.should_stop():
                break
            
            time.sleep(self.interval)
        
        self.set_status("stopped")
    
    def should_stop(self):
        return self.session.get("stop_agent") == "true"
```

## 💡 ベストプラクティス

### 1. エージェント設計

- **単一責任**: 各エージェントは一つの明確な役割を持つ
- **状態管理**: セッション変数を活用した状態保存
- **エラーハンドリング**: 適切な例外処理とログ出力
- **停止制御**: 適切な停止メカニズムの実装

### 2. システム設計

- **名前空間**: 意味のあるエージェントIDを使用
- **通信設計**: グローバル変数とメッセージの適切な使い分け
- **監視**: 重要な処理には監視エージェントを配置
- **調整**: 複雑なワークフローには調整エージェントを使用

### 3. パフォーマンス

- **並列実行**: CPUバウンドなタスクは並列実行を検討
- **リソース管理**: メモリ使用量とスレッド数の監視
- **タイムアウト**: 長時間実行タスクには適切なタイムアウト設定

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### エージェントが停止しない
```python
# 強制停止
agent.running = False
agent.session.save("stop_monitoring", "true")
```

#### メッセージが届かない
```python
# メッセージ確認
all_globals = agent.session.list_global()
for key, value in all_globals.items():
    if "msg_" in key:
        print(f"{key}: {value}")
```

#### システムがハング
```python
# システム緊急停止
system.session.save("@system_shutdown", "true")

# 全エージェント停止
for agent in system.agents:
    agent.stop()
```

### デバッグ支援

```python
import logging

# デバッグログ有効化
logging.basicConfig(level=logging.DEBUG)

# エージェント状態確認
print(f"Agent status: {agent.get_status()}")
print(f"Runtime info: {agent.get_runtime_info()}")

# システム状態確認
print(f"System info: {system.get_system_info()}")
```

## 🔗 関連ドキュメント

- [NLM基本ガイド](../README.md)
- [詳細技術文書](detailed_documentation.md)
- [使用例](../examples/basic_usage.md)
- [エッジケーステスト報告](edge_case_testing_report.md)

## 📚 サンプルコード集

### 基本的なデータ処理パイプライン

```python
from multi_agent_system import MultiAgentSystem
from agent_examples import DataCollectorAgent, ResearchAgent

system = MultiAgentSystem("data_pipeline")

# データ収集
collector = DataCollectorAgent("data_source", "sales_database")
system.add_agent(collector)

# 分析
analyzer = ResearchAgent("analyzer", "sales trend analysis")
system.add_agent(analyzer)

# 順次実行
results = system.run_sequential()

# 結果確認
analysis_result = analyzer.session.get("final_report")
print(f"分析結果: {analysis_result}")
```

### 監視システム

```python
from multi_agent_system import MultiAgentSystem
from agent_examples import MonitorAgent, CoordinatorAgent

system = MultiAgentSystem("monitoring_system")

# 複数の監視エージェント
cpu_monitor = MonitorAgent("cpu_monitor", check_interval=10)
disk_monitor = MonitorAgent("disk_monitor", check_interval=30)
system.add_agent(cpu_monitor)
system.add_agent(disk_monitor)

# 調整エージェント
coordinator = CoordinatorAgent("system_coordinator", 
                             team_agents=["cpu_monitor", "disk_monitor"])
system.add_agent(coordinator)

# 監視実行
results = system.run_monitored(check_interval=5, max_runtime=3600)
```

---

このガイドを参考に、NLMマルチエージェントシステムを効果的に活用してください。追加の質問や要望があれば、お気軽にお尋ねください。