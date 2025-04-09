import shutil
import subprocess
from pathlib import Path

from run_fpga_experiment import DATASETS, copy_source_files


def run_script(ds_name):
    command = "ssh xilinx@pynq sudo bash /home/xilinx/jupyter_notebooks/sevq/run2.sh " + ds_name
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    for line in process.stdout:
        print(line.decode("utf-8"), end="")


def copy_output_file(ds_name):
    source_path = Path(f'//pynq/xilinx/research/result2/{ds_name}.csv')
    out_path = Path(__file__).parent.joinpath('research', 'result2', f'{ds_name}.csv')
    out_path.parent.mkdir(exist_ok=True, parents=True)
    print('Copy', source_path, out_path)
    shutil.copy(source_path, out_path)


if __name__ == '__main__':
    copy_source_files()
    for ds_name in DATASETS:
        run_script(ds_name)
        copy_output_file(ds_name)
