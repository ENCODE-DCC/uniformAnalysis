#!/usr/bin/env python2.7
# tophatAlignE3.py ENCODE3 galaxy pipeline script for fastq alignment via Tophat
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#Usage: python(2.7) tophatAlign.py <'paired'|'unpaired'> <inFastq> <inFastqEval> \
#                               [<inFastqR2> <inFastqEvalR2>] <galaxyOutBam> \
#                               <spikeIn> <gender> <genome> <expType> <repNo> <analysisId>

import os, sys
import json
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.tophatAlignmentStep import TophatAlignmentStep

###############
testOnly = False
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        ana.readType = 'paired'
        TophatAlignmentStep(ana,'1').writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

# Command line args:
pairedOrUnpaired     = sys.argv[1]
galaxyInputFile      = sys.argv[2]
galaxyEvalFile       = sys.argv[3]    # Look up tagLength and encoding
galaxyOutputFile     = sys.argv[4]
spikeIn              = sys.argv[5]
gender               = sys.argv[6]
genome               = sys.argv[7]
expType              = sys.argv[8]
repNo                = sys.argv[9]
anaId                = sys.argv[10]
if pairedOrUnpaired == "paired":
    galaxyInputFile2 = sys.argv[4]
    galaxyEvalFile2  = sys.argv[5]
    galaxyOutputFile = sys.argv[6]
    spikeIn          = sys.argv[7]
    gender           = sys.argv[8]
    genome           = sys.argv[9]
    expType          = sys.argv[10]
    repNo            = sys.argv[11]
    anaId            = sys.argv[12]

# No longer command line parameters:
scriptPath = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
galaxyPath = '/'.join(scriptPath.split('/')[ :-2 ])  
settingsFile = scriptPath + '/' + "settingsE3.txt"

# read the fastq Evaluation json for tag length, encoding
encoding = 'sanger'
tagLength = 100
try:
    fp = open(galaxyEvalFile, 'r')
    valJson = json.load(fp)
    fp.close()
    encoding  = str(valJson['encoding'])
    tagLength = int(valJson['tagLength'])
except:
    pass # TODO: Require this?

if pairedOrUnpaired == "paired":
    encoding2  = encoding
    tagLength2 = tagLength
    try:
        fp = open(galaxyEvalFile2, 'r')
        valJson = json.load(fp)
        fp.close()
        encoding2  = str(valJson['encoding'])
        tagLength2 = int(valJson['tagLength'])
    except:
        pass
    if encoding != encoding2:
        raise Exception("Validation files suggest that paired fastq files are formats.")
    if tagLength != tagLength2:
        raise Exception("Validation files suggest that paired fastq files have different" + \
                                                                                " tag lengths.")

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, genome, expType)
ana.gender = gender
if testOnly:
    ana.dryRun = testOnly
ana.readType = pairedOrUnpaired

# What step expects:
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'tagsRep'+replicate+'.fastq'
#         Paired: 'tagsRd1Rep'+replicate+'.fastq' and 'tagsRd2Rep'+replicate+'.fastq' 
# Outputs: a single bam target keyed as:
#          'alignmentTophatRep'+replicate+'.bam'

bamFileKey  = 'alignmentTophatRep'+repNo + '.bam' # Used to tie outputs together
    
# Establish Inputs for galaxy and nonGalaxy alike
if pairedOrUnpaired == "paired":
    fastqRd1Key='tagsRd1Rep'+repNo + '.fastq' # Used to tie inputs together
    fastqRd2Key='tagsRd2Rep'+repNo + '.fastq' # Used to tie inputs together
    ana.registerFile(fastqRd1Key,'galaxyInput', galaxyInputFile)
    ana.registerFile(fastqRd2Key,'galaxyInput', galaxyInputFile2)
    nonGalaxyInput  = ana.nonGalaxyInput(fastqRd1Key)  # Registers and returns the outside location
    nonGalaxyInput2 = ana.nonGalaxyInput(fastqRd2Key)  # Registers and returns the outside location
    # outputs:
    ana.registerFile(bamFileKey,'galaxyOutput',galaxyOutputFile)
    resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
    ana.createOutFile(bamFileKey,'nonGalaxyOutput','%s_%s_tophat', ext='bam', \
                      input1=fastqRd1Key, input2=fastqRd2Key)
else:
    fastqKey='tagsRep'+repNo + '.fastq' # Used to tie inputs togther
    ana.registerFile(fastqKey,'galaxyInput', galaxyInputFile)
    nonGalaxyInput  = ana.nonGalaxyInput(fastqKey)  # Registers and returns the outside location
    # outputs:
    ana.registerFile(bamFileKey,'galaxyOutput',galaxyOutputFile)
    resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
    ana.createOutFile(bamFileKey,'nonGalaxyOutput','%s_tophat',ext='bam' )

# Establish step and run it:
step = TophatAlignmentStep(ana,repNo, spikeIn, encoding, tagLength)
sys.exit( step.run() )
