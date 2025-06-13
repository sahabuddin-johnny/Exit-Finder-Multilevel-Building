import pygame
import json
import os

# Configurable variables
floor_image_path = "mall_first_floor.png"  # Make sure the image is in the same folder
grid_rows, grid_cols = 30, 30  # Adjustable grid size
cell_types = {
    0: (255, 255, 255),  # walkable - white
    1: (0, 0, 0),        # wall - black
    2: (255, 165, 0),    # stair - orange
    3: (0, 255, 0)       # exit - green
}
label_keys = {
    pygame.K_w: 0,
    pygame.K_a: 1,
    pygame.K_s: 2,
    pygame.K_e: 3
}

# Load floor image
image = pygame.image.load(floor_image_path)
img_width, img_height = image.get_size()

cell_width = img_width // grid_cols
cell_height = img_height // grid_rows

# Initialize grid with walkable cells
grid = [[0 for _ in range(grid_cols)] for _ in range(grid_rows)]

pygame.init()
screen = pygame.display.set_mode((img_width, img_height))
pygame.display.set_caption("Mall Floor Map Annotator")
font = pygame.font.SysFont(None, 24)
current_label = 1  # Start with wall

running = True
while running:
    screen.blit(image, (0, 0))

    # Draw grid and colors
    for i in range(grid_rows):
        for j in range(grid_cols):
            rect = pygame.Rect(j * cell_width, i * cell_height, cell_width, cell_height)
            pygame.draw.rect(screen, cell_types[grid[i][j]], rect, 3)

    label_text = font.render(f"Label: {current_label} (W:Walk A:Wall S:Stair E:Exit)", True, (255, 0, 0))
    screen.blit(label_text, (10, 10))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in label_keys:
                current_label = label_keys[event.key]
            elif event.key == pygame.K_RETURN:
                output_path = "first_floor_grid.json"
                with open(output_path, "w") as f:
                    json.dump(grid, f)
                print(f"Map saved to {output_path}")
            elif event.key == pygame.K_ESCAPE:
                running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            col = x // cell_width
            row = y // cell_height
            if 0 <= row < grid_rows and 0 <= col < grid_cols:
                grid[row][col] = current_label

pygame.quit()
