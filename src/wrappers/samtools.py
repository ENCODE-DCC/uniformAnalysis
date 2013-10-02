#!/usr/bin/env python2.7
# samtools.py module holds methods for running samtools from a LogicalStep.
#
# Settings required: samtoolsPath (or toolsPath), chromInfoFile, samtoolsVersion
#
# Each granular function will add to the step.log: the start and stop time and the complete
# command line run.  Additionally, the logical styep should include the version() call
# placing the version in the step.log as well. Example log output:
#
# # samtools [version 0.1.19-44428cd]:
# 
# # 2013-09-18 12:07:30 'samtools view' begins...
# > samtools view -bt {ref} {input} -o {output}
# ... {samtools command stderr output}
# # 2013-09-18 12:30:03 'samtools view' returned 0

import datetime
from src.logicalstep import StepError

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    version = step.exp.getCmdOut(step.exp.getToolPath('samtools')+' 2>&1 | grep Version', \
                                 dryRun=False,logCmd=False)
    version = version[ len('Version: '): ]  # Clip off the version label
    expected = step.exp.getSetting('samtoolsVersion',version) # Not in settings then not enforced!
    if step.exp.strict and version != expected:
        raise Exception("Expecting samtools [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# samtools [version:" + version + "]")
    return version

def samToBam(step, input, output):
    '''
    Alignment step.
    '''
    cmd = '{samtools} view -bt {ref} {input} -o {output}'.format( \
          samtools=step.exp.getToolPath('samtools'), ref=step.exp.getSetting('chromInfoFile'), \
          input=input, output=output)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'samtools' sam-to-bam conversion begins...")
    step.err = step.exp.runCmd(cmd, log=step.log)
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'samtools' sam-to-bam conversion returned " + str(step.err))
    if step.err != 0:
        raise StepError('aln')
        
def bamSize(step, bam):
    '''
    Returns size of a bam.
    '''
    cmd = '{samtools} view -c {bam}'.format( samtools=step.exp.getToolPath('samtools'), bam=bam)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'samtools' bam size begins...")
    bamSizeStr = step.exp.getCmdOut(cmd, log=step.log)
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'samtools' bam size returned " + bamSizeStr)
    # TODO: no err code returned.  Use try?
    #if step.err != 0:
    #    raise StepError('aln')
    try:
        return int( bamSizeStr )
    except:
        if step.exp.dryRun():
            return 42850405
        raise StepError('bamSize')


