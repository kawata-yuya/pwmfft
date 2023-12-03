from .oscifft import OscilloscopeDftFromCsv
from .plotter import plot_frequency_contents, plot_spectrum, plot_waveform
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
    oscillo_dft = OscilloscopeDftFromCsv()
    
    oscillo_data_info = {
        "filepath": "",
        "filename": "",
    }
    
    for filepath in files:
        oscillo_data_info = {
            "filepath": filepath,
            "filename": path.splitext(path.basename(filepath))[0],
        }
        
        # ASCII形式のデータを読み込み
        oscillo_dft.read_csv(oscillo_data_info['filepath'])
        # 読み込んだデータをDFT変換
        oscillo_dft.dft()
        
        # 電圧波形を出力
        plot_waveform(
            oscillo_dft,
            path.join(output_file_path, f"01出力電圧波形_{oscillo_data_info['filename']}.png")
        )
        
        # 周波数含有率のグラフを出力
        plot_frequency_contents(
            oscillo_dft,
            path.join(output_file_path, f"02高調波含有率_{oscillo_data_info['filename']}.png"),
            FUNDAMENTAL_FREQUENCY,
        )
        
        # 考察用のスペクトラムを出力
        plot_spectrum(
            oscillo_dft,
            path.join(output_file_path, f"03スペクトラム(小)_{oscillo_data_info['filename']}.png"),
            max_plot_frequency=250,
            marker=True,
            title=oscillo_data_info['filename'],
        )

        # 考察用のスペクトラムを出力
        plot_spectrum(
            oscillo_dft,
            path.join(output_file_path, f"04スペクトラム(大)_{oscillo_data_info['filename']}.png"),
            max_plot_frequency=0,
            marker=False,
            title=oscillo_data_info['filename'],
        )
        
        # DFT変換の結果をcsvファイルに保存
        oscillo_dft.save_dft_real_result(path.join(output_file_path, f"05dft結果_{oscillo_data_info['filename']}.csv"),)
        oscillo_dft.save_frequency_contents_result(
            filepath=path.join(output_file_path, f"06高調波含有率_結果_{oscillo_data_info['filename']}.csv"),
            fundamental_frequency=FUNDAMENTAL_FREQUENCY,
            max_order=20,
            insert_invalid_contents=False
        )
        
        # 歪み率の表示
        print("歪み率[%]")
        total_harmonic_distribution = oscillo_dft.get_total_harmonic_distribution(FUNDAMENTAL_FREQUENCY)
        print(f"{oscillo_data_info['filename']}: {total_harmonic_distribution}%")
    

    return