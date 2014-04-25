#!/usr/bin/env python2.7
# mergeBamsE3.py ENCODE3 galaxy pipeline script for merging 2 bam replicates
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#  Usage: python(2.7) mergeBamsE3,py <inputBamA> <repA> <inputBamB> <repB> <galaxyOutMergedBam> \
#                                    <genome> <expType> <analysisId>

# TODO: Do we really need to track replicate numbers?

import os, sys
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.mergeBamStep import MergeBamStep

###############
testOnly = False
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        MergeBamStep(ana).writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)
     
galaxyInputBamA    = sys.argv[1]
repA               = sys.argv[2]
galaxyInputBamB    = sys.argv[3]
repB               = sys.argv[4]
galaxyOutMergedBam = sys.argv[5]
genome             = sys.argv[6]
expType            = sys.argv[7]
anaId              = sys.argv[8]

# No longer command line parameters:
scriptPath = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
galaxyPath = '/'.join(scriptPath.split('/')[ :-2 ])  
settingsFile = scriptPath + '/' + "settingsE3.txt"

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, genome, expType)
if testOnly:
    ana.dryRun = testOnly

# What step expects:
# Inputs: 2 bam files, pre-registered in the analysis and both keyed as: 'bamRep' + replicateN + '.bam'
# Outputs: 1 merged bam keyed as: 'mergedRep' + replicate1 + 'Rep' +replcicate2 + '.bam'
    
# set up keys that join inputs through various file forwardings:
bamAkey       = 'bamRep' + repA + '.bam'
bamBkey       = 'bamRep' + repB + '.bam'
mergedBamKey  = 'mergedRep' + repA + 'Rep' + repB + '.bam'

# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(bamAkey,'galaxyInput', galaxyInputBamA)
ana.registerFile(bamBkey,'galaxyInput', galaxyInputBamB)
nonGalaxyInput1  = ana.nonGalaxyInput(bamAkey)  # Registers and returns the outside location
nonGalaxyInput2  = ana.nonGalaxyInput(bamBkey)  # Need to register these to ensure nonGalOut naming

# outputs:
ana.registerFile( mergedBamKey,   'galaxyOutput',galaxyOutMergedBam)
resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
ana.createOutFile(mergedBamKey,'nonGalaxyOutput','%s_%s_merged',ext='bam', \
                  input1=bamAkey, input2=bamBkey)

# Establish step and run it:
step = MergeBamStep(ana,repA,repB)
sys.exit( step.run() )

