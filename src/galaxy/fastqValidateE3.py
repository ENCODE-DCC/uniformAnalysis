#!/usr/bin/env python2.7
# fastqValidateE3.py ENCODE3 galaxy pipeline script for fastq validation
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#Usage: python(2.7) fastqValidateE3.py <inFastq> <galaxyOutHtml> <galaxyOutDir> <galaxyOutSummary> \
#                                      <genome> <expType> <repNo> <analysisId>

import os, sys
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.fastqValidationStep import FastqValidationStep

###############
testOnly = False
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        FastqValidationStep(ana).writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

# Command line args:
galaxyInputFile  = sys.argv[1]
galaxyOutputHtml = sys.argv[2]
galaxyOutputDir  = sys.argv[3]
galaxyOutSummary = sys.argv[4]
genome           = sys.argv[5]
expType          = sys.argv[6]
repNo            = sys.argv[7]
anaId            = sys.argv[8]
if not galaxyOutputDir.endswith('/'):
    galaxyOutputDir = galaxyOutputDir + '/'
    
# No longer command line parameters:
scriptPath = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
galaxyPath = '/'.join(scriptPath.split('/')[ :-2 ])  
settingsFile = scriptPath + '/' + "settingsE3.txt"

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, genome, expType)
if testOnly:
    ana.dryRun = testOnly
    
# What step expects:
#
# Inputs: 1 fastq file, pre-registered in the analysis   keyed as:   'tags' + suffix + '.fastq'
# Outputs: directory of files (will include html target) keyed as: 'fastqValDir' + suffix
#          zipped file of that directory                 keyed as: 'fastqVal'   + suffix + '.zip'
#          html file in that directory                   keyed as: 'fastqVal'  + suffix + '.html'
#          json file                                     keyed as: 'fastqVal' + suffix + '.json'

# set up keys that join inputs through various file forwardings:
suffix = ana.galaxyFileId(galaxyInputFile) # suffix needs to be based on the input file
if suffix == '-1':
    suffix = ana.fileGetPart(galaxyInputFile,'root')
inputKey   = 'tags'         + suffix + '.fastq'
valDirKey  = 'fastqValDir' + suffix
valZipKey  = 'fastqVal'   + suffix + '.zip'
valHtmlKey = 'fastqVal'  + suffix + '.html'
valJsonKey = 'fastqVal' + suffix + '.json'

# Establish Inputs for galaxy and nonGalaxy alike
ana.registerFile(inputKey,'galaxyInput', galaxyInputFile)
nonGalaxyInput  = ana.nonGalaxyInput(inputKey)  # Registers and returns the outside location

# Output is complete dir
ana.registerFile(valDirKey,'galaxyOutput',galaxyOutputDir)
ana.createOutFile(valDirKey,'nonGalaxyOutput', '%s_sample_fastqc', ext='dir' )
ana.createOutFile(valZipKey,'nonGalaxyOutput', '%s_sample_fastqc', ext='zip' )
ana.createOutFile(valJsonKey,'nonGalaxyOutput','%s_validate',      ext='json' )

# Galaxy needs to know about a single file within the dir.  While it is moved to the analysisDir
# as part of the htmlDir, It must be manually moved for galaxy.  Thus, the standard
# analysis file forwarding is slightly modified here:
ana.registerFile(valHtmlKey,'galaxyOutput',galaxyOutputHtml)
nonGalaxyOutput = ana.createOutFile(valHtmlKey,'nonGalaxyOutput', \
                                   '%s_sample_fastqc/fastqc_report', ext='html' )
#ana.registerFile(valZipKey,'galaxyOutput',galaxyOutputZip) # No need: galaxy zips it anyway
jsonOut = ana.registerFile(valJsonKey,'galaxyOutput',galaxyOutSummary)

# This step needs closer control of how files are delivered:
ana.deliveryKeys([valDirKey,valZipKey,valJsonKey]) # Restrict file delivery to just these
ana.deliverToGalaxyKeys([valDirKey,valZipKey,valHtmlKey,valJsonKey]) # Restrict delivery to these and in order

## TODO: methods for delivering json

# Establish step and run it:
step = FastqValidationStep(ana,suffix)
err = step.run()

# Determine success or failure by reading json output
# NOTE: if this test were in FastqValidationStep(), the results would not be delivered to galaxy!
if err == 0:
    failures = ana.getCmdOut('grep "FAIL" '+jsonOut+'" | grep "basic" | wc -l',logCmd=False)
if failures != "0":
    print "Failed validation test!"
    # sys.exit(1)  # TODO: should we fail here????

sys.exit(err)


