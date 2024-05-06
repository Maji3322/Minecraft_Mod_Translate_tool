import json, tqdm, flet as ft, time
from venv import logger
import gui_module
from googletrans import Translator
from concurrent.futures import ThreadPoolExecutor

completed_translations = []

def translate_json(lang_file_path, page):
    """
    渡されたjsonファイルを翻訳し、ja_jp.jsonとして同階層に保存する関数。
    Args:
        lang_file_path (str): 翻訳するjsonファイルのパス
    """
    
    
    

    # 翻訳開始時刻を記録
    start_time = time.time()
    try:
        translator = Translator()
        
        logger.info("="*20)
        logger.info(f"LOG: {lang_file_path}の翻訳を開始します。")
        logger.info("="*20)
        
        print(f"LOG: {lang_file_path}の翻訳を開始します。")

        with open(lang_file_path, "r+", encoding="utf-8") as f: # それぞれの引数には、①ファイルのパス、②読み込みモード、③文字コードを指定
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

            # 翻訳事前準備
            ja_json = {}  # ja_jp.jsonを作成するための空の辞書を作成
            total_strings = sum(1 for _ in find_strings(en_json)) # en_us.jsonに含まれる文字列の数を数える
            progressbar, info_msg = gui_module.make_progress_bar(page, lang_file_path) # info_msgはプログレスバーの下に表示されるメッセージ

            translated_strings = 0  # 翻訳された文字列の数を数える
            # gui_module.make_progress_bar(page,total_strings)  # プログレスバーを作成
            # ターミナル用のプログレスバーを表示
            pbar = tqdm.tqdm(total=total_strings, position=0, leave=True)
            pbar.update(0)

            # 翻訳開始時間を記録

            # 残り時間を表示するラベルを作成
            # en_us.jsonの中身を走査して翻訳を実行
            for key, value in en_json.items():  # en_us.jsonの中身を走査

                if isinstance(value, str):  # valueが文字列の場合

                    try:
                        result = translator.translate(value, dest="ja")
                        ja_json[key] = result.text
                        translated_strings += 1
                        # ProgressBarをインクリメント
                        gui_module.progress_bar_update(progressbar, translated_strings, total_strings, info_msg, page, start_time)
                        
                        pbar.update(1)

                        # 残り時間を計算して表示

                    # 翻訳エラーが発生した場合は、ja_jp.jsonにen_us.jsonの内容をそのまま書き込む
                    except Exception as e:
                        logger.error(f"ERROR: translation error >> {e}")
                        ja_json[key] = value

                elif isinstance(value, dict):  # valueが辞書型の場合
                    ja_dict = {}  # ja_jp.jsonの中身を作成するための空の辞書を作成
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str):
                            try:
                                result = translator.translate(sub_value, dest="ja")  # 翻訳を実行
                                ja_dict[sub_key] = result.text
                                translated_strings += 1
                                # UpdateProgress関数を呼び出してTkinterのProgressBarを更新
                                pbar.update(1)

                                # 残り時間を計算して表示

                            # 翻訳エラーが発生した場合は、ja_jp.jsonにen_us.jsonの内容をそのまま書き込む
                            except Exception as e:
                                logger.error(f"ERROR: translation error >> {e}")
                                ja_dict[sub_key] = sub_value
                        else:
                            ja_dict[sub_key] = sub_value
                    ja_json[key] = ja_dict

            # ja_jp.jsonを保存する(file_pathのディレクトリにja_jp.jsonとして保存)
            with open(lang_file_path.replace("en_us.json", "ja_jp.json"), "w", encoding="utf-8") as f:
                json.dump(ja_json, f, indent=4, ensure_ascii=False)
            
            logger.info(f"LOG: {lang_file_path}の翻訳が完了しました。")
            logger.info("="*20)  # 終了を示すために区切り線を表示
            info_msg.value = f"翻訳が完了しました。"
            
            
            return 0
    except Exception as e:
        logger.error(f"ERROR: {lang_file_path}の翻訳に失敗しました。")
        logger.error(f"ERROR: {e}")
        print(f"ERROR: {lang_file_path}の翻訳に失敗しました。")
        print(f"ERROR: {e}")
        gui_module.err_dlg(page, "エラー",f"{lang_file_path}の翻訳に失敗しました。")
        return 1

def translate_in_thread(lang_file_paths, page):
    """
    マルチスレッドで翻訳を実行する関数
    """
    if lang_file_paths == "No lang folder":
        logger.error("ERROR: langフォルダが見つからなかったので、翻訳をスキップします。")
        gui_module.err_dlg(page, "エラー","langフォルダが見つからなかったので、翻訳をスキップします。")
        return
    elif lang_file_paths == "exist ja_jp.json":
        logger.info("LOG: ja_jp.jsonが見つかったので、翻訳をスキップします。")
        gui_module.err_dlg(page, "エラー","ja_jp.jsonが見つかったので、翻訳をスキップします。")
        return
    else:
        logger.info("LOG: en_us.jsonが見つかり、ja_jp.jsonがないため翻訳を開始します。")
        print(f"成功!{lang_file_paths}")
        
    with ThreadPoolExecutor() as executor:
        # 引数として、translate_json関数に渡すjsonファイルのパスと、pageを渡す
        results = executor.map(translate_json, lang_file_paths, [page]*len(lang_file_paths))
        for result in results:
            if result == 0:
                logger.info("LOG: 翻訳が完了しました。")
            else:
                logger.error("ERROR: 翻訳に失敗しました。")
                gui_module.err_dlg(page, "エラー","翻訳に失敗しました。")
                return
    # 全ての翻訳が終わったことを表示
    logger.info("LOG: 全ての翻訳が完了しました。")
    
    # 翻訳が完了したことを示すメッセージを表示
    gui_module.err_dlg(page, "完了","全ての翻訳が完了しました。")
    
    # メインスレッド以外を終了
    ThreadPoolExecutor().shutdown(wait=True)
    return 0





if __name__ == "__main__":
    ft.app(target=translate_json("test.json"))
    