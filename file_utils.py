
# NOTE: ファイルエディターを起動し、最終的には選択されたファイルのパスを返す。

import shutil, os, logging, zipfile
import logging.handlers
import gui_module

logger = logging.getLogger(__name__)


def init_dir(path):
    """
    渡されたディレクトリを空っぽにし、その場所に同じファイルを作成する。
    path: str
    """
    if os.path.exists(path):
        shutil.rmtree(path)
    
    try:
        os.makedirs(path)
    except Exception as e:
        logger.error("ERROR: %s ", e)
        logger.error("ERROR: %s の初期化に失敗したと思われます。", path)


def gen_pack_dir(pack_format, page, json_files):
    """
    pack.mcmetaを生成し、assetsフォルダを生成することができたら0を返す。
    バージョンが指定されていないときは、pack.mcmetaの生成を行わないで1を返す。
    pack_format: リソースパックのバージョン番号を指定
    json_files: 翻訳対象のen_us.jsonファイルのパスのリスト
    """
    
    # json_files に格納された各ファイルの2つ上の階層のフォルダの名前を取得
    asset_folders = [os.path.basename(os.path.dirname(os.path.dirname(json_file))) for json_file in json_files]
    # asset_foldersの各要素をカンマ区切りで結合して文字列にする(str)
    asset_folders = str("、".join(asset_folders))
    
    # pack.mcmetaを生成
    if not os.path.exists(os.path.join("translate_rp", "pack.mcmeta")):  # pack.mcmetaが存在しない場合
        with open(os.path.join("translate_rp", "pack.mcmeta"), "w+", encoding="utf-8") as f:  # pack.mcmetaを作成
            if pack_format != "":
                f.write(f'''{{
    "pack": {{
        "pack_format": {pack_format},
        "description": "{asset_folders}を翻訳したリソースパックです。"
    }}
}}''')
                logger.info("LOG: translate_rp\\pack.mcmetaを生成しました。")
                
                # assetsフォルダを生成
                os.makedirs(os.path.join("translate_rp", "assets"))
                return 0
            else:
                gui_module.err_dlg(page, "エラー", "バージョンを選択してください。")
                logger.error("ERROR: バージョンが指定されていません。")
                return 1


def lang_remove_other_files(path):
    """
    指定したフォルダとその中身以外のファイルとフォルダを削除する、langフォルダの処理をするための関数

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
            else:
                # エラーメッセージをprintとloggerに出力
                print("ERROR: %s は削除できませんでした。", os.path.join(root, file))
                logger.error("ERROR: %s は削除できませんでした。", os.path.join(root, file))
        for subdir in dirs:
            # langフォルダは削除しない
            if subdir != "lang":
                shutil.rmtree(os.path.join(root, subdir))
            else:
                # エラーメッセージをprintとloggerに出力
                print("ERROR: %s は削除できませんでした。", os.path.join(root, subdir))
                logger.error("ERROR: %s は削除できませんでした。", os.path.join(root, subdir))


def unzip_jar(path: str):
    """
    pathのjarファイルの名前でフォルダを作成し、その中にjarファイルを.zipを付けてコピーし、解凍する。
    Args:
        path (str): 解凍するjarファイルのパス
    """

    print(f"path: {path}")
    if not os.path.exists("temp"):
        os.mkdir("temp")

    # 解凍先のフォルダ
    jar_folder = os.path.join("temp", os.path.splitext(os.path.basename(path))[0])
    try:
        os.makedirs(jar_folder)
    except Exception as e:
        logger.error("ERROR: %s ", e)
        logger.error("ERROR: %s の作成に失敗したと思われます。", jar_folder)
        return
    
    # jarファイルをzipに変えてコピー
    jar_folder_zip_path = os.path.join(jar_folder, os.path.basename(path) + ".zip")
    shutil.copy(path, jar_folder_zip_path)

    # zipファイルを解凍
    with zipfile.ZipFile(jar_folder_zip_path, "r") as zip:
        print(f"unzip_jar: {jar_folder_zip_path}")
        try:
            zip.extractall(jar_folder)
        except Exception as e:
            logger.error("ERROR: %s ", e)
            logger.error("ERROR: %s の解凍に失敗したと思われます。", jar_folder_zip_path)

    return


def delete_files_except(root_dir, target_file_paths):
    """
    指定されたファイルを残し、そこにたどり着くためのフォルダも残して、
    他のファイルやフォルダをすべて削除する関数

    Args:
        root_dir (str): ルートディレクトリ(処理対象フォルダ)のパス
        target_file_path (str): 残すするファイルのパス
    """
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if file_path not in target_file_paths:
                os.remove(file_path)
        for dirname in dirnames:
            dir_path = os.path.join(dirpath, dirname)
            if not any(file_path.startswith(dir_path) for file_path in target_file_paths):
                shutil.rmtree(dir_path)

    # logに残っているファイルとフォルダを表示
    logger.info("----------------残っているファイルとフォルダ----------------")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            logger.info(os.path.join(dirpath, filename))
        for dirname in dirnames:
            logger.info(os.path.join(dirpath, dirname))


def copy_assets_folders(root_dir, json_file_paths):
    """
    json_file_paths に格納された各ファイルのassetsフォルダを
    translate_rp/assets フォルダにマージコピーする関数

    Args:
        root_dir (str): ルートディレクトリのパス
        json_file_paths (list): json ファイルのパスのリスト
    """
    translate_rp_dir = os.path.join(os.path.dirname(root_dir), 'translate_rp')
    assets_dir = os.path.join(translate_rp_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)

    for json_file_path in json_file_paths:
        # json ファイルのパスからassetsフォルダのパスを特定する
        src_assets_dir = os.path.dirname(os.path.dirname(json_file_path))

        # assetsフォルダのコピー先ディレクトリ名を作成
        dest_dirname = os.path.basename(src_assets_dir)
        dest_dir = os.path.join(assets_dir, dest_dirname)

        # 既存のフォルダがある場合はマージする
        if os.path.exists(dest_dir):
            for root, _, files in os.walk(src_assets_dir):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dest_dir, os.path.relpath(src_file, src_assets_dir))
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)
            print(f"assets フォルダをマージしました: {dest_dir}")
        else:
            # 新規にフォルダをコピー
            shutil.copytree(src_assets_dir, dest_dir)
            logger.info("assets フォルダをコピーしました: %s", dest_dir)


if __name__ == "__main__":
    init_dir("temp")
    init_dir("translate_rp")

