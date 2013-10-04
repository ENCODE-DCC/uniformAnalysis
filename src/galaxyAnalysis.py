#!/usr/bin/env python2.7
# galaxyAnaylysi.py module holds GalaxyAnalysis class which is the descendent of Analysis class
#               for Encode3 Pipeline analysis of submissions.  This derived class 
#               is specialized for Galaxy workflows.  The encode3 anapysis pipeline works
#               within a temporary directory and at the end of each logical step (e.g. alignment)
#               all targets are moved to their final destinations.  When run in Galaxy, the 
#               same basic methods are followed.  However, two important differences must be 
#               handled here: (1) galaxy file naming and (2) manual workFlow initiation
#               vs. automated pipeline processing.
#               (1) This derived class handles conversion of galaxy to nonGalaxy names and will 
#               symlink nonGalaxy outputs back into galaxy for future access.  
#               (2) While the complete Encode3 pipeline will have a clear concept of an
#               "analysis" as all processing of multiple replicates from raw input to 
#               alignment, peak calling, analysis and quality characterization; 
#               the galaxy "pipeline" is expected to support running a single "analysis"
#               in a series of workFlow steps.  This may be necessary as data becomes 
#               available at different times or replicates fail and need to be replaced.
#               In galaxy the processing is kicked off manually, not simply when data arrives.

import os,sys
from src.analysis import Analysis
from src.settings import Settings
from src.log import Log

