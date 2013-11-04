#!/usr/bin/env python2.7
# samtools.py module holds methods for running samtools from a LogicalStep.
#
# Settings required: samtoolsTool (or toolsDir), hg19ChromInfoFile

from src.logicalStep import StepError

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    version = step.ana.getCmdOut(step.ana.getTool(toolName)+' 2>&1 | grep Version', \
                                 dryRun=False,logCmd=False)
    version = version[ len('Version: '): ]  # Clip off the version label
    expected = step.ana.getSetting(toolName+'Version',version) # Not in settings then not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting "+toolName+" [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# "+toolName+" [version:" + version + "]")
    return version

def samToBam(step, inSam, outBam):
    '''Alignment step.'''
    
    cmd = '{samtools} view -bt {ref} {input} -o {output}'.format( \
          samtools=step.ana.getTool('samtools'), \
          ref=step.ana.getSetting(step.ana.genome+'ChromInfoFile'), \
          input=inSam, output=outBam)
          
    toolName = __name__.split('.')[-1] + " samToBam"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)
        
def bamSize(step, bam):
    '''Returns size of a bam.'''
    
    cmd = '{samtools} view -c {bam}'.format( samtools=step.ana.getTool('samtools'), bam=bam)
          
    toolName = __name__.split('.')[-1] + " bamSize"
    step.toolBegins(toolName)
    bamSizeStr = step.ana.getCmdOut(cmd, log=step.log)
    
    # no err code returned.  Generate one if return not an integer
    bamSize = 0
    try:
        bamSize = int( bamSizeStr )
    except:
        if step.ana.dryRun():
            bamSize = 42850405
        step.err = -1
    
    step.toolEnds(toolName,bamSize,raiseError=False) # Return was not an error code
    if step.err != 0:
        raise StepError(toolName)
    
    return bamSize
