# Ollama設定のJSON永続化 実装計画

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** アプリ再起動後もOllama設定（URLとモデル名）が保持されるよう、`ollama_config.json` への読み書きを実装する。

**Architecture:** `Config` クラスに `load()`/`save()` を追加して起動時に自動ロード。設定ダイアログ保存時に `config.save()` を呼ぶ。ファイル破損時は `config_corrupted` フラグ経由でUIダイアログを表示する。

**Tech Stack:** Python 3.x, Flet (UI), `pathlib.Path`, `json`, `unittest` + `unittest.mock`

> **注意:** `Config.__init__` に `self.load()` を追加すると、モジュールレベルの `config = Config()` が import 時に `load()` を実行する。これは意図された動作で、`load()` は例外を出さず、ファイルがなければプロジェクトルートに `ollama_config.json` を生成する。テストでは `Config()` を生成する前に `_config_file_path` をパッチし、実ファイルシステムへの影響を分離する。

---

## Chunk 1: Config クラスへの load/save 追加

### Task 1: `_config_file_path()` のテストと実装

**Files:**
- Modify: `tests/test_config.py`
- Modify: `src/utils/config.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_config.py` の冒頭 `import` に追加：

```python
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
```

その後、テストクラスを追加：

```python
class ConfigFilePathTests(unittest.TestCase):
    """Tests for _config_file_path static method."""

    def test_frozen_uses_executable_dir(self):
        """In frozen (compiled) mode, config file is next to the executable."""
        fake_exe = str(Path('C:/app/dist/app.exe'))
        with patch.object(sys, 'frozen', True, create=True), \
             patch.object(sys, 'executable', fake_exe):
            path = Config._config_file_path()
        expected = Path('C:/app/dist') / 'ollama_config.json'
        self.assertEqual(path, expected)

    def test_dev_mode_uses_project_root(self):
        """In dev mode, config file is at the project root (3 levels above config.py)."""
        # Ensure sys.frozen is not set
        with patch('sys.frozen', False, create=True):
            path = Config._config_file_path()
        # tests/test_config.py → parent = tests/ → parent = project root
        expected = Path(__file__).parent.parent / 'ollama_config.json'
        self.assertEqual(path, expected)
```

- [ ] **Step 2: テストが失敗することを確認**

```
python -m pytest tests/test_config.py::ConfigFilePathTests -v
```

Expected: `AttributeError: type object 'Config' has no attribute '_config_file_path'`

- [ ] **Step 3: `_config_file_path()` を実装する**

`src/utils/config.py` の `import` セクション（ファイル冒頭）に追加：

```python
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
```

`Config` クラスに追加（`VERSION_TO_PACK_FORMAT` の後あたり）：

```python
@staticmethod
def _config_file_path() -> Path:
    """Return the path to the JSON config file.

    In frozen (compiled) mode: next to the executable.
    In dev mode: at the project root (3 levels above this file).
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / 'ollama_config.json'
    return Path(__file__).parent.parent.parent / 'ollama_config.json'
```

- [ ] **Step 4: テストが通ることを確認**

```
python -m pytest tests/test_config.py::ConfigFilePathTests -v
```

Expected: PASS

- [ ] **Step 5: コミット**

```
git add src/utils/config.py tests/test_config.py
git commit -m "feat: add Config._config_file_path() static method"
```

---

### Task 2: `save()` のテストと実装

**Files:**
- Modify: `tests/test_config.py`
- Modify: `src/utils/config.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_config.py` に追加：

```python
class ConfigSaveTests(unittest.TestCase):
    """Tests for Config.save()."""

    def test_save_writes_url_and_model(self):
        """save() writes current URL and model to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            # Patch before Config() so __init__'s load() also uses the temp path
            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()
                cfg.OLLAMA_BASE_URL = 'http://example.com:11434'
                cfg.OLLAMA_MODEL = 'my-model'
                cfg.save()

            data = json.loads(config_path.read_text(encoding='utf-8'))

        self.assertEqual(data['ollama_base_url'], 'http://example.com:11434')
        self.assertEqual(data['ollama_model'], 'my-model')

    def test_save_does_not_raise_on_write_error(self):
        """save() logs a warning but does not raise if write fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()
            # Now point to an unwritable location
            with patch.object(Config, '_config_file_path', lambda self=None: Path('/nonexistent/dir/config.json')):
                cfg.save()  # Should not raise
```

- [ ] **Step 2: テストが失敗することを確認**

```
python -m pytest tests/test_config.py::ConfigSaveTests -v
```

Expected: `AttributeError: 'Config' object has no attribute 'save'`

- [ ] **Step 3: `save()` を実装する**

