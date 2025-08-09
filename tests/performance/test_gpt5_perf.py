#!/usr/bin/env python
"""Test performance impact of variable operations with gpt-5"""

from time import time
from nlm_interpreter import NLMSession


def test_gpt5_performance():
    """Compare performance with and without variables using gpt-5"""
    print("="*70)
    print("🔍 gpt-5 パフォーマンステスト（変数操作の影響）")
    print("="*70)
    
    session = NLMSession(model="gpt-5", namespace="gpt5_perf_test")
    
    # Test 1: No variables (just text processing)
    print("\n1️⃣ 変数なし（テキスト処理のみ）:")
    print("-" * 50)
    
    no_var_commands = [
        "Tell me what is 2+2",
        "Say hello world",
        "Count from 1 to 5",
        "What day comes after Monday?"
    ]
    
    no_var_times = []
    for cmd in no_var_commands:
        print(f"\nCommand: {cmd}")
        start = time()
        try:
            result = session.execute(cmd)
            elapsed = time() - start
            no_var_times.append(elapsed)
            print(f"  ⏱️  Time: {elapsed:.3f}s")
            print(f"  Result: {result[:80]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test 2: With variable save operations
    print("\n\n2️⃣ 変数保存あり ({{variable}}):")
    print("-" * 50)
    
    var_commands = [
        "Set {{answer}} to the result of 2+2",
        "Store 'hello world' in {{greeting}}",
        "Save the count from 1 to 5 in {{numbers}}",
        "Put 'Tuesday' in {{next_day}}"
    ]
    
    var_times = []
    for cmd in var_commands:
        print(f"\nCommand: {cmd}")
        start = time()
        try:
            result = session.execute(cmd)
            elapsed = time() - start
            var_times.append(elapsed)
            print(f"  ⏱️  Time: {elapsed:.3f}s")
            
            # Extract variable name and show value
            if "{{" in cmd:
                var_name = cmd[cmd.find("{{")+2:cmd.find("}}")]
                value = session.get(var_name)
                print(f"  Variable: {var_name} = {value}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test 3: Variable read operations
    print("\n\n3️⃣ 変数読み取りあり:")
    print("-" * 50)
    
    # First set some variables
    session.save("test_value", "42")
    session.save("test_name", "Alice")
    
    read_commands = [
        "What is the value of {{test_value}}?",
        "Tell me about {{test_name}}",
        "Combine {{test_value}} and {{test_name}} into a sentence"
    ]
    
    read_times = []
    for cmd in read_commands:
        print(f"\nCommand: {cmd}")
        start = time()
        try:
            result = session.execute(cmd)
            elapsed = time() - start
            read_times.append(elapsed)
            print(f"  ⏱️  Time: {elapsed:.3f}s")
            print(f"  Result: {result[:80]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Summary and Comparison
    print("\n\n" + "="*70)
    print("📊 gpt-5 パフォーマンス分析:")
    print("="*70)
    
    if no_var_times:
        avg_no_var = sum(no_var_times) / len(no_var_times)
        print(f"\n1️⃣ 変数なし:")
        print(f"   平均: {avg_no_var:.3f}s")
        print(f"   最速: {min(no_var_times):.3f}s")
        print(f"   最遅: {max(no_var_times):.3f}s")
    
    if var_times:
        avg_var = sum(var_times) / len(var_times)
        print(f"\n2️⃣ 変数保存:")
        print(f"   平均: {avg_var:.3f}s")
        print(f"   最速: {min(var_times):.3f}s")
        print(f"   最遅: {max(var_times):.3f}s")
    
    if read_times:
        avg_read = sum(read_times) / len(read_times)
        print(f"\n3️⃣ 変数読み取り:")
        print(f"   平均: {avg_read:.3f}s")
        print(f"   最速: {min(read_times):.3f}s")
        print(f"   最遅: {max(read_times):.3f}s")
    
    # Performance impact analysis
    if no_var_times and var_times:
        impact = (avg_var - avg_no_var) / avg_no_var * 100
        print(f"\n⚡ パフォーマンス影響:")
        print(f"   変数保存は {impact:.0f}% 遅い")
        
        if impact > 100:
            print(f"   🔴 大幅なスローダウン: ツール呼び出しのオーバーヘッドが原因")
        elif impact > 50:
            print(f"   🟡 顕著なスローダウン: マルチターン処理の影響")
        else:
            print(f"   🟢 影響は軽微")
    
    # Compare with all models
    print("\n\n📈 全モデル比較:")
    print("-" * 50)
    print("| モデル      | 変数なし | 変数保存 | 変数読取 |")
    print("|------------|---------|---------|---------|")
    print("| gpt-5-nano | 3.3秒   | 10.6秒  | 8.7秒   |")
    print("| gpt-5-mini | 3.4秒   | 5.5秒   | 6.9秒   |")
    
    if no_var_times and var_times:
        read_avg_str = f"{avg_read:.1f}秒" if read_times else "N/A"
        print(f"| gpt-5      | {avg_no_var:.1f}秒   | {avg_var:.1f}秒   | {read_avg_str}   |")
        
        print(f"\n🏆 パフォーマンスランキング:")
        # Determine best model for each category
        models_no_var = [("gpt-5-nano", 3.3), ("gpt-5-mini", 3.4), ("gpt-5", avg_no_var)]
        models_var = [("gpt-5-nano", 10.6), ("gpt-5-mini", 5.5), ("gpt-5", avg_var)]
        
        models_no_var.sort(key=lambda x: x[1])
        models_var.sort(key=lambda x: x[1])
        
        print(f"\n  変数なし処理（速い順）:")
        for i, (model, t) in enumerate(models_no_var, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print(f"    {medal} {model}: {t:.1f}秒")
        
        print(f"\n  変数保存処理（速い順）:")
        for i, (model, t) in enumerate(models_var, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print(f"    {medal} {model}: {t:.1f}秒")


if __name__ == "__main__":
    try:
        test_gpt5_performance()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()