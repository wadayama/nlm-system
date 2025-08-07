# Agent継承アーキテクチャ実装計画書

**作成日**: 2025年8月7日  
**実装予定**: 2週間後  
**目標**: 美しく汎用性の高いAgent継承ベース設計の実装  

## 1. 設計思想と目標

### 1.1 なぜ継承ベース設計を選択したのか

**従来のアプローチとの比較:**
- **インスタンス注入方式**: `Agent(agent_id, run_method)` - 動的だが型安全性が低い
- **継承ベース方式**: `class CustomAgent(Agent)` - オブジェクト指向的で保守性が高い

**継承選択の決定的理由:**
1. **複数同タイプエージェント生成**: `[ResearchAgent(f"researcher_{i}") for i in range(5)]`
2. **型安全性**: 抽象メソッドによる実装強制
3. **コードの可読性**: 各エージェントタイプが独立したクラス
4. **拡張性**: 新しいエージェントタイプの追加が容易
5. **デバッグ容易性**: クラス階層による明確な責任分担

### 1.2 Simple/Complex統合の利点

**統一アーキテクチャの実現:**
```python
# Simple Agent
class SimpleTaskAgent(Agent):
    async def run(self):
        await self.execute_macro("Execute task and complete")
        self.session.save("agent_status", "completed")

# Complex Agent  
class MonitorAgent(Agent):
    async def run(self):
        self.running = True
        while self.running:
            await self.monitor_system()
            await asyncio.sleep(1.0)
```

**利点:**
- 同一インターフェースでSimple/Complex両対応
- 段階的な複雑化が可能（Simple→Complexへの自然な移行）
- システム全体の統一性維持

### 1.3 状態外部化の維持

**核心原則**: すべてのエージェント状態をNLMセッションで外部化
- **透明性**: 全エージェント状態がSQLiteで監視可能
- **耐障害性**: エージェント再起動時の状態復旧
- **協調性**: グローバル変数による非同期通信

## 2. 技術アーキテクチャ

### 2.1 Agent基底クラス詳細設計

