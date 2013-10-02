#!/usr/bin/env python2.7
# fastqc.py module holds methods for running fastqc from a LogicalStep.
# It creates an HTML report of fastq validation info.
#
# Settings required: fastqcPath (or toolsPath)

import datetime
from src.logicalstep import StepError

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    version = step.exp.getCmdOut(step.exp.getToolPath('fastqc')+" -version | awk '{print $2}'",\
                                 dryRun=False,logCmd=False)
    expected = step.exp.getSetting('fastqcVersion',version) # Not in settings then not enforced!
    if step.exp.strict and version != expected:
        raise Exception("Expecting fastqc [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# fastqc validation [version: " + version + "]")
    return version

def validate(step, input, outDir):
    '''Validation'''
    cmd = '{fastqc} {fastq} --extract -t 4 -q -o {outDir}'.format( \
          fastqc=step.exp.getToolPath('fastqc'), fastq=input, outDir=outDir)

    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X")+" 'fastqc' begins...")
    step.err = step.exp.runCmd(cmd, log=step.log) # stdout goes to file
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + " 'fastqc' " + \
                 "returned " + str(step.err))
    if step.err != 0:
        raise StepError('fastqc')

