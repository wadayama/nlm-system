#!/usr/bin/env python
"""Test 7: Performance tests (without LLM)"""

from nlm_interpreter import NLMSession
import time

print("="*60)
print("7. パフォーマンステスト（LLM不要）")
print("="*60)

session = NLMSession(namespace="performance")

# Case 1: 非常に長い変数値
print("\nCase 1: 長大な値の処理")
long_value = "x" * 10000
session.save("huge", long_value)
retrieved = session.get("huge")
if len(retrieved) == 10000:
    print(f"✅ 10,000文字の値を正常に保存・取得")
else:
    print(f"❌ 値の長さが異なる: {len(retrieved)}")

# Case 2: 多数の変数
print("\nCase 2: 多数の変数作成")
start = time.time()
for i in range(100):
    session.save(f"var{i}", f"value{i}")
elapsed = time.time() - start
print(f"✅ 100個の変数を{elapsed:.3f}秒で作成")

# Case 3: 高速読み取り
print("\nCase 3: 高速読み取り")
start = time.time()
for i in range(100):
    value = session.get(f"var{i}")
elapsed = time.time() - start
print(f"✅ 100個の変数を{elapsed:.3f}秒で読み取り")

# Case 4: メモリ効率（巨大な値を複数）
print("\nCase 4: メモリ効率テスト")
huge_val = "y" * 100000
for i in range(10):
    session.save(f"huge{i}", huge_val)
print(f"✅ 10個の100KB変数を保存")

# Case 5: 名前空間の分離パフォーマンス
print("\nCase 5: 名前空間分離のオーバーヘッド")
sessions = []
start = time.time()
for i in range(10):
    s = NLMSession(namespace=f"ns{i}")
    s.save("test", f"value{i}")
    sessions.append(s)
elapsed = time.time() - start
print(f"✅ 10個のセッションを{elapsed:.3f}秒で作成")

# Case 6: グローバル変数のパフォーマンス
print("\nCase 6: グローバル変数アクセス")
start = time.time()
for i in range(50):
    session.save(f"@global{i}", f"gvalue{i}")
for i in range(50):
    value = session.get(f"@global{i}")
elapsed = time.time() - start
print(f"✅ 50個のグローバル変数の保存・取得を{elapsed:.3f}秒で完了")

print("\n" + "="*60)
print("テスト7完了")