import pandas as pd
from cacp.util import to_latex

from research.combine import RESULT_DIR
from research.const import ARTICLE_DIR

if __name__ == '__main__':
    speedup_df = pd.read_csv(RESULT_DIR / "speedup.csv")
    speedup_df['ARM processing time [s]'] = speedup_df['ARM processing time [s]'].apply(lambda x: "{:.3f}".format(x))
    speedup_df['FPGA processing time [s]'] = speedup_df['FPGA processing time [s]'].apply(lambda x: "{:.3f}".format(x))
    speedup_df['Speed up'] = speedup_df['Speed up'].apply(lambda x: "{:.3f}".format(x))
    speedup_df.index += 1
    speedup_df.style.hide(axis="index")
    with ARTICLE_DIR.joinpath('speedup.tex').open("w") as f:
        latex = to_latex(
            speedup_df,
            caption='Processing time comparison',
            label=f'tab:time'
        )
        latex = "\n".join("&".join(l.split('&')[1:]) if '&' in l else l for l in latex.split('\n'))
        f.write(latex)

    utilization_df = pd.read_csv(RESULT_DIR / "utilization.csv")
    utilization_df['Utilization'] = utilization_df['Utilization'].apply(lambda x: "{:.0f}".format(x))
    utilization_df['Available'] = utilization_df['Available'].apply(lambda x: "{:.0f}".format(x))
    utilization_df['Utilization %'] = utilization_df['Utilization %'].apply(lambda x: "{:.3f}".format(x))
    utilization_df.index += 1

    with ARTICLE_DIR.joinpath('utilization.tex').open("w") as f:
        latex = to_latex(
            utilization_df,
            caption='Resource utilization',
            label=f'tab:utilization'
        )
        latex = "\n".join("&".join(l.split('&')[1:]) if '&' in l else l for l in latex.split('\n'))
        f.write(latex)
