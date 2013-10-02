#!/usr/bin/env python2.7
# alignmentstep.py module holds AlignmentStep class which descends from LogicalStep class.
# It performs bwa alignment on single or paired end reads.
#
# Inputs: 1 or 2 fastq files, pre-registered in the experiment keyed as:
#         Single: 'fastqRep'+replicate
#         Paired: 'fastqRd1Rep'+replicate and 'fastqRd2Rep'+replicate 
#
# Outputs: a single bam target which will match and experiment target keyed as:
#          'bamRep'+replicate
# Interim: A single interim file which will match and experiment target keyed as:
#          'samRep'+replicate

from src.logicalStep import LogicalStep
from src.wrappers import bwa, samtools

class AlignmentStep(LogicalStep):

    def __init__(self, experiment, replicate):
        self.replicate = str(replicate)
        LogicalStep.__init__(self, experiment, experiment.readType() + 'Alignment_Rep' + self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def onRun(self):
        # Versions:
        bwa.version(self)
        samtools.version(self)
        
        # Outputs:
        sam = self.declareTempFile('samRep' + self.replicate,ext='sam')
        bam = self.declareExpFile('bamRep' + self.replicate,ext='bam')
        
        # Inputs:
        if self.exp.readType() == 'single':
            input1 = self.exp.getFile('fastqRep' + self.replicate)
        elif self.exp.readType() == 'paired':
            input1 = self.exp.getFile('fastqRd1Rep' + self.replicate)
            input2 = self.exp.getFile('fastqRd2Rep' + self.replicate)
             
        sai1 = self.declareTempFile('sai1')  # Why isn't this a garbage file?
        bwa.aln(self, input1, sai1)
        
        if self.exp.readType() == 'single':
            bwa.samse(self, sai1, input1, sam)
        elif self.exp.readType() == 'paired':
            sai2 = self.declareTempFile('sai2')  # Why isn't this a garbage file?
            bwa.aln(self, input2, sai2)
            bwa.sampe(self, sai1, input1, sai2, input2, sam)

        samtools.samToBam(self, sam, bam)

