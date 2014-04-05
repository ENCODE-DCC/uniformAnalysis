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

    def __init__(self, analysis, replicate, spikeIn='ERCC', encoding='sanger', tagLen=101):
        self.replicate = str(replicate)
        self.encoding  = encoding
        self.spikeIn   = spikeIn
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
        else:
            self.getToolVersion('tophat')
            self.getToolVersion('bowtie2')
            self.getToolVersion('samtools')
        
    def onRun(self):
        
        # Inputs:
        if self.ana.readType == 'single':
            input1 = self.ana.getFile('tagsRep' + self.replicate + '.fastq')
        elif self.ana.readType == 'paired':
            input1 = self.ana.getFile('tagsRd1Rep' + self.replicate + '.fastq')
            input2 = self.ana.getFile('tagsRd2Rep' + self.replicate + '.fastq')
             
        # Outputs:
        bam = self.declareTargetFile('alignmentTophatRep' + self.replicate + '.bam')
        
        # TODO: Distinguish between long and short RNA
        # TODO: Distinguish between ERCC and Wold
        # TODO Use tagLen to determine which genomeDir (--sjdbOverhang 100).  Currently all 100.
        # TODO Use tagLen to determine short RNA-seq.
        # TODO: support solexa?
        
        # Locate the correct reference file(s)
        genome = self.ana.genome
        refDir = self.ana.refDir + genome + "/tophatData/"
        if self.ana.gender == 'female':  # male and unspecified are treated the same
            refDir = self.ana.refDir + self.ana.gender + '.' + genome + "/tophatData/"
            
        if self.ana.type == 'RNAseq-long':
            if self.encoding.lower().startswith('sanger'):
                if self.ana.readType == 'single':
                    self.eap_long_se(refDir, self.spikeIn, input1, bam)
                elif self.ana.readType == 'paired':
                    self.eap_long_pe(refDir, self.spikeIn, input1, input2, bam)
            else:
                self.fail("fastq encoding '" + self.encoding + "' is not supported.")
        else:
                self.fail("Alignment by Tophat for '"+self.ana.type+"' is currently not supported.")
                
        samtools.index(self, bam)

    def eap_long_se(self, refDir, spikeIn, fastq, outBam):
        '''Single end bam generation'''
        
        cmd = "eap_run_tophat_long_se {ref} {spike} {fq} {output}".format( \
              ref=refDir, spike=spikeIn, fq=fastq, output=outBam)
              
        toolName = 'eap_run_tophat_long_se'
        self.toolBegins(toolName)
        self.getToolVersion(toolName)
        self.getToolVersion('tophat')
        self.getToolVersion('bowtie2')
        self.getToolVersion('samtools')
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)

    def eap_long_pe(self, refDir, spikeIn, fastq1, fastq2, outBam):
        '''Paired end bam generation'''
        
        cmd = "eap_run_tophat_long_pe {ref} {spike} {fq1} {fq2} {output}".format( \
              ref=refDir, spike=spikeIn, fq1=fastq1, fq2=fastq2, output=outBam)
              
        toolName = 'eap_run_tophat_long_pe'
        self.toolBegins(toolName)
        self.getToolVersion(toolName)
        self.getToolVersion('tophat')
        self.getToolVersion('bowtie2')
        self.getToolVersion('samtools')
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
