########### OBSOLETE!  Replaced by BamEvaluateStep.py ############
########### OBSOLETE!  Replaced by BamEvaluateStep.py ############
########### OBSOLETE!  Replaced by BamEvaluateStep.py ############

#!/usr/bin/env python2.7
# samplebamstep.py module holds SampleBamStep class which descends from LogicalStep class.
# It takes a sample of a bam and converts it to a sam file
#
# Inputs: 1 bam, pre-registered in the analysis keyed as: 'bamRep' + replicate
#
# Outputs: 1 interim sam file, keyed as: 'samSample' + replicate

from src.logicalstep import LogicalStep
from src.wrappers import samtools, sampleBam, bedtools

class SampleBamStep(LogicalStep):

    def __init__(self, analysis, replicate, sampleSize):
        self.replicate = str(replicate)
        self.sampleSize = sampleSize
        LogicalStep.__init__(self, analysis, 'sampleBam_Rep' + self.replicate)
        #self.bam = bam

    def writeVersions(self,file=None):
        '''Writes versions to to the log or a file.'''
        if file != None:
            #   writes self._stepVersion and each tool version to the file
            pass
        else:
            samtools.version(self)
            sampleBam.version(self)
            bedtools.version(self)

    def onRun(self):      
        self.writeVersions()

        # Versions:
        samtools.version(self)
        sampleBam.version(self)
        bedtools.version(self)
        
        # Outputs:
        samSample = self.declareInterimFile('samSampleRep' + self.replicate, ext='sam')
        #bamSample = self.declareTargetFile( 'bamSampleRep' + self.replicate, ext='bam')
        
        # Inputs:
        bam = self.ana.getFile('bamRep' + self.replicate)
        
        bamSize = samtools.bamSize(self,bam)
        # Take the whole bam if it is smaller than sampleSize requested.        
        if self.sampleSize > bamSize:
            self.sampleSize=bamSize
        
        bed = self.declareGarbageFile('bed')
        
        sampleBam.sample(self,bam,bamSize,sampleSize,bed)
        bedtools.bedToSam(self,bed,samSample)

