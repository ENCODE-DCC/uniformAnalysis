#!/usr/bin/env python2.7
# rnaBamToBwsE3.py ENCODE3 galaxy pipeline script for generating four alignment signals from a bam.
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#  Usage: python(2.7) rnaBamToBwsE3,py <inputBam> <bamEvalFile> <galaxyOutUniqPlus> \
#                                      <galaxyOutUniqMinus> <galaxyOutAllPlus> <galaxyOutAllMinus> \
#                                      <genome> <expType> <repNo> <analysisId>

import os, sys
import json
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.rnaBamToBwsStep import RnaBamToBwsStep

###############
testOnly = False
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        RnaBamToBwsStep(ana,'1','50').writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

galaxyInputFile     = sys.argv[1]
galaxyEvalFile      = sys.argv[2]    # Look up paired, tagLength
galaxyOutUniqPlus   = sys.argv[3]
galaxyOutUniqMinus  = sys.argv[4]
galaxyOutAllPlus    = sys.argv[5]
galaxyOutAllMinus   = sys.argv[6]
genome              = sys.argv[7]
expType             = sys.argv[8]
repNo               = sys.argv[9]
anaId               = sys.argv[10]

# No longer command line parameters:
scriptPath = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
galaxyPath = '/'.join(scriptPath.split('/')[ :-2 ])  
settingsFile = scriptPath + '/' + "settingsE3.txt"

# read the bam evaluation json for tag length
isPaired = False
tagLength = 50
try:
    fp = open(galaxyEvalFile, 'r')
    valJson = json.load(fp)
    fp.close()
    isPaired  = valJson['isPaired']
    tagLength = int(valJson['readSizeMean'])
    #tagLength = (valJson['readSizeMax'] + valJson['readSizeMin']) / 2
except:
    pass # TODO: Require this?

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, genome, expType)
if testOnly:
    ana.dryRun = testOnly
ana.setVar('tagLen',tagLength)

suffix = "Rep" + repNo
# What step expects:
# Inputs: 1 bam, pre-registered in analysis, keyed as: 'alignment' + suffix + '.bam'
# Outputs: target uniq + strand signal file, keyed as: 'uniqPlus'  + suffix + '.bw'
#          target uniq - strand signal file, keyed as: 'uniqMinus' + suffix + '.bw'
#          target all  + strand signal file, keyed as: 'allPlus'   + suffix + '.bw'
#          target all  - strand signal file, keyed as: 'allMinus'  + suffix + '.bw'
    
# set up keys that join inputs through various file forwardings:
bamInputKey   = 'alignment' + suffix + '.bam'
uniqPlusKey   = 'uniqPlus'  + suffix + '.bw'
UniqMinusKey  = 'uniqMinus' + suffix + '.bw'
allPlusKey    = 'allPlus'   + suffix + '.bw'
allMinusKey   = 'allMinus'  + suffix + '.bw'

# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(bamInputKey,'galaxyInput', galaxyInputFile)
nonGalaxyInput  = ana.nonGalaxyInput(bamInputKey)  # Registers and returns the outside location

# outputs:
ana.registerFile( uniqPlusKey, 'galaxyOutput',galaxyOutUniqPlus  )
ana.registerFile( UniqMinusKey,'galaxyOutput',galaxyOutUniqMinus )
ana.registerFile( allPlusKey,  'galaxyOutput',galaxyOutAllPlus   )
ana.registerFile( allMinusKey, 'galaxyOutput',galaxyOutAllMinus  )
resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
ana.createOutFile(uniqPlusKey, 'nonGalaxyOutput','%s_uniqPlus',ext='bw')
ana.createOutFile(UniqMinusKey,'nonGalaxyOutput','%s_uniqMinus',ext='bw')
ana.createOutFile(allPlusKey,  'nonGalaxyOutput','%s_allPlus',ext='bw')
ana.createOutFile(allMinusKey, 'nonGalaxyOutput','%s_allMinus',ext='bw')

# Establish step and run it:
step = RnaBamToBwsStep(ana,suffix)
sys.exit( step.run() )

