import os, subprocess, shutil, json
from jobTree.scriptTree.target import Target
from jobTree.scriptTree.stack import Stack
from ra.raFile import RaFile
from src.analysis import Analysis
from src.settings import Settings
from src.pipelines.dnasePipeline import DnasePipeline

class EncodeAnalysis(Analysis):
    
    def __init__(self, settingsFile, manifestFile, resume=0):

        manifest = Settings(manifestFile)
    
        Analysis.__init__(self, settingsFile, manifest['expName'])

        self.resume = resume
        
        self.name = manifest['expName']
        self.dataType = manifest['dataType']
        self.readType = manifest['readType']
        self.replicates = []
        
        self.json = {}
        
        if self.readType == 'single':
            if 'fileRep1' in manifest:
                self.replicates.append(1)
                self.registerInputFile('tagsRep1.fastq', manifest['fileRep1'])
            if 'fileRep2' in manifest:
                self.replicates.append(2)
                self.registerInputFile('tagsRep2.fastq', manifest['fileRep2'])

        elif self.readType == 'paired':
            if 'fileRd1Rep1' in manifest:
                self.replicates.append(1)
                self.registerInputFile('tagsRd1Rep1.fastq', manifest['fileRd1Rep1'])
                self.registerInputFile('tagsRd2Rep1.fastq', manifest['fileRd2Rep1'])
            if 'fileRd1Rep2' in manifest:
                self.replicates.append(2)
                self.registerInputFile('tagsRd1Rep2.fastq', manifest['fileRd1Rep2'])
                self.registerInputFile('tagsRd2Rep2.fastq', manifest['fileRd2Rep2'])
            
        self.interimDir = None
        self.targetDir = None    
        self.pipeline = None
        if self.dataType == 'DNAse':
            self.pipeline = DnasePipeline(self)
        else:
            pass

            
    def start(self):
        """
        probably need one of these in experiment
        """
        if self.resume == 0:
            self.createAnalysisDir()
        stack = Stack(self.pipeline)
        options = stack.getDefaultOptions()
        options.jobTree = self.dir + 'jobTreeRun'
        if self.resume != 0 and os.path.exists(self.dir + 'jobTreeRun'):
            shutil.rmtree(self.dir + 'jobTreeRun')
        options.logLevel = 'INFO'
        
        # need to set batch system, big mem/cpu batches
        
        print 'starting jobTree'
        i = stack.startJobTree(options)
        print "success!!!"
    
    def onFail(self, step):
        self.pipeline.stop()
        Analysis.onFail(self, step)
        raise Exception('just failing')
    
    def getFile(self, name):
        if name in self._inputFiles:
            return self._inputFiles[name]
        elif os.path.isfile(self.interimDir + name):
            return self.interimDir + name
        elif os.path.isfile(self.targetDir + name):
            return self.targetDir + name
        raise Exception('file ' + name + ' not found')
    
    def createAnalysisDir(self):
        Analysis.createAnalysisDir(self)
        self.interimDir = self.dir + 'interim/'
        os.mkdir(self.interimDir)
        self.targetDir = self.dir + 'target/'
        os.mkdir(self.targetDir)
        
    def deliverFiles(self, step):
        subDir = self.dir + step.name + '_submit/'
        os.mkdir(subDir)
    
        for k in step.interimFiles:
            if not os.path.exists(step.interimFiles[k]):
                raise Exception('file not found: ' + step.interimFiles[k])
            splits = k.split('/')
            localName = splits[len(splits) - 1]
            #os.rename(step.interimFiles[k], self.interimDir + localName)
            err = self.runCmd('mv {old} {to}'.format(old=step.interimFiles[k], to=self.interimDir + localName), dryRun=False, log=step.log)
        if len(step.targetFiles) > 0:
            #md = self.createMetadataFile(step, 'files')
            for k in step.targetFiles:
                if not os.path.exists(step.targetFiles[k]):
                    raise Exception('file not found: ' + step.targetFiles[k])
                splits = k.split('/')
                localName = splits[len(splits) - 1]
                #os.rename(step.targetFiles[k], self.targetDir + localName)
                err = self.runCmd('mv {old} {to}'.format(old=step.targetFiles[k], to=self.targetDir + localName), dryRun=False, log=step.log)
                err = self.runCmd('cp {old} {to}'.format(old=self.targetDir + localName, to=subDir + localName), dryRun=False, log=step.log)
                #shutil.copy(self.targetDir + localName, subDir + localName)
                
                # TODO: relevant metadata needs to be put into the steps
                #md.createStanza('object', localName)
                #md.add('fileName', subDir + localName)
                #md.add('readType', self.readType)
                #md.add('expId', self.id)
                #md.add('replicate', step.replicate) # this breaks after single-replicate
                
        for f in step.metaFiles:
            step.metaFiles[f].write()
            os.rename(step.metaFiles[f].filename, subDir + f + '.ra')
            
        if step.json:
            fp = open(subDir + step.name + '.json', 'w')
            json.dump(step.json, fp, sort_keys=True, indent=4, separators=(',', ': '))
            fp.close()
    
    def onSucceed(self, step):
        self.deliverFiles(step)
        step.log.out("'\n--- End of step ---")
        step.log.dump( self.log.file() )
        #step.cleanup()
    
    def createMetadataFile(self, step, name):
        if name in step.metaFiles:
            raise Exception('metadata file already exists')
        step.metaFiles[name] = RaFile(step.dir + name + '.ra')
        return step.metaFiles[name]
    
    def onRun(self, step):
        versions = self.createMetadataFile(step, 'versions')
        versions.createStanza('pipeline', self.pipeline.version)
        versions.add(step.name, step.version)
        step.writeVersions(versions)
        
    
    def runCmd2(self, cmd, logOut=True, logErr=True, dryRun=None, log=None):
        if log == None:
            log = self.log
        
        log.out('> ' + cmd)
        #log.close()
        
        if dryRun:
            return
        
        stdout = None
        outfile = None
        if '>' in cmd:
            splits = cmd.split('>')
            cmd = splits[0].strip()
            stdout = splits[1].strip()
            outfile = open(stdout, 'w')
        
            
        result = subprocess.call(cmd, stdout=outfile, stderr=log._log)
        #self.log('process completes with exit code ' + str(result))

        return result
