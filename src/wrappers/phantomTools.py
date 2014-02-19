#!/usr/bin/env python2.7
# phantomTools.py module holds methods for running R phantomTools scripts from a LogicalStep.
#
# Settings required: phantomToolDir (or toolsDir), RscriptTool (or Rscript must be on env PATH)

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    rVersion = step.getToolVersion('Rscript', logOut)
    version = step.getToolVersion(step.ana.toolsDir+'run_spp.R', logOut)
    return rVersion+'|'+version

def strandCorr(step, bam, strandCor):
    '''Generates strand correlations for bam.'''
    
    cmd = 'Rscript {path}run_spp.R -c={input} -out={output}'.format( \
          path=step.ana.toolsDir, \
          input=bam, output=strandCor)

    toolName = __name__.split('.')[-1] + " R:strandCorr"
    step.toolBegins(toolName)
    step.getToolVersion('Rscript', logOut=True)
    step.getToolVersion(step.ana.toolsDir+'run_spp.R', logOut=True)

    step.err = step.ana.runCmd(cmd, log=step.log)
    step.toolEnds(toolName,step.err)

