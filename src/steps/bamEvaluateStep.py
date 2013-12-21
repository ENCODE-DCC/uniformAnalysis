#!/usr/bin/env python2.7
# bamEvaluateStep.py module holds BamEvaluateStep class which descends from LogicalStep class.
# It takes a sample of a bam and characterizes the library completity
#
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'alignmentRep' + replicate + '.bam'
#
# Outputs: 1 target bam sample file, keyed as: 'alignmentRep'  + replicate + '_5M.bam'
#          1 target histogram  file, keyed as: 'metricRep'     + replicate +    '.txt'
#          1 target Corr       file, keyed as: 'strandCorrRep' + replicate +    '.txt'
#          1 interim json      file, keyed as: 'bamEvaluateRep' + replicate +  '.json'

import os
from src.logicalStep import LogicalStep
from src.wrappers import samtools, bedtools, picardTools, census, phantomTools

class BamEvaluateStep(LogicalStep):

    def __init__(self, analysis, replicate, sampleSize):
        self.replicate = str(replicate)
        self.sampleSize = sampleSize
        LogicalStep.__init__(self, analysis, 'bamEvaluateRep' + self.replicate)
        
    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('samtools', samtools.version(self))
            raFile.add('bedtools', bedtools.version(self))
            raFile.add('picardTools', picardTools.version(self))
            raFile.add('census', census.version(self))
            raFile.add('phantomTools', phantomTools.version(self))
        else:
            samtools.version(self)
            bedtools.version(self)
            picardTools.version(self)
            census.version(self)
            phantomTools.version(self)

    def onRun(self):      
        # Inputs:
        bam = self.ana.getFile('alignmentRep' + self.replicate + '.bam')
        
        # Outputs:
        metricHist = self.declareTargetFile( 'metricRep'    + self.replicate + '.txt')
        strandCorr = self.declareTargetFile( 'strandCorrRep'+ self.replicate + '.txt')
        fragSizeTxt = self.declareTargetFile( 'fragSize'+ self.replicate + '.txt')
        fragSizePdf = self.declareTargetFile( 'fragSize'+ self.replicate + '.pdf')
        bamSample  = self.declareInterimFile('alignmentRep' + self.replicate + '_5M.bam')
        
        bamSize = samtools.bamSize(self,bam)
         
        if self.sampleSize < bamSize:
            bamUnsorted  = self.declareGarbageFile('bamUnsortedSample.bam')
            picardTools.downSample(self,(self.sampleSize/float(bamSize)),bam,bamUnsorted)
        else:
            bamUnsorted = bam
            
        picardTools.sortBam(self, bamUnsorted, bamSample)
        census.metrics(self, bamSample, metricHist)

        self.json['redundancy'] = {}
        if not self.ana.dryRun:
            with open(metricHist, 'r') as metricsFile:
                lines = metricsFile.readlines()
                self.json['redundancy']['uniqueReads'] = lines[4].split(':')[-1].split()[0]
                self.json['redundancy']['totalReads'] = lines[3].split()[-1]
        else:
            self.json['redundancy']['uniqueReads'] = 0
            self.json['redundancy']['totalReads'] = 0
        
        phantomTools.strandCorr(self,bamSample,strandCorr)
        
        self.json['strandCorrelation'] = {}
        if not self.ana.dryRun:
            with open(strandCorr, 'r') as strandFile:
                for line in strandFile:
                    splits = line.split('\t')
                    self.json['strandCorrelation']['Frag'] = splits[2]
                    self.json['strandCorrelation']['RSC'] = splits[8]
                    self.json['strandCorrelation']['NSC'] = splits[9]
        else:
            self.json['strandCorrelation']['Frag'] = 0
            self.json['strandCorrelation']['RSC'] = 0
            self.json['strandCorrelation']['NSC'] = 0
        self.createAndWriteJsonFile()

        picardTools.fragmentSize(self, bamSample, fragSizeTxt, fragSizePdf)
        
        
