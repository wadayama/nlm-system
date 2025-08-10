#!/usr/bin/env python3
"""Test haiku generation with NLM System"""

import os
import sys
import time

from nlm_interpreter import NLMSession, nlm_execute


def test_haiku_generation():
    """Test haiku generation capabilities"""
    print("🌸 俳句生成テスト (Haiku Generation Test)")
    print("="*60)
    
    # Create session
    session = NLMSession(namespace="haiku_test")
    
    # Test 1: Simple haiku generation
    print("\nTest 1: シンプルな俳句生成")
    print("Instruction: Generate a haiku about spring and save it to {{spring_haiku}}")
    
    start_time = time.time()
    result = session.execute("Generate a haiku about spring and save it to {{spring_haiku}}")
    elapsed = time.time() - start_time
    
    print(f"Time: {elapsed:.2f}s")
    print(f"Result: {result}")
    
    # Check stored haiku
    stored_haiku = session.variable_db.get_variable("haiku_test.spring_haiku")
    if stored_haiku:
        print(f"\n保存された俳句 (Stored haiku):")
        print(f"  {stored_haiku}")
    
    print("\n" + "-"*60)
    
    # Test 2: Japanese theme haiku
    print("\nTest 2: 日本の季節をテーマにした俳句")
    print("Instruction: 桜について俳句を作って{{sakura_haiku}}に保存してください")
    
    start_time = time.time()
    result = session.execute("桜について俳句を作って{{sakura_haiku}}に保存してください")
    elapsed = time.time() - start_time
    
    print(f"Time: {elapsed:.2f}s")
    print(f"Result: {result}")
    
    # Check stored haiku
    stored_haiku = session.variable_db.get_variable("haiku_test.sakura_haiku")
    if stored_haiku:
        print(f"\n保存された俳句:")
        print(f"  {stored_haiku}")
    
    print("\n" + "-"*60)
    
    # Test 3: Multiple haiku with themes
    print("\nTest 3: テーマ別俳句の連続生成")
    themes = [
        ("summer", "夏"),
        ("autumn", "秋"),
        ("winter", "冬")
    ]
    
    for eng_theme, jp_theme in themes:
        print(f"\n{jp_theme}の俳句 ({eng_theme} haiku):")
        
        instruction = f"Create a haiku about {eng_theme} and save it to {{{{{eng_theme}_haiku}}}}"
        start_time = time.time()
        result = session.execute(instruction)
        elapsed = time.time() - start_time
        
        print(f"  Time: {elapsed:.2f}s")
        
        # Get the stored haiku
        stored = session.variable_db.get_variable(f"haiku_test.{eng_theme}_haiku")
        if stored:
            print(f"  俳句: {stored}")
    
    print("\n" + "-"*60)
    
    # Test 4: Get all haikus
    print("\nTest 4: 保存された全俳句の確認")
    result = session.execute("List all variables and show the haikus")
    print(f"Result: {result}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 俳句生成テスト結果:")
    
    all_vars = session.variable_db.list_variables()
    haiku_vars = {k: v for k, v in all_vars.items() if 'haiku' in k and k.startswith('haiku_test.')}
    
    print(f"\n生成された俳句数: {len(haiku_vars)}")
    print("\n全俳句リスト:")
    for var_name, haiku in haiku_vars.items():
        theme = var_name.split('.')[-1].replace('_haiku', '')
        print(f"\n{theme}:")
        # Try to format haiku nicely if it contains line breaks
        if '\n' in haiku:
            for line in haiku.split('\n'):
                print(f"  {line}")
        else:
            print(f"  {haiku}")


def test_haiku_with_expansion():
    """Test haiku generation with variable expansion"""
    print("\n\n🌺 俳句生成と変数展開テスト")
    print("="*60)
    
    session = NLMSession(namespace="haiku_expand")
    
    # Save a theme
    print("\nStep 1: テーマを変数に保存")
    session.execute("Save 'cherry blossoms' to {{theme}}")
    
    # Generate haiku using the theme
    print("\nStep 2: 変数を使って俳句生成")
    print("Instruction: Generate a haiku about {{theme}} and save to {{themed_haiku}}")
    
    start_time = time.time()
    result = session.execute("Generate a haiku about {{theme}} and save to {{themed_haiku}}")
    elapsed = time.time() - start_time
    
    print(f"Time: {elapsed:.2f}s")
    print(f"Result: {result}")
    
    # Check expansion
    theme = session.variable_db.get_variable("haiku_expand.theme")
    haiku = session.variable_db.get_variable("haiku_expand.themed_haiku")
    
    print(f"\nテーマ: {theme}")
    print(f"生成された俳句: {haiku}")
    
    # Test expansion in output
    print("\nStep 3: 俳句の表示テスト")
    expanded = session._expand_variables("The haiku about {{theme}} is: {{themed_haiku}}")
    print(f"Expanded result: {expanded}")


def test_global_haiku_collection():
    """Test global haiku collection"""
    print("\n\n🌍 グローバル俳句コレクション")
    print("="*60)
    
    # Create multiple sessions
    session1 = NLMSession(namespace="poet1")
    session2 = NLMSession(namespace="poet2")
    
    print("\nPoet 1: Creating morning haiku")
    session1.execute("Create a haiku about morning and save to {{@morning_haiku}}")
    
    print("\nPoet 2: Creating evening haiku")
    session2.execute("Create a haiku about evening and save to {{@evening_haiku}}")
    
    # Access from another session
    reader = NLMSession(namespace="reader")
    print("\nReader: Accessing global haiku collection")
    
    morning = reader._get_variable_tool("@morning_haiku")
    evening = reader._get_variable_tool("@evening_haiku")
    
    print(f"\nGlobal Haiku Collection:")
    print(f"Morning: {morning}")
    print(f"Evening: {evening}")


def main():
    """Run all haiku tests"""
    print("🎌 NLM System 俳句生成テスト")
    print("Testing haiku generation capabilities with variable management\n")
    
    # Check LMStudio connection
    import requests
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        print("✅ LMStudio is connected (default endpoint)")
    except:
        print("⚠️  LMStudio not found, trying Ollama...")
        try:
            response = requests.get("http://localhost:11434/v1/models", timeout=2)
            print("✅ Ollama is connected (performance may be slower)")
        except:
            print("❌ No LLM server found")
            return
    
    # Run tests
    test_haiku_generation()
    test_haiku_with_expansion()
    test_global_haiku_collection()
    
    print("\n" + "="*60)
    print("🎊 俳句生成テスト完了!")
    print("Haiku generation tests completed successfully!")


if __name__ == "__main__":
    main()