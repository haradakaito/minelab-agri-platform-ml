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
    with open(f"{Util.get_root_dir()}/config/config.json", "r") as f:
        config = json.load(f)

    group1_devices = ["minelab-iot-nexmon-1", "minelab-iot-nexmon-2", "minelab-iot-nexmon-3", "minelab-iot-nexmon-4"]
    group2_devices = ["minelab-iot-nexmon-a", "minelab-iot-nexmon-b"]

    # グループ1用の共通ファイル
    common_file_group1 = Util.get_common_files(
        path_list=[f"{Util.get_root_dir()}/data/csv-data/{device}/{file_type}/" for device in group1_devices]
    )

    # グループ2用の共通ファイル
    common_file_group2 = Util.get_common_files(
        path_list=[f"{Util.get_root_dir()}/data/csv-data/{device}/{file_type}/" for device in group2_devices]
    )

    # 各グループで処理を分ける
    for group_devices, common_files in [
        (group1_devices, common_file_group1),
        (group2_devices, common_file_group2)
    ]:
        for file_name in tqdm(common_files):
            print(f"ファイル名: {file_name}の受信時刻補正を開始します。")

            df_dict_original = {}
            for device in group_devices:
                file_path = f"{Util.get_root_dir()}/data/csv-data/{device}/{file_type}/{file_name}"
                try:
                    df_dict_original[device] = pd.read_csv(file_path, index_col=0)
                except FileNotFoundError:
                    print(f"⚠️ {file_path} が見つかりません。スキップします。")
                    continue

            # 時刻補正処理
            ta = TimeAdjuster(df_dict=df_dict_original, alpha=alpha)
            try:
                start = 0
                while True:
                    start = ta.adjust_time(start)
                    if start is True:
                        break
            except KeyError:
                pass

            # 保存処理
            for device in group_devices:
                if device in group1_devices:
                    save_dir = f"{Util.get_root_dir()}/data/adjusted-data/{device}/{file_type}"
                else:
                    save_dir = f"{Util.get_root_dir()}/data/adjusted-data-natori/{device}/{file_type}"
                Util.create_path(path=save_dir)
                ta.df_dict[device].to_csv(f"{save_dir}/{file_name}")
