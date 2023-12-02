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
    oscillo_data = [{
        "object": OscilloscopeDftFromCsv(fname),
        "filepath": fname,
        "filename": path.splitext(path.basename(fname))[0],
    }  for fname in files]
    
    
    
    for target in oscillo_data:
        target["object"].read_csv()
        target["object"].dft()
    

    for target in oscillo_data:
        plot_waveform(
            target["object"],
            path.join(output_file_path, f"01出力電圧波形_{target['filename']}.png")
        )
        
        plot_frequency_contents(
            target["object"],
            path.join(output_file_path, f"02高調波含有率_{target['filename']}.png"),
            FUNDAMENTAL_FREQUENCY,
        )
        plot_spectrum(
            target["object"],
            path.join(output_file_path, f"03スペクトラム(小)_{target['filename']}.png"),
            max_plot_frequency=250,
            marker=True,
            title=target['filename'],
        )

        plot_spectrum(
            target["object"],
            path.join(output_file_path, f"04スペクトラム(大)_{target['filename']}.png"),
            max_plot_frequency=0,
            marker=False,
            title=target['filename'],
        )
        
        target['object'].save_dft_real_result(path.join(output_file_path, f"05dft結果_{target['filename']}.csv"),)
        
        print("歪み率[%]")
        print(f"{target['filename']}: {target['object'].get_total_harmonic_distribution(50)}%")
    

    return