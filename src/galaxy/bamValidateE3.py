#!/usr/bin/env python2.7
# bamValidateE3.py ENCODE3 galaxy pipeline script for validating bam files
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#  Usage: python(2.7) bamValidateE3,py <userId> <galaxyInputBam> <galaxyOutBamEval> \
#                                      <genome> <expType> <repNo> <analysisId>

import os, sys
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.bamEvaluateStep import BamEvaluateStep

###############
testOnly = False
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        BamEvaluateStep(ana).writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)
     
galaxyInputFile     = sys.argv[1]
galaxyOutBamEval    = sys.argv[2]
genome              = sys.argv[3]
expType             = sys.argv[4]
repNo               = sys.argv[5]
anaId               = sys.argv[6]

# No longer command line parameters:
scriptPath = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
galaxyPath = '/'.join(scriptPath.split('/')[ :-2 ])  
settingsFile = scriptPath + '/' + "settingsE3.txt"

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, genome, expType)
if testOnly:
    ana.dryRun = testOnly

# What step expects:
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'alignmentRep' + replicate + '.bam'
# Outputs: 1 interim Corr       file, keyed as: 'strandCorr' + suffix +    '.txt'
#          1 target json        file, keyed as: 'bamEvaluate' + suffix +   '.json'

# TODO: Does a galaxy user really want the sample bam?
    
# set up keys that join inputs through various file forwardings:
bamInputKey   = 'alignmentRep'   + repNo +    '.bam'

# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(bamInputKey,'galaxyInput', galaxyInputFile)
nonGalaxyInput  = ana.nonGalaxyInput(bamInputKey)  # Registers and returns the outside location
suffix = 'Rep' + repNo
if nonGalaxyInput.lower().find('_star') != -1:
    suffix += 'ByStar'
elif nonGalaxyInput.find('_tophat') != -1:
    suffix += 'ByTophat'
elif nonGalaxyInput.lower().find('_bwa') != -1:
    suffix += 'ByBwa'
bamSampleKey  = 'alignment'      + suffix + '_5M.bam'
bamEvalKey    = 'bamEvaluate'    + suffix +    '.json'

# outputs:
ana.registerFile( bamEvalKey,     'galaxyOutput',galaxyOutBamEval)
resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
ana.createOutFile(bamEvalKey,  'nonGalaxyOutput','%s_bamEval',ext='json')

# Establish step and run it:
step = BamEvaluateStep(ana,repNo,suffix)
sys.exit( step.run() )

