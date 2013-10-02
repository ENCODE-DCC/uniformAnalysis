#!/usr/bin/env python2.7
# alignmentstep.py module holds AlignmentStep class which descends from LogicalStep class.
# It performs bwa alignment on single or paired end reads.
#
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'fastqRep'+replicate
#         Paired: 'fastqRd1Rep'+replicate and 'fastqRd2Rep'+replicate 
#
# Outputs: a single bam target which will match and analysis target keyed as:
#          'bamRep'+replicate

from src.logicalStep import LogicalStep
from src.wrappers import bwa, samtools

class AlignmentStep(LogicalStep):

    def __init__(self, analysis, replicate):
        self.replicate = str(replicate)
        LogicalStep.__init__(self, analysis, analysis.readType() + 'Alignment_Rep' + self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def onRun(self):
        # Versions:
        bwa.version(self)
        samtools.version(self)
        
        # Outputs:
        bam = self.declareTargetFile('bamRep' + self.replicate,ext='bam')
        
        # Inputs:
        if self.ana.readType() == 'single':
            input1 = self.ana.getFile('fastqRep' + self.replicate)
        elif self.ana.readType() == 'paired':
            input1 = self.ana.getFile('fastqRd1Rep' + self.replicate)
            input2 = self.ana.getFile('fastqRd2Rep' + self.replicate)
             
        sam = self.declareGarbageFile('sam')
        sai1 = self.declareGarbageFile('sai1')
        bwa.aln(self, input1, sai1)
        
        if self.ana.readType() == 'single':
            bwa.samse(self, sai1, input1, sam)
        elif self.ana.readType() == 'paired':
            sai2 = self.declareGarbageFile('sai2')
            bwa.aln(self, input2, sai2)
            bwa.sampe(self, sai1, input1, sai2, input2, sam)

        samtools.samToBam(self, sam, bam)

