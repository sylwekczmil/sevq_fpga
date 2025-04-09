#!/usr/bin/env bash
set -e
export XILINX_XRT=/usr
source /etc/profile.d/pynq_venv.sh
python3 /home/xilinx/jupyter_notebooks/sevq/run.py $1