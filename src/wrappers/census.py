#!/usr/bin/env python2.7
# census.py module holds methods for running python census scripts from a LogicalStep.
#
# Settings required: censusDir (or toolsDir), pythonTool (or toolsDir)

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    pyVersion = step.getToolVersion('python2.7', logOut)
    version = step.getToolVersion('bam_to_histo.py', logOut)
    return pyVersion+'|'+version

def metrics(step, bam, metrics):
    '''Generates metrics histogram from bam.'''
    singleFlag = ''
    if step.ana.readType == 'single':
        singleFlag = ' --single_ended'
    
    # TODO: Using dummy.bed for test data, need to switch back to using the real one!
    cmd = 'python2.7 {censusPath}bam_to_histo.py{flags} {censusPath}dummy.bed {input} | python2.7 {censusPath}calculate_libsize.py - > {output}'.format( \
          censusPath=step.ana.getDir('censusDir',alt='toolsDir'), flags=singleFlag, \
          input=bam, output=metrics)


    toolName = __name__.split('.')[-1] + " python:metrics"
    step.toolBegins(toolName)
    step.getToolVersion('python2.7', logOut=True)
    step.getToolVersion('bam_to_histo.py', logOut=True)

    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)

