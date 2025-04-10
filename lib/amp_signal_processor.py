import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, stft
from sklearn.decomposition import PCA

class AmpSignalProcessor:
    """振幅成分の信号処理クラス"""
    def __init__(self, df):
        self.df = df

    def remove_zero_subcarriers(self, inplace:bool=False) -> pd.DataFrame:
        """
        振幅成分のデータフレームから，全ての値が0のサブキャリア列を削除
        """
        # すべての値が0のサブキャリア列を削除
        df_non_null = self.df.loc[:, (self.df != 0).any(axis=0)]

        if inplace:
            self.df = df_non_null
        else:
            return df_non_null

    def normalize_by_mean(self, inplace:bool=False) -> pd.DataFrame:
        """
        各時刻ごとに，全サブキャリアの平均値で正規化された
        振幅成分（サブキャリア×時間）を返す
        """
        # 各時刻ごとに平均を計算
        df_mean = self.df.mean(axis=1)
        # 各値を各行の平均で除算して正規化
        df_norm = self.df.div(df_mean, axis=0)

        if inplace:
            self.df = df_norm
        else:
            return df_norm

    def estimate_fs(self) -> float:
        """
        インデックス（受信時刻）からサンプリング周波数（Hz）を推定する
        """
        # 差分を計算
        time_diffs = pd.Series(self.df.index).diff().dropna()
        # timedelta64型の場合は秒に変換
        if np.issubdtype(time_diffs.dtype, np.timedelta64):
            # timedelta64型の場合
            time_diffs = time_diffs.dt.total_seconds()
        # 平均間隔の逆数
        fs = 1.0 / time_diffs.mean()
        return fs

    def highpass_filter(self, cutoff:float=0.5, fs:float=50.0, order:int=5, inplace:bool=False) -> pd.DataFrame:
        """
        振幅成分にハイパスフィルタを適応し
        静的成分（低周波成分）を除去する
        """
        # Butterworthフィルタの係数設計
        nyq = 0.5*fs # ナイキスト周波数
        normal_cutoff = cutoff/nyq
        b, a = butter(order, normal_cutoff, btype="high", analog=False)
        # 各サブキャリアにフィルタを適用
        df_filtered = self.df.copy()
        for subcarrier in df_filtered.columns:
            df_filtered[subcarrier] = filtfilt(b, a, df_filtered[subcarrier])

        if inplace:
            self.df = df_filtered
        else:
            return df_filtered

    def pca(self, n_components:int=1, inplace=False) -> pd.DataFrame:
        """
        PCAによって振幅データ（時間×サブキャリア）から主成分を抽出する
        """
        # PCAを実行
        pca = PCA(n_components=n_components)
        transformed = pca.fit_transform(self.df.values)
        # 新しいデータフレームを作成
        columns = [f"PC{i+1}" for i in range(n_components)]
        df_pca  = pd.DataFrame(transformed, index=self.df.index, columns=columns)

        if inplace:
            self.df = df_pca
        else:
            return df_pca

    def compute_spectrogram(self, column:str="PC1", fs:float=50.0, nperseg:int=128, noverlap:int=64, inplace:bool=False) -> pd.DataFrame:
        """
        指定した列の時系列データからスペクトログラムを計算する（STFTベース）
        """
        # 指定した列の時系列データを取得
        series        = self.df[column].values
        signal_length = len(series)
        # STFTのパラメータを調整
        nperseg  = min(nperseg, signal_length)
        noverlap = min(noverlap, nperseg-1)
        # STFTを計算
        f, t, Zxx = stft(series, fs=fs, nperseg=nperseg, noverlap=noverlap)
        # STFTの絶対値（振幅スペクトル）を取り，データフレームに変換
        df_spec = pd.DataFrame(np.abs(Zxx).T, index=t, columns=f)

        if inplace:
            self.df = df_spec
        else:
            return df_spec