from src.pipelines.pipeline import Pipeline

from src.steps.alignmentStep import AlignmentStep
from src.steps.bamEvaluateStep import BamEvaluateStep
from src.steps.hotspotStep import HotspotStep

class DnasePipeline(Pipeline):
    """
    Pipeline for DNAse
    """
    
    def __init__(self, analysis):
        Pipeline.__init__(self, analysis)
        self.version = '0.9'
        
    def getSingleReplicatePipeline(self, replicate):
        return [
            AlignmentStep(self.analysis, replicate),
            BamEvaluateStep(self.analysis, replicate, 5000000),
            HotspotStep(self.analysis, replicate)
        ]
       
    def getSecondPartPipeline(self):
        """
        Gets the second part of the pipeline. This would be after both
        replicates have been run.
        """
        pass
        
    