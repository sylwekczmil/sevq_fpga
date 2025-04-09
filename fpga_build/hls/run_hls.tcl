# Create a project
open_project -reset vitis_hls_proj_for_main

# Add design files
add_files main.cpp
# Add test bench & files
add_files -tb main_test.cpp

# Set the top-level function
set_top top

# ########################################################
# Create a solution
open_solution -reset solution1
# Define technology and clock rate
set_part  {xc7z020clg400-1}
create_clock -period "100MHz"

# Run all
csim_design
csynth_design
cosim_design
export_design -version 1.0.0

exit