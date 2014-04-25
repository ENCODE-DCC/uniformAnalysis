#!/usr/bin/env python2.7
# samtools.py module holds methods for running samtools from a LogicalStep.
#
# Settings required: samtoolsTool (or toolsDir), hg19ChromInfoFile
# Runs from (in path) tools dir symlink

from src.logicalStep import StepError

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    return step.getToolVersion(toolName, logOut)

def samToBam(step, inSam, outBam):
    '''Sam to Bam converion.'''
    
    cmd = 'samtools view -bt {ref} {input} -o {output}'.format( \
          ref=step.ana.getSetting(step.ana.genome+'ChromInfoFile'), \
          input=inSam, output=outBam)
          
    toolName = __name__.split('.')[-1] + " samToBam"
    step.toolBegins(toolName)
    step.getToolVersion('samtools',logOut=True)

    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)
        
def bamSize(step, bam):
    '''Returns size of a bam.'''
    
    cmd = 'samtools view -c {bam}'.format(bam=bam)
          
    toolName = __name__.split('.')[-1] + " bamSize"
    step.toolBegins(toolName)
    step.getToolVersion('samtools',logOut=True)

    bamSizeStr = step.ana.getCmdOut(cmd, log=step.log)
    
    # no err code returned.  Generate one if return not an integer
    bamSize = 0
    step.err = 0
    if step.ana.dryRun:
        bamSize = 42850405
    else:
        try:
            bamSize = int( bamSizeStr )
        except:
            step.err = -1
    
    step.toolEnds(toolName,bamSize,raiseError=False) # Return was not an error code
    if step.err != 0:
        raise StepError(toolName)
    
    return bamSize

def merge(step, inList, outBam):
    '''Mer bams.'''
    cmd = 'samtools merge -f {output} {inList}'.format(output=outBam, inList=' '.join(inList))
          
    toolName = __name__.split('.')[-1] + " merge"
    step.toolBegins(toolName)
    step.getToolVersion('samtools',logOut=True)

    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)
        
def sort(step, inBam, outBam):
    '''Sorts the bam file so that it can be indexed'''
    #
    # KLUDGE: -f would be the correct option to not have to cut off the filetype, but it does not work correctly in samtools 1.19
    #    and a new version has not been released yet. When the new version of samtools is accepted, we can change this
    #
    cmd = 'samtools sort {inBam} {outBam}'.format(inBam=inBam, outBam=outBam.replace('.bam', ''))
    # Was working as:
    #cmd = 'samtools sort -o {inBam} tmp > {outBam}'.format(inBam=inBam, outBam=outBam)
    toolName = __name__.split('.')[-1] + ' sort'
    step.toolBegins(toolName)
    step.getToolVersion('samtools',logOut=True)

    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName, step.err)
    
def index(step, inBam):
    '''Indexes a sorted bam'''
    cmd = 'samtools index {inBam}'.format(inBam=inBam)
    toolName = __name__.split('.')[-1] + ' index'
    step.toolBegins(toolName)
    step.getToolVersion('samtools',logOut=True)

    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName, step.err)
    
def idxstats(step, inBam, outStats):
    '''Calculates stats for each chromosome in a sorted and indexed bam'''
    cmd = 'samtools idxstats {inBam} > {outStats}'.format(inBam=inBam, outStats=outStats)
    toolName = __name__.split('.')[-1] + ' idxstats'
    step.toolBegins(toolName)
    step.getToolVersion('samtools',logOut=True)

    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName, step.err)

def header(step, inBam, outHeader):
    '''Outputs header of a bam'''
    cmd = 'samtools view -H {inBam} > {outHeader}'.format(inBam=inBam, outHeader=outHeader)
    toolName = __name__.split('.')[-1] + ' header'
    step.toolBegins(toolName)
    step.getToolVersion('samtools',logOut=True)

    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName, step.err)
    
    