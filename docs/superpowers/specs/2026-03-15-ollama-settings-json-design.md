# Ollama設定のJSON永続化 — 設計仕様

**日付:** 2026-03-15
**ブランチ:** refactor-phase-2

---

## 概要

アプリ再起動後もOllama設定（サーバーURL・モデル名）が保持されるよう、実行ディレクトリに `ollama_config.json` を保存・読み込みする仕組みを追加する。

---

## 設定ファイルの仕様

- **ファイル名:** `ollama_config.json`
- **保存場所:** 実行ファイル（`.exe`）またはスクリプトと同じディレクトリ
- **フォーマット:**

```json
{
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "mitmul/plamo-2-translate"
}
```

### ファイル状態ごとの挙動

| 状態 | 動作 |
|------|------|
| ファイルなし | デフォルト値で自動作成（失敗時はログ警告のみ） |
| ファイルあり・正常 | 読み込んで反映 |
| ファイルあり・壊れている | `config_corrupted` プロパティが `True` になる。UI起動・`page.update()` の後にダイアログ表示 |

---

## コンポーネント設計

### 1. `Config` クラスの変更（`src/utils/config.py`）

#### 内部状態

```python
self._config_corrupted: bool = False  # 壊れフラグ（外部はプロパティ経由）
```

#### 追加するメソッド・プロパティ

**`_config_file_path() -> Path`** (staticmethod)

実行環境に応じてJSONファイルのパスを返す。

- `sys.frozen` が `True`（Nuitkaでコンパイル済み）→ `Path(sys.executable).parent / "ollama_config.json"`
- それ以外（開発時）→ `Path(__file__).parent.parent.parent / "ollama_config.json"`
  （`config.py` は `src/utils/config.py` なので、3階層上がプロジェクトルート）

**`config_corrupted` プロパティ（読み取り専用）**

```python
@property
def config_corrupted(self) -> bool:
    return self._config_corrupted
```

**`load() -> None`**

JSONを読んで `_ollama_base_url` / `_ollama_model` を上書きする。`_config_corrupted` も更新する。

```
ファイルなし:
  → デフォルト値を維持
  → save() を呼び自動作成を試みる
  → save() が失敗した場合はログ警告のみ（UIエラーにしない）
  → _config_corrupted = False

ファイルあり・正常:
  → 値を読み込んで反映
  → _config_corrupted = False

ファイルあり・破損（JSONDecodeError 等）:
  → デフォルト値を維持
  → _config_corrupted = True
```

**`save() -> None`**

現在の `_ollama_base_url` と `_ollama_model` を `ollama_config.json` に書き出す。書き込みエラーはキャッチしてログに記録する（例外を呼び出し元に伝播させない）。

#### `__init__` の変更

```python
def __init__(self):
    self._pack_format: Optional[int] = None
    self._ollama_base_url: str = self.OLLAMA_DEFAULT_BASE_URL
    self._ollama_model: str = self.OLLAMA_DEFAULT_MODEL
    self._config_corrupted: bool = False
    self.load()  # 起動時に自動ロード
```

---

### 2. `MinecraftModTranslatorApp.initialize_ui`（`src/ui/app.py`）

`page.update()` の **後** に以下を追加：

```python
page.update()  # ← 既存行（UIを先にレンダリング）

if config.config_corrupted:
    self._show_corrupted_config_dialog(page)
```

ダイアログはページが描画された後に表示されるため、空白画面の上に出るという問題を防ぐ。

#### `_show_corrupted_config_dialog(page)` の新規追加

```
タイトル: 設定ファイルのエラー
本文:    設定ファイル (ollama_config.json) が壊れています。
         新しく作成しますか？（デフォルト値に戻ります）
ボタン:  [キャンセル]  [新規作成]
```

- 「新規作成」→ `config.save()` を呼んでデフォルト値で上書き → その後 `config.load()` を呼ぶことで `_config_corrupted` を内部でリセット（プライベート属性への直接アクセスを避ける）
- 「キャンセル」→ 何もしない（デフォルト値のまま動作継続）

---

### 3. 設定ダイアログの変更（`src/ui/components.py`）

`save_settings()` 内に `config.save()` を1行追加：

```python
def save_settings(e):
    ...
    config.OLLAMA_BASE_URL = url
    config.OLLAMA_MODEL = model
    config.save()          # ← 追加
    ...
```

---

## データフロー

```
アプリ起動
  └─ Config.__init__()
       └─ config.load()
            ├─ ファイルなし → save()で自動作成試行
            │                  └─ 失敗時はログ警告のみ
            │                _config_corrupted = False
            ├─ 正常        → 値を反映, _config_corrupted = False
            └─ 破損        → デフォルト維持, _config_corrupted = True

initialize_ui()
  └─ page.update()  ← UIを先にレンダリング
  └─ config.config_corrupted == True → ダイアログ表示
       ├─ 新規作成 → config.save() → config.load()（内部でフラグリセット）
       └─ キャンセル → 何もしない

設定ダイアログで保存
  └─ config.OLLAMA_BASE_URL = url
  └─ config.OLLAMA_MODEL = model
  └─ config.save()  → ollama_config.json に書き出し
```

---

## エラーハンドリング

- `load()` 内の例外はすべてキャッチしてログに記録、デフォルト値で継続
- `save()` 内の書き込みエラーはキャッチしてログに記録（呼び出し元に伝播しない）
- ファイルなしで `save()` が失敗した場合：次回起動時も「ファイルなし」として再試行される（無限サイレント失敗を防ぐためログ警告を必ず出力）
