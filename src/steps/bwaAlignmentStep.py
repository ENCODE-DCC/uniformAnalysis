#!/usr/bin/env python2.7
# bwaAlignmentStep.py module holds BwaAlignmentStep class which descends from LogicalStep class.
# It performs bwa alignment on single or paired end reads.
#
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'tagsRep'+replicate+'.fastq'
#         Paired: 'tagsRd1Rep'+replicate+'.fastq' and 'tagsRd2Rep'+replicate+'.fastq' 
#
# Outputs: a single bam target and an index for it which will match and analysis targets keyed as:
#          'alignmentRep'+replicate+'.bam'
#          'alignmentRep'+replicate+'.bam.bai'
#    and an interim json file, keyed as: 'alignmentRep' + replicate +  '.json'

from src.logicalStep import LogicalStep
from src.wrappers import bwa, samtools

class BwaAlignmentStep(LogicalStep):

    def __init__(self, analysis, replicate):
        self.replicate = str(replicate)
        LogicalStep.__init__(self, analysis, analysis.readType + '_bwaAlignment_Rep' + \
                                                                                   self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all step versions

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
        
        # TODO: Add support for solexa fastqs
        # usage v1: eap_run_slx_bwa_se bwa-index solexa-reads.fq out.bam
        # usage v3: eap_run_slx_bwa_pe bwa-index solexa1.fq solexa2.fq out.bam
        
        # Inputs:
        if self.ana.readType == 'single':
            input1 = self.ana.getFile('tagsRep' + self.replicate + '.fastq')
        elif self.ana.readType == 'paired':
            input1 = self.ana.getFile('tagsRd1Rep' + self.replicate + '.fastq')
            input2 = self.ana.getFile('tagsRd2Rep' + self.replicate + '.fastq')
             
        # Outputs:
        bam = self.declareTargetFile('alignmentRep' + self.replicate + '.bam')
        
        if self.ana.readType == 'single':
            # usage v3: eap_run_bwa_se bwa-index reads.fq out.bam
            bwa.eap_se(self, input1, bam)
        elif self.ana.readType == 'paired':
            # usage v4: eap_run_bwa_pe bwa-index read1.fq read2.fq out.bam
            bwa.eap_pe(self, input1, input2, bam)
