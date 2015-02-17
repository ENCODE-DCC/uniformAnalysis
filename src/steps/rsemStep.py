#!/usr/bin/env python2.7
# tophatAlignmentStep.py module holds TophatAlignmentStep class which descends from LogicalStep.
# It performs tophat alignment on single or paired end reads.
#
# Inputs: 1 Annotation alignment bam             keyed: 'annotation'              + suffix + '.bam'
# Outputs: 1 target Gene       results tab file, keyed: 'quantifyGenesRsem'       + suffix + '.tab'
#          1 target Transcript results tab file, keyed: 'quantifyTranscriptsRsem' + suffix + '.tab'

from src.logicalStep import LogicalStep

class RsemStep(LogicalStep):

    def __init__(self, analysis, suffix=""):
        self.suffix    = str(suffix)
        LogicalStep.__init__(self, analysis, 'quantitateRsem_' + analysis.readType + '_' + suffix)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all step versions

    def writeVersions(self,raFile=None,allLevels=False,scriptName=None):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            if scriptName != None:
                raFile.add(scriptName, self.getToolVersion(scriptName))
            raFile.add('rsem', self.getToolVersion('rsem-calculate-expression'))
            raFile.add('bowtie2', self.getToolVersion('bowtie2'))
            raFile.add('samtools', self.getToolVersion('samtools'))
        else:
            if scriptName != None:
                self.getToolVersion(scriptName)
            self.getToolVersion('rsem-calculate-expression')
            self.getToolVersion('bowtie2')
            self.getToolVersion('samtools')
        
    def onRun(self):
        
        # Inputs:
        annoBam = self.ana.getFile('annotation' + self.suffix + '.bam')
             
        # Outputs:
        genesFile = self.declareTargetFile('quantifyGenesRsem'       + self.suffix + '.tab')
        transFile = self.declareTargetFile('quantifyTranscriptsRsem' + self.suffix + '.tab')
        
        # Locate the correct reference file(s)
        # All RSEM results use male genome/annotation index with tRNAs and ERCC spike-ins
        genome = self.ana.genome
        refDir = self.ana.refDir + genome + "/rsemData/rsemIndex"
            
        if self.ana.type == 'RNAseq-long':
            if self.ana.readType == 'single':
                self.eap_long_se(refDir, annoBam, genesFile, transFile)
            elif self.ana.readType == 'paired':
                self.eap_long_pe(refDir, annoBam, genesFile, transFile)
        else:
            self.fail("Quantification by RSEM for '"+self.ana.type+"' is currently not supported.")

    def eap_long_pe(self, refDir, inAnnoBam, outGene, outTrans):
        '''RSEM quantification for paired-end datasets'''
        
        cmd = "eap_run_rsem_long_pe {ref} {annoBamIn} {geneOut} {transOut}".format( \
              ref=refDir, annoBamIn=inAnnoBam, geneOut=outGene, transOut=outTrans,)
              
        toolName = 'eap_run_rsem_long_pe'
        self.toolBegins(toolName)
        self.writeVersions(scriptName=toolName)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)

    def eap_long_se(self, refDir, inAnnoBam, outGene, outTrans):
        '''RSEM quantification for single-end datasets'''
        
        cmd = "eap_run_rsem_long_se {ref} {annoBamIn} {geneOut} {transOut}".format( \
              ref=refDir, annoBamIn=inAnnoBam, geneOut=outGene, transOut=outTrans)
              
        toolName = 'eap_run_rsem_long_se'
        self.toolBegins(toolName)
        self.writeVersions(scriptName=toolName)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
