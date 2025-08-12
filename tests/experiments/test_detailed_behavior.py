#!/usr/bin/env python3
"""詳細な非変数マクロ動作分析"""

from src.nlm_interpreter import NLMSession

def detailed_analysis():
    """より詳細な動作パターンの分析"""
    
    print("🔍 詳細な非変数マクロ動作分析")
    print("="*50)
    
    session = NLMSession(namespace="detailed_analysis", model="gpt-5-mini")
    
    # より詳細なテストケース
    test_cases = [
        # 純粋な質問（変数操作期待なし）
        {
            "type": "純粋質問",
            "query": "機械学習とは何ですか？",
            "expected": "直接回答"
        },
        
        # 自然言語での保存要求（変数構文なし）
        {
            "type": "自然言語保存",
            "query": "Pythonの説明を explanation という変数に保存してください",
            "expected": "ツール呼び出し"
        },
        
        # 明示的な変数構文
        {
            "type": "明示的変数",
            "query": "Save 'Hello' to {{greeting}}",
            "expected": "ツール呼び出し"
        },
        
        # あいまいな指示
        {
            "type": "あいまい指示",
            "query": "何かデータを test に入れて",
            "expected": "？"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 {test_case['type']}: {test_case['query']}")
        print(f"期待動作: {test_case['expected']}")
        
        try:
            result = session.execute(test_case['query'])
            print(f"✅ 実際の応答:")
            print(f"   {result}")
            
            # ツール呼び出しがあったかの判定（簡易）
            has_tool_call = "Successfully saved" in result or "Variable" in result
            print(f"📊 ツール呼び出し: {'有' if has_tool_call else '無'}")
            
        except Exception as e:
            print(f"❌ エラー: {e}")
        
        print("-" * 30)
    
    print("\n最終的な変数状態:")
    print(f"ローカル: {session.list_local()}")

if __name__ == "__main__":
    detailed_analysis()