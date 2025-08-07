# GitHub プライベートリポジトリ設定手順

## 1. ローカルリポジトリの初期化

新しいフォルダ（`/Users/wadayama/Dropbox/nlm_system`）で以下を実行：

```bash
cd /Users/wadayama/Dropbox/nlm_system
git init
git add .
git commit -m "Initial commit: NLM System with cleaned structure"
```

## 2. GitHubでプライベートリポジトリ作成

1. GitHubにログイン
2. 右上の「+」→「New repository」をクリック
3. 以下の設定で作成：
   - **Repository name**: `nlm-system`
   - **Description**: "Natural Language Macro System with Multi-Agent Support"
   - **Private**: ✅ チェック
   - **Initialize this repository with**: 何も選択しない（READMEなし）

## 3. ローカルとGitHubを接続

GitHubでリポジトリ作成後に表示されるコマンドを実行：

```bash
git remote add origin https://github.com/wadayama/nlm-system.git
git branch -M main
git push -u origin main
```

または、SSHを使用する場合：

```bash
git remote add origin git@github.com:wadayama/nlm-system.git
git branch -M main
git push -u origin main
```

## 4. 認証設定（必要な場合）

### HTTPS使用時
Personal Access Tokenが必要です：
1. GitHub Settings → Developer settings → Personal access tokens
2. "Generate new token (classic)" をクリック
3. `repo` スコープを選択
4. トークンを生成し、pushの際のパスワードとして使用

### SSH使用時
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# 出力された公開鍵をGitHub Settings → SSH and GPG keys に追加
```

## 5. 今後の作業フロー

```bash
# 変更をステージング
git add .

# コミット
git commit -m "コミットメッセージ"

# プッシュ
git push

# ブランチ作成して作業
git checkout -b feature/agent-implementation
# 作業後
git add .
git commit -m "Implement Agent base class"
git push -u origin feature/agent-implementation
```

## 6. 推奨される初期コミット構成

```bash
# 初回コミット（実行済み）
git commit -m "Initial commit: NLM System with cleaned structure"

# 2回目以降の推奨コミット
git commit -m "docs: Add CLAUDE.md for LLM instructions"
git commit -m "test: Clean up and organize test files"
git commit -m "chore: Add .gitignore for Python project"
```

## 注意事項

- `variables.db` はgitignoreされているため、コミットされません
- プライベートリポジトリのため、他者はアクセスできません
- 定期的にコミット・プッシュすることを推奨します

---

*設定完了後、このファイルは削除しても構いません。*