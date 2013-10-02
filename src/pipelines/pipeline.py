from jobTree.scriptTree.target import Target

class RunSequence(Target):

    def __init__(self, workqueue, ram=1000000000, cpus=1):
        Target.__init__(self, time=0.00025, memory=ram, cpu=cpus)
        self.workqueue = workqueue
        
    def run(self):
        self.addChildTarget(self.workqueue.pop(0))
        if len(self.workqueue) > 0:
            self.setFollowOnTarget(RunSequence(self.workqueue))

class Pipeline(Target):
    """
    Pipelines will be lightweight objects which contain essentially just a
    list of the steps needed to be taken. We might want to start by designing
    the system such that there's a single-experiment part and a full part
    """
    
    def __init__(self, experiment, ram=1000000000, cpus=1):
        Target.__init__(self, time=0.00025, memory=ram, cpu=cpus)
        self.experiment = experiment
        
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
        
    def run(self):
        if 1 in self.experiment.replicates:
            self.addChildTarget(RunSequence(self.getSingleReplicatePipeline(1)))
        if 2 in self.experiment.replicates:
            self.addChildTarget(RunSequence(self.getSingleReplicatePipeline(2)))
            
        
            