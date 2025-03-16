from lib import AWSHandler, ErrorHandler, Util

if __name__ == '__main__':
    try:
        # AWSハンドラを初期化
        aws_handler = AWSHandler(region_name='ap-northeast-1', bucket_name='minelab-iot-storage')

        # 時間範囲を設定（現在時刻から24時間以内）
        start_time = Util.get_timestamp(delta_hour=-24)
        end_time   = Util.get_timestamp()

        # 指定した時間範囲のオブジェクトをダウンロード
        aws_handler.download_s3_objects_within_time_range(
            base_prefix    = 'projects/csi/pcap-data/',                 # プレフィックス
            local_base_dir = f'{Util.get_root_dir()}/data/pcap-data/',  # ローカルディレクトリ
            start_time     = start_time,                                # 開始時間
            end_time       = end_time                                   # 終了時間
        )

    except Exception as e:
        # エラーハンドラを初期化
        handler = ErrorHandler(log_file=f'{Util.get_root_dir()}/log/{Util.get_exec_file_name()}.log')
        handler.handle_error(e)