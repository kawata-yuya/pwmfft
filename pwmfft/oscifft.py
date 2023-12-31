import numpy as np
from numpy.fft import fft, fftfreq, ifft

NULL_ARRAY = np.array([])       # np.empty(0)

class OscilloCsvLoader:
    """
    CSVファイルから波形データを読み込むためのクラス。

    Attributes
    ----------
    _filename : str
        CSVファイル名
    _second_values : np.ndarray
        時間軸のデータを保持する1次元NumPy配列。
    _voltage_values1 : np.ndarray
        チャンネル1の電圧データを保持する1次元NumPy配列。
    _voltage_values2 : np.ndarray
        チャンネル2の電圧データを保持する1次元NumPy配列。存在しない場合はNULL_ARRAY。
    _has_2ch : bool
        チャンネル2が存在するかどうかを示すブール値。

    Methods
    -------
    load_csv(filename: str)
        CSVファイルを読み込み、データを対応する属性に保存する。
    """
    def __init__(self):
        self._filename: str = ''
        self._second_values:   np.ndarray = NULL_ARRAY
        self._voltage_values1: np.ndarray = NULL_ARRAY
        self._voltage_values2: np.ndarray = NULL_ARRAY
        self._has_2ch: bool = False
        
    def load_csv(self, filename: str) -> None:
        """
        CSVファイルを読み込み、
        _second_valuesと_voltage_values1、
        _voltage_values2(ch2が存在する場合)の
        配列にデータを保存します。

        Parameters
        ----------
        filename : str
            CSVファイル名。

        Raises
        ------
        Exception
            指定したファイルが見つからない場合に発生します。
        """
        
        # すでに別のファイルを読み込んでいた場合は初期化
        if self._filename != "":
            self.__init__()
        
        self._filename = filename
        
        try:
            _matrix_tmp =  np.loadtxt(
                fname=self._filename,
                dtype=np.float64, 
                delimiter=',',
                skiprows=2,
            ).T

            if _matrix_tmp.shape[0] == 2:
                self._second_values, self._voltage_values1 = _matrix_tmp
            else:
                self._has_2ch = True
                self._second_values   = _matrix_tmp[0]
                self._voltage_values1 = _matrix_tmp[1]
                self._voltage_values2 = _matrix_tmp[2]
        
        except FileNotFoundError:
            raise Exception('有効なcsvファイルが見つかりませんでした。')
    
    @property
    def second_values(self):
        return self._second_values
    
    @property
    def voltage_values1(self):
        return self._voltage_values1
    
    @property
    def voltage_values2(self):
        return self._voltage_values2
    
    @property
    def has_2ch(self):
        return self._has_2ch


