#!/usr/bin/env python2.7
# bedops.py module holds methods for running bedops utilities from a LogicalStep.
#
# Settings required: bedopsDir (or toolsDir)
# Runs from (in path) tools dir symlink

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    # Note: all bedtools should have the same version.
    toolName = __name__.split('.')[-1]
    return step.getToolVersion(toolName, logOut)

def unstarch(step, inStarched, outUnstarched):
    '''unstarch (uncompress) a file.'''
    
    cmd = 'unstarch {starched} > {unstarched}'.format( \
          starched=inStarched, unstarched=outUnstarched)
          
    toolName = __name__.split('.')[-1] + " unstatch"
    step.toolBegins(toolName)
    step.getToolVersion('unstarch', logOut=True)
    
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)
