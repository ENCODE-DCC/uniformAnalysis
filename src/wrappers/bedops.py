#!/usr/bin/env python2.7
# bedops.py module holds methods for running bedops utilities from a LogicalStep.
#
# Settings required: bedopsDir (or toolsDir)

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    # Note: all bedtools should have the same version.
    toolName = __name__.split('.')[-1]
    path = step.ana.getDir(toolName+'Dir',alt='toolsDir')
    version = step.ana.getCmdOut(path + "bedops --version 2>&1 | grep version | awk '{print $2}'", \
                                 dryRun=False,logCmd=False)
    expected = step.ana.getSetting(toolName+'Version',version) # Not in settings: not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting "+toolName+" [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# "+toolName+" [version: " + version + "]")
    return version

def unstarch(step, inStarched, outUnstarched):
    '''unstarch (uncompress) a file.'''
    
    cmd = '{path}unstarch {starched} > {unstarched}'.format( \
          path=step.ana.getDir('bedopsDir',alt='toolsDir'), starched=inStarched, \
          unstarched=outUnstarched)
          
    toolName = __name__.split('.')[-1] + " unstatch"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)
