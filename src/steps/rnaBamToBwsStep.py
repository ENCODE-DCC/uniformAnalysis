#!/usr/bin/env python2.7
# rnaBamToBwsStep.py module holds RnaBamToBwsStep class which descends from LogicalStep class.
# It takes a bam input and generates four bigwig signals.
#
# Inputs: 1 bam, pre-registered in analysis, keyed as: 'alignment' + suffix + '.bam'
# Outputs: target uniq + strand signal file, keyed as: 'uniqPlus'  + suffix + '.bw'
#          target uniq - strand signal file, keyed as: 'uniqMinus' + suffix + '.bw'
#          target all  + strand signal file, keyed as: 'allPlus'   + suffix + '.bw'
#          target all  - strand signal file, keyed as: 'allMinus'  + suffix + '.bw'

from src.logicalStep import LogicalStep

class RnaBamToBwsStep(LogicalStep):

    def __init__(self, analysis, suffix, tagLen=36):
        self.suffix = str(suffix)
        #self.replicate = str(replicate)
        self.tagLen    = int(tagLen)
        LogicalStep.__init__(self, analysis, 'rnaBamToBws_' + self.suffix)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('eap_run_rna_bam_to_bigwigs', \
                       self.getToolVersion('eap_run_rna_bam_to_bigwigs'))
            self.getToolVersion('samtools')
            raFile.add('makewigglefromBAM-NH.py', \
                       self.getToolVersion('makewigglefromBAM-NH.py'))
            raFile.add('python2.7',   self.getToolVersion('python2.7'))
            raFile.add('wigToBigWig',  self.getToolVersion('wigToBigWig'))
            #raFile.add('perl', self.getToolVersion('perl'))
        else:
            self.getToolVersion('eap_run_rna_bam_to_bigwigs')
            self.getToolVersion('samtools')
            self.getToolVersion('makewigglefromBAM-NH.py')
            self.getToolVersion('python2.7')
            self.getToolVersion('wigToBigWig')
            #self.getToolVersion('perl')

    def onRun(self):
        # Inputs:
        bam = self.ana.getFile('alignment' + self.suffix + '.bam')

        # Outputs:
        uniqPlusBw  = self.declareTargetFile('uniqPlus'  + self.suffix + '.bw')
        uniqMinusBw = self.declareTargetFile('uniqMinus' + self.suffix + '.bw')
        allPlusBw   = self.declareTargetFile('allPlus'   + self.suffix + '.bw')
        allMinusBw  = self.declareTargetFile('allMinus'  + self.suffix + '.bw')

        # male will be fine.
        chromFile = self.ana.refDir + "male." +self.ana.genome + "/chrom.sizes"
        if self.ana.gender == 'female':  # male and unspecified are treated the same
            chromFile = self.ana.refDir + self.ana.gender + '.' + self.ana.genome + "/chrom.sizes"

        self.eap_bamToBigWigs(bam, chromFile, uniqPlusBw, uniqMinusBw, allPlusBw, allMinusBw)

    def eap_bamToBigWigs(self, inBam, chromFile, uniqPlusOut,uniqMinusOut,allPlusOut,allMinusOut):
        '''Hostspot peak calling'''
        
        cmd = "eap_run_rna_bam_to_bigwigs {bam} {chroms} {upOut} {umOut} {apOut} {amOut}".format( \
              bam=inBam, chroms=chromFile, \
              upOut=uniqPlusOut, umOut=uniqMinusOut, apOut=allPlusOut, amOut=allMinusOut)
              
        toolName = 'eap_run_rna_bam_to_bigwigs'
        self.toolBegins(toolName)
        self.writeVersions()
    
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
