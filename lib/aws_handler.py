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

# 使用例
if __name__ == "__main__":
    # AWSHandler インスタンス作成
    aws_handler = AWSHandler()
    # バケット名と対象フォルダ（プレフィックス）を指定
    bucket_name = "minelab-iot-storage"
    prefix = "projects/csi/image-data/"
    # フォルダ（ディレクトリ）一覧を取得
    directories = aws_handler.list_s3_directories(bucket_name, prefix)
    print("S3ディレクトリ一覧:")
    for directory in directories:
        print(directory)
    # ファイル一覧を取得
    files = aws_handler.list_s3_objects(bucket_name, prefix)
    print("\nS3ファイル一覧:")
    for file in files:
        print(file)