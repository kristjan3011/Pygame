import pygame, random
pygame.init()

# VÄRVID
VÄRVID = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255),
    (255, 153, 255), (153, 255, 153), (153, 204, 255)
]

# EKRAAN
LAIUS, KORGUS = 640, 480
TAUST = (40, 40, 40)
ekraan = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Hiire juhtimine")
clock = pygame.time.Clock()

# MUUTUJAD
ringid = []  # [x, y, raadius, värv]
MAX_RINGID = 10
KASV = 2
MAX_RAADIUS = 60

# MÄNGUTSÜKKEL
running = True
while running:
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            värv = random.choice(VÄRVID)
            ringid.append([x, y, 10, värv])

            # hoia ainult viimased 10 ringi
            if len(ringid) > MAX_RINGID:
                ringid = ringid[-MAX_RINGID:]

            # suurenda kõiki ringe
            for r in ringid:
                r[2] = min(r[2] + KASV, MAX_RAADIUS)

    # JOONISTAMINE
    ekraan.fill(TAUST)
    for x, y, raadius, värv in ringid:
        pygame.draw.circle(ekraan, värv, (x, y), raadius, 2)

    pygame.display.flip()

pygame.quit()