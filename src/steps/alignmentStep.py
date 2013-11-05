#!/usr/bin/env python2.7
# alignmentstep.py module holds AlignmentStep class which descends from LogicalStep class.
# It performs bwa alignment on single or paired end reads.
#
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'tagsRep'+replicate+'.fastq'
#         Paired: 'tagsRd1Rep'+replicate+'.fastq' and 'tagsRd2Rep'+replicate+'.fastq' 
#
# Outputs: a single bam target which will match and analysis target keyed as:
#          'alignmentRep'+replicate+'.bam'

from src.logicalStep import LogicalStep
from src.wrappers import bwa, samtools

class AlignmentStep(LogicalStep):

    def __init__(self, analysis, replicate):
        self.replicate = str(replicate)
        LogicalStep.__init__(self, analysis, analysis.readType + 'Alignment_Rep' + self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('bwa', bwa.version(self))
            raFile.add('samtools', samtools.version(self))
        else:
            bwa.version(self)
            samtools.version(self)
        
    def onRun(self):
        # Outputs:
        bam = self.declareResultFile('alignmentRep' + self.replicate+'.bam')
        
        # Inputs:
        if self.ana.readType == 'single':
            input1 = self.ana.getFile('tagsRep' + self.replicate+'.fastq')
        elif self.ana.readType == 'paired':
            input1 = self.ana.getFile('tagsRd1Rep' + self.replicate+'.fastq')
            input2 = self.ana.getFile('tagsRd2Rep' + self.replicate+'.fastq')
             
        sam = self.declareGarbageFile('alignment.sam')
        sai1 = self.declareGarbageFile('sai1.sai')
        bwa.aln(self, input1, sai1)
        
        if self.ana.readType == 'single':
            bwa.samse(self, sai1, input1, sam)
        elif self.ana.readType == 'paired':
            sai2 = self.declareGarbageFile('sai2.sai')
            bwa.aln(self, input2, sai2)
            bwa.sampe(self, sai1, input1, sai2, input2, sam)

        # TODO: unique autosome mapping count:
        # https://github.com/qinqian/GCAP/blob/master/gcap/funcs/mapping.py reads_mapping()
        # autosomeCount
            
        samtools.samToBam(self, sam, bam)

