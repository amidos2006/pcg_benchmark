import numpy as np

"""
Get all the locations of a specific tile value in the 2D array

Parameters:
    map (int[][]): is a numpy 2D array that need to be searched
    tile_values (int[]): is an array of all the possible values that need to be discovered in the input map

Returns:
    [int,int][]: an array of (x,y) location in the input array that is equal to the values in tile_values
"""
def _get_certain_tiles(map, tile_values):
    tiles=[]
    for y in range(map.shape[0]):
        for x in range(map.shape[1]):
            if map[y][x] in tile_values:
                tiles.append((x,y))
    return tiles

"""
Run Dijkstra Algorithm and return the map and the location that are visited

Parameters:
    x(int): the x position of the starting point of the dijkstra algorithm
    y(int): the y position of the starting point of the dijkstra algorithm
    map(int[][]): the input 2D map that need to be tested for dijkstra
    passable_values(int[]): the values that are considered passable

Returns:
    int[][]: the dijkstra map where the value is the distance towards x, y location
    int[][]: a binary 2D array where 1 means visited by Dijkstra algorithm and 0 means not
"""
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

"""
Get an array of positions that leads to the starting of Dijkstra

Parameters:
    dijkstra(int[][]): the dijkstra map that need to be tested
    sx(int): the x position to get path from
    sy(int): the y position to get path from

Returns:
    [int,int][]: an array of all the positions that lead from starting position to (sx,sy)
"""
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

"""
Get the number of tiles that the flood fill algorithm fill

Parameters:
    x(int): the x position for the flood fill algorithm
    y(int): the y position for the flood fill algorithm
    color_map(int[][]): the color map where the test happen on map and is added to this variable
    map(int[][]): the maze that need to be flood filled (it doesn't change)
    color_index(int): the color that is used to color the region
    passable_Values(int[]): the tiles that are considered the same when are near each other

Returns:
    int: number of tiles for the flood fill
"""
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

"""
Calculate the number of regions in the map that have the same values in the tile_values

Parameters:
    maze(int[][]):  the maze that need to be checked for regions
    tile_values(int[]): the values that need to be checked making regions

Returns:
    Number of seperate regions in the maze that have the same values using 1 size Von Neumann neighborhood
"""
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

"""
Calculate the size of the regions in the maze specified by the locations that have the same values in the tile_values

Parameters:
    maze(int[][]): the maze that need to be tested for regions
    locations([int,int][]): an array of x,y locations that specify the starting point of the regions
    tile_values(int[]): the values that are considered the same in the regions
    
Returns:
    int[]: an array of the size of the regions that have the starting points in the locations
"""
def get_regions_size(maze, locations, tile_values):
    result = []
    region_index=0
    color_map = np.full((maze.shape[0], maze.shape[1]), -1)
    for (x,y) in locations:
        num_tiles = _flood_fill(x, y, color_map, maze, region_index + 1, tile_values)
        if num_tiles > 0:
            region_index += 1
            result.append(num_tiles)
        else:
            continue
    return result

"""
Get the longest shortest path in a maze. This is calculated by first calculating the Dijstra for all the tiles values.
Then Picking the highest value in the map and run Dijkstra again and get the maximum value

Parameters:
    maze(int[][]): the maze that need to be tested for the longest shortest path
    tile_values(int[]): the values that are passable in the maze

Returns:
    int: the longest shortest distance in a maze
"""
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

"""
Get the distance between two points in a maze

Parameters:
    maze(int[][]): the maze that need to be tested for distance
    start_tile([int,int]): the starting x,y position for the distance metric
    end_tile([int,int]): the ending x,y positon for the distance metric
    passable_tiles(int[]): the passable tiles in the maze

Returns:
    int: the distance between the starting tile and ending tile in the maze
"""
def get_distance_length(maze, start_tile, end_tile, passable_tiles):
    start_tiles = _get_certain_tiles(maze, [start_tile])
    end_tiles = _get_certain_tiles(maze, [end_tile])
    if len(start_tiles) == 0 or len(end_tiles) == 0:
        return -1
    (sx,sy) = start_tiles[0]
    (ex,ey) = end_tiles[0]
    dikjstra_map, _ = _run_dikjstra(sx, sy, maze, passable_tiles)
    return dikjstra_map[ey][ex]

