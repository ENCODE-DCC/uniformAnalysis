#!/usr/bin/env python2.7
# hotspotStep.py module holds HotspotStep class which descends from LogicalStep class.
# It takes a bam input and calls peaks using hotspot.
#
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'alignmentRep' + replicate + '.bam'
#
# Outputs: 1 target  peak file, keyed as: 'peaksRep' + replicate + '.bed'

import os
from src.logicalStep import LogicalStep
from src.wrappers import hotspot

class HotspotStep(LogicalStep):

    def __init__(self, analysis, replicate):
        self.replicate = str(replicate)
        LogicalStep.__init__(self, analysis, analysis.readType + 'Hotspot_Rep' + self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def writeVersions(self,raFile=None):
        '''Writes versions to to the log or a file.'''
        if raFile != None:
            raFile.add('hotspot', hotspot.version(self))
        else:
            hotspot.version(self)

    def onRun(self):
        # Inputs:
        bam = self.ana.getFile('alignmentRep' + self.replicate + '.bam')
        
        # Outputs:
        #peaks = self.declareTargetFile('peaksRep' + self.replicate,ext='bed') # is this a bed?
        fileName = os.path.split( bam )[1]
        root = os.path.splitext( fileName )[0]
        peaks = self.declareTargetFile('peaksRep' + self.replicate + '.bed', \
                                       name=root + '-peaks/' + root + '.peaks',ext='bed')
        # TODO: determine what the actual targets really are:
        #hotspots = self.declareTargetFile('hotRep' + self.replicate + '.bed', \
        #                               name=root + '-final/' + root + '.hot',ext='bed')
        #starchedBed = self.declareTargetFile('bedRep' + self.replicate + '.starch', \
        #                           name=root + '-peaks/' + root + '.tagdensity.bed.starch',ext='')
        
        tokensName = self.declareGarbageFile('tokens',ext='txt')
        runhotspotName = self.declareGarbageFile('runhotspot',ext='sh')
        
        hotspot.runHotspot(self, tokensName, runhotspotName, bam, peaks)

