#!/usr/bin/env python2.7
# fastqValidateStep.py module holds FastqValidateStep class which descends from LogicalStep class.
# It performs fastq validation obviously enough.
#
# Inputs: 1 fastq file, pre-registered in the analysis keyed as: 'tags' + suffix + '.fastq'
#
# Outputs: directory of files (will include html target) keyed as: 'valDir' + suffix
#          zipped file of that directory                 keyed as: 'val' + suffix + '.zip'

from src.logicalStep import LogicalStep
from src.wrappers import ucscUtils, fastqc

class FastqValidationStep(LogicalStep):

    def __init__(self, analysis, suffix):
        self.suffix = str(suffix)
        LogicalStep.__init__(self, analysis, 'fastqValidation_' + self.suffix)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions
        
    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('ucscUtils', ucscUtils.version(self,tool='fastqStatsAndSubsample'))
            raFile.add('fastqc', fastqc.version(self))
        else:
            ucscUtils.version(self,tool='fastqStatsAndSubsample')
            fastqc.version(self)

    def onRun(self):
        # Outputs:  
        valDir  = self.declareTargetFile('valDir'+self.suffix, name='sampleTags_fastqc', ext='dir')
        self.declareTargetFile('val'  + self.suffix + '.zip',name='sampleTags_fastqc', ext='zip')
        # NOTE: valHtml resides inside valDir and only needs to be known at analysis level.
        #valHtml = self.declareResultFile('val' + self.suffix + '.html') 
        
        # Inputs:
        fastq = self.ana.getFile('tags' + self.suffix + '.fastq')
        
        sampleFastq = self.declareGarbageFile('sampleTags.fastq')
        simpleStats = self.declareGarbageFile('simpleStats.txt')

        # sample granular step
        ucscUtils.fastqStatsAndSubsample(self,fastq,simpleStats,sampleFastq)

        # sample fastqc step that generates HTML output
        fastqc.validate(self,sampleFastq,valDir)
