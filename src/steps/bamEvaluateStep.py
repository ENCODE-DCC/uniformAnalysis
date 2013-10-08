#!/usr/bin/env python2.7
# bamEvaluateStep.py module holds BamEvaluateStep class which descends from LogicalStep class.
# It takes a sample of a bam and characterizes the library completity
#
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'bamRep' + replicate
#
# Outputs: 1 interim sam       file, keyed as: 'samSampleRep'  + replicate
#          1 target  histogram file, keyed as: 'metricRep'     + replicate
#          1 target  Corr      file, keyed as: 'strandCorrRep' + replicate

import os
from src.logicalStep import LogicalStep
from src.wrappers import samtools, sampleBam, bedtools, picardTools, census, phantomTools

class BamEvaluateStep(LogicalStep):

    def __init__(self, analysis, replicate, sampleSize):
        self.replicate = str(replicate)
        self.sampleSize = sampleSize
        LogicalStep.__init__(self, analysis, 'bamEvaluate_Rep' + self.replicate)
        
    def onRun(self):      

        # Versions:
        samtools.version(self)
        sampleBam.version(self)
        bedtools.version(self)
        picardTools.version(self)
        census.version(self)
        phantomTools.version(self)
        
        # Outputs:
        samSample  = self.declareInterimFile('samSampleRep' + self.replicate, ext='sam')
        #bamSample = self.declareInterimFile('bamSampleRep' + self.replicate, ext='bam')
        metricHist = self.declareTargetFile( 'metricRep'     + self.replicate, ext='txt')
        strandCorr = self.declareTargetFile( 'strandCorrRep'+ self.replicate, ext='txt')
        
        # Inputs:
        bam = self.ana.getFile('bamRep' + self.replicate)
        
        bamSize = samtools.bamSize(self,bam)
        # Take the whole bam if it is smaller than sampleSize requested.        
        if self.sampleSize > bamSize:
            self.sampleSize=bamSize - 1 # TODO: this is a hack since sampleBam is currently not working with inSize=outSize, we should handle this case more elegantly
        
        # because garbage bam file name is used in output, it needs a meaningful name:
        fileName = os.path.split( bam )[1]
        root = os.path.splitext( fileName )[0]

        bed        = self.declareGarbageFile('bed')
        bamSample  = self.declareGarbageFile('bam',name=root+'_sample',ext='bam')
        
        sampleBam.sample(self,bam,bamSize,self.sampleSize,bed)
        bedtools.bedToSam(self,bed,samSample)
        picardTools.samSortToBam(self,samSample,bamSample)
        census.metrics(self,bamSample,metricHist)
        phantomTools.strandCorr(self,bamSample,strandCorr)