```python
from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime
from nlm_interpreter import NLMSession

class Agent(ABC):
    """
    エージェント基底クラス
    
    設計原則:
    - 抽象runメソッドによる実装強制
    - NLMセッションによる状態外部化
    - 非同期実行対応
    - 共通機能の統一提供
    """
    
    def __init__(self, agent_id: str):
        """
        Args:
            agent_id: エージェント識別子（NLMセッションの名前空間になる）
        """
        self.agent_id = agent_id
        self.session = NLMSession(namespace=agent_id)
        self.running = False
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        
        # 初期状態設定
        self.session.save("agent_id", agent_id)
        self.session.save("creation_time", str(datetime.now()))
        self.session.save("agent_status", "initialized")
        
    @abstractmethod
    async def run(self):
        """
        エージェントのメイン実行ループ
        各サブクラスで必ず実装する
        
        Simple Agent: 一度実行して終了
        Complex Agent: 継続的な評価ループ
        """
        pass
    
    async def safe_run(self):
        """
        エラーハンドリング付きrun実行
        実際のシステムではこのメソッドを呼び出す
        """
        try:
            self.logger.info(f"Starting agent {self.agent_id}")
            self.session.save("agent_status", "starting")
            self.session.save("start_time", str(datetime.now()))
            
            await self.run()  # サブクラス実装を呼び出し
            
            self.session.save("agent_status", "completed")
            self.session.save("completion_time", str(datetime.now()))
            self.logger.info(f"Agent {self.agent_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Agent {self.agent_id} error: {e}")
            self.session.save("agent_status", "error")
            self.session.save("error_message", str(e))
            self.session.save("error_time", str(datetime.now()))
            raise
    
    def stop(self):
        """エージェントの優雅な停止"""
        self.logger.info(f"Stopping agent {self.agent_id}")
        self.running = False
        self.session.save("agent_status", "stopping")
    
    async def execute_macro(self, macro_content: str) -> str:
        """
        自然言語マクロ実行の統一インターフェース
        
        Args:
            macro_content: 実行するマクロ内容
            
        Returns:
            マクロ実行結果
        """
        self.logger.debug(f"Executing macro: {macro_content[:100]}...")
        result = await self.session.execute(macro_content)
        return result
    
    # === 共通ユーティリティメソッド ===
    
    async def wait_for_global(self, key: str, expected_value: str, timeout: int = 30) -> bool:
        """
        グローバル変数が期待値になるまで待機
        
        Args:
            key: グローバル変数名（@プレフィックス不要）
            expected_value: 期待値
            timeout: タイムアウト（秒）
            
        Returns:
            期待値になったかどうか
        """
        for _ in range(timeout):
            current_value = self.session.get(f"@{key}")
            if current_value == expected_value:
                self.logger.debug(f"Global variable @{key} reached expected value: {expected_value}")
                return True
            await asyncio.sleep(1.0)
        
        self.logger.warning(f"Timeout waiting for @{key} to become {expected_value}")
        return False
    
    def send_message(self, target_agent: str, message: str):
        """
        他エージェントへのメッセージ送信
        
        Args:
            target_agent: 送信先エージェントID
            message: メッセージ内容
        """
        msg_key = f"msg_{self.agent_id}_to_{target_agent}"
        self.session.save(f"@{msg_key}", message)
        self.session.save(f"@{msg_key}_timestamp", str(datetime.now()))
        self.logger.info(f"Sent message to {target_agent}: {message[:50]}...")
    
    def check_messages(self) -> list:
        """
        自分宛てのメッセージをチェック
        
        Returns:
            メッセージのリスト
        """
        messages = []
        all_globals = self.session.list_global()
        
        # 自分宛てのメッセージを検索
        target_pattern = f"_to_{self.agent_id}"
        for key, value in all_globals.items():
            if key.endswith(target_pattern) and key.startswith("msg_") and not key.endswith("_timestamp"):
                # タイムスタンプも取得
                timestamp_key = f"{key}_timestamp"
                timestamp = all_globals.get(timestamp_key, "unknown")
                
                messages.append({
                    "from": key.split("_")[1],  # msg_sender_to_receiver -> sender
                    "message": value,
                    "timestamp": timestamp
                })
        
        if messages:
            self.logger.info(f"Received {len(messages)} messages")
        
        return messages
    
    def get_agent_status(self, agent_id: str) -> str:
        """
        他エージェントの状態を取得
        
        Args:
            agent_id: 対象エージェントID
            
        Returns:
            エージェントの状態
        """
        status = self.session.variable_db.get_variable(f"{agent_id}:agent_status")
        return status if status else "unknown"
    
    def get_all_agent_statuses(self) -> dict:
        """
        全エージェントの状態を取得
        
        Returns:
            エージェントID -> 状態のdict
        """
        all_vars = self.session.variable_db.list_variables()
        statuses = {}
        
        for var_name, value in all_vars.items():
            if ":" in var_name and var_name.endswith(":agent_status"):
                agent_id = var_name.split(":")[0]
                statuses[agent_id] = value
        
        return statuses
```

### 2.2 抽象メソッドパターンの詳細

**Python ABCモジュールの活用:**
```python
from abc import ABC, abstractmethod

# 抽象メソッドの定義
@abstractmethod
async def run(self):
    pass

# 実装強制の確認
try:
    agent = Agent("test")  # TypeError: Can't instantiate abstract class Agent with abstract method run
except TypeError as e:
    print(f"Expected error: {e}")

# 正常なサブクラス
class ConcreteAgent(Agent):
    async def run(self):  # 必須実装
        await self.execute_macro("Do something")
```

### 2.3 非同期実行アーキテクチャ

