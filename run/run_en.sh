#!/bin/bash
# Run energy measurement experiments sequentially.

HOMED=/home/cappadokes
CODE=$HOMED/code
SAMOS=$HOMED/Desktop/phD/y345/research/pymm/samos22/${PYTHONRAT}
VENV=$SAMOS/tmp/venv
RESULTS=$SAMOS/results
MACHINE=laptop

export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$CODE/pyperf/pyperf/:/usr/local/ssl/lib/
export READEN=$CODE/pyperf/pyperf/libreaden.so

cd $CODE/pyperformance
$VENV/bin/python -m pip install .
cd $CODE/pyperf
$VENV/bin/python -m pip install .
#	Do not forget to align the runner python before starting!
python3 -m pip install $CODE/pyperformance

#	DRAM Energy
#export ENFILE=/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:2/energy_uj

# Jemalloc.
#$VENV/bin/python -m pyperf system tune
#PYTHONMALLOC=malloc LD_PRELOAD=$CODE/jemalloc/lib/libjemalloc.so.2 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,PYTHONMALLOC,LD_LIBRARY_PATH --venv $VENV --track-energy -o $RESULTS/jemalloc/$MACHINE/en_dram.json.gz

# pymalloc-jemalloc.
#$VENV/bin/python -m pyperf system tune
#LD_PRELOAD=$CODE/jemalloc/lib/libjemalloc.so.2 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,LD_LIBRARY_PATH --venv $VENV --track-energy -o $RESULTS/pymalloc_jemalloc/$MACHINE/en_dram.json.gz

# Baseline.
#$VENV/bin/python -m pyperf system tune
#python3 -m pyperformance run --rigorous --venv $VENV --track-energy --inherit-environ LD_LIBRARY_PATH -o $RESULTS/baseline/$MACHINE/en_dram.json.gz

# Malloc.
#$VENV/bin/python -m pyperf system tune
#PYTHONMALLOC=malloc python3 -m pyperformance run --rigorous --inherit-environ PYTHONMALLOC,LD_LIBRARY_PATH --venv $VENV --track-energy -o $RESULTS/malloc/$MACHINE/en_dram.json.gz

# Mimalloc.
#$VENV/bin/python -m pyperf system tune
#PYTHONMALLOC=malloc LD_PRELOAD=$CODE/mimalloc/out/release/libmimalloc.so.2.0 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,LD_LIBRARY_PATH,PYTHONMALLOC --venv $VENV --track-energy -o $RESULTS/mimalloc/$MACHINE/en_dram.json.gz

# pymalloc-mimalloc.
#$VENV/bin/python -m pyperf system tune
#LD_PRELOAD=$CODE/mimalloc/out/release/libmimalloc.so.2.0 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,LD_LIBRARY_PATH --venv $VENV --track-energy -o $RESULTS/pymalloc_mimalloc/$MACHINE/en_dram.json.gz

# CPU Energy
export ENFILE=/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj

# Jemalloc.
#$VENV/bin/python -m pyperf system tune
#PYTHONMALLOC=malloc LD_PRELOAD=$CODE/jemalloc/lib/libjemalloc.so.2 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,LD_LIBRARY_PATH,PYTHONMALLOC --venv $VENV --track-energy -o $RESULTS/jemalloc/$MACHINE/en_cpu.json.gz

# pymalloc-jemalloc.
#$VENV/bin/python -m pyperf system tune
#LD_PRELOAD=$CODE/jemalloc/lib/libjemalloc.so.2 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,LD_LIBRARY_PATH --venv $VENV --track-energy -o $RESULTS/pymalloc_jemalloc/$MACHINE/en_cpu.json.gz

# Baseline.
#$VENV/bin/python -m pyperf system tune
#python3 -m pyperformance run --rigorous --venv $VENV --inherit-environ LD_LIBRARY_PATH --track-energy -o $RESULTS/baseline/$MACHINE/en_cpu.json.gz

# Malloc.
#$VENV/bin/python -m pyperf system tune
#PYTHONMALLOC=malloc python3 -m pyperformance run --rigorous --inherit-environ PYTHONMALLOC,LD_LIBRARY_PATH --venv $VENV --track-energy -o $RESULTS/malloc/$MACHINE/en_cpu.json.gz

# Mimalloc.
$VENV/bin/python -m pyperf system tune
PYTHONMALLOC=malloc LD_PRELOAD=$CODE/mimalloc/out/release/libmimalloc.so.2.0 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,PYTHONMALLOC,LD_LIBRARY_PATH --venv $VENV --track-energy -o $RESULTS/mimalloc/$MACHINE/en_cpu.json.gz

# pymalloc-mimalloc.
$VENV/bin/python -m pyperf system tune
LD_PRELOAD=$CODE/mimalloc/out/release/libmimalloc.so.2.0 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,LD_LIBRARY_PATH --venv $VENV --track-energy -o $RESULTS/pymalloc_mimalloc/$MACHINE/en_cpu.json.gz

