from ..core import MarioAgent
import numpy as np

class Agent(MarioAgent):
    def initialize(self, model):
        self._choices = []
        # right run
        for _ in range(8):
            self._choices.append([False, True, False, True, False])
        # right jump and run
        for _ in range(8):
            self._choices.append([False, True, False, True, True])
        # right
        for _ in range(4):
            self._choices.append([False, True, False, False, False])
        # right jump
        for _ in range(4):
            self._choices.append([False, True, False, False, True])
        # left
        self._choices.append([True, False, False, False, False])
        # left run
        self._choices.append([True, False, False, True, False])
        # left jump
        self._choices.append([True, False, False, False, True])
        # left jump and run
        self._choices.append([True, False, False, True, True])

    def getActions(self, model):
        return self._choices[self._random.integers(len(self._choices))]

    def getAgentName(self):
        return "RandomAgent"