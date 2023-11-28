#!/bin/bash


# This is the makeQCchecks_Var.sh bash file.
# Last modified by Matthew Brooks on March 12th, 2018
# This is a command for making a batch file for running a VariantEval on the
# individual and grouped VCF files. This assumes the samples have been run
# through the JointCallVCF.sh and JointCallVCF_Families.swarm scripts.
# This creates the swarm file.
# https://software.broadinstitute.org/gatk/documentation/article?id=7869


########################
# Submit the batch file:
: '
swarm \
-g 24 \
-t 8 \
--time=24:00:00 \
--gres=lscratch:100 \
-f QCchecks_Var.swarm
'

########################
# Load Versions and References
GATK_VERSION="3.8-0"
BASEDIR='/data/brooksma/Index/Mouse/ENSEMBL/v84/'
BWAIDX=$BASEDIR'BWA/Mus_musculus.GRCm38.dna.toplevel.fa'
WD='/data/brooksma/Fielding-Dong/'



###############################################
## VariantEval Report for individual VCF files
###############################################

# Code for VariantEval in QCchecks_Var.sh
for FILE in VCF/*vcf.gz
do
    BASE=${FILE##*/}
    echo "module load GATK/$GATK_VERSION || exit 1; \\
    cd $WD; \\
    GATK -m 24g -p 8 \\
    VariantEval \\
    -R $BWAIDX \\
    --eval $FILE \\
    -o QC/${BASE}_rpt" >> QCchecks_Var.swarm
done



###############################################
## VariantEval Report for grouped VCF files
###############################################

# Code for VariantEval in QCchecks_Var.sh
for FILE in VCF/*vcf
do
    BASE=${FILE##*/}
    echo "module load GATK/$GATK_VERSION || exit 1; \\
    cd $WD; \\
    GATK -m 24g -p 8 \\
    VariantEval \\
    -R $BWAIDX \\
    --eval $FILE \\
    -o QC/${BASE}_rpt" >> QCchecks_Var.swarm
done