```python
class MultiAgentSystem:
    """マルチエージェントシステム実行管理"""
    
    def __init__(self):
        self.agents = []
        self.system_session = NLMSession(namespace="system")
        
    def add_agent(self, agent: Agent):
        """エージェントをシステムに追加"""
        self.agents.append(agent)
        
    async def run_all_agents(self):
        """全エージェントの並行実行"""
        # システム開始時刻記録
        self.system_session.save("@system_status", "running")
        self.system_session.save("@system_start_time", str(datetime.now()))
        
        try:
            # 全エージェントを並行実行
            tasks = [agent.safe_run() for agent in self.agents]
            await asyncio.gather(*tasks)
            
            self.system_session.save("@system_status", "completed")
            
        except KeyboardInterrupt:
            # 優雅な停止
            logging.info("System shutdown requested")
            self.system_session.save("@system_status", "shutting_down")
            
            for agent in self.agents:
                agent.stop()
                
            # 停止完了待機
            await asyncio.sleep(2.0)
            self.system_session.save("@system_status", "stopped")
            
        except Exception as e:
            logging.error(f"System error: {e}")
            self.system_session.save("@system_status", "error")
            self.system_session.save("@system_error", str(e))
            raise
```

## 3. 段階的実装計画

### Phase 1: 基盤実装（実装開始時）

**期間**: 1-2日  
**目標**: 基本的なAgent基底クラスと実行システムの完成

**実装項目:**
1. **Agent基底クラス** (`agent_base.py`)
   ```python
   # 上記の完全版Agent基底クラスを実装
   ```

2. **基本サブクラス例** (`agent_examples.py`)
   ```python
   class SimpleTaskAgent(Agent):
       """Simple Agent - 1回実行型"""
       
       def __init__(self, agent_id: str, task_macro: str):
           super().__init__(agent_id)
           self.task_macro = task_macro
           
       async def run(self):
           result = await self.execute_macro(self.task_macro)
           self.session.save("task_result", result)
           return result

   class ComplexMonitorAgent(Agent):
       """Complex Agent - 継続実行型"""
       
       def __init__(self, agent_id: str, monitor_interval: float = 5.0):
           super().__init__(agent_id)
           self.monitor_interval = monitor_interval
           
       async def run(self):
           self.running = True
           while self.running:
               await self.monitor_step()
               
               # 終了条件チェック
               if self.session.get("@system_shutdown") == "true":
                   break
                   
               await asyncio.sleep(self.monitor_interval)
       
       async def monitor_step(self):
           """サブクラスでオーバーライド可能な監視ステップ"""
           await self.execute_macro("Monitor system status and save to {{monitor_result}}")
   ```

3. **マルチエージェント実行システム** (`multi_agent_system.py`)
   ```python
   # 上記のMultiAgentSystemクラスを実装
   ```

4. **基本テスト** (`test_agent_basic.py`)
   ```python
   async def test_basic_agents():
       """基本機能テスト"""
       
       # Simple Agent テスト
       simple_agent = SimpleTaskAgent("simple_1", "Save 'Hello' to {{greeting}}")
       await simple_agent.safe_run()
       
       result = simple_agent.session.get("greeting")
       assert result == "Hello"
       
       # Complex Agent テスト（短時間実行）
       complex_agent = ComplexMonitorAgent("monitor_1", monitor_interval=1.0)
       
       # 3秒後に停止
       async def stop_after_delay():
           await asyncio.sleep(3.0)
           complex_agent.stop()
       
       await asyncio.gather(
           complex_agent.safe_run(),
           stop_after_delay()
       )
   ```

### Phase 2: 具体例実装（基盤完成後）

**期間**: 3-4日  
**目標**: 実用的なエージェント例の実装

**実装項目:**

