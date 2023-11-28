"""
This is the GATK3_preprocessing.v1.0.py Snakefile.
Last modified by Matthew Brooks on Feb 20th, 2018
This runs the GATK 3.8 variant calling pipeline from Indel realignment,
recalibrate base quality scores, and per sample variant calling.
https://software.broadinstitute.org/gatk/documentation/article?id=7156
https://software.broadinstitute.org/gatk/documentation/article?id=2801
https://software.broadinstitute.org/gatk/documentation/article?id=7870#4
"""

#######################################
# Import config file and modules needed
#######################################

import config
import glob
import os


#############################################################
# List of directories needed and end point files for analysis
#############################################################

BWAREF = config.BWAIDX
INDELREF = config.INDELREF
SNPREF = config.SNPREF

GATK_VERSION = "3.8-0"

########################################
# Import sample names from the FQ folder
########################################

SAMPLES = [os.path.basename(fname).split('.')[0] for fname in glob.glob('BWA_GATK/*.markdup.bam')]


#############################################################
# List of directories needed and end point files for analysis
#############################################################

DRS = ['logs/']
#ALN = expand("BWA_GATK/{sample}.clean.bam", sample=SAMPLES)
REALN = expand("INDEL/{sample}.realigned.bam", sample=SAMPLES)
PLOT = expand("INDEL/{sample}.realigned.recalb.plots.pdf", sample=SAMPLES)
GVCF = expand("VCF/{sample}.vcf.gz", sample=SAMPLES)

##############################
# Snakemake rules for analysis
##############################

localrules: all

rule all:
   input: DRS + PLOT + GVCF
   threads: 1
   params: mem = "4G", time = "48:00:00"
   shell:  """ \
   mv slurm* logs/; \
   """


rule dirs:
   output: DRS
   threads: 1
   params:
       mem = "4G",
       time = "01:00:00"
   shell:  "mkdir -p "+' '.join(DRS)


rule rtc:
    input: "BWA_GATK/{sample}.markdup.bam"
    output: "INDEL/{sample}.intervals"
    threads: 4
    params:
        mem = "12G",
        time = "8:00:00",
        gres = "lscratch:100"
    shell: """ \
    module load GATK/{GATK_VERSION} || exit 1; \
    GATK -m {params.mem} -p {threads} \
    RealignerTargetCreator \
    -R {BWAREF} \
    -I {input} \
    -known {INDELREF} \
    -o {output} \
    -nt {threads} \
    """


rule indelrealn:
    input:
        BAM = "BWA_GATK/{sample}.markdup.bam",
        INT = "INDEL/{sample}.intervals"
    output: "INDEL/{sample}.realigned.bam"
    threads: 4
    params:
        mem = "12G",
        time = "12:00:00",
        gres = "lscratch:100"
    shell: """ \
    module load GATK/{GATK_VERSION} || exit 1; \
    GATK -m {params.mem} -p {threads} \
    IndelRealigner \
    -R {BWAREF} \
    -I {input.BAM} \
    -known {INDELREF} \
    -targetIntervals {input.INT} \
    -o {output} \
    """


rule baserecalb:
    input: "INDEL/{sample}.realigned.bam"
    output: "INDEL/{sample}.realigned.BaseRecalibrator"
    threads: 8
    params:
        mem = "24G",
        time = "48:00:00",
        gres = "lscratch:100"
    shell: """ \
    module load GATK/{GATK_VERSION} || exit 1; \
    GATK -m {params.mem} -p {threads} \
    BaseRecalibrator \
    -I {input} \
    -R {BWAREF} \
    -knownSites {SNPREF} \
    -o {output} \
    """


rule printrecalb:
    input:
        BAM = "INDEL/{sample}.realigned.bam",
        CAL = "INDEL/{sample}.realigned.BaseRecalibrator"
    output: "INDEL/{sample}.realigned.recal.bam"
    threads: 8
    params:
        mem = "24G",
        time = "48:00:00",
        gres = "lscratch:100"
    shell: """ \
    module load GATK/{GATK_VERSION} || exit 1; \
    GATK -m {params.mem} -p {threads} \
    PrintReads \
    -I {input.BAM} \
    -o {output} \
    -R {BWAREF} \
    -BQSR {input.CAL} \
    """


rule qcrecalb:
    input: "INDEL/{sample}.realigned.recal.bam"
    output: "INDEL/{sample}.realigned.BaseRecalibrator.after"
    threads: 1
    params:
        mem = "24G",
        time = "48:00:00",
        gres = "lscratch:100"
    shell: """ \
    module load GATK/{GATK_VERSION} || exit 1; \
    GATK -m {params.mem} -p {threads} \
    BaseRecalibrator \
    -I {input} \
    -R {BWAREF} \
    -knownSites {SNPREF} \
    -o {output} \
    """


rule qcrecalbplot:
    input:
        FOR = "INDEL/{sample}.realigned.BaseRecalibrator",
        AFT = "INDEL/{sample}.realigned.BaseRecalibrator.after"
    output: "INDEL/{sample}.realigned.recalb.plots.pdf"
    threads: 1
    params:
        mem = "12G",
        time = "2:00:00",
        gres = "lscratch:100"
    shell: """ \
    module load GATK/{GATK_VERSION} || exit 1; \
    GATK -m {params.mem} -p {threads} \
    AnalyzeCovariates \
    -R {BWAREF} \
    -before {input.FOR} \
    -after {input.AFT} \
    -plots {output} \
    """


rule gvcf:
    input: "INDEL/{sample}.realigned.recal.bam"
    output: "VCF/{sample}.vcf.gz"
    threads: 8
    params:
        mem = "12G",
        time = "36:00:00",
        gres = "lscratch:100"
    shell: """ \
    module load GATK/{GATK_VERSION} || exit 1; \
    GATK -m {params.mem} -p {threads} \
    HaplotypeCaller \
    -R {BWAREF} \
    -I {input} \
    -o {output} \
    -ERC GVCF \
    -variant_index_type LINEAR \
    -variant_index_parameter 128000 \
    """
