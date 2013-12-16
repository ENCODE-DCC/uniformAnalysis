#!/usr/bin/env python2.7
# bamValidateE3.py ENCODE3 galaxy pipeline script for validating bam files

#  Usage: python(2.7) bamValidateE3,py <galaxyRootDir> <userId> <encode3SettingsFile> \
#                                      <'paired'|'unpaired'> <inputBam> <sampleSize> \
#                                      <galaxyOutSampleBam> <galaxyOutHistoMetrics> \
#                                      <galaxyOutStrandCorr> <repNo> <named>

import os, sys
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.bamEvaluateStep import BamEvaluateStep

###############
testOnly = False
#python bamValidateE3.py /hive/users/tdreszer/galaxy/galaxy-dist 47 \
#                 /hive/users/tdreszer/galaxy/uniformAnalysis/test/settingsE3.txt unpaired \
#                 /hive/users/tdreszer/galaxy/data/dnase/UwDnaseAg04449RawDataRep1.bam 5000000 \
#                 /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_293.dat \
#                 /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_294.dat \
#                 /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_295.dat 1 test
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        BamEvaluateStep(ana,'1','5000000').writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)
     
galaxyPath = sys.argv[1]
userId = sys.argv[2]
settingsFile = sys.argv[3]
singlePaired = sys.argv[4]
galaxyInputFile = sys.argv[5]
sampleSize = int( sys.argv[6] )
galaxyOutSampleBam = sys.argv[7]
galaxyOutMetric = sys.argv[8]
galaxyOutStrandCorr = sys.argv[9]
repNo = sys.argv[10]
anaId = 'U' + userId
if len( sys.argv ) > 11:
    anaId = sys.argv[11] + anaId

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, 'hg19')
ana.dryRun(testOnly)
ana.readType = singlePaired

# What step expects:
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'alignmentRep' + replicate + '.bam'
# Outputs: 1 target bam sample file, keyed as: 'alignmentRep'  + replicate + '_5M.bam'
#          1 target histogram  file, keyed as: 'metricRep'     + replicate +    '.txt'
#          1 target Corr       file, keyed as: 'strandCorrRep' + replicate +    '.txt'
    
# set up keys that join inputs through various file forwardings:
bamInputKey   = 'alignmentRep'  + repNo +    '.bam'
bamSampleKey  = 'alignmentRep'  + repNo + '_5M.bam'
metricKey     = 'metricRep'     + repNo +    '.txt'
strandCorrKey = 'strandCorrRep' + repNo +    '.txt'

# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(bamInputKey,'galaxyInput', galaxyInputFile)
nonGalaxyInput  = ana.nonGalaxyInput(bamInputKey)  # Registers and returns the outside location

# outputs:
ana.registerFile( metricKey,       'galaxyOutput',galaxyOutMetric)
resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
ana.createOutFile(metricKey,    'nonGalaxyOutput','%s_metricHist',ext='txt')
ana.registerFile( strandCorrKey,   'galaxyOutput',galaxyOutStrandCorr)
ana.createOutFile(strandCorrKey,'nonGalaxyOutput','%s_strandCorr',ext='txt')
ana.registerFile(bamSampleKey,     'galaxyOutput',galaxyOutSampleBam)
ana.createOutFile(bamSampleKey, 'nonGalaxyOutput','%s_sample',ext='bam' )

# Establish step and run it:
step = BamEvaluateStep(ana,repNo,sampleSize=sampleSize)
step.run()

