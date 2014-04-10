import os, sys, pprint, traceback, json
from datetime import datetime
from jobTree.scriptTree.target import Target
from ra.raFile import RaFile
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
        return self.ana.version + '.' + str(self._stepVersion)
        
    @property
    def err(self):
        return self._err
    
    @err.setter
    def err(self,value):
        self._err = value

    @property
    def status(self):
        '''Returns status of step: Init/Running/Success/Fail.'''
        return self._status
        
    def __init__(self, analysis, stepName, ram=1000000000, cpus=1):
        Target.__init__(self, time=0.00025, memory=ram, cpu=cpus)
        self._stepVersion = 1
        self._analysis = analysis
        self.interimFiles = {}
        self.targetFiles = {}
        self._garbageFiles = {}
        self.metaFiles = {}  # ???
        self.json = {}
        self.log = Log() # Before logfile is declared, log print to stdout
        self._stepName = stepName # descendent classes MUST fill in the _stepName
        self._err = -1 # descendent classes should set this to returns from ganular steps
        self._status = 'Init' # Init/Running/Success/Fail
        self._dir = None # needs to make temp directory for itself
        self.ana.registerStep(self)  # Analysis may manage multiple steps simultaneously

    def __str__(self):
        return pprint.pformat(self)
        
    def run(self):
        self._status = 'Running'
        self.createDir()
        self.declareLogFile() # Ensures that the logical step dir and log exist
        self.log.out("--- Beginning '" + self._stepName + "' [version: "+self.version+"] [" + 
                     datetime.now().strftime("%Y-%m-%d %X (%A)")+ '] ---')
        self._prevDir = os.getcwd()
        os.chdir(self.dir)
        self.log.out("> cd "+self.dir)
        try:
            self.ana.onRun(self)
            self.onRun() #now this calls child onRun directly
        except StepError as e:
            return self.onFail(e)
        except Exception as e:
            return self.onFail(e, logTrace=True)
        self.success()  # success() must be outside of try or else we loose any exeptions
        return 0
        
    def onRun(self):
        '''this part would likely be overridden for each logical step'''
        raise Exception('children need to override this')
        
    def encodeDebug(self, message):
        self.logToMaster(message)
        
    def success(self):
        self._status = 'Success'
        if self.ana.dryRun:
            self.mockUpResults()
        for fileName in self.metaFiles:
            self.metaFiles[fileName].write()
        self._err = 0 # by definition
        os.chdir(self._prevDir)
        #self.log.out("> cd "+self._prevDir)
        self.log.out("\n>> Successfully completed '" + self._stepName + "'\n")
        self.ana.onSucceed(self)
        
    def fail(self, message):
        raise StepError(message)
    
    def onFail(self, e, logTrace=False):
        self._status = 'Fail'
        self.log.out(">>> Failure during '" + self._stepName + ': ' + str(e) + "'\n")
        if logTrace:
            self.log.out(traceback.format_exc())
        if self._err == 0:
            self._err = 1  # Make sure this error is noticed!
        return self.ana.onFail(self)

    def createDir(self):
        '''Creates logical step directory'''
        self._dir = self.ana.createTempDir(self.name, clean=True)
        
    def fileNameOrFullPath(self, filePath):
        '''Returns just the file name or the full path as appropriate'''
        if filePath.endswith('/') or not filePath.startswith(self.dir):
            return filePath
        else:   # Since file is in step dir, and so is execution, just return name
            return os.path.split(filePath)[1]
       
    def declareTargetFile(self, key, name=None, ext=''):
        '''
        Reserves name for a file we want to keep permanantly, and returns a
        fully qualified filename in the local temp dir
        '''
        self.targetFiles[key] = self.makeFilePath(key, name, ext)
        return self.fileNameOrFullPath(self.targetFiles[key])
        
    def declareInterimFile(self, key, name=None, ext=''):
        '''
        Reserves name for a file we want to keep during the life of the analysis, and returns a
        fully qualified filename in the local temp dir
        '''
        self.interimFiles[key] = self.makeFilePath(key, name, ext)
        return self.fileNameOrFullPath(self.interimFiles[key])

        
    def declareGarbageFile(self, key, name=None, ext=''):
        '''
        Reserves name for a file we do not care about, and returns a fully
        qualified filename in the local temp dir
        '''
        self._garbageFiles[key] = self.makeFilePath(key, name, ext)
        return self.fileNameOrFullPath(self._garbageFiles[key])
        
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
        
    def mockUpPath(self,path,show=False):
        '''Touch a file or make a directory'''
        if path.endswith('/'):
            self.ana.runCmd('mkdir -p '+path,logOut=show,logErr=show,dryRun=False,log=self.log)
        else:
            dirt = os.path.split( path )[0]
            self.ana.runCmd('mkdir -p '+dirt,logOut=show,logErr=show,dryRun=False,log=self.log)
            self.ana.runCmd('touch -a '+path,logOut=show,logErr=show,dryRun=False,log=self.log)
        
    def mockUpResults(self):
        '''
        For each result file, will create it empty if it does not exist.
        This is used to mock up results in a dry run.
        '''
        for key in self.targetFiles.keys():
            self.mockUpPath(self.targetFiles[key],True)
        for key in self.interimFiles.keys():
            self.mockUpPath(self.interimFiles[key],True)

    def deliverTargetFile(self, name, pathToTarget):
        '''
        Hard links a step 'target' file to the analysis 'target' file in
        the analysis directory. This is expected when a logical step succeeds.
        '''
        # Because dryRun should mock up result files, we should set dryRun to False to actually
        # make links to the mocked up files.
        return self.ana.linkOrCopy(self.targetFiles[name], pathToTarget,
                                   logOut=True,dryRun=False,log=self.log)

    def deliverInterimFile(self, name, pathToInterim):
        '''
        Hard links a step 'target' file to the analysis 'target' file in
        the analysis directory. This is expected when a logical step succeeds.
        '''
        # Because dryRun should mock up result files, we should set dryRun to False to actually
        # make links to the mocked up files.
        return self.ana.linkOrCopy(self.interimFiles[name], pathToInterim,
                                   logOut=True,dryRun=False,log=self.log)

    def deliverResultFile(self, name, pathToTarget):
        '''
        Hard links a step 'result' file to the analysis 'interim' or 'target' file in
        the analysis directory. This is expected when a logical step succeeds.
        '''
        try:
            return self.deliverTargetFile(name, pathToTarget)
        except:
            return self.deliverInterimFile(name, pathToTarget)

    def cleanup(self):
        '''
        Removes the temporary 'step' directory and all of its contents.
        This is expected when a logical step succeeds.
        '''
        if self._dir != None:
            self.ana.runCmd('rm -rf ' + self._dir)
        #self._analysis.removeStep(self)  # Do we want to do this?
        
    def makeFilePath(self, key, name=None, ext=''):
        '''
        Returns a fully qualified file/dir name
        '''
        if name == None:
            name = key
        if len(ext) > 0:
            if ext.lower() == 'dir':  # directories are also supported!
                if not name.endswith('/'):
                    ext = '/'
            elif not ext.startswith('.'):
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
        if raiseError and not retVal == 0:
            self._err = retVal
            self.fail(toolName + " returned " + str(self._err))

    def writeVersions(self,raFile=None):
        '''Writes versions to to the log or a file.'''
        # Each logical step is expected to extend or replace this to record the actual tool versions
        if raFile != None:
            raFile.add("ENCODE_Analysis_pipeline",self.ana.version)
            self.log.out("# ENCODE Analysis pipeline [version: " + self.ana.version + "]")
            raFile.add(self.name+'_Step',self.version)
            self.log.out("# "+self.name+"_Step [version: " + self.version + "]")
        else:
            self.log.out("# ENCODE Analysis pipeline [version: "+self.ana.version+"]")
            self.log.out("# "+self.name+"_Step [version: "+self.version+ "]")
            
    def createAndWriteJsonFile(self, name=None, target=False, jsonObj=None):
        '''
        Creates and writes the json object as an interim file keyed as {name}.ra.
        '''
        if name == None:
            name = self.name
        if target:
            filePath = self.declareTargetFile(name + '.json')
        else:
            filePath = self.declareInterimFile(name + '.json')
        if jsonObj == None:
            jsonObj = self.json
        if jsonObj:
            fp = open(filePath, 'w')
            json.dump(jsonObj, fp, sort_keys=True, indent=4, separators=(',', ': '))
            fp.close()

    def createMetadataFile(self, name, target=False):
        '''
        Creates a metadata file as an interim file keyed as {name}.ra.
        '''
        if name in self.metaFiles:
            raise Exception('metadata file already exists')
        if target:
            filePath = self.declareTargetFile(name + '.ra')
        else:
            filePath = self.declareInterimFile(name + '.ra')
        self.metaFiles[name] = RaFile(filePath)
        return self.metaFiles[name]
    
    def printPaths(self, tab, log=None):
        '''Used in debugging; prints step's paths, etc.'''
        if log == None:
            log = self.log
        if self._dir != None:
            title = self.name + ' dir:'
            log.out(title.ljust(tab) + self.dir )
        if self.log.file() != None:
            title = self.name + ' log:'
            log.out(title.ljust(tab) + self.log.file() )
        for key in sorted( self._garbageFiles.keys() ):
            title = "garbage[%s]:" % (key)
            log.out(title.ljust(tab) + self._garbageFiles[key])
        for key in sorted( self.interimFiles.keys() ):
            title = "interimFile[%s]:" % (key)
            log.out(title.ljust(tab) + self.interimFiles[key])
        for key in sorted( self.targetFiles.keys() ):
            title = "targetFile[%s]:" % (key)
            log.out(title.ljust(tab) + self.targetFiles[key])

    def getToolVersion(self, executable, logOut=True):
        '''
        Retrieves tool version, but if there is no success, then the version is the md5sum.
        '''
        if executable.find('/') == -1: # Not a path, then look for this on the path!
            toolId = self.ana.getCmdOut("md5sum `which "+executable+"` | awk '{print $1}'", \
                                        dryRun=False,logCmd=False)
            if toolId.startswith('which: no'): # failed to find executable: might be perl script
                toolId = self.ana.getCmdOut("md5sum "+self.ana.toolsDir + executable + \
                                            " | awk '{print $1}'",dryRun=False,logCmd=False)
                if toolId.startswith('md5sum: '): # failed to find executable
                    toolId = ""
            toolName = executable
        else:
            toolId = self.ana.getCmdOut("md5sum "+executable+" | awk '{print $1}'", \
                                        dryRun=False,logCmd=False)
            if toolId.startswith('md5sum: '): # failed to find executable
                toolId = ""
            toolName = os.path.split( executable )[1]

        toolData = self.ana.getToolData(toolId, toolName)
        if toolData == None:
            version = 'md5sum:'+toolId  # when all else fails
            if logOut:
                self.log.out("# tool: "+toolName+" [version: " + version + "]")
            return version

        try:
            version = toolData['version']
        except:
            try:
                version = toolData['packageVersion']
            except:
                raise Exception("Tool '"+executable+"' was found in tool database, " + \
                                "but 'version' was not!")

        # Try to get actual version and compare the two
        if 'versionCommand' in toolData:
            actual = self.ana.getCmdOut(toolData['versionCommand'],dryRun=False,logCmd=False)
            if version != actual:
                if self.ana.strict:
                    raise Exception("Expecting "+executable+" [version: "+version+"], " + \
                                    "but found [version: "+actual+"]")
                version = actual # Use actual rather than expected.

        # If the toolData was found by name, then the tooldIds may not match, so:
        if toolId != toolData['toolId'] and toolId != "":
            version += ' (md5sum:'+toolId+')' 

        # If there is a package name or version that differs, then use it
        intro = "tool: "
        if 'packageName' in toolData and 'packageVersion' in toolData:
            package = toolData['packageName']
            packageVersion = toolData['packageVersion']
            if packageVersion != version or package.lower() != toolName.lower():
                toolName = package+'('+toolName+')' 
                intro = "package(tool): "
                if packageVersion != version:
                    version = packageVersion+'('+version+')' 
            
        if logOut:
            self.log.out("# "+intro+toolName+" [version: " + version + "]")

        return version
            
        

############ command line testing ############
if __name__ == '__main__':
    '''
    Command-line testing - WARNING: out of date
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
