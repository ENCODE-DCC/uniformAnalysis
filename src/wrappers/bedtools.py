#!/usr/bin/env python2.7
# bedtools.py module holds methods for running bedtools from a LogicalStep.
#
# Settings required: bedtoolsPath (or toolsPath), chromInfoFile

import datetime
from src.logicalstep import StepError

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    # Note: all bedtools should have the same version.
    path = step.exp.getPath('bedtoolsPath',alt='toolsPath')
    version = step.exp.getCmdOut(path + "bedToBam 2>&1 | grep Version | awk '{print $2}'", \
                                 dryRun=False,logCmd=False)
    expected = step.exp.getSetting('bedtoolsVersion',version) # Not in settings then not enforced!
    if step.exp.strict and version != expected:
        raise Exception("Expecting bedtools [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# bedtools [version: " + version + "]")
    return version

def bedToSam(step, bed, sam):
    '''
    Convert Bed to Sam.
    '''
    cmd = '{path}bedToBam -ubam -i {bed} -g {chromInfo} > {sam}'.format( \
          path=step.exp.getPath('bedtoolsPath',alt='toolsPath'), bed=bed, \
          chromInfo=step.exp.getSetting('chromInfoFile'),sam=sam)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'bedtools' bed-to-sam conversion begins...")
    step.err = step.exp.runCmd(cmd, logOut=False, log=step.log)
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'bedtools' bed-to-sam conversion returned " + str(step.err))
    if step.err != 0:
        raise StepError('bedToSam')

