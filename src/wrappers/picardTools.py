#!/usr/bin/env python2.7
# picardTools.py module holds methods for running picard-tools from a LogicalStep.
#
# Settings required: javaTool (or must be on env PATH), picardToolsDir (or toolsDir)

##### TODO: Resolve path for java.  

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    javaVersion = step.getToolVersion('java', logOut)
    version = step.getToolVersion(step.ana.toolsDir+'SortSam.jar', logOut)
    return javaVersion+'|'+version

def sortBam(step, sam, bam):
    '''Sorts sam and converts to bam file.'''
    
    cmd = 'java -Xmx5g -XX:ParallelGCThreads=4 -jar {path}SortSam.jar I={input} O={output} SO=coordinate VALIDATION_STRINGENCY=SILENT'.format( \
          path=step.ana.toolsDir, input=sam, output=bam)

    toolName = __name__.split('.')[-1] + " java:sortBam"
    step.toolBegins(toolName)
    step.getToolVersion('java', logOut=True)
    step.getToolVersion(step.ana.toolsDir+'SortSam.jar', logOut=True)

    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)

def fragmentSize(step, inBam, out, pdf):
    '''Calculates the fragment size'''
    
    cmd = 'java -Xmx5g -XX:ParallelGCThreads={threads} -jar {path}CollectInsertSizeMetrics.jar HISTOGRAM_FILE={pdf} I={inBam} O={out} VALIDATION_STRINGENCY=SILENT'.format( \
        threads=4, path=step.ana.toolsDir, pdf=pdf, inBam=inBam, out=out)
    
    toolName = __name__.split('.')[-1] + " java:fragmentSize"
    step.toolBegins(toolName)
    step.getToolVersion('java', logOut=True)
    step.getToolVersion(step.ana.toolsDir+'CollectInsertSizeMetrics.jar', logOut=True)

    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)

def downSample(step, probability, bamIn, bamOut):
    '''Downsamples a bam file'''
    
    cmd = 'java -Xmx5g -XX:ParallelGCThreads=4 -jar {path}DownsampleSam.jar PROBABILITY={fraction} RANDOM_SEED={seed} INPUT={input} OUTPUT={output} VALIDATION_STRINGENCY=SILENT'.format( \
          path=step.ana.toolsDir, \
          fraction=probability, seed=step.ana.getSetting('bamSampleSeed', '12345'), \
          input=bamIn, output=bamOut)
    
    toolName = __name__.split('.')[-1] + " java:downSample"
    step.toolBegins(toolName)
    step.getToolVersion('java', logOut=True)
    step.getToolVersion(step.ana.toolsDir+'DownsampleSam.jar', logOut=True)

    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)
    