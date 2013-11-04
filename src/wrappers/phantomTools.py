#!/usr/bin/env python2.7
# phantomTools.py module holds methods for running R phantomTools scripts from a LogicalStep.
#
# Settings required: phantomToolDir (or toolsDir), RscriptTool (or Rscript must be on env PATH)

##### TODO: Resolve path for Rscript. 

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    toolName = __name__.split('.')[-1]
    rVersion = step.ana.getCmdOut(step.ana.getTool('Rscript',orInPath=True) + \
                                  "Rscript --version 2>&1 | awk '{print $5}'", \
                                  dryRun=False,logCmd=False)
    expected = step.ana.getSetting('RscriptVersion',rVersion) # Not in settings then not enforced!
    if step.ana.strict and rVersion != expected:
        raise Exception("Expecting Rscript [version: "+expected+"], " + \
                        "but found [version: "+rVersion+"]")
    version = step.ana.getCmdOut('grep Version ' + \
                                 step.ana.getDir(toolName+'Dir',alt='toolsDir') + \
                                 "README.txt | awk '{print $2}'", dryRun=False,logCmd=False)
    expected = step.ana.getSetting(toolName+'Version',version) # Not in settings then not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting "+toolName+" [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# "+toolName+" [version: " + version + \
                     "] running on Rscript [version: " + rVersion + "]")
    return version

def strandCorr(step, bam, strandCor):
    '''Generates strand correlations for bam.'''
    
    cmd = '{rscript} {phantomTools}run_spp.R -c={input} -out={output}'.format( \
          rscript=step.ana.getTool('Rscript',orInPath=True), \
          phantomTools=step.ana.getDir('phantomToolsDir',alt='toolsDir'), \
          input=bam, output=strandCor)

    toolName = __name__.split('.')[-1] + " R:strandCorr"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)

