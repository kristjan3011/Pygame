import pygame
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 30  # Each cell in the grid is 30x30 pixels
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Maze grid (1 = Wall, 0 = Empty path, 2 = Pellet, 3 = Ghost, 4 = Pac-Man)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 3, 1, 0, 1, 3, 0, 0, 0, 0, 1, 3, 1, 0, 1, 3, 0, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Store pellet positions separately
pellet_positions = [(row_idx, col_idx) for row_idx, row in enumerate(maze) for col_idx, cell in enumerate(row) if
                    cell == 2]


def display_message(screen, message, color=WHITE):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)


# Get Pac-Man & Ghost positions
def get_positions():
    pacman_pos = None
    ghost_positions = []
    for row_idx, row in enumerate(maze):
        for col_idx, cell in enumerate(row):
            if cell == 4:
                pacman_pos = [row_idx, col_idx]
            elif cell == 3:
                ghost_positions.append([row_idx, col_idx])
    return pacman_pos, ghost_positions


pacman_pos, ghost_positions = get_positions()
score = 0
lives = 3


def check_collision(screen):
    global lives, pacman_pos
    for ghost in ghost_positions:
        if pacman_pos == ghost:
            lives -= 1
            if lives > 0:
                display_message(screen, "You lost a life!", RED)
            if lives == 0:
                display_message(screen, "Game Over!", RED)
                pygame.quit()
                exit()

            # Reset Pac-Man position and update the maze immediately
            old_row, old_col = pacman_pos
            maze[old_row][old_col] = 0  # Clear old position
            pacman_pos = [1, 1]  # Reset to start position
            maze[1][1] = 4  # Place Pac-Man back on the grid


def draw_maze(screen):
    for row_idx, row in enumerate(maze):
        for col_idx, cell in enumerate(row):
            x, y = col_idx * GRID_SIZE, row_idx * GRID_SIZE
            if cell == 1:
                pygame.draw.rect(screen, BLUE, (x, y, GRID_SIZE, GRID_SIZE))
            elif cell == 2:
                pygame.draw.circle(screen, WHITE, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 5)
            elif cell == 3:
                pygame.draw.circle(screen, RED, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 12)
            elif cell == 4:
                pygame.draw.circle(screen, YELLOW, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 12)


def move_pacman(direction, screen):
    global pacman_pos, score
    row, col = pacman_pos
    new_row, new_col = row, col
    if direction == "UP":
        new_row -= 1
    elif direction == "DOWN":
        new_row += 1
    elif direction == "LEFT":
        new_col -= 1
    elif direction == "RIGHT":
        new_col += 1

    if maze[new_row][new_col] != 1:
        if (new_row, new_col) in pellet_positions:
            pellet_positions.remove((new_row, new_col))
            score += 10

        maze[row][col] = 0  # Clear old position
        maze[new_row][new_col] = 4  # Move Pac-Man
        pacman_pos = [new_row, new_col]

    check_collision(screen)


def move_ghosts(screen):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for ghost in ghost_positions:
        row, col = ghost
        random.shuffle(directions)

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if maze[new_row][new_col] in [0, 2]:
                maze[row][col] = 0  # Restore empty path
                if (row, col) in pellet_positions:
                    maze[row][col] = 2  # Restore pellet if ghost was on one

                ghost[0], ghost[1] = new_row, new_col
                maze[new_row][new_col] = 3  # Move ghost
                break
    check_collision(screen)


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man (Beginner Version)")
    clock = pygame.time.Clock()

    while True:
        screen.fill(BLACK)
        draw_maze(screen)
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 100, 10))

        move_ghosts(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move_pacman("UP", screen)
                elif event.key == pygame.K_DOWN:
                    move_pacman("DOWN", screen)
                elif event.key == pygame.K_LEFT:
                    move_pacman("LEFT", screen)
                elif event.key == pygame.K_RIGHT:
                    move_pacman("RIGHT", screen)

        clock.tick(5)  # Control game speed


if __name__ == "__main__":
    main()

'''


'''