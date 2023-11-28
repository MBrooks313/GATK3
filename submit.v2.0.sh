#!/bin/bash
# Author: Margaret R. Starostik
# Last update: May 15th, 2017 by Matthew Brooks
# Run with: sbatch --time=24:00:00 submit.v2.0.sh

cd $SLURM_SUBMIT_DIR
module load python/3.5

mkdir -p logs
snakemake \
--snakefile GATK3_preprocessing_v2.0.py \
--jobname "{rulename}.{jobid}.snake" \
--keep-going \
--latency-wait 600 \
--verbose -j \
--stats Indexes_snakefile.stats \
--latency-wait 360 --timestamp \
--rerun-incomplete \
--cores 300 \
--cluster-config GATK3_v1.0.yaml \
--cluster="sbatch --mem={params.mem} --time={params.time} --cpus-per-task={threads} --out logs/job_%j.out" \
>& logs/GATK3_snakefile.log
