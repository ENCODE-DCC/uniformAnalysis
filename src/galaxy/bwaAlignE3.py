#!/usr/bin/env python2.7
# bwaAlignE3.py ENCODE3 galaxy pipeline script for fastq alignment via bwa
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#Usage: python(2.7) bwaAlign.py <'paired'|'unpaired'> <inFastq> <inValFile> \
#                               [<inFastqR2> <inValFileR2>] <galaxyOutBam> <repNo> <analysisId>

import os, sys
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.bwaAlignmentStep import BwaAlignmentStep

###############
testOnly = False
#python bwaAlignE3.py unpaired \
#           /hive/users/tdreszer/galaxy/data/dnase/UwDnaseAg04449RawDataRep1.fastq \
#           /hive/users/tdreszer/galaxy/data/dnase/UwDnaseAg04449RawDataRep1_s100000_fastqc/fastqc_report.html \
#           /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_293.dat 1 test
#python bwaAlignE3.py paired /hive/users/tdreszer/galaxy/data/dnase/UwDgfRep1Rd1.fastq \
#           /hive/users/tdreszer/galaxy/data/dnase/UwDgfRep1Rd1_s100000_fastqc/fastqc_report.html \
#           /hive/users/tdreszer/galaxy/data/dnase/UwDgfRep1Rd2.fastq \
#           /hive/users/tdreszer/galaxy/data/dnase/UwDgfRep1Rd2_s100000_fastqc/fastqc_report.html \
#           /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_293.dat 1 test
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        ana.readType = 'paired'
        BwaAlignmentStep(ana,'1').writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

# Command line args:
pairedOrUnpaired     = sys.argv[1]
galaxyInputFile      = sys.argv[2]
galaxyValFile        = sys.argv[3]    # Only used to enforce step in galaxy!
galaxyOutputFile     = sys.argv[4]
repNo                = sys.argv[5]
anaId                = sys.argv[6]
if pairedOrUnpaired == "paired":
    galaxyInputFile2 = sys.argv[4]
    galaxyValFile2   = sys.argv[5]    # Only used to enforce step in galaxy!
    galaxyOutputFile = sys.argv[6]
    repNo            = sys.argv[7]
    anaId            = sys.argv[8]

# No longer command line parameters:
scriptPath = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
galaxyPath = '/'.join(scriptPath.split('/')[ :-2 ])  
settingsFile = scriptPath + '/' + "settingsE3.txt"

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, 'hg19')
if testOnly:
    ana.dryRun = testOnly
ana.readType = pairedOrUnpaired

# What step expects:
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'tagsRep'+replicate + '.fastq'
#         Paired: 'tagsRd1Rep'+replicate + '.fastq' and 'tagsRd2Rep'+replicate + '.fastq' 
# Outputs: a single bam target and an index for it which will match and analysis targets keyed as:
#          'alignmentRep'+replicate+'.bam'
#          'alignmentRep'+replicate+'.bam.bai'
#    and an interim json file, keyed as: 'alignmentRep' + replicate +  '.json'

bamFileKey  = 'alignmentRep'+repNo + '.bam' # Used to tie outputs togther
#bamIndexKey = 'alignmentRep'+repNo + '.bam.bai'  # NOTE: Galaxy provides a bam index
    
# Establish Inputs for galaxy and nonGalaxy alike
if pairedOrUnpaired == "paired":
    fastqRd1Key='tagsRd1Rep'+repNo + '.fastq' # Used to tie inputs togther
    fastqRd2Key='tagsRd2Rep'+repNo + '.fastq' # Used to tie inputs togther
    ana.registerFile(fastqRd1Key,'galaxyInput', galaxyInputFile)
    ana.registerFile(fastqRd2Key,'galaxyInput', galaxyInputFile2)
    nonGalaxyInput  = ana.nonGalaxyInput(fastqRd1Key)  # Registers and returns the outside location
    nonGalaxyInput2 = ana.nonGalaxyInput(fastqRd2Key)  # Registers and returns the outside location
    # outputs:
    ana.registerFile(bamFileKey,'galaxyOutput',galaxyOutputFile)
    #ana.registerFile(bamIndexKey,'galaxyOutput',galaxyOutputFile2)
    resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
    ana.createOutFile(bamFileKey,'nonGalaxyOutput','%s_%s', ext='bam', \
                      input1=fastqRd1Key, input2=fastqRd2Key)
    #ana.createCompanionOutFile(bamFileKey.bamIndexKey,ext='bam.bai')
else:
    fastqKey='tagsRep'+repNo + '.fastq' # Used to tie inputs togther
    ana.registerFile(fastqKey,'galaxyInput', galaxyInputFile)
    nonGalaxyInput  = ana.nonGalaxyInput(fastqKey)  # Registers and returns the outside location
    # outputs:
    ana.registerFile(bamFileKey,'galaxyOutput',galaxyOutputFile)
    #ana.registerFile(bamIndexKey,'galaxyOutput',galaxyOutputFile2)
    resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
    ana.createOutFile(bamFileKey,'nonGalaxyOutput',ext='bam' )
    #ana.createCompanionOutFile(bamFileKey.bamIndexKey,ext='bam.bai')

# Establish step and run it:
step = BwaAlignmentStep(ana,repNo)
sys.exit( step.run() )
