""" 複数MODを同時翻訳する """
"""
参考サイト 
- Pythonでクリップボードにファイルをコピーする方法 (Windows). (2023). Retrieved 3 November 2023, from https://qiita.com/Rilm2525/items/5ef4b4e8552b71971ad4
"""

from tkinter.ttk import *
from plyer import notification
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

import os, zipfile, shutil, json, threading, pyperclip, time, tqdm, customtkinter as ctk

from googletrans import Translator
import logging
import logging.handlers

# ログの設定
logger = logging.getLogger(__name__) # ロガーを取得
logger.setLevel(logging.DEBUG) # ログレベルの設定
# ログファイルを出力するディレクトリが存在しない場合は作成する
if not os.path.exists("logs"):
    os.mkdir("logs")
rh = logging.handlers.RotatingFileHandler(filename='logs/mcmt.log', maxBytes=100000, backupCount=3) # ログローテーションを設定
logger.addHandler(rh) # ログハンドラーを追加
logger.debug("===== START =====") # ログを出力

# Tkinterの初期化
root = ctk.CTk()

# Google翻訳APIを使うための初期設定
translator = Translator()

def int_temp_dir():
    """
    テンポラリフォルダを初期化します。存在しない場合は作成します。
    既存のファイルやディレクトリを削除します。
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
                print(f"ERROR: ファイルの削除に失敗しました >> {e}")
    else:
        os.mkdir(temp_dir)

def int_translating_resourcepack_dir():
    """
    'translating_resourcepack' フォルダを削除する。
    """
    print("LOG: translating_resourcepackフォルダを初期化します。")
    if os.path.exists("translating_resourcepack"):
        shutil.rmtree("translating_resourcepack")

""" def int_gui1(place, excepted_widget):

    # 指定されたウィジェット以外のウィジェットを削除
    for widget in root.winfo_children():
        if widget != root:
            widget.destroy() """

def before_screen():
    """
    翻訳するMODのjarファイルを選択するためのGUIを作成する関数。

    Parameters:
        なし

    Returns:
        なし
    """
    title_label = ctk.CTkLabel(root, text="MC-MOD Translating tool", font=("Noto Sans JP Black", 30))
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    global gui1
    gui1 = ctk.CTkFrame(root, width=750, height=380, corner_radius=6, border_width=1, fg_color=['gray90', 'gray13'], border_color=['gray65', 'gray28'])
    gui1.grid_columnconfigure(0, weight=1)
    gui1.grid_rowconfigure(0, weight=1)
    gui1.grid(row=3, column=0, padx=25, pady=(5,25), sticky="nsew")
    
    # 指示を表示するラベルを作成
    instruction_label = ctk.CTkLabel(gui1, text="翻訳するMODのバージョンを選択してください。", font=("Noto Sans JP", 18))
    instruction_label.pack(fill="x", pady=3, padx=1)
    
    # バージョンが選択されたらpack_format変数に対応する値をリストから代入する
    def select_version(value):
        global pack_format
        pack_format = value
        # ボタンを削除
        gui1.destroy()
        
        
        
        global gui2
        gui2 = ctk.CTkFrame(root, width=750, height=380, corner_radius=6, border_width=1, fg_color=['gray90', 'gray13'], border_color=['gray65', 'gray28'])
        gui2.grid_columnconfigure(0, weight=1)
        gui2.grid_rowconfigure(0, weight=1)
        gui2.grid(row=3, column=0, padx=25, pady=(5,25), sticky="nsew")
        
        # 翻訳するMODのjarファイルを選択するためのボタンを作成
        select_file_button = ctk.CTkButton(gui2, text="翻訳するMODのjarファイルを選択", command=lambda: select_file(), anchor="center", corner_radius=6, border_width=0, border_spacing=2, fg_color=['#3a7ebf', '#1f538d'], hover_color=['#325882', '#14375e'], border_color=['#3E454A', '#949A9F'], text_color=['#DCE4EE', '#DCE4EE'], text_color_disabled=['gray74', 'gray60'], font=("Noto Sans JP", 30))
        select_file_button.grid(row=1, column=0, pady=(203,10), padx=10, sticky="nsew")
        
        # クリップボードにあるmodsフォルダーのパスから翻訳するためのボタンを作成
        select_file_button = ctk.CTkButton(gui2, text="クリップボードから翻訳", command=lambda: select_file_from_clipboard(), anchor="center", corner_radius=6, border_width=0, border_spacing=2, fg_color=['#3a7ebf', '#1f538d'], hover_color=['#325882', '#14375e'], border_color=['#3E454A', '#949A9F'], text_color=['#DCE4EE', '#DCE4EE'], text_color_disabled=['gray74', 'gray60'], font=("Noto Sans JP", 30))
        select_file_button.grid(row=2, column=0, pady=(10,203), padx=10, sticky="nsew")
    
    # Minecraftのバージョンと対応するコマンドの辞書
    version_commands = {
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

    # ボタンを生成して配置する関数
    def create_version_button(version, command, pady):
        return ctk.CTkButton(
            gui1,
            anchor="center",
            corner_radius=6,
            border_width=0,
            border_spacing=2,
            fg_color=['#3a7ebf', '#1f538d'],
            hover_color=['#325882', '#14375e'],
            border_color=['#3E454A', '#949A9F'],
            text_color=['#DCE4EE', '#DCE4EE'],
            text_color_disabled=['gray74', 'gray60'],
            font=("Arial", 18),
            text=version,
            command=lambda: select_version(command)
        ).pack(fill="x", pady=pady, padx=10)

    # バージョンごとのボタンを生成して配置
    for version, command in version_commands.items():
        pady = (0, 5) if version == "1.6.1 ~ 1.8.9" else ((5, 10) if version == "1.20.2" else 5)
        create_version_button(version, command, pady)

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
    file_paths = filedialog.askopenfilenames(filetypes = fTyp, initialdir = initialdir)  # ファイル選択ダイアログを表示
    file_names = list([os.path.basename(file_name) for file_name in file_paths])         # 選択されたファイルの名前を取得
    
    num = 0
    # 翻訳処理を別のスレッドで実行
    t = threading.Thread(target=translate_in_thread, args=(file_paths,file_names)) # translate_in_thread関数を別のスレッドで実行, file_nameを引数として渡す
    t.start()

def select_file_from_clipboard():
    """
    クリップボードからファイルパスを取得し、その中のjarファイルをリストとして取得する関数。
    jarファイルが存在しない場合、エラーメッセージを表示する。
    jarファイルが存在する場合、翻訳処理を別のスレッドで実行する。
    """
    global file_names
    file_paths = []
    
    # クリップボードにあるmodsフォルダーのパスを取得
    mods_path = pyperclip.paste()
    
    # mods_pathを整形する
    mods_path = mods_path.replace("\"","")
    
    # modsフォルダーのパスが存在するか確認
    if os.path.exists(mods_path):
        
        # modsフォルダーのパスが存在する場合、その中のjarファイルをリストとして取得
        file_paths = [os.path.join(mods_path, file) for file in os.listdir(mods_path) if file.endswith(".jar")]
        file_names = list([os.path.basename(file_name) for file_name in file_paths])         # 選択されたファイルの名前を取得

    else:
        
        # modsフォルダーのパスが存在しない場合、エラーメッセージを表示して関数を終了
        tk.messagebox.showerror("エラー","クリップボードにパスがありません。")
        return
    
    # 翻訳処理を別のスレッドで実行(フリーズ回避)
    t = threading.Thread(target=translate_in_thread, args=(file_paths, file_names)) # translate_in_thread関数を別のスレッドで実行, file_nameを引数として渡す
    t.start()

def translate_in_thread(file_paths, file_name):
    """
    ready_translate関数を別のスレッドで実行するための関数

    Args:
        file_paths (tuple): 翻訳するjarファイルのパス
        file_name (str): 翻訳するファイルの名前

    Returns:
        None
    """
    # 翻訳を開始することを通知
    print("="*20)
    print(f"LOG: {file_name}の翻訳を開始します")
    print(f"LOG: ファイルパス >> {file_paths}")
    print("="*20)

    # 翻訳するファイルの数を取得
    global total_files
    total_files = len(file_paths)
    # 翻訳が完了したファイルの数を取得するための変数を初期化
    global processed_files
    processed_files = 0
    
    gui2.destroy() # ファイル選択画面を削除
    
    # 翻訳するファイルの名前を表示
    global gui3
    gui3 = ctk.CTkFrame(root, width=750, height=380, corner_radius=6, border_width=1, fg_color=['gray90', 'gray13'], border_color=['gray65', 'gray28'])
    gui3.grid_rowconfigure(0, weight=0)
    gui3.grid(row=2, column=0, padx=25, pady=(5,150), sticky="nsew")
    
    processed_files_label = ctk.CTkLabel(gui3, text=f"翻訳済みのファイル: {processed_files}/{total_files}", font=("Noto Sans JP Black", 18))
    processed_files_label.pack(fill="x", pady=2, padx=1)
    
    icon_image = ctk.CTkImage(light_image=Image.open("resources/icon.png"), dark_image=Image.open("resources/icon.png"), size=[100,100])
    icon_image_label = ctk.CTkLabel(root, image=icon_image, text="")
    icon_image_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    
    # 翻訳処理を実行
    for file_path in file_paths:
        ready_translate(file_path, file_name)
        int_temp_dir() # tempフォルダを初期化
        
        # 現在のファイル進行度を表示
        print("="*20)
        print(f"LOG: 進捗 {processed_files}/{total_files}")
        print("="*20)
        # processed_files_labelを更新
        processed_files_label.configure(text=f"翻訳済みのファイル: {processed_files}/{total_files}")
        
        # 最後のファイルの翻訳が完了したらアプリを終了する
        if processed_files == total_files:
            print("LOG: 翻訳が完了しました。")
            # 翻訳完了を通知
            path_to_icon="resources/icon.ico"
            notification.notify(
                title="翻訳完了",
                message="すべての翻訳が完了しました。",
                app_name="MC-MOD Translating tool",
                app_icon=path_to_icon
                )
            time.sleep(1)
            # 起動したすべてのスレッドを終了
            for th in threading.enumerate(): # 現在動作中のスレッドをすべて取得
                if th != threading.main_thread(): # メインスレッド以外のスレッドを終了
                    th._stop() # スレッドを終了
                # メインスレッドを終了
                else:
                    logger.debug("===== END =====")
                    os._exit(0)
            root.destroy() # GUIを終了

def ready_translate(file_path, file_name):
    """
    指定されたjarファイルを解凍し、en_us.jsonファイルを読み込み、翻訳を実行する。
    翻訳されたja_jp.jsonファイルを生成し、mod_nameフォルダに保存する。
    また、translating_resourcepack/assets内にmod_nameフォルダを作成し、langフォルダを含むフォルダを複製する。
    ただし、langフォルダとen_us.jsonとja_jp.json以外のファイルは削除する。
    
    引数:
    - file_path: str型。翻訳対象のjarファイルのパス。
    - file_name: str型。翻訳対象のjarファイルの名前。
    
    戻り値:
    - なし
    """
    # 選択されたjarファイルをtempfileにzipfileを使って解凍する
    OpF = zipfile.ZipFile(file_path, "r")      # readモードでzipファイルを開く
    OpF.extractall("temp")                     # tempフォルダに解凍する
    
    if search_lang_file("temp") == "No en_us.json": # en_us.jsonが見つからなかった場合
        logger.error(f"ERROR: {file_path}のen_us.jsonが見つかりませんでした。")
        # 次のファイルの翻訳処理を開始
        return
    
    if search_lang_file("temp") == "No lang folder": # langフォルダが見つからなかった場合
        logger.error(f"ERROR: {file_path}のlangフォルダが見つかりませんでした。")
        # 次のファイルの翻訳処理を開始
        return
    
    if search_lang_file("temp") == "exist ja_jp.json": # ja_jp.jsonが見つからなかった場合
        logger.error(f"ERROR: {file_path}のja_jp.jsonが見つかったので、翻訳をスキップします。")
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
            logger.info(f"LOG: {mod_name}フォルダを複製しました。")
    
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
    translate_json(file_path, mod_name)

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
                    logger.info("LOG: en_us.jsonが見つかったので、翻訳を開始します。")
                    return lang_path
                
                else:  # en_us.jsonが存在しない場合
                    logger.info("LOG: en_us.jsonが見つからなかったので、翻訳をスキップします。")
                    return "No en_us.json"
                
            # langフォルダにja_jp.jsonがあるときは何もせずに関数を終了
            else:
                logger.info("LOG: ja_jp.jsonが見つかったので、翻訳をスキップします。")
                return "exist ja_jp.json"
    logger.info("LOG: langフォルダが見つからなかったので、翻訳をスキップします。")
    return "No lang folder"

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

def translate_json(file_path,mod_name):
    """
    en_us.jsonの文字列を日本語に翻訳し、ja_jp.jsonに保存します。
    
    Args:
    - file_name (str): 翻訳対象のファイル名。
    - mod_name (str): ファイルが属するmodの名前。
    """
    logger.info("="*20)
    logger.info(f"LOG: {file_path}の翻訳を開始します。")
    logger.info(f"LOG: mod_name = {mod_name}")
    logger.info("="*20)
    file_name_label = ctk.CTkLabel(gui3, text=os.path.basename(file_path), font=("Noto Sans JP", 18))
    file_name_label.pack(fill="x", pady=2, padx=1)
    

    
    
    generate_translating_resourcepack_dir()
    logger.info(f"LOG: pack_format >> {pack_format}")
    logger.info("="*20)

    # en_us.jsonを開く
    with open(search_lang_file("temp"), "r+", encoding="utf-8") as f:
        en_json = json.load(f)

    # 翻訳事前準備
    ja_json = {} # ja_jp.jsonを作成するための空の辞書を作成
    total_strings = sum(1 for _ in find_strings(en_json)) # en_us.jsonに含まれる文字列の数を数える
    
    # プログレスバーを表示
    import tkinter.ttk as ttk
    translated_strings = 0 # 翻訳された文字列の数を数える
    progress = ttk.Style()
    progress.theme_use("alt")
    progress.configure("Custom.Horizontal.TProgressbar",
                        background="#3a7ebf",
                        foreground="#939BA2",
                        bordercolor="#4A4D50",
                        troughtcolor="#939BA2"
                        )
    progress = ttk.Progressbar(gui3,
                                orient="horizontal",
                                length=500,
                                mode="determinate",
                                style="Custom.Horizontal.TProgressbar",
                                maximum=total_strings,
                                variable=translated_strings
                                )
    progress.pack(pady=10, padx=10, fill="x")
    
    # ターミナル用のプログレスバーを表示
    pbar = tqdm.tqdm(total=total_strings)
    pbar.update(0)

    # en_us.jsonの中身を走査して翻訳を実行
    for key, value in en_json.items(): # en_us.jsonの中身を走査
    
        if isinstance(value, str): # valueが文字列の場合
            
            try:
                result = translator.translate(value, dest="ja")
                ja_json[key] = result.text
                translated_strings += 1
                # UpdateProgress関数を呼び出してTTkinterのProgressBarを更新
                progress.step(1)
                pbar.update(1)
            
            # 翻訳エラーが発生した場合は、ja_jp.jsonにen_us.jsonの内容をそのまま書き込む
            except Exception as e:
                logger.error(f"ERROR: translation error >> {e}")
                ja_json[key] = value
        
        elif isinstance(value, dict): # valueが辞書型の場合
            ja_dict = {} # ja_jp.jsonの中身を作成するための空の辞書を作成
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str):
                    try:
                        result = translator.translate(sub_value, dest="ja") # 翻訳を実行
                        ja_dict[sub_key] = result.text
                        translated_strings += 1
                        # UpdateProgress関数を呼び出してTkinterのProgressBarを更新
                        update_progress(translated_strings / total_strings)
                        pbar.update(1)
                    
                    # 翻訳エラーが発生した場合は、ja_jp.jsonにen_us.jsonの内容をそのまま書き込む
                    except Exception as e:
                        logger.error(f"ERROR: translation error >> {e}")
                        ja_dict[sub_key] = sub_value
                else:
                    ja_dict[sub_key] = sub_value
            ja_json[key] = ja_dict
    
    # ja_jp.jsonを保存する
    with open(os.path.join("translating_resourcepack", "assets", mod_name, "lang", "ja_jp.json"), "w+", encoding="utf-8") as f:
        json.dump(ja_json, f, ensure_ascii=False, indent=4)

    logger.info(f"LOG: {file_path}の翻訳が完了しました。")
    logger.info("="*20) # 終了を示すために区切り線を表示
    global processed_files
    processed_files += 1 # 翻訳が完了したファイルの数を数える

    file_name_label.destroy()
    progress.destroy()

def generate_translating_resourcepack_dir():
    """
    翻訳用リソースパックのディレクトリを生成する関数。

    Args:
        なし

    Returns:
        なし
    """
    
    # 現在の階層にtranslating_resourcepackフォルダを生成
    if not os.path.exists("translating_resourcepack"):
        os.mkdir("translating_resourcepack")
        logger.info("LOG: translating_resourcepackフォルダを生成しました。")
    
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
        logger.info("LOG: translating_resourcepack\\pack.mcmetaを生成しました。")

    # translating_resourcepack\assetsを生成
    if not os.path.exists(os.path.join("translating_resourcepack", "assets")):
        os.mkdir(os.path.join("translating_resourcepack", "assets"))
        logger.info("LOG: translating_resourcepack\\assetsを生成しました。")

def update_progress(root):
    """
    プログレスバーの値を更新し、GUIを更新します。

    Args:
        root: GUIのルートウィンドウ。
        value: プログレスバーに設定する値。
    """
    # progress.step() # プログレスバーの値を更新

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

def main():
    """
    この関数は、tempフォルダとtranslating_resourcepackフォルダを初期化します。
    タイトルとアイコンを持つtkinterウィンドウを作成します。
    before_screen関数を呼び出し、メインループを開始します。
    """
    # tempフォルダを初期化
    int_temp_dir()
    
    # translating_resourcepackフォルダを初期化
    int_translating_resourcepack_dir()
    
    # Ctkinterのウィンドウを作成
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    root.title("MC-MOD Translating tool")
    root.geometry("700x630")
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    

    # iconを設定
    path_to_icon="resources/icon.ico"
    root.iconbitmap(default=path_to_icon)
    
    before_screen()

    # メインループを開始
    root.mainloop()

if __name__ == "__main__":
    main()
