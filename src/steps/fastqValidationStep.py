#!/usr/bin/env python2.7
# fastqValidateStep.py module holds FastqValidateStep class which descends from LogicalStep class.
# It performs fastq validation obviously enough.
#
# Inputs: 1 fastq file, pre-registered in the analysis keyed as: 'fastq' + suffix
#
# Outputs: directory of files (will include html target) keyed as: 'valDir' + suffix

from src.logicalStep import LogicalStep
from src.wrappers import fastqStatsAndSubsample, fastqc
import datetime

class FastqValidationStep(LogicalStep):

    def __init__(self, analysis, suffix):
        self.suffix = str(suffix)
        LogicalStep.__init__(self, analysis, 'fastqValidation_' + self.suffix)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def onRun(self):
        # Versions:
        fastqStatsAndSubsample.version(self)
        fastqc.version(self)
        
        # Outputs:
        valDir  = self.declareTargetFile('valDir'  + self.suffix, ext='dir')
        # NOTE: valHtml resides inside valDir and only needs to be known at analysis level.
        #valHtml = self.declareTargetFile('valHtml' + self.suffix, ext='html') 
        
        # Inputs:
        input = self.ana.getFile('fastq' + self.suffix)
        
        sampleFastq = self.declareGarbageFile('sampleFastq', ext='fastq')
        simpleStats = self.declareGarbageFile('simpleStats', ext='txt')

        # sample granular step
        fastqStatsAndSubsample.sample(self,input,simpleStats,sampleFastq)

        # sample fastqc step that generates HTML output
        fastqc.validate(self,sampleFastq,valDir)


