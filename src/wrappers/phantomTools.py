#!/usr/bin/env python2.7
# phantomTools.py module holds methods for running R phantomTools scripts from a LogicalStep.
#
# Settings required: phantomToolPath (or toolsPath), Rscript MUST BE ON PATH ???

##### TODO: Resolve path for Rscript.  

import datetime
from src.logicalstep import StepError

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    rVersion = step.exp.getCmdOut(step.exp.getPath('RscriptPath','') + \
                                  "Rscript --version 2>&1 | awk '{print $5}'", \
                                  dryRun=False,logCmd=False)
    expected = step.exp.getSetting('RscriptVersion',rVersion) # Not in settings then not enforced!
    if step.exp.strict and rVersion != expected:
        raise Exception("Expecting Rscript [version: "+expected+"], " + \
                        "but found [version: "+rVersion+"]")
    version = step.exp.getCmdOut('grep Version ' + \
                                 step.exp.getPath('phantomToolsPath',alt='toolPath') + \
                                 "README.txt | awk '{print $2}'", dryRun=False,logCmd=False)
    expected = step.exp.getSetting('phantomToolsVersion',version) # Not in settings then not enforced!
    if step.exp.strict and version != expected:
        raise Exception("Expecting phantomTools [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# phantomTools [version: " + version + \
                     "] running on Rscript [version: " + rVersion + "]")
    return version

def strandCorr(step, bam, strandCor):
    '''
    Generates strand correlations for bam.
    '''
    cmd = 'Rscript {phantomTools}run_spp.R -c={input} -out={output}'.format( \
          phantomTools=step.exp.getPath('phantomToolsPath',alt='toolPath'), \
          input=bam, output=strandCor)

    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'Rscript' phantomTools strandCorr begins...")
    step.err = step.exp.runCmd(cmd, log=step.log)
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'Rscript' phantomTools strandCorr returned " + str(step.err))
    if step.err != 0:
        raise StepError('strandCorr')

