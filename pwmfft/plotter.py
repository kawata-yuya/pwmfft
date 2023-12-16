from os import path

import matplotlib.pyplot as plt
import japanize_matplotlib

from .oscifft import DFTFFTProcessor

# 目盛りの向きを内側に設定
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'


class PWMPlotterAndCsvOut:
    """
    DFTFFTProcessorから得られたデータを可視化、
    CSVにて出力するためのプロッターとCSV出力クラス。

    Attributes
    ----------
    _target : DFTFFTProcessor
        可視化および出力対象のDFTFFTProcessorクラスのインスタンス。
    _input_filename : str
        入力データのファイル名。
    _output_directory_path : str
        出力ファイルを保存するディレクトリのパス。
    _number_of_outputs : int
        出力ファイルの通し番号。
    _FUNDAMENTAL_FREQUENCY : float
        基本周波数。
    _dpi : int
        出力ファイルの解像度（dots per inch）。

    Methods
    -------
    plot_frequency_contents()
        高調波含有率のグラフを生成し、保存する。
    plot_spectrum(max_plot_frequency=0.0, marker=False)
        スペクトラムのプロットを生成し、保存する。
    plot_waveform()
        電圧対時刻の波形をプロットし、保存する。
    save_dft_real_result()
        実数表現によるDFT結果をCSVファイルに保存する。
    save_frequency_contents_result(max_order=20, insert_invalid_contents=False)
        高調波含有率の結果をCSVファイルに保存する。
    save_total_total_harmonic_distribution()
        歪み率の結果をCSVファイルに保存する。
    """
    def __init__(
        self,
        target: DFTFFTProcessor,
        input_filename: str,
        output_file_directory_path: str,
        fundamental_frequency: float,
        dpi: int = 300,
        ):
        """
        PWMPlotterAndCsvOutの初期化メソッド。

        Parameters
        ----------
        target : DFTFFTProcessor
            DFTの結果を算出するDFTFFTProcessorクラスのインスタンス。
        input_filename : str
            入力ファイル名。
        output_file_directory_path : str
            出力ファイルを保存するディレクトリのパス。
        fundamental_frequency : float
            基本周波数。
        dpi : int, optional
            出力ファイルの解像度（デフォルトは300）。
        """
        self._target: DFTFFTProcessor = target
        self._input_filename: str = input_filename
        self._output_directory_path: str = output_file_directory_path
        self._number_of_outputs: int = 0
        self._FUNDAMENTAL_FREQUENCY = fundamental_frequency
        self._dpi = dpi

    def _get_output_filepath(self, filename, extension="png"):
        """
        出力ファイルのパスを取得するメソッド。

        Parameters
        ----------
        filename : str
            ファイル名。
        extension : str, optional
            ファイルの拡張子（デフォルトは"png"）。

        Returns
        -------
        str
            出力ファイルのパス。

        Notes
        -----
        このメソッドは内部でファイルの出力回数を管理し、
        出力ファイル名には通し番号が付与されます。

        Example
        -------
        >>> pwm_plotter = PWMPlotterAndCsvOut(target_instance, "input_file", "output_directory", 100)
        >>> pwm_plotter._get_output_filepath("高調波含有率")
        "output_directory/01_高調波含有率_input_file.png"
        >>> pwm_plotter._get_output_filepath("スペクトラム", "jpg")
        "output_directory/02_スペクトラム_input_file.jpg"
        """
        self._number_of_outputs += 1
        return path.join(
                self._output_directory_path,
                f"{self._number_of_outputs:02}_{filename}_{self._input_filename}.{extension}"
            )

    @property
    def dpi(self) -> int:
        """
        出力画像のDPIを取得します。

        Returns
        -------
        int
            出力画像のDPI。
        """
        return self._dpi

    @dpi.setter
    def dpi(self, value: int) -> None:
        """
        出力画像のDPIを設定します。

        Parameters
        ----------
        value : int
            設定するDPI。
        """
        if not isinstance(value, int) or value <= 0:
            raise ValueError("DPIは正の整数である必要があります。")
        self._dpi = value

    def plot_frequency_contents(
            self,
        ) -> None:
        """
        高調波含有率のグラフを生成し、指定されたファイルパスに保存します。
        """
        fig = plt.figure(figsize=(8, 6.5))
        plt.subplots_adjust(wspace=0.4, hspace=0.5)
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)

        ax1.grid()
        ax2.grid()
        ax1.set_xlabel("次数")
        ax2.set_xlabel("次数")
        ax1.set_ylabel("高調波含有率[%]")
        ax2.set_ylabel("高調波含有率[%]")
        ax1.set_title("(a) 基本波から500次まで", y=-0.35)
        ax2.set_title("(b) 基本波から20次まで",  y=-0.35)
        ax1.set_xlim(0, 500)
        ax2.set_xlim(0, 20)
        ax1.set_ylim(0, 120)
        ax2.set_ylim(0, 120)

        ax1.set_xticks([50*i for i in range(1, 11)])
        ax2.set_xticks([i for i in range(21)], [str(i) if i!=1 else '' for i in range(21)])

        ax1.text(-8, -30, "基\n本\n波")
        ax2.text(0.7, -30, "基\n本\n波")

        ax1.bar(range(501), self._target.get_frequency_contents(self._FUNDAMENTAL_FREQUENCY, 500), color="#000000", align="center", clip_on=False) 
        ax2.plot(range(21),  self._target.get_frequency_contents(self._FUNDAMENTAL_FREQUENCY, 20), marker="s", c="#000000", clip_on=False)


        plt.savefig(
            self._get_output_filepath("高調波含有率"),
            dpi=self._dpi
        )
        plt.close()
        return

    def plot_spectrum(
            self,
            max_plot_frequency:float=0.0,
            marker:bool=False,
        ):
        """
        スペクトラム（周波数対振幅）のプロットを生成し、指定されたファイルパスに保存します。

        Parameters
        ----------
        target : DFTFFTProcessor instance
            DFTの結果を算出するDFTFFTProcessorクラスのインスタンス。
        filepath : str
            グラフを保存するパス。
        title : str
            グラフのタイトル。
        max_plot_frequency : int, optional
            プロットする最大周波数。デフォルトは0（全範囲）。
        marker : bool, optional
            マーカー（データポイント）を表示するかどうか。デフォルトはFalse。
        """
        fig = plt.figure(figsize=(8, 6))

        if marker:
            plt.plot(self._target.frequency_for_real, self._target.amplitude_real, marker='s', c="#000000")
        else:
            plt.plot(self._target.frequency_for_real, self._target.amplitude_real, c="#000000")

        plt.xlabel('周波数[Hz]')
        plt.ylabel('振幅[V]')

        subtitle = ""
        if max_plot_frequency != 0:
            subtitle = f"~{max_plot_frequency}"
            plt.xlim(0, max_plot_frequency)
        else:
            subtitle = f"~{self._target.max_frequency}"
            plt.xlim(0, self._target.max_frequency)

        plt.ylim(0, self._target.amplitude_real.max()*1.2)

        plt.title(self._input_filename)

        plt.savefig(
            self._get_output_filepath(f"スペクトラム({subtitle})"), 
            dpi=self._dpi
        )
        plt.close()

    def plot_waveform(self):
        """
        電圧対時刻の波形をプロットし、指定されたパスに保存します。

        Parameters
        ----------
        self._target : DFTFFTProcessor instance
            DFTの結果を算出するDFTFFTProcessorクラスのインスタンス。
        filepath : str
            グラフを保存するパス。
        """
        fig = plt.Figure(figsize=(4,3))

        plt.plot(self._target.second_values, self._target.voltage_values, c='#000000')
        plt.grid()
        plt.xlim(-0.03, 0.03)

        plt.xlabel("時刻[s]")
        plt.ylabel("電圧[V]")

        plt.savefig(
            self._get_output_filepath("出力電圧波形"),
            dpi=self._dpi
        )
        plt.close()

    def save_dft_real_result(self):
        """
        実数表現によるDFT結果（周波数成分とその振幅）をCSVファイルに保存します。
        """
        self._target.save_dft_real_result(
            self._get_output_filepath("dft結果", "csv")
        )
    
    def save_frequency_contents_result(
            self,
            max_order = 20,
            insert_invalid_contents=False,
        ):
        """
        高調波含有率の結果をCSVファイルに保存します。

        Parameters
        ----------
        max_order : int, optional
            最大次数（デフォルトは20）。
        insert_invalid_contents : bool, optional
            最大倍数が分析可能な最大周波数を超えた場合に
            無効成分を挿入するかどうか（デフォルトはFalse）。
        """
        self._target.save_frequency_contents_result(
            filepath=self._get_output_filepath("高調波含有率_結果", "csv"),
            fundamental_frequency = self._FUNDAMENTAL_FREQUENCY,
            max_order = max_order,
            insert_invalid_contents = insert_invalid_contents,
        )
    
    def save_total_total_harmonic_distribution(self):
        """
        歪み率の結果をCSVファイルに保存します。
        """
        thd_tmp = self._target.get_total_harmonic_distribution(self._FUNDAMENTAL_FREQUENCY)
        with open(path.join(self._output_directory_path, "歪み率.csv"), "a") as f:
            f.write(f"{self._input_filename}, {thd_tmp}\n")
