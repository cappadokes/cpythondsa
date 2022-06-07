#! /bin/bash
#	Run time, memory and energy measurements both for debug and release versions.

export PYTHONRAT=naked_debug
./run_tm_jm.sh
./run_en.sh
#export PYTHONRAT=naked_debug
#./run_time_mem.sh
#./run_en.sh