1. **研究エージェント** (`research_agents.py`)
   ```python
   class ResearchAgent(Agent):
       """研究タスク専用エージェント"""
       
       async def run(self):
           self.running = True
           self.session.save("research_phase", "literature_review")
           
           while self.running:
               phase = self.session.get("research_phase")
               
               if phase == "literature_review":
                   await self.literature_review()
               elif phase == "data_collection":
                   await self.data_collection()
               elif phase == "analysis":
                   await self.data_analysis()
               elif phase == "complete":
                   break
                   
               await asyncio.sleep(2.0)
       
       async def literature_review(self):
           await self.execute_macro(
               "Review literature on {{research_topic}} and save findings to {{literature_findings}}"
           )
           
           # 完了条件チェック
           findings = self.session.get("literature_findings")
           if findings and len(findings) > 100:  # 十分な文献レビュー完了
               self.session.save("research_phase", "data_collection")
       
       async def data_collection(self):
           await self.execute_macro(
               "Collect research data based on {{research_plan}} and save to {{collected_data}}"
           )
           
           data = self.session.get("collected_data")
           if data:
               self.session.save("research_phase", "analysis")
       
       async def data_analysis(self):
           await self.execute_macro(
               "Analyze collected data {{collected_data}} and save results to {{analysis_results}}"
           )
           
           results = self.session.get("analysis_results")
           if results:
               self.session.save("research_phase", "complete")
   ```

2. **コーディネーターエージェント** (`coordinator_agents.py`)
   ```python
   class ProjectCoordinatorAgent(Agent):
       """プロジェクト全体の調整を行うエージェント"""
       
       def __init__(self, agent_id: str, team_agents: list):
           super().__init__(agent_id)
           self.team_agents = team_agents
           
       async def run(self):
           self.running = True
           
           while self.running:
               # チーム状況の監視
               team_status = self.get_team_status()
               
               # 調整判断
               await self.execute_macro(
                   f"Based on team status {team_status}, decide coordination action and save to {{coordination_action}}"
               )
               
               action = self.session.get("coordination_action")
               await self.execute_coordination_action(action)
               
               if action == "project_complete":
                   self.session.save("@project_status", "completed")
                   break
               
               await asyncio.sleep(3.0)
       
       def get_team_status(self) -> dict:
           """チーム全体の状況を取得"""
           status = {}
           for agent_id in self.team_agents:
               status[agent_id] = self.get_agent_status(agent_id)
           return status
       
       async def execute_coordination_action(self, action: str):
           """調整アクションの実行"""
           if action == "assign_new_task":
               # 新しいタスクをアサイン
               self.session.save("@new_task_available", "true")
           elif action == "request_status_update":
               # 状況更新を要求
               for agent_id in self.team_agents:
                   self.send_message(agent_id, "Please provide status update")
   ```

3. **統合実行例** (`research_system_demo.py`)
   ```python
   async def run_research_project():
       """研究プロジェクトの実行例"""
       
       system = MultiAgentSystem()
       
       # エージェント作成
       researchers = [
           ResearchAgent(f"researcher_{i}") 
           for i in range(3)
       ]
       
       coordinator = ProjectCoordinatorAgent(
           "coordinator",
           team_agents=[r.agent_id for r in researchers]
       )
       
       # システムに追加
       for agent in researchers:
           system.add_agent(agent)
       system.add_agent(coordinator)
       
       # プロジェクト設定
       system.system_session.save("@research_topic", "AI Agent Architecture")
       system.system_session.save("@project_status", "starting")
       
       # 実行
       await system.run_all_agents()
   ```

### Phase 3: 高度機能追加（基本機能完成後）

**期間**: 1週間  
**目標**: 監視、動的制御、最適化機能の追加

**実装項目:**

1. **リアルタイム監視** (`agent_monitor.py`)
2. **動的エージェント制御** (`dynamic_control.py`)
3. **パフォーマンス最適化** (`performance_optimization.py`)

## 4. 完全コード実装例

### 4.1 即実装可能なスターターコード

