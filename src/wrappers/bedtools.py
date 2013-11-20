#!/usr/bin/env python2.7
# bedtools.py module holds methods for running bedtools from a LogicalStep.
#
# Settings required: bedtoolsDir (or toolsDir), hg19ChromInfoFile

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    # Note: all bedtools should have the same version.
    toolName = __name__.split('.')[-1]
    path = step.ana.getDir(toolName+'Dir',alt='toolsDir')
    version = step.ana.getCmdOut(path + "bedToBam 2>&1 | grep Version | awk '{print $2}'", \
                                 dryRun=False,logCmd=False)
    expected = step.ana.getSetting(toolName+'Version',version) # Not in settings: not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting "+toolName+" [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# "+toolName+" [version: " + version + "]")
    return version

def bedToBam(step, bed, bam):
    '''Convert Bed to Bam.'''
    
    cmd = '{path}bedToBam -i {bed} -g {chromInfo} > {bam}'.format( \
          path=step.ana.getDir('bedtoolsDir',alt='toolsDir'), bed=bed, \
          chromInfo=step.ana.getSetting(step.ana.genome+'ChromInfoFile'),bam=bam)
          
    toolName = __name__.split('.')[-1] + " bedToBam"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)

def intersectBed(step, inBed1, inBed2, outBed):
    '''Intersects bed with chromInfo Bed to Bam.'''
    
    cmd = '{path}intersectBed -a {bedA} -b {bedB} -f 1.00 > {bedOut}'.format( \
          path=step.ana.getDir('bedtoolsDir',alt='toolsDir'),bedA=inBed1,bedB=inBed2,bedOut=outBed)
          
    toolName = __name__.split('.')[-1] + " intersectBed"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)

def toBedGraph(step, tagLen, inBed, outBedGraph):
    '''Convert Bed to bedGraph.'''
    
    # TODO: The correct bed to intersect with is ???
    intersectWith = step.ana.getDir('hotspotDir') + 'data/' + step.ana.genome + \
                                                    '.K' + tagLen + '.mappable_only.bed'

    cmd = '{path}intersectBed -a {bedA} -b {bedB} -f 1.00 | cut -f 1,2,3,5> {bedGraph}'.format( \
          path=step.ana.getDir('bedtoolsDir',alt='toolsDir'),bedA=inBed, \
          bedB=intersectWith,bedGraph=outBedGraph)
          
    toolName = __name__.split('.')[-1] + " toBedGraph"
    step.toolBegins(toolName)
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)
