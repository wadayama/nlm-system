#!/usr/bin/env python3
"""現状システムでの非変数マクロ動作実験

変数操作を伴わないマクロ（{{variable}}構文なし）が
現在のNLMシステムでどのように処理されるかを実験的に検証する。
"""

from src.nlm_interpreter import NLMSession
import time

def test_current_non_variable_behavior():
    """現状システムでの非変数マクロ動作を包括的にテスト"""
    
    print("🧪 非変数マクロ動作実験")
    print("="*60)
    print("目的: 現在のNLMシステムが{{variable}}構文なしのクエリにどう反応するかを確認")
    print("="*60)
    
    # テスト用セッション作成
    session = NLMSession(namespace="non_var_experiment", model="gpt-5-mini")
    
    # 事前準備: いくつかの変数を設定
    session.save("name", "田中")
    session.save("@project", "NLMテスト")
    
    print(f"📋 事前設定完了:")
    print(f"  ローカル変数: {session.list_local()}")
    print(f"  グローバル変数: {session.list_global()}")
    
    # テストケース定義
    test_cases = [
        # === カテゴリ1: 基本的な事実確認質問 ===
        {
            "category": "基本質問",
            "cases": [
                "日本で一番高い山は？",
                "What is the capital of France?",
                "2+2は何ですか？",
                "Tell me about Python programming language",
                "今日は何曜日ですか？"
            ]
        },
        
        # === カテゴリ2: 複雑な説明・解説質問 ===
        {
            "category": "説明・解説質問",
            "cases": [
                "機械学習とは何か簡潔に説明してください",
                "Explain how photosynthesis works",
                "量子コンピュータの基本原理を教えて",
                "What are the benefits of renewable energy?",
                "SQLとNoSQLデータベースの違いは？"
            ]
        },
        
        # === カテゴリ3: 計算・推論系質問 ===
        {
            "category": "計算・推論質問", 
            "cases": [
                "10の階乗を計算してください",
                "Calculate the area of a circle with radius 5",
                "1から100までの和は？",
                "What is 25% of 80?",
                "フィボナッチ数列の最初の10項を教えて"
            ]
        },
        
        # === カテゴリ4: 混合パターン（変数構文あり） ===
        {
            "category": "混合パターン",
            "cases": [
                "日本の首都を教えて、{{capital}}に保存してください",
                "Calculate 2+2 and save the result to {{math_result}}",
                "Explain AI briefly and store it in {{@ai_explanation}}",
                "今日の日付を{{today}}に記録して",
                "Set {{status}} to 'completed' after answering this"
            ]
        },
        
        # === カテゴリ5: 変数参照を含む質問 ===
        {
            "category": "変数参照質問",
            "cases": [
                "{{name}}さんの年齢を教えてください",  # nameは事前設定済み
                "{{@project}}について詳しく説明して",   # @projectは事前設定済み
                "{{unknown_var}}の値は何ですか？",       # 存在しない変数
                "Tell me about {{name}} and their background",
                "What is the status of {{@project}}?"
            ]
        },
        
        # === カテゴリ6: システム動作・メタ質問 ===
        {
            "category": "システム動作",
            "cases": [
                "Tokyo を capital という名前で保存して",  # 変数構文なしの保存要求
                "変数一覧を表示してください",               # ツール機能の直接要求
                "Save 'Hello World' as a greeting",      # 英語での保存要求
                "何かの値を test という変数に入れて",        # 抽象的な保存要求
                "Delete all my variables"                # 削除要求
            ]
        }
    ]
    
    # 実験実行
    experiment_results = []
    
    for test_group in test_cases:
        category = test_group["category"]
        cases = test_group["cases"]
        
        print(f"\n{'='*20} {category} {'='*20}")
        
        for i, query in enumerate(cases, 1):
            print(f"\n📋 テスト {category}-{i}: {query}")
            
            try:
                start_time = time.time()
                result = session.execute(query)
                execution_time = time.time() - start_time
                
                print(f"✅ 応答 ({execution_time:.2f}s):")
                print(f"   {result[:300]}{'...' if len(result) > 300 else ''}")
                
                # 結果記録
                experiment_results.append({
                    "category": category,
                    "query": query,
                    "success": True,
                    "response": result,
                    "execution_time": execution_time,
                    "response_length": len(result)
                })
                
            except Exception as e:
                print(f"❌ エラー: {str(e)[:200]}{'...' if len(str(e)) > 200 else ''}")
                
                experiment_results.append({
                    "category": category,
                    "query": query,
                    "success": False,
                    "error": str(e),
                    "execution_time": 0,
                    "response_length": 0
                })
                
            # レート制限対策
            time.sleep(1)
    
    # 実験後の状態確認
    print(f"\n{'='*20} 実験後の状態確認 {'='*20}")
    print(f"📊 ローカル変数: {session.list_local()}")
    print(f"📊 グローバル変数: {session.list_global()}")
    
    # 結果分析
    analyze_results(experiment_results)
    
    return experiment_results

def analyze_results(results):
    """実験結果の分析とレポート生成"""
    
    print(f"\n{'='*20} 実験結果分析 {'='*20}")
    
    # 基本統計
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - successful_tests
    
    print(f"📈 基本統計:")
    print(f"   総テスト数: {total_tests}")
    print(f"   成功: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
    print(f"   失敗: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    
    # カテゴリ別成功率
    print(f"\n📊 カテゴリ別成功率:")
    categories = {}
    for result in results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "success": 0}
        categories[cat]["total"] += 1
        if result["success"]:
            categories[cat]["success"] += 1
    
    for cat, stats in categories.items():
        success_rate = stats["success"] / stats["total"] * 100
        print(f"   {cat}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    # パフォーマンス分析
    successful_results = [r for r in results if r["success"]]
    if successful_results:
        avg_time = sum(r["execution_time"] for r in successful_results) / len(successful_results)
        avg_length = sum(r["response_length"] for r in successful_results) / len(successful_results)
        
        print(f"\n⏱️ パフォーマンス統計:")
        print(f"   平均実行時間: {avg_time:.2f}秒")
        print(f"   平均応答長: {avg_length:.0f}文字")
    
    # エラー分析
    if failed_tests > 0:
        print(f"\n❌ エラー分析:")
        error_types = {}
        for result in results:
            if not result["success"]:
                error = result.get("error", "Unknown error")
                error_type = error.split(":")[0] if ":" in error else error[:50]
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            print(f"   {error_type}: {count}回")

def main():
    """メイン実行関数"""
    try:
        print("🚀 非変数マクロ動作実験開始")
        results = test_current_non_variable_behavior()
        
        print(f"\n{'='*60}")
        print("✅ 実験完了！結果は上記の通りです。")
        print("💡 次のステップ: この結果を基に改善方針を検討してください。")
        
        return True
        
    except Exception as e:
        print(f"\n💥 実験中にエラーが発生: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)