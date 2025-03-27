import json
import importlib
import numpy as np
import pandas as pd
from lib import Util, ErrorHandler

def decode_pcap2csv(decoder, pcap_path: str, csv_path: str, filename: str) -> None:
    """
    PCAPファイルをCSVファイルに変換する関数

    params
    ------
    decoder: object
        デコーダークラス
    pcap_path: str
        PCAPファイルのパス
    csv_path: str
        保存先のパス
    filename: str
        ファイル名

    return
    ------
    None
    """
    try:
        # データの読み込み
        samples = decoder.read_pcap(pcap_filepath=f"{pcap_path}/{filename}")

        # データの抽出
        df_amp  = pd.DataFrame([np.abs(samples.get_csi(index=index, rm_nulls=True, rm_pilots=False)) for index in range(samples.nsamples)])   # 振幅
        df_pha  = pd.DataFrame([np.angle(samples.get_csi(index=index, rm_nulls=True, rm_pilots=False)) for index in range(samples.nsamples)]) # 位相
        df_time = pd.DataFrame([samples.get_time(index=index) for index in range(samples.nsamples)])                                          # 受信時刻

        # 受信時間を先頭カラムに追加
        df_amp = pd.concat([df_time, df_amp], axis=1)
        df_pha = pd.concat([df_time, df_pha], axis=1)

        # カラム名の変更
        df_amp.columns = ['Time'] + Util.get_alphabet_list(num=df_amp.shape[1]-1)
        df_pha.columns = ['Time'] + Util.get_alphabet_list(num=df_pha.shape[1]-1)

        # CSVファイルに保存
        Util.create_path(f"{csv_path}/amp")
        Util.create_path(f"{csv_path}/pha")
        df_amp.to_csv(f"{csv_path}/amp/{Util.remove_extension(file_name=filename)}.csv")
        df_pha.to_csv(f"{csv_path}/pha/{Util.remove_extension(file_name=filename)}.csv")

    except Exception as e:
        # エラーハンドラを初期化
        handler = ErrorHandler(log_file=f'{Util.get_root_dir()}/log/{Util.get_exec_file_name()}.log')
        handler.log_error(e)

if __name__ == '__main__':
    try:
        # 設定ファイルの読み込み
        with open(f'{Util.get_root_dir()}/config/config.json', 'r') as f:
            config = json.load(f)

        # PCAPファイルのデコード
        for field_device in config["FieldDevice"]["Pcap"]:
            for filename in Util.get_file_name_list(path=f"{Util.get_root_dir()}/data/pcap-data/{field_device}", ext='.pcap'):
                # PCAPファイルをCSVファイルに変換
                decode_pcap2csv(
                    decoder   = importlib.import_module(f"lib.interleaved"),
                    pcap_path = f"{Util.get_root_dir()}/data/pcap-data/{field_device}",
                    csv_path  = f"{Util.get_root_dir()}/data/csv-data/{field_device}",
                    filename  = filename
                )

    except Exception as e:
        # エラーハンドラを初期化
        handler = ErrorHandler(log_file=f'{Util.get_root_dir()}/log/{Util.get_exec_file_name()}.log')
        handler.handle_error(e)
