from .core import MarioGame, MarioAgent
from importlib import import_module


def runLevel(levelString, agentName, gameTime = 20, iterations = 100, stickyActions = 8, marioState = 0, seed = None):
    MarioAgent.iterations = iterations
    MarioAgent.stickyActions = stickyActions
    game = MarioGame()
    agentModule = import_module(f"{__package__}.agents.{agentName}")
    return game.runGame(agentModule.Agent(seed), levelString, gameTime, marioState)