`src/utils/config.py` の `Config` クラスに追加：

```python
def save(self) -> None:
    """Write current Ollama settings to ollama_config.json."""
    path = self._config_file_path()
    try:
        data = {
            'ollama_base_url': self._ollama_base_url,
            'ollama_model': self._ollama_model,
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved Ollama config to {path}")
    except Exception as e:
        logger.warning(f"Failed to save Ollama config to {path}: {e}")
```

- [ ] **Step 4: テストが通ることを確認**

```
python -m pytest tests/test_config.py::ConfigSaveTests -v
```

Expected: PASS

- [ ] **Step 5: コミット**

```
git add src/utils/config.py tests/test_config.py
git commit -m "feat: add Config.save() for persisting Ollama settings"
```

---

### Task 3: `load()` と `config_corrupted` プロパティのテストと実装

**Files:**
- Modify: `tests/test_config.py`
- Modify: `src/utils/config.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_config.py` に追加：

```python
class ConfigLoadTests(unittest.TestCase):
    """Tests for Config.load()."""

    def test_load_reads_url_and_model(self):
        """load() sets URL and model from valid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            config_path.write_text(json.dumps({
                'ollama_base_url': 'http://remote:11434',
                'ollama_model': 'custom-model',
            }), encoding='utf-8')

            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()

        self.assertEqual(cfg.OLLAMA_BASE_URL, 'http://remote:11434')
        self.assertEqual(cfg.OLLAMA_MODEL, 'custom-model')
        self.assertFalse(cfg.config_corrupted)

    def test_load_creates_file_when_missing(self):
        """load() auto-creates ollama_config.json with defaults when file is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            # Patch before Config() so both __init__'s load() and save() use temp path
            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()

            self.assertTrue(config_path.exists())
            data = json.loads(config_path.read_text(encoding='utf-8'))

        self.assertEqual(data['ollama_base_url'], Config.OLLAMA_DEFAULT_BASE_URL)
        self.assertEqual(data['ollama_model'], Config.OLLAMA_DEFAULT_MODEL)
        self.assertFalse(cfg.config_corrupted)

    def test_load_sets_corrupted_flag_on_bad_json(self):
        """load() sets config_corrupted=True and keeps defaults when JSON is invalid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            config_path.write_text('{ not valid json', encoding='utf-8')

            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()

        self.assertTrue(cfg.config_corrupted)
        self.assertEqual(cfg.OLLAMA_BASE_URL, Config.OLLAMA_DEFAULT_BASE_URL)
        self.assertEqual(cfg.OLLAMA_MODEL, Config.OLLAMA_DEFAULT_MODEL)

    def test_config_corrupted_is_false_by_default(self):
        """config_corrupted is False on a fresh Config with a missing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()
        self.assertFalse(cfg.config_corrupted)
```

- [ ] **Step 2: テストが失敗することを確認**

```
python -m pytest tests/test_config.py::ConfigLoadTests -v
```

Expected: `AttributeError: 'Config' object has no attribute 'load'`

- [ ] **Step 3: 既存テスト `ConfigVersionTests` を更新する**

`__init__` に `self.load()` を加えると、既存の `test_get_app_version_uses_package_metadata` も実ファイルシステムに触れるようになる。`tests/test_config.py` の既存テストを以下に差し替え：

```python
class ConfigVersionTests(unittest.TestCase):
    """Tests for version-related configuration behavior."""

    def test_get_app_version_uses_package_metadata(self):
        """The app version should come from package metadata, not pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()
        self.assertEqual(cfg.get_app_version(), __version__)
```

- [ ] **Step 4: `load()`・`config_corrupted` プロパティ・`__init__` 変更を実装する**

`src/utils/config.py` の `Config.__init__` を以下に更新：

```python
def __init__(self):
    """Initialize configuration with default values."""
    self._pack_format: Optional[int] = None
    self._ollama_base_url: str = self.OLLAMA_DEFAULT_BASE_URL
    self._ollama_model: str = self.OLLAMA_DEFAULT_MODEL
    self._config_corrupted: bool = False
    self.load()
```

`config_corrupted` プロパティを追加：

```python
@property
def config_corrupted(self) -> bool:
    """True if the config file was found but could not be parsed."""
    return self._config_corrupted
```

`load()` を追加：

