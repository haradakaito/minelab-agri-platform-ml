import numpy as np
import sys
sys.setrecursionlimit(10**6)

class TimeAdjuster:
    """受信時刻補正を行うクラス"""
    def __init__(self, df_dict: dict, alpha: float):
        self.df_dict = df_dict # データフレームの辞書
        self.alpha   = alpha   # 標準偏差の閾値
        self.rm_idx  = set()   # 除去する行のインデックス

    def calc_idx_time_std(self, idx: int) -> float:
        """time_dictの任意の列"""
        idx_time_list = [float(self.df_dict[key]["Time"][idx]) for key in self.df_dict.keys()]
        return np.nanstd(idx_time_list)

    def calc_idx_time_argmax(self, idx: int) -> int:
        """最大値の列を計算する"""
        idx_time_list = [float(self.df_dict[key]["Time"][idx]) for key in self.df_dict.keys()]
        return np.nanargmax(idx_time_list)

    def shift_idx_time(self, key: str, idx: int) -> None:
        """指定した行を1つ後ろにずらす"""
        df                = self.df_dict[key]      # データフレーム
        df.loc[len(df)]   = np.nan                 # 末尾に行を追加
        df.iloc[idx+1:]   = df.iloc[idx:-1].values # idx行以降を1つシフト
        df.iloc[idx]      = np.nan                 # idx行を空にする
        self.df_dict[key] = df                     # 更新

    def adjust_time(self, start) -> None:
        """受信時刻の補正を行う"""
        for idx in range(start, len(self.df_dict[list(self.df_dict.keys())[0]]["Time"])):
            # 標準偏差が閾値を超える場合
            if self.calc_idx_time_std(idx) <= self.alpha:
                continue
            # 最大値の列を計算
            argmax = self.calc_idx_time_argmax(idx)
            key    = list(self.df_dict.keys())[argmax]
            # 指定した行を1つ後ろにずらす
            self.shift_idx_time(key, idx)
            self.rm_idx.add(idx)
            return idx
        # rm_idxに含まれる行を全てのデータフレームから削除
        for key in self.df_dict.keys():
            self.df_dict[key] = self.df_dict[key].drop(self.rm_idx).reset_index(drop=True)
        return True

    def judge_df_shape(self) -> bool:
        """データフレームの形状が一致しているか判定する"""
        shape = [self.df_dict[key].shape[0] for key in self.df_dict.keys()]
        return shape
        # return len(set(shape)) == 1