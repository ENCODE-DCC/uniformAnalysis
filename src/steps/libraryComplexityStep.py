#!/usr/bin/env python2.7
# librarycomplexity.py module holds LibraryComplexityStep class which descends from LogicalStep class.
# It takes a sample sam and characterizes the library completity
#
# Inputs: 1 sampled sam, pre-registered in the experiment keyed as: 'samSample' + suffix
#
# Outputs: 1 target  histogram file, keyed as: 'histo' + suffix
#          1 target  Corr      file, keyed as: 'strandCorr' + suffix

from src.logicalstep import LogicalStep
from src.wrappers import picardTools, census, phantomTools

class LibraryComplexityStep(LogicalStep):

    def __init__(self, experiment, suffix, sampleSize):
        self.suffix = str(suffix)
        LogicalStep.__init__(self, experiment, 'libraryComplexity_' + self.suffix)
        #self.bam = bam
        
    def onRun(self):      

        # Versions:
        picardTools.version(self)
        census.version(self)
        phantomTools.version(self)
        
        # Outputs:
        samSample  = self.declareTempFile('samSample' + self.suffix, ext='sam')
        #bamSample = self.declareTempFile('bamSample' + self.suffix, ext='bam')
        metricHist = self.declareExpFile( 'histo'     + self.suffix, ext='metric')
        strandCorr = self.declareExpFile( 'strandCorr'+ self.suffix, ext='')
        
        # Inputs:
        samSample = self.exp.getFile('samSample' + self.suffix)
        
        bamSample  = self.declareGarbageFile('bam')
        
        picardTools.samSortToBam(self,samSample,bamSample)  # Is this a target?  Probably not
        census.metrics(self,bamSample,metricHist)
        phantomTools.strandCorr(self,bamSample,strandCorr)
        
        # python2.7 /cluster/home/mmaddren/grad/pipeline/gcap/census-master/bam_to_histo.py /cluster/home/mmaddren/grad/pipeline/gcap/census-master/seq.cov005.ONHG19.bed
        # UwDgfRep1_5M_sort.bam | python2.7 /cluster/home/mmaddren/grad/pipeline/gcap/census-master/calculate_libsize.py - > UwDgfRep1_census.metric

