import pandas as pd
import numpy as np
import collections
from tslearn.clustering import KShape

class SignalProcessor:
    """信号処理クラス"""
    def __init__(self, df):
        self.df = df

    def get_data(self):
        return self.df

    def remove_all_zero_col(self, inplace:bool=False):
        """全て0の列を削除"""
        try:
            df = self.df.copy()

            # 全て0の列を削除
            for col in df.columns:
                if (df[col] == 0).all():
                    df = df.drop(col, axis=1)

            # inplace=Trueの場合は元のdfを更新
            if inplace:
                self.df = df
                return self.df
            else:
                return df
        except Exception as e:
            raise e

    def remove_all_value_col(self, inplace:bool=False):
        """全て同じ値の列を削除"""
        try:
            df = self.df.copy()

            # 全て同じ値の列を削除
            for col in df.columns:
                if len(df[col].unique()) == 1:
                    df = df.drop(col, axis=1)

            # inplace=Trueの場合は元のdfを更新
            if inplace:
                self.df = df
                return self.df
            else:
                return df
        except Exception as e:
            raise e

    def hampel_filter(self, window_size:int=5, alpha:float=3.0, inplace:bool=False):
        """hampelフィルターを全ての列に適用"""
        try:
            df = self.df.copy()

            # hampelフィルターを全ての列に適用
            for col in df.columns:
                df[col] = self._hampel_filter_col(df[col].values, window_size, alpha)

            # inplace=Trueの場合は元のdfを更新
            if inplace:
                self.df = df
                return self.df
            else:
                return df
        except Exception as e:
            raise e

    def _hampel_filter_col(self, array:np.ndarray, window_size:int, alpha:float) -> np.ndarray:
        """
        Hampelフィルター

        params
        ------
        array: np.ndarray
            フィルターをかける配列
        window_size: int
            ウィンドウサイズ
        alpha: float
            閾値

        return
        ------
        np.ndarray
            フィルター後の配列
        """
        new_array   = array.copy()   # フィルター後の配列
        n           = len(array)     # 配列の長さ
        half_window = window_size//2 # ウィンドウサイズの半分

        # 各要素についてフィルターをかける
        for i in range(n):
            # ウィンドウの範囲を取得
            start  = max(0, i-half_window)   # 0以下にならないようにmaxを取る
            end    = min(n, i+half_window+1) # n以上にならないようにminを取る
            kernel = array[start:end]        # ウィンドウの範囲を取得

            # 中央値と尺度統計量を計算
            median = np.median(kernel)                 # 中央値
            mad    = np.median(np.abs(kernel-median))  # MAD (中央値絶対偏差)
            std    = 1.4826*mad                        # Hampelフィルターのスケールファクター

            # 外れ値の検出と置き換え
            if np.abs(array[i]-median) > alpha*std:
                new_array[i] = median
        return new_array

    def difference_filter(self, stride:int=1, inplace:bool=False):
        """差分フィルター"""
        try:
            df = self.df.copy()

            # 差分フィルター
            df = df.diff(stride)
            df = df.dropna(axis=0)
            df = df.reset_index(drop=True)

            # inplace=Trueの場合は元のdfを更新
            if inplace:
                self.df = df
                return self.df
            else:
                return df
        except Exception as e:
            raise e

    def standardize(self, inplace:bool=False):
        """標準化"""
        try:
            df = self.df.copy()

            # 標準化
            df = (df - df.mean()) / df.std()

            # inplace=Trueの場合は元のdfを更新
            if inplace:
                self.df = df
                return self.df
            else:
                return df
        except Exception as e:
            raise e

    def kshape_clustering(self, n_clusters:int=1, inplace:bool=False):
        """KShapeクラスタリング"""
        try:
            df = self.df.copy()

            # KShapeクラスタリング
            kshape = KShape(n_clusters=n_clusters, random_state=3407)
            kshape_base = kshape.fit(df.T.values)
            cnt = collections.Counter(kshape_base.labels_)
            cluster_labels_KS = {}
            for k in cnt:
                cluster_labels_KS['cluster-{}'.format(k)] = cnt[k]
            centroids = pd.DataFrame()
            for i in range(len(kshape_base.cluster_centers_)):
                centroids = pd.concat([centroids, pd.Series(kshape_base.cluster_centers_[i].reshape(len(kshape_base.cluster_centers_[i])))], axis=1)

            # inplace=Trueの場合は元のdfを更新
            if inplace:
                self.df = centroids
                return self.df
            else:
                return centroids
        except Exception as e:
            raise e