**ディレクトリ構成:**
```
nlm_system/
├── agent_base.py           # Agent基底クラス
├── agent_examples.py       # 基本サブクラス例
├── multi_agent_system.py   # マルチエージェント実行システム
├── research_agents.py      # 具体的なエージェント例
├── test_agent_basic.py     # 基本テスト
└── demo_research_system.py # デモ実行
```

### 4.2 エントリーポイント実装例

```python
# demo_research_system.py - 実行可能なデモ

import asyncio
import logging
from agent_base import Agent
from agent_examples import SimpleTaskAgent, ComplexMonitorAgent
from multi_agent_system import MultiAgentSystem
from research_agents import ResearchAgent, ProjectCoordinatorAgent

async def main():
    """メインデモ実行"""
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Agent継承アーキテクチャ デモ開始")
    
    # システム作成
    system = MultiAgentSystem()
    
    # Simple Agent例
    simple_agents = [
        SimpleTaskAgent("setup_1", "Initialize project environment and save to {{env_status}}"),
        SimpleTaskAgent("setup_2", "Prepare research tools and save to {{tools_ready}}")
    ]
    
    # Complex Agent例
    complex_agents = [
        ResearchAgent("researcher_1"),
        ResearchAgent("researcher_2"),
        ProjectCoordinatorAgent("coordinator", ["researcher_1", "researcher_2"])
    ]
    
    # システムに追加
    for agent in simple_agents + complex_agents:
        system.add_agent(agent)
    
    # グローバル設定
    system.system_session.save("@research_topic", "Multi-Agent System Design")
    system.system_session.save("@project_deadline", "2 weeks")
    
    print("📋 エージェント構成:")
    for agent in system.agents:
        print(f"  - {agent.agent_id} ({type(agent).__name__})")
    
    # 実行
    try:
        await system.run_all_agents()
        print("✅ 全エージェント実行完了")
    except KeyboardInterrupt:
        print("⏹️ ユーザによる停止")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. 検証・テスト戦略

### 5.1 機能テスト項目

**基盤機能テスト:**
```python
async def test_agent_inheritance():
    """継承機能のテスト"""
    
    # 抽象クラスのインスタンス化エラー確認
    try:
        agent = Agent("test")
        assert False, "Should not be able to instantiate abstract class"
    except TypeError:
        pass  # 期待される動作
    
    # 正常なサブクラスのテスト
    class TestAgent(Agent):
        async def run(self):
            self.session.save("test_result", "success")
    
    test_agent = TestAgent("test_1")
    await test_agent.safe_run()
    
    result = test_agent.session.get("test_result")
    assert result == "success"

async def test_multiple_same_type_agents():
    """同タイプ複数エージェントのテスト"""
    
    agents = [ResearchAgent(f"researcher_{i}") for i in range(5)]
    
    # 各エージェントが独立した名前空間を持つことを確認
    for i, agent in enumerate(agents):
        agent.session.save("agent_number", str(i))
    
    for i, agent in enumerate(agents):
        result = agent.session.get("agent_number")
        assert result == str(i)

async def test_agent_communication():
    """エージェント間通信のテスト"""
    
    agent1 = ResearchAgent("sender")
    agent2 = ResearchAgent("receiver")
    
    # メッセージ送信
    agent1.send_message("receiver", "Hello from sender")
    
    # メッセージ受信確認
    messages = agent2.check_messages()
    assert len(messages) == 1
    assert messages[0]["from"] == "sender"
    assert messages[0]["message"] == "Hello from sender"
