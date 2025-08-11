# Multi-Agent System User Guide

## 📖 Overview

The NLM system's multi-agent functionality enables efficient processing of complex tasks through coordinated operation of multiple agents. Each agent has its own independent NLM session (namespace) and communicates/coordinates through global variables.

## 🚀 Quick Start

### Basic Usage

```python
from multi_agent_system import MultiAgentSystem
from agent_examples import DataCollectorAgent, ResearchAgent

# Create system
system = MultiAgentSystem("my_project")

# Create and add agents
collector = DataCollectorAgent("collector1", "database_source")
researcher = ResearchAgent("researcher1", "AI trends")

system.add_agent(collector)
system.add_agent(researcher)

# Sequential execution
results = system.run_sequential()
print(f"Results: {results['successful']} successful, {results['failed']} failed")
```

## 🔧 Agent Types

### 1. DataCollectorAgent (Data Collection Agent)
One-time execution type. Collects data from specified source and completes.

```python
from agent_examples import DataCollectorAgent

# Create data collection agent
collector = DataCollectorAgent(
    agent_id="collector_1",
    data_source="customer_database"
)

# Execute independently
result = collector.run()
```

**Use Cases**: 
- Information retrieval from databases
- Data collection from APIs
- File processing

### 2. MonitorAgent (Monitoring Agent)
Continuous execution type. Periodically monitors systems and detects anomalies.

```python
from agent_examples import MonitorAgent

# Create monitoring agent (5-second interval)
monitor = MonitorAgent(
    agent_id="monitor_1",
    check_interval=5.0
)

# Execute in background
import threading
monitor_thread = threading.Thread(target=monitor.run)
monitor_thread.start()

# To stop monitoring
monitor.session.save("stop_monitoring", "true")
```

**Use Cases**:
- System monitoring
- Resource usage checking
- Log monitoring

### 3. ResearchAgent (Research Agent)
Phased execution type. Executes research tasks through multiple phases.

```python
from agent_examples import ResearchAgent

# Create research agent
researcher = ResearchAgent(
    agent_id="researcher_1",
    research_topic="latest_trends_in_machine_learning"
)

# Execute in 5 phases (literature review → data collection → analysis → integration → report)
result = researcher.run()

# Get final report
final_report = researcher.session.get("final_report")
```

**Research Phases**:
1. Literature Review (literature_review)
2. Data Collection (data_collection)
3. Analysis (analysis)
4. Synthesis (synthesis)
5. Reporting (reporting)

### 4. CoordinatorAgent (Coordinator Agent)
An agent that coordinates and manages other agents.

```python
from agent_examples import CoordinatorAgent

# Create coordinator agent
coordinator = CoordinatorAgent(
    agent_id="coordinator_1",
    team_agents=["collector_1", "researcher_1", "monitor_1"]
)

# Start team coordination
coordinator.run()
```

**Functions**:
- Monitor team member status
- Task assignment
- Alert handling
- Progress management

## 🎯 Execution Modes

### 1. Sequential Execution
Executes agents one by one in order.

```python
# Safe and predictable execution
results = system.run_sequential()
```

**Features**:
- Other agents continue execution even if errors occur
- Execution order is guaranteed
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
# エージェント間でグローバル変数を使った通信（簡素化版）
agent1.session.save("@msg_for_researcher", "データ収集完了")
agent1.session.save("@msg_from", "agent1")

# メッセージ確認
msg = researcher.session.get("@msg_for_researcher")
sender = researcher.session.get("@msg_from")
if msg:
    print(f"{sender}から: {msg}")
```

### グローバル変数での情報共有

```python
# グローバル情報設定
collector.session.save("@shared_data", "収集済みデータ")

# 他のエージェントから参照
shared_data = researcher.session.get("@shared_data")
```

### SystemSessionでの統一的なグローバル変数管理

エージェント間での情報共有をより直感的に行うためにSystemSessionを使用できます：

```python
from system_session import SystemSession

# システム全体の共有状態管理
system_state = SystemSession()

# グローバル変数設定（@プレフィックス自動処理）
system_state.set_global("pipeline_status", "processing")
system_state.set_global("current_phase", "data_collection")
system_state.set_global("error_count", "0")

# 自然言語マクロとの一貫性
system_state.execute("Save 'high_priority' to {{@alert_level}}")

# エージェントから統一的にアクセス
class DataCollectorAgent(BaseAgent):
    def run(self):
        # SystemSessionで状態確認
        system = SystemSession()
        current_phase = system.get_global("current_phase")  # "data_collection"
        
        if current_phase == "data_collection":
            # データ収集実行
            self.execute_macro("Collect data and save to {{collected_data}}")
            
            # 次のフェーズに更新
            system.set_global("current_phase", "analysis")
            system.set_global("pipeline_status", "analysis_ready")

# 他のエージェントからも同じインターフェースで参照
class AnalysisAgent(BaseAgent):
    def run(self):
        system = SystemSession()
        
        # 統一的なインターフェースで状態確認
        status = system.get_global("pipeline_status")  # "analysis_ready"
        phase = system.get_global("current_phase")     # "analysis"
        
        if status == "analysis_ready":
            # 分析実行
            self.execute_macro("Perform analysis on collected data")
```

**SystemSession使用のメリット**：
- **一貫性**: 自然言語マクロの`{{@variable}}`とPythonの`system.get_global("variable")`が統一
- **認知負荷軽減**: @プレフィックスの自動処理により記述が簡潔
- **エラー削減**: インターフェース統一により変数アクセスミスを防止

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
# ブロードキャスト機能は削除されました
# 代わりにグローバル変数を使用
system.system_session.save("@broadcast_msg", "システム定期メンテナンス開始")
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
        self.logger.info("カスタム処理開始")  # log_activityは削除されました
        
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
            if self.session.get("@stop_signal") == "true":  # stop()メソッドは削除されました
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
    # stop()メソッドは削除されました - 手動で停止
    agent.running = False
    agent.set_status("stopped")
```

### デバッグ支援

```python
import logging

# デバッグログ有効化
logging.basicConfig(level=logging.DEBUG)

# エージェント状態確認
print(f"Agent status: {agent.get_status()}")
# get_runtime_info()は削除されました
print(f"Agent ID: {agent.agent_id}")
print(f"Status: {agent.get_status()}")

# システム状態確認
print(f"System info: {system.get_system_info()}")
```

## 🔗 関連ドキュメント

- [NLM基本ガイド](../README.md)
- [詳細技術文書](detailed_documentation.md)
- [使用例](../README.md#python-api-usage)
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