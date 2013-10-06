#!/usr/bin/env python2.7
# bedtools.py module holds methods for running bedtools from a LogicalStep.
#
# Settings required: bedtoolsPath (or toolsPath), chromInfoFile

import datetime
from src.logicalStep import StepError

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    # Note: all bedtools should have the same version.
    path = step.ana.getToolPath('bedtools')
    version = step.ana.getCmdOut(path + " bedtobam 2>&1 | grep Version | awk '{print $2}'", \
                                 dryRun=False,logCmd=False)
    expected = step.ana.getSetting('bedtoolsVersion',version) # Not in settings: not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting bedtools [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# bedtools [version: " + version + "]")
    return version

def bedToSam(step, bed, sam):
    '''
    Convert Bed to Sam.
    '''
    cmd = '{path} bedtobam -ubam -i {bed} -g {chromInfo} > {sam}'.format( \
          path=step.ana.getToolPath('bedtools'), bed=bed, \
          chromInfo=step.ana.getSetting('chromInfoFile'),sam=sam)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'bedtools' bed-to-sam conversion begins...")
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'bedtools' bed-to-sam conversion returned " + str(step.err))
    if step.err != 0:
        raise StepError('bedToSam')

