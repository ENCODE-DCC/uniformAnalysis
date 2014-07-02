#!/usr/bin/env python2.7
# starAlignmentStep.py module holds StarAlignmentStep class which descends from LogicalStep class.
# It performs star alignment on single or paired end reads.
#
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'tagsRep'+replicate+'.fastq'
#         Paired: 'tagsRd1Rep'+replicate+'.fastq' and 'tagsRd2Rep'+replicate+'.fastq' 
# Outputs: target genome bam keyed as:          'genomeAlignedStarRep' + replicate + '.bam'
#          interim annotation bam keyed as: 'annotationAlignedStarRep' + replicate + '.bam'
#          and either 4 (paired/stranded) signal files:'signalStarRep' + replicate + 'UniqMinus.bw'
#                                                      'signalStarRep' + replicate +  'UniqPlus.bw'
#                                                      'signalStarRep' + replicate +  'AllMinus.bw'
#                                                      'signalStarRep' + replicate +   'AllPlus.bw'
#          or 2 (unpaired/unstranded) target signals:  'signalStarRep' + replicate +      'Uniq.bw'
#                                                      'signalStarRep' + replicate +       'All.bw'

from src.logicalStep import LogicalStep

class StarAlignmentStep(LogicalStep):

    def __init__(self, analysis, replicate='1', libId='', encoding='sanger', tagLen=100):
        self.replicate = str(replicate)
        self.encoding  = encoding
        self.libId     = libId
        self.tagLen    = int(tagLen)
        LogicalStep.__init__(self, analysis, 'alignmentByStar_' + analysis.readType + 'Rep' + \
                                                                                   self.replicate)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all step versions

    def writeVersions(self,raFile=None,allLevels=False,scriptName=None):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            if scriptName != None:
                raFile.add(scriptName, self.getToolVersion(scriptName))
            raFile.add('star', self.getToolVersion('STAR'))
            raFile.add('samtools', self.getToolVersion('samtools'))
        else:
            if scriptName != None:
                self.getToolVersion(scriptName)
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
        genoBam = self.declareTargetFile(     'genomeAlignedStarRep' + self.replicate + '.bam')
        annoBam = self.declareInterimFile('annotationAlignedStarRep' + self.replicate + '.bam')
        if self.ana.readType == 'single':
            uniqBw = self.declareTargetFile(      'signalStarRep' + self.replicate + 'Uniq.bw')
            allBw  = self.declareTargetFile(      'signalStarRep' + self.replicate + 'All.bw')
        elif self.ana.readType == 'paired':
            uniqMinusBw = self.declareTargetFile( 'signalStarRep' + self.replicate + 'UniqMinus.bw')
            uniqPlusBw  = self.declareTargetFile( 'signalStarRep' + self.replicate + 'UniqPlus.bw')
            allMinusBw  = self.declareTargetFile( 'signalStarRep' + self.replicate + 'AllMinus.bw')
            allPlusBw   = self.declareTargetFile( 'signalStarRep' + self.replicate + 'AllPlus.bw')
        
        # Locate the correct reference file(s)
        # All STAR results use [male|female] genome/annotation index with tRNAs and ERCC spike-ins
        genome = self.ana.genome
        refDir    = self.ana.refDir + genome + "/starData" 
        chromFile = self.ana.refDir + genome + "/chrom.sizes"
        if self.ana.gender == 'female':  # male and unspecified are treated the same
            refDir    = self.ana.refDir + self.ana.gender + '.' + genome + "/starData"
            chromFile = self.ana.refDir + self.ana.gender + '.' + genome + "/chrom.sizes"
        
        if self.ana.type == 'RNAseq-long':
            if self.ana.readType == 'single':
                self.eap_long_se(refDir, chromFile, self.libId, input1, genoBam, annoBam, \
                                 allBw, uniqBw)
            elif self.ana.readType == 'paired':
                self.eap_long_pe(refDir, chromFile, self.libId, input1, input2, genoBam, \
                                 annoBam, allMinusBw, allPlusBw, uniqMinusBw, uniqPlusBw)
        else:
                self.fail("Alignment by STAR for '"+self.ana.type+"' is currently not supported.")

    def eap_long_se(self, refDir, chromRef, libId, fastq, outGenoBam, outAnnoBam, outAllBw, outUniqBw):
        '''Single-end unstranded genome and transcriptome alignment by STAR'''
        
        cmd = "eap_run_star_long_se {ref} {chrRef} {lib} {fq} {genoBamOut} {annoBamOut} {allOut} {uniqOut}".format( \
              ref=refDir, chrRef=chromRef, lib=libId, fq=fastq, genoBamOut=outGenoBam, \
              annoBamOut=outAnnoBam, allOut=outAllBw, uniqOut=outUniqBw)
              
        toolName = 'eap_run_star_long_se'
        self.toolBegins(toolName)
        self.writeVersions(scriptName=toolName)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)

    def eap_long_pe(self, refDir, chromRef, libId, fastq1, fastq2, outGenoBam, outAnnoBam, \
                    outAllMinusBw, outAllPlusBw, outUniqMinusBw, outUniqPlusBw):
        '''Paired-end stranded genome and transcriptome alignment by STAR'''
        
        cmd = "eap_run_star_long_pe {ref} {chrRef} {lib} {fq1} {fq2} {genoBamOut} {annoBamOut} {allMinusOut} {allPlusOut} {uniqMinusOut} {uniqPlusOut}".format( \
              ref=refDir, chrRef=chromRef, lib=libId, fq1=fastq1, fq2=fastq2, \
              genoBamOut=outGenoBam, annoBamOut=outAnnoBam, \
              allMinusOut=outAllMinusBw, allPlusOut=outAllPlusBw, \
              uniqMinusOut=outUniqMinusBw, uniqPlusOut=outUniqPlusBw)
              
        toolName = 'eap_run_star_long_pe'
        self.toolBegins(toolName)
        self.writeVersions(scriptName=toolName)
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
