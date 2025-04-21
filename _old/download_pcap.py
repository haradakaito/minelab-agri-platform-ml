import json
from lib import AWSHandler, ErrorHandler, Util

if __name__ == '__main__':
    try:
        # 設定ファイルの読み込み
        with open(f"{Util.get_root_dir()}/config/config.json") as f:
            config = json.load(f)

        # AWSハンドラを初期化
        aws_handler = AWSHandler(region_name='ap-northeast-1', bucket_name='minelab-iot-storage')

        for all_device in config["AllDevice"]["Pcap"]:
            Util.create_path(path=f'{Util.get_root_dir()}/data/pcap-data/{all_device}')
            # 指定した時間範囲のオブジェクトをダウンロード
            aws_handler.download_s3_objects(
                remote_path = f'projects/csi/pcap-data/{all_device}/',               # S3のプレフィックス
                local_path  = f'{Util.get_root_dir()}/data/pcap-data/{all_device}/', # ローカルパス
                start_time  = Util.get_timestamp(delta_hour=-24),                    # 開始時間
                end_time    = Util.get_timestamp()                                   # 終了時間
            )

    except Exception as e:
        # エラーハンドラを初期化
        handler = ErrorHandler(log_file=f'{Util.get_root_dir()}/log/{Util.get_exec_file_name()}.log')
        handler.handle_error(e)