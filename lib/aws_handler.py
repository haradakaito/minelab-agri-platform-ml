import os
import boto3
from datetime import datetime
from dateutil import parser

class AWSHandler:
    """AWSの各種サービスを操作するためのハンドラクラス"""

    def __init__(self, region_name: str, bucket_name: str):
        """コンストラクタ"""
        self.s3_client      = boto3.client('s3', region_name=region_name)
        self.s3_bucket_name = bucket_name

    def _list_s3_objects(self, prefix: str) -> list:
        """
        指定したS3プレフィックス内のすべてのオブジェクト（ファイル）一覧を取得

        params
        ------
        prefix: str
            S3のプレフィックス（ディレクトリ）パス

        return
        ------
        objects: list
            オブジェクト一覧（dictのリスト）
        """
        objects = []
        continuation_token = None
        # ページネーションを使ってオブジェクト一覧を取得
        while True:
            # 継続トークンを指定してリクエスト
            if continuation_token:
                response = self.s3_client.list_objects_v2(
                    Bucket = self.s3_bucket_name,          # バケット名
                    Prefix = prefix,                       # プレフィックス
                    ContinuationToken = continuation_token # 継続トークン
                )
            else:
                response = self.s3_client.list_objects_v2(
                    Bucket = self.s3_bucket_name, # バケット名
                    Prefix = prefix               # プレフィックス
                )

            # レスポンスからオブジェクト一覧を取得
            if 'Contents' in response:
                objects.extend(response['Contents'])
            # 継続トークンがあれば次のページを取得
            if response.get('IsTruncated'):
                continuation_token = response['NextContinuationToken']
            else:
                break
        return objects

    def _validation_time_range(self, start_time: str, end_time: str) -> bool:
        """指定した時間範囲のバリデーションを行い，問題がなければ True を返す"""
        try:
            start_dt = parser.parse(start_time)
            end_dt   = parser.parse(end_time)
            return all([
                start_dt <= end_dt,
                0 <= start_dt.year   <= 9999, 0 <= end_dt.year   <= 9999, # 年は0以上9999以下
                1 <= start_dt.month  <= 12,   1 <= end_dt.month  <= 12,   # 月は1以上12以下
                1 <= start_dt.day    <= 31,   1 <= end_dt.day    <= 31,   # 日は1以上31以下
                0 <= start_dt.hour   <= 23,   0 <= end_dt.hour   <= 23,   # 時間は0以上23以下
                0 <= start_dt.minute <= 59,   0 <= end_dt.minute <= 59,   # 分は0以上59以下
                0 <= start_dt.second <= 59,   0 <= end_dt.second <= 59    # 秒は0以上59以下
            ])

        except Exception:
            return False

    def download_s3_objects_within_time_range(self, base_prefix: str, local_base_dir: str, start_time: str, end_time: str):
        """
        指定した時間範囲のオブジェクトをローカルにダウンロードする

        params
        ------
        base_prefix: str
            S3のプレフィックス（ディレクトリ）パス
        local_base_dir: str
            ダウンロード先のローカルディレクトリパス
        start_time: str
            ダウンロード開始時間（ISO 8601形式）
        end_time: str
            ダウンロード終了時間（ISO 8601形式）

        return
        ------
        None
        """

        # 時間範囲のバリデーション
        if not self._validation_time_range(start_time, end_time):
            raise ValueError("時間範囲が不正です")

        # 指定したプレフィックス内の全オブジェクトを取得
        for object in self._list_s3_objects(prefix=base_prefix):
            s3_key = object['Key']
            # S3キーから日付情報を抽出
            try:
                filename      = os.path.basename(s3_key)                              # ファイル名
                timestamp_str = filename.split('.')[0]                                # タイムスタンプ部分
                file_dt       = datetime.strptime(timestamp_str, "%Y-%m-%dT%H-%M-%S") # ファイルの日時
            except Exception as e:
                print(f"エラー: {s3_key} -> {e}")
                continue

            # 指定した時間範囲内のファイルのみ処理
            if parser.parse(start_time) <= file_dt <= parser.parse(end_time):
                relative_path   = s3_key[len(base_prefix):]                   # プレフィックスを除いた相対パス
                local_file_path = os.path.join(local_base_dir, relative_path) # ローカルファイルパス
                # 必要なディレクトリを作成
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                # ダウンロード
                self.s3_client.download_file(self.s3_bucket_name, s3_key, local_file_path)
                print(f"Downloaded: {s3_key} -> {local_file_path}")

# 使用例
if __name__ == "__main__":
    # AWSハンドラの初期化
    aws_handler = AWSHandler(region_name="ap-northeast-1", bucket_name="minelab-iot-storage")
    # 指定した時間範囲のオブジェクトをダウンロード
    aws_handler.download_s3_objects_within_time_range(
        base_prefix    = "projects/csi/image-data/",
        local_base_dir = "/home/csi/minelab-agri-platform-ml/__dev__/harada/data/image-data/",
        start_time     = "2025-03-12T00:00:00",
        end_time       = "2025-03-13T00:00:00"
    )