```

### 5.2 統合テストシナリオ

```python
async def integration_test_research_project():
    """研究プロジェクト統合テスト"""
    
    # システム構築
    system = MultiAgentSystem()
    
    # エージェント作成
    researchers = [ResearchAgent(f"researcher_{i}") for i in range(2)]
    coordinator = ProjectCoordinatorAgent("coordinator", [r.agent_id for r in researchers])
    
    for agent in researchers + [coordinator]:
        system.add_agent(agent)
    
    # プロジェクト設定
    system.system_session.save("@research_topic", "Test Topic")
    
    # 短時間実行テスト（無限ループ回避）
    async def stop_after_timeout():
        await asyncio.sleep(10.0)  # 10秒後に停止
        system.system_session.save("@system_shutdown", "true")
    
    # 並行実行
    await asyncio.gather(
        system.run_all_agents(),
        stop_after_timeout()
    )
    
    # 結果確認
    for researcher in researchers:
        status = researcher.session.get("agent_status")
        assert status in ["completed", "stopping", "stopped"]
```

### 5.3 パフォーマンステスト

```python
import time
import psutil

async def performance_test():
    """パフォーマンステスト"""
    
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    
    # 大量エージェント作成テスト
    agents = [SimpleTaskAgent(f"perf_test_{i}", "Save 'done' to {{status}}") for i in range(100)]
    
    system = MultiAgentSystem()
    for agent in agents:
        system.add_agent(agent)
    
    # 実行
    await system.run_all_agents()
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss
    
    # パフォーマンス指標
    execution_time = end_time - start_time
    memory_usage = (end_memory - start_memory) / 1024 / 1024  # MB
    
    print(f"100エージェント実行時間: {execution_time:.2f}秒")
    print(f"メモリ使用量増加: {memory_usage:.2f}MB")
    
    # パフォーマンス基準
    assert execution_time < 30.0  # 30秒以内
    assert memory_usage < 100.0   # 100MB以内
```

## 6. 実装上の注意点と対策

### 6.1 潜在的課題と対策

**課題1: 大量エージェント実行時のリソース消費**
```python
# 対策: エージェントプール管理
class AgentPool:
    def __init__(self, max_concurrent_agents=10):
        self.max_concurrent = max_concurrent_agents
        self.semaphore = asyncio.Semaphore(max_concurrent_agents)
    
    async def run_agent_with_limit(self, agent):
        async with self.semaphore:
            await agent.safe_run()
