# Migration Guide: deep-translator to OpenRouter LLM

このガイドでは、以前のバージョン（deep-translator使用）から新しいバージョン（OpenRouter LLM使用）への移行方法を説明します。

## 変更点の概要

### 削除された機能
- **deep-translator**: Google翻訳APIを使用した無料翻訳機能
- 自動的な翻訳（APIキー不要）

### 追加された機能
- **OpenRouter LLM翻訳**: より高品質なLLMベースの翻訳
- 無料モデルのサポート（APIキー必要だが、無料モデルを使用可能）
- カスタマイズ可能な翻訳プロンプト
- より正確なゲーム用語の翻訳

## 移行手順

### 1. 新しいバージョンへのアップデート

```bash
# 既存の依存関係を削除
pip uninstall deep-translator

# 新しい依存関係をインストール
pip install openai python-dotenv
```

または、`requirements.txt`から自動インストール：

```bash
pip install -r requirements.txt
```

### 2. OpenRouter APIキーの取得

1. [OpenRouter](https://openrouter.ai/)にアクセス
2. 無料アカウントを作成
3. [APIキーページ](https://openrouter.ai/keys)でAPIキーを生成
4. APIキーを安全な場所にコピー

### 3. 設定方法

**推奨方法**: UI設定ダイアログを使用

1. アプリケーションを起動
2. ⚙️（設定）アイコンをクリック
3. APIキーを入力フィールドに貼り付け
4. 「モデルを取得」ボタンをクリック
5. 検索バーで目的のモデルを検索（例：「free」で無料モデル検索）
6. 使用したいモデルをクリックして選択
7. （オプション）レート制限対策としてフォールバックモデルを追加
8. 「保存」をクリック

**代替方法（開発者向け、非推奨）**: .env ファイル設定

> **注意**: `.env`ファイル設定は非推奨です。セキュリティのため、UI設定（⚙️アイコン）を使用することを強く推奨します。

開発者や高度なユーザー向けに、`.env`ファイルでの設定も可能です：

プロジェクトのルートディレクトリに`.env`ファイルを作成します：

```env
# OpenRouter API Key（必須）
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here

# 使用するモデル（オプション）
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

**重要**: `.env`ファイルはGitにコミットしないでください（既に`.gitignore`に含まれています）

### 4. 動作確認

アプリケーションを起動して、翻訳機能が正常に動作することを確認します：

```bash
python main.py
```

## トラブルシューティング

### エラー: "OpenRouter API key is not set"

**原因**: APIキーが設定されていません

**解決方法**:
1. アプリケーションを起動
2. ⚙️（設定）アイコンをクリック
3. APIキーを入力して保存
4. （代替）`.env`ファイルに`OPENROUTER_API_KEY=your-key-here`を追加してアプリを再起動

### エラー: "Model not found"

**原因**: 指定したモデルが存在しないか、利用できません

**解決方法**:
1. モデルIDを確認（`:free`サフィックスを忘れずに）
2. [OpenRouterモデルリスト](https://openrouter.ai/models)で最新のモデルを確認
3. `.env`ファイルのモデルIDを更新

### 翻訳が遅い

**原因**: 無料モデルは有料モデルより遅い場合があります

**解決方法**:
1. より高速な無料モデル（`google/gemini-flash-1.5:free`など）を試す
2. 有料モデルの使用を検討
3. 並列処理が有効になっていることを確認

## 無料モデルと有料モデルの比較

| 項目 | 無料モデル | 有料モデル |
|------|-----------|-----------|
| APIキー | 必要 | 必要 |
| コスト | 無料 | 使用量に応じて課金 |
| 速度 | 通常 | 高速 |
| 品質 | 良好 | 非常に良好 |
| レート制限 | あり | より緩い |
| 推奨用途 | 個人使用、テスト | 商用、大規模プロジェクト |

## よくある質問

### Q: 以前のバージョンと同じように完全無料で使えますか？

A: OpenRouterアカウントは無料で作成でき、無料モデルを使用できます。ただし、APIキーの設定が必要です。

### Q: deep-translatorに戻すことはできますか？

A: 技術的には可能ですが、現在のバージョンではサポートされていません。古いバージョンのコードに戻す必要があります。

### Q: 翻訳品質は向上しましたか？

A: はい。LLMベースの翻訳はコンテキストを理解し、ゲーム用語をより適切に翻訳できます。

### Q: 複数のLLMプロバイダー（OpenAI、Anthropicなど）をサポートしますか？

A: OpenRouterは単一のAPIで複数のLLMプロバイダーにアクセスできます。モデルIDを変更するだけで異なるプロバイダーのモデルを使用できます。

## さらに詳しい情報

- [OpenRouter無料モデルガイド](./OPENROUTER_FREE_MODELS.md)
- [OpenRouter公式ドキュメント](https://openrouter.ai/docs)
- [サポートされているモデル一覧](https://openrouter.ai/models)

## サポート

問題が発生した場合は、以下の方法でサポートを受けられます：

1. [GitHubイシュー](https://github.com/Maji3429/Minecraft_Mod_Translate_tool/issues)を作成
2. エラーメッセージの全文を含める
3. `.env`ファイルの内容は**含めないでください**（APIキーが漏洩します）

---

**注意**: このアップデートにより、deep-translatorの依存関係は完全に削除されました。古いバージョンに戻す必要がある場合は、Gitの履歴から以前のコミットをチェックアウトしてください。
