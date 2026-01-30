# OpenRouter 無料モデルガイド

このドキュメントでは、OpenRouterで利用可能な無料モデルと、その設定方法について説明します。

## 利用可能な無料モデル

OpenRouterでは、`:free`サフィックスを付けたモデルを無料で使用できます。以下は推奨される無料モデルです：

### 推奨モデル

1. **Meta Llama 3.2 3B Instruct (デフォルト)**
   - モデルID: `meta-llama/llama-3.2-3b-instruct:free`
   - コンテキスト長: 131,072トークン
   - 特徴: バランスの取れた性能と速度

2. **Google Gemini Flash 1.5**
   - モデルID: `google/gemini-flash-1.5:free`
   - コンテキスト長: 1,048,576トークン (1M)
   - 特徴: 非常に長いコンテキストウィンドウ

3. **Qwen 2 7B Instruct**
   - モデルID: `qwen/qwen-2-7b-instruct:free`
   - コンテキスト長: 32,768トークン
   - 特徴: 多言語対応に優れる

## セットアップ方法

### 1. OpenRouter APIキーの取得

1. [OpenRouter](https://openrouter.ai/)にアクセス
2. アカウントを作成（無料）
3. [APIキーページ](https://openrouter.ai/keys)でAPIキーを生成
4. APIキーをコピー

### 2. 環境設定

1. プロジェクトルートに`.env`ファイルを作成
2. 以下の内容を記述：

```env
# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# モデル選択（以下のいずれかを使用）
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
# OPENROUTER_MODEL=google/gemini-flash-1.5:free
# OPENROUTER_MODEL=qwen/qwen-2-7b-instruct:free
```

### 3. モデルの変更

異なるモデルを試したい場合は、`.env`ファイルの`OPENROUTER_MODEL`の値を変更してください。

## 無料モデルの制限

- **レート制限**: 無料モデルには利用制限があります。短時間に大量のリクエストを送信すると制限に達する可能性があります
- **可用性**: 無料モデルは有料モデルより可用性が低い場合があります
- **性能**: 無料モデルは一般的に有料モデルより小さいため、複雑なタスクでは性能が劣る場合があります

## トラブルシューティング

### API キーエラー

```
TranslationError: OpenRouter API key is not set
```

解決方法:
1. `.env`ファイルが存在することを確認
2. `OPENROUTER_API_KEY`が正しく設定されていることを確認
3. APIキーが有効であることを確認

### レート制限エラー

```
429 Too Many Requests
```

解決方法:
1. しばらく待ってから再試行
2. 翻訳するMODの数を減らす
3. 有料モデルの使用を検討

### モデルが見つからない

```
Model not found
```

解決方法:
1. モデルIDが正確であることを確認
2. `:free`サフィックスが含まれていることを確認
3. [OpenRouterモデルリスト](https://openrouter.ai/models)で最新のモデルIDを確認

## より高度な使用方法

### カスタムプロンプトの設定

翻訳プロンプトは`src/core/translator.py`の`translate_text`関数内で定義されています。
より良い翻訳結果を得るために、プロンプトをカスタマイズできます。

### 有料モデルの使用

より高品質な翻訳が必要な場合は、有料モデルの使用を検討してください：

- `anthropic/claude-3.5-sonnet` - 最高品質の翻訳
- `openai/gpt-4o` - バランスの取れた性能
- `google/gemini-pro-1.5` - コスト効率的

有料モデルを使用する場合は、OpenRouterアカウントにクレジットを追加する必要があります。

## 参考リンク

- [OpenRouter公式サイト](https://openrouter.ai/)
- [OpenRouterドキュメント](https://openrouter.ai/docs)
- [利用可能なモデル一覧](https://openrouter.ai/models)
- [価格設定](https://openrouter.ai/docs/overview/models)
