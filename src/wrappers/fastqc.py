#!/usr/bin/env python2.7
# fastqc.py module holds methods for running fastqc from a LogicalStep.
# It creates an HTML report of fastq validation info.
#
# Settings required: fastqcPath (or toolsPath)

import os, datetime
from src.logicalStep import StepError

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    version = step.ana.getCmdOut(step.ana.getToolPath('fastqc') + " -version | awk '{print $2}'", \
                                 dryRun=False,logCmd=False)
    expected = step.ana.getSetting('fastqcVersion',version) # Not in settings: not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting fastqc [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# fastqc validation [version: " + version + "]")
    return version

def validate(step, input, outDir):
    '''Validation'''
    cmd = '{fastqc} {fastq} --extract -q'.format( \
          fastqc=step.ana.getToolPath('fastqc'), fastq=input)

    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X")+" 'fastqc' begins...")
    step.err = step.ana.runCmd(cmd, log=step.log) # stdout goes to file
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + " 'fastqc' " + \
                 "returned " + str(step.err))
    if step.err != 0:
        raise StepError('fastqc')

