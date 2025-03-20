from pcg_benchmark.probs.utils import _get_certain_tiles
import numpy as np
from math import log2, sqrt

def kl_divergence(p, q):
    return sum(p[i] * log2(p[i]/q[i]) for i in range(len(p)) if p[i] > 0 and q[i] > 0)

def js_dist(p, q):
    m = 0.5 * (p + q)
    return sqrt(0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m))

class State:
    def __init__(self, level, x, y, falling):
        self._x = x
        self._y = y
        self._falling = falling
        self._level = level.copy()

    def clone(self):
        return State(self._level, self._x, self._y, self._falling)

    def update(self, dx, dy):
        if self._falling:
            self._y += 1
        else:
            if abs(dy) >= 1:
                ny = self._y + dy
                if ny < 0:
                    ny = 0
                if ny > self._level.shape[0] - 1:
                    ny = self._level.shape[0] - 1
                if self._level[ny][self._x] != 0:
                    if self._level[self._y][self._x] == 5:
                        self._y = ny
                    elif self._level[self._y][self._x] == 6 and dy > 0:
                        self._y = ny
            if abs(dx) >= 1:
                nx = self._x + dx
                if nx < 0:
                    nx = 0
                if nx > self._level.shape[1] - 1:
                    nx = self._level.shape[1] - 1
                if self._level[self._y][nx] != 0:
                    self._x = nx
        self._falling = 0
        if self._y < self._level.shape[0] - 1 and self._level[self._y][self._x] == 1 and\
            self._level[self._y+1][self._x] not in [0, 5]:
            self._falling = 1

    def __str__(self):
        return f"{self._x},{self._y},{self._falling}"
    
    def value(self):
        if self._falling:
            return 4
        if self._level[self._y][self._x] == 6:
            return 3
        if self._level[self._y][self._x] == 5:
            return 2
        return 1

def read_loderunner(file):
    level = []
    with open(file) as f:
        lines = f.readlines()
        for l in lines:
            l = l.strip()
            if len(l) > 0:
                level.append([])
            for c in l:
                level[-1].append(int(c))
    return np.array(level)

def string_loderunner(level):
    result = ""
    for y in range(level.shape[0]):
        for x in range(level.shape[1]):
            result += str(level[y][x])
        result += "\n"
    return result

def play_loderunner(level):
    exploration = np.zeros((level.shape[0], level.shape[1])).astype(int)

    level = np.array(level)
    temp = _get_certain_tiles(level, [2])
    if len(temp) == 0:
        return exploration
    sx, sy = temp[0]

    level = level.copy()
    level[level == 2] = 1
    level[level == 3] = 1
    level[level == 4] = 1
    
    falling = 0
    if sy < level.shape[0] - 1 and level[sy][sx] == 1 and level[sy+1][sx] not in [0, 5]:
        falling = 1
    visited = set()
    open = [State(level, sx, sy, falling)]
    while len(open) > 0:
        current = open.pop(0)
        if str(current) in visited:
            continue
        visited.add(str(current))
        exploration[current._y][current._x] = current.value()
        for a in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            next = current.clone()
            next.update(a[0], a[1])
            open.append(next)
    return exploration