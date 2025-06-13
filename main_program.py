import pygame
import json
import heapq

# === CONFIG ===
floor_images = {
    0: "mall_ground_floor.png",
    1: "mall_first_floor.png"
}
floor_grids = {
    0: "ground_floor_grid.json",
    1: "first_floor_grid.json"
}
cell_colors = {
    0: (255, 255, 255),  # walkable
    1: (0, 0, 0),        # wall
    2: (255, 165, 0),    # stair
    3: (0, 255, 0)       # exit
}

# === LOAD DATA ===
floors = {}
images = {}
for i in floor_grids:
    with open(floor_grids[i], 'r') as f:
        floors[i] = json.load(f)
    images[i] = pygame.image.load(floor_images[i])

rows, cols = len(floors[0]), len(floors[0][0])
img_width, img_height = images[0].get_size()
cell_width = img_width // cols
cell_height = img_height // rows

# === A* PATHFINDING ===
def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def find_exits():
    result = []
    for f in floors:
        for i in range(rows):
            for j in range(cols):
                if floors[f][i][j] == 3:
                    result.append((f, i, j))
    return result

def find_stairs():
    stairs = []
    for f in floors:
        for i in range(rows):
            for j in range(cols):
                if floors[f][i][j] == 2:
                    stairs.append((f, i, j))
    return stairs

def astar_multi(start, exits):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    stairs = find_stairs()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current in exits:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        f, x, y = current
        neighbors = []

        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and floors[f][nx][ny] != 1:
                neighbors.append((f, nx, ny))

        if floors[f][x][y] == 2:
            for sf, sx, sy in stairs:
                if (sx, sy) == (x, y) and sf != f:
                    neighbors.append((sf, sx, sy))

        for neighbor in neighbors:
            temp_g = g_score[current] + 1
            if neighbor not in g_score or temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                f_score = temp_g + min(
                    heuristic((neighbor[1], neighbor[2]), (e[1], e[2]))
                    for e in exits if e[0] == neighbor[0]
                )
                heapq.heappush(open_set, (f_score, neighbor))

    return []

# === MAIN APP ===
pygame.init()
screen = pygame.display.set_mode((img_width, img_height))
font = pygame.font.SysFont(None, 24)

current_floor = 0
start_point = None
path = []
exits = find_exits()

running = True
while running:
    screen.blit(images[current_floor], (0, 0))

    # Draw exits and stairs
    for i in range(rows):
        for j in range(cols):
            val = floors[current_floor][i][j]
            if val in [2, 3]:
                color = cell_colors[val]
                pygame.draw.rect(screen, color, pygame.Rect(j*cell_width, i*cell_height, cell_width, cell_height), 3)

    # Draw path
    for (f, i, j) in path:
        if f == current_floor:
            pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(j*cell_width, i*cell_height, cell_width, cell_height))

    # Draw start
    if start_point and start_point[0] == current_floor:
        _, si, sj = start_point
        pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(sj*cell_width, si*cell_height, cell_width, cell_height))

    # UI
    label = font.render(f"Floor: {current_floor+1} | Click=Start | F=Find | S=Switch | Esc=Exit", True, (255, 0, 0))
    screen.blit(label, (10, 10))
    pygame.display.flip()

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_s:
                current_floor = 1 - current_floor
            elif event.key == pygame.K_f and start_point:
                path = astar_multi(start_point, exits)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            j, i = x // cell_width, y // cell_height
            if 0 <= i < rows and 0 <= j < cols and floors[current_floor][i][j] != 1:
                start_point = (current_floor, i, j)
                path = []

pygame.quit()
