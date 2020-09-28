#!/bin/sh

# Job name
#PBS -N simple

# Output file
#PBS -o simple_output.log

# Error file
#PBS -e simple_err.log

# request resources and set limits
#PBS -l walltime=72:00:00
#PBS -l select=1:ncpus=16:mem=16GB
# ngpus=4
#:ompthreads=24
# 'select' chooses number of nodes.

#  load required modules
module load lang/python/anaconda/pytorch
#lang/cuda

# We might need to add the global paths to our code to the pythonpath. Also set the data directories globally.
cd /work/es1595/random-baseline

#  run the script
python simple_baseline.py --train-file socialIQa_v1.4/socialIQa_v1.4_trn.jsonl --input-file socialIQa_v1.4/socialIQa_v1.4_tst.jsonl  --output-file predictions.lst

# To submit: qsub pbs_simple.sh
# To display the queue: qstat -Q gpu (this is usually where the GPU job ends up)
# Display server status: qstat -B <server>
# Display job information: qstat <jobID>

# To monitor job progress:
# qstat -f | grep exec_host
# Find the node where this job is running.
# ssh to the node.
# tail /var/spool/pbs/spool/<job ID>.bp1.OU
