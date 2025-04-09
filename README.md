## Environment setup
* PYNQ image v2.7 https://pynq.readthedocs.io/en/latest/pynq_sd_card.html
* above PYNQ image requires Xilinx Tools with version 2020.2 https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools/2020-2.html
* PYNQ vivado files `build/board_files/pynq-z*`, copy to your Vivado installation, in the ./data/boards/board_files directory.
* PYNQ board available in local network

## Scripts

* Script to build the overlay [run_fpga_build.py](run_fpga_build.py)
* Script to run experiments on PYNQ FPGA [run_fpga_experiment.py](run_fpga_experiment.py)
* Scripts to run experiments on PYNQ ARM [run_fpga_experiment2.py](run_fpga_experiment2.py)

All of this scripts should be run on your PR, they will copy the code to PYNQ.
