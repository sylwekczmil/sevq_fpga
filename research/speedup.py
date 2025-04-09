import pandas as pd

from fpga_experiment.dataset import ClassificationDataset
from research.const import RESULT_CSV, RESULT_DIR

if __name__ == '__main__':
    df = pd.read_csv(RESULT_CSV)
    g = df.groupby('Algorithm')
    fpga = df[df['Algorithm'] == "FPGA"].groupby('Dataset').mean()
    arm = df[df['Algorithm'] == "ARM"].groupby('Dataset').mean()

    speedup_df = pd.DataFrame()
    speedup_df['ARM processing time [s]'] = arm['Train time [s]'] + arm['Prediction time [s]']
    speedup_df['FPGA processing time [s]'] = fpga['Train time [s]'] + fpga['Prediction time [s]']

    speedup_df['Speed up'] = speedup_df['ARM processing time [s]'] / speedup_df['FPGA processing time [s]']

    speedup_df.reset_index(inplace=True)
    speedup_df = speedup_df.rename(columns={'index': 'Dataset'})
    speedup_df = speedup_df.sort_values('Speed up', ascending=False)


    def get_number_of_records(x):
        return ClassificationDataset(x['Dataset']).instances


    def get_number_of_attrs(x):
        return ClassificationDataset(x['Dataset']).features


    speedup_df['Instances'] = speedup_df.apply(get_number_of_records, axis=1)
    speedup_df['Attributes'] = speedup_df.apply(get_number_of_attrs, axis=1)

    speedup_df = speedup_df[['Dataset', 'Instances', 'Attributes',
                             'ARM processing time [s]', 'FPGA processing time [s]',
                             'Speed up']]

    print(speedup_df['Speed up'].mean())
    speedup_df.to_csv(RESULT_DIR / "speedup.csv", index=False)
