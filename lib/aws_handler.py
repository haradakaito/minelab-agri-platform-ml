import os
import boto3

class AWSHandler:
    """AWSの各種サービスを操作するためのハンドラクラス"""

    def __init__(self, region_name="ap-northeast-1"):
        self.s3_client = boto3.client('s3', region_name=region_name)

    def list_s3_directories(self, bucket_name, prefix):
        """指定したS3プレフィックス内のフォルダ一覧を取得"""
        response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
        if 'CommonPrefixes' in response:
            directories = [prefix_info['Prefix'] for prefix_info in response['CommonPrefixes']]
            return directories
        else:
            return []

    def list_s3_objects(self, bucket_name, prefix):
        """指定したS3プレフィックス内のすべてのオブジェクト（ファイル）一覧を取得"""
        objects = []
        response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            objects = [obj['Key'] for obj in response['Contents']]
        return objects

    def download_s3_objects(self, bucket_name, prefix, local_dir):
        """指定したS3プレフィックス内のすべてのオブジェクトをローカルにダウンロードする"""
        os.makedirs(local_dir, exist_ok=True)
        objects = self.list_s3_objects(bucket_name, prefix)
        for obj_key in objects:
            relative_path = obj_key[len(prefix):]  # プレフィックスを取り除いた相対パス
            local_path = os.path.join(local_dir, relative_path)
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            print(f"Downloading {obj_key} to {local_path} ...")
            self.s3_client.download_file(bucket_name, obj_key, local_path)
        print("Download complete.")

# 使用例
if __name__ == "__main__":
    aws_handler = AWSHandler()
    bucket_name = "minelab-iot-storage"
    prefix = "projects/csi/image-data/"
    local_download_path = "../data"

    # S3オブジェクトをローカルにダウンロード
    aws_handler.download_s3_objects(bucket_name, prefix, local_download_path)