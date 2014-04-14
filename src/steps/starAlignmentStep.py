#!/usr/bin/env python2.7
# starAlignmentStep.py module holds StarAlignmentStep class which descends from LogicalStep class.
# It performs star alignment on single or paired end reads.
#
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'tagsRep'+replicate+'.fastq'
#         Paired: 'tagsRd1Rep'+replicate+'.fastq' and 'tagsRd2Rep'+replicate+'.fastq' 
# Outputs: a single bam target keyed as: 'alignmentStarRep'+replicate+'.bam'

from src.logicalStep import LogicalStep
from src.wrappers import samtools

class StarAlignmentStep(LogicalStep):

    def __init__(self, analysis, replicate='1', spikeIn='ERCC', libId='', \
                                                                encoding='sanger', tagLen=100):
        self.replicate = str(replicate)
        self.encoding  = encoding
        self.spikeIn   = spikeIn
        self.libId     = libId
        self.tagLen    = int(tagLen)
        LogicalStep.__init__(self, analysis, 'alignmentByStar_' + analysis.readType + 'Rep' + \
                                                                                   self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all step versions

    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('star', self.getToolVersion('STAR'))
            raFile.add('samtools', self.getToolVersion('samtools'))
        else:
            self.getToolVersion('STAR')
            self.getToolVersion('samtools')
        
    def onRun(self):
        
        # Inputs:
        if self.ana.readType == 'single':
            input1 = self.ana.getFile('tagsRep' + self.replicate + '.fastq')
        elif self.ana.readType == 'paired':
            input1 = self.ana.getFile('tagsRd1Rep' + self.replicate + '.fastq')
            input2 = self.ana.getFile('tagsRd2Rep' + self.replicate + '.fastq')
             
        # Outputs:
        bam = self.declareTargetFile('alignmentStarRep' + self.replicate + '.bam')
        
        # Locate the correct reference file(s)
        genome = self.ana.genome
        refDir = self.ana.refDir + genome + "/starData/" 
        if self.ana.gender == 'female':  # male and unspecified are treated the same
            refDir = self.ana.refDir + self.ana.gender + '.' + genome + "/starData/"
        refDir += self.spikeIn  # doesn't end in '/' on purpose.
        
        if self.ana.type == 'RNAseq-long':
            if self.encoding.lower().startswith('sanger'):
                if self.ana.readType == 'single':
                    self.eap_long_se(refDir, self.libId, input1, bam)
                elif self.ana.readType == 'paired':
                    self.eap_long_pe(refDir, self.libId, input1, input2, bam)
            else:
                self.fail("fastq encoding '" + self.encoding + "' is not supported.")
        else:
                self.fail("Alignment by STAR for '"+self.ana.type+"' is currently not supported.")
                
        samtools.index(self, bam)

    def eap_long_se(self, refDir, libId, fastq, outBam):
        '''Single end bam generation'''
        
        cmd = "eap_run_star_long_se {ref} {lib} {fq} {output}".format( \
              ref=refDir, lib=libId, fq=fastq, output=outBam)
              
        toolName = 'eap_run_star_long_se'
        self.toolBegins(toolName)
        self.getToolVersion(toolName,logOut=True)
        self.getToolVersion('STAR',logOut=True)
        self.getToolVersion('samtools',logOut=True)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)

    def eap_long_pe(self, refDir, libId, fastq1, fastq2, outBam):
        '''Paired end bam generation'''
        
        cmd = "eap_run_star_long_pe {ref} {lib} {fq1} {fq2} {output}".format( \
              ref=refDir, lib=libId, fq1=fastq1, fq2=fastq2, output=outBam)
              
        toolName = 'eap_run_star_long_pe'
        self.toolBegins(toolName)
        self.getToolVersion(toolName,logOut=True)
        self.getToolVersion('STAR',logOut=True)
        self.getToolVersion('samtools',logOut=True)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
