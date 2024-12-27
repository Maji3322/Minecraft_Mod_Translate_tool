# NOTE: ファイルエディターを起動し、最終的には選択されたファイルのパスを返す。

import logging
import logging.handlers
import os
import shutil
import zipfile

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
    except OSError as e:
        logger.error("%sの初期化に失敗しました。エラー: %s", path, str(e))
    return


def gen_pack_dir(pack_format, page, json_files):
    """
    pack.mcmetaを生成し、assetsフォルダを生成することができたら0を返す。
    バージョンが指定されていないときは、pack.mcmetaの生成を行わないで1を返す。
    pack_format: リソースパックのバージョン番号を指定
    json_files: 翻訳対象のen_us.jsonファイルのパスのリスト
    """

    # json_files に格納された各ファイルの2つ上の階層のフォルダの名前を取得
    asset_folders = [
        os.path.basename(os.path.dirname(os.path.dirname(json_file)))
        for json_file in json_files
    ]
    # asset_foldersの各要素をカンマ区切りで結合して文字列にする(str)
    asset_folders = str("、".join(asset_folders))

    pack_mcmeta_content = f"""
{{
    "pack": {{
        "pack_format": {pack_format},
        "description": "{asset_folders}を翻訳したリソースパックです。"
    }}
    }}
"""
    # pack.mcmetaを生成
    if not os.path.exists(
        os.path.join("translate_rp", "pack.mcmeta")
    ):  # pack.mcmetaが存在しない場合
        with open(
            os.path.join("translate_rp", "pack.mcmeta"), "w+", encoding="utf-8"
        ) as f:  # pack.mcmetaを作成
            if pack_format != "":
                f.write(pack_mcmeta_content)
                logger.info("translate_rp\\pack.mcmetaを生成しました。")

                # assetsフォルダを生成
                os.makedirs(os.path.join("translate_rp", "assets"))
                return 0
            else:
                if page:
                    gui_module.err_dlg(page, "エラー", "バージョンを選択してください。")
                    logger.error("バージョンが指定されていません。")
                return 1
        # Ensure the directory and file are created even if pack_format is empty
        os.makedirs(os.path.join("translate_rp", "assets"), exist_ok=True)
        with open(
            os.path.join("translate_rp", "pack.mcmeta"), "w+", encoding="utf-8"
        ) as f:
            f.write(pack_mcmeta_content)
        logger.info("translate_rp\\pack.mcmetaを生成しました。")
        return 0


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
                print(f"ERROR: {os.path.join(root, file)}は削除できませんでした。")
                logger.error(
                    "ERROR: %sは削除できませんでした。", os.path.join(root, file)
                )
        for dir in dirs:
            # langフォルダは削除しない
            if dir != "lang":
                shutil.rmtree(os.path.join(root, dir))
            else:
                # エラーメッセージをprintとloggerに出力
                print(f"ERROR: {os.path.join(root, dir)}は削除できませんでした。")
                logger.error(
                    "ERROR: %sは削除できませんでした。", os.path.join(root, dir)
                )


def recursive_unzip_jar(path: str):
    """
    0. `temp`フォルダがない場合は作成
    2. その中にjarファイルを.zipを付けてコピーし、`temp`フォルダに解凍する。
    3. modjar.jar/META-INF/jars/modjar2.jarというファイルがあり続ける限り、再帰的に解凍する。
    Args:
        path (str): 解凍するjarファイルのパス

    Returns:
        jar_folder (list): 解凍したファイルのパス
    """

    logger.info("%sを解凍します。", path)

    if not os.path.exists("temp"):
        os.mkdir("temp")

    # 解凍先のフォルダを作成
    jar_folder = os.path.join(
        os.getcwd(), "temp", os.path.splitext(os.path.basename(path))[0]
    )

    # jarファイルをzipに変えてコピーを作成
    zip_path = jar_folder + ".zip"

    # 関数の引数にあるjarファイルを、作成したzip_pathの先にコピーする
    logger.info("%sをコピーします。", path)
    logger.info("コピー先: %s", zip_path)
    shutil.copy(path, zip_path)

    # zipファイルを解凍。with文を使うと、ファイルを閉じる処理を自動で行ってくれる。(busy対策)
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        print(f"unzip_jar: {zip_path}")
        try:
            zip_file.extractall(jar_folder)  # 解凍先をjar_folderに変更
        except zipfile.BadZipFile as e:
            print(f"ERROR: {zip_path}の解凍に失敗しました。\n{e}")
            logger.error("%sの解凍に失敗しました。", zip_path)
        except FileNotFoundError as e:
            print(f"ERROR: {zip_path}が見つかりません。\n{e}")
            logger.error("%sが見つかりません。", zip_path)

    # zipファイルを削除
    os.remove(zip_path)

    # 解凍したフォルダの中の、META-INF/jarsフォルダの中にあるjarファイルを再帰的に解凍
    more_jars = []
    for root, _, files in os.walk(f"{jar_folder}/META-INF/jars"):
        for file in files:
            if file.endswith(".jar"):
                more_jars.append(os.path.join(root, file))
    # 再帰的に解凍
    for jar in more_jars:
        recursive_unzip_jar(jar)

    return jar_folder


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
            if not any(
                os.path.commonpath([file_path, dir_path]) == dir_path
                for file_path in target_file_paths
            ):
                shutil.rmtree(dir_path)

    # Print the remaining files and folders
    print("Remaining files and folders:")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            print(os.path.join(dirpath, filename))
        for dirname in dirnames:
            print(os.path.join(dirpath, dirname))

    return


def copy_assets_folders(root_dir, json_file_paths):
    """
    json_file_paths に格納された各ファイルのassetsフォルダを
    translate_rp/assets フォルダにマージコピーする関数

    Args:
        root_dir (str): ルートディレクトリのパス
        json_file_paths (list): json ファイルのパスのリスト
    """
    translate_rp_dir = os.path.join(os.path.dirname(root_dir), "translate_rp")
    assets_dir = os.path.join(translate_rp_dir, "assets")
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
                    dst_file = os.path.join(
                        dest_dir, os.path.relpath(src_file, src_assets_dir)
                    )
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)
            print(f"assets フォルダをマージしました: {dest_dir}")
        else:
            # 新規にフォルダをコピー
            shutil.copytree(src_assets_dir, dest_dir)
            print(f"assets フォルダをコピーしました: {dest_dir}")


if __name__ == "__main__":
    init_dir("temp")
    init_dir("translate_rp")
