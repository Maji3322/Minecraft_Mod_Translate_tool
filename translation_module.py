import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from venv import logger

import httpcore
import tqdm
from googletrans import Translator

import gui_module

completed_translations = []


def retry_on_timeout(max_retries=3, base_delay=2):
    """
    タイムアウトエラーが発生した場合に指数バックオフでリトライする装飾子

    Args:
        max_retries: 最大リトライ回数
        base_delay: 基本待機時間（秒）
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except httpcore._exceptions.ReadTimeout as e:
                    retries += 1
                    if retries > max_retries:
                        raise
                    # 指数バックオフ + ランダム要素を加える（ジッター）
                    delay = base_delay * (2 ** (retries - 1)) + random.uniform(0, 1)
                    print(
                        f"翻訳タイムアウト、{delay:.2f}秒後に{retries}回目のリトライ..."
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


@retry_on_timeout(max_retries=5, base_delay=3)
def translate_with_retry(translator, text, dest="ja"):
    """
    リトライ機能付きの翻訳関数

    Args:
        translator: Translatorインスタンス
        text: 翻訳するテキスト
        dest: 翻訳先言語
    Returns:
        翻訳結果
    """
    return translator.translate(text, dest=dest)


def translate_json(lang_file_path, page):
    """
    渡されたjsonファイルを翻訳し、ja_jp.jsonとして同階層に保存する関数。
    Args:
        lang_file_path (str): 翻訳するjsonファイルのパス
    """

    start_time = time.time()
    try:
        translator = Translator()

        logger.info("=" * 20)
        logger.info("%sの翻訳を開始します。", lang_file_path)
        logger.info("=" * 20)
        print(f"LOG: {lang_file_path}の翻訳を開始します。")

        with open(lang_file_path, "r+", encoding="utf-8") as f:

            def find_strings(json_data):
                """
                JSONデータ内の文字列を再帰的に検索して返す関数。
                Args:
                    json_data (dict): 検索対象のJSONデータ
                Returns:
                    generator: JSONデータ内の文字列を返すジェネレータ
                """
                for value in json_data.values():
                    if isinstance(value, str):
                        yield value
                    elif isinstance(value, dict):
                        yield from find_strings(value)

            en_json = json.load(f)
            ja_json = {}
            total_strings = sum(1 for _ in find_strings(en_json))

            progressbar, info_msg = gui_module.make_progress_bar(page, lang_file_path)
            translated_strings = 0
            pbar = tqdm.tqdm(total=total_strings, position=0, leave=True)
            pbar.update(0)

            for key, value in en_json.items():
                if isinstance(value, str):
                    try:
                        result = translate_with_retry(translator, value, dest="ja")
                        # TODO:いつかここに専用辞書を配備したい
                        # Google翻訳では半角記号が全角記号に変換されてしまうことがあるため、カラースキーマのために置換。
                        result.text = result.text.replace("％", " %").replace("$ ", "$")
                        ja_json[key] = result.text
                        translated_strings += 1
                        gui_module.progress_bar_update(
                            progressbar,
                            translated_strings,
                            total_strings,
                            info_msg,
                            page,
                            start_time,
                        )
                        pbar.update(1)
                    except Exception as e:
                        logger.error(
                            f"Error translating {lang_file_path}: {e}", exc_info=True
                        )
                        gui_module.err_dlg(
                            page, "エラー", f"{lang_file_path}の翻訳に失敗しました。"
                        )
                        raise RuntimeError("翻訳エラーが発生しました。") from e
                elif isinstance(value, dict):
                    ja_dict = {}
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str):
                            try:
                                result = translate_with_retry(
                                    translator, sub_value, dest="ja"
                                )
                                ja_dict[sub_key] = result.text
                                translated_strings += 1
                                pbar.update(1)
                            except Exception as e:
                                logger.error(
                                    f"Error translating {lang_file_path}: {e}",
                                    exc_info=True,
                                )
                                gui_module.err_dlg(
                                    page,
                                    "エラー",
                                    f"{lang_file_path}の翻訳に失敗しました。",
                                )
                                raise RuntimeError("翻訳エラーが発生しました。") from e
                        else:
                            ja_dict[sub_key] = sub_value
                    ja_json[key] = ja_dict

            with open(
                lang_file_path.replace("en_us.json", "ja_jp.json"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(ja_json, f, indent=4, ensure_ascii=False)

            logger.info("%sの翻訳が完了しました。", lang_file_path)
            logger.info("=" * 20)
            info_msg.value = (
                f"完了：{translated_strings}/{total_strings}箇所を翻訳しました。"
            )
            return 0
    except (json.JSONDecodeError, IOError, RuntimeError) as e:
        logger.error(f"Error translating {lang_file_path}: {e}", exc_info=True)
        gui_module.err_dlg(page, "エラー", f"{lang_file_path}の翻訳に失敗しました。")
        return 1


def translate_in_thread(lang_file_paths, page):
    """
    マルチスレッドで翻訳を実行する関数
    """
    if lang_file_paths == "No lang folder":
        logger.error(
            "ERROR: langフォルダが見つからなかったので、翻訳をスキップします。"
        )
        gui_module.err_dlg(
            page, "エラー", "langフォルダが見つからなかったので、翻訳をスキップします。"
        )
        return
    elif lang_file_paths == "exist ja_jp.json":
        logger.info("ja_jp.jsonが見つかったので、翻訳をスキップします。")
        gui_module.err_dlg(
            page, "エラー", "ja_jp.jsonが見つかったので、翻訳をスキップします。"
        )
        return
    else:
        logger.info("en_us.jsonが見つかり、ja_jp.jsonがないため翻訳を開始します。")
        print(f"成功!{lang_file_paths}")

    with ThreadPoolExecutor() as executor:
        # 引数として、translate_json関数に渡すjsonファイルのパスと、pageを渡す
        results = executor.map(
            translate_json, lang_file_paths, [page] * len(lang_file_paths)
        )
        for result in results:
            if result == 0:
                logger.info("翻訳が完了しました。")
            else:
                logger.error("翻訳に失敗しました。")
                gui_module.err_dlg(page, "エラー", "翻訳に失敗しました。")
                return
    # 全ての翻訳が終わったことを表示
    logger.info("全ての翻訳が完了しました。")

    # 翻訳が完了したことを示すメッセージを表示
    gui_module.err_dlg(page, "完了", "全ての翻訳が完了しました。")

    # メインスレッド以外を終了
    ThreadPoolExecutor().shutdown(wait=True)
    return 0
