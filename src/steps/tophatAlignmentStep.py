#!/usr/bin/env python2.7
# tophatAlignmentStep.py module holds TophatAlignmentStep class which descends from LogicalStep.
# It performs tophat alignment on single or paired end reads.
#
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'tagsRep'+replicate+'.fastq'
#         Paired: 'tagsRd1Rep'+replicate+'.fastq' and 'tagsRd2Rep'+replicate+'.fastq' 
# Outputs: a single bam target keyed as: 'alignmentTophatRep'+replicate+'.bam'

from src.logicalStep import LogicalStep
from src.wrappers import samtools

class TophatAlignmentStep(LogicalStep):

    def __init__(self, analysis, replicate='1', spikeIn='ERCC', libId='', \
                                                                encoding='sanger', tagLen=100):
        self.replicate = str(replicate)
        self.encoding  = encoding
        self.spikeIn   = spikeIn
        self.libId     = libId
        self.tagLen    = int(tagLen)
        LogicalStep.__init__(self, analysis, 'alignmentByTophat_' + analysis.readType + 'Rep' + \
                                                                                   self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all step versions

    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('tophat', self.getToolVersion('tophat'))
            raFile.add('bowtie2', self.getToolVersion('bowtie2'))
            raFile.add('samtools', self.getToolVersion('samtools'))
            raFile.add('tophat_bam_xsA_tag_fix.pl', self.getToolVersion('tophat_bam_xsA_tag_fix.pl'))
        else:
            self.getToolVersion('tophat')
            self.getToolVersion('bowtie2')
            self.getToolVersion('samtools')
            self.getToolVersion('tophat_bam_xsA_tag_fix.pl')
        
    def onRun(self):
        
        # Inputs:
        if self.ana.readType == 'single':
            input1 = self.ana.getFile('tagsRep' + self.replicate + '.fastq')
        elif self.ana.readType == 'paired':
            input1 = self.ana.getFile('tagsRd1Rep' + self.replicate + '.fastq')
            input2 = self.ana.getFile('tagsRd2Rep' + self.replicate + '.fastq')
             
        # Outputs:
        bam = self.declareTargetFile('alignmentTophatRep' + self.replicate + '.bam')
        
        # Locate the correct reference file(s)
        genome = self.ana.genome
        refDir = self.ana.refDir + genome + "/tophatData" # doesn't end in '/' on purpose.
        if self.ana.gender == 'female':  # male and unspecified are treated the same
            refDir = self.ana.refDir + self.ana.gender + '.' + genome + "/tophatData"
            
        if self.ana.type == 'RNAseq-long':
            if self.spikeIn == 'ERCC':
                if self.ana.readType == 'single':
                    self.eap_long_ercc_se(refDir, self.libId, input1, bam)
                elif self.ana.readType == 'paired':
                    self.eap_long_ercc_pe(refDir, self.libId, input1, input2, bam)
            elif self.spikeIn == 'WSC':
                if self.ana.readType == 'single':
                    self.eap_long_wsc_se(refDir, self.libId, input1, bam)
                elif self.ana.readType == 'paired':
                    self.eap_long_wsc_pe(refDir, self.libId, input1, input2, bam)
            else:
                self.fail("Alignment by Tophat, spike-in '"+self.spikeIn+ \
                          "' iscurrently not supported.")
        else:
                self.fail("Alignment by Tophat for '"+self.ana.type+"' is currently not supported.")
                
        samtools.index(self, bam)

    def eap_long_ercc_pe(self, refDir, libId, fastq1, fastq2, outBam):
        '''Paired end bam generation'''
        
        cmd = "eap_run_tophat_long_ercc_pe {ref} {lib} {fq1} {fq2} {output}".format( \
              ref=refDir, lib=libId, fq1=fastq1, fq2=fastq2, output=outBam)
              
        toolName = 'eap_run_tophat_long_ercc_pe'
        self.toolBegins(toolName)
        self.getToolVersion(toolName)
        self.getToolVersion('tophat')
        self.getToolVersion('bowtie2')
        self.getToolVersion('samtools')
        self.getToolVersion('tophat_bam_xsA_tag_fix.pl')
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)

    # This is probably never used in EAP.
    def eap_long_ercc_se(self, refDir, libId, fastq, outBam):
        '''Single end bam generation'''
        
        cmd = "eap_run_tophat_long_ercc_se {ref} {lib} {fq} {output}".format( \
              ref=refDir, lib=libId, fq=fastq, output=outBam)
              
        toolName = 'eap_run_tophat_long_ercc_se'
        self.toolBegins(toolName)
        self.getToolVersion(toolName)
        self.getToolVersion('tophat')
        self.getToolVersion('bowtie2')
        self.getToolVersion('samtools')
        self.getToolVersion('tophat_bam_xsA_tag_fix.pl')
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)

    def eap_long_wsc_pe(self, refDir, libId, fastq1, fastq2, outBam):
        '''Paired end bam generation'''
        
        cmd = "eap_run_tophat_long_wsc_pe {ref} {lib} {fq1} {fq2} {output}".format( \
              ref=refDir, lib=libId, fq1=fastq1, fq2=fastq2, output=outBam)
              
        toolName = 'eap_run_tophat_long_wsc_pe'
        self.toolBegins(toolName)
        self.getToolVersion(toolName)
        self.getToolVersion('tophat')
        self.getToolVersion('bowtie2')
        self.getToolVersion('samtools')
        self.getToolVersion('tophat_bam_xsA_tag_fix.pl')
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)

    def eap_long_wsc_se(self, refDir, libId, fastq, outBam):
        '''Single end bam generation'''
        
        cmd = "eap_run_tophat_long_wsc_se {ref} {lib} {fq} {output}".format( \
              ref=refDir, lib=libId, fq=fastq, output=outBam)
              
        toolName = 'eap_run_tophat_long_wsc_se'
        self.toolBegins(toolName)
        self.getToolVersion(toolName)
        self.getToolVersion('tophat')
        self.getToolVersion('bowtie2')
        self.getToolVersion('samtools')
        self.getToolVersion('tophat_bam_xsA_tag_fix.pl')
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