"""
Get a path between two position as (x,y) locations

Parameters:
    maze(int[][]): the maze that need to check for path in it
    start_tile([int,int]): x,y for the starting tile for path finding
    end_tile([int,int]): x,y for the ending tile for path finding
    passable_tiles(int[]): the passable tiles in the maze

Returns:
    [int,int][]: an array of x,y corridnates that connected between start_tile and end_tile
"""
def get_path(maze, start_tile, end_tile, passable_tiles):
    maze = np.array(maze)
    start_tiles = _get_certain_tiles(maze, [start_tile])
    end_tiles = _get_certain_tiles(maze, [end_tile])
    if len(start_tiles) == 0 or len(end_tiles) == 0:
        return []
    (sx,sy) = start_tiles[0]
    (ex,ey) = end_tiles[0]
    dikjstra_map, _ = _run_dikjstra(sx, sy, maze, passable_tiles)
    return _get_path(dikjstra_map, ex, ey)

"""
Calculate horizontal symmetric tiles

Parameters:
    maze(int[][]): the maze that need to be tested for symmetry

Returns:
    int: get the number of tiles that are symmetric horizontally
"""
def get_horz_symmetry(maze):
    symmetry = 0
    for i in range(maze.shape[0]):
        for j in range(int(maze.shape[1]/2)):
            if maze[i][j] == maze[i][-j-1]:
                symmetry += 1
    return symmetry

"""
Get the input map modified using all the rotations and flipping

Parameters:
    map(int[][]): the input map that need to be transformed

Returns:
    int[][][]: all the possible transformed maps (rotate,flipping)
"""
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

"""
Get number of tiles in a maze that are equal to tile_values

Parameters:
    maze(int[][]): the 2d maze that need to be tested
    tile_values(int[]): the values that needs to be counted in the maze

Returns:
    int: return the number of tiles in the map of these values
"""
def get_num_tiles(maze, tile_values):
    return len(_get_certain_tiles(maze, tile_values))

"""
Get a histogram of horizontally connected region lengths

Parameters:
    maze(int[][]): the maze that need to be tested
    tile_values(int[]): the values that create groups

Returns:
    int[]: a histogram of length for the horizontal groups of the same value
"""
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

"""
Get a histogram of vertically connected region lengths

Parameters:
    maze(int[][]): the maze that need to be tested
    tile_values(int[]): the values that create groups

Returns:
    int[]: a histogram of length for the vertical groups of the same value
"""
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

"""
Get a bin number for a float value between 0 and 1

Parameters:
    value(float): a float value that needs to be discretized between 0 and bins
    bins(int): number of bins that are possible

Returns:
    int: a value between 0 and bins that reflect which discrete value works
"""
def discretize(value, bins):
    return int(bins * np.clip(value,0,1)-0.00000001)

"""
Reshape the reward value to be between 0 and 1 based on a trapizoid

Parameters:
    value(float): the value that need to be reshaped between 0 and 1
    min_value(float): the minimum value where the reward is 0 at it
    plat_low(float): the minimum value where the reward become 1
    plat_high(float): the maximum value where the rewards stays 1 at. Optional parameter where not provided 
    equal to plat_low
    max_value(float): the maximum value where the rewrad is back at 0. Optional parameter where not provided
    it will be equal to plat_high

Returns:
    float: a value between 0 and 1 based on where it falls in the trapizoid reward scheme
"""
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

"""
Normalize a value between low and high

Parameters:
    value(float): the value need to be normalized
    low(float): the lowest value for the normalization
    high(float): the highest value for the normalization

Returns:
    float: the normalized value between 0 and 1
"""
def get_normalized_value(value, low, high):
    return (value - low) / (high - low + 0.00000000000001)