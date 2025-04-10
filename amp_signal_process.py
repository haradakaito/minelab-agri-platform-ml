import json
import pandas as pd
from tqdm import tqdm
from lib import AmpSignalProcessor

from lib import Util

if __name__ == "__main__":
    # 設定ファイルの読み込み
    with open(f"{Util.get_root_dir()}/config/config.json", "r") as f:
        config = json.load(f)

    # 共通ファイルを取得
    common_file = Util.get_common_files(path_list=[f"{Util.get_root_dir()}/data/adjusted-data/{field_device}/amp/" for field_device in config["AllDevice"]["Pcap"]])

    # 各ファイルに対して信号処理を適用
    for field_device in sorted(config["FieldDevice"]["Pcap"]):
        for file_name in tqdm(common_file):
            # ファイルのパスを取得
            file_path = f"{Util.get_root_dir()}/data/adjusted-data/{field_device}/amp/{file_name}"
            # データを読み込み（TimeカラムをIndexに設定）
            df = pd.read_csv(file_path, index_col=0).set_index("Time", drop=True).dropna(how="any").reset_index(drop=True)

            # 信号処理を適用
            sp = AmpSignalProcessor(df.copy())
            ## 未使用サブキャリア除去
            sp.remove_zero_subcarriers(inplace=True)
            ## 正規化スケーリング（サブキャリア平均）
            sp.normalize_by_mean(inplace=True)
            ## ハイパスフィルタ（静的成分除去）
            fs = sp.estimate_fs()
            sp.highpass_filter(cutoff=0.4, fs=fs, order=5, inplace=True)
            ## PCA（主成分抽出）
            sp.pca(n_components=1, inplace=True)
            ## スペクトログラム作成（STFT）
            sp.compute_spectrogram(column="PC1", fs=fs, nperseg=128, noverlap=64, inplace=True)

            # データを保存
            Util.create_path(f"{Util.get_root_dir()}/data/preprocessed-data/{field_device}/amp/")
            sp.df.to_csv(f"{Util.get_root_dir()}/data/preprocessed-data/{field_device}/amp/{file_name}", index=True)