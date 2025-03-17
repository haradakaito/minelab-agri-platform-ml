import os
import sys
import netifaces
import socket
import base64
from datetime import datetime, timedelta
from pathlib import Path

class Util:
    """ユーティリティクラス"""
    @staticmethod
    def get_mac_address(interface: str = "wlan0") -> str:
        """MACアドレスを取得する関数"""
        try:
            mac_address = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
            return mac_address
        except Exception as e:
            raise e

    @staticmethod
    def get_root_dir() -> Path:
        """プロジェクトのルートディレクトリを取得する関数"""
        try:
            root_dir = Path(__file__).resolve().parent.parent
            return root_dir
        except Exception as e:
            raise e

    @staticmethod
    def get_device_name() -> str:
        """デバイス名を取得する関数"""
        try:
            device_name = socket.gethostname()
            return device_name
        except Exception as e:
            raise e

    @staticmethod
    def get_timestamp(delta_hour: int = 0) -> str:
        """タイムスタンプを取得する関数"""
        # 「YYYY-MM-DDThh-mm-ss」形式で取得
        try:
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            if delta_hour != 0:
                timestamp = (datetime.now() + timedelta(hours=delta_hour)).strftime("%Y-%m-%dT%H-%M-%S")
            return timestamp
        except Exception as e:
            raise e

    @staticmethod
    def encode_base64(data: bytes) -> str:
        """バイナリデータをBase64エンコードする関数"""
        try:
            encoded_data = base64.b64encode(data).decode('utf-8')
            return encoded_data
        except Exception as e:
            raise e

    @staticmethod
    def create_path(path: str) -> None:
        """指定パスを作成する関数"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except Exception as e:
            raise e

    @staticmethod
    def get_exec_file_name():
        """実行ファイル名を取得する関数"""
        try:
            return os.path.splitext(os.path.basename(sys.argv[0]))[0]
        except Exception as e:
            raise e

    @staticmethod
    def get_dir_list(path: str) -> list:
        """指定したパス内のすべてのディレクトリ名をリストで返す関数"""
        try:
            return sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
        except Exception as e:
            raise e

    @staticmethod
    def get_file_name_list(path: str, ext: str) -> list:
        """指定したパス内のすべてのファイル名をリストで返す関数"""
        try:
            return sorted([f for f in os.listdir(path) if f.endswith(ext) and os.path.isfile(os.path.join(path, f))])
        except Exception as e:
            raise e

    @staticmethod
    def remove_extension(file_name: str) -> str:
        """指定したファイル名の拡張子を外す"""
        try:
            return os.path.splitext(file_name)[0]
        except Exception as e:
            raise e

    @staticmethod
    def get_alphabet_list(num: int) -> list:
        """アルファベットリストを取得する関数"""
        try:
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            alphabet_list = []
            for i in range(num):
                if i < 26:
                    alphabet_list.append(alphabet[i])
                else:
                    alphabet_list.append(alphabet[i//26-1] + alphabet[i%26])
            return alphabet_list
        except Exception as e:
            raise e

    @staticmethod
    def get_common_files(*path) -> list:
        try:
            common_files = []
            for i, p in enumerate(path):
                if i == 0:
                    common_files = set(Util.get_file_name_list(p, ""))
                else:
                    common_files = common_files & set(Util.get_file_name_list(p, ""))
            return sorted(list(common_files))
        except Exception as e:
            raise e

# 使用例
if __name__ == "__main__":
    try:
        # MACアドレスを取得
        mac_address = Util.get_mac_address()
        print("MAC Address:", mac_address)
        # ルートディレクトリを取得
        root_dir = Util.get_root_dir()
        print("Root Directory:", root_dir)
        # タイムスタンプを取得
        timestamp = Util.get_timestamp()
        print("Timestamp:", timestamp)
        # デバイス名を取得
        device_name = Util.get_device_name()
        print("Device Name:", device_name)
        # バイナリデータをBase64エンコード
        data = b"Hello, World!"
        encoded_data = Util.encode_base64(data)
        print("Encoded Data:", encoded_data)
        # ディレクトリを作成
        Util.create_path(path="/home/pi/minelab-agri-platform/minelab-iot-gateway/pcap/minelab-iot-nexmon-1")
        # 実行ファイル名を取得
        print("Exec FileName: ", Util.get_exec_file_name())
        # ディレクトリ名を取得
        print("DirList: ", Util.get_dir_list(path="/home/pi"))
        # ファイル名を取得
        print("FileList: ", Util.get_file_name_list(path="/home/pi/", ext=".csv"))
        # 拡張子を外す
        print("FileName(No Ext): ", Util.remove_extension(file_name="sample.csv"))
        # アルファベットリストを取得
        print("Alphabet List: ", Util.get_alphabet_list(50))
        # 共通ファイルを取得
        print("Common Files: ", Util.get_common_files(
            "/home/pi/minelab-agri-platform/minelab-iot-gateway/pcap/minelab-iot-nexmon-1",
            "/home/pi/minelab-agri-platform/minelab-iot-gateway/pcap/minelab-iot-nexmon-2"
        ))
    except Exception as e:
        print(e)