#!/usr/bin/env python2.7
# samplebamstep.py module holds SampleBamStep class which descends from LogicalStep class.
# It takes a sample of a bam and converts it to a sam file
#
# Inputs: 1 bam, pre-registered in the experiment keyed as: 'bam' + suffix
#
# Outputs: 1 interim sam file, keyed as: 'samSample' + suffix

from src.logicalstep import LogicalStep
from src.wrappers import samtools, sampleBam, bedtools

class SampleBamStep(LogicalStep):

    def __init__(self, experiment, suffix, sampleSize):
        self.suffix = str(suffix)
        self.sampleSize = sampleSize
        LogicalStep.__init__(self, experiment, 'sampleBam_' + self.suffix)
        #self.bam = bam
        
    def onRun(self):      

        # Versions:
        samtools.version(self)
        sampleBam.version(self)
        bedtools.version(self)
        
        # Outputs:
        samSample = self.declareTempFile('samSample' + self.suffix, ext='sam')
        #bamSample = self.declareExpFile( 'bamSample' + self.suffix, ext='bam')
        
        # Inputs:
        bam = self.exp.getFile('bam' + self.suffix)
        
        bamSize = samtools.bamSize(self,bam)
        # Take the whole bam if it is smaller than sampleSize requested.        
        if self.sampleSize > bamSize:
            self.sampleSize=bamSize
        
        bed = self.declareGarbageFile('bed')
        
        sampleBam.sample(self,bam,bamSize,sampleSize,bed)
        bedtools.bedToSam(self,bed,samSample)

