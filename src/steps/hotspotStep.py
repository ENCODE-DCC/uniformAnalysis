#!/usr/bin/env python2.7
# hotspotStep.py module holds HotspotStep class which descends from LogicalStep class.
# It takes a bam input and calls peaks using hotspot.
#
# Inputs: 1 bam, pre-registered in analysis   keyed as: 'alignment' + suffix + '.bam'
# Outputs: target broadPeak hotspot file,     keyed as: 'hot'       + suffix + '.bigBed'
#          target narrowPeak peaks file,      keyed as: 'peaks'     + suffix + '.bigBed'
#          target density bigWig file,        keyed as: 'density'   + suffix + '.bigWig'

from src.logicalStep import LogicalStep

class HotspotStep(LogicalStep):

    def __init__(self, analysis, suffix, tagLen=36):
        self.suffix = str(suffix)
        #self.replicate = str(replicate)
        self.tagLen    = int(tagLen)
        LogicalStep.__init__(self, analysis, 'peaksByHotspot_' + self.suffix)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('eap_run_hotspot', self.getToolVersion('eap_run_hotspot'))
            raFile.add('hotspot',     self.getToolVersion( \
                                      self.ana.toolsDir+'hotspot-distr/hotspot-deploy/bin/hotspot'))
            raFile.add('python2.7',   self.getToolVersion('python2.7'))
            raFile.add('hotspot.py',  self.getToolVersion('hotspot.py'))
            raFile.add('bedToBigBed', self.getToolVersion('bedToBigBed'))
            raFile.add('bedmap',      self.getToolVersion('bedmap'))
            raFile.add('sort-bed',    self.getToolVersion('sort-bed'))
            raFile.add('starchcat',   self.getToolVersion('starchcat'))
            raFile.add('unstarch',    self.getToolVersion('unstarch'))
            raFile.add('intersectBed',self.getToolVersion( \
                                                    self.ana.toolsDir+'bedtools/bin/intersectBed'))
            raFile.add('bedGraphPack',self.getToolVersion('bedGraphPack'))
            raFile.add('bedGraphToBigWig', self.getToolVersion('bedGraphToBigWig'))
        else:
            self.getToolVersion('eap_run_hotspot')
            self.getToolVersion(self.ana.toolsDir+'hotspot-distr/hotspot-deploy/bin/hotspot')
            self.getToolVersion('python2.7')
            self.getToolVersion('hotspot.py')
            self.getToolVersion('bedToBigBed')
            self.getToolVersion('bedmap')
            self.getToolVersion('sort-bed')
            self.getToolVersion('starchcat')
            self.getToolVersion('unstarch')
            self.getToolVersion(self.ana.toolsDir+'bedtools/bin/intersectBed')
            self.getToolVersion('bedGraphPack')
            self.getToolVersion('bedGraphToBigWig')

    def onRun(self):
        # Inputs:
        bam = self.ana.getFile('alignment' + self.suffix + '.bam')

        # Outputs:
        broadPeaks  = self.declareTargetFile('hot'     + self.suffix + '.bigBed')
        narrowPeaks = self.declareTargetFile('peaks'   + self.suffix + '.bigBed')
        bigWig      = self.declareTargetFile('density' + self.suffix + '.bigWig')

        self.eap_hotspot(self.ana.genome, bam, self.tagLen, narrowPeaks, broadPeaks, bigWig)

    def eap_hotspot(self, genome, inBam, tagLen, outNarrowPeak, outBroadPeak, outBigWig):
        '''Hostspot peak calling'''
        
        cmd = "eap_run_hotspot {db} {bam} {readLen} {narrowOut} {broadOut} {bwOut}".format( \
              db=genome, bam=inBam, readLen=tagLen, \
              narrowOut=outNarrowPeak, broadOut=outBroadPeak, bwOut=outBigWig)
              
        toolName = 'eap_run_hotspot'
        self.toolBegins(toolName)
        self.writeVersions()

        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
