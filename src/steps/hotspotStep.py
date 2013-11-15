#!/usr/bin/env python2.7
# hotspotStep.py module holds HotspotStep class which descends from LogicalStep class.
# It takes a bam input and calls peaks using hotspot.
#
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'alignmentRep' + replicate + '.bam'
#
# Outputs: target broadPeak hotspot file,     keyed as: 'hot'     + suffix + '.bed'
#          target broadPeak hotspot FDR file, keyed as: 'hotFrd'  + suffix + '.bed'
#          target narrowPeak peaks file,      keyed as: 'peaks'   + suffix + '.bed'
#          interim density bed file,          keyed as: 'density' + suffix + '.bed.starch'
#          target density bigWig file,        keyed as: 'density' + suffix + '.bigWig'

import os
from src.logicalStep import LogicalStep
from src.wrappers import hotspot, bedops, bedtools, ucscUtils

class HotspotStep(LogicalStep):

    def __init__(self, analysis, suffix, tagLen=36):
        self.suffix = str(suffix)
        #self.replicate = str(replicate)
        self.tagLen    = str(tagLen)
        LogicalStep.__init__(self, analysis, 'hotspot_' + self.suffix)
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
        bam = self.ana.getFile('alignment' + self.suffix + '.bam')
        
        # Outputs:
        fileName = os.path.split( bam )[1]
        root = os.path.splitext( fileName )[0]
        # broad peaks:
        self.declareTargetFile('hot' + self.suffix + '.bed', \
                               name=root + '-final/' + root + '.hot.bed')
        self.declareTargetFile('hotFdr' + self.suffix + '.bed', \
                               name=root + '-final/' + root + '.fdr0.01.hot.bed')
        # narrow peaks:
        self.declareTargetFile('peaks' + self.suffix + '.bed', \
                               name=root + '-final/' + root + '.fdr0.01.pks.bed')
        # densityBed to be turned into a bigWig
        starched = self.declareInterimFile('density' + self.suffix + '.bed.starch', \
                                name=root + '-peaks/' + root + '.tagdensity.bed.starch')
        bigWig = self.declareTargetFile('density' + self.suffix + '.bigWig')
        
        # run hotspot pipeline (many scripts)
        tokensName = self.declareGarbageFile('tokens.txt')
        runhotspotName = self.declareGarbageFile('runhotspot.sh')
        hotspot.runHotspot(self, tokensName, runhotspotName, bam, self.tagLen)

        # "unstarch input.bed.starch > output.bed"
        unstarched  = self.declareGarbageFile('unstarched.bed')
        bedops.unstarch(self, starched, unstarched)

        # convert to bedGraph
        bedGraph = self.declareGarbageFile('density' + self.suffix + '.bedGraph')
        bedtools.toBedGraph(self, self.tagLen, unstarched, bedGraph)

        # And finally convert density bedGraph to bigWig
        ucscUtils.bedGraphToBigWig(self, bedGraph, bigWig)
 
        # TODO: Union DHS overlap on the peaks with hotspot
        # https://github.com/qinqian/GCAP/blob/master/gcap/funcs/union_dhs_overlap.py union_DHS_overlap()
