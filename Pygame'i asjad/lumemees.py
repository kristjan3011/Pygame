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

    SKY = (135, 206, 250)  # helesinine
    screen.fill(SKY)

    # Lumemees (3 ringi)
    pygame.draw.circle(screen, WHITE, (150, 220), 60)   # alumine
    pygame.draw.circle(screen, WHITE, (150, 140), 45)   # keskmine
    pygame.draw.circle(screen, WHITE, (150, 80), 30)    # pea

    # Silmad
    pygame.draw.circle(screen, BLACK, (140, 75), 5)
    pygame.draw.circle(screen, BLACK, (160, 75), 5)

    # Porgand/nina
    pygame.draw.polygon(screen, ORANGE, [(150, 85), (180, 90), (150, 95)])

    # Nööbid
    pygame.draw.circle(screen, BLACK, (150, 130), 5)
    pygame.draw.circle(screen, BLACK, (150, 150), 5)
    pygame.draw.circle(screen, BLACK, (150, 170), 5)

    # Käed
    pygame.draw.line(screen, (120, 70, 15), (110, 140), (60, 110), 4)  # vasak käsi
    pygame.draw.line(screen, (120, 70, 15), (190, 140), (240, 110), 4)  # parem käsi

    # Kübar
    pygame.draw.rect(screen, BLACK, (120, 50, 60, 20))  # kübara äär
    pygame.draw.rect(screen, BLACK, (130, 30, 40, 25))  # kübara ülemine osa

    # Päike
    pygame.draw.circle(screen, (255, 255, 0), (260, 40), 25)

    # Kiired
    for i in range(12):
        angle = i * 30
        x_end = 260 + 40 * pygame.math.Vector2(1, 0).rotate(angle).x
        y_end = 40 + 40 * pygame.math.Vector2(1, 0).rotate(angle).y
        pygame.draw.line(screen, (255, 255, 0), (260, 40), (x_end, y_end), 2)

    # Pilv
    # Pilv vasakus ülanurgas
    pygame.draw.circle(screen, (230, 230, 230), (40, 25), 18)
    pygame.draw.circle(screen, (230, 230, 230), (65, 20), 25)
    pygame.draw.circle(screen, (230, 230, 230), (90, 25), 18)

    # Pilv ülal keskel
    pygame.draw.circle(screen, (230, 230, 230), (130, 15), 15)
    pygame.draw.circle(screen, (230, 230, 230), (150, 10), 20)
    pygame.draw.circle(screen, (230, 230, 230), (170, 15), 15)

    # Pilv paremas ülanurgas
    pygame.draw.circle(screen, (230, 230, 230), (210, 25), 18)
    pygame.draw.circle(screen, (230, 230, 230), (235, 20), 25)
    pygame.draw.circle(screen, (230, 230, 230), (260, 25), 18)

    # Pulk vartega
    BROWN = (120, 70, 15)
    # Põhipulk
    pygame.draw.line(screen, BROWN, (60, 180), (60, 60), 5)

    #oksad varre otsas
    pygame.draw.line(screen, BROWN, (60, 80), (45, 65), 3)
    pygame.draw.line(screen, BROWN, (60, 80), (75, 65), 3)
    pygame.draw.line(screen, BROWN, (60, 80), (50, 75), 3)
    pygame.draw.line(screen, BROWN, (60, 80), (70, 75), 3)
    pygame.display.flip()

pygame.quit()