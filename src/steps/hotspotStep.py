from src.logicalStep import LogicalStep
from src.wrappers import hotspot

class AlignmentStep(LogicalStep):

    def __init__(self, experiment, replicate):
        self.replicate = str(replicate)
        LogicalStep.__init__(self, experiment, experiment.readType() + 'Hotspot_Rep' + self.replicate)

    def onRun(self):
        # Versions:
        hotspot.version(self)
        
        tokensName = self.declareGarbageFile('tokens.txt')
        runhotspotName = self.declareGarbageFile('runhotspot.sh')
        
        hotspot.runHotspot(self, tokensName, runhotspotName)

