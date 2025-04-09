import shutil
import subprocess
from pathlib import Path


def copy_source_files():
    source_dir_path = Path(__file__).parent.joinpath('fpga_experiment')
    out_dir_path = Path(f'//pynq/xilinx/jupyter_notebooks/sevq')

    for p in source_dir_path.glob('*.py'):
        print('Copy', p, out_dir_path)
        shutil.copy(p, out_dir_path)

    for p in source_dir_path.glob('*.sh'):
        print('Copy', p, out_dir_path)
        shutil.copy(p, out_dir_path)


def run_script(ds_name):
    command = "ssh xilinx@pynq sudo bash /home/xilinx/jupyter_notebooks/sevq/run.sh " + ds_name
    print(command)
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    for line in process.stdout:
        print(line.decode("utf-8"), end="")


def copy_output_file(ds_name):
    source_path = Path(f'//pynq/xilinx/research/result/{ds_name}.csv')
    out_path = Path(__file__).parent.joinpath('research', 'result', f'{ds_name}.csv')
    out_path.parent.mkdir(exist_ok=True, parents=True)
    print('Copy', source_path, out_path)
    shutil.copy(source_path, out_path)


DATASETS = [
    "abalone",
    "appendicitis",
    "automobile",
    "balance",
    "banana",
    "bands",
    "breast",
    "bupa",
    "car",
    "chess",
    "cleveland",
    "contraceptive",
    "dermatology",
    "ecoli",
    "flare",
    "german",
    "glass",
    "hayes-roth",
    "heart",
    "hepatitis",
    "housevotes",
    "ionosphere",
    "iris",
    "led7digit",
    "lymphography",
    "mammographic",
    "marketing",
    "monk-2",
    "mushroom",
    "newthyroid",
    "phoneme",
    "pima",
    "post-operative",
    "saheart",
    "satimage",
    "segment",
    "tae",
    "texture",
    "thyroid",
    "tic-tac-toe",
    "titanic",
    "twonorm",
    "vehicle",
    "vowel",
    "wine",
    "winequality-red",
    "winequality-white",
    "wisconsin",
    "yeast",
    "zoo",
]

if __name__ == '__main__':
    copy_source_files()
    for ds_name in DATASETS:
        run_script(ds_name)
        copy_output_file(ds_name)
