import sys
from pathlib import Path
from timeit import default_timer as timer

import pandas as pd

from algorithm import SEVQ
from dataset import ClassificationDataset
from util import accuracy, precision, recall, auc, f1

METRICS = (('AUC', auc), ('Accuracy', accuracy), ('Precision', precision), ('Recall', recall), ('F1', f1))


def run_on_arm_folds():
    result_path = Path("/home/xilinx/research/result2/")
    # shutil.rmtree(result_path, ignore_errors=True)
    result_path.mkdir(parents=True, exist_ok=True)

    ds_name = sys.argv[1]

    ds_result_path = result_path / f'{ds_name}.csv'

    if ds_result_path.exists():
        return

    records = []
    ds = ClassificationDataset(ds_name)
    for fold in ds.folds():
        try:
            print(f"running {ds.name} fold {fold.index}", flush=True)

            model = SEVQ()
            train_start_time = timer()
            labels = fold.labels
            model.fit(fold.x_train, fold.y_train)
            train_time = timer() - train_start_time
            pred_start_time = timer()
            pred = model.predict(fold.x_test)
            pred_time = timer() - pred_start_time

            result = {
                'Dataset': ds_name,
                'Algorithm': 'SEVQ',
                'Number of classes': len(set(fold.y_train)),
                'Train size': len(fold.x_train),
                'Test size': len(fold.x_test),
                'CV index': fold.index,
                'Train time [s]': train_time,
                'Prediction time [s]': pred_time
            }

            for (metric, metric_fun) in METRICS:
                result[metric] = metric_fun(fold.y_test, pred, labels)

            print(result, flush=True)
            records.append(result)

        except Exception as e:
            print(f'\n\n\nError while processing ds: {ds.name} \n\n\n', e, flush=True)
            return

    df = pd.DataFrame(records)
    df = df.sort_values(by=['Dataset', 'Algorithm', 'CV index'])
    df.to_csv(ds_result_path, index=False)


if __name__ == '__main__':
    run_on_arm_folds()
