import os
import shutil
import time
from pathlib import Path

from fpga_build.tools import FpgaBuildTools


class FpgaBuildRunner:

    @staticmethod
    def cleanup(in_directory: str):
        for item in os.listdir(in_directory):
            if item.startswith('vivado') or item.startswith('vitis') or item == '.Xil' or item == 'NA':
                file_path = os.path.join(in_directory, item)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

    def build(self, in_dir: str, project_name='sevq', run_hls=True, run_vivado=True, cleanup_before=True,
              copy_bit_file=True):

        if cleanup_before:
            self.cleanup(in_dir)

        build_tools = FpgaBuildTools()

        if run_hls:
            build_tools.vitis_hls_run('run_hls.tcl', in_directory=in_dir)
        if run_vivado:
            build_tools.vivado_run('-mode batch -source run_vivado.tcl', in_directory=in_dir)

        if copy_bit_file:
            bit_file = f"{in_dir}/vivado_project/vivado_project.runs/impl_1/vivado_design_wrapper.bit"
            hwh_file = f"{in_dir}/vivado_project/vivado_project.gen/sources_1/bd/vivado_design/hw_handoff/vivado_design.hwh"

            seconds_from_start = 0
            while not os.path.exists(bit_file):
                print(f'Waiting for bit file for {seconds_from_start}s')
                time.sleep(10)
                seconds_from_start += 10

            time.sleep(5)

            shutil.copy(bit_file, f'{in_dir}/overlay.bit')
            shutil.copy(hwh_file, f'{in_dir}/overlay.hwh')

            print(f'Build done, bitstream copied to: {in_dir}.')

            out_dir_path = Path(f'//pynq/xilinx/overlays/{project_name}')
            out_dir = str(out_dir_path)
            try:
                out_dir_path.mkdir(exist_ok=True, parents=True)
                shutil.copy(bit_file, f'{out_dir}/overlay.bit')
                shutil.copy(hwh_file, f'{out_dir}/overlay.hwh')
                print(f'Build done, bitstream copied to: {out_dir}.')
            except Exception as e:
                print(f'Could not copy bitstream to: {out_dir}.')

        print('End')
