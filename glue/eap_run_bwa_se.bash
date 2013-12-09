#!/bin/bash -ex
# Align single ended reads with BWA and make genome-sorted BAM

#Get better names for inputs
index=$1
reads=$2
output=$3
mkdir tmp

#Do the alignments
bwa aln -t 4 $index $reads > tmp/out.sai
bwa samse $index tmp/out.sai $reads > tmp/out.sam
rm tmp/out.sai
samtools view -S -b tmp/out.sam > tmp/out.bam
rm tmp/out.sam
samtools sort -n tmp/out.bam tmp/sorted
mv tmp/sorted.bam $output
rm tmp/out.bam
rm -r tmp
