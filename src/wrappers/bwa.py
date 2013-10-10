#!/usr/bin/env python2.7
# bwa.py module holds methods for running bwa from a LogicalStep.
# It performs bwa alignment on single or paired end reads.
#
# Settings required: bwaTool (or toolsDir), dbAssemblyFile, bwaVersion

import datetime
from src.logicalStep import StepError

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    version = step.ana.getCmdOut(step.ana.getTool('bwa')+' 2>&1 | grep Version',\
                                 dryRun=False,logCmd=False)
    version = version[ len('Version: '): ]  # Clip off the version label
    expected = step.ana.getSetting('bwaVersion',version) # Not in settings then not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting bwa alignment [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# bwa alignment [version: " + version + "]")
    return version

def aln(step, input, output):
    '''
    Alignment step.
    '''
    cmd = '{bwa} aln -t {threads} {ref} {input} > {output}'.format( \
          bwa=step.ana.getTool('bwa'), threads=4, \
          ref=step.ana.getSetting('dbAssemblyFile'), \
          input=input, output=output)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X")+" 'bwa aln' begins...")
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log) # stdout goes to file
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + " 'bwa aln' " + \
                 "returned " + str(step.err))
    if step.err != 0:
        raise StepError('aln')
        
def sampe(step, sai1, fastq1, sai2, fastq2, output):
    '''
    Paired end sam generation
    '''
    cmd = '{bwa} sampe {ref} {sai1} {sai2} {fastq1} {fq2} > {output}'.format( \
          bwa=step.ana.getTool('bwa'), ref=step.ana.getSetting('dbAssemblyFile'), \
          sai1=sai1, fastq1=fastq1, sai2=sai2, fq2=fastq2, output=output)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X")+" 'bwa sampe' begins...")
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log) # stdout goes to file
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + " 'bwa sampe' " + \
                 "returned " + str(step.err))
    if step.err != 0:
        raise StepError('sampe')
    
def samse(step, sai, fastq, output):
    '''
    Unpaired (single end) sam generation
    '''
    cmd = '{bwa} samse {ref} {sai} {fastq} > {output}'.format( \
          bwa=step.ana.getTool('bwa'), ref=step.ana.getSetting('dbAssemblyFile'), \
          sai=sai, fastq=fastq, output=output)
          
    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X")+" 'bwa samse' begins...")
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log) # stdout goes to file
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + " 'bwa samse' " + \
                 "returned " + str(step.err))
    if step.err != 0:
        raise StepError('samse')

