import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
from tkinter import ttk
from plyer import notification

import os, zipfile, shutil, json
from googletrans import Translator

# Tkinterの初期化
root = tk.Tk()

# Google翻訳APIを使うための初期設定
translator = Translator()

def int_temp_dir():
    """
    tempフォルダを初期化する関数
    """
    root = os.path.dirname(os.path.abspath(__file__))
    dir = "temp"
    temp_dir = os.path.join(root, dir)
    if os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)
    else:
        os.mkdir(temp_dir)

def int_translating_resourcepack_dir():
    """
    'translating_resourcepack' フォルダを削除する。
    """
    print("translating_resourcepackフォルダを削除します。")
    if os.path.exists("translating_resourcepack"):
        shutil.rmtree("translating_resourcepack")

def generate_translating_resourcepack_dir():
    """ 
    translating_resourcepackフォルダを生成し、中にpack.mcmetaとassetsを作成する関数です。
    """
    # 現在の階層にtranslating_resourcepackフォルダを生成
    if not os.path.exists("translating_resourcepack"):
        os.mkdir("translating_resourcepack")
        print("translating_resourcepackフォルダを生成しました。")
    
    # translating_resourcepack\pack.mcmetaを生成
    if not os.path.exists(os.path.join("translating_resourcepack", "pack.mcmeta")): # pack.mcmetaが存在しない場合
        with open(os.path.join("translating_resourcepack", "pack.mcmeta"), "w+") as f: # pack.mcmetaを作成
            if pack_format != "":
                f.write('''{
        "pack": {
            "pack_format": %s,
            "description": "This is a translating resource pack."
        }
}''' % str(pack_format))
            else:
                tk.messagebox.showinfo("エラー","バージョンを選択してください。")
                main()
        print("translating_resourcepack\\pack.mcmetaを生成しました。")

    # translating_resourcepack\assetsを生成
    if not os.path.exists(os.path.join("translating_resourcepack", "assets")):
        os.mkdir(os.path.join("translating_resourcepack", "assets"))
        print("translating_resourcepack\\assetsを生成しました。")

def remove_other_files(path):
    """
    指定したフォルダとその中身以外のファイルとフォルダを削除する

    Args:
        path (str): 削除するフォルダのパス

    Returns:
        None
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            # langフォルダとその中身は削除しない
            if os.path.join(root, file) != os.path.join(root, "lang"):
                os.remove(os.path.join(root, file))
        for dir in dirs:
            # langフォルダは削除しない
            if dir != "lang":
                shutil.rmtree(os.path.join(root, dir))

def find_strings(data):
    """
    引数として渡されたデータから、文字列を抽出して返すジェネレーター関数です。

    Args:
        data: 文字列を抽出する対象のデータ。辞書、リスト、文字列のいずれかを指定します。

    Yields:
        dataから抽出された文字列。
    """
    if isinstance(data, str):
        yield data
    elif isinstance(data, dict):
        for value in data.values():
            yield from find_strings(value)
    elif isinstance(data, list):
        for item in data:
            yield from find_strings(item)

def search_lang_file(path):
    """
    指定されたパスからlangフォルダを探し、その中にあるen_us.jsonファイルのパスを返します。

    Args:
    path (str): 検索を開始するフォルダのパス

    Returns:
    str: en_us.jsonファイルのパス。見つからない場合はNoneを返します。
    """
    for root, dirs, files in os.walk(path):
        if "lang" in dirs:
            # langフォルダにja_jp.jsonが無いときはen_us.jsonのパスをlang_pathに代入
            if not os.path.exists(os.path.join(root, "lang", "ja_jp.json")):
                
                if os.path.exists(os.path.join(root, "lang", "en_us.json")):  # en_us.jsonが存在する場合
                    lang_path = os.path.join(root, "lang", "en_us.json")
                    print("en_us.jsonが見つかったので、翻訳を開始します。")
                    return lang_path
                
                else:  # en_us.jsonが存在しない場合
                    print("en_us.jsonが見つからなかったので、翻訳をスキップします。")
                    return "No en_us.json"
                
            # langフォルダにja_jp.jsonがあるときは何もせずに関数を終了
            else:
                print("ja_jp.jsonが見つかったので、翻訳をスキップします。")
                return "exist ja_jp.json"
    print("langフォルダが見つからなかったので、翻訳をスキップします。")
    return "No lang folder"

def select_file():
    """
    ファイル選択ダイアログを表示し、選択されたファイルのパスをGUI上に表示する。
    選択されたファイルに対して、ready_translate関数を実行し、翻訳処理を行う。
    翻訳処理が完了したら、tempフォルダを初期化し、最後のファイルの翻訳が完了したら、アプリを終了する。

    Returns:
        選択されたファイルのパスのリスト
    """
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
    tempfileを使用して選択されたjarファイルを抽出し、抽出されたファイルからlangフォルダを検索します。
    既存の translating_resourcepack/assets フォルダにコピーし、コピーされたフォルダ内の en_us.json 以外のすべてのファイルを削除します。
    そして、translating_resourcepack/assets/lang フォルダに en_us.json を翻訳する ja_jp.json ファイルを作成します。
    
    戻り値
    - なし
    """
    
    # 選択されたjarファイルをtempfileにzipfileを使って解凍する
    OpF = zipfile.ZipFile(file_name, "r")      # readモードでzipファイルを開く
    OpF.extractall("temp")                     # tempフォルダに解凍する
    
    if search_lang_file("temp") == "No en_us.json": # en_us.jsonが見つからなかった場合
        # plyerのnotificationを使ってエラーを通知
        notification.notify(
            title="エラー",
            message=f"{file_name}のen_us.jsonが見つかりませんでした。",
            app_name="MC-MOD Translating tool",
            app_icon="resources/icon.ico"
        )
        # 次のファイルの翻訳処理を開始
        return
    
    if search_lang_file("temp") == "No lang folder": # langフォルダが見つからなかった場合
        # plyerのnotificationを使ってエラーを通知
        notification.notify(
            title="エラー",
            message=f"{file_name}のlangフォルダが見つかりませんでした。",
            app_name="MC-MOD Translating tool",
            app_icon="resources/icon.ico"
        )
        # 次のファイルの翻訳処理を開始
        return
    
    if search_lang_file("temp") == "exist ja_jp.json": # ja_jp.jsonが見つからなかった場合
        # plyerのnotificationを使ってエラーを通知
        notification.notify(
            title="翻訳スキップ",
            message=f"{file_name}のja_jp.jsonが見つかったので、翻訳をスキップします。",
            app_name="MC-MOD Translating tool",
            app_icon="resources/icon.ico"
        )
        # 次のファイルの翻訳処理を開始
        return
    
    else: # en_us.jsonが見つかった場合
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
    """
    選択されたjarファイルからen_us.jsonを読み込み、Google翻訳APIを使用してja_jp.jsonを作成する関数
    翻訳の進捗状況を表示するために、update_progress関数を使用します。
    エラーが発生した場合は、Tkinterのウィンドウにエラーメッセージを表示します。
    """
    # プログレスバーを表示
    global progress
    progress = Progressbar(root, orient='horizontal', mode='determinate', length=500, value=0, maximum=100)
    progress.pack()
    generate_translating_resourcepack_dir()
    print(pack_format)
    
    print(mod_name)

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
            
            try:
                result = translator.translate(value, dest="ja")
                ja_json[key] = result.text
                translated_strings += 1
                # UpdateProgress関数を呼び出してTkinterのProgressBarを更新
                n_value = translated_strings / total_strings * 100
                update_progress(root, n_value)
                print(f"{n_value}%完了")
            
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
                        print(f"{translated_strings / total_strings * 100}%完了")
                    
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
    # 翻訳完了を通知
    path_to_icon="resources/icon.ico"
    notification.notify(
        title="翻訳完了",
        message=f"{file_name}の翻訳が完了しました。",
        app_name="MC-MOD Translating tool",
        app_icon=path_to_icon
    )

