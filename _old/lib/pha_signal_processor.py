import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
from scipy.signal import stft

class PhaSignalProcessor:
    """位相成分の信号処理クラス"""
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

    def upwrap_phase(self, inplace:bool=False) -> pd.DataFrame:
        """
        各サブキャリアのラップされた位相をアンラップして連続値に変換する
        """
        # 位相をアンラップ
        df_unwrap = self.df.copy()
        for col in df_unwrap.columns:
            df_unwrap[col] = np.unwrap(df_unwrap[col].values)

        if inplace:
            self.df = df_unwrap
        else:
            return df_unwrap

    def remove_linear_drift(self, inplace: bool = False) -> pd.DataFrame:
        """
        各時刻ごとにサブキャリア方向に線形回帰を行い、
        ドリフト成分（傾き＋オフセット）を除去した位相成分を返す
        """

        # 現在の列ラベル（文字列）を数値インデックスに置き換え
        numeric_columns = list(range(len(self.df.columns)))
        df_numeric = self.df.copy()
        df_numeric.columns = numeric_columns

        df_corrected = pd.DataFrame(index=self.df.index, columns=self.df.columns)

        # 線形回帰：時刻ごと（行単位）に処理
        subcarriers = np.array(numeric_columns).reshape(-1, 1)
        for t in df_numeric.index:
            phi_t               = df_numeric.loc[t].values.reshape(-1, 1)
            model               = LinearRegression().fit(subcarriers, phi_t)
            drift               = model.predict(subcarriers).flatten()
            corrected           = phi_t.flatten() - drift
            df_corrected.loc[t] = corrected

        df_corrected = df_corrected.astype(float)

        if inplace:
            self.df = df_corrected
        else:
            return df_corrected

    def pca(self, n_components:int=1, inplace=False) -> pd.DataFrame:
        """
        PCAによって位相データ（時間×サブキャリア）から主成分を抽出する
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
        # STFTの絶対値（位相スペクトル）を取り，データフレームに変換
        df_spec = pd.DataFrame(np.abs(Zxx).T, index=t, columns=f)

        if inplace:
            self.df = df_spec
        else:
            return df_spec