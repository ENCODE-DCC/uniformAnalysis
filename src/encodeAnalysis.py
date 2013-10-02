import os
from jobTree.scriptTree.target import Target
from jobTree.scriptTree.stack import Stack
from src.analysis import Analysis
from src.settings import Settings
from src.pipelines.dnasepipeline import DnasePipeline

class EncodeAnalysis(Analysis):
    
    def __init__(self, settingsFile, manifestFile):

        manifest = Settings(manifestFile)
    
        Experiment.__init__(self, settingsFile, manifest['expId'])
    
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
        self.createExpDir()
        stack = Stack(self.pipeline)
        options = stack.getDefaultOptions()
        options.jobTree = self.getSetting('jobTreePath')
        options.logLevel = 'INFO'
        
        # need to set batch system, big mem/cpu batches
        
        print 'starting jobTree'
        i = stack.startJobTree(options)
        print "success!!!"
    
    
    def runCmd2(self, cmd, stderr):
        stdout = None
        if '>' in cmd:
            splits = cmd.split('>')
            cmd = splits[0].strip()
            stdout = splits[1].strip()
        errstr = ''
        errfile = None
        if stderr != None:
            if not self.args.dryrun:
                errfile = open(stderr, mode='w')
            errstr = ' 2> ' + stderr
        outstr = ''
        outfile = None
        if stdout != None:
            if not self.args.dryrun:
                outfile = open(stdout, mode='w')
            outstr = ' 1> ' + stdout
        self.log('running process...')
        self.logToMaster(cmd + outstr + errstr)
        result = 0
        if not self.args.dryrun:
            result = subprocess.call(cmd, stdout=outfile, stderr=errfile)
        self.log('process completes with exit code ' + str(result))
        if stdout != None and not self.args.dryrun:
            outfile.close()
        if stderr != None and not self.args.dryrun:
            errfile.close()
        return result
