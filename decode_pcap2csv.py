import json
import importlib
import numpy as np
import pandas as pd
from lib import Util, ErrorHandler

def decode_pcap2csv(decoder, pcap_path: str, save_path: str, filename: str) -> None:
    """
    PCAPファイルをCSVファイルに変換する関数

    params
    ------
    decoder: object
        デコーダークラス
    pcap_path: str
        PCAPファイルのパス
    save_path: str
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
        Util.create_path(f"{save_path}/amp") # ディレクトリが存在しない場合は作成
        Util.create_path(f"{save_path}/pha") # ディレクトリが存在しない場合は作成
        df_amp.to_csv(f"{save_path}/amp/{filename.replace('.pcap', '.csv')}")
        df_pha.to_csv(f"{save_path}/pha/{filename.replace('.pcap', '.csv')}")

    except Exception as e:
        # エラーハンドラを初期化
        handler = ErrorHandler(log_file=f'{Util.get_root_dir()}/log/{Util.get_exec_file_name()}.log')
        handler.log_error(e)

if __name__ == '__main__':
    try:
        # 設定ファイルの読み込み
        with open('config/config.json', 'r') as file:
            config = json.load(file)

        # デコード対象のパスを取得
        timestamp = Util.get_timestamp(delta_hour=-24)    # 24時間前のタイムスタンプを取得
        year      = timestamp.split('T')[0].split('-')[0] # 年
        month     = timestamp.split('T')[0].split('-')[1] # 月
        day       = timestamp.split('T')[0].split('-')[2] # 日

        # ファイル名のリストを取得
        # MEMO: ネストが深いのでリファクタリングが必要
        pcap_root_path  = f"{Util.get_root_dir()}/data/pcap-data"
        basic_time_path = f"year={year}/month={month}/day={day}"
        for dirname in Util.get_dir_list(path=pcap_root_path):
            try:
                for hour in Util.get_dir_list(path=f"{pcap_root_path}/{dirname}/{basic_time_path}"):
                    for minute in Util.get_dir_list(path=f"{pcap_root_path}/{dirname}/{basic_time_path}/{hour}"):
                        for filename in Util.get_file_name_list(path=f"{pcap_root_path}/{dirname}/{basic_time_path}/{hour}/{minute}", ext='.pcap'):
                            # PCAPファイルをCSVファイルに変換
                            decode_pcap2csv(
                                decoder   = importlib.import_module(f"lib.interleaved"),
                                pcap_path = f"{pcap_root_path}/{dirname}/{basic_time_path}/{hour}/{minute}",
                                save_path = f"{Util.get_root_dir()}/data/csv-data/{dirname}/{basic_time_path}/{hour}/{minute}",
                                filename  = filename
                            )

            except Exception as e:
                # エラーハンドラを初期化
                handler = ErrorHandler(log_file=f'{Util.get_root_dir()}/log/{Util.get_exec_file_name()}.log')
                handler.log_error(e)
                continue

    except Exception as e:
        # エラーハンドラを初期化
        handler = ErrorHandler(log_file=f'{Util.get_root_dir()}/log/{Util.get_exec_file_name()}.log')
        handler.handle_error(e)
