import matplotlib.pyplot as plt
import japanize_matplotlib

from .oscifft import OscilloscopeDftFromCsv

# 目盛りの向きを内側に設定
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'


def plot_frequency_contents(
        target:OscilloscopeDftFromCsv,
        filepath:str,
        fundamental_frequency:float,
    ) -> None:
    """
    高調波含有率のグラフを生成し、指定されたファイルパスに保存します。

    Parameters
    ----------
    target : OscilloscopeDftFromCsv instance
        DFTの結果を算出するOscilloscopeDftFromCsvクラスのインスタンス。
    filepath : str
        グラフを保存するパス。
    fundamental_frequency : float
        基本周波数
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
    
    ax1.bar(range(501), target.get_frequency_contents(fundamental_frequency, 500), color="#000000", align="center", clip_on=False) 
    ax2.plot(range(21),  target.get_frequency_contents(fundamental_frequency, 20), marker="s", c="#000000", clip_on=False)

    
    plt.savefig(filepath, dpi=300)
    plt.close()
    return

def plot_spectrum(
        target:OscilloscopeDftFromCsv,
        filepath:str,
        title:str,
        max_plot_frequency:float=0.0,
        marker:bool=False,
    ):
    """
    スペクトラム（周波数対振幅）のプロットを生成し、指定されたファイルパスに保存します。

    Parameters
    ----------
    target : OscilloscopeDftFromCsv instance
        DFTの結果を算出するOscilloscopeDftFromCsvクラスのインスタンス。
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
        plt.plot(target.frequency_for_real, target.amplitude_real, marker='s', c="#000000")
    else:
        plt.plot(target.frequency_for_real, target.amplitude_real, c="#000000")
    
    plt.xlabel('周波数[Hz]')
    plt.ylabel('振幅[V]')
    
    if max_plot_frequency != 0:
        plt.xlim(0, max_plot_frequency)
    else:
        plt.xlim(0, target.max_frequency)

    plt.ylim(0, target.amplitude_real.max()*1.2)
    
    plt.title(title)
    
    plt.savefig(filepath, dpi=300)
    plt.close()

def plot_waveform(target: OscilloscopeDftFromCsv, filepath:str):
    """
    電圧対時刻の波形をプロットし、指定されたパスに保存します。

    Parameters
    ----------
    target : OscilloscopeDftFromCsv instance
        DFTの結果を算出するOscilloscopeDftFromCsvクラスのインスタンス。
    filepath : str
        グラフを保存するパス。
    """
    fig = plt.Figure(figsize=(4,3))
    
    plt.plot(target.second_values, target.voltage_values, c='#000000')
    plt.grid()
    plt.xlim(-0.03, 0.03)

    plt.xlabel("時刻[s]")
    plt.ylabel("電圧[V]")
    
    plt.savefig(filepath)
    plt.close()
