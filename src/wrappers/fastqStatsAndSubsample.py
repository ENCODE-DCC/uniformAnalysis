#!/usr/bin/env python2.7
# fastqStatsAndSubsample.py module holds methods for running fastqStatsAndSubsample from 
# a LogicalStep.  It is used to sample a fastq.
#
# Settings required: fastqStatsAndSubsamplePath (or toolsPath), fastqSampleReads, fastqSampleSeed

import datetime
from src.logicalstep import StepError

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    #version = step.exp.getCmdOut(step.exp.getToolPath('fastqStatsAndSubsample') + \
    #                             " -version | awk '{print $2}'",dryRun=False,logCmd=False)
    version = "unknown"  # Sorry, this tool has no version.
    #expected = step.exp.getSetting('fastqcVersion',version) # Not in settings then not enforced!
    #if step.exp.strict and version != expected:
    #    raise Exception("Expecting fastqStatsAndSubsample [version: "+expected+"], " + \
    #                    "but found [version: "+version+"]")
    if logOut:
        step.log.out("# fastqStatsAndSubsample [version: " + version + "]")
    return version

def sample(step, input, simpleStats, sampleFastq):
    '''
    Alignment step.
    '''
    cmd = '{sampler} -sampleSize={reads} -seed={seed} {input} {outStats} {outSample}'.format( \
          sampler=step.exp.getToolPath('fastqStatsAndSubsample'), \
          reads=step.exp.getSetting('fastqSampleReads','100000'), \
          seed=step.exp.getSetting('fastqSampleSeed', '12345'), \
          input=input, outStats=simpleStats, outSample=sampleFastq)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X")+" 'sampleFastq' begins...")
    step.err = step.exp.runCmd(cmd, log=step.log) # stdout goes to file
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + " 'sampleFastq' " + \
                 "returned " + str(step.err))
    if step.err != 0:
        raise StepError('sampleFastq')

