import sys, string
import os, os.path, datetime
import commands
from settings import Settings
from log import Log

class Analysis(object):
    '''
    This is the interface for an instantiation of the Encode Analysis 
    pipeline on a single analysis, which has two specific implementations:
    - EncodeAnalysis: for use in the official pipeline run by ENCODE
    - GalaxyAnalysis: code run by the Galaxy system for end-users
    '''
    
    @property
    def analysisId(self):
        return self._analysisId
        
    @property
    def dir(self):
        '''Returns the analysis directory'''
        if self._analysisDir == None:
            raise Exception("Trying to retrieve directory before its been created")
        return self._analysisDir
    
    @property
    def version(self):
        return str(self._pipelineVersion)
        
    def __init__(self, settingsFile, analysisId=None):
        '''
        Takes in a settings file which contains various paths to tools, a temp
        directory and other configuration setting for all analyses.  Optionally
        a manifest file for analysis specific details (relevant input files and 
        analysis ID) may be provided.  If no manifest file is provided, those
        details will have to be "registered" to the analysis, one by one.
        '''
        self._pipelineVersion = 1
        self._analysisId      = analysisId
        self.log              = Log() # Before logfile is declared, log print to stdout
        self._analysisDir     = None
        self._tmpDirs         = {}  # Note: these should be replaced with _steps[0].stepDir()
        self._steps           = []  # Keep track of ordered logical steps?
        self._inputFiles      = {}
        self._interimFiles    = {}
        self._targetOutput    = {}
        self._readType        = None    
        self._dryRun          = False
        self.strict           = False
        self._deliveryKeys    = None
        
        self._settingsFile = os.path.abspath( settingsFile )
        self._settings = Settings(self._settingsFile)


    def dryRun(self,setTo=None):
        '''
        Sets or returns the dryRun variable.
        '''
        if setTo != None:
            self._dryRun = setTo
        return self._dryRun

    def readType(self,setTo=None):
        '''
        Sets or returns the dryRun variable.
        '''
        if setTo != None:
            if setTo.lower() == 'paired':
                self._readType = 'paired'
            else:
                self._readType = 'single'
        return self._readType

    def getSetting(self, settingName, default=None, alt=None):
        '''
        Retrieves setting from the settings file
        '''
        if self._settingsFile == None or self._settings == None:
            raise ValueError('ENCODE3 settings file is unknown!')
        return self._settings.get(settingName,default,alt)
        
    def getPath(self, settingName, default=None, alt=None):
        '''        Retrieves full path from the settings file
        '''
        if self._settingsFile == None or self._settings == None:
            raise ValueError('ENCODE3 settings file is unknown!')
        return self._settings.getPath(settingName,default,alt)
        
    def getToolPath(self, toolName, orInPath=False):
        '''        Retrieves full path to tool from the settings file
        '''
        # NOTE: set orInPath=True then missing full path will default to execution path
        #       Example: if toolName is 'bwa' and 'bwaPath' not in settings file, and
        #       if orInPath==True then 'bwa' will be returned, and if bwa is found on
        #       execution path, no error will occur.
        if self._settingsFile == None or self._settings == None:
            raise ValueError('ENCODE3 settings file is unknown!')
        try:
            toolPath = self._settings.get(toolName + 'Path')
            return os.path.abspath(toolPath)
        except:
            if orInPath:
                return toolName
            # to clever by half: we know there is no toolName+'Path' so if toolPath
            # is missing, then exception will already have the correct message.
            return self.getPath(toolName + 'Path',alt='toolPath') + toolName
        
    def createAnalysisDir(self):
        '''creates analysis level directory'''
        if self.analysisId == None:
            raise Exception('This analysis has not been registered or defined in manifest')    
        if self._analysisDir != None:
            raise Exception('The directory for this analysis has already been created')
            
        self._analysisDir = self.getPath('tmpDir') + self.analysisId.replace(' ','_') + '/'
        if not os.path.isdir(self._analysisDir):
            os.makedirs(self._analysisDir)
        return self._analysisDir
        
    def createTempDir(self, name):
        '''
        Returns a named temporary directory, creating it if necessary
        '''
        # Used for logicalStep dirs. Since steps could run in parallel, tmpDirs are in dict.
        if name in self._tmpDirs:
            raise Exception(name + ' already exists as a temporary directory in this analysis')
            
        tmpdir = self.dir + name.replace(' ','_') + '/'
        if not os.path.isdir(tmpdir):
            os.mkdir(tmpdir)
        self._tmpDirs[name] = tmpdir
        return tmpdir
    
    def registerInputFile(self, name, fileWithPath=None):
        '''
        Registers a single input file by name.  Retrieve again by name.
        Input files reside outside the analysis directory and are input to steps.
        '''
        if fileWithPath != None:
            self._inputFiles[name] = fileWithPath
        return self._inputFiles[name]
    
    def inputFile(self, name):
        return self._inputFiles[name]
        
    def registerInterimOutput(self, name, fileNoPath=None):
        '''
        Registers a single interim output file by name. Retrieve again by name.
        Interim outputs are generated by some steps to be used by other steps.
        They reside in the analysis directory and should be deleted when the 
        analysis concludes.
        '''
        if fileNoPath != None:
            self._interimFiles[name] = self.dir + fileNoPath
        return self._interimFiles[name]
    
    def interimOutput(self, name):
        return self._interimFiles[name]
        
    def registerTargetOutput(self, name, outputNoPath=None):
        '''
        Registers a single target output (typically a file) by name. Retrieve again by name.
        Target outputs are the result of successful steps.  They are written to the analysis
        directory and are expected to be hard-linked outside of it when the analysis completes.
        '''
        if outputNoPath != None:
            self._targetOutput[name] = self.dir + outputNoPath
        return self._targetOutput[name]
    
    def targetOutput(self, name):
        return self._targetOutput[name]
        
    def targetName(self, name):
        '''
        Returns the targetFile Name, stripped of the path.
        '''
        analysisDir, targetName = os.path.split( self.targetOutput(name) )
        return targetName
        
    def linkOrCopy(self, fromLoc, toLoc, soft=False, logOut=True, log=None):
        '''
        Standard call for all cases of moving files/dirs into position.
        '''
        if soft:
            err = self.runCmd('ln -sf ' + fromLoc + ' ' + toLoc, logOut=logOut,log=log)
        else:
            err = self.runCmd('ln -f ' + fromLoc + ' ' + toLoc, logOut=logOut,log=log)
            
        if err != 0:  # If link won't do, then we need to copy. NOTE: use -r because might be dir
            err = self.runCmd('cp -rf ' + fromLoc + ' ' + toLoc, logOut=logOut,log=log)
        
        if err != 0:
            raise Exception("Unable to ln or cp '" + fromLoc + "' to '" + toLoc + "'")
        return err
    
    def getFile(self, name, io='input'):
        '''
        gets the filename to a file we created previously through either 
        registerInputFile/registerTargetOutput OR passed as input in a manifest file.
        '''
        if io == 'input':
            return self._inputFiles[name]
        else:
            return self._targetOutput[name]

    def declareLogFile(self, name=None):
        '''
        Gets or sets the filename for the log that might be created at the analysis level.
        '''
        if self.log != None and self.log.file() != None:
            return self.log.file()  # Could check that name matches log
        if name == None:
            if self._analysisId == None:
                raise Exception("This 'analysis' has not been registered or defined in manifest.")
            name = self._analysisId
        self.log.declareFile(self.dir + name.replace(' ','') + '.log')
        #self.log.empty()  # Analysis log is a running log except when explicitly emptied
        return self.log.file()
        
    def registerStep(self, step):
        '''
        Multiple logical steps can be managed by an analysis simultaneously
        '''
        self._steps.append(step)
        
    def removeStep(self, step):
        '''
        Multiple logical steps can be managed by an analysis simultaneously
        '''
        try:
            self._steps.remove(step)
        except:
            pass
        
    ### Proccessing support ###         
    def deliverFiles(self, step):
        '''
        Delivers interim and target files based upon matching keys.
        about and maybe trashing the directory as well?
        '''
        # Because we do not want to stop the loop for an exception
        # we record exceptions and raise one at the end.
        fails = '' 
        # copy interims
        fullSetOfKeys = self._interimFiles.keys()
        deliveryKeys = fullSetOfKeys
        if self._deliveryKeys != None:
            deliveryKeys = self._deliveryKeys
        for key in deliveryKeys:
            if key not in fullSetOfKeys:
                continue
            try:
                step.convertFileToInterim(key, self._interimFiles[key])
            except:
                fails = fails + "Failed to find interim result for '"+key+"'\n"
        # copy targets
        fullSetOfKeys = self._targetOutput.keys()
        deliveryKeys = fullSetOfKeys
        if self._deliveryKeys != None:
            deliveryKeys = self._deliveryKeys
        for key in deliveryKeys:
            if key not in fullSetOfKeys:
                continue
            try:
                step.convertFileToTarget(key, self._targetOutput[key]) 
            except:
                fails = fails + "Failed to find target result for '"+key+"'\n"
        if len(fails) > 0:
            raise Exception(fails)
    
    def deliveryKeys(self,justThisSet):
        '''
        Register certain keys to be delived in deliverFiles and in this order.
        Without setting this, all keys in interim and target files will be delivered.
        '''
        self._deliveryKeys = justThisSet
        
    def onSucceed(self, step):
        '''
        pipeline will handle all success steps, like copying out files we care
        about and maybe trashing the directory as well?
        '''
        # deliver the files from step to analysis directory
        try:
            self.deliverFiles(step)  
        except:
            pass # descendent classes should consider this an exception
            
        step.log.out("'\n--- End of step ---")
        step.log.dump( self.log.file() ) # to stdout if no runningLog
        # Morgan, do you want the step log going to stdout even if there is an analysis log?
        #if self.log.file() != None:  # If analysis log, be sure to just print step log to stdout
        #    step.log.dump()
        if not self.dryRun():
            step.cleanup()               # Removes step.stepDir()
        else:
            self.log.out('') # skip a lineline
            self.runCmd('ls -l ' + step.dir, dryRun=False)
            self.log.out('')
        self.removeStep(step)  # Do we want to do this?   
        return 0
        
    def onFail(self, step):
        '''
        pipeline will handle failure of logical steps like sweeping the log to the running log
        '''
        step.log.out("\n--- End of step ---")
        step.log.dump(self.log.file()) # to stdout if no runningLog  
        if self.log.file() != None:  # If analysis log, be sure to just print step log to stdout
            step.log.dump()
        if self.dryRun():
            self.log.out('') # skip a lineline
            self.runCmd('ls -l ' + step.dir, dryRun=False)
            self.log.out('')
        self.removeStep(step)  # Do we want to do this?   
        return step.error()
        
    def runCmd(self, cmd, logOut=True, logErr=True, dryRun=None, log=None):
        '''
        Runs the provided command and returns error code.  Does NOT trigger onFail.
        Note that you can pass in a log object if you don't want to use the analysis log.
        '''
        if dryRun == None:
            dryRun=self._dryRun
        if log == None:
            log = self.log
        log.out('> ' + cmd)  # Always log command itself
        if dryRun:
            return 0
        log.close()  # Ensure log is closed so that command redirect can be tacked on
        logFile = log.file()
        if logFile != None and logOut and logErr:
            err = os.system(cmd + ' >> ' + logFile + ' 2>&1')
        elif logFile != None and logErr:
            err = os.system(cmd + ' 2>>' + logFile)
        else:
            err = os.system(cmd)
        return err
        
    def getCmdOut(self, cmd, dryRun=None, logCmd=True, logResult=False, default='', log=None, errOk=False):
        '''
        Runs the provided command and returns the stdout.
        Note that you can pass in a log object if you don't want to use the analysis log.
        '''
        if dryRun == None:
            dryRun=self._dryRun
        if log == None:
            log = self.log
        if logCmd:
            log.out('> ' + cmd)
        if dryRun:
            return default
        err, out = commands.getstatusoutput(cmd)
        if logResult:
            log.out(out)
        if err != 0 and not errOk:
            raise Exception("Running [" + cmd + "] returned '" + str(err))
        if len(out) == 0:
            out = default
        return out