class DFTFFTProcessor:
    """
    オシロスコープデータを管理し、DFT変換を行うクラス

    Attributes
    ----------
    _second_values : np.ndarray
        時間軸のデータを保持する1次元NumPy配列。
    _voltage_values : np.ndarray
        電圧データを保持する1次元NumPy配列。
    _frequency_for_complex : np.ndarray
        複素数表現の周波数の配列。
    _frequency_for_real : np.ndarray
        実数表現の周波数の配列（半分のサイズ）。
    _amplitude_complex : np.ndarray
        周波数に対する振幅（複素数）。
    _amplitude_real : np.ndarray
        周波数に対する振幅（実数）。
    _max_frequency : float
        最大の周波数。
    _min_frequency : float
        最小の周波数。
    _number_of_sample : int
        サンプル数。
    _sampling_time : float
        サンプリング時間。
    _sampling_period : float
        サンプリング周期。

    Methods
    -------
    __init__(second_values: np.ndarray, voltage_values: np.ndarray)
        DFTFFTProcessorクラスのインスタンスを初期化する。
    from_csv_loader(loader: OscilloCsvLoader, ch: int=1) -> DFTFFTProcessor
        OscilloCsvLoaderからDFTFFTProcessorを生成するクラスメソッド。
    dft() -> None
        Discrete Fourier Transform（離散フーリエ変換）を実行し、周波数と振幅を計算する。
    get_frequency_component(f: float) -> float
        指定した周波数に最も近い周波数成分の振幅を返す。
    get_frequency_components(a: float, b: float) -> np.ndarray
        2つの周波数範囲で周波数成分の振幅を返す。
    get_frequency_contents(fundamental_frequency: float, max_order: int, insert_invalid_contents: bool=True) -> np.ndarray
        基本周波数の倍数の最大次数までの振幅の配列を返す。
    get_total_harmonic_distribution(fundamental_frequency: float) -> float
        基本周波数に対する歪み率を計算する。
    get_particular_frequencies_waveform(min_freq: float, max_freq: float) -> Tuple[np.ndarray, np.ndarray]
        特定の周波数範囲のみを出力波形から取り出し、電圧波形を返す。
    save_dft_real_result(filepath: str) -> None
        実数表現によるDFT結果をCSVファイルに保存する。
    save_frequency_contents_result(filepath: str, fundamental_frequency: float, max_order: int, insert_invalid_contents: bool=True) -> None
        高調波含有率の結果をCSVファイルに保存する。
    """
    def __init__(
        self,
        second_values:  np.ndarray,
        voltage_values: np.ndarray,
    ):
        """
        DFTFFTProcessorクラスのインスタンスを初期化する。

        Parameters
        ----------
        second_values : np.ndarray
            時間軸のデータを保持する1次元NumPy配列。
        voltage_values : np.ndarray
            電圧データを保持する1次元NumPy配列。
        """
        self._second_values: np.array  = second_values
        self._voltage_values: np.array = voltage_values
        self._frequency_for_complex: np.array = NULL_ARRAY
        self._frequency_for_real:    np.array = NULL_ARRAY         # Half size
        self._amplitude_complex:     np.array = NULL_ARRAY
        self._amplitude_real:        np.array = NULL_ARRAY
        
        self._max_frequency: float = 0.0
        self._min_frequency: float = 0.0
        
        self._number_of_sample: int = 0
        self._sampling_time:  float = 0.0
        self._sampling_period:float = 0.0
    
    @classmethod
    def from_csv_loader(
        cls,
        loader: OscilloCsvLoader,
        ch: int=1,
    ) -> 'DFTFFTProcessor':
        """
        OscilloCsvLoaderからDFTFFTProcessorを生成するクラスメソッド。

        Parameters
        ----------
        loader : OscilloCsvLoader
            OscilloCsvLoaderのインスタンス。
        ch : int, optional
            チャンネル番号（デフォルトは1）。

        Returns
        -------
        DFTFFTProcessor
        
        Raises
        ------
        ValueError
            ch=2と指定されたが、loaderには2chの情報がない場合に発生します。
        """
        if ch == 1:
            return cls(loader.second_values, loader.voltage_values1)
        elif ch == 2:
            if not loader.has_2ch:
                raise ValueError("ch=2としましたが、loderには2chの情報はありませんでした。")
            return cls(loader.second_values, loader.voltage_values2)
    
    # 各属性のゲッターは以下の通りです。それぞれのゲッターは対応する属性を返します。
    # 属性は内部的に変更可能でありながら外部からは読み取り専用となります。
    @property
    def frequency_for_complex(self) -> np.ndarray:
        return self._frequency_for_complex
    
    @property
    def frequency_for_real(self) -> np.ndarray:
        return self._frequency_for_real

    @property
    def amplitude_complex(self) -> np.ndarray:
        return self._amplitude_complex
    
    @property
    def amplitude_real(self) -> np.ndarray:
        return self._amplitude_real
    
    @property
    def second_values(self) -> np.ndarray:
        return self._second_values
    
    @property
    def voltage_values(self) -> np.ndarray:
        return self._voltage_values
    
    @property
    def sampling_time(self) -> float:
        return self._sampling_time
    
    @property
    def max_frequency(self) -> float:
        return self._max_frequency
    
    @property
    def min_frequency(self) -> float:
        return self._min_frequency
        
    def dft(self) -> None:
        """
        Discrete Fourier Transform（離散フーリエ変換）を実行します。
        サンプリング数、サンプリング時間、サンプリング期間を計算し、
        複素数表現および実数表現の周波数と振幅を計算します。
        """
        self._number_of_sample = len(self._second_values)
        self._sampling_time= np.max(self._second_values) - np.min(self._second_values)
        self._sampling_period = self._sampling_time / self._number_of_sample

        self._frequency_for_complex = fftfreq(
            n=self._number_of_sample,
            d=self._sampling_period,
        )
        self._frequency_for_real = self._frequency_for_complex[:self._number_of_sample//2]
        
        self._max_frequency = self._frequency_for_real.max()
        self._min_frequency = self._frequency_for_real.min()
        
        self._amplitude_complex = fft(self._voltage_values)
        self._amplitude_real = np.abs(self._amplitude_complex[:self._number_of_sample//2]) * 2.0 / self._number_of_sample
        self._amplitude_real[0] /= 2.0
        
        return

    def get_frequency_component(self, f: float) -> float:
        """
        指定した周波数に最も近い周波数成分の振幅を返します。

        Parameters
        ----------
        f : float
            振幅を取得したい周波数。

        Returns
        -------
        float
            指定した周波数付近の振幅。
        """
        near_index = np.argmin((self._frequency_for_real - f)**2)
        return self._amplitude_real[near_index]
    
    def get_frequency_components(self, a:float, b:float) -> float:
        """
        2つの周波数範囲で周波数成分の振幅を返します。

        Parameters
        ----------
        a : float
            範囲の最小周波数。
        b : float
            範囲の最大周波数。

        Returns
        -------
        float
            指定した範囲の振幅。
        """
        start_near_index = np.argmin((self._frequency_for_real - a)**2)
        end_near_index   = np.argmin((self._frequency_for_real - b)**2)
        if start_near_index == end_near_index:
            return np.array(self.get_frequency_component(a))
        
        return self._amplitude_real[start_near_index:end_near_index]
    
    def get_frequency_contents(
            self,
            fundamental_frequency:float,
            max_order:int,
            insert_invalid_contents:bool=True,
        ) -> np.ndarray:
        """
        与えられた基本周波数の倍数の最大次数までの
        振幅の配列(0次を含む)を返します。

        Parameters
        ----------
        fundamental_frequency : float
            基本周波数
        max_order : int
            最大次数
        insert_invalid_contents : bool, optional
            最大倍数が分析可能な最大周波数を超えた場合に
            無効成分を挿入するかどうか（デフォルトはTrue）。

        Returns
        -------
        np.ndarray
            基本周波数の倍数ごとの振幅の配列(0次を含む)。
            各振幅は基本周波数成分の振幅で正規化され、パーセント表記されます。
        """
        
        if (not insert_invalid_contents and 
            max_order*fundamental_frequency > self._max_frequency):
            max_order = int(self._max_frequency / fundamental_frequency)
        
        return np.array([
            self.get_frequency_component(fundamental_frequency*i)
            for i in range(max_order+1)]) / self.get_frequency_component(fundamental_frequency)*100.0
        
    def get_total_harmonic_distribution(
        self,
        fundamental_frequency:float,
        ) -> float:
        """
        基本周波数に対する歪み率の計算

        Parameters
        ----------
        fundamental_frequency : float
            基本周波数

        Returns
        -------
        float
            歪み率[%]
        """
        
        _frequency_contents = self.get_frequency_contents(fundamental_frequency,
                                                            99999, False)
        
        return float(np.sqrt((_frequency_contents[2:]**2).sum()))
    
    def get_particular_frequencies_waveform(
            self,
            min_freq:float,
            max_freq:float
        ):
        """
        特定の周波数範囲のみを出力波形から取り出し、電圧波形を出力するメソッド。

        Parameters
        ----------
        min_freq : float
            最小周波数。
        max_freq : float
            最大周波数。

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            時間軸のデータと特定の周波数範囲内の電圧波形。
        """
        upper_conditions = np.abs(self._frequency_for_complex) >= min_freq
        lower_conditions = np.abs(self._frequency_for_complex) <= max_freq
        dones_meet_conditions = upper_conditions and lower_conditions
        
        amplitude = np.where(dones_meet_conditions, self._amplitude_complex, 0)
        
        return self._second_values, ifft(amplitude)
    
    
    def save_dft_real_result(self, filepath):
        """
        実数表現によるDFT結果（周波数成分とその振幅）をCSVファイルに保存します。

        Parameters
        ----------
        filepath : str
            結果を保存するCSVファイルのパス。

        Notes
        -----
        CSVファイルはカンマで区切られ、ヘッダーには"frequency[Hz], amplitude[V]"が含まれます。
        frequency[Hz]列は周波数成分、amplitude[V]列はその振幅を表します。
        """
        save_arr = np.stack([self.frequency_for_real, self.amplitude_real], axis=1)
        np.savetxt(
            fname=filepath,
            X=save_arr,
            delimiter=',',
            header="frequency[Hz], amplitude[V]"
        )
    
    def save_frequency_contents_result(
            self,
            filepath:str,
            fundamental_frequency:float,
            max_order:int,
            insert_invalid_contents:bool=True,
        ) -> None:
        """
        高調波含有率の結果をCSVファイルに保存します。

        Parameters
        ----------
        filepath : str
            CSVを保存するパス。
        fundamental_frequency : float
            基本周波数
        max_order : int
            最大次数
        insert_invalid_contents : bool, optional
            最大倍数が分析可能な最大周波数を超えた場合に
            無効成分を挿入するかどうか（デフォルトはTrue）。
        
        Notes
        -----
        CSVファイルはカンマで区切られ、
        ヘッダーには"order, voltage[V], content[%]"が含まれます。
        order列は次数、content[％]列はその高調波含有率を表します。
        """

        frequency_contents = self.get_frequency_contents(
            fundamental_frequency=fundamental_frequency,
            max_order=max_order,
            insert_invalid_contents=insert_invalid_contents,
        )
        frequency_contents_voltage = frequency_contents * self.get_frequency_component(fundamental_frequency) / 100.0

        save_arr = np.stack([np.arange(frequency_contents.shape[0]), frequency_contents_voltage, frequency_contents], axis=1)
        np.savetxt(
            fname=filepath,
            X=save_arr,
            delimiter=',',
            header="order, voltage[V], content[%]"
        )
    
