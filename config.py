#This is the config file for the SE-RNAseq.py Snakefile

#Mus musculus
BASEDIR = '/data/brooksma/Index/Mouse/ENSEMBL/v84/'

BWAIDX = BASEDIR + 'BWA/Mus_musculus.GRCm38.dna.toplevel.fa'
INDELREF = '/fdb/GATK_resource_bundle/mm10/mgp.v5.merged.indels.dbSNP142.normed.fixedNames.vcf.gz'
SNPREF = '/fdb/GATK_resource_bundle/mm10/mgp.v5.merged.snps_all.dbSNP142.fixedNames.vcf.gz'
