#!/usr/bin/env python2.7
# fastqValidateStep.py module holds FastqValidateStep class which descends from LogicalStep class.
# It performs fastq validation obviously enough.
#
# Inputs: 1 fastq file, pre-registered in the analysis   keyed as:   'tags' + suffix + '.fastq'
#
# Outputs: directory of files (will include html target) keyed as: 'fastqValDir' + suffix
#          zipped file of that directory                 keyed as: 'fastqVal'   + suffix + '.zip'
#          html file in that directory                   keyed as: 'fastqVal'  + suffix + '.html'
#          json file                                     keyed as: 'fastqVal' + suffix + '.json'

from src.logicalStep import LogicalStep
from src.wrappers import ucscUtils, fastqc

class FastqValidationStep(LogicalStep):

    def __init__(self, analysis, suffix=''):
        self.suffix = str(suffix)
        LogicalStep.__init__(self, analysis, 'fastqValidation_' + self.suffix)
        self._stepVersion = self._stepVersion + 0  # Increment allows changing all set versions
        
    def writeVersions(self,raFile=None,allLevels=False):
        '''Writes versions to to the log or a file.'''
        if allLevels:
            LogicalStep.writeVersions(self, raFile)
        if raFile != None:
            raFile.add('ucscUtils', ucscUtils.version(self,tool='fastqStatsAndSubsample'))
            raFile.add('fastqc', fastqc.version(self))
        else:
            ucscUtils.version(self,tool='fastqStatsAndSubsample')
            fastqc.version(self)

    def onRun(self):
        # Inputs:
        fastq = self.ana.getFile('tags' + self.suffix + '.fastq')
        
        # Outputs:  
        valDir = self.declareTargetFile('fastqValDir'+self.suffix,
                                        name='sampleTags_fastqc',ext='dir')
        self.declareTargetFile('fastqVal'+self.suffix+'.zip',name='sampleTags_fastqc', ext='zip')
        self.declareTargetFile('fastqVal'+self.suffix+'.html', 
                               name='sampleTags_fastqc/fastqc_report', ext='html')
        
        sampleFastq = self.declareGarbageFile('sampleTags.fastq')
        simpleStats = self.declareGarbageFile('simpleStats.txt')

        # sample granular step
        ucscUtils.fastqStatsAndSubsample(self,fastq,simpleStats,sampleFastq)

        # sample fastqc step that generates HTML output
        fastqc.validate(self,sampleFastq,valDir)
        
        # json summary:
        if not self.ana.dryRun:
            # grep "Sequence length" t2U1/chr22_r2r1_sample_fastqc/fastqc_data.txt | awk '{print $3}'
            # 50
            qcStats = valDir + "fastqc_data.txt"
            qcSummary = valDir + "summary.txt"
            self.json['baseCount' ] = self.ana.getCmdOut( \
                'grep "baseCount" '+simpleStats+" | head -1 | awk '{print $2}'",logCmd=False)
            self.json['encoding'  ] = self.ana.getCmdOut( \
                'grep "Encoding" '+qcStats+" | head -1 |  cut -f 2",logCmd=False)
            self.json['gcPcnt'    ] = self.ana.getCmdOut( \
                'grep "\%GC" '+qcStats+" | head -1 | awk '{print $2}'",logCmd=False)
            self.json['qualMean'  ] = self.ana.getCmdOut( \
                'grep "qualMean" '+simpleStats+" | head -1 | awk '{print $2}'",logCmd=False)
            self.json['qualSD'    ] = self.ana.getCmdOut( \
                'grep "qualStd" '+simpleStats+" | head -1 | awk '{print $2}'",logCmd=False)
            self.json['tagLength' ] = self.ana.getCmdOut( \
                'grep "Sequence length" '+qcStats+" | head -1 | awk '{print $3}'",logCmd=False)
            self.json['tagLenSD'  ] = self.ana.getCmdOut( \
                'grep "readSizeStd" '+simpleStats+" | head -1 | awk '{print $2}'",logCmd=False)
            self.json['tagsSampled'] = self.ana.getCmdOut( \
                'grep "Total Sequences" '+qcStats + " | head -1 | awk '{print $3}'",logCmd=False)
            self.json['tagsTotal'  ] = self.ana.getCmdOut( \
                'grep "readCount" '+simpleStats+" | head -1 | awk '{print $2}'",logCmd=False)
            self.json['FastQC'] = {}
            self.json['FastQC']['basic'] = self.ana.getCmdOut( \
                'grep "Basic Statistics" '+qcSummary+" | head -1 | awk '{print $1}'",
                logCmd=False)
            self.json['FastQC']['per base quality'] = self.ana.getCmdOut( \
                'grep "base sequence quality" '+qcSummary+" | head -1 | awk '{print $1}'",
                logCmd=False)
            self.json['FastQC']['per tag quality'] = self.ana.getCmdOut( \
                'grep "sequence quality scores" '+qcSummary+" | head -1 | awk '{print $1}'",
                logCmd=False)
            self.json['FastQC']['per base content'] = self.ana.getCmdOut( \
                'grep "base sequence content" '+qcSummary+" | head -1 | awk '{print $1}'",
                logCmd=False)
            self.json['FastQC']['per base GC content'] = self.ana.getCmdOut( \
                'grep "base GC content" '+qcSummary+" | head -1 | awk '{print $1}'",
                logCmd=False)
            self.json['FastQC']['per tag GC content'] = self.ana.getCmdOut( \
                'grep "sequence GC content" '+qcSummary+" | head -1 | awk '{print $1}'",
                logCmd=False)
            self.json['FastQC']['tag length distribution'] = self.ana.getCmdOut( \
                'grep "Sequence Length Dist" '+qcSummary+" | head -1 | awk '{print $1}'",
                logCmd=False)
            self.json['FastQC']['tag duplication levels'] = self.ana.getCmdOut( \
                'grep "Sequence Duplication Levels" '+qcSummary+" | head -1 | awk '{print $1}'",
                logCmd=False)
            self.json['FastQC']['tag over-representation'] = self.ana.getCmdOut( \
                'grep "Overrepresented sequences" '+qcSummary+" | head -1 | awk '{print $1}'",
                logCmd=False)
            self.json['FastQC']['tag K-mer Content'] = self.ana.getCmdOut( \
                'grep "Kmer Content" '+qcSummary+" | head -1 | awk '{print $1}'",
                logCmd=False)
        else:
            self.json['baseCount'  ] = '0'
            self.json['encoding'   ] = 'faked'
            self.json['gcPcnt'     ] = '50'
            self.json['qualMean'   ] = '0'
            self.json['qualSD'     ] = '0'
            self.json['tagLength'  ] = '50'
            self.json['tagLenSD'   ] = '0'
            self.json['tagsSampled'] = '666'
            self.json['tagsTotal'  ] = '999'
            self.json['FastQC'] = {}
            self.json['FastQC']['basic'] = 'PASS'
        self.createAndWriteJsonFile( 'fastqVal'+ self.suffix, target=True )
        

