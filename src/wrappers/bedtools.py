#!/usr/bin/env python2.7
# bedtools.py module holds methods for running bedtools from a LogicalStep.
#
# Settings required: bedtoolsDir (or toolsDir), hg19ChromInfoFile
# NOTE: Must run from bedtools/bin dir !!!

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    # Note: all bedtools should have the same version.
    return step.getToolVersion(step.ana.toolsDir+'bedtools/bin/bedToBam', logOut)

def bedToBam(step, bed, bam):
    '''Convert Bed to Bam.'''
    toolsDir=step.ana.toolsDir+'bedtools/bin/'
    
    cmd = '{path}bedToBam -i {bed} -g {chromInfo} > {bam}'.format( \
          path=toolsDir, bed=bed, \
          chromInfo=step.ana.getSetting(step.ana.genome+'ChromInfoFile'),bam=bam)
          
    toolName = __name__.split('.')[-1] + " bedToBam"
    step.toolBegins(toolName)
    step.getToolVersion(toolsDir+'bedToBam', logOut=True)
    
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)

def intersectBed(step, inBed1, inBed2, outBed):
    '''Intersects bed with chromInfo Bed to Bam.'''
    toolsDir=step.ana.toolsDir+'bedtools/bin/'
    
    cmd = '{path}intersectBed -a {bedA} -b {bedB} -f 1.00 > {bedOut}'.format( \
          path=toolsDir,bedA=inBed1,bedB=inBed2,bedOut=outBed)
          
    toolName = __name__.split('.')[-1] + " intersectBed"
    step.toolBegins(toolName)
    step.getToolVersion(toolsDir+'intersectBed', logOut=True)
    
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)

def toBedGraph(step, tagLen, inBed, outBedGraph):
    '''Convert Bed to bedGraph.'''
    toolsDir=step.ana.toolsDir+'bedtools/bin/'
    
    # TODO: The correct bed to intersect with is ???
    intersectWith = step.ana.getDir('hotspotDir') + 'data/' + step.ana.genome + \
                                                    '.K' + tagLen + '.mappable_only.bed'

    cmd = '{path}intersectBed -a {bedA} -b {bedB} -f 1.00 | cut -f 1,2,3,5> {bedGraph}'.format( \
          path=toolsDir,bedA=inBed, \
          bedB=intersectWith,bedGraph=outBedGraph)
          
    toolName = __name__.split('.')[-1] + " toBedGraph"
    step.toolBegins(toolName)
    step.getToolVersion(toolsDir+'intersectBed', logOut=True)
    
    step.err = step.ana.runCmd(cmd, logOut=False, log=step.log)
    step.toolEnds(toolName,step.err)
