"""
This is the GATK3_preprocessing.v1.0.py Snakefile.
Last modified by Matthew Brooks on Feb 27th, 2018
This runs the GATK 3.8 preprocessing pipeline from making the uBAM, marking
Illumina adapters, and BWA alignment.
https://software.broadinstitute.org/gatk/best-practices/workflow?id=11145
https://gatkforums.broadinstitute.org/gatk/discussion/6472/read-groups
https://software.broadinstitute.org/gatk/documentation/article?id=6483
https://software.broadinstitute.org/gatk/documentation/article?id=6484
"""

#######################################
# Import config file and modules needed
#######################################

import config
import glob
import os


#############################################################
# List of required references and software versions
#############################################################

BWAREF = config.BWAIDX

PICARD_VERSION = "2.9.2"
BWA_VERSION = "0.7.17"


########################################
# Import sample names from the FQ folder
########################################

SAMPLES = [os.path.basename(fname).split('_1')[0] for fname in glob.glob('FQ/*1.fq.gz')]


#############################################################
# List of directories needed and end point files for analysis
#############################################################

DRS = ['logs/']
ALN = expand("BWA_GATK/{sample}.clean.bam", sample=SAMPLES)


##############################
# Snakemake rules for analysis
##############################

localrules: all

rule all:
    """
    Starting rule that defines what endpoints are needed to be created.
    """
    input: DRS + ALN
    threads: 1
    params: mem = "4G", time = "48:00:00"
    shell:  """ \
    mv slurm* logs/; \
    """


rule dirs:
    """
    This makes the needed directories not created in the rules.
    """
    output: DRS
    threads: 1
    params:
       mem = "4G",
       time = "01:00:00"
    shell:  "mkdir -p "+' '.join(DRS)


rule uBam:
    """
    This assumes all Read Group information is in the sample name of the
    original fastq files and will be parsed for creation of the proper read
    group information during the creation of the uBAM.
    Ex, S0021pup_USD16084608L_HHFWNCCXY_L5_1.fq.gz
    """
    input:
       R1 = "FQ/{sample}_1.fq.gz",
       R2 = "FQ/{sample}_2.fq.gz"
    output: "BWA_GATK/{sample}.unmapped.bam"
    threads: 8
    params:
       mem = "8G",
       time = "04:00:00"
    shell:  """ \
    module load picard/{PICARD_VERSION} || exit 1; \
    TEXT={wildcards.sample} \
    ARR=(${{TEXT//_/ }}); \
    READ=${{ARR[0]}}.${{ARR[2]}}.${{ARR[3]}}; \
    LIB=${{ARR[1]}}; \
    PLATU=${{ARR[2]}}.${{ARR[3]}}.${{ARR[1]}}; \
    SAMP=${{ARR[0]}}; \
    java -XX:ParallelGCThreads={threads} -Xmx{params.mem} \
    -jar $PICARDJARPATH/picard.jar FastqToSam \
    FASTQ={input.R1} \
    FASTQ2={input.R2} \
    OUTPUT={output} \
    READ_GROUP_NAME=$READ \
    LIBRARY_NAME=$LIB \
    PLATFORM_UNIT=$PLATU \
    PLATFORM=ILLUMINA \
    SAMPLE_NAME=$SAMP \
    """


rule markAdapt:
    """
    This marks up the adapters used in the library generation step.
    """
    input: "BWA_GATK/{sample}.unmapped.bam"
    output:
        BAM = "BWA_GATK/{sample}.markadd.bam",
        MET = "BWA_GATK/{sample}.metrix.txt"
    threads: 8
    params:
       mem = "8G",
       time = "04:00:00"
    shell:  """ \
    module load picard/{PICARD_VERSION} || exit 1; \
    java -XX:ParallelGCThreads={threads} -Xmx{params.mem} \
    -jar $PICARDJARPATH/picard.jar MarkIlluminaAdapters \
    I={input} \
    O={output.BAM} \
    M={output.MET} \
    """


rule align:
    """
    This generates an interleaved Fastq file from the uBAM to feed BWA for
    alignment. The alined data output is then processed by MergeBamAlignment to
    fix the alignment output.
    """
    input:
        UBAM = "BWA_GATK/{sample}.unmapped.bam",
        MBAM = "BWA_GATK/{sample}.markadd.bam"
    output:
        BAM = "BWA_GATK/{sample}.clean.bam",
        BAI = "BWA_GATK/{sample}.clean.bai"
    threads: 12
    params:
       mem = "36G",
       time = "12:00:00",
       gres = "lscratch:100"
    shell:  """ \
    module load picard/{PICARD_VERSION} bwa/{BWA_VERSION} || exit 1; \
    java -Xmx{params.mem} \
    -jar $PICARDJARPATH/picard.jar SamToFastq \
    I={input.MBAM} \
    FASTQ=/dev/stdout \
    CLIPPING_ATTRIBUTE=XT CLIPPING_ACTION=2 INTERLEAVE=true NON_PF=true | \
    bwa mem -M -t {threads} -p {BWAREF} /dev/stdin | \
    java -Xmx{params.mem} \
    -jar $PICARDJARPATH/picard.jar MergeBamAlignment \
    ALIGNED_BAM=/dev/stdin \
    UNMAPPED_BAM={input.UBAM} \
    OUTPUT={output.BAM} \
    R={BWAREF} \
    CREATE_INDEX=true \
    ADD_MATE_CIGAR=true \
    CLIP_ADAPTERS=false \
    CLIP_OVERLAPPING_READS=true \
    INCLUDE_SECONDARY_ALIGNMENTS=true \
    MAX_INSERTIONS_OR_DELETIONS=-1 \
    PRIMARY_ALIGNMENT_STRATEGY=MostDistant \
    ATTRIBUTES_TO_RETAIN=XS \
    """
