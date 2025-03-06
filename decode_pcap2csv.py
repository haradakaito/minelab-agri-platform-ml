import json
import importlib
import numpy as np
import pandas as pd

if __name__ == '__main__':
    try:
        # 設定ファイルの読み込み
        with open('config/config.json', 'r') as file:
            config = json.load(file)

        # デコーダの読み込み
        decoder = importlib.import_module(f"lib.{config['Decoder']}")

        # ファイル名の入力
        filename = input("ファイル名を入力してください：")
        # 拡張子がない場合は付与
        if filename == "":
            filename = config["DefaultFile"]
        elif not filename.endswith('.pcap'):
            filename += '.pcap'

        # データの読み込み
        print("データの読み込みを開始します")
        samples = decoder.read_pcap(pcap_filepath=f"{config['InputPath']}/{filename}")

        # データの抽出
        print("データの抽出を開始します")
        csi_amp = [np.abs(samples.get_csi(index=index, rm_nulls=True, rm_pilots=False)) for index in range(samples.nsamples)]   # 振幅
        csi_pha = [np.angle(samples.get_csi(index=index, rm_nulls=True, rm_pilots=False)) for index in range(samples.nsamples)] # 位相

        # データをcsvで保存
        print("データの保存を開始します")
        df_amp = pd.DataFrame(csi_amp)
        df_pha = pd.DataFrame(csi_pha)
        df_amp.to_csv(f"{config['OutputPath']}/amp/{filename.replace('.pcap', '.csv')}")
        df_pha.to_csv(f"{config['OutputPath']}/pha/{filename.replace('.pcap', '.csv')}")
        print(f"変換が完了しました\n振幅データ：{config['OutputPath']}/amp/{filename.replace('.pcap', '.csv')}\n位相データ{config['OutputPath']}/pha/{filename.replace('.pcap', '.csv')}")

    except Exception as e:
        print(f"エラーが発生しました：{e}")
