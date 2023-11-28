#!/bin/bash


# This is the makeMarkDup.sh bash file.
# Last modified by Matthew Brooks on Feb 20th, 2018
# https://software.broadinstitute.org/gatk/documentation/article?id=6747
# This is a make command for Picard Mark Duplicates on multiple input BAM files
# per sample. This assumes the samples have been run through the
# GATK3_preprocessing_v1.0.py snakemake pipeline. This creates the swarm file
# for the Picard MarkDuplicate rule of the preprocessing section.
# Submit the swarm file:
# swarm -f MarkDup.swarm -t 12 -g 64 --gres=lscratch:200 --time=12:00:00


#Get base names for the samples
for FILE in BWA_GATK/*clean.bam
do
BAM=${FILE##*/}
BASE=${BAM%%_*}
SAMPLES=( "${SAMPLES[@]}" "$BASE")
done;

#Make the SAMPLES array uniq
USAMP=($(echo "${SAMPLES[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))


#Loop through for each sample
for indi in ${USAMP[@]}
do
    #Declare output and stat file names
    MD="BWA_GATK/${indi}.markdup.bam"
    STAT="BWA_GATK/${indi}_markdup_metrics.txt"

    #1 of 3 code for MarkDuplicates
    echo "module load picard; \\
java -XX:ParallelGCThreads=\$SLURM_CPUS_PER_TASK \\
-Xmx64G \\
-jar \$PICARDJARPATH/picard.jar MarkDuplicates \\" >> MarkDup.swarm

    #Loop through to get all the BAM files for that sample
    for rdbams in BWA_GATK/${indi}*clean.bam
    do
        #2 of 3 code for MarkDuplicates
        echo "I=${rdbams} \\" >> MarkDup.swarm
    done;

    #3 of 3 code for MarkDuplicates
    echo "OUTPUT=$MD \\
M=$STAT \\
OPTICAL_DUPLICATE_PIXEL_DISTANCE=250 \\
CREATE_INDEX=true \\
TMP_DIR=lscratch/\$SLURM_JOBID;
    " >> MarkDup.swarm

done;
