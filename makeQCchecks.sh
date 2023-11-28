#!/bin/bash


# This is the makeQCchecks.sh bash file.
# Last modified by Matthew Brooks on March 12th, 2018
# This is a command for making a batch file for running a ReadGroupProperties
# and DepthOfCoverage calcualtion on the input BAM and final analyzed BAM files,
# respectively. This assumes the samples have been run through the
# GATK3_preprocessing_v2.0.py snakemake pipeline. This creates the batch file.
# https://software.broadinstitute.org/gatk/documentation/article?id=7869


########################
# Submit the batch file:
: '
sbatch \
--mem=12g \
--cpus-per-task=1 \
--time=24:00:00 \
--gres=lscratch:100 \
QCchecks.sh
'

########################
# Load Versions and References
GATK_VERSION="3.8-0"
BASEDIR='/data/brooksma/Index/Mouse/ENSEMBL/v84/'
BWAIDX=$BASEDIR'BWA/Mus_musculus.GRCm38.dna.toplevel.fa'
WD='/data/brooksma/Fielding-Dong/'



###############################################
## ReadGroupProperties Report
###############################################

#Get base names for the individual ReadGroupProperties samples
for FILE in BWA_GATK/*clean.bam
do
    BAM=${FILE##*/}
    SAMPLES=( "${SAMPLES[@]}" "$BAM")
done;


# Code 1 of 3 for ReadGroupProperties in QCchecks.sh
echo "#!/bin/bash \\
mkdir -p QC; \\
module load GATK/$GATK_VERSION || exit 1; \\
cd $WD; \\
GATK -m 12g -p 1 \\
ReadGroupProperties \\
-R $BWAIDX \\" >> QCchecks.sh

# Code 2 of 3 code for ReadGroupProperties in QCchecks.sh
#Loop through to get all the VCF files
for indi in ${SAMPLES[@]}
do
    echo "-I BWA_GATK/${indi} \\" >> QCchecks.sh
done;

# Code 3 of 3 for ReadGroupProperties in QCchecks.sh
echo "-o QC/readgroup_report.grp" >> QCchecks.sh



###############################################
## DepthOfCoverage Report
###############################################

#Get base names for the individual samples
for FILE in BWA_GATK/*markdup.bam
do
    BAM=${FILE##*/}
    SAMPLES2=( "${SAMPLES2[@]}" "$BAM")
done;


# Code 1 of 3 for DepthOfCoverage in QCchecks.sh
echo "module load GATK/$GATK_VERSION || exit 1; \\
cd $WD; \\
GATK -m 12g -p 1 \\
DepthOfCoverage \\
-R $BWAIDX \\" >> QCchecks.sh

# Code 2 of 3 code for DepthOfCoverage in QCchecks.sh
#Loop through to get all the VCF files
for indi in ${SAMPLES2[@]}
do
    echo "-I BWA_GATK/${indi} \\" >> QCchecks.sh
done;

# Code 3 of 3 for DepthOfCoverage in QCchecks.sh
echo "-o QC/coverage_report" >> QCchecks.sh
