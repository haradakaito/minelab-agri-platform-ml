import os
import numpy as np

__all__ = ['read_pcap']

# Null および Pilot OFDMサブキャリアのインデックス
nulls = {
    20:  [x+32  for x in [-32, -31, -30, -29, 31, 30, 29, 0]],
    40:  [x+64  for x in [-64, -63, -62, -61, -60, -59, -1, 63, 62, 61, 60, 59, 1, 0]],
    80:  [x+128 for x in [-128, -127, -126, -125, -124, -123, -1, 127, 126, 125, 124, 123, 1, 0]],
    160: [x+256 for x in [-256, -255, -254, -253, -252, -251, -129, -128, -127, -5, -4, -3, -2, -1, 255, 254, 253, 252, 251, 129, 128, 127, 5, 4, 3, 3, 1, 0]]
}

pilots = {
    20:  [x+32  for x in [-21, -7, 21, 7]],
    40:  [x+64  for x in [-53, -25, -11, 53, 25, 11]],
    80:  [x+128 for x in [-103, -75, -39, -11, 103, 75, 39, 11]],
    160: [x+256 for x in [-231, -203, -167, -139, -117, -89, -53, -25, 231, 203, 167, 139, 117, 89, 53, 25]]
}

class SampleSet(object):
    """PCAPファイルから読み取ったデータを格納するヘルパークラス"""
    def __init__(self, samples, bandwidth, timestamps):
        self.rssi, self.fctl, self.mac, self.seq, self.css, self.csi = samples
        self.timestamps   = timestamps        # 受信時間を追加
        self.nsamples     = self.csi.shape[0] # サンプル数
        self.nsubcarriers = self.csi.shape[1] # サブキャリア数
        self.bandwidth    = bandwidth         # 帯域幅

    def get_rssi(self, index):
        """RSSIを取得"""
        return self.rssi[index]

    def get_fctl(self, index):
        """FCTLを取得"""
        return self.fctl[index]

    def get_mac(self, index):
        """MACアドレスを取得"""
        return self.mac[index*6: (index+1)*6]

    def get_seq(self, index):
        """シーケンス番号とフラグメント番号を取得"""
        sc = int.from_bytes(self.seq[index*2: (index+1)*2], byteorder='little', signed=False)
        fn = sc % 16
        sc = (sc - fn) // 16
        return (sc, fn)

    def get_css(self, index):
        """コアと空間ストリームを取得"""
        return self.css[index*2: (index+1)*2]

    def get_csi(self, index, rm_nulls=False, rm_pilots=False):
        """CSIを取得"""
        csi = self.csi[index].copy()
        if rm_nulls:
            csi[nulls[self.bandwidth]]  = 0
        if rm_pilots:
            csi[pilots[self.bandwidth]] = 0
        return csi

    def get_time(self, index):
        """受信時間を取得（開始からの相対時間）"""
        return self.timestamps[index]

    def print(self, index):
        """サンプルを表示"""
        macid  = self.get_mac(index).hex()
        macid  = ':'.join([macid[i:i+2] for i in range(0, len(macid), 2)])
        sc, fn = self.get_seq(index)
        css    = self.get_css(index).hex()
        rssi   = self.get_rssi(index)
        fctl   = self.get_fctl(index)
        time   = self.get_time(index)
        print(f'\nSample #{index}\n---------------\nSource Mac ID: {macid}\nSequence: {sc}.{fn}\nCore and Spatial Stream: 0x{css}\nRSSI: {rssi}\nFCTL: {fctl}\nTime: {time:.6f} sec\n')

def __find_bandwidth(incl_len):
    '''帯域幅を推定する'''
    pkt_len = int.from_bytes(incl_len, byteorder='little', signed=False)
    nbytes_before_csi = 60
    pkt_len += (128-nbytes_before_csi)
    bandwidth = 20*int(pkt_len//(20*3.2*4))
    return bandwidth

def __find_nsamples_max(pcap_filesize, nsub):
    """最大サンプル数を決定する"""
    return int((pcap_filesize-24)/(12+46+18+(nsub*4)))

def read_pcap(pcap_filepath, bandwidth=0, nsamples_max=0):
    """PCAPファイルからサンプルを読み取る"""
    pcap_filesize = os.stat(pcap_filepath).st_size
    with open(pcap_filepath, 'rb') as pcapfile:
        fc = pcapfile.read()

    if bandwidth == 0:
        bandwidth = __find_bandwidth(fc[32:36])
    nsub = int(bandwidth * 3.2)
    if nsamples_max == 0:
        nsamples_max = __find_nsamples_max(pcap_filesize, nsub)

    rssi = bytearray(nsamples_max * 1)
    fctl = bytearray(nsamples_max * 1)
    mac  = bytearray(nsamples_max * 6)
    seq  = bytearray(nsamples_max * 2)
    css  = bytearray(nsamples_max * 2)
    csi  = bytearray(nsamples_max * nsub * 4)
    timestamps = np.zeros(nsamples_max, dtype=np.float64)

    ptr = 24
    nsamples = 0
    first_timestamp = None

    while ptr < pcap_filesize:
        ts_sec  = int.from_bytes(fc[ptr:ptr+4], byteorder='little', signed=False)
        ts_usec = int.from_bytes(fc[ptr+4:ptr+8], byteorder='little', signed=False)
        timestamp = ts_sec + ts_usec / 1e6

        if first_timestamp is None:
            first_timestamp = timestamp

        timestamps[nsamples] = timestamp - first_timestamp

        ptr += 8
        frame_len = int.from_bytes(fc[ptr:ptr+4], byteorder='little', signed=False)
        ptr += 50

        rssi[nsamples] = fc[ptr+2]
        fctl[nsamples] = fc[ptr+3]
        mac[nsamples*6:(nsamples+1)*6] = fc[ptr+4:ptr+10]
        seq[nsamples*2:(nsamples+1)*2] = fc[ptr+10:ptr+12]
        css[nsamples*2:(nsamples+1)*2] = fc[ptr+12:ptr+14]
        csi[nsamples*(nsub*4):(nsamples+1)*(nsub*4)] = fc[ptr+18:ptr+18+nsub*4]

        ptr += (frame_len - 42)
        nsamples += 1

    csi_np = np.frombuffer(csi, dtype=np.int16, count=nsub * 2 * nsamples)
    csi_np = csi_np.reshape((nsamples, nsub * 2))
    csi_cmplx = np.fft.fftshift(csi_np[:, ::2] + 1.j * csi_np[:, 1::2], axes=(1,))
    rssi = np.frombuffer(rssi, dtype=np.int8, count=nsamples)

    return SampleSet((rssi, fctl, mac, seq, css, csi_cmplx), bandwidth, timestamps[:nsamples])

if __name__ == "__main__":
    samples = read_pcap('pcap_files/_sample.pcap')
    samples.print(0)
    samples.print(10)