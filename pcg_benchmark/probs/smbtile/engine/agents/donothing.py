from ..core import MarioAgent
from ..helper import MarioActions

class Agent(MarioAgent):
    def initialize(self, model):
        return
    
    def getActions(self, model):
        return [False] * MarioActions.numberOfActions()
    
    def getAgentName(self):
        return "DoNothingAgent"