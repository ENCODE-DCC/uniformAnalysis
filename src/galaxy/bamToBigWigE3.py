#!/usr/bin/env python2.7
# bamToBigWigE3.py ENCODE3 galaxy pipeline script for generating bigWig density signals from a bam.
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#  Usage: python(2.7) bamToBigWigE3,py <inputBam> <bamEvalFile> <readFilter> <strand> \
#                                      <galaxyOutSignal> <genome> <expType> <repNo> <analysisId>

import os, sys
import json
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.bamToBwStep import BamToBwStep

###############
testOnly = False
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        BamToBwStep(ana,'1','50').writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

galaxyInputFile     = sys.argv[1]
galaxyEvalFile      = sys.argv[2]
readFilter          = sys.argv[3]
strand              = sys.argv[4]
galaxyOutSignal     = sys.argv[5]
genome              = sys.argv[6]
expType             = sys.argv[7]
repNo               = sys.argv[8]
anaId               = sys.argv[9]

# No longer command line parameters:
scriptPath = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
galaxyPath = '/'.join(scriptPath.split('/')[ :-2 ])  
settingsFile = scriptPath + '/' + "settingsE3.txt"

# read the bam evaluation json for tag length
alignedBy = 'STAR'  # TODO: change to 'unknown'
try:
    fp = open(galaxyEvalFile, 'r')
    valJson = json.load(fp)
    fp.close()
    if 'alignedBy' in valJson:
        alignedBy = valJson['alignedBy']
except:
    pass # TODO: Require this?

# This should not need to be varified:
if readFilter != 'All' and readFilter != 'Uniq':
    raise Exception("Read filter may only be 'All' or 'Uniq'.")
if strand != 'Plus' and strand != 'Minus':
    raise Exception("Strand may only be 'Plus' or 'Minus'.")

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, genome, expType)
if testOnly:
    ana.dryRun = testOnly

suffix = "Rep" + repNo
if alignedBy != 'unknown':
    suffix = alignedBy.capitalize() + suffix

# What step expects:
# Inputs: 1 bam, pre-registered in analysis, keyed as: 'alignment' + suffix + '.bam'
# Outputs: target signal file, keyed as: 'signal + suffix + readFiler + strand + '.bw'
    
# set up keys that join inputs through various file forwardings:
bamInputKey   = 'alignment' + suffix + '.bam'
signalKey     = 'signal'  + suffix + readFilter + strand + '.bw'

# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(bamInputKey,'galaxyInput', galaxyInputFile)
nonGalaxyInput  = ana.nonGalaxyInput(bamInputKey)  # Registers and returns the outside location

# outputs:
ana.registerFile( signalKey, 'galaxyOutput',galaxyOutSignal  )
resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
ana.createOutFile(signalKey, 'nonGalaxyOutput', \
                             '%s_' + readFilter.lower() + strand.capitalize(),ext='bw')

# Establish step and run it:
step = BamToBwStep(ana,suffix,readFilter,strand)
sys.exit( step.run() )

