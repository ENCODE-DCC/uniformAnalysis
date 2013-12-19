#!/usr/bin/env python2.7
# ucscUtils.py module holds methods for running various utilities from the kent/src tree in
# a LogicalStep.
#
# Settings required: fastqStatsAndSubsampleTool (or toolsDir), fastqSampleReads, fastqSampleSeed,
#                    bedGraphToBigWigTool (or toolsDir), hg19ChromInfoFile
#                    sampleBamTool (or toolsDir), hg19ChromInfoFile

def version(step, logOut=True, tool=None):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    if tool != None:
        toolName = tool
    version = "unversioned"  # Sorry, this tool has no version.
    if toolName == 'bedGraphToBigWig':
        version = step.ana.getCmdOut(step.ana.getTool(toolName) + \
                                 '  2>&1 | grep "'+toolName+' v"' + " | awk '{print $3}'",
                                 dryRun=False,logCmd=False)
        expected = step.ana.getSetting(toolName+'Version',version) # Not in settings: not enforced!
        if step.ana.strict and version != expected:
            raise Exception("Expecting "+toolName+" [version: "+expected+"], " + \
                            "but found [version: "+version+"]")

    if logOut:
        step.log.out("# "+toolName+" [version: " + version + "]")
    return version

def bedGraphToBigWig(step, inBedGraph, outBigWig):
    '''Converts a bedGraph to a bigWig.'''
    
        # "bedGraphToBigWig input.tmp chromLengths output.bigWig"
    cmd = '{tool} {bedGraph} {chromInfo} {bigWig}'.format( \
          tool=step.ana.getTool('bedGraphToBigWig'), bedGraph=inBedGraph, \
          chromInfo=step.ana.getSetting(step.ana.genome+'ChromInfoFile'), \
          bigWig=outBigWig)
          
    toolName = __name__.split('.')[-1] + " bedGraphToBigWig"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)

def fastqStatsAndSubsample(step, inFastq, simpleStats, sampleFastq):
    '''Sample a fastq.'''
    
    cmd = '{tool} -sampleSize={reads} -seed={seed} {input} {outStats} {outSample}'.format( \
          tool=step.ana.getTool('fastqStatsAndSubsample'), \
          reads='{sample}',seed=step.ana.getSetting('fastqSampleSeed', '12345'), \
          input=inFastq, outStats=simpleStats, outSample=sampleFastq)
    
    sampleSize = int( step.ana.getSetting('fastqSampleReads','100000') )
      
    toolName = __name__.split('.')[-1] + ' fastqStatsAndSubsample'
    step.toolBegins(toolName)
    
    #step.err = step.ana.runCmd(cmd, log=step.log) # stdout goes to file
    while sampleSize >= 40000:
        step.err = step.ana.runCmd(cmd.format(sample=sampleSize), log=step.log)
        if step.err != 65280: # size error
            break;
        sampleSize = sampleSize - 15000
        
    step.toolEnds(toolName,step.err)

def sampleBam(step, bam, bamSize, sampleSize, samSample):
    '''Samples a bam file.'''
    
    # BUGBUG sampleBam not working on paired reads!  Replacing with picard DownSampleSam
    # Is this really a ucscUtil???  Yes: src/hg/encode3/encPipe/sampleBam
    cmd = '{sampler} {input} {inSize} {outSize} {output}'.format( \
          sampler=step.ana.getTool('sampleBam'), input=bam, \
          inSize=str(bamSize), outSize=str(sampleSize), output=samSample)
          
    toolName = __name__.split('.')[-1] + ' sampleBam'
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)
