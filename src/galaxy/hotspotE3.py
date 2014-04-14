#!/usr/bin/env python2.7
# hotspotE3.py ENCODE3 galaxy pipeline script for peak calling from bam files using hotspot
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#  Usage: python(2.7) hotspotE3,py <inputBam> <bamEvalFile> \
#                                  <galaxyOutHot> <galaxyOutPeaks> <galaxyOutDensity> \
#                                  <fullOrSample> <genome> <expType> <repNo> <analysisId>

import os, sys
import json
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.hotspotStep import HotspotStep

###############
testOnly = False
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        HotspotStep(ana).writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

galaxyInputFile     = sys.argv[1]
galaxyEvalFile      = sys.argv[2]    # Look up paired, tagLength
galaxyOutputHot     = sys.argv[3]
galaxyOutputPeaks   = sys.argv[4]
galaxyOutputDensity = sys.argv[5]
fullOrSample        = sys.argv[6]
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

# TODO: suffix needs to know whether this is being run on a sample!
suffix = "Rep" + repNo
if fullOrSample == 'sample':
    suffix = suffix + '_sample'

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, genome, expType)
if testOnly:
    ana.dryRun = testOnly
ana.setVar('tagLen',tagLength)

# What step expects:
# Inputs: 1 bam, pre-registered in analysis   keyed as: 'alignment' + suffix + '.bam'
# Outputs: target broadPeak hotspot file,     keyed as: 'hot'       + suffix + '.bigBed'
#          target narrowPeak peaks file,      keyed as: 'peaks'     + suffix + '.bigBed'
#          target density bigWig file,        keyed as: 'density'   + suffix + '.bigWig'
    
# set up keys that join inputs through various file forwardings:
bamInputKey   = 'alignment' + suffix + '.bam'
hotKey        = 'hot'       + suffix + '.bigBed'
peakKey       = 'peaks'     + suffix + '.bigBed'
densityKey    = 'density'   + suffix + '.bigWig'

# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(bamInputKey,'galaxyInput', galaxyInputFile)
nonGalaxyInput  = ana.nonGalaxyInput(bamInputKey)  # Registers and returns the outside location

# outputs:
ana.registerFile( hotKey,     'galaxyOutput',galaxyOutputHot    )
ana.registerFile( peakKey,    'galaxyOutput',galaxyOutputPeaks  )
ana.registerFile( densityKey, 'galaxyOutput',galaxyOutputDensity)
resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
ana.createOutFile(hotKey,     'nonGalaxyOutput',ext='bigBed')
ana.createOutFile(peakKey,    'nonGalaxyOutput',ext='bigBed')
ana.createOutFile(densityKey, 'nonGalaxyOutput',ext='bigWig')

# Establish step and run it:
step = HotspotStep(ana,suffix,tagLength)
sys.exit( step.run() )

