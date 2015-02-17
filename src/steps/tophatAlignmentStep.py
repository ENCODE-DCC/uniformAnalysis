#!/usr/bin/env python2.7
# tophatAlignmentStep.py module holds TophatAlignmentStep class which descends from LogicalStep.
# It performs tophat alignment on single or paired end reads.
#
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'tagsRep'+replicate+'.fastq'
#         Paired: 'tagsRd1Rep'+replicate+'.fastq' and 'tagsRd2Rep'+replicate+'.fastq' 
# Outputs: a single bam target keyed as: 'alignmentTophatRep'+replicate+'.bam'

from src.logicalStep import LogicalStep

class TophatAlignmentStep(LogicalStep):

    def __init__(self, analysis, replicate='1', libId='', encoding='sanger', tagLen=100):
        self.replicate = str(replicate)
        self.encoding  = encoding
        self.libId     = libId
        self.tagLen    = int(tagLen)
        LogicalStep.__init__(self, analysis, 'alignmentByTophat_' + analysis.readType + 'Rep' + \
                                                                                   self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all step versions

    def writeVersions(self,raFile=None,allLevels=False,scriptName=None):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            if scriptName  != None:
                raFile.add(scriptName, self.getToolVersion(scriptName))
            raFile.add('tophat', self.getToolVersion('tophat'))
            raFile.add('bowtie2', self.getToolVersion('bowtie2'))
            raFile.add('samtools', self.getToolVersion('samtools'))
            raFile.add('tophat_bam_xsA_tag_fix.pl', self.getToolVersion('tophat_bam_xsA_tag_fix.pl'))
        else:
            if scriptName != None:
                self.getToolVersion(scriptName)
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
        # All TopHat results use [male|female] genome index AND 
        #                        annotation indexes with tRNAs and ERCC spike-ins
        genome = self.ana.genome
        refPrefix = self.ana.refDir + genome + "/tophatData/"
        if self.ana.gender == 'female':  # male and unspecified are treated the same
            refPrefix = self.ana.refDir + self.ana.gender + '.' + genome + "/tophatData/"
        annoPrefix = refPrefix + "annotation"
        refPrefix += "genome"

        if self.ana.type == 'RNAseq-long':
            if self.ana.readType == 'single':
                self.eap_long_se(refPrefix, annoPrefix, self.libId, input1, bam)
            elif self.ana.readType == 'paired':
                self.eap_long_pe(refPrefix, annoPrefix, self.libId, input1, input2, bam)
        else:
                self.fail("Alignment by Tophat for '"+self.ana.type+"' is currently not supported.")

    def eap_long_pe(self, refPrefix, annoPrefix, libId, fastq1, fastq2, outBam):
        '''Paired end bam generation'''
        
        cmd = "eap_run_tophat_long_pe {ref} {anno} {lib} {fq1} {fq2} {output}".format( \
              ref=refPrefix, anno=annoPrefix, lib=libId, fq1=fastq1, fq2=fastq2, output=outBam)
              
        toolName = 'eap_run_tophat_long_pe'
        self.toolBegins(toolName)
        self.writeVersions(scriptName=toolName)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)

    def eap_long_se(self, refPrefix, annoPrefix, libId, fastq, outBam):
        '''Single end bam generation'''
        
        cmd = "eap_run_tophat_long_se {ref} {anno} {lib} {fq} {output}".format( \
              ref=refPrefix, anno=annoPrefix, lib=libId, fq=fastq, output=outBam)
              
        toolName = 'eap_run_tophat_long_se'
        self.toolBegins(toolName)
        self.writeVersions(scriptName=toolName)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
