#!/usr/bin/env python2.7
# macsE3.py ENCODE3 galaxy pipeline script for peak calling from bam files using MACS
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#Usage: python(2.7) macsE3.py <'DNase'|'ChIPseq'> <inputBam> <inputEval> \
#                             [<controlBam> <controlEval>] <galaxyOutPeaks> <galaxyOutDensity> \
#                             <genome> <expType> <repNo> <analysisId>

import os, sys
import json
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.macsStep import MacsStep

###############
testOnly = False
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        MacsStep(ana).writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

galaxyInputFile     = sys.argv[1]
galaxyValFile       = sys.argv[2]  # look up paired
galaxyOutputPeaks   = sys.argv[3]
galaxyOutputDensity = sys.argv[4]
genome              = sys.argv[5]
expType             = sys.argv[6]
repNo               = sys.argv[7]
anaId               = sys.argv[8]
if expType.lower() == 'chipseq':
    galaxyInputFile2    = sys.argv[3]
    galaxyValFile2      = sys.argv[4]
    galaxyOutputPeaks   = sys.argv[5]
    galaxyOutputDensity = sys.argv[6]
    genome              = sys.argv[7]
    expType             = sys.argv[8]
    repNo               = sys.argv[9]
    anaId               = sys.argv[10]

# No longer command line parameters:
scriptPath = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
galaxyPath = '/'.join(scriptPath.split('/')[ :-2 ])  
settingsFile = scriptPath + '/' + "settingsE3.txt"

# read the fastq validation json for tag length, encoding
# TODO: Should be better evaluation of the eval files.
isPaired = False
try:
    fp = open(galaxyValFile, 'r')
    valJson = json.load(fp)
    fp.close()
    isPaired  = valJson['isPaired']
except:
    pass # TODO: Require this?

if expType.lower() == 'chipseq':
    isPaired2 = isPaired
    try:
        fp = open(galaxyValFile2, 'r')
        valJson = json.load(fp)
        fp.close()
        isPaired2  = valJson['isPaired']
    except:
        pass 
    # TODO Is this really an error?
    if isPaired != isPaired2:
        raise Exception("Evaluation files suggest that alignment and control files do not match.")


# TODO: suffix needs to know whether this is being run on a sample!
suffix = expType + "Rep" + repNo

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, genome, expType)
if testOnly:
    ana.dryRun = testOnly
if isPaired:
    ana.readType = 'paired'
else:
    ana.readType = 'single'

# What step expects:
# Inputs: 1 bam, pre-registered in analysis           keyed as: 'alignment' + suffix + '.bam'
#         1 bam control (optional), pre-registered    keyed as: 'control' + suffix + '.bam'
# Outputs: target narrowPeak peaks file,      keyed as: 'peaks'     + suffix + '.bigBed'
#          target density bigWig file,        keyed as: 'density'   + suffix + '.bigWig'
    
# set up keys that join inputs through various file forwardings:
bamInputKey     = 'alignment' + suffix + '.bam'
controlInputKey = 'control'   + suffix + '.bam'
peakKey         = 'peaks'     + suffix + '.bigBed'
densityKey      = 'density'   + suffix + '.bigWig'

# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(bamInputKey,'galaxyInput', galaxyInputFile)
nonGalaxyInput  = ana.nonGalaxyInput(bamInputKey)  # Registers and returns the outside location
if expType.lower() == 'chipseq':
    ana.registerFile(controlInputKey,'galaxyInput', galaxyInputFile)
    ana.nonGalaxyInput(controlInputKey)

# outputs:
ana.registerFile( peakKey,    'galaxyOutput',galaxyOutputPeaks  )
ana.registerFile( densityKey, 'galaxyOutput',galaxyOutputDensity)
resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
ana.createOutFile(peakKey,    'nonGalaxyOutput',ext='bigBed')
ana.createOutFile(densityKey, 'nonGalaxyOutput',ext='bigWig')

# Establish step and run it:
step = MacsStep(ana,suffix,expType,isPaired)
sys.exit( step.run() )

