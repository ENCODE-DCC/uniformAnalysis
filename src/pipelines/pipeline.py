from jobTree.scriptTree.target import Target

class RunSequence(Target):

    def __init__(self, pipeline, workqueue, ram=1000000000, cpus=1):
        Target.__init__(self, time=0.00025, memory=ram, cpu=cpus)
        self.workqueue = workqueue
        self.pipeline = pipeline
        
    def run(self):
        if not self.pipeline.running:
            return
    
        self.addChildTarget(self.workqueue.pop(0))
        if len(self.workqueue) > 0:
            self.setFollowOnTarget(RunSequence(self.pipeline, self.workqueue))

class Pipeline(Target):
    """
    Pipelines will be lightweight objects which contain essentially just a
    list of the steps needed to be taken. We might want to start by designing
    the system such that there's a single-analysis part and a full part
    """
    
    def __init__(self, analysis, ram=1000000000, cpus=1):
        Target.__init__(self, time=0.00025, memory=ram, cpu=cpus)
        self.analysis = analysis
        self.running = False
        
    def getSingleReplicatePipeline(self, replicate):
        """
        Gets the single-replicate part of the pipeline. This allows each
        replicate to be handled separately.
        """
        pass
       
    def getSecondPartPipeline(self):
        """
        Gets the second part of the pipeline. This would be after both
        replicates have been run.
        """
        pass
        
    def stop(self):
        self.running = False
        
    def run(self):
        self.running = True
        if 1 in self.analysis.replicates:
            self.addChildTarget(RunSequence(self, self.getSingleReplicatePipeline(1)))
        if 2 in self.analysis.replicates:
            self.addChildTarget(RunSequence(self, self.getSingleReplicatePipeline(2)))
            
        
            