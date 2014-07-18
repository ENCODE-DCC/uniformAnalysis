#!/usr/bin/env python2.7
# starAlignE3.py ENCODE3 galaxy pipeline script for fastq alignment via STAR
# Must run from within galaxy sub-directory.  Requires settingsE3.txt in same directory as script
#
#Usage: python(2.7) starAlign.py <'paired'|'unpaired'> <inFastq> <inFastqEval> \
#                               [<inFastqR2> <inFastqEvalR2>] <genomeOutBam> <annotationOutBam> \
#                               <signalOutAll[Minus]> [<signalOutAllPlus>] \
#                               <signalOutUniq[Minus]> [<signalOutUniqPlus>] <statsOutput> \
#                               <libId> <gender> <genome> <expType> <repNo> <analysisId>

import os, sys
import json
from src.galaxyAnalysis import GalaxyAnalysis
from src.steps.starAlignmentStep import StarAlignmentStep

###############
testOnly = False
###############

if  sys.argv[1] == '--version':
    settingsFile = os.path.split( os.path.abspath( sys.argv[0] ) )[0] + '/' + "settingsE3.txt"
    if os.path.isfile( settingsFile ):  # Unfortunately can't get xml arg for settings
        ana = GalaxyAnalysis(settingsFile, 'versions', 'hg19')
        ana.readType = 'paired'
        StarAlignmentStep(ana).writeVersions(allLevels=True) # Prints to stdout
    else:
        print "Can't locate " + settingsFile
    exit(0)

# Command line args:
pairedOrUnpaired     = sys.argv[1]
galaxyInputFile      = sys.argv[2]
galaxyEvalFile       = sys.argv[3]    # Look up tagLength and encoding
galaxyGenoBamOutput  = sys.argv[4]
galaxyAnnoBamOutput  = sys.argv[5]
galaxyBwAllOut       = sys.argv[6]
galaxyBwUniqOut      = sys.argv[7]
galaxyStatsOut       = sys.argv[8]
libId                = sys.argv[9]
gender               = sys.argv[10]
genome               = sys.argv[11]
expType              = sys.argv[12]
repNo                = sys.argv[13]
anaId                = sys.argv[14]
if pairedOrUnpaired == "paired":
    galaxyInputFile2     = sys.argv[4]
    galaxyEvalFile2      = sys.argv[5]
    galaxyGenoBamOutput  = sys.argv[6]
    galaxyAnnoBamOutput  = sys.argv[7]
    galaxyBwAllMinusOut  = sys.argv[8]
    galaxyBwAllPlusOut   = sys.argv[9]
    galaxyBwUniqMinusOut = sys.argv[10]
    galaxyBwUniqPlusOut  = sys.argv[11]
    galaxyStatsOut       = sys.argv[12]
    libId                = sys.argv[13]
    gender               = sys.argv[14]
    genome               = sys.argv[15]
    expType              = sys.argv[16]
    repNo                = sys.argv[17]
    anaId                = sys.argv[18]

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
# Outputs: target genome bam keyed as:          'genomeAlignedStarRep' + replicate + '.bam'
#          interim annotation bam keyed as: 'annotationAlignedStarRep' + replicate + '.bam'
#          interim statistics txt file keyed as:   'statisticsStarRep' + replicate + '.txt'
#          and either 4 (paired) signal files:         'signalStarRep' + replicate + 'UniqMinus.bw'
#                                                      'signalStarRep' + replicate +  'UniqPlus.bw'
#                                                      'signalStarRep' + replicate +  'AllMinus.bw'
#                                                      'signalStarRep' + replicate +   'AllPlus.bw'
#          or 2 (unpaired) target signal file2:        'signalStarRep' + replicate +      'Uniq.bw'
#                                                      'signalStarRep' + replicate +       'All.bw'

genoBamKey  =     'genomeAlignedStarRep'+repNo + '.bam' # Used to tie outputs together
annoBamKey  = 'annotationAlignedStarRep'+repNo + '.bam' # Used to tie outputs together
statsKey    =        'statisticsStarRep'+repNo + '.txt' # Used to tie outputs together
    