def before_screen():
    """
    翻訳するMODのjarファイルを選択するためのGUIを作成する関数。

    Parameters:
        なし

    Returns:
        なし
    """
    global gui1
    global selectFile_button
    
    gui1 = tk.Frame(root)
    gui1.pack()
    selectFile_button = tk.Button(root, text="翻訳するMODのjarファイルを選択", command=lambda:select_file(), width=50, height=5)
    selectFile_button.pack()
    
    # Minecraftのバージョンごとのpack_formatの対応表を辞書型で定義
    pack_format_dict = {
        "1.6.1 ~ 1.8.9": 1,
        "1.9 ~ 1.10.2": 2,
        "1.11 ~ 1.12.2": 3,
        "1.13 ~ 1.14.4": 4,
        "1.15 ~ 1.16.1": 5,
        "1.16.2 ~ 1.16.5": 6,
        "1.17 ~ 1.17.1": 7,
        "1.18 ~ 1.18.2": 8,
        "1.19 ~ 1.19.2": 9,
        "1.19.3": 12,
        "1.19.4": 13,
        "1.20 ~ 1.20.1": 15,
        "1.20.2": 18
    }
    
    # バージョンのリストを作成
    version_list = list(pack_format_dict.keys())
    
    # プルダウンメニューを作成
    version_combobox = ttk.Combobox(root, values=version_list, state="readonly")
    version_combobox.pack()
    
    # バージョンが選択されたらpack_format変数に対応する値をリストからbindで代入する
    def select_version(event):
        global pack_format
        pack_format = ""
        pack_format = pack_format_dict[version_combobox.get()]
    
    version_combobox.bind("<<ComboboxSelected>>", select_version)

def after_screen():
    """
    ファイル選択後の画面を表示する関数。
    選択ファイルボタンを削除し、プログレスバーを表示する。
    ready_translate関数を呼び出して翻訳処理を開始する。

    Parameters
    ----------
    なし

    Returns
    -------
    なし
    """
    selectFile_button.destroy()
    gui2 = tk.Frame(root)
    gui2.pack()

    # プログレスバーを表示
    global progress
    progress = Progressbar(root, orient='horizontal', mode='determinate', length=500, value=0, maximum=100)
    progress.pack()

def main():
    """
    メイン関数。tempフォルダとtranslating_resourcepackフォルダを初期化し、
    tkinterのウィンドウを作成する。また、プログレスバーを初期化し、
    before_screen関数を呼び出してメインループを開始する。
    """
    # tempフォルダを初期化
    int_temp_dir()
    
    # translating_resourcepackフォルダを初期化
    int_translating_resourcepack_dir()
    
    # tkinterのウィンドウを作成
    root.title("MC-MOD Translating tool")
    root.geometry("800x450")
    
    before_screen()

    # メインループを開始
    root.mainloop()

if __name__ == "__main__":

    main()