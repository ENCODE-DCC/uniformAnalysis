#!/usr/bin/env python2.7
# bamEvaluateStep.py module holds BamEvaluateStep class which descends from LogicalStep class.
# It takes a sample of a bam and characterizes the library completity
#
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'alignmentRep' + replicate + '.bam'
#
# Outputs: 1 interim bam sample file, keyed as: 'sampleRep'     + replicate + '.bam'
#          1 target  histogram  file, keyed as: 'metricRep'     + replicate + '.txt'
#          1 target  Corr       file, keyed as: 'strandCorrRep' + replicate + '.txt'

import os
from src.logicalStep import LogicalStep
from src.wrappers import samtools, bedtools, picardTools, census, phantomTools

class BamEvaluateStep(LogicalStep):

    def __init__(self, analysis, replicate, sampleSize):
        self.replicate = str(replicate)
        self.sampleSize = sampleSize
        LogicalStep.__init__(self, analysis, 'bamEvaluate_Rep' + self.replicate)
        
    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('samtools', samtools.version(self))
            raFile.add('bedtools', bedtools.version(self))
            raFile.add('picardTools', picardTools.version(self))
            raFile.add('census', census.version(self))
            raFile.add('phantomTools', phantomTools.version(self))
        else:
            samtools.version(self)
            bedtools.version(self)
            picardTools.version(self)
            census.version(self)
            phantomTools.version(self)

    def onRun(self):      
        # Inputs:
        bam = self.ana.getFile('alignmentRep' + self.replicate + '.bam')
        
        # Outputs:
        metricHist = self.declareTargetFile( 'metricRep'    + self.replicate + '.txt')
        strandCorr = self.declareTargetFile( 'strandCorrRep'+ self.replicate + '.txt')
        # because garbage bam file name is used in output, it needs a meaningful name:
        fileName = os.path.split( bam )[1]
        root = os.path.splitext( fileName )[0]
        bamSample  = self.declareInterimFile('sampleRep' + self.replicate + '.bam', \
                                             name=root + '_sample.bam')
        
        bamSize = samtools.bamSize(self,bam)
         
        if self.sampleSize < bamSize:
            bamUnsorted  = self.declareGarbageFile('bamUnsortedSample.bam')
            picardTools.downSample(self,(self.sampleSize/float(bamSize)),bam,bamUnsorted)
        else:
            bamUnsorted = bam
            
        picardTools.sortBam(self,bamUnsorted,bamSample)
        census.metrics(self,bamSample,metricHist)
        
        # TODO: convert census metrics into json + document
        # https://github.com/qinqian/GCAP/blob/master/gcap/funcs/library_complexity.py stat_redun_census(), redundancy_doc()
        
        phantomTools.strandCorr(self,bamSample,strandCorr)
        
        # TODO: convert strand corr into json + document
        # https://github.com/qinqian/GCAP/blob/master/gcap/funcs/nsc_rsc.py stat_strand_cor() strand_cor_doc()

        # TODO: calculate fragment size with picard tools (pe) or macs2 (se) create document
        # https://github.com/qinqian/GCAP/blob/master/gcap/funcs/fragment.py fragment_size()
