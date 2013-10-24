import sys, pprint, traceback
from datetime import datetime
from jobTree.scriptTree.target import Target
from analysis import Analysis
from log import Log

class StepError(Exception):
    
    def __init__(self, step=None, message=None):
        self.message = message
        pass


class LogicalStep(Target):
    '''
    defines a single logical step of the pipeline (like alignment) that has
    control over its own temp directory
    '''
    
    @property
    def ana(self):
        return self._analysis
    
    @property
    def analysis(self):
        return self._analysis
    
    @property
    def dir(self):
        '''Returns the temporary logical step directory'''
        if self._dir == None:
            raise Exception("Trying to retrieve directory before its been created")
        return self._dir
        
    @property
    def name(self):
        return self._stepName
    
    @property
    def version(self):
        return self.analysis.version + '.' + str(self._stepVersion)
        
    def __init__(self, analysis, stepName, ram=1000000000, cpus=1):
        Target.__init__(self, time=0.00025, memory=ram, cpu=cpus)
        self._stepVersion = 1
        self._analysis = analysis
        self.targetFiles = {}
        self.interimFiles = {}
        self.garbageFiles = {}
        self.metaFiles = {}
        self.log = Log() # Before logfile is declared, log print to stdout
        self._stepName = stepName # descendent classes MUST fill in the _stepName
        self._err = -1 # descendent classes should set this to returns from ganular steps
        self._status = 'Init' # Init/Running/Success/Fail
        self._dir = None # needs to make temp directory for itself
        self.analysis.registerStep(self)  # Analysis may manage multiple steps simultaneously

    def __str__(self):
        return pprint.pformat(self)
        
    def run(self):
        self._status = 'Running'
        self.createDir()
        self.declareLogFile() # Ensures that the logical step dir and log exist
        self.log.out("--- Beginning '" + self._stepName + "' [version: "+self.version+"] [" + 
                     datetime.now().strftime("%Y-%m-%d %X (%A)")+ '] ---')
        try:
            self.ana.onRun(self)
            self.onRun() #now this calls child onRun directly
        except StepError as e:
            self.onFail(e)
            return self._err
        except Exception as e:
            self.onFail(e, logTrace=True)
            return self._err
        self.success()  # success() must be outside of try or else we loose any exeptions
        return 0
        
    def onRun(self):
        '''this part would likely be overridden for each logical step'''
        raise Exception('children need to override this')
        
    def encodeDebug(self, message):
        self.logToMaster(message)
        
    def success(self):
        self._status = 'Success'
        self._err = 0 # by definition
        self.log.out("\n>> Successfully completed '" + self._stepName + "'\n")
        self.analysis.onSucceed(self)
        
    def fail(self, message):
        raise StepError(message)
    
    def onFail(self, e, logTrace=False):
        self._status = 'Fail'
        self.log.out(">>> Failure during '" + self._stepName + ': ' + str(e) + "'\n")
        if logTrace:
            self.log.out(traceback.format_exc())
        self.analysis.onFail(self)

            
    def status(self):
        '''
        Returns status of step: Init/Running/Success/Fail.
        '''
        return self._status
        
    def error(self):
        '''
        Returns the last error code saved from a granular step
        '''
        return self._err
        
    def createDir(self):
        '''Creates logical step directory'''
        self._dir = self.analysis.createTempDir(self.name)
       
    def declareTargetFile(self, key, name=None, ext=None):
        '''
        Reserves name for a file we want to keep permanantly, and returns a
        fully qualified filename in the local temp dir
        '''
        self.targetFiles[key] = self.makeFilePath(key, name, ext)
        return self.targetFiles[key]
        
    def declareInterimFile(self, key, name=None, ext=None):
        '''
        Reserves name for a file we want to keep for part or all of the
        duration of the pipeline before being deleted, and returns a fully
        qualified filename in the local temp dir
        '''
        self.interimFiles[key] = self.makeFilePath(key, name, ext)
        return self.interimFiles[key]
        
    def declareGarbageFile(self, key, name=None, ext=None):
        '''
        Reserves name for a file we do not care about, and returns a fully
        qualified filename in the local temp dir
        '''
        self.garbageFiles[key] = self.makeFilePath(key, name, ext)
        return self.garbageFiles[key]
        
    def declareLogFile(self, name=None):
        '''
        Gets or sets the filename for the log that will be created by this logical step.
        '''
        if self.log != None and self.log.file() != None and name != None:
            return self.log.file()
        #self.encodeDebug(str(self))
        if name == None:
            if self._stepName != None:
                name = self._stepName
            else:
                raise Exception("This 'logical step' has not been named.")
        self.log.declareFile(self.dir + name.replace(' ','_') + '.log')
        self.log.empty()  # Logical step log always starts empty!
        return self.log.file()
        
    def convertFileToTarget(self, name, pathToTarget):
        '''
        Hard links a 'target' file to the analysis 'target' file in the analysis directory.
        This is expected when a logical step succeeds.
        '''
        return self.analysis.linkOrCopy(self.targetFiles[name], pathToTarget, log=self.log)

    def convertFileToInterim(self, name, pathToInterim):
        '''
        Hard links a 'interim' file to the analysis 'interim' file in the analysis directory.
        This is expected when a logical step succeeds.
        '''
        return self.analysis.linkOrCopy(self.interimFiles[name], pathToInterim, log=self.log)

    def cleanup(self):
        '''
        Removes the temporary 'step' directory and all of its contents.
        This is expected when a logical step succeeds.
        '''
        if self._dir != None:
            self.analysis.runCmd('rm -rf ' + self._dir)
        #self._analysis.removeStep(self)  # Do we want to do this?
        
    def makeFilePath(self, key, name=None, ext=None):
        '''
        Returns a fully qualified file/dir name
        '''
        if ext == None:
            if name == None:
                ext = key
            else:
                ext = ''
        if name == None:
            name = key
        if ext.lower() == 'dir':  # directories are also supported!
            if not name.endswith('/'):
                ext = '/'
        elif len(ext) > 0 and not ext.startswith('.'):
            ext = '.' + ext
        return self.dir + name + ext
    
    def toolBegins(self, toolName):
        '''Standardized message before tool comandline'''
        self.log.out("\n# " + datetime.now().strftime("%Y-%m-%d %X") + " '" + toolName + \
                     "' begins...")
        
    def toolEnds(self,toolName,retVal,raiseError=True):
        '''Standardized message after tool comandline.  Raise exception for non-zero retVal.'''
        self.log.out("# "+datetime.now().strftime("%Y-%m-%d %X") + " '" + toolName + \
                     "' returned " + str(retVal))
        if raiseError and retVal != 0:
            raise StepError(toolName)


