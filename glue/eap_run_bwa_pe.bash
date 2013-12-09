#!/bin/bash -ex
# Align paired ended reads with BWA and make genome-sorted BAM

#Get better names for inputs
index=$1
read1=$2
read2=$3
output=$4

#Do the alignments
mkdir tmp
bwa aln -t 4 $index $read1 > tmp/read1.sai
bwa aln -t 4 $index $read2 > tmp/read2.sai
bwa sampe $index tmp/read1.sai tmp/read2.sai $read1 $read2 > tmp/out.sam
rm tmp/read1.sai tmp/read2.sai
samtools view -S -b tmp/out.sam > tmp/out.bam
rm tmp/out.sam
samtools sort -n tmp/out.bam tmp/sorted
mv tmp/sorted.bam $output
rm tmp/out.bam
rm -r tmp
