#!/usr/bin/env python2.7
# hotspot.py module holds methods for running hotspot from 
# a LogicalStep.  It is used to call peaks form a bam.
#
# toolsDir must be in path and 'eap' bash scripts must be in toolsDir. 
# Settings required: hotspotDir
# NOTE: Must run from hotspot-dist/hotspot-deploy/bin dir !!!

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
    return step.getToolVersion(step.ana.toolsDir+'hotspot-distr/hotspot-deploy/bin/hotspot', logOut)

def eap_hotspot(step, genome, inBam, tagLen, outNarrowPeak, outBroadPeak, outBigWig):
    '''Hostspot peak calling'''
    
    # Currently sets path internally, but we should make sure hotspot-disty/hotspot-deploy/bin
    # and bedtools/bin are in path.  Ideally this is done via toolsDir then relative path.
    
    # usage v1: eap_run_hotspot genome input.bam readLength out.narrowPeak out.broadPeak out.bigWig
    cmd = "eap_run_hotspot {db} {bam} {readLen} {narrowOut} {broadOut} {bwOut}".format( \
          db=genome, bam=inBam, readLen=tagLen, \
          narrowOut=outNarrowPeak, broadOut=outBroadPeak, bwOut=outBigWig)
          
    toolName = 'eap_run_hotspot'
    step.toolBegins(toolName)
    fromDir = os.getcwd()
    os.chdir(step.dir)
    #step.ana.runCmd("pushd "+step.dir, dryRun=False,logCmd=False)
    step.getToolVersion(toolName, logOut=True)
    step.getToolVersion(step.ana.toolsDir+'hotspot-distr/hotspot-deploy/bin/hotspot', logOut=True)
    #step.getToolVersion(step.ana.toolsDir+'hotspot-distr/hotspot-deploy/bin/wavePeaks', logOut=True) # TODO?
    #step.getToolVersion(step.ana.toolsDir+'hotspot-distr/ScriptTokenizer/src/script-tokenizer.py', logOut=True) # TODO?
    step.getToolVersion('python2.7', logOut=True)
    step.getToolVersion('hotspot.py', logOut=True)
    step.getToolVersion('bedToBigBed', logOut=True)
    step.getToolVersion('bedmap', logOut=True)
    step.getToolVersion('sort-bed', logOut=True)
    step.getToolVersion('starchcat', logOut=True)
    step.getToolVersion('unstarch', logOut=True)
    step.getToolVersion(step.ana.toolsDir+'bedtools/bin/intersectBed', logOut=True)
    step.getToolVersion('bedGraphPack', logOut=True)
    step.getToolVersion('bedGraphToBigWig', logOut=True)

    step.err = step.ana.runCmd(cmd, log=step.log)
    os.chdir(fromDir)
    #step.ana.runCmd("popd", dryRun=False,logCmd=False)
    step.toolEnds(toolName,step.err)

def runHotspot(step, tokensFile, runhotspotScript, bam, tagLen):
    '''Hostspot peak calling tool'''
    
    toolName = __name__.split('.')[-1] + " peak calling"
    step.toolBegins(toolName)
    step.getToolVersion(step.ana.toolsDir+'hotspot-deploy/bin/hotspot', logOut=True)

    # raise this exception where tagLength is actually used.
    if tagLen not in ['32','36','40','50','58','72','76','100']:
        raise StepError('hotspot tag length ' + tagLen + ' not supported!')
    
    hotspotDir = step.ana.getDir('hotspotDir')
    genome = step.ana.genome

    # generate tokens.txt file
    tokens = open(tokensFile, 'w')
    tokens.write('[script-tokenizer]\n')
    tokens.write('_TAGS_ = ' + bam + '\n')
    # For ChIPseq, provide input (aka control):
    tokens.write('_USE_INPUT_ = F\n')
    tokens.write('_INPUT_TAGS_ =\n')
    tokens.write('_GENOME_ = ' + genome + '\n')
    tokens.write('_CHROM_FILE_ = ' + hotspotDir + 'data/' + genome + '.chromInfo.bed\n')
    tokens.write('_K_ = ' + tagLen + '\n') # <<<<<<<<<<<<<< IMPORTANT TO SET BASED UPON DATA !!!!
    tokens.write('_MAPPABLE_FILE_ = ' + hotspotDir + 'data/' + \
                                        genome + '.K' + tagLen + '.mappable_only.bed\n')
    tokens.write('_DUPOK_ = T\n')      # TODO: 'T' for DNase but 'F' otherwise
    tokens.write('_FDRS_ = "0.01"\n')
    tokens.write('_DENS_:\n')  # If not provided, will be generated
    tokens.write('_OUTDIR_ = ' + step.dir[ :-1 ] + '\n') # outputs must be written to step.dir
    tokens.write('_RANDIR_ = ' + step.dir[ :-1 ] + '\n')    # could safely be the same as OUTDIR
    #tokens.write('_RANDIR_ = ' + step.dir + 'rand\n')    # could safely be the same as OUTDIR
    tokens.write('_OMIT_REGIONS_: ' + hotspotDir + 'data/Satellite.' + genome + '.bed\n')
    tokens.write('_CHECK_ = F\n')  # TODO: Various test datasets fail when 'T'!  But production?
    tokens.write('_CHKCHR_ = chrX\n')  # Only used when CHECK = T, but test data fails when CHECK=T 
    tokens.write('_HOTSPOT_ = ' + hotspotDir + 'hotspot-deploy/bin/hotspot\n')
    tokens.write('_CLEAN_ = F\n')    # Changed to F (from T) because step.dir is cleaned up anyway
    tokens.write('_PKFIND_BIN_ = ' + hotspotDir + 'hotspot-deploy/bin/wavePeaks\n')
    tokens.write('_PKFIND_SMTH_LVL_ = 3\n')
    tokens.write('_SEED_=101\n')
    # Hotspot program parameters
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
    envPath = step.ana.getDir('bedtoolsDir',alt='toolsDir') + ':' + envPath
    envPath = step.ana.getDir('bedopsDir',alt='toolsDir') + ':' + envPath 
    envPath = hotspotDir + 'hotspot-deploy/bin/' + ':' + envPath 
    os.putenv('PATH',envPath)
    step.log.out('PATH='+envPath)  # Put path in log
    step.log.out('')  # skip a line
    
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
    runhotspot.write('retCode=0\n')   # Should have a return code from last script run
    runhotspot.write('for script in $scripts\n')
    runhotspot.write('do\n')
    runhotspot.write('    ' + step.dir + '$(basename $script).tok\n')
    runhotspot.write('    retCode=$?\n')
    runhotspot.write('done\n')
    runhotspot.write('exit $retCode\n')
    runhotspot.close()
    os.chmod(runhotspotScript, 0775) # Make this executable (leading 0 is for octal)
    # TODO: add runhotspotScript to the log?
    #step.log.out('Run hotspot script:')
    #step.log.appendFile(runhotspotScript)
    #step.log.out('')  # skip a line
    
    step.err = step.ana.runCmd(runhotspotScript, log=step.log)
    step.toolEnds(toolName,step.err)
            
