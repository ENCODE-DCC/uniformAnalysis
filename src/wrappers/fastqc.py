#!/usr/bin/env python2.7
# fastqc.py module holds methods for running fastqc from a LogicalStep.
# It creates an HTML report of fastq validation info.
#
# Settings required: fastqcTool (or toolsDir)

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    version = step.ana.getCmdOut(step.ana.getTool(toolName) + " -version | awk '{print $2}'", \
                                 dryRun=False,logCmd=False)
    expected = step.ana.getSetting(toolName+'Version',version) # Not in settings: not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting "+toolName+" [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# "+toolName+" validation [version: " + version + "]")
    return version

def validate(step, inFastq, outDir):
    '''Validation'''
    
    cmd = '{fastqc} {fastq} --extract -q'.format( \
          fastqc=step.ana.getTool('fastqc'), fastq=inFastq)

    toolName = __name__.split('.')[-1] + " validate"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)
