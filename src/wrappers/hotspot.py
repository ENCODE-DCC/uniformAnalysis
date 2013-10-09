#!/usr/bin/env python2.7
# hotspot.py module holds methods for running hotspot from 
# a LogicalStep.  It is used to call peaks form a bam.
#
# Settings required: hotspotDir

import os, datetime
from src.logicalStep import StepError

def version(step, logOut=True):
    '''Returns tool version.  Will log to stepLog unless requested not to.'''
    version = step.ana.getCmdOut(step.ana.getDir('hotspotDir') + 'hotspot-deploy/bin/hotspot' + \
                                 " 2>&1 | grep HotSpot | awk '{print $1}'", \
                                 dryRun=False,logCmd=False)
    expected = step.ana.getSetting('fastqcVersion',version) # Not in settings: not enforced!
    if step.ana.strict and version != expected:
        raise Exception("Expecting hotspot [version: "+expected+"], " + \
                        "but found [version: "+version+"]")
    if logOut:
        step.log.out("# hotspot [version: " + version + "]")
    return version

def runHotspot(step, tokensName, runhotspotName, bam, peaks):
        
    hotspotDir = step.ana.getDir('hotspotDir')
        
    # generate tokens.txt file
    tokens = open(tokensName, 'w')
    tokens.write('[script-tokenizer]\n')
    tokens.write('_TAGS_ = ' + bam + '\n')
    tokens.write('_USE_INPUT_ = F\n')
    tokens.write('_INPUT_TAGS_ =\n')
    tokens.write('_GENOME_ = hg19\n')
    tokens.write('_K_ = 36\n')
    tokens.write('_CHROM_FILE_ = ' + hotspotDir + 'data/hg19.chromInfo.bed\n')
    tokens.write('_MAPPABLE_FILE_ = ' + hotspotDir + 'data/hg19.K36.mappable_only.bed.starch\n')
    tokens.write('_DUPOK_ = T\n')
    tokens.write('_FDRS_ = "0.01"\n')
    tokens.write('_DENS_:\n')
    tokens.write('_OUTDIR_ = ' + hotspotDir + 'pipeline-scripts/test\n')
    tokens.write('_RANDIR_ = ' + hotspotDir + 'pipeline-scripts/test\n')
    tokens.write('_OMIT_REGIONS_: ' + hotspotDir + 'data/Satellite.hg19.bed\n')
    tokens.write('_CHECK_ = T\n')
    tokens.write('_CHKCHR_ = chrX\n')
    tokens.write('_HOTSPOT_ = ' + hotspotDir + 'hotspot-deploy/bin/hotspot\n')
    tokens.write('_CLEAN_ = T\n')
    tokens.write('_PKFIND_BIN_ = ' + hotspotDir + 'hotspot-deploy/bin/wavePeaks\n')
    tokens.write('_PKFIND_SMTH_LVL_ = 3\n')
    tokens.write('_SEED_=101\n')
    tokens.write('_THRESH_ = 2\n')
    tokens.write('_WIN_MIN_ = 200\n')
    tokens.write('_WIN_MAX_ = 300\n')
    tokens.write('_WIN_INCR_ = 50\n')
    tokens.write('_BACKGRD_WIN_ = 50000\n')
    tokens.write('_MERGE_DIST_ = 150\n')
    tokens.write('_MINSIZE_ = 10\n')
    tokens.close()
    # TODO: put all these tokens in the log?
        
    # generate runhotspot file
    runhotspot = open(runhotspotName, 'w')
    runhotspot.write('#! /bin/bash\n')
    runhotspot.write('scriptTokBin=' + hotspotDir + 'ScriptTokenizer/src/script-tokenizer.py\n')
    runhotspot.write('pipeDir=' + hotspotDir + 'pipeline-scripts\n')
    runhotspot.write('tokenFile=' + tokensName + '\n')
    runhotspot.write('scripts="$pipeDir/run_badspot\n')
    runhotspot.write('    $pipeDir/run_make_lib\n')
    runhotspot.write('    $pipeDir/run_wavelet_peak_finding\n')
    runhotspot.write('    $pipeDir/run_10kb_counts\n')
    runhotspot.write('    $pipeDir/run_generate_random_lib\n')
    runhotspot.write('    $pipeDir/run_pass1_hotspot\n')
    runhotspot.write('    $pipeDir/run_pass1_merge_and_thresh_hotspots\n')
    runhotspot.write('    $pipeDir/run_pass2_hotspot\n')
    runhotspot.write('    $pipeDir/run_rescore_hotspot_passes\n')
    runhotspot.write('    $pipeDir/run_spot\n')
    runhotspot.write('    $pipeDir/run_thresh_hot.R\n')
    runhotspot.write('    $pipeDir/run_both-passes_merge_and_thresh_hotspots\n')
    runhotspot.write('    $pipeDir/run_add_peaks_per_hotspot\n')
    runhotspot.write('    $pipeDir/run_final"\n')
    runhotspot.write('$scriptTokBin --clobber --output-dir=' + step.dir + ' $tokenFile $scripts\n')
    runhotspot.write('for script in $scripts\n')
    runhotspot.write('do\n')
    runhotspot.write('    ./$(basename $script).tok\n')
    runhotspot.write('done\n')
    
    # TODO: chmod to be executable?
        
        #result = self.ana.runCmd([runhotspotName], logfilename, outputfilename) # TODO: NEED TO CHANGE THIS
        #if result != 0:
        #    self.fail()
    
    #cmd = './{script} > {peaks}'.format(script=runhotspotName, peaks=peaks)
    cmd = './' + runhotspotName

    step.log.out("\n# "+datetime.datetime.now().strftime("%Y-%m-%d %X")+" 'hotspot' begins...")
    step.err = step.ana.runCmd(cmd, log=step.log) # stdout goes to file
    step.log.out("# "+datetime.datetime.now().strftime("%Y-%m-%d %X") + " 'hotspot' " + \
                 "returned " + str(step.err))
    if step.err != 0:
        raise StepError('hotspot')
            