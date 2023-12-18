from .plotter import PWMPlotterAndCsvOut
from .oscifft import DFTFFTProcessor
from .oscifft import OscilloCsvLoader

from os import path, makedirs, getcwd
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Process oscillo data and generate PWM plots.")
    parser.add_argument("inputfiles", nargs="+", help="Input CSV file(s)")
    parser.add_argument("--dpi", type=int, default=100, help="DPI for output plots")
    parser.add_argument("--outputdir", default="output", help="Output directory path")
    parser.add_argument("-f", "--fundamentalfrequency", type=float, default=50.0, help="Fundamental frequency")
    return parser.parse_args()

def main() -> None:
    now_dir = getcwd()
    args = parse_args()

    output_file_path = path.join(now_dir, args.outputdir)

    # 出力ディレクトリが存在しない場合は新規作成
    if not path.exists(output_file_path):
        makedirs(output_file_path)
        
    loader = OscilloCsvLoader()

    output_csv_path = path.join(output_file_path, "歪み率.csv")
    with open(output_csv_path, "w") as f:
        f.write("filename, 歪み率[%]\n")

    for filepath in args.inputfiles:
        oscillo_data_info = {
            "filepath": filepath,
            "filename": path.splitext(path.basename(filepath))[0],
        }

        # ASCII形式のデータを読み込み
        loader.load_csv(oscillo_data_info["filepath"])
        oscillo_dft = DFTFFTProcessor.from_csv_loader(loader)
        # 読み込んだデータをDFT変換
        oscillo_dft.dft()

        pwm_plot = PWMPlotterAndCsvOut(
            target=oscillo_dft,
            input_filename=oscillo_data_info["filename"],
            output_file_directory_path=output_file_path,
            fundamental_frequency=args.fundamentalfrequency,
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