```python
def load(self) -> None:
    """Load Ollama settings from ollama_config.json.

    - File missing: auto-create with defaults (save failure is logged, not raised).
    - File valid: apply stored values.
    - File corrupted: keep defaults, set config_corrupted=True.
    """
    path = self._config_file_path()
    self._config_corrupted = False

    if not path.exists():
        logger.info(f"Config file not found at {path}. Creating with defaults.")
        self.save()
        return

    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        self._ollama_base_url = data.get('ollama_base_url', self.OLLAMA_DEFAULT_BASE_URL)
        self._ollama_model = data.get('ollama_model', self.OLLAMA_DEFAULT_MODEL)
        logger.info(f"Loaded Ollama config from {path}")
    except Exception as e:
        logger.warning(f"Failed to parse Ollama config at {path}: {e}")
        self._config_corrupted = True
```

- [ ] **Step 5: テストが通ることを確認**

```
python -m pytest tests/test_config.py -v
```

Expected: すべて PASS

- [ ] **Step 6: コミット**

```
git add src/utils/config.py tests/test_config.py
git commit -m "feat: add Config.load() and config_corrupted property for JSON persistence"
```

---

## Chunk 2: UI 側の変更

### Task 4: `app.py` に破損ダイアログを追加

**Files:**
- Modify: `src/ui/app.py`

- [ ] **Step 1: `_show_corrupted_config_dialog()` メソッドを追加する**

`src/ui/app.py` の `MinecraftModTranslatorApp` クラスに追加（`_show_settings_dialog` の直後）：

```python
def _show_corrupted_config_dialog(self, page: ft.Page) -> None:
    """Show a dialog when ollama_config.json is corrupted.

    Args:
        page: The page to show the dialog on.
    """
    def recreate(e):
        page.pop_dialog()
        config.save()
        config.load()
        logger.info("Recreated corrupted ollama_config.json with defaults")

    def cancel(e):
        page.pop_dialog()

    dialog = ft.AlertDialog(
        title=ft.Text("設定ファイルのエラー"),
        content=ft.Text(
            "設定ファイル (ollama_config.json) が壊れています。\n"
            "新しく作成しますか？（デフォルト値に戻ります）"
        ),
        actions=[
            ft.TextButton("キャンセル", on_click=cancel),
            ft.ElevatedButton("新規作成", on_click=recreate),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        modal=True,
    )
    page.show_dialog(dialog)
```

- [ ] **Step 2: `initialize_ui()` の末尾に破損チェックを追加する**

`src/ui/app.py` の `initialize_ui()` 内、既存の `page.update()` の **後** に追加：

```python
        # Update the page
        page.update()

        # Show dialog if config file was corrupted on startup
        if config.config_corrupted:
            self._show_corrupted_config_dialog(page)
```

- [ ] **Step 3: アプリを起動して動作確認**

通常起動でダイアログが出ないことを確認：

```
python -m src.main
```

破損ファイルのテスト：プロジェクトルートの `ollama_config.json` を `{ invalid` に書き換えてから再起動。ダイアログが表示されること、「新規作成」を押すと正常なJSONが生成されることを確認。

- [ ] **Step 4: コミット**

```
git add src/ui/app.py
git commit -m "feat: show dialog when ollama_config.json is corrupted on startup"
```

---

### Task 5: `components.py` の `save_settings()` に `config.save()` を追加

**Files:**
- Modify: `src/ui/components.py`

- [ ] **Step 1: `save_settings()` 内に `config.save()` を追加する**

`src/ui/components.py` の `show_ollama_settings_dialog()` 内の `save_settings()` を修正：

```python
    def save_settings(e):
        url = url_field.value.strip() if url_field.value else ""
        model = model_field.value.strip() if model_field.value else ""
        if not url:
            show_error_dialog(page, "エラー", "サーバー URL を入力してください")
            return
        if not model:
            show_error_dialog(page, "エラー", "モデル名を入力してください")
            return
        url_changed = config.OLLAMA_BASE_URL != url
        config.OLLAMA_BASE_URL = url
        config.OLLAMA_MODEL = model
        config.save()          # ← 追加：設定をJSONに永続化
        if url_changed:
            reset_ollama_client()
        page.pop_dialog()
        on_save()
```

- [ ] **Step 2: 手動動作確認**

アプリを起動 → 設定ダイアログを開く → URLとモデルを変更して保存 → アプリを再起動 → 設定が保持されていることを確認。

- [ ] **Step 3: コミット**

```
git add src/ui/components.py
git commit -m "feat: persist Ollama settings to JSON when saved from dialog"
```

---

## 完了確認

- [ ] `python -m pytest tests/test_config.py -v` がすべて PASS
- [ ] 初回起動で `ollama_config.json` が自動生成される
- [ ] 設定ダイアログで保存するとJSONが更新される
- [ ] 再起動後も設定値が保持される
- [ ] `ollama_config.json` を壊した状態で起動するとダイアログが表示される
