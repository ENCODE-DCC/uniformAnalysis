########### OBSOLETE!  Replaced by BamEvaluateStep.py ############
########### OBSOLETE!  Replaced by BamEvaluateStep.py ############
########### OBSOLETE!  Replaced by BamEvaluateStep.py ############

#!/usr/bin/env python2.7
# librarycomplexity.py module holds LibraryComplexityStep class which descends from LogicalStep class.
# It takes a sample sam and characterizes the library completity
#
# Inputs: 1 sampled sam, pre-registered in the analysis keyed as: 'samSampleRep' + replicate+'.sam'
#
# Outputs: 1 target  histogram file, keyed as: 'histoRep' + replicate + '.txt'
#          1 target  Corr      file, keyed as: 'strandCorrRep' + replicate + '.txt'

from src.logicalstep import LogicalStep
from src.wrappers import picardTools, census, phantomTools

class LibraryComplexityStep(LogicalStep):

    def __init__(self, analysis, replicate, sampleSize):
        self.replicate = str(replicate)
        LogicalStep.__init__(self, analysis, 'libraryComplexity_Rep' + self.replicate)
        #self.bam = bam

    def writeVersions(self,raFile=None):
        '''Writes versions to to the log or a file.'''
        if raFile != None:
            #   writes self._stepVersion and each tool version to the file
            pass
        else:
            picardTools.version(self)
            census.version(self)
            phantomTools.version(self)

    def onRun(self):      
        # Outputs:
        #samSample  = self.declareInterimFile('samSampleRep' + self.replicate + '.sam', ext='sam')
        metricHist = self.declareTargetFile( 'histoRep'     + self.replicate + '.txt', ext='metric')
        strandCorr = self.declareTargetFile( 'strandCorrRep'+ self.replicate + '.txt', ext='')
        
        # Inputs:
        samSample = self.ana.getFile('samSampleRep' + self.replicate + '.sam')
        
        bamSample  = self.declareGarbageFile('bam')
        
        picardTools.samSortToBam(self,samSample,bamSample)  # Is this a target?  Probably not
        census.metrics(self,bamSample,metricHist)
        phantomTools.strandCorr(self,bamSample,strandCorr)
        
        # python2.7 /cluster/home/mmaddren/grad/pipeline/gcap/census-master/bam_to_histo.py /cluster/home/mmaddren/grad/pipeline/gcap/census-master/seq.cov005.ONHG19.bed
        # UwDgfRep1_5M_sort.bam | python2.7 /cluster/home/mmaddren/grad/pipeline/gcap/census-master/calculate_libsize.py - > UwDgfRep1_census.metric

