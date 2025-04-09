import pandas as pd
from cacp.comparison import DEFAULT_METRICS
from cacp.plot import process_comparison_results_plots
from cacp.result import process_comparison_results
from cacp.time import process_times
from cacp.winner import process_comparison_result_winners

from research.const import THIS_PATH, RESULT_DIR, RESULT_CSV

if __name__ == '__main__':
    result_fpga_dfs = [pd.read_csv(p) for p in (THIS_PATH / "result").glob('*.csv')]
    result_arm_dfs = [pd.read_csv(p) for p in (THIS_PATH / "result2").glob('*.csv')]

    result_fpga_df = pd.concat(result_fpga_dfs)
    result_arm_df = pd.concat(result_arm_dfs)

    result = pd.concat((result_fpga_df, result_arm_df))

    RESULT_DIR.mkdir(exist_ok=True, parents=True)
    result.to_csv(RESULT_CSV, index=False)

    process_comparison_results(RESULT_DIR, DEFAULT_METRICS)
    process_comparison_results_plots(RESULT_DIR, DEFAULT_METRICS)
    process_comparison_result_winners(RESULT_DIR, DEFAULT_METRICS)
    process_times(RESULT_DIR)
