import os, subprocess
from jobTree.scriptTree.target import Target
from jobTree.scriptTree.stack import Stack
from src.analysis import Analysis
from src.settings import Settings
from src.pipelines.dnasePipeline import DnasePipeline

class EncodeAnalysis(Analysis):
    
    def __init__(self, settingsFile, manifestFile):

        manifest = Settings(manifestFile)
    
        Analysis.__init__(self, settingsFile, manifest['expId'])
    
        self.name = manifest['expName']
        self.dataType = manifest['dataType']
        self.readType( manifest['readType'] )
        self.replicates = []
        
        if self.readType() == 'single':
            if 'fileRep1' in manifest:
                self.replicates.append(1)
                self.registerInputFile('fastqRep1', manifest['fileRep1'])
            if 'fileRep2' in manifest:
                self.replicates.append(2)
                self.registerInputFile('fastqRep2', manifest['fileRep2'])

        elif self.readType() == 'paired':
            if 'fileRd1Rep1' in manifest:
                self.replicates.append(1)
                self.registerInputFile('fastqRd1Rep1', manifest['fileRd1Rep1'])
                self.registerInputFile('fastqRd2Rep1', manifest['fileRd2Rep1'])
            if 'fileRd1Rep2' in manifest:
                self.replicates.append(2)
                self.registerInputFile('fastqRd1Rep2', manifest['fileRd1Rep2'])
                self.registerInputFile('fastqRd2Rep2', manifest['fileRd2Rep2'])
            
        self.pipeline = None
        if self.dataType == 'DNAse':
            self.pipeline = DnasePipeline(self)
        else:
            pass

            
    def start(self):
        """
        probably need one of these in experiment
        """
        self.createAnalysisDir()
        stack = Stack(self.pipeline)
        options = stack.getDefaultOptions()
        options.jobTree = self.getSetting('tmpDir') + '/jobTreeRun'
        options.logLevel = 'INFO'
        
        # need to set batch system, big mem/cpu batches
        
        print 'starting jobTree'
        i = stack.startJobTree(options)
        print "success!!!"
    
    def onFail(self, step):
        self.pipeline.stop()
        Analysis.onFail(self, step)
    
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
