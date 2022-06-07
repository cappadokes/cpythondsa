#!/bin/bash
# Run time and memory measurement experiments sequentially.
# ATTENTION: This script makes important assumptions with
# regard to the server's directory structure! Use with caution
# and understand what you're doing.

HOMED=/home/cappadokes
CODE=$HOMED/code
SAMOS=$HOMED/Desktop/phD/y345/research/pymm/samos22/${PYTHONRAT}
VENV=$SAMOS/tmp/venv
RESULTS=$SAMOS/results
MACHINE=laptop

export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$CODE/pyperf/pyperf/:/usr/local/ssl/lib/

cd $CODE/pyperformance
$VENV/bin/python -m pip install .
cd $CODE/pyperf
$VENV/bin/python -m pip install .
python3 -m pip install $CODE/pyperformance

#	Time

# Jemalloc.
$VENV/bin/python -m pyperf system tune
PYTHONMALLOC=malloc LD_PRELOAD=$CODE/jemalloc_newest/lib/libjemalloc.so.2 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,PYTHONMALLOC,LD_LIBRARY_PATH --venv $VENV -o $RESULTS/jemalloc/$MACHINE/time.json.gz

# pymalloc-jemalloc.
$VENV/bin/python -m pyperf system tune
LD_PRELOAD=$CODE/jemalloc_newest/lib/libjemalloc.so.2 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,LD_LIBRARY_PATH --venv $VENV -o $RESULTS/pymalloc_jemalloc/$MACHINE/time.json.gz

# Baseline.
$VENV/bin/python -m pyperf system tune
python3 -m pyperformance run --rigorous --inherit-environ LD_LIBRARY_PATH --venv $VENV -o $RESULTS/baseline/$MACHINE/time.json.gz

# Malloc.
$VENV/bin/python -m pyperf system tune
PYTHONMALLOC=malloc python3 -m pyperformance run --rigorous --inherit-environ PYTHONMALLOC,LD_LIBRARY_PATH --venv $VENV -o $RESULTS/malloc/$MACHINE/time.json.gz

# Mimalloc.
$VENV/bin/python -m pyperf system tune
PYTHONMALLOC=malloc LD_PRELOAD=$CODE/mimalloc/out/release/libmimalloc.so.2.0 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,PYTHONMALLOC,LD_LIBRARY_PATH --venv $VENV -o $RESULTS/mimalloc/$MACHINE/time.json.gz

# pymalloc-mimalloc.
$VENV/bin/python -m pyperf system tune
LD_PRELOAD=$CODE/mimalloc/out/release/libmimalloc.so.2.0 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,LD_LIBRARY_PATH --venv $VENV -o $RESULTS/pymalloc_mimalloc/$MACHINE/time.json.gz

#	Memory

# Jemalloc.
$VENV/bin/python -m pyperf system tune
PYTHONMALLOC=malloc LD_PRELOAD=$CODE/jemalloc_newest/lib/libjemalloc.so.2 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,PYTHONMALLOC,LD_LIBRARY_PATH --track-memory --venv $VENV -o $RESULTS/jemalloc/$MACHINE/mem.json.gz

# pymalloc-jemalloc.
$VENV/bin/python -m pyperf system tune
LD_PRELOAD=$CODE/jemalloc_newest/lib/libjemalloc.so.2 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,LD_LIBRARY_PATH --track-memory --venv $VENV -o $RESULTS/pymalloc_jemalloc/$MACHINE/mem.json.gz

# Baseline.
$VENV/bin/python -m pyperf system tune
python3 -m pyperformance run --rigorous --inherit-environ LD_LIBRARY_PATH --track-memory --venv $VENV -o $RESULTS/baseline/$MACHINE/mem.json.gz

# Malloc.
$VENV/bin/python -m pyperf system tune
PYTHONMALLOC=malloc python3 -m pyperformance run --rigorous --inherit-environ PYTHONMALLOC,LD_LIBRARY_PATH --track-memory --venv $VENV -o $RESULTS/malloc/$MACHINE/mem.json.gz

# Mimalloc.
$VENV/bin/python -m pyperf system tune
PYTHONMALLOC=malloc LD_PRELOAD=$CODE/mimalloc/out/release/libmimalloc.so.2.0 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,PYTHONMALLOC,LD_LIBRARY_PATH --track-memory --venv $VENV -o $RESULTS/mimalloc/$MACHINE/mem.json.gz

# pymalloc-mimalloc.
$VENV/bin/python -m pyperf system tune
LD_PRELOAD=$CODE/mimalloc/out/release/libmimalloc.so.2.0 python3 -m pyperformance run --rigorous --inherit-environ LD_PRELOAD,LD_LIBRARY_PATH --track-memory --venv $VENV -o $RESULTS/pymalloc_mimalloc/$MACHINE/mem.json.gz

