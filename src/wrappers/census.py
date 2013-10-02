#!/usr/bin/env python2.7
# census.py module holds methods for running python census scripts from a LogicalStep.
#
# Settings required: censusPath (or toolsPath), pythonPath (or toolsPath)

import datetime
from src.logicalstep import StepError

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    pyVersion = step.exp.getCmdOut(step.exp.getToolPath('python') + " -V 2>&1 | awk '{print $2}'", \
                                       dryRun=False,logCmd=False)
    expected = step.exp.getSetting('pythonVersion',pyVersion) # Not in settings then not enforced!
    if step.exp.strict and pyVersion != expected:
        raise Exception("Expecting python [version: "+expected+"], " + \
                        "but found [version: "+pyVersion+"]")
    version = step.exp.getCmdOut(step.exp.getToolPath('python') + ' ' + \
                                       step.exp.getPath('censusPath',alt='toolPath') + \
                                       "bam_to_histo.py -v 2>&1 | awk '{print $1}'", \
                                       dryRun=False,logCmd=False)
    expected = step.exp.getSetting('censusVersion',version) # Not in settings then not enforced!
    if step.exp.strict and version != expected:
        raise Exception("Expecting census [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# census [version: " + version + \
                     "] running on python [version: " + pyVersion + "]")
    return version

def metrics(step, bam, metrics):
    '''
    Generates metrics histogram from bam.
    '''
    cmd = '{python} {censusPath}bam_to_histo.py {censusPath}seq.cov005.ONHG19.bed {input} | {python} {censusPath}calculate_libsize.py - > {output}'.format( \
          python=step.exp.getToolPath('python'), \
          censusPath=step.exp.getPath('censusPath',alt='toolPath'), \
          samSortJar=step.exp.getSetting('samSortJarFile'), \
          input=bam, output=metrics)

    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'python' census metrics begins...")
    step.err = step.exp.runCmd(cmd, log=step.log)
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'python' census metrics returned " + str(step.err))
    if step.err != 0:
        raise StepError('census')

