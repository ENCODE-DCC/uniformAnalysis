#!/usr/bin/env python2.7
# bwaAlignmentStep.py module holds BwaAlignmentStep class which descends from LogicalStep class.
# It performs bwa alignment on single or paired end reads.
#
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'tagsRep'+replicate+'.fastq'
#         Paired: 'tagsRd1Rep'+replicate+'.fastq' and 'tagsRd2Rep'+replicate+'.fastq' 
#
# Outputs: a single bam target keyed as:
#          'alignmentRep'+replicate+'.bam'

from src.logicalStep import LogicalStep
from src.wrappers import samtools

class BwaAlignmentStep(LogicalStep):

    def __init__(self, analysis, replicate, encoding):
        self.replicate = str(replicate)
        self.encoding  = encoding
        LogicalStep.__init__(self, analysis, 'alignmentByBwa_' + analysis.readType + 'Rep' + \
                                                                                   self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all step versions

    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('bwa', self.getToolVersion('bwa'))
            raFile.add('samtools', self.getToolVersion('samtools'))
        else:
            self.getToolVersion('bwa')
            self.getToolVersion('samtools')
        
    def onRun(self):
        
        # Inputs:
        if self.ana.readType == 'single':
            input1 = self.ana.getFile('tagsRep' + self.replicate + '.fastq')
        elif self.ana.readType == 'paired':
            input1 = self.ana.getFile('tagsRd1Rep' + self.replicate + '.fastq')
            input2 = self.ana.getFile('tagsRd2Rep' + self.replicate + '.fastq')
             
        # Outputs:
        bam = self.declareTargetFile('alignmentRep' + self.replicate + '.bam')
        
        # Locate the correct reference file(s)
        #refFile = step.ana.getSetting(step.ana.genome +'AssemblyFile')
        genome = self.ana.genome
        refFile = self.ana.refDir + genome + "/bwaData/" + genome + ".fa"
        #gender = self.ana.gender
        #if gender == 'female' or gender == 'male':
        #    refFile = self.ana.refDir + gender + '.' + genome + "/bwaData/" + genome + ".fa"
        
        if self.encoding.lower().startswith('sanger'):
            if self.ana.readType == 'single':
                self.eap_se(refFile, input1, bam)
            elif self.ana.readType == 'paired':
                self.eap_pe(refFile, input1, input2, bam)
        elif self.encoding.lower().startswith('solexa'):
            if self.ana.readType == 'single':
                self.eap_slx_se(refFile, input1, bam)
            elif self.ana.readType == 'paired':
                self.eap_slx_pe(refFile, input1, input2, bam)
        else:
            self.fail("fastq encoding '" + self.encoding + "' is not supported.")
                
        samtools.index(self, bam)

    # As no other step should call star scripts, there is no need for a wrapper
    # and wrapped methods are here:
    
    def eap_se(self, refFile, fastq, outBam):
        '''Single end bam generation'''
        
        # Using bash scripts to run bwa single-end on sanger style fastq
        # usage v3: eap_run_bwa_se bwa-index reads.fq out.bam
        cmd = "eap_run_bwa_se {ref} {fq} {output}".format( \
              ref=refFile, fq=fastq, output=outBam)
              
        toolName = 'eap_run_bwa_se'
        self.toolBegins(toolName)
        self.getToolVersion(toolName,logOut=True)
        self.getToolVersion('bwa',logOut=True)
        self.getToolVersion('samtools',logOut=True)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
    
    def eap_pe(self, refFile, fastq1, fastq2, outBam):
        '''Paired end bam generation'''
        
        # Using bash scripts to run bwa paired-end on sanger style fastqs
        # usage v4: eap_run_bwa_pe bwa-index read1.fq read2.fq out.bam
        cmd = "eap_run_bwa_pe {ref} {fq1} {fq2} {output}".format( \
              ref=refFile, fq1=fastq1, fq2=fastq2, output=outBam)
              
        toolName = 'eap_run_bwa_pe'
        self.toolBegins(toolName)
        self.getToolVersion(toolName,logOut=True)
        self.getToolVersion('bwa',logOut=True)
        self.getToolVersion('samtools',logOut=True)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
    
    def eap_slx_se(self, refFile, solexaFq, outBam):
        '''Single end bam generation'''
        
        # Using bash scripts to run bwa single-end on solexa style fastq
        # usage v1: eap_run_slx_bwa_se bwa-index solexa-reads.fq out.bam
        cmd = "eap_run_slx_bwa_se {ref} {fq} {output}".format( \
              ref=refFile, fq=solexaFq, output=outBam)
              
        toolName = 'eap_run_slx_bwa_se'
        self.toolBegins(toolName)
        self.getToolVersion(toolName,logOut=True)
        self.getToolVersion('bwa',logOut=True)
        self.getToolVersion('samtools',logOut=True)
        self.getToolVersion('edwSolexaToSangerFastq',logOut=True)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
    
    def eap_slx_pe(self, refFile, solexaFq1, solexaFq2, outBam):
        '''Paired end bam generation'''
        
        # Using bash scripts to run bwa paired-end on solexa style fastqs
        # usage v3: eap_run_slx_bwa_pe bwa-index solexa1.fq solexa2.fq out.bam
        cmd = "eap_run_slx_bwa_pe {ref} {fq1} {fq2} {output}".format( \
              ref=refFile, fq1=solexaFq1, fq2=solexaFq2, output=outBam)
              
        toolName = 'eap_run_slx_bwa_pe'
        self.toolBegins(toolName)
        self.getToolVersion(toolName,logOut=True)
        self.getToolVersion('bwa',logOut=True)
        self.getToolVersion('samtools',logOut=True)
        self.getToolVersion('edwSolexaToSangerFastq',logOut=True)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
