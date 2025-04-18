import json
import pandas as pd
from tqdm import tqdm
import sys
sys.setrecursionlimit(10**6)

from lib import Util, TimeAdjuster

# 定数
alpha = 0.01
file_type = "amp"

if __name__ == "__main__":
    # 設定ファイルの読み込み
    with open(f"{Util.get_root_dir()}/config/config.json", "r") as f:
        config = json.load(f)

    # 共通ファイルを取得
    common_file = Util.get_common_files(path_list=[f"{Util.get_root_dir()}/data/csv-data/{device}/{file_type}/" for device in config["AllDevice"]["Pcap"]])

    # 共通ファイルをループ
    for file_name in tqdm(common_file):

        print(f"ファイル名: {file_name}の受信時刻補正を開始します。")

        # データフレームを辞書に格納
        df_dict_original = {}
        for device in sorted(config["AllDevice"]["Pcap"]):
            file_path = f"{Util.get_root_dir()}/data/csv-data/{device}/{file_type}/{file_name}"
            df_dict_original[device] = pd.read_csv(file_path, index_col=0)

        # インスタンスを生成
        ta = TimeAdjuster(df_dict=df_dict_original, alpha=alpha)

        try:
            # 時間調整を行う
            start = 0
            while True:
                start = ta.adjust_time(start)
                if start is True:
                    break

        except KeyError:
            pass

        # データを保存
        for device in sorted(config["AllDevice"]["Pcap"]):
            Util.create_path(path=f"{Util.get_root_dir()}/data/adjusted-data/{device}/{file_type}")
            ta.df_dict[device].to_csv(f"{Util.get_root_dir()}/data/adjusted-data/{device}/{file_type}/{file_name}")