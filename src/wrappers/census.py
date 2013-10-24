#!/usr/bin/env python2.7
# census.py module holds methods for running python census scripts from a LogicalStep.
#
# Settings required: censusDir (or toolsDir), pythonTool (or toolsDir)

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    pyVersion = step.ana.getCmdOut(step.ana.getTool('python') + " -V 2>&1 | awk '{print $2}'", \
                                   dryRun=False,logCmd=False)
    expected = step.ana.getSetting('pythonVersion',pyVersion) # Not in settings: not enforced!
    if step.ana.strict and pyVersion != expected:
        raise Exception("Expecting python [version: "+expected+"], " + \
                        "but found [version: "+pyVersion+"]")
    version = step.ana.getCmdOut(step.ana.getTool('python') + ' ' + \
                                 step.ana.getDir(toolName+'Dir',alt='toolsDir') + \
                                 "bam_to_histo.py -v 2>&1 | awk '{print $1}'", \
                                 dryRun=False,logCmd=False)
    expected = step.ana.getSetting(toolName+'Version',version)
    if step.ana.strict and version != expected:
        raise Exception("Expecting "+toolName+" [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# "+toolName+" [version: " + version + \
                     "] running on python [version: " + pyVersion + "]")
    return version

def metrics(step, bam, metrics):
    '''Generates metrics histogram from bam.'''
    singleFlag = ''
    if step.ana.readType == 'single':
        singleFlag = ' --single_ended'
    
    # TODO: Using dummy.bed for test data, need to switch back to using the real one!
    cmd = '{python} {censusPath}bam_to_histo.py{flags} {censusPath}dummy.bed {input} | {python} {censusPath}calculate_libsize.py - > {output}'.format( \
          python=step.ana.getTool('python'), flags=singleFlag, \
          censusPath=step.ana.getDir('censusDir',alt='toolsDir'), \
          samSortJar=step.ana.getTool('samSortJar'), input=bam, output=metrics)

    toolName = __name__.split('.')[-1] + " python:metrics"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)

