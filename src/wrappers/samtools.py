#!/usr/bin/env python2.7
# samtools.py module holds methods for running samtools from a LogicalStep.
#
# Settings required: samtoolsTool (or toolsDir), chromInfoFile

import datetime
from src.logicalStep import StepError

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    version = step.ana.getCmdOut(step.ana.getTool('samtools')+' 2>&1 | grep Version', \
                                 dryRun=False,logCmd=False)
    version = version[ len('Version: '): ]  # Clip off the version label
    expected = step.ana.getSetting('samtoolsVersion',version) # Not in settings then not enforced!
    if step.ana.strict and version != expected:
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
          samtools=step.ana.getTool('samtools'), ref=step.ana.getSetting('chromInfoFile'), \
          input=input, output=output)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'samtools' sam-to-bam conversion begins...")
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'samtools' sam-to-bam conversion returned " + str(step.err))
    if step.err != 0:
        raise StepError('aln')
        
def bamSize(step, bam):
    '''
    Returns size of a bam.
    '''
    cmd = '{samtools} view -c {bam}'.format( samtools=step.ana.getTool('samtools'), bam=bam)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'samtools' bam size begins...")
    bamSizeStr = step.ana.getCmdOut(cmd, log=step.log)
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'samtools' bam size returned " + bamSizeStr)
    # TODO: no err code returned.  Use try?
    #if step.err != 0:
    #    raise StepError('aln')
    try:
        return int( bamSizeStr )
    except:
        if step.ana.dryRun():
            return 42850405
        raise StepError('bamSize')


