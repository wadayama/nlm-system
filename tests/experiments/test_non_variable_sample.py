#!/usr/bin/env python3
"""簡易版: 非変数マクロ動作実験"""

from src.nlm_interpreter import NLMSession

def quick_non_variable_test():
    """代表的なケースでの動作確認"""
    
    print("🧪 非変数マクロ動作実験（簡易版）")
    print("="*50)
    
    session = NLMSession(namespace="quick_test", model="gpt-5-mini")
    
    # 代表的なテストケース
    test_cases = [
        ("基本質問", "日本で一番高い山は？"),
        ("計算質問", "2+2は？"),
        ("混合パターン", "日本の首都を教えて、{{capital}}に保存してください"),
        ("変数なし保存要求", "Tokyo を capital という変数に保存して"),
        ("システム要求", "変数一覧を表示してください")
    ]
    
    print("事前状態:")
    print(f"  ローカル変数: {session.list_local()}")
    print(f"  グローバル変数: {session.list_global()}")
    
    for category, query in test_cases:
        print(f"\n📋 {category}: {query}")
        try:
            result = session.execute(query)
            print(f"✅ 応答: {result[:200]}...")
        except Exception as e:
            print(f"❌ エラー: {e}")
    
    print("\n事後状態:")
    print(f"  ローカル変数: {session.list_local()}")
    print(f"  グローバル変数: {session.list_global()}")

if __name__ == "__main__":
    quick_non_variable_test()