from src.pipelines.pipeline import Pipeline

from src.steps.alignmentStep import AlignmentStep
from src.steps.bamEvaluateStep import BamEvaluateStep
from src.steps.hotspotStep import HotspotStep
from src.steps.mergeBamStep import MergeBamStep

class DnasePipeline(Pipeline):
    """
    Pipeline for DNAse
    """
    
    def __init__(self, analysis):
        Pipeline.__init__(self, analysis)
        self.version = '1'
        
    def getSingleReplicatePipeline(self, replicate):
        return [
            AlignmentStep(self.analysis, replicate),
            BamEvaluateStep(self.analysis, replicate, 5000000),
            HotspotStep(self.analysis, 'Rep' + str(replicate)),
            HotspotStep(self.analysis, 'Rep' + str(replicate) + '5M')
        ]
       
    def getSecondPartPipeline(self):
        """
        Gets the second part of the pipeline. This would be after both
        replicates have been run.
        """
        return [
            MergeBamStep(self.analysis, 1, 2),
            HotspotStep(self.analysis, 'Rep1Rep2')
        ]
        
    