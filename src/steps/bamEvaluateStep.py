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
        
    def writeVersions(self,file=None):
        '''Writes versions to to the log or a file.'''
        if file != None:
            file.add('samtools', samtools.version(self))
            file.add('sampleBam', sampleBam.version(self))
            file.add('bedtools', bedtools.version(self))
            file.add('picardTools', picardTools.version(self))
            file.add('census', census.version(self))
            file.add('phantomTools', phantomTools.version(self))
        else:
            samtools.version(self)
            sampleBam.version(self)
            bedtools.version(self)
            picardTools.version(self)
            census.version(self)
            phantomTools.version(self)

    def onRun(self):      
        self.writeVersions()

        # Inputs:
        bam = self.ana.getFile('bamRep%s.bam' % self.replicate)
        
        # Outputs:
        metricHist = self.declareTargetFile( 'metricRep'     + self.replicate, ext='txt')
        strandCorr = self.declareTargetFile( 'strandCorrRep'+ self.replicate, ext='txt')
        # because garbage bam file name is used in output, it needs a meaningful name:
        fileName = os.path.split( bam )[1]
        root = os.path.splitext( fileName )[0]
        bamSample  = self.declareInterimFile('bamSampleRep' + self.replicate, \
                                             name=root + '_sample', ext='bam')
        
        bamSize = samtools.bamSize(self,bam)
        
        
        if self.sampleSize < bamSize:
            bed        = self.declareGarbageFile('bed')
            bamUnsorted  = self.declareGarbageFile('bamUnsortedSample',ext='bam')
            sampleBam.sample(self,bam,bamSize,self.sampleSize,bed)
            bedtools.bedToBam(self,bed,bamUnsorted)
        else:
            bamUnsorted = bam
            
        picardTools.sortBam(self,bamUnsorted,bamSample)
        census.metrics(self,bamSample,metricHist)
        phantomTools.strandCorr(self,bamSample,strandCorr)

