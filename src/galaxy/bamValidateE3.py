#!/usr/bin/env python2.7
# bamValidateE3.py ENCODE3 galaxy pipeline script for validating bam files
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#  Usage: python(2.7) bamValidateE3,py <userId> <'paired'|'unpaired'> <inputBam> \
#                                      <galaxyOutSampleBam> <galaxyOutHistoMetrics> \
#                                      <galaxyOutStrandCorr> <repNo> <analysisId>

import os, sys
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.bamEvaluateStep import BamEvaluateStep

###############
testOnly = False
#python bamValidateE3.py /hive/users/tdreszer/galaxy/data/dnase/UwDnaseAg04449RawDataRep1.bam \
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
     
singlePaired        = sys.argv[1]
galaxyInputFile     = sys.argv[2]
galaxyOutSampleBam  = sys.argv[3]
galaxyOutMetric     = sys.argv[4]
galaxyOutStrandCorr = sys.argv[5]
repNo               = sys.argv[6]
anaId               = sys.argv[7]

# No longer command line parameters:
scriptPath = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
galaxyPath = '/'.join(scriptPath.split('/')[ :-2 ])  
settingsFile = scriptPath + '/' + "settingsE3.txt"
sampleSize = 5000000

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, 'hg19')
if testOnly:
    ana.dryRun = testOnly
ana.readType = singlePaired

# What step expects:
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'alignmentRep' + replicate + '.bam'
# Outputs: 1 target bam sample file, keyed as: 'alignmentRep'  + replicate + '_5M.bam'
#          1 target histogram  file, keyed as: 'metricRep'     + replicate +    '.txt'
#          1 target Corr       file, keyed as: 'strandCorrRep' + replicate +    '.txt'
#          1 interim json      file, keyed as: 'bamEvaluateRep' + replicate +  '.json'
    
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
sys.exit( step.run() )

