#!/usr/bin/env python2.7
# fastqValidateE3.py ENCODE3 galaxy pipeline script for fastq validation

#Usage: python(2.7) fastqValidateE3.py <galaxyRootDir> <userId> <encode3SettingsFile> \
#                                      <inFastq> <galaxyOutHtml> <repNo> <named>
#      The command line tools that will be run:
#      fastqStatsAndSubsample -sampleSize=<sampleSize> -seed=<randomSeed>  <inFile> stats.out sampleOf.fastq
#      fastqc sampleOf.fastq --extract -t 4 -q -o outputDir/

import os, sys
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.fastqValidationStep import FastqValidationStep

###############
testOnly = False
#python fastqValidateE3.py /hive/users/tdreszer/galaxy/galaxy-dist 47 \
#               /hive/users/tdreszer/galaxy/uniformAnalysis/test/settingsE3.txt 
#               /hive/users/tdreszer/galaxy/data/dnase/UwDnaseAg04449RawDataRep1.fastq \
#               /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_293.dat  \
#               /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_293/files 1 test
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        FastqValidationStep(ana,'1').writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

# Command line args:
galaxyPath = sys.argv[1]
userId = sys.argv[2]
settingsFile = sys.argv[3]
galaxyInputFile = sys.argv[4]
galaxyOutputHtml = sys.argv[5]
galaxyOutputDir  = sys.argv[6]
if not galaxyOutputDir.endswith('/'):
    galaxyOutputDir = galaxyOutputDir + '/'
repNo = sys.argv[7]
anaId = 'U' + userId
if len( sys.argv ) > 8:
    anaId = sys.argv[8] + anaId
    
# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, 'hg19')
ana.dryRun(testOnly)
    
# What step expects:
#
# Inputs: 1 fastq file, pre-registered in the analysis   keyed as:   'tags' + suffix + '.fastq'
# Outputs: directory of files (will include html target) keyed as: 'valDir' + suffix
#          zipped file of that directory                 keyed as:    'val' + suffix + '.zip'
#          html file in that directory                   keyed as:    'val' + suffix + '.html'

# set up keys that join inputs through various file forwardings:
suffix = ana.galaxyFileId(galaxyInputFile) # suffix needs to be based on the input file
if suffix == '-1':
    suffix = ana.fileGetPart(galaxyInputFile,'root')
inputKey   = 'tags'   + suffix + '.fastq'
valDirKey  = 'valDir' + suffix
valZipKey  = 'val'    + suffix + '.zip'
valHtmlKey = 'val'    + suffix + '.html'

# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(inputKey,'galaxyInput', galaxyInputFile)
nonGalaxyInput  = ana.nonGalaxyInput(inputKey)  # Registers and returns the outside location

# Output is complete dir
ana.registerFile(valDirKey,'galaxyOutput',galaxyOutputDir)
nonGalaxyOutDir = ana.createOutFile(valDirKey,'nonGalaxyOutput', '%s_sample_fastqc', ext='dir' )
#ana.registerFile(valZipKey,'galaxyOutput',galaxyOutputZip)
nonGalaxyOutZip = ana.createOutFile(valZipKey,'nonGalaxyOutput', '%s_sample_fastqc', ext='zip' )

# Galaxy needs to know about a single file within the dir.  While it is moved to the analysisDir
# as part of the htmlDir, It must be manually moved for galaxy.  Thus, the standard
# analysis file forwarding is slightly modified here:
ana.registerFile(valHtmlKey,'galaxyOutput',galaxyOutputHtml)
nonGalaxyOutput = ana.createOutFile(valHtmlKey,'nonGalaxyOutput', \
                                   '%s_sample_fastqc/fastqc_report', ext='html' )

# This step needs closer control of how files are delivered:
ana.deliveryKeys([valDirKey,valZipKey]) # Restrict file delivery to just these
ana.deliverToGalaxyKeys([valDirKey,valZipKey,valHtmlKey]) # Restrict delivery to these and in order

# Establish step and run it:
step = FastqValidationStep(ana,suffix)
step.run()

# NOTE: would be nice to copy nonGalaxyOutZip to galaxyOutputDir, but galaxy will zip it up anyway


