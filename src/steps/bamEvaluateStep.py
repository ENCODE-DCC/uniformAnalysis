#!/usr/bin/env python2.7
# bamEvaluateStep.py module holds BamEvaluateStep class which descends from LogicalStep class.
# It takes a sample of a bam and characterizes the library completity
#
# Inputs: 1 bam, pre-registered in the experiment keyed as: 'bam' + suffix
#
# Outputs: 1 interim sam       file, keyed as: 'samSample' + suffix
#          1 target  histogram file, keyed as: 'histo' + suffix
#          1 target  Corr      file, keyed as: 'strandCorr' + suffix

from src.logicalStep import LogicalStep
from src.wrappers import samtools, sampleBam, bedtools, picardTools, census, phantomTools

class BamEvaluateStep(LogicalStep):

    def __init__(self, experiment, suffix, sampleSize):
        self.suffix = str(suffix)
        self.sampleSize = sampleSize
        LogicalStep.__init__(self, experiment, 'bamEvaluate_' + self.suffix)
        
    def onRun(self):      

        # Versions:
        samtools.version(self)
        sampleBam.version(self)
        bedtools.version(self)
        picardTools.version(self)
        census.version(self)
        phantomTools.version(self)
        
        # Outputs:
        samSample  = self.declareTempFile('samSample' + self.suffix, ext='sam')
        #bamSample = self.declareTempFile('bamSample' + self.suffix, ext='bam')
        metricHist = self.declareExpFile( 'histo'     + self.suffix, ext='metric')
        strandCorr = self.declareExpFile( 'strandCorr'+ self.suffix, ext='')
        
        # Inputs:
        bam = self.exp.getFile('bam' + self.suffix)
        
        bamSize = samtools.bamSize(self,bam)
        # Take the whole bam if it is smaller than sampleSize requested.        
        if self.sampleSize > bamSize:
            self.sampleSize=bamSize
        
        bed        = self.declareGarbageFile('bed')
        bamSample  = self.declareGarbageFile('bam')
        
        sampleBam.sample(self,bam,bamSize,self.sampleSize,bed)
        bedtools.bedToSam(self,bed,samSample)
        picardTools.samSortToBam(self,samSample,bamSample)  # Is this a target?  Probably not
        census.metrics(self,bamSample,metricHist)
        phantomTools.strandCorr(self,bamSample,strandCorr)

