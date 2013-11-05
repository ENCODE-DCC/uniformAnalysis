#!/usr/bin/env python2.7
# mergeBamStep.py module holds MergeBamStep class which descends from LogicalStep class.
# It merges 2 bam files using samtools merge.
#
# Inputs: 2 bam files, pre-registered in the analysis and both keyed as: 'bamRep' + replicateN + '.bam'
#
# Outputs: 1 merged bam keyed as: 'mergedRep' + replicate1 + 'Rep' +replcicate2 + '.bam'

from src.logicalStep import LogicalStep
from src.wrappers import samtools

class MergeBamStep(LogicalStep):

    def __init__(self, analysis, replicate1, replicate2):
        self.replicate1 = str(replicate1)
        self.replicate2 = str(replicate2)
        LogicalStep.__init__(self, analysis, \
                             'mergeBam_Rep' + self.replicate1 + 'Rep' + self.replicate2)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions
        
    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('samtools', samtools.version(self))
        else:
            samtools.version(self)

    def onRun(self):
        # Inputs:
        bamRep1 = self.ana.getFile('bamRep' + self.replicate1 + '.bam')
        bamRep2 = self.ana.getFile('bamRep' + self.replicate2 + '.bam')
        
        # Outputs:  
        mergedBam = self.declareResultFile('mergedRep' + self.replicate1 + 'Rep' + \
                                                         self.replicate2+'.bam')

        # merge
        samtools.merge(self,[bamRep1,bamRep2],mergedBam)
