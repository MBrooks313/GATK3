#!/bin/bash


# This is the makeJointCallVCF.sh bash file.
# Last modified by Matthew Brooks on March 11th, 2018
# This is a command for making a batch file for running a joint VCF call on
# multiple input VCF files. This assumes the samples have been run through the
# GATK3_preprocessing_v2.0.py snakemake pipeline. This creates the batch file.
# https://software.broadinstitute.org/gatk/documentation/article?id=7869
#
# Submit the batch file:
: '
sbatch \
--mem=12g \
--cpus-per-task=1 \
--time=48:00:00 \
--gres=lscratch:100 \
JointCallVCF.sh
'

# Load Versions and References
GATK_VERSION="3.8-0"
BASEDIR='/data/brooksma/Index/Mouse/ENSEMBL/v84/'
BWAIDX=$BASEDIR'BWA/Mus_musculus.GRCm38.dna.toplevel.fa'
WD='/data/brooksma/Fielding-Dong/VCF'

#Get base names for the samples
for FILE in VCF/*vcf.gz
do
VCF=${FILE##*/}
SAMPLES=( "${SAMPLES[@]}" "$VCF")
done;


# Code 1 of 3 for JointCallVCF.sh
echo "#!/bin/bash
# JointCallVCF.sh

function fail {
    echo "FAIL: $@" >&2
    exit 1  # signal failure
}

export TMPDIR=/lscratch/\$SLURM_JOB_ID


module load GATK/$GATK_VERSION || exit 1;
cd $WD;
GATK -m 24g -p 8 \\
GenotypeGVCFs \\
-R $BWAIDX \\" >> JointCallVCF.sh


# Code 2 of 3 code for JointCallVCF.sh
#Loop through to get all the VCF files
for indi in ${SAMPLES[@]}
do
    echo "-V ${indi} \\" >> JointCallVCF.sh
done;


# Code 3 of 3 for JointCallVCF
echo "-o JointCalls.vcf" >> JointCallVCF.sh
