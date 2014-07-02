#!/usr/bin/env python2.7
# rsemQuantfyAlign.py ENCODE3 galaxy pipeline script for transcript quantification via RSEM
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#Usage: python(2.7) rsemQuantfyAlign.py <inAnnotationBam> <bamEvalFile> \
#                               <geneResults> <transcriptResults> \
#                               <annotationBam> \
#                               <genome> <expType> <repNo> <analysisId>

import os, sys
import json
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.rsemStep import RsemStep

###############
testOnly = False
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        ana.readType = 'paired'
        RsemStep(ana).writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

# Command line args:
galaxyBamInput       = sys.argv[1]
galaxyEvalFile       = sys.argv[2]    # Look up tagLength and encoding
galaxyOutGenes       = sys.argv[3]
galaxyOutTrans       = sys.argv[4]
genome               = sys.argv[5]
expType              = sys.argv[6]
repNo                = sys.argv[7]
anaId                = sys.argv[8]

# No longer command line parameters:
scriptPath = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
galaxyPath = '/'.join(scriptPath.split('/')[ :-2 ])  
settingsFile = scriptPath + '/' + "settingsE3.txt"

# read the fastq Evaluation json for tag length, encoding
alignedBy = 'STAR'  # TODO: change to 'unknown'
pairedOrUnpaired = 'single';
try:
    fp = open(galaxyEvalFile, 'r')
    valJson = json.load(fp)
    fp.close()
    if 'alignedBy' in valJson:
        alignedBy = valJson['alignedBy']
    if 'isPaired' in valJson and valJson['isPaired']:
        pairedOrUnpaired = 'paired';
except:
    pass # TODO: Require this?

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, genome, expType)
if testOnly:
    ana.dryRun = testOnly
ana.readType = pairedOrUnpaired

suffix = "Rep" + repNo
# if tansformed/transformable bam is provided.
if alignedBy != 'unknown':
    suffix = alignedBy.capitalize() + suffix
    
# What step expects:
# Inputs: 1 Annotation alignment bam             keyed: 'annotation'              + suffix + '.bam'
# Outputs: 1 target Gene       results tab file, keyed: 'quantifyGenesRsem'       + suffix + '.tab'
#          1 target Transcript results tab file, keyed: 'quantifyTranscriptsRsem' + suffix + '.tab'

bamInputKey  = 'annotation'              + suffix + '.bam' # Used to tie inputs together
genesFileKey = 'quantifyGenesRsem'       + suffix + '.tab' # Used to tie outputs together
transFileKey = 'quantifyTranscriptsRsem' + suffix + '.tab'
    
# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(bamInputKey,'galaxyInput', galaxyBamInput)
nonGalaxyInput  = ana.nonGalaxyInput(bamInputKey)  # Registers and returns the outside location
# outputs:
ana.registerFile(genesFileKey,'galaxyOutput',galaxyOutGenes)
resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
ana.createOutFile(genesFileKey,'nonGalaxyOutput','%s_rsemGenes', ext='tab')
ana.registerFile(transFileKey,'galaxyOutput',galaxyOutTrans)
ana.createOutFile(transFileKey,'nonGalaxyOutput','%s_rsemTranscripts', ext='tab')

# Establish step and run it:
step = RsemStep(ana, suffix)
sys.exit( step.run() )
