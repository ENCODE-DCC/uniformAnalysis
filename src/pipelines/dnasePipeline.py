from src.pipelines.pipeline import Pipeline
from src.steps.alignmentstep import AlignmentStep

class DnasePipeline(Pipeline):
    """
    Pipeline for DNAse
    """
    
    def __init__(self, experiment):
        Pipeline.__init__(self, experiment)
        
    def getSingleReplicatePipeline(self, replicate):
        return [ AlignmentStep(self.experiment, replicate) ]
       
    def getSecondPartPipeline(self):
        """
        Gets the second part of the pipeline. This would be after both
        replicates have been run.
        """
        pass
        
    