############ command line testing ############
if __name__ == '__main__':
    '''
    Command-line testing
    '''
    print "======== begin '" + sys.argv[0] + "' test ========"
    e3 = Analysis('/hive/users/tdreszer/galaxy/galaxy-dist/tools/encode/settingsE3.txt',
                      analysisId='command-line test')
    samInterim = e3.registerInterimOutput('sam',e3.dir + 'rep1Interim.sam')
    bamTarget = e3.registerTargetOutput( 'bam',e3.dir + 'rep1Target.bam')
    
    ls = LogicalStep(e3,stepName='test Logical Step') 
    sai1 = ls.declareGarbageFile('read1','sai')
    sai2 = ls.declareGarbageFile('read2','sai')
    sam = ls.declareInterimFile('sam')
    bam = ls.declareAnalysisFile('bam')
    ls.run() # should create temp dir, logFile etc.
    # fake some outputs
    e3.getCmdOut('echo sai1 > '+ sai1,logResult=True, log=ls.log)
    e3.getCmdOut('echo sam > '+ sam,logResult=True, log=ls.log)
    e3.getCmdOut('echo bam > '+ bam,logResult=True, log=ls.log)
    
    # try failure:
    #ls._err = 1 # cheating since no granular steps are run
    #exit(ls.fail())
    

    # try success:
    ls.success()
    
    # Note this test avoids writting to a analysis level log!
    cmd = 'ls -l '+ e3.dir
    print '\n> ' + cmd
    print e3.getCmdOut(cmd,logResult=False)

    print "======== end '" + sys.argv[0] + "' test ========"
