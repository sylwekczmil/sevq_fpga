cmake_minimum_required(VERSION 3.21)
project(sevq)

set(CMAKE_CXX_STANDARD 14)

include_directories(C:/Xilinx/Vitis_HLS/2020.2/include)
add_executable(sevq main.h main.cpp main_test.cpp)
