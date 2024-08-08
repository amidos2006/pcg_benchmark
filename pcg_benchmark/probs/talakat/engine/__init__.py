import json
import os
import copy
import numpy as np
from .tracery import Grammar
from .core import World
from .agents import AStar, ActionNumber

spawnerGrammar = None
with open(os.path.dirname(__file__) + "/spawnerGrammar.json") as f:
      spawnerGrammar = json.load(f)

parameters = None
with open(os.path.dirname(__file__) + "/parameters.json") as f:
      parameters = json.load(f)

def generateTalakatScript(spawnerSequences):
      is_multiple = hasattr(spawnerSequences[0], "__len__")
      if not is_multiple:
            spawnerSequences = [spawnerSequences]

      tempGrammar = copy.deepcopy(spawnerGrammar)
      spawnerTracery = Grammar(tempGrammar)
            
      input = "{\"spawners\":{"
      index = 0
      for i in range(len(spawnerSequences)-1, -1, -1):
            name = f"spawner_{i}"
            tempSequence = spawnerSequences[index].copy()
            if isinstance(tempSequence, np.ndarray):
                  tempSequence = tempSequence.tolist()
            input += "\"" + name + "\":" + spawnerTracery.flatten_sequence("#origin#", tempSequence) + ","
            tempGrammar["name"].append(name)
            index+=1
      input = input[0:len(input) - 1] + "}, \"boss\":{\"health\": " + str(parameters["maxHealth"]) + ", \"script\":["
      input += "{\"health\":" + "\"" + "1" + "\",\"events\":[" + "\"spawn, spawner_0\"" + "]},"
      input = input[0:len(input) - 1] + "]}}"
      return json.loads(input)

def runGame(jsonScript):
      startWorld = World(parameters["width"], parameters["height"], parameters["maxNumBullets"])
      startWorld.initialize(jsonScript)
      ai = AStar()
      ai.initialize()
      
      results = []
      currentWorld = startWorld
      while not currentWorld.isWon() and not currentWorld.isLose():
            tempWorld = currentWorld.clone()
            tempWorld.hideUnknown = True
            action = ai.getAction(tempWorld, parameters["maxValue"], parameters)
            if action == -1:
                  break
            results.append((currentWorld, action))
            if not currentWorld.update(ActionNumber.getAction(action)) or\
                  len(currentWorld.spawners) > parameters["maxNumSpawners"]:
                  break
      return results

def runPattern(jsonScript):
      startWorld = World(parameters["width"], parameters["height"], parameters["maxNumBullets"])
      startWorld.initialize(jsonScript)
      startWorld.player.invulnerable = True
      results = []
      currentWorld = startWorld
      while not currentWorld.isWon() and not currentWorld.isLose():
            results.append((currentWorld.clone(), ActionNumber.NONE))
            if not currentWorld.update(ActionNumber.getAction(ActionNumber.NONE)) or\
                  len(currentWorld.spawners) > parameters["maxNumSpawners"]:
                  break
      return results