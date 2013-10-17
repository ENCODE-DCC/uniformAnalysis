#!/usr/bin/env python2.7
# fastqValidateStep.py module holds FastqValidateStep class which descends from LogicalStep class.
# It performs fastq validation obviously enough.
#
# Inputs: 1 fastq file, pre-registered in the analysis keyed as: 'tags' + suffix + 'fastq'
#
# Outputs: directory of files (will include html target) keyed as: 'valDir' + suffix
#          zipped file of that directory                 keyed as: 'val' + suffix + '.zip'

from src.logicalStep import LogicalStep
from src.wrappers import fastqStatsAndSubsample, fastqc

class FastqValidationStep(LogicalStep):

    def __init__(self, analysis, suffix):
        self.suffix = str(suffix)
        LogicalStep.__init__(self, analysis, 'fastqValidation_' + self.suffix)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions
        
    def writeVersions(self,raFile=None):
        '''Writes versions to to the log or a file.'''
        if raFile != None:
            raFile.add('fastqStatsAndSubsample', fastqStatsAndSubsample.version(self))
            raFile.add('fastqc', fastqc.version(self))
        else:
            fastqStatsAndSubsample.version(self)
            fastqc.version(self)

    def onRun(self):
        # Outputs:  
        # NOTE: These outputs must be declared even thouugh they don't appear to be used.
        #       This is s that the analysis class can find them on sucess.
        valDir  = self.declareTargetFile('valDir'  + self.suffix, name='sampleFastq_fastqc', ext='dir')
        valZip  = self.declareTargetFile('val'  + self.suffix + '.zip', 
                                         name='sampleFastq_fastqc', ext='zip')
        # NOTE: valHtml resides inside valDir and only needs to be known at analysis level.
        #valHtml = self.declareTargetFile('val' + self.suffix + '.html', ext='html') 
        
        # Inputs:
        fastq = self.ana.getFile('tags' + self.suffix + '.fastq')
        
        sampleFastq = self.declareGarbageFile('sampleTags', ext='fastq')
        simpleStats = self.declareGarbageFile('simpleStats', ext='txt')

        # sample granular step
        fastqStatsAndSubsample.sample(self,fastq,simpleStats,sampleFastq)

        # sample fastqc step that generates HTML output
        fastqc.validate(self,sampleFastq,valDir)


