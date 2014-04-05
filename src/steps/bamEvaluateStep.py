#!/usr/bin/env python2.7
# bamEvaluateStep.py module holds BamEvaluateStep class which descends from LogicalStep class.
# It takes a sample of a bam and characterizes the library complexity
#
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'alignmentRep' + replicate + '.bam'
# Outputs: 1 interim bam sample file, keyed as: 'alignmentRep'  + replicate + '_5M.bam'
#          1 interim Corr       file, keyed as: 'strandCorrRep' + replicate +    '.txt'
#          1 target json        file, keyed as: 'bamEvaluateRep' + replicate +   '.json'

import os
from src.logicalStep import LogicalStep
from src.settings import Settings
from src.wrappers import samtools, bedtools, phantomTools, ucscUtils

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
            raFile.add('phantomTools', phantomTools.version(self))
            raFile.add('ucscUtils', ucscUtils.version(self))
        else:
            samtools.version(self)
            bedtools.version(self)
            phantomTools.version(self)
            ucscUtils.version(self)

    def onRun(self):
        # Inputs:
        bam = self.ana.getFile('alignmentRep' + self.replicate + '.bam')
        
        # Outputs:
        strandCorr = self.declareInterimFile('strandCorrRep'+ self.replicate + '.txt')
        bamSample  = self.declareInterimFile('alignmentRep' + self.replicate + '_5M.bam')

        # Read bam header to see if aligner can be determined
        bamHeader  = self.declareGarbageFile('bamHeader.txt')
        samtools.header(self,bam,bamHeader)
        pg = self.ana.getCmdOut("grep \@PG "+bamHeader,logCmd=False,errOk=True)
        if pg.find('STAR') != -1:
            self.json['alignedBy'] = 'STAR'
        elif pg.lower().find('tophat') != -1:
            self.json['alignedBy'] = 'Tophat'
        elif pg.find('BEDTools_bedToBam') != -1:
            self.json['alignedBy'] = 'bwa'
        else:
            self.json['alignedBy'] = 'unknown'

        # Do UCSCs bam stats
        statsRa  = self.declareGarbageFile('stats.ra')
        tagAlignSample  = self.declareGarbageFile('sample.tagAlign')
        ucscUtils.edwBamStats(self, bam, statsRa, tagAlignSample, self.sampleSize)
        
        # json summary of stats:
        if not self.ana.dryRun:
            stats = Settings(statsRa)
            if stats.getBoolean('isPaired'):
                self.ana.readType = "paired"
                self.json['isPaired'] = True 
            else:
                self.ana.readType = "single"
                self.json['isPaired'] = False 
            self.json['isSortedByTarget' ] = stats.getBoolean('isSortedByTarget' )
            self.json['readCount'        ] = long( stats.get( 'readCount'        ))
            self.json['readBaseCount'    ] = long( stats.get( 'readBaseCount'    ))
            self.json['mappedCount'      ] = long( stats.get( 'mappedCount'      ))
            self.json['uniqueMappedCount'] = long( stats.get( 'uniqueMappedCount'))
            self.json['readSizeMean'     ] = int(  stats.get( 'readSizeMean'     ))
            self.json['readSizeStd'      ] = int(  stats.get( 'readSizeStd'      ))
            self.json['readSizeMin'      ] = int(  stats.get( 'readSizeMin'      ))
            self.json['readSizeMax'      ] = int(  stats.get( 'readSizeMax'      ))
            self.json['u4mReadCount'     ] = long( stats.get( 'u4mReadCount'     ))
            self.json['u4mUniquePos'     ] = long( stats.get( 'u4mUniquePos'     ))
            self.json['u4mUniqueRatio'   ] = float(stats.get( 'u4mUniqueRatio'   ))
            self.json['targetSeqCount'   ] = int(  stats.get( 'targetSeqCount'   ))
            self.json['targetBaseCount'  ] = long( stats.get( 'targetBaseCount'  ))
        else:
            self.ana.readType = "single"
            self.json['isPaired'         ] = False
            self.json['isSortedByTarget' ] = True
            self.json['readCount'        ] = 0
            self.json['readBaseCount'    ] = 0
            self.json['mappedCount'      ] = 0
            self.json['uniqueMappedCount'] = 0
            self.json['readSizeMean'     ] = 50
            self.json['readSizeStd'      ] = 0
            self.json['readSizeMin'      ] = 0
            self.json['readSizeMax'      ] = 0
            self.json['u4mReadCount'     ] = 0
            self.json['u4mUniquePos'     ] = 0
            self.json['u4mUniqueRatio'   ] = 0
            self.json['targetSeqCount'   ] = 0
            self.json['targetBaseCount'  ] = 0
        
        # Strand correlation 
        phantomTools.strandCorr(self,tagAlignSample,strandCorr)
        
        if stats.getBoolean('isSortedByTarget' ):
            bedtools.bedToBam(self,tagAlignSample,bamSample)
        else:
            bamUnsorted  = self.declareGarbageFile('sampleUnsorted.bam')
            bedtools.bedToBam(self,tagAlignSample,bamUnsorted)
            samtools.sort(self,bamUnsorted,bamSample)
        
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
            
        self.createAndWriteJsonFile( 'bamEvaluateRep'+ self.replicate, target=True )
