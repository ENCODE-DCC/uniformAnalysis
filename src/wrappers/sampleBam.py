#!/usr/bin/env python2.7
# sampleBam.py module holds methods for running sampleBam from 
# a LogicalStep.  It is used to sample a fastq.
#
# Settings required: sampleBamPath

import datetime
from src.logicalStep import StepError

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    #version = step.ana.getCmdOut(step.ana.getToolPath('sampleBam') + \
    #                             " -version | awk '{print $2}'",dryRun=False,logCmd=False)
    version = "unknown"  # Sorry, this tool has no version.
    #expected = step.ana.getSetting('sampleBam',version) # Not in settings then not enforced!
    #if step.ana.strict and version != expected:
    #    raise Exception("Expecting sampleBam [version: "+expected+"], " + \
    #                    "but found [version: "+version+"]")
    if logOut:
        step.log.out("# sampleBam [version: " + version + "]")
    return version

def sample(step, bam, bamSize, sampleSize, samSample):
    '''
    Alignment step.
    '''
    cmd = '{sampler} {input} {inSize} {outSize} {output}'.format( \
          sampler=step.ana.getToolPath('sampleBam'), input=bam, \
          inSize=str(bamSize), outSize=str(sampleSize), output=samSample)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X")+" 'sampleBam' begins...")
    step.err = step.ana.runCmd(cmd, log=step.log) # stdout goes to file
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + " 'sampleBam' " + \
                 "returned " + str(step.err))
    if step.err != 0:
        raise StepError('sampleBam')

