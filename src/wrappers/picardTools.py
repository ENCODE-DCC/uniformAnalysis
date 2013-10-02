#!/usr/bin/env python2.7
# picardTools.py module holds methods for running picard-tools from a LogicalStep.
#
# Settings required: javaPath (or toolsPath), picardToolsPath (or toolsPath)

##### TODO: Resolve path for java.  

import datetime
from src.logicalStep import StepError

def version(step, logOut=True):
    '''
    Returns tool version.  Will log to stepLog unless requested not to.
    '''
    javaVersion = step.ana.getCmdOut(step.ana.getPath('javaPath','') + \
                                     "java -version 2>&1 | grep version | awk '{print $3}'", \
                                     dryRun=False,logCmd=False)
    if len(javaVersion) and javaVersion[0] == '"':
        javaVersion = javaVersion[ 1:-1] # striping quites
    expected = step.ana.getSetting('javaVersion',javaVersion) # Not in settings then not enforced!
    if step.ana.strict and javaVersion != expected:
        raise Exception("Expecting java [version: "+expected+"], " + \
                        "but found [version: "+javaVersion+"]")
    version = step.ana.getCmdOut(step.ana.getPath('javaPath','') + 'java -jar ' + \
                                 step.ana.getSetting('samSortJarFile') + ' --version', \
                                 dryRun=False,logCmd=False,errOk=True)
    expected = step.ana.getSetting('picardToolsVersion',version)# Not in settings then not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting java [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# picard-tools samSort [version: " + version + 
                     "] running on java [version: " + javaVersion + "]")
    return version

def samSortToBam(step, sam, bam):
    '''
    Sorts sam and converts to bam file.
    '''
    cmd = '{javaPath}java -Xmx5g -XX:ParallelGCThreads=4 -jar {samSortJar} I={input} O={output} SO=coordinate VALIDATION_STRINGENCY=SILENT'.format( \
          javaPath=step.ana.getPath('javaPath',''), \
          samSortJar=step.ana.getSetting('samSortJarFile'), \
          input=sam, output=bam)

    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'java' samSortToBam begins...")
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + \
                 " 'java' samSortToBam returned " + str(step.err))
    if step.err != 0:
        raise StepError('samSortToBam')

