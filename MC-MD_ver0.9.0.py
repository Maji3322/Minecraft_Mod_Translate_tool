import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar

import os
import zipfile
import shutil
import json

from googletrans import Translator

# Tkinterの初期化
root = tk.Tk()

# Google翻訳APIを使うための初期設定
translator = Translator()

# tempの初期化
def int_temp_dir():
    print("tempフォルダを初期化します。")
    # tempフォルダの中をすべて削除する
    for root, dirs, files in os.walk("temp"):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))

# translating_resourcepackの初期化
def int_translating_resourcepack_dir():
    print("translating_resourcepackフォルダを初期化します。")
    # translating_resourcepack\assetsより下のフォルダをすべて削除する(assetsフォルダは削除しない)
    for root, dirs, files in os.walk("translating_resourcepack\\assets"):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs: 
            shutil.rmtree(os.path.join(root, dir))

def remove_other_files(path):
    """指定したフォルダとその中身以外のファイルとフォルダを削除する"""

    for root, dirs, files in os.walk(path):
        for file in files:
            # langフォルダとその中身は削除しない
            if os.path.join(root, file) != os.path.join(root, "lang"):
                os.remove(os.path.join(root, file))
        for dir in dirs:
            # langフォルダは削除しない
            if dir != "lang":
                shutil.rmtree(os.path.join(root, dir))


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

def search_lang_file(path):
    # pathに渡されたフォルダの中からlangフォルダを探し、その中のen_us.jsonのパスを返す
    for root, dirs, files in os.walk(path):
        if "lang" in dirs:
            lang_path = os.path.join(root, "lang", "en_us.json")
            if os.path.exists(lang_path):
                return lang_path
    return None

def select_file():

    # ファイル選択ダイアログを表示
    fTyp = [(".jarファイル",".jar")]                                                     # ファイルの種類
    initialdir = "C:\\"                                                                # ファイル選択ダイアログの初期ディレクトリ
    global file_names
    file_names = filedialog.askopenfilenames(filetypes = fTyp, initialdir = initialdir)  # ファイル選択ダイアログを表示
    
    # 選択ファイル名をGUI上に表示(形式は"選択されたファイル名：(ファイル名)")
    for file_name in file_names:
        file_name_label = tk.Label(root, text="選択されたファイルのパス：" + file_name)
        file_name_label.pack()
    
    # 翻訳処理を実行
    for file_name in file_names:
        ready_translate(file_name)
        int_temp_dir() # tempフォルダを初期化
        # 最後のファイルの翻訳が完了したら、アプリを終了する
        if file_name == file_names[-1]:
            root.destroy()

    return file_names

def ready_translate(file_name):
    """
    この関数はtempfileを使用して選択されたjarファイルを抽出し、抽出されたファイルからlangフォルダを検索します、 
    既存の translating_resourcepack/assets フォルダにコピーし、コピーされたフォルダ内の en_us.json 以外のすべてのファイルを削除します、 
    そして、translating_resourcepack/assets/lang フォルダに en_us.json を翻訳する ja_jp.json ファイルを作成します。
    
    戻り値
    - なし
    """
    
    # 選択されたjarファイルをtempfileにzipfileを使って解凍する
    OpF = zipfile.ZipFile(file_name, "r")      # readモードでzipファイルを開く
    OpF.extractall("temp")                     # tempフォルダに解凍する
    
    with open(search_lang_file("temp"), "r+", encoding="utf-8") as f: # en_us.jsonを開く
        en_json = json.load(f) # en_us.jsonを読み込む
    
    # 解凍したjarファイルの中をサブフォルダーも含めて検索し、langフォルダを含むフォルダを既存のtranslating_resorcepack\assets内に複製する
    for root, dirs, files in os.walk("temp"):
        if "lang" in dirs:
            mod_name = os.path.basename(root)
            shutil.copytree(os.path.join(root), os.path.join("translating_resourcepack", "assets", mod_name))
    
    """ 本当は全部コピーするのではなくmod_nameのフォルダ名を取得して、そのフォルダの中のlangフォルダだけをコピーし、フォルダを作成した中にコピーするようにしたい """
    
    # translating_resourcepack\assets\langフォルダの中にあるファイルとフォルダ(langフォルダとen_us.jsonとja_jp.jsonを除く)ファイルをすべて削除する
    remove_other_files(os.path.join("translating_resourcepack", "assets", mod_name))
    
    # translating_resourcepack\assets\(mod_name)のフォルダ内の「langフォルダと、その中のファイルまたはフォルダ」以外のファイルとフォルダをすべて削除する
    for file in os.listdir(root):
        if not file.endswith(".json"):
            os.remove(os.path.join(root, file))

    for dir in os.listdir(root):
        if dir != "lang":
            shutil.rmtree(os.path.join(root, dir))
    
    
    # 翻訳を実行
    translate_json(file_name, mod_name)

