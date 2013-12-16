#!/usr/bin/env python2.7
# hotspotE3.py ENCODE3 galaxy pipeline script for peak calling from bam files

#  Usage: python(2.7) hotspotE3,py <galaxyRootDir> <userId> <encode3SettingsFile> <inputBam> \
#                                  <tagLen> <metrixFile> <galaxyOutHot> <galaxyOutPeaks> \
#                                  <galaxyOutDensity> <fullOrSample> <repNo> <named>

import os, sys
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.hotspotStep import HotspotStep

###############
testOnly = False
#python hotspotE3.py /hive/users/tdreszer/galaxy/galaxy-dist 47 
#            /hive/users/tdreszer/galaxy/uniformAnalysis/test/settingsE3.txt 
#            /hive/users/tdreszer/galaxy/data/dnase/UwDnaseAg04449RawDataRep1.bam 36 
#            /hive/users/tdreszer/galaxy/data/dnase/UwDnaseAg04449RawDataRep1_metricHist.txt 
#            /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_293.dat \
#            /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_294.dat \
#            /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_295.dat full 1 test
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        HotspotStep(ana,'1','50').writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

galaxyPath = sys.argv[1]
userId = sys.argv[2]
settingsFile = sys.argv[3]
#singlePaired = sys.argv[4]
galaxyInputFile  = sys.argv[4]
tagLen           = sys.argv[5]
galaxyMetricFile = sys.argv[6]    # Only used to enforce step in galaxy!
galaxyOutputHot     = sys.argv[7]
galaxyOutputPeaks   = sys.argv[8]
galaxyOutputDensity = sys.argv[9]
fullOrSample        = sys.argv[10]
repNo = sys.argv[11]
anaId = 'U' + userId
if len( sys.argv ) > 12:
    anaId = sys.argv[12] + anaId

# TODO: suffix needs to know whether this is being run on a sample!
suffix = "Rep" + repNo
if fullOrSample == 'sample':
    suffix = suffix + '_sample'

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, 'hg19')
ana.dryRun(testOnly)
ana.setVar('tagLen',tagLen)

# What step expects:
# Inputs: 1 bam, pre-registered in analysis   keyed as: 'alignment' + suffix + '.bam'
# Outputs: target broadPeak hotspot file,     keyed as: 'hot'       + suffix + '.bed'
#          target broadPeak hotspot FDR file, keyed as: 'hotFrd'    + suffix + '.bed'
#          target narrowPeak peaks file,      keyed as: 'peaks'     + suffix + '.bed'
#          interim density bed file,          keyed as: 'density'   + suffix + '.bed.starch'
#          target density bigWig file,        keyed as: 'density'   + suffix + '.bigWig'
    
# set up keys that join inputs through various file forwardings:
bamInputKey   = 'alignment' + suffix + '.bam'
hotKey        = 'hot'       + suffix + '.bed'
#hotFdrKey     = 'hotFdr'    + suffix + '.bed'   # Don't even bother with unwanted interims!
peakKey       = 'peaks'     + suffix + '.bed'
#starchedKey   = 'density'   + suffix + '.bed.starch'
densityKey    = 'density'   + suffix + '.bigWig'

# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(bamInputKey,'galaxyInput', galaxyInputFile)
nonGalaxyInput  = ana.nonGalaxyInput(bamInputKey)  # Registers and returns the outside location

# outputs:
ana.registerFile( hotKey,     'galaxyOutput',galaxyOutputHot    )
ana.registerFile( peakKey,    'galaxyOutput',galaxyOutputPeaks  )
ana.registerFile( densityKey, 'galaxyOutput',galaxyOutputDensity)
resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
ana.createOutFile(hotKey,     'nonGalaxyOutput',ext='bed')
#ana.createOutFile(hotFdrKey,  'intermediate',   ext='bed')
ana.createOutFile(peakKey,    'nonGalaxyOutput',ext='bed')
#ana.createOutFile(starchedKey,'intermediate',   ext='bed.starch' )
ana.createOutFile(densityKey, 'nonGalaxyOutput',ext='bigWig')

# Establish step and run it:
step = HotspotStep(ana,suffix,tagLen)
step.run()

