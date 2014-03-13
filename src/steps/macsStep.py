#!/usr/bin/env python2.7
# macsStep.py module holds HotspotStep class which descends from LogicalStep class.
# It takes a bam input and calls peaks using MACS.
#
# Inputs: 1 bam, pre-registered in analysis           keyed as: 'alignment' + suffix + '.bam'
#         1 bam control (optional), pre-registered    keyed as: 'control' + suffix + '.bam'
# Outputs: target narrowPeak peaks file,      keyed as: 'peaks'     + suffix + '.bigBed'
#          target density bigWig file,        keyed as: 'density'   + suffix + '.bigWig'

from src.logicalStep import LogicalStep

class MacsStep(LogicalStep):

    def __init__(self, analysis, suffix, expType='ChIPseq',isPaired=False):
        self.suffix = str(suffix)
        #self.replicate = str(replicate)
        self.expType    = str(expType)
        self.isPaired   = isPaired
        LogicalStep.__init__(self, analysis, 'peaksByMacs_' + self.suffix)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('macs',                     self.getToolVersion('macs2'))
            raFile.add('eap_macs2_xls_to_narrowPeak', 
                                                self.getToolVersion('eap_macs2_xls_to_narrowPeak'))
            raFile.add('eap_narrowPeak_to_bigBed', self.getToolVersion('eap_narrowPeak_to_bigBed'))
            raFile.add('bedGraphToBigWig',         self.getToolVersion('bedGraphToBigWig'))
        else:
            self.getToolVersion('macs2')
            self.getToolVersion('eap_macs2_xls_to_narrowPeak')
            self.getToolVersion('eap_narrowPeak_to_bigBed')
            self.getToolVersion('bedGraphToBigWig')

    def onRun(self):
        # Inputs:
        bam = self.ana.getFile('alignment' + self.suffix + '.bam')
        if self.expType.lower() == 'chipseq':
            control = self.ana.getFile('control' + self.suffix + '.bam')

        # Outputs:
        narrowPeaks = self.declareTargetFile('peaks'   + self.suffix + '.bigBed')
        bigWig      = self.declareTargetFile('density' + self.suffix + '.bigWig')

        if self.expType.lower() == 'chipseq':
            if self.isPaired:
                self.eap_chip_pe(self.ana.genome, bam, control, narrowPeaks, bigWig)
            else:
                self.eap_chip_se(self.ana.genome, bam, control, narrowPeaks, bigWig)
        elif self.expType.lower() == 'dnase':
            if self.isPaired:
                self.eap_dnase_pe(self.ana.genome, bam, narrowPeaks, bigWig)
            else:
                self.eap_dnase_se(self.ana.genome, bam, narrowPeaks, bigWig)
        else:
            self.fail("Only ChIP-seq or DNase experiment types supported. " + \
                      "'" + self.encoding + "' is not supported.")

    def eap_dnase_se(self, genome, inBam, outBigBed, outBigWig):
        '''Single-end macs2 peak-calling for DNase'''
        
        # usage v2: eap_run_macs2_dnase_se target in.bam out.narrowPeak.bigBed out.bigWig
        cmd = "eap_run_macs2_dnase_se {target} {bam} {bbOut} {bwOut}".format( \
              target=genome, bam=inBam, \
              bbOut=outBigBed, bwOut=outBigWig)
              
        toolName = 'eap_run_macs2_dnase_se'
        self.toolBegins(toolName)
        self.getToolVersion(toolName,logOut=True)
        self.getToolVersion('macs2',logOut=True)
        self.getToolVersion('eap_macs2_xls_to_narrowPeak',logOut=True)
        self.getToolVersion('eap_narrowPeak_to_bigBed',logOut=True)
        self.getToolVersion('bedGraphToBigWig', logOut=True)
    
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
    
    def eap_dnase_pe(self, genome, inBam, outBigBed, outBigWig):
        '''Paired-end macs2 peak-calling for DNase'''
        
        # usage v2: eap_run_macs2_dnase_pe target in.bam out.narrowPeak.bigBed out.bigWig
        cmd = "eap_run_macs2_dnase_pe {target} {bam} {bbOut} {bwOut}".format( \
              target=genome, bam=inBam, \
              bbOut=outBigBed, bwOut=outBigWig)
              
        toolName = "eap_run_macs2_dnase_pe"
        self.toolBegins(toolName)
        self.getToolVersion(toolName,logOut=True)
        self.getToolVersion('macs2',logOut=True)
        self.getToolVersion('eap_macs2_xls_to_narrowPeak',logOut=True)
        self.getToolVersion('eap_narrowPeak_to_bigBed',logOut=True)
        self.getToolVersion('bedGraphToBigWig', logOut=True)
    
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
    
    def eap_chip_se(self, genome, inBam, controlBam, outBigBed, outBigWig):
        '''Single-end macs2 peak-calling for Chip-seq'''
        
        # usage v1: eap_run_macs2_chip_se target in.bam control.bam out.narrowPeak.bigBed out.bigWig
        cmd = "eap_run_macs2_chip_se {target} {bam} {bamControl} {bbOut} {bwOut}".format( \
              target=genome, bam=inBam, bamControl=controlBam, \
              bbOut=outBigBed, bwOut=outBigWig)
              
        toolName = 'eap_run_macs2_chip_se'
        self.toolBegins(toolName)
        self.getToolVersion(toolName,logOut=True)
        self.getToolVersion('macs2',logOut=True)
        self.getToolVersion('eap_macs2_xls_to_narrowPeak',logOut=True)
        self.getToolVersion('eap_narrowPeak_to_bigBed',logOut=True)
        self.getToolVersion('bedGraphToBigWig', logOut=True)
    
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
    
    def eap_chip_pe(self, genome, inBam, controlBam, outBigBed, outBigWig):
        '''Paired-end macs2 peak-calling for Chip-seq'''
        
        # usage v1: eap_run_macs2_chip_pe target in.bam control.bam out.narrowPeak.bigBed out.bigWig
        cmd = "eap_run_macs2_chip_pe {target} {bam} {bamControl} {bbOut} {bwOut}".format( \
              target=genome, bam=inBam, bamControl=controlBam, \
              bbOut=outBigBed, bwOut=outBigWig)
              
        toolName = 'eap_run_macs2_chip_pe'
        self.toolBegins(toolName)
        self.getToolVersion(toolName,logOut=True)
        self.getToolVersion('macs2',logOut=True)
        self.getToolVersion('eap_macs2_xls_to_narrowPeak',logOut=True)
        self.getToolVersion('eap_narrowPeak_to_bigBed',logOut=True)
        self.getToolVersion('bedGraphToBigWig', logOut=True)
    
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
