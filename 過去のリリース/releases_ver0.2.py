import os
import json
import zipfile
from googletrans import Translator

# Google翻訳APIを使うための初期設定
translator = Translator()

# MODフォルダのパス
mod_folder = os.path.join(os.getcwd(), "mods")

# MODフォルダ内のすべてのMODを検索
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
                print(f"{mod_file_path}内にen_us.jsonが見つかりませんでした。")
                continue

            # en_us.jsonを読み込む
            with mod_file.open(en_us_json_path, "r") as en_file:
                en_json = json.loads(en_file.read().decode("utf-8"))

            # 翻訳を実行
            ja_json = {}
            for key, value in en_json.items():
                if isinstance(value, str):
                    result = translator.translate(value, dest="ja")
                    ja_json[key] = result.text
                elif isinstance(value, dict):
                    ja_dict = {}
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str):
                            result = translator.translate(sub_value, dest="ja")
                            ja_dict[sub_key] = result.text
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

print("すべてのMODの翻訳が完了しました。")