# Establish Inputs for galaxy and nonGalaxy alike
if pairedOrUnpaired == "paired":
    fastqRd1Key='tagsRd1Rep'+repNo + '.fastq' # Used to tie inputs together
    fastqRd2Key='tagsRd2Rep'+repNo + '.fastq' # Used to tie inputs together
    ana.registerFile(fastqRd1Key,'galaxyInput', galaxyInputFile)
    ana.registerFile(fastqRd2Key,'galaxyInput', galaxyInputFile2)
    nonGalaxyInput  = ana.nonGalaxyInput(fastqRd1Key)  # Registers and returns the outside location
    nonGalaxyInput2 = ana.nonGalaxyInput(fastqRd2Key)  # Registers and returns the outside location
    # outputs:
    ana.registerFile(genoBamKey,'galaxyOutput',galaxyGenoBamOutput)
    resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
    ana.createOutFile(genoBamKey,'nonGalaxyOutput','%s_%s_starGenome', ext='bam', \
                      input1=fastqRd1Key, input2=fastqRd2Key)
    ana.registerFile(annoBamKey,'galaxyOutput',galaxyAnnoBamOutput)
    ana.createOutFile(annoBamKey,'nonGalaxyOutput','%s_%s_starAnnotation', ext='bam', \
                      input1=fastqRd1Key, input2=fastqRd2Key)
    ana.registerFile( statsKey,   'galaxyOutput',galaxyStatsOut)
    ana.createOutFile(statsKey,'nonGalaxyOutput','%s_%s_starStats', ext='txt', \
                      input1=fastqRd1Key, input2=fastqRd2Key)
    # signal bigWigs:
    allMinusKey =               'signalStarRep' + repNo +  'AllMinus.bw'
    ana.registerFile( allMinusKey,   'galaxyOutput',galaxyBwAllMinusOut)
    ana.createOutFile(allMinusKey,'nonGalaxyOutput','%s_%s_starAllMinus', ext='bw', \
                      input1=fastqRd1Key, input2=fastqRd2Key)
    allPlusKey =               'signalStarRep' + repNo +   'AllPlus.bw'
    ana.registerFile( allPlusKey,    'galaxyOutput',galaxyBwAllPlusOut)
    ana.createOutFile(allPlusKey,'nonGalaxyOutput','%s_%s_starAllPlus',  ext='bw', \
                      input1=fastqRd1Key, input2=fastqRd2Key)
    uniqMinusKey =               'signalStarRep' + repNo + 'UniqMinus.bw'
    ana.registerFile( uniqMinusKey,   'galaxyOutput',galaxyBwUniqMinusOut)
    ana.createOutFile(uniqMinusKey,'nonGalaxyOutput','%s_%s_starUniqMinus',ext='bw', \
                      input1=fastqRd1Key, input2=fastqRd2Key)
    uniqPlusKey =               'signalStarRep' + repNo +  'UniqPlus.bw'
    ana.registerFile( uniqPlusKey,   'galaxyOutput',galaxyBwUniqPlusOut)
    ana.createOutFile(uniqPlusKey,'nonGalaxyOutput','%s_%s_starUniqPlus', ext='bw', \
                      input1=fastqRd1Key, input2=fastqRd2Key)
else:
    fastqKey='tagsRep'+repNo + '.fastq' # Used to tie inputs togther
    ana.registerFile(fastqKey,'galaxyInput', galaxyInputFile)
    nonGalaxyInput  = ana.nonGalaxyInput(fastqKey)  # Registers and returns the outside location
    # outputs:
    ana.registerFile(genoBamKey,'galaxyOutput',galaxyGenoBamOutput)
    resultsDir  = ana.resultsDir(galaxyPath) # prefers nonGalaxyInput location over settings loc
    ana.createOutFile(genoBamKey,'nonGalaxyOutput','%s_starGenome',ext='bam')
    ana.registerFile(annoBamKey,'galaxyOutput',galaxyAnnoBamOutput)
    ana.createOutFile(annoBamKey,'nonGalaxyOutput','%s_starAnnotation', ext='bam')
    ana.registerFile( statsKey,   'galaxyOutput',galaxyStatsOut)
    ana.createOutFile(statsKey,'nonGalaxyOutput','%s_starStats', ext='txt')
    # signal bigWigs:
    allKey =                'signalStarRep' + repNo + 'All.bw'
    ana.registerFile( allKey,   'galaxyOutput',galaxyBwAllOut)
    ana.createOutFile(allKey,'nonGalaxyOutput','%s_starAll',  ext='bw')
    uniqKey =                'signalStarRep' + repNo + 'Uniq.bw'
    ana.registerFile( uniqKey,   'galaxyOutput',galaxyBwUniqOut)
    ana.createOutFile(uniqKey,'nonGalaxyOutput','%s_starUniq',ext='bw')

# Establish step and run it:
step = StarAlignmentStep(ana,repNo, libId, encoding, tagLength)
sys.exit( step.run() )
