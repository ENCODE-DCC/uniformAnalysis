#!/usr/bin/env python2.7
# fastqStatsAndSubsample.py module holds methods for running fastqStatsAndSubsample from 
# a LogicalStep.  It is used to sample a fastq.
#
# Settings required: fastqStatsAndSubsampleTool (or toolsDir), fastqSampleReads, fastqSampleSeed

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    #version = step.ana.getCmdOut(step.ana.getTool(toolName) + \
    #                             " -version | awk '{print $2}'",dryRun=False,logCmd=False)
    version = "unversioned"  # Sorry, this tool has no version.
    #expected = step.ana.getSetting(toolName+'Version',version) # Not in settings: not enforced!
    #if step.ana.strict and version != expected:
    #    raise Exception("Expecting "+toolName+" [version: "+expected+"], " + \
    #                    "but found [version: "+version+"]")
    if logOut:
        step.log.out("# "+toolName+" [version: " + version + "]")
    return version

def sample(step, inFastq, simpleStats, sampleFastq):
    '''Alignment step.'''
    
    cmd = '{sampler} -sampleSize={reads} -seed={seed} {input} {outStats} {outSample}'.format( \
          sampler=step.ana.getTool('fastqStatsAndSubsample'), \
          reads='{sample}',seed=step.ana.getSetting('fastqSampleSeed', '12345'), \
          input=inFastq, outStats=simpleStats, outSample=sampleFastq)
    
    sampleSize = int( step.ana.getSetting('fastqSampleReads','100000') )
      
    toolName = __name__.split('.')[-1]
    step.toolBegins(toolName)
    
    #step.err = step.ana.runCmd(cmd, log=step.log) # stdout goes to file
    while sampleSize >= 40000:
        step.err = step.ana.runCmd(cmd.format(sample=sampleSize), log=step.log)
        if step.err != 65280: # size error
            break;
        sampleSize = sampleSize - 15000
        
    step.toolEnds(toolName,step.err)

