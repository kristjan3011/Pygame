import pygame, sys

pygame.init()

# ekraani seaded
LAIUS = 640
KORGUS = 480
ekraan = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Ping Pong")

# värvid
TAUST = (220, 235, 255)
TEKST_VARV = (30, 30, 80)

# palli pilt
PALL_SUURUS = 20
pall_img = pygame.image.load("img/ball.png").convert_alpha()
pall_img = pygame.transform.scale(pall_img, (PALL_SUURUS, PALL_SUURUS))

pall_x = LAIUS // 2
pall_y = KORGUS // 3
pall_kiirus_x = 10
pall_kiirus_y = 10

# aluse pilt
ALUS_LAIUS = 120
ALUS_KORGUS = 20
alus_img = pygame.image.load("img/pad.png").convert_alpha()
alus_img = pygame.transform.scale(alus_img, (ALUS_LAIUS, ALUS_KORGUS))

alus_x = (LAIUS - ALUS_LAIUS) // 2
alus_y = int(KORGUS / 1.5)
alus_kiirus = 5
alus_suund = 1

# skoor
skoor = 0

kell = pygame.time.Clock()

# mängutsükkel
while True:
    for sundmus in pygame.event.get():
        if sundmus.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # palli liikumine
    pall_x += pall_kiirus_x
    pall_y += pall_kiirus_y

    # vasak / parem sein
    if pall_x <= 0:
        pall_x = 0
        pall_kiirus_x = abs(pall_kiirus_x)
    elif pall_x + PALL_SUURUS >= LAIUS:
        pall_x = LAIUS - PALL_SUURUS
        pall_kiirus_x = -abs(pall_kiirus_x)

    # ülemine sein
    if pall_y <= 0:
        pall_y = 0
        pall_kiirus_y = abs(pall_kiirus_y)

    # alumine äär, negatiivne punkt
    if pall_y + PALL_SUURUS >= KORGUS:
        skoor -= 1
        pall_x = LAIUS // 2
        pall_y = KORGUS // 3
        pall_kiirus_x = 4
        pall_kiirus_y = 4

    # aluse liikumine
    alus_x += alus_kiirus * alus_suund

    if alus_x <= 0:
        alus_x = 0
        alus_suund = 1
    elif alus_x + ALUS_LAIUS >= LAIUS:
        alus_x = LAIUS - ALUS_LAIUS
        alus_suund = -1

    # rect objektid PNG‑de jaoks
    pall_rect = pygame.Rect(pall_x, pall_y, PALL_SUURUS, PALL_SUURUS)
    alus_rect = pygame.Rect(alus_x, alus_y, ALUS_LAIUS, ALUS_KORGUS)

    # kokkupõrge
    if pall_rect.colliderect(alus_rect) and pall_kiirus_y > 0:
        pall_kiirus_y = -abs(pall_kiirus_y)
        pall_y = alus_y - PALL_SUURUS
        skoor += 1

    # joonistamine
    ekraan.fill(TAUST)

    # PNG pall
    ekraan.blit(pall_img, (pall_x, pall_y))

    # PNG alus
    ekraan.blit(alus_img, (alus_x, alus_y))

    # font
    font = pygame.font.SysFont("Arial", 28)

    # Skoor
    skoor_tekst = font.render(f"Skoor: {skoor}", True, TEKST_VARV)
    ekraan.blit(skoor_tekst, (10, 10))

    pygame.display.flip()
    kell.tick(60)
