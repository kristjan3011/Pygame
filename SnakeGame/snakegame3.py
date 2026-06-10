import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 10
GRID_SIZE = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

snake = [(WIDTH // 2, HEIGHT // 2)]
food = (random.randint(0, WIDTH // GRID_SIZE - 1) * GRID_SIZE,
        random.randint(0, HEIGHT // GRID_SIZE - 1) * GRID_SIZE)
direction = (GRID_SIZE, 0)
next_direction = direction

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction[1] == 0:
                next_direction = (0, -GRID_SIZE)
            elif event.key == pygame.K_DOWN and direction[1] == 0:
                next_direction = (0, GRID_SIZE)
            elif event.key == pygame.K_LEFT and direction[0] == 0:
                next_direction = (-GRID_SIZE, 0)
            elif event.key == pygame.K_RIGHT and direction[0] == 0:
                next_direction = (GRID_SIZE, 0)

    direction = next_direction
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    if new_head in snake or new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
        running = False

    snake.insert(0, new_head)

    if new_head == food:
        food = (random.randint(0, WIDTH // GRID_SIZE - 1) * GRID_SIZE,
                random.randint(0, HEIGHT // GRID_SIZE - 1) * GRID_SIZE)
    else:
        snake.pop()

    screen.fill((0, 0, 0))
    for segment in snake:
        pygame.draw.rect(screen, (0, 255, 0), (segment[0], segment[1], GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, (255, 0, 0), (food[0], food[1], GRID_SIZE, GRID_SIZE))

    pygame.display.flip()

pygame.quit()