#!/usr/bin/env python2.7
# hotspotStep.py module holds HotspotStep class which descends from LogicalStep class.
# It takes a bam input and calls peaks using hotspot.
#
# Inputs: 1 bam, pre-registered in analysis   keyed as: 'alignment' + suffix + '.bam'
#
# Outputs: target broadPeak hotspot file,     keyed as: 'hot'       + suffix + '.bigBed'
#          target narrowPeak peaks file,      keyed as: 'peaks'     + suffix + '.bigBed'
#          target density bigWig file,        keyed as: 'density'   + suffix + '.bigWig'

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
        broadPeaks  = self.declareTargetFile('hot'     + self.suffix + '.bigBed')
        narrowPeaks = self.declareTargetFile('peaks'   + self.suffix + '.bigBed')
        bigWig      = self.declareTargetFile('density' + self.suffix + '.bigWig')

        # usage v1: 
        #     eap_run_hotspot genome input.bam readLength out.narrowPeak out.broadPeak out.bigWig
        hotspot.eap_hotspot(self, self.ana.genome, bam, self.tagLen, \
                            narrowPeaks, broadPeaks, bigWig)
