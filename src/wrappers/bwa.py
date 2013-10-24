#!/usr/bin/env python2.7
# bwa.py module holds methods for running bwa from a LogicalStep.
# It performs bwa alignment on single or paired end reads.
#
# Settings required: bwaTool (or toolsDir), hg19AssemblyFile, bwaVersion

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    version = step.ana.getCmdOut(step.ana.getTool(toolName)+' 2>&1 | grep Version',\
                                 dryRun=False,logCmd=False)
    version = version[ len('Version: '): ]  # Clip off the version label
    expected = step.ana.getSetting(toolName+'Version',version) # Not in settings then not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting "+toolName+" alignment [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# "+toolName+" alignment [version: " + version + "]")
    return version

def aln(step, fastq, outSai):
    '''Alignment step.'''
    
    cmd = '{bwa} aln -t {threads} {ref} {input} > {output}'.format( \
          bwa=step.ana.getTool('bwa'), threads=4, \
          ref=step.ana.getSetting(step.ana.genome +'AssemblyFile'), \
          input=fastq, output=outSai)
          
    toolName = __name__.split('.')[-1] + " aln"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)
        
def sampe(step, sai1, fastq1, sai2, fastq2, outSam):
    '''Paired end sam generation'''
    
    cmd = '{bwa} sampe {ref} {sai1} {sai2} {fastq1} {fq2} > {output}'.format( \
          bwa=step.ana.getTool('bwa'), ref=step.ana.getSetting(step.ana.genome +'AssemblyFile'), \
          sai1=sai1, fastq1=fastq1, sai2=sai2, fq2=fastq2, output=outSam)
          
    toolName = __name__.split('.')[-1] + " sampe"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)
    
def samse(step, sai, fastq, outSam):
    '''Unpaired (single end) sam generation'''
    
    cmd = '{bwa} samse {ref} {sai} {fastq} > {output}'.format( \
          bwa=step.ana.getTool('bwa'), ref=step.ana.getSetting(step.ana.genome +'AssemblyFile'), \
          sai=sai, fastq=fastq, output=outSam)
          
    toolName = __name__.split('.')[-1] + " samse"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)

