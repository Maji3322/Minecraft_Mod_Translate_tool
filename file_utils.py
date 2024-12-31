# NOTE: ファイルエディターを起動し、最終的には選択されたファイルのパスを返す。

import json
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
    logger.info("%sを初期化します。", path)
    print(f"{path}を初期化します。")
    if os.path.exists(path):
        logger.debug("%sは存在します。削除します。", path)
        shutil.rmtree(path)

    try:
        os.makedirs(path)
        logger.debug("%sを作成しました。", path)
    except OSError as e:
        logger.error("%sの初期化に失敗しました。エラー: %s", path, str(e))
    return

def gen_pack_dir(pack_format, page, json_files):
    """
    pack.mcmetaを生成し、assetsフォルダを生成する関数。

    Args:
        pack_format (str): リソースパックのバージョン番号
        page (ft.Page): ページオブジェクト
        json_files (list): 翻訳対象のen_us.jsonファイルのパスのリスト

    Returns:
        int: 成功時は0、失敗時は1
    """
    try:
        if not pack_format:
            logger.error("バージョンが指定されていません。")
            if page:
                gui_module.err_dlg(page, "エラー", "バージョンを選択してください。")
            return 1

        # translate_rpディレクトリの初期化はprocess_app側で行うように変更
        # logger.debug("translate_rpディレクトリを初期化します。")
        # init_dir("translate_rp")
        # logger.info("translate_rpディレクトリを初期化しました。")

        # assetsディレクトリを作成
        os.makedirs(os.path.join("translate_rp", "assets"), exist_ok=True)
        logger.info("translate_rp/assetsディレクトリを確認しました。")

        # asset_foldersの取得と結合
        asset_folders = [
            os.path.basename(os.path.dirname(os.path.dirname(json_file)))
            for json_file in json_files
        ]
        asset_folders_str = "、".join(asset_folders)

        # pack.mcmetaの内容を作成
        pack_mcmeta_content = {
            "pack": {
                "pack_format": int(pack_format),
                "description": f"{asset_folders_str}を翻訳したリソースパックです。",
            }
        }

        # pack.mcmetaファイルを生成
        with open(
            os.path.join("translate_rp", "pack.mcmeta"), "w", encoding="utf-8"
        ) as f:
            json.dump(pack_mcmeta_content, f, indent=4, ensure_ascii=False)
            logger.info("pack.mcmetaファイルを生成しました。")

        return 0

    except Exception as e:
        error_msg = f"translate_rpフォルダの生成中にエラーが発生しました: {str(e)}"
        logger.error(error_msg, exc_info=True)
        if page:
            gui_module.err_dlg(page, "エラー", error_msg)
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
    jarファイルを再帰的に解凍する関数。META-INF/jars内のjarファイルも同様に処理する。

    Args:
        path (str): 解凍するjarファイルのパス

    Returns:
        jar_folder (str): 解凍したファイルのパス
    """
    if not os.path.exists(path):
        logger.error("%sが見つかりません。スキップします。", path)
        return None

    logger.info("%sを解凍します。", path)

    # tempフォルダがない場合は作成
    if not os.path.exists("temp"):
        os.mkdir("temp")

    # 解凍先のフォルダを作成（ベースフォルダ）
    base_name = os.path.splitext(os.path.basename(path))[0]
    jar_folder = os.path.join(os.getcwd(), "temp", base_name)
    os.makedirs(jar_folder, exist_ok=True)

    # jarファイルをzipとしてコピー
    _, ext = os.path.splitext(path)
    if ext.lower() == ".jar":
        zip_path = jar_folder + ".zip"
        shutil.copy2(path, zip_path)
    else:
        zip_path = path

    # zipファイルを解凍
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            print(f"unzip_jar: {zip_path}")
            zip_file.extractall(jar_folder)
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        logger.error("解凍エラー: %s - %s", zip_path, str(e))
        return jar_folder

    # 一時的なzipファイルを削除
    if ext.lower() == ".jar" and os.path.exists(zip_path):
        os.remove(zip_path)

    # META-INF/jarsフォルダ内のjarファイルを処理
    meta_jars_path = os.path.join(jar_folder, "META-INF", "jars")
    if os.path.exists(meta_jars_path):
        for root, _, files in os.walk(meta_jars_path):
            for file in files:
                if file.endswith(".jar"):
                    inner_jar_path = os.path.join(root, file)
                    try:
                        # 内部jarファイル用の解凍先フォルダを短い名前で作成
                        inner_base_name = os.path.splitext(file)[0][
                            :30
                        ]  # 名前を30文字に制限
                        inner_jar_folder = os.path.join(
                            jar_folder,
                            f"__{inner_base_name}",  # プレフィックスを追加して区別
                        )
                        os.makedirs(inner_jar_folder, exist_ok=True)

                        # 内部jarファイルを解凍
                        with zipfile.ZipFile(inner_jar_path, "r") as inner_zip:
                            print(f"解凍中(内部jar): {inner_jar_path}")
                            inner_zip.extractall(inner_jar_folder)

                    except (zipfile.BadZipFile, FileNotFoundError, OSError) as e:
                        logger.error(
                            "内部jar解凍エラー: %s - %s", inner_jar_path, str(e)
                        )
                        continue

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
    # ここでのinit_dir呼び出しを削除
    # init_dir("temp")
    # init_dir("translate_rp")
    pass
