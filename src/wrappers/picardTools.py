#!/usr/bin/env python2.7
# picardTools.py module holds methods for running picard-tools from a LogicalStep.
#
# Settings required: javaTool (or must be on env PATH), picardToolsDir (or toolsDir)

##### TODO: Resolve path for java.  

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    javaVersion = step.ana.getCmdOut(step.ana.getTool('java',orInPath=True) + \
                                     " -version 2>&1 | grep version | awk '{print $3}'", \
                                     dryRun=False,logCmd=False)
    if len(javaVersion) and javaVersion[0] == '"':
        javaVersion = javaVersion[ 1:-1 ] # striping quites
    expected = step.ana.getSetting('javaVersion',javaVersion) # Not in settings then not enforced!
    if step.ana.strict and javaVersion != expected:
        raise Exception("Expecting java [version: "+expected+"], " + \
                        "but found [version: "+javaVersion+"]")
    version = step.ana.getCmdOut(step.ana.getTool('java',orInPath=True) + ' -jar ' + \
                                 step.ana.getDir(toolName+'Dir',alt='toolsDir') + \
                                 'SortSam.jar --version', dryRun=False,logCmd=False,errOk=True)
    expected = step.ana.getSetting(toolName+'Version',version)# Not in settings then not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting "+toolName+" samSort [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# "+toolName+" samSort [version: " + version + 
                     "] running on java [version: " + javaVersion + "]")
    return version

def sortBam(step, sam, bam):
    '''Sorts sam and converts to bam file.'''
    
    cmd = '{java} -Xmx5g -XX:ParallelGCThreads=4 -jar {picard}SortSam.jar I={input} O={output} SO=coordinate VALIDATION_STRINGENCY=SILENT'.format( \
          java=step.ana.getTool('java',orInPath=True), \
          picard=step.ana.getDir('picardToolsDir',alt='toolsDir'), input=sam, output=bam)

    toolName = __name__.split('.')[-1] + " java:sortBam"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)

def fragmentSize(step):
    '''Calculates the fragment size'''
    
    cmd = '{java} -Xmx5g -XX:ParallelGCThreads={threads} -jar {picard}Frag {param[insertsize]} HISTOGRAM_FILE={output[pdf]} I={input[bam]} O={output[insert]} VALIDATION_STRINGENCY=SILENT'
    
    toolName = __name__.split('.')[-1] + " java:fragmentSize"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)

def downSample(step, probability, bamIn, bamOut):
    '''Downsamples a bam file'''
    
    cmd = '{java} -Xmx5g -XX:ParallelGCThreads=4 -jar {picard}DownsampleSam.jar PROBABILITY={fraction} RANDOM_SEED={seed} INPUT={input} OUTPUT={output} VALIDATION_STRINGENCY=SILENT'.format( \
          java=step.ana.getTool('java',orInPath=True), \
          picard=step.ana.getDir('picardToolsDir',alt='toolsDir'), \
          fraction=probability, seed=step.ana.getSetting('bamSampleSeed', '12345'), \
          input=bamIn, output=bamOut)
    
    toolName = __name__.split('.')[-1] + " java:downSample"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)
    