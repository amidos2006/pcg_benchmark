import numpy as np

def _get_certain_tiles(map, tile_values):
    tiles=[]
    for y in range(map.shape[0]):
        for x in range(map.shape[1]):
            if map[y][x] in tile_values:
                tiles.append((x,y))
    return tiles

def _run_dikjstra(x, y, map, passable_values):
    dikjstra_map = np.full((map.shape[0], map.shape[1]),-1)
    visited_map = np.zeros((map.shape[0], map.shape[1]))
    queue = [(x, y, 0)]
    while len(queue) > 0:
        (cx,cy,cd) = queue.pop(0)
        if map[cy][cx] not in passable_values or (dikjstra_map[cy][cx] >= 0 and dikjstra_map[cy][cx] <= cd):
            continue
        visited_map[cy][cx] = 1
        dikjstra_map[cy][cx] = cd
        for (dx,dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx,ny=cx+dx,cy+dy
            if nx < 0 or ny < 0 or nx >= len(map[0]) or ny >= len(map):
                continue
            queue.append((nx, ny, cd + 1))
    return dikjstra_map, visited_map

def _get_path(dikjsta, sx, sy):
    path = []
    cx,cy = sx,sy
    while dikjsta[cy][cx] > 0:
        path.append((cx,cy))
        minx, miny = cx, cy
        for (dx,dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx,ny=cx+dx,cy+dy
            if nx < 0 or ny < 0 or nx >= len(dikjsta[0]) or ny >= len(dikjsta) or dikjsta[ny][nx] < 0:
                continue
            if dikjsta[ny][nx] < dikjsta[miny][minx]:
                minx, miny = nx, ny
        if minx == cx and miny == cy:
            break
        cx, cy = minx, miny
    if len(path) > 0:
        path.append((cx, cy))
    path.reverse()
    return path

def _flood_fill(x, y, color_map, map, color_index, passable_values):
    num_tiles = 0
    queue = [(x, y)]
    while len(queue) > 0:
        (cx, cy) = queue.pop(0)
        if color_map[cy][cx] != -1 or map[cy][cx] not in passable_values:
            continue
        num_tiles += 1
        color_map[cy][cx] = color_index
        for (dx,dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx,ny=cx+dx,cy+dy
            if nx < 0 or ny < 0 or nx >= len(map[0]) or ny >= len(map):
                continue
            queue.append((nx, ny))
    return num_tiles

def get_number_regions(maze, tile_values):
    empty_tiles = _get_certain_tiles(maze, tile_values)
    region_index=0
    color_map = np.full((maze.shape[0], maze.shape[1]), -1)
    for (x,y) in empty_tiles:
        num_tiles = _flood_fill(x, y, color_map, maze, region_index + 1, tile_values)
        if num_tiles > 0:
            region_index += 1
        else:
            continue
    return region_index

def get_longest_path(maze, tile_values):
    empty_tiles = _get_certain_tiles(maze, tile_values)
    final_visited_map = np.zeros((maze.shape[0], maze.shape[1]))
    final_value = 0
    for (x,y) in empty_tiles:
        if final_visited_map[y][x] > 0:
            continue
        dikjstra_map, visited_map = _run_dikjstra(x, y, maze, tile_values)
        final_visited_map += visited_map
        (my,mx) = np.unravel_index(np.argmax(dikjstra_map, axis=None), dikjstra_map.shape)
        dikjstra_map, _ = _run_dikjstra(mx, my, maze, tile_values)
        max_value = np.max(dikjstra_map)
        if max_value > final_value:
            final_value = max_value
    return final_value

def get_distance_length(maze, start_tile, end_tile, passable_tiles):
    start_tiles = _get_certain_tiles(maze, [start_tile])
    end_tiles = _get_certain_tiles(maze, [end_tile])
    if len(start_tiles) == 0 or len(end_tiles) == 0:
        return -1
    (sx,sy) = start_tiles[0]
    (ex,ey) = end_tiles[0]
    dikjstra_map, visited_map = _run_dikjstra(sx, sy, maze, passable_tiles)
    return dikjstra_map[ey][ex]

def get_path(maze, start_tile, end_tile, passable_tiles):
    maze = np.array(maze)
    start_tiles = _get_certain_tiles(maze, [start_tile])
    end_tiles = _get_certain_tiles(maze, [end_tile])
    if len(start_tiles) == 0 or len(end_tiles) == 0:
        return []
    (sx,sy) = start_tiles[0]
    (ex,ey) = end_tiles[0]
    dikjstra_map, visited_map = _run_dikjstra(sx, sy, maze, passable_tiles)
    return _get_path(dikjstra_map, ex, ey)

def get_horz_symmetry(maze):
    symmetry = 0
    for i in range(maze.shape[0]):
        for j in range(int(maze.shape[1]/2)):
            if maze[i][j] == maze[i][-j-1]:
                symmetry += 1
    return symmetry

def get_all_transforms(map):
    map = np.array(map)
    results = []
    for invH in [False, True]:
        for invV in [False, True]:
            for rot in [False, True]:
                newMap = np.zeros(map.shape)
                for y in range(len(newMap)):
                    for x in range(len(newMap[y])):
                        nx,ny = x,y
                        if invH:
                            nx = newMap.shape[1] - nx - 1
                        if invV:
                            ny = newMap.shape[0] - ny - 1
                        if rot and map.shape[0] == map.shape[1]:
                            temp = nx
                            nx = ny
                            ny = temp
                        newMap[ny][nx] = map[y][x]
                results.append(newMap)
    return results

def get_num_tiles(maze, tile_values):
    return len(_get_certain_tiles(maze, tile_values))

def get_horz_histogram(maze, tile_values):
    histogram = np.zeros(maze.shape[1])
    for i in range(maze.shape[0]):
        start_index = -1
        for j in range(maze.shape[1]):
            if maze[i][j] in tile_values:
                if start_index < 0:
                    start_index = j
            else:
                if start_index >= 0:
                    histogram[j - start_index] += 1
    return histogram

def get_vert_histogram(maze, tile_values):
    histogram = np.zeros(maze.shape[0])
    for j in range(maze.shape[1]):
        start_index = -1
        for i in range(maze.shape[0]):
            if maze[i][j] in tile_values:
                if start_index < 0:
                    start_index = i
            else:
                if start_index >= 0:
                    histogram[i - start_index] += 1
    return histogram

def discretize(value, bins):
    return int(bins * np.clip(value,0,1)-0.00000001)

def get_range_reward(value, min_value, plat_low, plat_high = None, max_value = None):
    if max_value == None:
        max_value = plat_high
    if plat_high == None:
        plat_high = plat_low
        max_value = plat_low
    if value >= plat_low and value <= plat_high:
        return 1.0
    if value <= min_value or value >= max_value:
        return 0.0
    if value < plat_low:
        return np.clip((value - min_value) / (plat_low - min_value + 0.00000001), 0.0, 1.0)
    if value > plat_high:
        return np.clip((max_value - value) / (max_value - plat_high + 0.00000001), 0.0, 1.0)

def get_normalized_value(value, low, high):
    return (value - low) / (high - low + 0.00000000000001)