def update_progress(root, value):
    """
    progressを更新する関数
    
    Args:
        root (tkinter.Tk): GUIのルートウィンドウ
        progress (tkinter.tk.Progressbar): アップデートするプログレスバー
        value (int): プログレスバーに新しく設定する値
    """
    progress["value"] = value
    root.update_idletasks()

def translate_json(file_name,mod_name):
    print(mod_name)
    """
    選択されたjarファイルからen_us.jsonを読み込み、Google翻訳APIを使用してja_jp.jsonを作成する関数
    翻訳の進捗状況を表示するために、update_progress関数を使用します。
    エラーが発生した場合は、Tkinterのウィンドウにエラーメッセージを表示します。
    """

    # en_us.jsonを開く
    with open(search_lang_file("temp"), "r+", encoding="utf-8") as f:
        en_json = json.load(f)

    # 翻訳を実行
    print("starting translation...")
    ja_json = {} # ja_jp.jsonを作成するための空の辞書を作成
    total_strings = sum(1 for _ in find_strings(en_json)) # en_us.jsonに含まれる文字列の数を数える
    translated_strings = 0 # 翻訳された文字列の数を数える

    for key, value in en_json.items(): # en_us.jsonの中身を走査
    
        if isinstance(value, str): # valueが文字列の場合
            print("en_us.jsonの中身が文字列です")
            try:
                result = translator.translate(value, dest="ja")
                ja_json[key] = result.text
                translated_strings += 1
                # UpdateProgress関数を呼び出してTkinterのProgressBarを更新
                n_value = translated_strings / total_strings * 100
                update_progress(root, n_value)
            
            # 翻訳エラーが発生した場合は、ja_jp.jsonにen_us.jsonの内容をそのまま書き込む
            except Exception as e:
                print(f"翻訳エラー: {e}")
                ja_json[key] = value
        
        elif isinstance(value, dict): # valueが辞書型の場合
            print("valueが文辞書型です")
            ja_dict = {} # ja_jp.jsonの中身を作成するための空の辞書を作成
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str):
                    try:
                        result = translator.translate(sub_value, dest="ja") # 翻訳を実行
                        ja_dict[sub_key] = result.text
                        translated_strings += 1
                        # UpdateProgress関数を呼び出してTkinterのProgressBarを更新
                        update_progress(root, translated_strings / total_strings * 100)
                    
                    # 翻訳エラーが発生した場合は、ja_jp.jsonにen_us.jsonの内容をそのまま書き込む
                    except Exception as e:
                        print(f"翻訳エラー: {e}")
                        ja_dict[sub_key] = sub_value
                else:
                    ja_dict[sub_key] = sub_value
            ja_json[key] = ja_dict
    
    # ja_jp.jsonを保存する
    with open(os.path.join("translating_resourcepack", "assets", mod_name, "lang", "ja_jp.json"), "w+", encoding="utf-8") as f:
        json.dump(ja_json, f, ensure_ascii=False, indent=4)

    print(f"{file_name}の翻訳が完了しました。")
    print("="*50) # 終了を示すために区切り線を表示
    # tkinterのウィンドウに翻訳完了を示すメッセージをポップアップ表示
    tk.messagebox.showinfo("翻訳完了", f"{file_name}の翻訳が完了しました。")

def before_screen():
    global gui1
    global selectFile_button
    gui1 = tk.Frame(root)
    gui1.pack()
    selectFile_button = tk.Button(root, text="翻訳するMODのjarファイルを選択", command=lambda:select_file(), width=50, height=5)
    selectFile_button.pack()


def after_screen():
    selectFile_button.destroy()
    gui2 = tk.Frame(root)
    gui2.pack()
    # 翻訳ボタンを表示
    translate_button = tk.Button(root, text="翻訳", command=lambda:ready_translate(), width=50, height=5)
    translate_button.pack()
    # プログレスバーを表示
    global progress
    progress = Progressbar(root, orient='horizontal', mode='determinate', length=500, value=0, maximum=100)
    progress.pack()



def main():
    # tempフォルダを初期化
    int_temp_dir()
    # translating_resourcepackフォルダを初期化
    int_translating_resourcepack_dir()
    # tkinterのウィンドウを作成
    root.title("マインクラフトJava版MOD翻訳ツール")
    root.geometry("600x400")
    root.resizable(0, 0)
    
    # progress変数を初期化
    global progress
    progress = Progressbar(root, orient='horizontal', mode='determinate', length=500, value=0, maximum=100)
    progress.pack()

    
    before_screen()

    # メインループを開始
    root.mainloop()

if __name__ == "__main__":

    main()