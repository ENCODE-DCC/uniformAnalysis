#!/usr/bin/env python2.7
# hotspotStep.py module holds HotspotStep class which descends from LogicalStep class.
# It takes a bam input and calls peaks using hotspot.
#
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'alignmentRep' + replicate + '.bam'
#
# Outputs: target broadPeak hotspot file, keyed as: 'hotRep' + replicate + '.bed'
#          interim broadPeak hotspot FDR file, keyed as: 'hotFrdRep' + replicate + '.bed'
#          target narrowPeak peaks file, keyed as: 'peaksRep' + replicate + '.bed'
#          interim density bed file, keyed as: 'densityRep' + replicate + '.bed.starch'
#          target density bigWig file, keyed as: 'densityRep' + replicate + '.bigWig'

import os
from src.logicalStep import LogicalStep
from src.wrappers import hotspot, bedops, bedtools, ucscUtils

class HotspotStep(LogicalStep):

    def __init__(self, analysis, replicate, tagLen):
        self.replicate = str(replicate)
        self.tagLen    = str(tagLen)
        LogicalStep.__init__(self, analysis, 'hotspot_Rep' + self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('hotspot',hotspot.version(self))
            raFile.add('bedops',  bedops.version(self))
            raFile.add('bedtools', bedtools.version(self))
            raFile.add('ucscUtils', ucscUtils.version(self, tool='bedGraphToBigWig'))
        else:
            hotspot.version(self)
            bedops.version(self)
            bedtools.version(self)
            ucscUtils.version(self, tool='bedGraphToBigWig')

    def onRun(self):
        # Inputs:
        bam = self.ana.getFile('alignmentRep' + self.replicate + '.bam')
        
        # Outputs:
        fileName = os.path.split( bam )[1]
        root = os.path.splitext( fileName )[0]
        # TODO: determine what the actual targets really are:
        # FROM hotspot README (Running hotspot) will leave a final output directory whose name is
        # the same as the tags file name, appended with the suffix "-final".  Within this
        # directory will be found files with some or all of the following names:
        #   *.hot.bed                 minimally thresholded hotspots
        #   *.fdr0.01.hot.bed         FDR thresholded hotspots
        #   *.fdr0.01.pks.bed         FDR thresholded peaks
        #   *.fdr0.01.pks.dens.txt    smoothed tag density value at each peak
        #   *.fdr0.01.pks.zscore.txt  z-score for the hotspot containing each peak
        #   *.fdr0.01.pks.pval.txt    binomial p-value for the hotspot containing each peak
        # broad peaks:
        self.declareResultFile('hotRep' + self.replicate + '.bed', \
                               name=root + '-final/' + root + '.hot.bed')
        self.declareResultFile('hotFdrRep' + self.replicate + '.bed', \
                               name=root + '-final/' + root + '.fdr0.01.hot.bed')
        # narrow peaks:
        self.declareResultFile('peaksRep' + self.replicate + '.bed', \
                               name=root + '-final/' + root + '.fdr0.01.pks.bed')
        # densityBed to be turned into a bigWig
        starched = self.declareResultFile('densityRep' + self.replicate + '.bed.starch', \
                                name=root + '-peaks/' + root + '.tagdensity.bed.starch')
        bigWig = self.declareResultFile('densityRep' + self.replicate + '.bigWig')
        
        # TODO: check GCAP pipeline code for config parameters:
        # https://github.com/qinqian/GCAP/blob/master/gcap/funcs/peaks_calling.py spot_conf()
        
        tokensName = self.declareGarbageFile('tokens.txt')
        runhotspotName = self.declareGarbageFile('runhotspot.sh')
        
        ### run hotspot pipeline (many scripts)
        hotspot.runHotspot(self, tokensName, runhotspotName, bam, self.tagLen)

        ### Now convert density bed.starch to bedGraph
        
        # "unstarch input.bed.starch > output.bed"
        unstarched  = self.declareGarbageFile('unstarched.bed')
        bedops.unstarch(self, starched, unstarched)
        #
        # convert to bedGraph
        bedGraph = self.declareGarbageFile('densityRep' + self.replicate + '.bedGraph')
        bedtools.toBedGraph(self, self.tagLen, unstarched, bedGraph)
        
        ### And finally convert density bedGraph to bigWig
        ucscUtils.bedGraphToBigWig(self, bedGraph, bigWig)
 
        # 0) run hostpot on replicate bams (1 per replicate)
        # Need to:
        # 1) convert densityBed to bigWig (bedGrahToBigWig (?)
        # 2) merge replicate full bams
        # 3) run hotspot on merged replicate   (1 only)
        # 4) convert mergedDensityBam to bigWig
        # 5) run hotspot on each 5M sample bam (1 per replicate)
        # Expect 3 targets per rep (hot,pk,bigWig) + 4 for merged (bam,hot,pk,bigWig)
        #    and 3 per 5M sampleBam = 10+6=16
        
        # TODO: Additional processing to generate bigWig file and filter output, and get SPOT score by running on 5M sampling:
        # https://github.com/qinqian/GCAP/blob/master/gcap/funcs/peaks_calling.py _hotspot_on_replicates()

        # TODO: Union DHS overlap on the peaks with hotspot
        # https://github.com/qinqian/GCAP/blob/master/gcap/funcs/union_dhs_overlap.py union_DHS_overlap()