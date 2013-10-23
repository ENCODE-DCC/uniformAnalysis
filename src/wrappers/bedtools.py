#!/usr/bin/env python2.7
# bedtools.py module holds methods for running bedtools from a LogicalStep.
#
# Settings required: bedtoolsDir (or toolsDir), hg19ChromInfoFile

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    # Note: all bedtools should have the same version.
    path = step.ana.getDir('bedtoolsDir',alt='toolsDir')
    version = step.ana.getCmdOut(path + "bedToBam 2>&1 | grep Version | awk '{print $2}'", \
                                 dryRun=False,logCmd=False)
    expected = step.ana.getSetting('bedtoolsVersion',version) # Not in settings: not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting bedtools [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# bedtools [version: " + version + "]")
    return version

def bedToBam(step, bed, bam):
    '''
    Convert Bed to Bam.
    '''
    cmd = '{path}bedToBam -i {bed} -g {chromInfo} > {bam}'.format( \
          path=step.ana.getDir('bedtoolsDir',alt='toolsDir'), bed=bed, \
          chromInfo=step.ana.getSetting(step.ana.genome+'ChromInfoFile'),bam=bam)
          
    toolName = __name__ + " bedToBam"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)
