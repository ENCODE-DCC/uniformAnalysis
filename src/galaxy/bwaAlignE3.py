#!/usr/bin/env python2.7
# bwaAlignE3.py ENCODE3 galaxy pipeline script for fastq alignment via bwa

#Usage: python(2.7) bwaAlign.py <galaxyRootDir> <historyId> <encode3SettingsFile> \
#                               <'paired'|'unpaired'> <inFastq> <inValFile> \
#                               [<inFastqR2> <inValFileR2>] <galaxyOutBam> <repNo> <named>

import os, sys
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.alignmentStep import AlignmentStep

###############
testOnly = False
#python bwaAlignE3.py /hive/users/tdreszer/galaxy/galaxy-dist 47 \
#           /hive/users/tdreszer/galaxy/uniformAnalysis/test/settingsE3.txt unpaired \
#           /hive/users/tdreszer/galaxy/data/dnase/UwDnaseAg04449RawDataRep1.fastq \
#           /hive/users/tdreszer/galaxy/data/dnase/UwDnaseAg04449RawDataRep1_s100000_fastqc/fastqc_report.html \
#           /hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_293.dat 1 test
#python bwaAlignE3.py /hive/users/tdreszer/galaxy/galaxy-dist 47 \
#           /hive/users/tdreszer/galaxy/uniformAnalysis/test/settingsE3.txt paired \
#           /hive/users/tdreszer/galaxy/data/dnase/UwDgfRep1Rd1.fastq \
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
        AlignmentStep(ana,'1').writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

# Command line args:
galaxyPath = sys.argv[1]
userId = sys.argv[2]
settingsFile = sys.argv[3]
pairedOrUnpaired = sys.argv[4]
galaxyInputFile = sys.argv[5]
galaxyValFile = sys.argv[6]    # Only used to enforce step in galaxy!
galaxyOutputFile = sys.argv[7]
repNo = sys.argv[8]
anaId = 'U' + userId
if len( sys.argv ) > 9:
    anaId = sys.argv[9] + anaId
if pairedOrUnpaired == "paired":
    galaxyInputFile2 = sys.argv[7]
    galaxyValFile2 = sys.argv[8]    # Only used to enforce step in galaxy!
    galaxyOutputFile = sys.argv[9]
    repNo = sys.argv[10]
    anaId = 'U' + userId
    if len( sys.argv ) > 11:
        anaId = sys.argv[11] + anaId

# Set up 'ana' so she can do all the work.  If anaId matches another, then it's log is extended
ana = GalaxyAnalysis(settingsFile, anaId, 'hg19')
ana.dryRun(testOnly)
ana.readType = pairedOrUnpaired

# What step expects:
# Inputs: 1 or 2 fastq files, pre-registered in the analysis keyed as:
#         Single: 'tagsRep'+replicate + '.fastq'
#         Paired: 'tagsRd1Rep'+replicate + '.fastq' and 'tagsRd2Rep'+replicate + '.fastq' 
# Outputs: a single bam target and an index for it which will match and analysis targets keyed as:
#          'alignmentRep'+replicate+'.bam'
#          'alignmentRep'+replicate+'.bam.bai'
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
step = AlignmentStep(ana,repNo)
step.run()


