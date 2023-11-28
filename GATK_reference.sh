#!/bin/bash
#sbatch --mem=24g --time=12:00:00 GATK_reference.sh


module load bwa

bwa index -a bwtsw /data/brooksma/Index/Mouse/ENSEMBL/v84/Mus_musculus.GRCm38.dna.toplevel.fa


module load samtools

samtools faidx /data/brooksma/Index/Mouse/ENSEMBL/v84/Mus_musculus.GRCm38.dna.toplevel.fa


module load picard;

java -jar $PICARDJARPATH/picard.jar CreateSequenceDictionary \
R=/data/brooksma/Index/Mouse/ENSEMBL/v84/Mus_musculus.GRCm38.dna.toplevel.fa \
O=/data/brooksma/Index/Mouse/ENSEMBL/v84/Mus_musculus.GRCm38.dna.toplevel.dict;
