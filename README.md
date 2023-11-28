This is the GATK 3.8 pipeline. Read the Tutorials.txt for context and how the pipeline proceeds.
Created by Matthew Brooks Feb 2018. Last modified March 12th, 2018.

How to run:

1.  submit.v1.0.sh for running GATK3_preprocessing_v1.0.py
    assigns read groups, makes unmapped BAMs, marks Illumina adapters, performs
    BWA alignment, performs MergeBamAlignment

2.  makeMarkDup.sh to make MarkDup.swarm
    performs MarkDuplicates on sample BAM files

3.  submit.v2.0.sh for running GATK3_preprocessing_v2.0.py
    indel realignment, base recalibration of quality scores, call individual
    genomic VCF files

4.  makeJointCallVCF.sh to make JointCallVCF.sh
    runs GenotypeGVCFs on all individual VCF files

5.  modify JointCallVCF.sh to make JointCallVCF_Families.sh
    runs GenotypeGVCFs on families using VCF files

6.  makeQCchecks.sh to make QCchecks.sh
    read group properties and depth of coverage calculations

7.  makeQCcheck_Var.sh to make QCchecks_Var.swarm
    variant evaluation of individual and grouped VCF files


I plan to better optimize into a single snakemake file in the future.


File Generation

GATK_BWA
*fastq.gz -> *unmapped.bam -> *markadd.bam -> *clean.bam -> *markdup.bam ->

INDEL
*realigned.bam -> *realigned.recal.bam ->

VCF
*vcf.gz -> JointCall*.vcf