class GalaxyAnalysis(Analysis):
    '''
    Descendent from Analysis class with 'galaxy' specific methods.

    Functions are for resolving names/paths and logging
    '''

    def __init__(self, settingsFile,analysisId):
        Analysis.__init__(self, settingsFile, analysisId=analysisId)
        self._resultsDir = None  # Outside of galaxy and tmpDir struct. Same as inputFile location
        self._stayWithinGalaxy = self._settings.getBoolean('stayWithinGalaxy', False)
        self._galaxyInputs = {}      # May be in galaxy-dist/database/files or else symlinked lib
        self._galaxyOutputs = {}     # In galaxy-dist/database/files
        self._nonGalaxyOutputs = {}  # In resultsDir (same as inputFiles location directory
        self._fileSets = { 'galaxyInput' : self._galaxyInputs, 
                           'galaxyOutput': self._galaxyOutputs, 
                        'nonGalaxyInput' : self._inputFiles, 
                        'nonGalaxyOutput': self._nonGalaxyOutputs, 
                                 'target': self._targetOutput, 
                           'intermediate': self._interimFiles }
        self._deliverToGalaxyKeys = None
        self.createAnalysisDir() # encode pipeline creates this via the manifest.
        self.declareLogFile()
                           
    def createAnalysisDir(self):
        '''
        creates analysis level directory
        MUST override default version for galaxy
        '''
        if self.analysisId == None:
            raise Exception('This analysis has not been registered or defined in manifest')    
        if self._analysisDir != None:
            #raise Exception('The directory for this analysis has already been created')
            return self._analysisDir
            
        if self._stayWithinGalaxy:
            self._analysisDir = os.getcwd() # Override the Analysis class version for this
            if not self._analysisDir.endswith('/'):
                self._analysisDir = self._analysisDir + '/'
        else:
            self._analysisDir = self.getPath('tmpDir')
        self._analysisDir = self._analysisDir + self.analysisId.replace(' ','_') + '/'
        if not os.path.isdir(self._analysisDir):
            os.makedirs(self._analysisDir)
        return self._analysisDir
        
    def fileParse(self, someFile):
        '''
        Returns an dict object with fullPath, dir, fileName, root, and ext
        broken upon cleanly and normalized.
        '''
        
        fullPath =  os.path.abspath( someFile )  # Always work with absolute paths
        directory, fileName = os.path.split( fullPath )
        root, ext = os.path.splitext( fileName )
        if ext == None or ext == '':
            ext = 'dir'
        return { 'fullPath': fullPath, 'dir': directory + '/',  # normalize dirs to end in '/'
                 'fileName': fileName, 'root': root, 'ext': ext}
                 
    def stayWithinGalaxy(self):
        return self._stayWithinGalaxy
        
    def fileGetPart(self, file, part):
        fileParts = self.fileParse(file)
        try:
            return fileParts[part]
        except:
            raise ValueError("Unknown part of file: '"+part+"' for file:"+file)
        
    def anyKey(self,io):
        '''
        Returns the first key found for an io type, or else None
        '''
        try:
            for key in self._fileSets[io].keys():  
                return key
        except:
            return None

    def registerFile(self, name, io, someFile ):
        '''
        Registers one file of a given io type in the set of all files that are being tracked.
        '''
        
        try:
            filesContainer = self._fileSets[ io ]
        except:
            raise ValueError("File IO type'" + io + "' not supported!")
            
        fullPath =  os.path.abspath( someFile )  # Always work with absolute paths
        if io == 'nonGalaxyInput':
            self.registerInputFile(name, fullPath)
        elif io == 'nonGalaxyOutput': # 2 files: one in analysisDir, second in resultsDir
            self._fileSets[ io ][ name ] = fullPath   
            self.registerTargetOutput(name, self.fileGetPart(fullPath,'fileName'))
        elif io == 'intermediate':
            self.registerInterimOutput(name, self.fileGetPart(fullPath,'fileName'))
        else:
            # TODO: make galaxy register routines
            self._fileSets[ io ][ name ] = fullPath   
        return self._fileSets[ io ][ name ]
        
    def nonGalaxyInput(self, name):
        '''
        Registers and returns a nonGalaxyInput filePath based upon a named galaxyInput.
        Since galaxyInput could be a symlink to an outside location, this function
        resolves the symlink and prefers the outside location.
        '''
        try:
            galaxyInput = self._fileSets['galaxyInput'][name]
        except:
            raise Exception('Galaxy input file ' + name + 
                            ' must be registered before Non-Galaxy input name can be resolved.')
        if not self._stayWithinGalaxy:
            galaxyInputPath = self.fileGetPart( galaxyInput, 'fullPath')
            if os.path.islink( galaxyInputPath ):
                nonGalaxyInput = os.path.abspath( os.readlink( galaxyInputPath ) )
                self.registerFile(name,'nonGalaxyInput',nonGalaxyInput )
                return self._fileSets['nonGalaxyInput'][name]
          
        self.registerFile(name,'nonGalaxyInput',galaxyInput )
        return self._fileSets['nonGalaxyInput'][name]
        
    def resultsDir(self, galaxyPath=None):
        '''
        returns the directory to put target results in.  Possibly outside of galaxy.
        '''
        if self._resultsDir != None:
            return self._resultsDir

        # Stay within Galaxy so use galaxyOutput which, by definition is in resultsDir.
        if self._stayWithinGalaxy:
            key = self.anyKey('galaxyOutput')
            if key == None:
                raise Exception("Output file must be registered before 'resultsDir' can be " + \
                                "determined.")
            self._resultsDir = self.fileGetPart( self._fileSets['galaxyOutput'][key], 'dir')
            if galaxyPath != None:  # overkill but be thourough 
                galaxyPath = os.path.abspath( galaxyPath )
                if not self._resultsDir.startswith( galaxyPath ):
                    raise Exception("Requested to stay within Galaxy but '" + \
                                    self._resultsDir + "' is not within Galaxy!")
            return self._resultsDir  # Dir from input file so must be there
        
        # Look for non-Galaxy input location
        key = self.anyKey('nonGalaxyInput')
        if key != None:
            self._resultsDir = self.fileGetPart( self._fileSets['nonGalaxyInput'][key], 'dir')
            if self._resultsDir == self.fileGetPart(self._fileSets['galaxyInput'][key], 'dir'):
                if galaxyPath != None:
                    galaxyPath = os.path.abspath( galaxyPath )
                    if self._resultsDir.startswith( galaxyPath ):
                        # TODO decide whether to "except or accept" as discovered to be True
                        raise Exception("Not expected to stay within Galaxy but '" + \
                                         self._resultsDir + "' is inside Galaxy!")
                        self._stayWithinGalaxy = True # Requested or not, we're staying inside today
                return self._resultsDir  # Dir from input file so must be there
                
        # If all else fails, look for a setting.  TODO: Consider removing this option.
        if self._resultsDir == None:
            try:
                self._resultsDir = self._settings.getSetting('resultsDir', self._resultsDir)
            except:
                raise Exception("No input file has been registered and The ENCODE3 setting " + 
                                "'resultsDir' is not defined in "+ self._settingsFile)
            if not self._resultsDir.endswith('/'):
                self._resultsDir = self._resultsDir + '/'
            if os.path.isdir( self._resultsDir ) == False:
                os.mkdir( self._resultsDir ) # Dir from setting so make sure it is there
        return self._resultsDir

    def galaxyFileId(self,fileName):
        '''
        Returns the ID of a particular galaxy output (e.g. 'dataset_278.dat' returns '278'). 
        '''
        galaxyId = ''
        galaxyRoot = self.fileGetPart(fileName,'root')
        if galaxyRoot == None or len(galaxyRoot) == 0:
            return "0"
        piecesOfRoot = galaxyRoot.split('_')
        if piecesOfRoot == None or len(piecesOfRoot) < 2:
            return "-1"
        return piecesOfRoot[1] 
    
    def _makeNameWithTemplate(self, rootTemplate=None, ext=None, input='', input2=None ):
        '''
        Creates a file name without a path from a template and existing input file(s).
        If inputs are omitted then a single input is assumed and will be indeterminate if
        there is not exactly 1 non-galaxy input.  If no inputs are desired, then set input=None.
        If template is omitted it will default to '%s' or '%s_%s' if 2 inputs. 
        '''
        root = root2 = ''
        if input == '':
            input = self.anyKey('nonGalaxyInput')
        try:
            if input != None and input != '':
                root  = self.fileGetPart( self._fileSets['nonGalaxyInput'][input], 'root')
            if input2 != None and input2 != '':
                root2 = self.fileGetPart( self._fileSets['nonGalaxyInput'][input2],'root')
        except:
            raise Exception('One or more inputs needed to generate output file name!')
            
        fileName = rootTemplate
        if root != '' and root2 != '':
            len2 = len(root2)
            for ix in range( len(root) ):   # 2nd name should be shortened by common portion
                if root[ix] != root2[ix]:
                    if ix > 2:
                         root2 = root2[ ix: ]
                    break
            if rootTemplate == None or rootTemplate == '':
                rootTemplate = '%s_%s'
            fileName = rootTemplate % (root,root2)
        elif root != '':
            if rootTemplate == None or rootTemplate == '':
                rootTemplate = '%s'
            fileName = rootTemplate % (root)
        if ext != None:
            if ext == 'dir':
                if not fileName.endswith('/'):
                    fileName = fileName + '/'
            else:
                fileName = fileName + '.' + ext
        return fileName    
    
    def createOutFile(self, name, io, rootTemplate=None, ext=None, input='', input2=None ):
        '''
        Creates, registers and returns an output file name based upon input file(s).
        Note that ext='dir' will create a directory.
        '''
        fileName = self._makeNameWithTemplate(rootTemplate, ext, input, input2 )
        if io == 'nonGalaxyOutput':
            self.registerTargetOutput(name, fileName)
            self._fileSets[ io ][ name ] = self.resultsDir() + fileName   
            return self._fileSets[ io ][ name ] 
        elif io == 'intermediate':
            return self.registerInterimOutput(name, fileName)
        else:
            raise ValueError("Unknown file type '" + io + "' when creating file!")
    
    def printPaths(self, log=None):
        '''
        Prints all known input and output paths and file names.
        '''
        tab=30  # Makes for aligned values in output
        if log == None:
            log = self.log
        log.out('\n# Location settings:')
        log.out('analysis dir:'.ljust(tab) + self.dir)
        if self.log.file() != None:
            log.out('analysis log:'.ljust(tab) + self.log.file())
        if self._settingsFile != None:  # raise exception?
            log.out('settingsFile:'.ljust(tab) + self._settingsFile)
        if self._resultsDir != None:  # raise exception?
            log.out('resultsDir:'.ljust(tab) + self._resultsDir)
            
        # files:
        for io in sorted(self._fileSets.keys()):
            for name in sorted( self._fileSets[io].keys() ):
                fileName = self._fileSets[io][name]
                if io == 'galaxyInput':
                    ngFile = self._fileSets['nonGalaxyInput'][name]
                    if fileName == ngFile:
                        continue;
                title = "%s[%s]:" % (io,name)
                log.out(title.ljust(tab) + fileName)

        # logical step dirs and logs            
        if len( self._steps ) > 0:
            for ix in range( len( self._steps ) ):
                step = self._steps[ix]
                if step._dir != None:
                    title = step.name + ' dir:'
                    log.out(title.ljust(tab) + step.dir )
                if step.log.file() != None:
                    title = step.name + ' log:'
                    log.out(title.ljust(tab) + step.log.file() )
                for name in sorted( step.garbageFiles.keys() ):
                    title = "garbage[%s]:" % (name)
                    log.out(title.ljust(tab) + step.garbageFiles[name])
                for name in sorted( step.interimFiles.keys() ):
                    title = "interimFile[%s]:" % (name)
                    log.out(title.ljust(tab) + step.interimFiles[name])
                for name in sorted( step.targetFiles.keys() ):
                    title = "targetFile[%s]:" % (name)
                    log.out(title.ljust(tab) + step.targetFiles[name])
        log.out('') # add a blank line at the end

    def deliverToGalaxy(self, log=None):
        """
        Call this after successfully completing logical steps.
        Moves targetOutput files to NonGalaxy locations,
        then symlinks nonGalaxyOutputs to galaxyOutputs.
        """
        # interim files stay in analysisDir
        # copy targets from analysisDir to resultsDir
        # NOTE: cmds are logged to analysisLog, not stepLog
        if log == None:
            log = self.log
        err=0
        count=0
        # Because we do not want to stop the loop for an exception
        # we record exceptions and raise one at the end.
        fails = '' 
        fullSetOfKeys = self._targetOutput.keys()
        deliveryKeys = fullSetOfKeys
        if self._deliverToGalaxyKeys != None:
            deliveryKeys = self._deliverToGalaxyKeys
        for key in deliveryKeys:
            if key not in fullSetOfKeys:
                continue
            try:
                permanentOutput = self._nonGalaxyOutputs[key]
                if self._stayWithinGalaxy:
                    if key in self._galaxyOutputs:
                        permanentOutput = self._galaxyOutputs[key]
                    else:
                        permanentOutput = None
                
                # hardlink target in analysisDir to resultsDir
                if permanentOutput != None:
                    err = self.linkOrCopy(self._targetOutput[key],permanentOutput,log=log)
                    if err != 0:
                        fails = fails + "Failure to tidy up: '" + \
                                self._targetOutput[key]+"' to '"+permanentOutput+"'\n"
                    else:
                        count = count + 1
                # symlink result back into galaxy
                if not self._stayWithinGalaxy and key in self._galaxyOutputs:
                    galaxyOutput = self._galaxyOutputs[key]
                    # softlink so permenant location can be discovered by future steps
                    err = self.linkOrCopy(permanentOutput,galaxyOutput,soft=True,log=log)
                    if err != 0:
                        fails = fails + "Failure to tidy up: '" + \
                                self._targetOutput[key]+"' to '"+galaxyOutput+"'\n"
            except:
                fails = fails + "Failure to tidy up target '"+key+"'\n"
                
        if self._stayWithinGalaxy:
            what = " result(s) to Galaxy."
        else:
            what = " result(s) to Galaxy and non-Galaxy locations."
        if err != 0:
            log.out("\n>>> Failure to pass" + what)
        elif count > 0:
            log.out("\n>> Passed "+str(count) + what)
        if len(fails) > 0:
            raise Exception(fails)
        
    def deliverToGalaxyKeys(self,justThisSet):
        '''
        Register certain keys to be delived in deliverToGalaxy and in this order.
        Without setting this, all target file keys will be delivered.
        '''
        self._deliverToGalaxyKeys = justThisSet
        
    def logToResultDir(self):
        '''
        Copies the analysis log to the results dir, if it is outside galaxy
        '''
        # TODO: figure out what to do inside galaxy.  Replace stepLog with analysis log?
        if not self._stayWithinGalaxy:
            if self.log.file() != None:
                nonGalaxyLog = self.resultsDir() + self.fileGetPart( self.log.file(), 'fileName' )
                os.system('rm -f ' + nonGalaxyLog)
                self.log.dump(nonGalaxyLog)
        
    def onSucceed(self, step):
        """
        Extend analysis.onSucceed to handle galaxy specific pipeline will handle all success 
        steps, like copying out files we care about and emptying the step directory
        """
        if self.dryRun():
            self.printPaths(log=step.log)   # For posterity
        
        #try:
        self.deliverFiles(step)
        self.deliverToGalaxy(log=step.log)
        #except:
        #    pass # Lets see any exceptions
        
        step.log.out("\n--- End of step ---\n")
        
        step.log.dump( self.log.file() ) # to stdout if no runningLog
        self.logToResultDir()
        if self.log.file() != None:  # If analysisLog, then be sure to just print step log to stdout
            step.log.dump()
        if not self.dryRun():
            step.cleanup()               # Removes logicalStep.stepDir()
        #else:
        #    self.runCmd('ls -l ' + step.dir, dryRun=False)
        #    self.log.out('')
        self.removeStep(step)  # Do we want to do this?   
        return 0
    
    def onFail(self, logicalStep):
        """
        Override Analysis.onFail() to include galaxy specific things
        """
        if self.dryRun():
            self.printPaths(log=logicalStep.log)   # For posterity

        err = Analysis.onFail(self,logicalStep)
        exit( err )
    

