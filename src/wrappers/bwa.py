#!/usr/bin/env python2.7
# bwa.py module holds methods for running bwa from a LogicalStep.
# It performs bwa alignment on single or paired end reads.
#
# toolsDir must be in path and 'eap' bash scripts must be in toolsDir. 
# Settings required: bwaTool (or toolsDir), hg19AssemblyFile, bwaVersion.
# Runs from (in path) tools dir symlink

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    return step.getToolVersion(toolName, logOut)

def aln(step, fastq, outSai):
    '''Alignment step.'''
    
    cmd = 'bwa aln -t {threads} {ref} {input} > {output}'.format( \
          threads=4, ref=step.ana.getSetting(step.ana.genome +'AssemblyFile'), \
          input=fastq, output=outSai)
          
    toolName = __name__.split('.')[-1] + " aln"
    step.toolBegins(toolName)
    step.getToolVersion('bwa',logOut=True)
    
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)
        
def sampe(step, sai1, fastq1, sai2, fastq2, outSam):
    '''Paired end sam generation'''
    
    cmd = 'bwa sampe {ref} {sai1} {sai2} {fastq1} {fq2} > {output}'.format( \
          ref=step.ana.getSetting(step.ana.genome +'AssemblyFile'), \
          sai1=sai1, fastq1=fastq1, sai2=sai2, fq2=fastq2, output=outSam)
          
    toolName = __name__.split('.')[-1] + " sampe"
    step.toolBegins(toolName)
    step.getToolVersion('bwa',logOut=True)
    
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)
    
def samse(step, sai, fastq, outSam):
    '''Unpaired (single end) sam generation'''
    
    cmd = 'bwa samse {ref} {sai} {fastq} > {output}'.format( \
          ref=step.ana.getSetting(step.ana.genome +'AssemblyFile'), \
          sai=sai, fastq=fastq, output=outSam)
          
    toolName = __name__.split('.')[-1] + " samse"
    step.toolBegins(toolName)
    step.getToolVersion('bwa',logOut=True)
    
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)

def eap_se(step, fastq, outBam):
    '''Single end bam generation'''
    
    # Using bash scripts to run bwa single-end on sanger style fastq
    # usage v3: eap_run_bwa_se bwa-index reads.fq out.bam
    cmd = "eap_run_bwa_se {ref} {fq} {output}".format( \
          ref=step.ana.getSetting(step.ana.genome +'AssemblyFile'), \
          fq=fastq, output=outBam)
          
    toolName = 'eap_run_bwa_se'
    step.toolBegins(toolName)
    step.getToolVersion(toolName,logOut=True)
    step.getToolVersion('bwa',logOut=True)
    step.getToolVersion('samtools',logOut=True)
    
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)

def eap_pe(step, fastq1, fastq2, outBam):
    '''Paired end bam generation'''
    
    # Using bash scripts to run bwa paired-end on sanger style fastqs
    # usage v4: eap_run_bwa_pe bwa-index read1.fq read2.fq out.bam
    cmd = "eap_run_bwa_pe {ref} {fq1} {fq2} {output}".format( \
          ref=step.ana.getSetting(step.ana.genome +'AssemblyFile'), \
          fq1=fastq1, fq2=fastq2, output=outBam)
          
    toolName = 'eap_run_bwa_pe'
    step.toolBegins(toolName)
    step.getToolVersion(toolName,logOut=True)
    step.getToolVersion('bwa',logOut=True)
    step.getToolVersion('samtools',logOut=True)
    
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)

def eap_slx_se(step, solexaFq, outBam):
    '''Single end bam generation'''
    
    # Using bash scripts to run bwa single-end on solexa style fastq
    # usage v1: eap_run_slx_bwa_se bwa-index solexa-reads.fq out.bam
    cmd = "eap_run_slx_bwa_se {ref} {fq} {output}".format( \
          ref=step.ana.getSetting(step.ana.genome +'AssemblyFile'), \
          fq=solexaFq, output=outBam)
          
    toolName = 'eap_run_slx_bwa_se'
    step.toolBegins(toolName)
    step.getToolVersion(toolName,logOut=True)
    step.getToolVersion('bwa',logOut=True)
    step.getToolVersion('samtools',logOut=True)
    step.getToolVersion('edwSolexaToSangerFastq',logOut=True)
    
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)

def eap_slx_pe(step, solexaFq1, solexaFq2, outBam):
    '''Paired end bam generation'''
    
    # Using bash scripts to run bwa paired-end on solexa style fastqs
    # usage v3: eap_run_slx_bwa_pe bwa-index solexa1.fq solexa2.fq out.bam
    cmd = "eap_run_slx_bwa_pe {ref} {fq1} {fq2} {output}".format( \
          ref=step.ana.getSetting(step.ana.genome +'AssemblyFile'), \
          fq1=solexaFq1, fq2=solexaFq2, output=outBam)
          
    toolName = 'eap_run_slx_bwa_pe'
    step.toolBegins(toolName)
    step.getToolVersion(toolName,logOut=True)
    step.getToolVersion('bwa',logOut=True)
    step.getToolVersion('samtools',logOut=True)
    step.getToolVersion('edwSolexaToSangerFastq',logOut=True)
    
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)
    
