import math

class ClearEvent:
    def __init__(self, name):
        self.name = name

    def apply(self, world, x, y):
        if self.name.lower() == "bullet":
            world.removeAllBullets()
        elif self.name.lower() == "spawner":
            world.removeAllSpawners()
        else:
            world.removeSpawners(self.name.lower())

class SpawnEvent:
    def __init__(self, name, radius, phase, speed, direction):
        self.name = name
        self.radius = radius
        self.phase = phase
        self.speed = speed
        self.direction = direction

    def apply(self, world, x, y):
        spawned = None
        if self.name.lower() == "bullet":
            spawned = world.bulletClass(x + self.radius * math.cos(self.phase), y + self.radius * math.sin(self.phase))
            spawned.initialize(self.speed, self.direction)
        else:
            spawned = world.definedSpawners[self.name.lower()].clone()
            spawned.setStartingValues(x + self.radius * math.cos(self.phase),
                y + self.radius * math.sin(self.phase), self.speed, self.direction)
        world.addEntity(spawned)

class ConditionalEvent:
    def __init__(self, input):
        self.health = 100
        if "health" in input:
            self.health = 100 * float(input["health"])
        self.events = []
        if "events" in input:
            for s in input["events"]:
                parts = s.split(",")
                type = ""
                name = ""
                radius = 0
                phase = 0
                speed=0
                direction=0
                if len(parts) >= 1:
                    type = parts[0].strip().lower()
                if len(parts) >= 2:
                    name = parts[1].strip().lower()
                if len(parts) >= 3:
                    radius = int(parts[2])
                if len(parts) >= 4:
                    phase = int(parts[3])
                if len(parts) >= 5:
                    speed = int(parts[4])
                if len(parts) >= 6:
                    direction = int(parts[5])
                if type == "spawn" or type == "add":
                    self.events.append(SpawnEvent(name, radius, phase, speed, direction))
                if type == "delete" or type == "clear":
                    self.events.append(ClearEvent(name))

    def apply(self, world, x, y):
        for e in self.events:
            e.apply(world, x, y)