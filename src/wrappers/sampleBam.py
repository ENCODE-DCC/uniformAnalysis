#!/usr/bin/env python2.7
# sampleBam.py module holds methods for running sampleBam from 
# a LogicalStep.  It is used to sample a fastq.
#
# Settings required: sampleBamTool (or toolsDir)

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    #version = step.ana.getCmdOut(step.ana.getTool('sampleBam') + \
    #                             " -version | awk '{print $2}'",dryRun=False,logCmd=False)
    version = "unversioned"  # Sorry, this tool has no version.
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
          sampler=step.ana.getTool('sampleBam'), input=bam, \
          inSize=str(bamSize), outSize=str(sampleSize), output=samSample)
          
    toolName = __name__
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)