```

**課題2: エージェント間デッドロック**
```python
# 対策: タイムアウト付き待機
async def safe_wait_for_global(self, key, expected_value, timeout=30):
    """デッドロック防止用の安全な待機"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        value = self.session.get(f"@{key}")
        if value == expected_value:
            return True
        await asyncio.sleep(0.1)
    
    # タイムアウト時の処理
    self.logger.warning(f"Timeout waiting for @{key}, proceeding anyway")
    return False
```

**課題3: エラー伝播による全システム停止**
```python
# 対策: エージェント単位でのエラー隔離
async def run_all_agents_with_isolation(self):
    """エラー隔離付きエージェント実行"""
    results = []
    
    for agent in self.agents:
        try:
            result = await agent.safe_run()
            results.append(("success", agent.agent_id, result))
        except Exception as e:
            self.logger.error(f"Agent {agent.agent_id} failed: {e}")
            results.append(("error", agent.agent_id, str(e)))
            # 他のエージェントは継続実行
    
    return results
```

### 6.2 デバッグ戦略

**1. 詳細ログシステム**
```python
# 各エージェントの詳細ログ
class Agent(ABC):
    def __init__(self, agent_id):
        # ... existing code ...
        
        # 詳細ログ設定
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        handler = logging.FileHandler(f"logs/agent_{agent_id}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    async def execute_macro(self, macro_content):
        self.logger.info(f"Executing macro: {macro_content[:100]}...")
        start_time = time.time()
        
        result = await self.session.execute(macro_content)
        
        execution_time = time.time() - start_time
        self.logger.info(f"Macro completed in {execution_time:.2f}s: {result[:100]}...")
        
        return result
```

**2. リアルタイム状態監視**
```python
class SystemMonitor:
    """システム全体の状態監視"""
    
    def __init__(self, system: MultiAgentSystem):
        self.system = system
        
    async def monitor_loop(self):
        """監視ループ"""
        while True:
            status_report = self.generate_status_report()
            print(f"\n=== システム状況 {datetime.now().strftime('%H:%M:%S')} ===")
            print(status_report)
            
            await asyncio.sleep(5.0)
    
    def generate_status_report(self) -> str:
        """状況レポート生成"""
        report = []
        
        for agent in self.system.agents:
            status = agent.session.get("agent_status")
            last_activity = agent.session.get("last_activity_time")
            report.append(f"{agent.agent_id}: {status} (last: {last_activity})")
        
        return "\n".join(report)
```

**3. インタラクティブデバッグ**
```python
async def debug_session():
    """対話型デバッグセッション"""
    
    system = MultiAgentSystem()
    # ... エージェント追加 ...
    
    # デバッグ用コマンド
    while True:
        command = input("\nDebug command (status/stop/continue/quit): ").strip().lower()
        
        if command == "status":
            for agent in system.agents:
                status = agent.session.get("agent_status")
                print(f"{agent.agent_id}: {status}")
                
        elif command == "stop":
            for agent in system.agents:
                agent.stop()
                
        elif command == "continue":
            break
            
        elif command == "quit":
            return
```

### 6.3 監視・ログ設計

**階層的ログレベル:**
```python
# システムレベル: INFO
# エージェントレベル: INFO
# マクロ実行レベル: DEBUG
# エラー詳細: ERROR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system.log'),
        logging.StreamHandler()
    ]
)
```

**メトリクス収集:**
```python
class AgentMetrics:
    """エージェント性能指標収集"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_execution_time(self, agent_id: str, execution_time: float):
        if agent_id not in self.metrics:
            self.metrics[agent_id] = []
        self.metrics[agent_id].append(execution_time)
    
    def get_average_execution_time(self, agent_id: str) -> float:
        if agent_id not in self.metrics:
            return 0.0
        return sum(self.metrics[agent_id]) / len(self.metrics[agent_id])
```

## 7. 実装チェックリスト

### 2週間後の実装時に確認すべき項目

**基盤実装チェックリスト:**
- [ ] Agent基底クラスの実装（抽象メソッド含む）
- [ ] 基本サブクラス（SimpleTaskAgent, ComplexMonitorAgent）実装
- [ ] MultiAgentSystem実行システム実装
- [ ] エラーハンドリング（safe_run）実装
- [ ] 基本テストの作成と実行

**機能実装チェックリスト:**
- [ ] エージェント間通信（send_message, check_messages）
- [ ] グローバル変数待機（wait_for_global）
- [ ] 状態監視機能（get_agent_status, get_all_agent_statuses）
- [ ] 優雅な停止機能（stop）
- [ ] ログシステム統合

**統合テストチェックリスト:**
- [ ] 複数同タイプエージェント生成テスト
- [ ] Simple/Complex混在実行テスト
- [ ] エージェント間通信テスト
- [ ] エラー隔離テスト
- [ ] パフォーマンステスト

**運用準備チェックリスト:**
- [ ] ログディレクトリ作成
- [ ] 監視ダッシュボード設定
- [ ] デバッグ用ツール準備
- [ ] ドキュメント更新

## 8. まとめ

この実装計画により、美しく汎用性の高いAgent継承アーキテクチャを段階的に構築できます。

**核心的な設計決定:**
1. **抽象基底クラス**: 実装強制による型安全性
2. **NLMセッション統合**: 状態外部化の維持
3. **非同期実行**: スケーラブルな並行処理
4. **段階的実装**: Simple→Complexへの自然な移行

**期待される成果:**
- 複数同タイプエージェントの効率的生成
- 統一されたエージェント管理インターフェース
- 保守性の高いオブジェクト指向設計
- 既存NLMシステムとの完全互換性

2週間後の実装時には、このドキュメントを参照して確実に美しいアーキテクチャを実現してください。