############ command line testing ############
if __name__ == '__main__':
    """
    Test this thang
    """
    import datetime
    from logicalstep import LogicalStep
    
    print "======== begin '" + sys.argv[0] + "' test ========"
    analysisId = 'galaxyAnalysis Test' 
    repNo = '1'   
    stepName = 'Test E3 Fake Step'
    
    settingFile = '/hive/users/tdreszer/galaxy/galaxy-dist/tools/encode/settingsE3.txt'    
    galaxyInputFile = '/cluster/home/mmaddren/grad/pipeline/data/UwDnase/' \
                    + 'wgEncodeUwDnaseAg04449RawDataRep1.fastq'
    galaxyOutputFile = '/hive/users/tdreszer/galaxy/galaxy-dist/database/files/000/dataset_269.dat'
    galaxyPath = '/hive/users/tdreszer/galaxy/'
    
    e3 = GalaxyAnalysis(settingFile, analysisId)
    e3.dryRun(True)
    
    # Command-line args predefined in in settings:
    reads = e3.getSetting('fastqSampleReads','100000')
    seed = e3.getSetting('fastqSampleSeed','12345')

    # Establish up tool locations
    toolPath = e3.getSetting('toolPath')
    fastqcToolPath = e3.getSetting('fastqcToolPath',toolPath)
    
    # Get nonGalaxy paths
    e3.registerFile('fastq','galaxyInput',galaxyInputFile)
    e3.registerFile('validated','galaxyOutput',galaxyOutputFile)
    nonGalaxyInput = e3.nonGalaxyInput('fastq')
    resultsDir     = e3.resultsDir(galaxyPath)
    runningLog     = e3.declareLogFile()
    e3.log.empty()  # start with an empty log
    
    # Begin logging
    step = LogicalStep(e3,stepName)
    
    # Establish temporary and Permenant outputs  
    sampleOf     = step.declareGarbageFile('sampleOf_s' + reads, suffix='fastq')
    sampledStats = step.declareGarbageFile('sampledStats', suffix='txt')
    # The following 2 are bound together by the same nameKey:
    stepFile      = step.declareTargetFile('validateRep'+repNo, suffix='html') # will become nonGalaxyOutput
    nonGalaxyOutput = e3.createOutFile('validateRep'+repNo,'nonGalaxyOutput', \
                                   '%s_s'+reads+'_fastqc/fastqc_report', ext='html' )

    # FAKING step.run()
    step._status = 'Running'
    step.declareLogFile() # Ensures that the logical step dir and log exist
    step.log.out("--- Beginning '" + stepName + "' [" + 
               datetime.datetime.now().strftime("%Y-%m-%d %X (%A)")+ '] ---')

    # For posterity
    e3.printPaths()

    # Outputs of sampling will be found in the named tmpDir dir, 
    # NOTE: sampledStats could be /dev/null as it is not examined 
    e3.log.out('\n# fastqStatsAndSubsample [unversioned]:')
    err = e3.runCmd('> some command',log=step.log)
    if err != 0:
        step.log.out('>>> Failure on some command.')
        step.fail()

    # All fastqc outputs will be found in the named resultsDir dir, 
    # but a single html file in a subdir is wanted by galaxy
    version = e3.getCmdOut(fastqcToolPath + 'fastqc -version')
    e3.log.out('\n# fastqc [' + version + ']:')
    e3.log.out('> some other command')
    if err != 0:
        step.log.out('>>> Failure on some other command.')
        step.fail()

    # step succeeds so this should handle cleanup.
    step.success()
    
    print "======== end '" + sys.argv[0] + "' test ========"
        
