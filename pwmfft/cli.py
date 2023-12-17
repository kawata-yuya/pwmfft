from .oscifft import DFTFFTProcessor, OscilloCsvLoader
from .plotter import PWMPlotterAndCsvOut
import glob
from os import path, pardir

# 基本周波数
FUNDAMENTAL_FREQUENCY = 49.994

def main() -> None:
    # 現在のスクリプトファイルのディレクトリを取得
    current_dir = path.dirname(path.abspath(__file__))
    # 1つ上の階層のディレクトリパスを取得
    parent_dir = path.abspath(path.join(current_dir, pardir))
    output_file_path = path.join(parent_dir, "output")

    files = glob.glob("csv/*.csv")
    loader = OscilloCsvLoader()
    
    
    with open("歪み率.csv", "w") as f:
        f.write("filename, 歪み率[%]\n")

    for filepath in files:
        # ASCII形式のデータを読み込み
        loader.load_csv(filepath)
        oscillo_dft = DFTFFTProcessor.from_csv_loader(loader)
        # 読み込んだデータをDFT変換
        oscillo_dft.dft()
        
        # plot管理クラスの定義
        pwm_plot = PWMPlotterAndCsvOut(
            target=oscillo_dft,
            input_filename=path.splitext(path.basename(filepath))[0],
            output_file_directory_path=output_file_path,
            fundamental_frequency=FUNDAMENTAL_FREQUENCY,
        )
        
        # 電圧波形を出力
        pwm_plot.plot_waveform()
        
        # 周波数含有率のグラフを出力
        
        pwm_plot.plot_frequency_contents()
        
        # 考察用のスペクトラムを出力
        pwm_plot.plot_spectrum(
            max_plot_frequency=250.0,
            marker=True,
        )
        
        # 考察用のスペクトラムを出力
        pwm_plot.plot_spectrum(
            marker=False,
        )
        
        # DFT変換の結果をcsvファイルに保存
        pwm_plot.save_dft_real_result()
        pwm_plot.save_frequency_contents_result()
        
        # 歪み率の保存
        pwm_plot.save_total_total_harmonic_distribution()

    return