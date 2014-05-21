#!/usr/bin/env python2.7
# bamEvaluateStep.py module holds BamEvaluateStep class which descends from LogicalStep class.
# It takes a sample of a bam and characterizes the library complexity
#
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'alignmentRep' + replicate + '.bam'
# Outputs: 1 interim Corr       file, keyed as: 'strandCorr' + suffix +    '.txt'
#          1 target json        file, keyed as: 'bamEvaluate' + suffix +   '.json'

from src.logicalStep import LogicalStep
from src.settings import Settings

class BamEvaluateStep(LogicalStep):

    def __init__(self, analysis, replicate="1", suffix=""):
        self.replicate = str(replicate)
        self.suffix = suffix
        LogicalStep.__init__(self, analysis, 'bamEvaluate' + self.suffix)
        
    def writeVersions(self,raFile=None,allLevels=False,scriptName=None):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            if scriptName != None:
                raFile.add(scriptName, self.getToolVersion(scriptName))
            raFile.add('edwBamStats', self.getToolVersion('edwBamStats'))
            raFile.add('samtools', self.getToolVersion('samtools'))
            raFile.add('Rscript', self.getToolVersion('Rscript'))
            raFile.add('run_spp.R', self.getToolVersion(self.ana.toolsDir+'run_spp.R'))
        else:
            if scriptName != None:
                self.getToolVersion(scriptName)
            self.getToolVersion('edwBamStats')
            self.getToolVersion('samtools')
            self.getToolVersion('Rscript')
            self.getToolVersion(self.ana.toolsDir+'run_spp.R')

    def onRun(self):
        # Inputs:
        bam = self.ana.getFile('alignmentRep' + self.replicate + '.bam')
        
        # Outputs:
        strandCorr = self.declareInterimFile('strandCorr'+ self.suffix + '.txt')
        bamSample  = self.declareGarbageFile('alignment' + self.suffix + '_5M.bam')

        # Run the val script
        statsRa  = self.declareGarbageFile('stats.ra')
        if self.ana.type == 'DNase':
            tagLen = 36 # 100? TODO find this info from somewhere
            spotsRa  = self.declareGarbageFile('spots.ra')
            self.eap_dnase_stats(bam,self.ana.genome,tagLen,statsRa,strandCorr,spotsRa)
        else:
            self.eap_eval_bam(bam,bamSample,statsRa,strandCorr)
        
        
        # json summary of stats:
        if not self.ana.dryRun:
            stats = Settings(statsRa)
            for key in stats.keys():   # sorted( stats.keys() )
                if key == 'isPaired':
                    self.json[key] = stats.getBoolean(key) 
                    if stats.getBoolean(key):
                        self.ana.readType = "paired"
                    else:
                        self.ana.readType = "single"
                elif key == 'isSortedByTarget':
                    self.json[key] = stats.getBoolean(key) 
                elif key == 'readCount' or key == 'readBaseCount' or key == 'mappedCount' \
                  or key == 'uniqueMappedCount' or key == 'u4mReadCount' or key == 'u4mUniquePos' \
                  or key == 'targetBaseCount':
                    self.json[key] = long(stats.get(key))
                elif key == 'readSizeMean' or key == 'readSizeStd' or key == 'readSizeMin' \
                  or key == 'readSizeMax' or key == 'targetSeqCount':
                    self.json[key] = int(stats.get(key))
                elif key == 'u4mUniqueRatio':
                    self.json[key] = float(stats.get(key))
                else:
                    self.json[key] = stats.get(key)
        else:
            self.ana.readType = "single"
            self.json['alignedBy'        ] = 'unknown'
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
            
        if self.ana.type == 'DNase':
            self.json['hotspots'] = {}
            if not self.ana.dryRun:
                spots = Settings(spotsRa)
                for key in spots.keys():   # sorted( stats.keys() )
                    if key == 'spotRatio' or key == 'enrichment' or key == 'maxEnrichment' \
                    or key == 'sumSignal' or key == 'spotSumSignal':
                        self.json['hotspots'][key] = float(spots.get(key))
                    elif key == 'basesInGenome' or key == 'basesInSpots' \
                      or key == 'basesInSpotsWithSignal':
                        self.json['hotspots'][key] = long(spots.get(key))
                    else:
                        self.json['hotspots'][key] = spots.get(key)
            else:
                self.json['hotspots']['spotRatio'] = 0.1
                self.json['hotspots']['enrichment']   = 0.2
                self.json['hotspots']['maxEnrichment']   = 0.3
                self.json['hotspots']['basesInGenome']     = 4
                self.json['hotspots']['basesInSpots']         = 5
                self.json['hotspots']['basesInSpotsWithSignal']  = 6
                self.json['hotspots']['sumSignal']              = '7.654321e+08'
                self.json['hotspots']['spotSumSignal']         = '8.765432e+08'
            
        self.createAndWriteJsonFile( 'bamEvaluate'+ self.suffix, target=True )
        
    def eap_eval_bam(self, inBam, outSampleBam, outStats, outStrandCorr):
        '''Evaluate bam file'''
    
        cmd = "eap_eval_bam {bamIn} {bamOut} {statsOut} {strandCorrOut}".format( \
              bamIn=inBam, bamOut=outSampleBam, statsOut=outStats, strandCorrOut=outStrandCorr)
          
        toolName = 'eap_eval_bam'
        self.toolBegins(toolName)
        self.writeVersions(scriptName=toolName)
    
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)

    def eap_dnase_stats(self, inBam, genome, tagLen, outBamStats, outStrandCorr, outSpots):
        '''Evaluate bam file for DNase experiments'''
    
        #eap_dnase_stats in.bam target readSize bamStats.ra sppStats.ra spotStats.ra
        cmd = "eap_dnase_stats {bamIn} {db} {readSize} {bamStatsOut} {sppOut} {spotsOut}".format( \
              bamIn=inBam, db=genome, readSize=tagLen, bamStatsOut=outBamStats, \
              sppOut=outStrandCorr, spotsOut=outSpots)
          
        toolName = 'eap_dnase_stats'
        self.toolBegins(toolName)
        self.writeVersions(scriptName=toolName)
    
        self.err = self.ana.runCmd(cmd, log=self.log)
        self.toolEnds(toolName,self.err)

