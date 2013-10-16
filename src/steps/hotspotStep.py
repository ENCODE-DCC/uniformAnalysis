#!/usr/bin/env python2.7
# hotspotStep.py module holds HotspotStep class which descends from LogicalStep class.
# It takes a bam input and calls peaks using hotspot.
#
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'bamRep' + replicate
#
# Outputs: 1 target  peak file, keyed as: 'peaksRep' + replicate

from src.logicalStep import LogicalStep
from src.wrappers import hotspot

class HotspotStep(LogicalStep):

    def __init__(self, analysis, replicate):
        self.replicate = str(replicate)
        LogicalStep.__init__(self, analysis, analysis.readType() + 'Hotspot_Rep' + self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def writeVersions(self,file=None):
        '''Writes versions to to the log or a file.'''
        if file != None:
            #   writes self._stepVersion and each tool version to the file
            pass
        else:
            hotspot.version(self)

    def onRun(self):
        self.writeVersions()
        
        # Outputs:
        peaks = self.declareTargetFile('peaksRep' + self.replicate,ext='bed') # is this a bed?
        
        # Inputs:
        bam = self.ana.getFile('bamRep%s.bam' % self.replicate)
        
        tokensName = self.declareGarbageFile('tokens',ext='txt')
        runhotspotName = self.declareGarbageFile('runhotspot',ext='sh')
        
        hotspot.runHotspot(self, tokensName, runhotspotName, bam, peaks)

