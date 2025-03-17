import json
from lib import AWSHandler, ErrorHandler, Util

if __name__ == '__main__':
    try:
        # 設定ファイルの読み込み
        with open(f"{Util.get_root_dir()}/config/config.json") as f:
            config = json.load(f)

        # AWSハンドラを初期化
        aws_handler = AWSHandler(region_name='ap-northeast-1', bucket_name='minelab-iot-storage')

    except Exception as e:
        # エラーハンドラを初期化
        handler = ErrorHandler(log_file=f'{Util.get_root_dir()}/log/{Util.get_exec_file_name()}.log')
        handler.handle_error(e)