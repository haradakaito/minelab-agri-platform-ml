import os
import sys
import logging
import traceback
from datetime import datetime

# エラーハンドラー
class ErrorHandler:
    """エラーハンドリングを行うクラス"""
    def __init__(self, log_file: str):
        """ログファイルを指定してエラーハンドラーを初期化"""
        self.log_file = log_file
        # log_fileのパスが存在しない場合は作成
        if not os.path.exists(log_file):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        # ログ設定を追加
        logging.basicConfig(
            filename=self.log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )

    def log_error(self, error: Exception) -> None:
        """エラーをログファイルに書き込む"""
        error_message = self._format_error_message(error)
        logging.error(error_message)
        # print(f"エラーが発生しました: {error_message}")

    def _format_error_message(self, error: Exception) -> str:
        """エラーの詳細を整形して文字列で返す"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 予期しないエラーの場合はトレースバックを含めたメッセージを取得
        # traceback_str = traceback.format_exc()
        return f"[{timestamp}] Unexpected Error: {error}"

    def handle_error(self, error: Exception) -> None:
        """エラーを処理するメソッド"""
        self.log_error(error)
        sys.exit(1)