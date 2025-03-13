from lib import AWSHandler, ErrorHandler, Util

if __name__ == '__main__':
    try:
        # AWSハンドラを初期化
        aws_handler = AWSHandler()

    except Exception as e:
        # エラーハンドラを初期化
        handler = ErrorHandler(log_file=f'{Util.get_root_dir()}/log/{Util.get_exec_file_name()}.log')
        handler.handle_error(e)