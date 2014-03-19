#!/usr/bin/env python2.7
# fastqc.py module holds methods for running fastqc from a LogicalStep.
# It creates an HTML report of fastq validation info.
#
# Settings required: fastqcTool (or toolsDir)
# Runs from (in path) tools dir symlink

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    return step.getToolVersion(toolName, logOut)

def validate(step, inFastq, outDir):
    '''Validation'''
    
    cmd = 'fastqc {fastq} --extract -q'.format( fastq=inFastq )

    toolName = __name__.split('.')[-1] + " validate"
    step.toolBegins(toolName)
    step.getToolVersion('fastqc', logOut=True)

    step.err = step.ana.runCmd(cmd, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)