############ command line testing ############
if __name__ == '__main__':
    '''
    Command-line testing
    '''
    print "======== begin '" + sys.argv[0] + "' test ========"
    e3 = Analysis('/hive/users/tdreszer/galaxy/uniformAnalysis/src/test/settingsE3.txt') 

    # test getSetting    
    fastqSampleReads = e3.getSetting('fastqSampleReads','100000')
    print "fastqSampleReads: " + fastqSampleReads
    # Expect exception:
    #flippyFloppy = e3.getSetting('flippyFloppy')

    # test analysisDir which implicitly tests getSetting:    
    e3.analysisId('command-line test') # Should throw exception without this line
    analysisDir = e3.createAnalysisDir()
    print "analysisDir:     " + analysisDir
    
    # test running log which should implicitly test analysisDir   
    runningLog = e3.declareLogFile('running')
    print "runningLog: " + runningLog
    e3.log.empty()  # previous test might have left some junk here
    e3.log.out("--- Beginning Running Log for analysis '" +e3.analysisId()+ "' ---")
    e3.log.out('Log file name: ' + e3.log.file() + '\n')

    # test registerInputFile and registerTargetOutput
    inFile = e3.registerInputFile('fastqRep1',  
        '/cluster/home/mmaddren/grad/pipeline/data/UwDnase/wgEncodeUwDnaseAg04449RawDataRep1.fastq')
    outFile = e3.registerTargetOutput('bamRep1','wgEncodeUwDnaseAg04449RawDataRep1.bam')
    e3.log.out('Known input:   ' + inFile)
    e3.log.out('Target output: ' + e3.getFile('bamRep1', io='target') + '\n')
    
    # test createTempDir and temp log as would be called by logicalSteps
    stepDir = e3.createTempDir('logiStep1')
    print "stepDir:    " + stepDir
    stepLog = Log(stepDir + 'temp.log')
    print "stepLog:    " + stepLog.file()
    stepLog.out('>>> Beginning Step Log ---')
    stepLog.out('Log file name: ' + stepLog.file() + '\n')
    stepLog.out('> fakeGranular -step -1 command\n')
    stepLog.out('> fakeGranularStep -2 command\n')
    stepLog.out('> fake -granularStep -3 command\n')

    # show that both logs are working but have yet to be combined
    print '\n..... Current contents of running log (no step log!):'
    os.system('cat ' + e3.log.file())
    print '...................................................'
    print '\n..... Current contents of step log:'
    os.system('cat ' + stepLog.file())
    print '...................................................'
    
    # end the stepLog as a logical step might
    stepLog.out('<<< End step log ---\n')
    stepLog.dump(e3.log.file())   # this should be done in e3.onSuccess()
    os.system('rm -rf ' + stepDir) # This will be done in logicalStep.cleanup()
    e3.log.out('--- End running log ---')
    print '\n..... Current contents of running log (includes step log):'
    os.system('cat ' + e3.log.file())
    print '...................................................'

    # Restart the running log.  Really this is expected to be called at the start, not the end.
    e3.log.empty()
    e3.log.out('--- New Running Log ---')
    e3.getCmdOut('ls -l '+ e3.getFile('fastqRep1'),logResult=True)
    e3.getCmdOut('ls -l '+ '/cluster/home/mmaddren/grad/pipeline/data/UwDnase/' \
                 + e3.targetName('bamRep1'),logResult=True)
    try:
        e3.getCmdOut('ls -l '+ stepDir,logResult=True)
    except:
        pass
    e3.getCmdOut('ls -l '+ analysisDir,logResult=True)
    print '\n..... Contents of new running log:'
    os.system('cat ' + e3.log.file())
    print '...................................................'
    
    # Not testing:
    # def runProcess(self, cmd)
    # def onSucceed(self, logicalStep)
    # def onFail(self, logicalstep)

    print "======== end '" + sys.argv[0] + "' test ========"

        
