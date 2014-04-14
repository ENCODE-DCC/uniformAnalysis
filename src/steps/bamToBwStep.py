#!/usr/bin/env python2.7
# bamToBwStep.py module holds BamToBwStep class which descends from LogicalStep class.
# It takes a bam input and generates bigWig signal.
#
# Inputs: 1 bam, pre-registered in analysis, keyed as: 'alignment' + suffix + '.bam'
# Outputs: target signal file, keyed as: 'signal + suffix + readFiler + strand + '.bw'

import os
from src.logicalStep import LogicalStep
from src.wrappers import samtools

class BamToBwStep(LogicalStep):

    def __init__(self, analysis, suffix="", readFilter='all', strand='Plus'):
        self.suffix = str(suffix)
        self.readFilter = readFilter
        self.strand     = strand
        LogicalStep.__init__(self, analysis, 'bamToBws_' + \
                                                    readFilter.lower() + strand + '_' + suffix)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions

    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        script = 'eap_run_bam_to_bw_' + self.readFilter.lower() + '_' + self.strand.lower()
        if raFile != None:
            raFile.add(script, self.getToolVersion(script))
            self.getToolVersion('samtools')
            raFile.add('makewigglefromBAM-NH.py', \
                       self.getToolVersion('makewigglefromBAM-NH.py'))
            raFile.add('python2.7',   self.getToolVersion('python2.7'))
            raFile.add('wigToBigWig',  self.getToolVersion('wigToBigWig'))
            #raFile.add('perl', self.getToolVersion('perl'))
        else:
            self.getToolVersion(script)
            self.getToolVersion('samtools')
            self.getToolVersion('makewigglefromBAM-NH.py')
            self.getToolVersion('python2.7')
            self.getToolVersion('wigToBigWig')
            #self.getToolVersion('perl')

    def onRun(self):
        # Inputs:
        bam = self.ana.getFile('alignment' + self.suffix + '.bam')
        
        # Outputs:
        outBw  = self.declareTargetFile('signal'+self.suffix+self.readFilter+self.strand+'.bw')

        # if bam is unindexed, create an index.
        #bai = bam + '.bai'
        #if not os.path.exists(bai):
        #    samtools.index(self, bam)

        # male will be fine.
        chromFile = self.ana.refDir + "male." +self.ana.genome + "/chrom.sizes"
        if self.ana.gender == 'female':  # male and unspecified are treated the same
            chromFile = self.ana.refDir + self.ana.gender + '.' + self.ana.genome + "/chrom.sizes"

        # Since eap_run scripts are not supposed to have if statements, there are 4 versions
        # of the same thing and the ifs are here.
        script = 'eap_run_bam_to_bw'
        readFilter = self.readFilter.lower()
        if readFilter == 'uniq' or readFilter == 'all':
            script += '_' + readFilter 
        else:
            raise Exception("Read filter may only be 'All' or 'Uniq'.")
        strand = self.strand.lower()
        if strand == 'plus' or strand == 'minus':
            script += '_' + strand 
        else:
            raise Exception("Strand may only be 'Plus' or 'Minus'.")
        
        # Run the script
        self.eap_bamToBw(script, bam, chromFile, outBw)
        
    def eap_bamToBw(self, script, inBam, chromFile, outBw):
        '''Hostspot peak calling'''
        
        toolName = script
        cmd = "{tool} {bam} {chroms} {bwOut}".format( \
              tool=toolName, bam=inBam, chroms=chromFile, bwOut=outBw)
            
        self.toolBegins(toolName)
        self.getToolVersion(toolName)
        self.getToolVersion('samtools')
        self.getToolVersion('makewigglefromBAM-NH.py')
        self.getToolVersion('python2.7')
        self.getToolVersion('wigToBigWig')
        
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)
