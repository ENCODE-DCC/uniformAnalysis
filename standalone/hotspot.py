#!/usr/bin/python2.7

import sys, os, argparse, subprocess, json

def main():
    readLengths = ['32', '36', '40', '50', '58', '72', '76', '100']
    genomes = ['hg19', 'mm9']
    dataTypes = ['DNase-seq', 'ChIP-seq']

    parser = argparse.ArgumentParser(description = 'Hotspot wrapper for Uniform Analysis Pipeline')
    parser.add_argument('hotspotLocation', help='The directory to the hotspot installation, for instance "/hive/groups/encode/encode3/tools/hotspot-distr-v4/"')
    #parser.add_argument('bedtoolsLocation', help='The directory to bedtools (used by hotspot), for instance "/hive/groups/encode/encode3/tools/bedtools-2.17.0/"')
    #parser.add_argument('bedopsLocation', help='The directory to bedops (used by hotspot), for instance "/hive/groups/encode/encode3/tools/bedops/"')
    #parser.add_argument('configFile', help='Configuration file containing additional parameters')
    parser.add_argument('inputBam', help='Alignment file (in BAM format) to run hotspot on')
    parser.add_argument('genome', help='Which genome to use, the following are supported: ' + ','.join(genomes))
    parser.add_argument('dataType', help='Which datatype to use, the following are supported: ' + ','.join(dataTypes))
    parser.add_argument('readLength', help='Tag length in base pairs, the following are supported: ' + ','.join(readLengths))
    parser.add_argument('tmpDir', help='Path to a temporary directory that will be created by this tool and cleaned up afterwards')
    parser.add_argument('outputDir', help='Path to a directory to which the output files will be copied')
    parser.add_argument('-s', '--seed', type=int, default=101)
    parser.add_argument('-i', '--inputControl', default=None, help='Bam file, For ChIP-seq runs, an input will be required')
    parser.add_argument('-c', '--checkChr', default=None, help='Tests a portion of the given chromosome (e.g. chrX)')
    
    if len(sys.argv) < 2:
        parser.print_usage() 
        return
    args = parser.parse_args(sys.argv[1:])
    
    #if not os.path.isfile(args.configFile):
    #    raise ValueError('configFile: %s is not a valid file' % args.configFile)
    #config = json.load(args.configFile)
    #args.hotspotLocation = config['hotspotLocation']
    #args.bedtoolsLocation = config['bedtoolsLocation']
    #args.bedopsLocation = config['bedopsLocation']
    
    # ensure all inputs are valid directories/files/arguments
    if not os.path.isdir(args.hotspotLocation):
        raise ValueError('hotspotLocation: %s is not a valid directory' % args.hotspotLocation)
    #if not os.path.isdir(args.bedtoolsLocation):
    #    raise ValueError('bedtoolsLocation: %s is not a valid directory' % args.bedtoolsLocation)       
    #if not os.path.isdir(args.bedopsLocation):
    #    raise ValueError('bedopsLocation: %s is not a valid directory' % args.bedopsLocation)       
    if not os.path.isfile(args.inputBam):
        raise ValueError('inputBam: %s is not a valid file' % args.inputBam)
    if args.genome not in genomes:
        raise ValueError('genome: ' + args.genome + ' is not a valid genome, must be one of: ' + ','.join(genomes))
    if args.readLength not in readLengths:
        raise ValueError('readLength: ' + args.readLength + ' is not a supported read length, must be one of: ' + ','.join(readLengths))
    #if os.path.isdir(args.tmpDir):
    #    raise ValueError('tmpDir: %s should not already exist' % args.tmpDir)
      
    # checking dataType constraints
    if args.dataType == 'DNase-seq':
        if args.inputControl != None:
            raise ValueError('DNase-seq does not support input controls')
    elif args.dataType == 'ChIP-seq':   
        if args.inputControl == None:
            raise ValueError('ChIP-seq requires an input control')
        if not os.path.isfile(args.inputControl):
            raise ValueError('inputControl: %s is not a valid file' % args.inputControl)
    
    args.hotspotLocation = os.path.abspath(args.hotspotLocation)
    #args.bedtoolsLocation = os.path.abspath(args.bedtoolsLocation)
    #args.bedopsLocation = os.path.abspath(args.bedopsLocation)
    args.inputBam = os.path.abspath(args.inputBam)
    args.tmpDir = os.path.abspath(args.tmpDir)
    args.outputDir = os.path.abspath(args.outputDir)
    if args.inputControl != None:
        args.inputControl = os.path.abspath(args.inputControl)
    
    # make all directory names end with a slash
    if not args.hotspotLocation.endswith('/'):
        args.hotspotLocation += '/'
    #if not args.bedtoolsLocation.endswith('/'):
    #    args.bedtoolsLocation += '/'
    #if not args.bedopsLocation.endswith('/'):
    #    args.bedopsLocation += '/'
    #args.bedopsLocation += 'bin/'
    if not args.tmpDir.endswith('/'):
        args.tmpDir += '/'
    if not args.outputDir.endswith('/'):
        args.outputDir += '/'
    
    # create all hotspot filenames
    chromInfoBed = args.hotspotLocation + 'data/' + args.genome + '.chromInfo.bed'
    mappableFile = args.hotspotLocation + 'data/' + args.genome + '.K' + args.readLength + '.mappable_only.bed'
    omitRegionsFile = args.hotspotLocation + 'data/Satellite.' + args.genome + '.bed'
    hotspotExe = args.hotspotLocation + 'hotspot-deploy/bin/hotspot'
    peakFindExe = args.hotspotLocation + 'hotspot-deploy/bin/wavePeaks'
    tokenizerExe = args.hotspotLocation + 'ScriptTokenizer/src/script-tokenizer.py'
    pipeDir = args.hotspotLocation + 'pipeline-scripts'
    
    # ensure all hotspot files are in the right location
    for f in chromInfoBed, mappableFile, omitRegionsFile, hotspotExe, peakFindExe, tokenizerExe, pipeDir:
        if not os.path.exists(f):
            raise ValueError('hotspotLocation: installation is missing ' + f)
        
    # hotspot names its directories according to the name of the input bam, so we must capture that value as well
    fileName = os.path.split(args.inputBam)[1] 
    runName = os.path.splitext(fileName)[0]
    
    # mapping from files hotspot creates to what we want to name them as
    outputs = {
        args.tmpDir + runName + '-final/' + runName + '.hot.bed': args.outputDir + 'broadPeaks.bed',
        args.tmpDir + runName + '-final/' + runName + '.hot.pval.txt': args.outputDir + 'broadPeaks.pval',
        
        args.tmpDir + runName + '-final/' + runName + '.fdr0.01.hot.bed': args.outputDir + 'broadPeaksFdr.bed',
        
        args.tmpDir + runName + '-final/' + runName + '.fdr0.01.pks.bed': args.outputDir + 'narrowPeaks.bed',
        args.tmpDir + runName + '-final/' + runName + '.fdr0.01.pks.pval.txt': args.outputDir + 'narrowPeaks.pval',
        args.tmpDir + runName + '-final/' + runName + '.fdr0.01.pks.dens.txt': args.outputDir + 'narrowPeaks.dens',
        
        args.tmpDir + runName + '-peaks/' + runName + '.tagdensity.bed.starch': args.outputDir + 'density.bed.starch' #this needs to be turned into a bigWig
    }
        
    if not os.path.isdir(args.tmpDir):
        os.makedirs(args.tmpDir)
    
    # generate tokens.txt file
    tokensName = args.tmpDir + 'tokens.txt'
    with open(tokensName, 'w') as tokens:
        tokens.write('[script-tokenizer]\n')
        tokens.write('_TAGS_ = %s\n' % args.inputBam)
        
        if args.inputControl != None:
            tokens.write('_USE_INPUT_ = T\n')
            tokens.write('_INPUT_TAGS_ = %s\n' % args.inputControl)
        else:
            tokens.write('_USE_INPUT_ = F\n')
            tokens.write('_INPUT_TAGS_ =\n')
            
        tokens.write('_GENOME_ = %s\n' % args.genome)
        tokens.write('_CHROM_FILE_ = %s\n' % chromInfoBed)
        tokens.write('_K_ = %s\n' % args.readLength)
        tokens.write('_MAPPABLE_FILE_ = %s\n' % mappableFile)
        
        # Duplicates ok for DNAse, but not for other datatypes
        if args.dataType == 'Dnase-seq':
            tokens.write('_DUPOK_ = T\n')
        else:
            tokens.write('_DUPOK_ = F\n')
            
        tokens.write('_FDRS_ = "0.01"\n')
        tokens.write('_DENS_:\n')  # If not provided, will be generated
        tokens.write('_OUTDIR_ = %s\n' % args.tmpDir[:-1])
        tokens.write('_RANDIR_ = %s\n' % args.tmpDir[:-1]) # Nothing overlaps
        tokens.write('_OMIT_REGIONS_: %s\n' % omitRegionsFile)
        
        if args.checkChr != None:
            tokens.write('_CHECK_ = T\n')
            tokens.write('_CHKCHR_ = %s\n' % args.checkChr)
        else:
            tokens.write('_CHECK_ = F\n')
            tokens.write('_CHKCHR_ = chrX\n')
            
        tokens.write('_HOTSPOT_ = %s\n' % hotspotExe)
        tokens.write('_CLEAN_ = F\n') # We handle cleanup
        tokens.write('_PKFIND_BIN_ = %s\n' % peakFindExe)
        tokens.write('_PKFIND_SMTH_LVL_ = 3\n')
        tokens.write('_SEED_=%d\n' % args.seed)
        
        # Hotspot program parameters, should these be parameterized in the script?
        tokens.write('_THRESH_ = 2\n')
        tokens.write('_WIN_MIN_ = 200\n')
        tokens.write('_WIN_MAX_ = 300\n')
        tokens.write('_WIN_INCR_ = 50\n')
        tokens.write('_BACKGRD_WIN_ = 50000\n')
        tokens.write('_MERGE_DIST_ = 150\n')
        tokens.write('_MINSIZE_ = 10\n')
    
    # Extend PATH because various tools are run without qualification within hotspot, so prepend bedops, bedtools, and hotspot
    envPath = os.getenv('PATH')
    envPath = args.hotspotLocation + 'hotspot-deploy/bin/' + ':' + envPath #args.bedopsLocation + ':' + args.bedtoolsLocation + ':' + envPath
    os.putenv('PATH', envPath)
    
    # generate runhotspot file
    runhotspotName = args.tmpDir + 'runhotspot.sh'
    with open(runhotspotName, 'w') as runhotspot:
        runhotspot.write('#! /bin/bash -ex\n')
        runhotspot.write('scriptTokBin=%s\n' % tokenizerExe)
        runhotspot.write('pipeDir=%s\n' % pipeDir)
        runhotspot.write('tokenFile=%s\n' % tokensName)
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
        runhotspot.write('$scriptTokBin --clobber --output-dir=%s $tokenFile $scripts\n' % args.tmpDir)
        runhotspot.write('cd %s\n' % args.tmpDir)
        runhotspot.write('retCode=0\n')
        runhotspot.write('for script in $scripts\n')
        runhotspot.write('do\n')
        runhotspot.write('    %s$(basename $script).tok\n' % args.tmpDir)
        runhotspot.write('    retCode=$?\n')
        runhotspot.write('done\n')
        runhotspot.write('exit $retCode\n')
    
    os.chmod(runhotspotName, 0775) # Make this executable (leading 0 is for octal)
    
    retCode = subprocess.call(runhotspotName)
    if retCode != 0:
        return retCode
    
    if not os.path.isdir(args.outputDir):
        os.makedirs(args.outputDir)

    # move out all the files we want to keep
    for hotfile, outfile in outputs.iteritems():
        os.rename(hotfile, outfile)

    return 0
        
if __name__ == '__main__':
    main()
    
