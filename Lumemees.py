import pygame
pygame.init()

# Akna seaded
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Lumemees – Kristjan")

# Värvid
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 140, 0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    # Lumemees (3 ringi)
    pygame.draw.circle(screen, WHITE, (150, 220), 60)   # alumine
    pygame.draw.circle(screen, WHITE, (150, 140), 45)   # keskmine
    pygame.draw.circle(screen, WHITE, (150, 80), 30)    # pea

    # Silmad
    pygame.draw.circle(screen, BLACK, (140, 75), 5)
    pygame.draw.circle(screen, BLACK, (160, 75), 5)

    # Porgand/nina
    pygame.draw.polygon(screen, ORANGE, [(150, 85), (180, 90), (150, 95)])

    pygame.display.flip()

pygame.quit()
