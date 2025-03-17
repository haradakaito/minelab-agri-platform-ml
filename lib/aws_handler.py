import os
import boto3
from datetime import datetime as dt

class AWSHandler:
    """AWSの各種サービスを操作するためのハンドラクラス"""

    def __init__(self, region_name: str, bucket_name: str):
        """コンストラクタ"""
        self.s3_client      = boto3.client('s3', region_name=region_name)
        self.s3_bucket_name = bucket_name

    def _list_s3_objects(self, prefix: str) -> list:
        """指定したS3プレフィックス内のすべてのオブジェクト（ファイル）一覧を取得"""
        try:
            objects            = []   # オブジェクト一覧
            continuation_token = None # 継続トークン

            # ページネーションを使ってオブジェクト一覧を取得
            while True:
                # 継続トークンを指定してリクエスト
                if continuation_token:
                    response = self.s3_client.list_objects_v2(Bucket=self.s3_bucket_name, Prefix=prefix, ContinuationToken=continuation_token)
                else:
                    response = self.s3_client.list_objects_v2(Bucket=self.s3_bucket_name, Prefix=prefix)

                # レスポンスからオブジェクト一覧を取得
                if 'Contents' in response:
                    objects.extend(response['Contents'])
                # 継続トークンの確認（次のページがあるか）
                if response.get('IsTruncated'):
                    continuation_token = response['NextContinuationToken']
                else:
                    break
            return objects
        except Exception as e:
            raise e

    def _validation_time_range(self, start_time: str, end_time: str, timestamp_format: str) -> bool:
        """時間範囲のバリデーション"""
        start_dt = dt.strptime(start_time, timestamp_format)
        end_dt   = dt.strptime(end_time,   timestamp_format)
        return all([
            start_dt <= end_dt,
            0 <= start_dt.year   <= 9999, 0 <= end_dt.year   <= 9999, # 年は0以上9999以下
            1 <= start_dt.month  <= 12,   1 <= end_dt.month  <= 12,   # 月は1以上12以下
            1 <= start_dt.day    <= 31,   1 <= end_dt.day    <= 31,   # 日は1以上31以下
            0 <= start_dt.hour   <= 23,   0 <= end_dt.hour   <= 23,   # 時間は0以上23以下
            0 <= start_dt.minute <= 59,   0 <= end_dt.minute <= 59,   # 分は0以上59以下
            0 <= start_dt.second <= 59,   0 <= end_dt.second <= 59    # 秒は0以上59以下
        ])

    def download_s3_objects(self, remote_path: str, local_path: str, start_time: str, end_time: str) -> None:
        """
        指定した時間範囲内のS3オブジェクトをダウンロード

        params
        ------
        remote_path: str
            S3のプレフィックス
        local_path: str
            ローカルパス
        start_time: str
            開始時間
        end_time: str
            終了時間

        return
        ------
        None
        """

        timestamp_format = "%Y-%m-%dT%H-%M-%S" # タイムスタンプのフォーマット

        try:
            # 時間範囲のバリデーション
            if not self._validation_time_range(start_time=start_time, end_time=end_time, timestamp_format=timestamp_format):
                raise ValueError("時間範囲が不正です")

            # 指定したプレフィックス内の全オブジェクトを取得
            for object in self._list_s3_objects(prefix=remote_path):
                filename_ext = os.path.basename(object['Key'])                           # ファイル名（拡張子あり）
                timestamp    = dt.strptime(filename_ext.split('.')[0], timestamp_format) # ファイル名（タイムスタンプ）を取得

                # 指定した時間範囲内のファイルのみダウンロード（ローカルパスに保存）
                print(object['Key'])
                if dt.strptime(start_time, timestamp_format) <= timestamp <= dt.strptime(end_time, timestamp_format):
                    self.s3_client.download_file(self.s3_bucket_name, object['Key'], f"{local_path}{filename_ext}")
        except Exception as e:
            raise e

# 使用例
if __name__ == "__main__":
    # AWSハンドラの初期化
    aws_handler = AWSHandler(region_name="ap-northeast-1", bucket_name="minelab-iot-storage")
    # 指定した時間範囲のオブジェクトをダウンロード
    aws_handler.download_s3_objects(
        remote_path = "projects/csi/image-data/minelab-iot-camera-1",
        local_path  = "..data/image-data/minelab-iot-camera-1/",
        start_time  = "2025-03-13T00-00-00",
        end_time    = "2025-03-14T00-00-00"
    )