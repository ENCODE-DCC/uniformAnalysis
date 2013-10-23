#!/usr/bin/env python2.7
# hotspot.py module holds methods for running hotspot from 
# a LogicalStep.  It is used to call peaks form a bam.
#
# Settings required: hotspotDir

# SELECTED notes copied from hotspot README:
# This distribution includes scripts for computing minimally thresholded (z-score = 2) hotspots; 
# FDR thresholded hotspots, using randomly generated tags; and FDR thresholded peaks within
# hotspots. 
#
# Hotspot calls, FDR thresholding and peak-calling require two passes of calls to hotspot, as well 
# as generation of random data, hotspot calling on that, and peak-calling on tag densities.
#
# For ChIP-seq data, you have the option of including an additional ChIP-seq input file
# (tokens _USE_INPUT_ and _INPUT_TAGS_), which will trigger subtracting input tags from the 
# ChIP tags in hotspots in the final scoring of hotspots.
#
# The hotspot program makes use of mappability information.  For a given tag length (k-mer size, 
# variable _K_), only a subset of the genome is uniquely mappable.  Hotspot uses this information 
# to help compute the background expectation for gauging enrichment.  The file defined by 
# variable _MAPPABLE_FILE_ in runall.tokens.txt contains the mappable positions in the 
# genome for a given k-mer size. We have included a file for 36-mers and the human genome hg19 
# in the data directory.  If you need a different combination, we provide a script in the
# hotspot-deploy/bin directory, called enumerateUniquelyMappableSpace, which will generate the
# mappability file for you, given a genome name and a k-mer size.
#
# (Running hotspot) will leave a final output directory whose name is the same as the
# tags file name, appended with the suffix "-final".  Within this directory will be found 
# files with some or all of the following names:
#   *.hot.bed                 minimally thresholded hotspots
#   *.fdr0.01.hot.bed         FDR thresholded hotspots
#   *.fdr0.01.pks.bed         FDR thresholded peaks
#   *.fdr0.01.pks.dens.txt    smoothed tag density value at each peak
#   *.fdr0.01.pks.zscore.txt  z-score for the hotspot containing each peak
#   *.fdr0.01.pks.pval.txt    binomial p-value for the hotspot containing each peak
#
# Dependencies needed in PATH:
# python2.6+, R, bedops v2.0.0+ 64bit, bedTools, wavelets (in hotspot-deploy/bin/)
# The unix utility program bc is used to perform some calculations.
#
# auxillary script: enumerateUniquelyMappableSpace requires:
# bowtie and bowtie-build must be in your path, /usr/bin/perl, 
# qsub for parallelizing (unparallelize: comment out the two lines that start with "qsub,"
# and the two lines that start with "EOF.")



import os
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

def runHotspot(step, tokensFile, runhotspotScript, bam, tagLen):
    
    toolName = __name__ + " peak calling"
    step.toolBegins(toolName)

    # raise this exception where tagLength is actually used.
    if tagLen not in ['32','36','40','50','58','72','76','100']:
        raise StepError('hotspot tag length ' + tagLen + ' not supported!')
    
    hotspotDir = step.ana.getDir('hotspotDir')
    genome = step.ana.genome

    # generate tokens.txt file
    tokens = open(tokensFile, 'w')
    tokens.write('[script-tokenizer]\n')
    tokens.write('_TAGS_ = ' + bam + '\n')
    tokens.write('_USE_INPUT_ = F\n')
    tokens.write('_INPUT_TAGS_ =\n')
    tokens.write('_GENOME_ = ' + genome + '\n')
    tokens.write('_CHROM_FILE_ = ' + hotspotDir + 'data/' + genome + '.chromInfo.bed\n')
    tokens.write('_K_ = ' + tagLen + '\n') # <<<<<<<<<<<<<< IMPORTANT TO SET BASED UPON DATA !!!!
    tokens.write('_MAPPABLE_FILE_ = ' + hotspotDir + 'data/' + \
                                        genome + '.K' + tagLen + '.mappable_only.bed\n')
    tokens.write('_DUPOK_ = T\n')      # TODO: 'T' for DNase but 'F' otherwise
    tokens.write('_FDRS_ = "0.01"\n')
    tokens.write('_DENS_:\n')
    tokens.write('_OUTDIR_ = ' + step.dir[ :-1 ] + '\n') # outputs must be written to step.dir
    tokens.write('_RANDIR_ = ' + step.dir + 'rand\n')    # outputs must be written to step.dir
    tokens.write('_OMIT_REGIONS_: ' + hotspotDir + 'data/Satellite.' + genome + '.bed\n')
    tokens.write('_CHECK_ = T\n')
    tokens.write('_CHKCHR_ = chr22\n')  # TODO: Change to chr22 (from chrX) until end of debug
    tokens.write('_HOTSPOT_ = ' + hotspotDir + 'hotspot-deploy/bin/hotspot\n')
    tokens.write('_CLEAN_ = F\n')    # Changed to F (from T) because step.dir is cleaned up anyway
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
    # Put all these tokens in the log:
    step.log.out('Tokenized parameters:')
    step.log.appendFile(tokensFile)
    step.log.out('')  # skip a line
    
    # Extend PATH because various tools are expected
    envPath = os.getenv('PATH')
    envPath = envPath + ':' + step.ana.getDir('bedtoolsDir',alt='toolsDir')
    envPath = envPath + ':' + step.ana.getDir('bedopsDir',alt='toolsDir')
    envPath = envPath + ':' + hotspotDir + 'hotspot-deploy/bin/'
    os.putenv('PATH',envPath)
    
    # generate runhotspot file
    runhotspot = open(runhotspotScript, 'w')
    runhotspot.write('#! /bin/bash\n')
    runhotspot.write('scriptTokBin=' + hotspotDir + 'ScriptTokenizer/src/script-tokenizer.py\n')
    runhotspot.write('pipeDir=' + hotspotDir + 'pipeline-scripts\n')
    runhotspot.write('tokenFile=' + tokensFile + '\n')
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
    runhotspot.write('cd ' + step.dir + '\n')   # outputs must be written to step.dir
    runhotspot.write('for script in $scripts\n')
    runhotspot.write('do\n')
    runhotspot.write('    ' + step.dir + '$(basename $script).tok\n')
    runhotspot.write('done\n')
    runhotspot.close()
    os.chmod(runhotspotScript, 0775) # Make this executable (leading 0 is for octal)
    # TODO: add runhotspotScript to the log?
    #step.log.out('Run hotspot script:')
    #step.log.appendFile(runhotspotScript)
    #step.log.out('')  # skip a line
    
    step.err = step.ana.runCmd(runhotspotScript, log=step.log) # stdout goes to file
    step.toolEnds(toolName,step.err)
            
