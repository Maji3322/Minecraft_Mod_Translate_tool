import os
import json
import zipfile
from googletrans import Translator

# Google翻訳APIを使うための初期設定
translator = Translator()

# en_jsonに含まれるすべての文字列をジェネレーターとして返す関数
def find_strings(data):
    if isinstance(data, str):
        yield data
    elif isinstance(data, dict):
        for value in data.values():
            yield from find_strings(value)
    elif isinstance(data, list):
        for item in data:
            yield from find_strings(item)

# MODフォルダのパス
mod_folder = os.path.join(os.getcwd(), "mods")

for file_name in os.listdir(mod_folder):
    if file_name.endswith(".jar"):
        # MODファイルのパス
        mod_file_path = os.path.join(mod_folder, file_name)

        # en_us.jsonのパス
        en_us_json_path = ""

        # MODファイルを展開してen_us.jsonのパスを取得
        with zipfile.ZipFile(mod_file_path, "r") as mod_file:
            for name in mod_file.namelist():
                if name.endswith("en_us.json"):
                    en_us_json_path = name
                    break

            if not en_us_json_path:
                print("en_us.jsonが見つかりませんでした。")
                exit()

            # en_us.jsonを読み込む
            with mod_file.open(en_us_json_path, "r") as en_file:
                en_json = json.loads(en_file.read().decode("utf-8"))

            # 翻訳を実行
            ja_json = {}
            total_strings = sum(1 for _ in find_strings(en_json))
            translated_strings = 0
            for key, value in en_json.items():
                if isinstance(value, str):
                    try:
                        result = translator.translate(value, dest="ja")
                        ja_json[key] = result.text
                        translated_strings += 1
                        print(f"{file_name}: {translated_strings}/{total_strings} ({translated_strings/total_strings*100:.1f}%)")
                    # Keep the original text if translation fails
                    except Exception as e:
                        print(f"翻訳エラー: {e}")
                        ja_json[key] = value
                elif isinstance(value, dict):
                    ja_dict = {}
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str):
                            result = translator.translate(sub_value, dest="ja")
                            ja_dict[sub_key] = result.text
                            translated_strings += 1
                            print(f"{file_name}: {translated_strings}/{total_strings} ({translated_strings/total_strings*100:.1f}%)")
                        else:
                            ja_dict[sub_key] = sub_value
                    ja_json[key] = ja_dict
                else:
                    ja_json[key] = value

            # ja_jp.jsonを出力
            ja_jp_json_path = os.path.join(*os.path.split(en_us_json_path)[:-1], "ja_jp.json")
            with zipfile.ZipFile(mod_file_path, mode='a') as mod_file:
                mod_file.writestr(ja_jp_json_path, json.dumps(ja_json, ensure_ascii=False, indent=4))

            print(f"{file_name}の翻訳が完了しました。")
            print("="*50)

else:
    print("MODが見つかりませんでした。")