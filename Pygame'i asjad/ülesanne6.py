import pygame, sys, random
# Kristjan IS25
pygame.init()

# Taustamuusika
try:
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("music/tausta_muss.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except Exception as e:
    print("Heli ei saanud käivituda:", e)

# Ekraan
LAIUS = 640 # 1920 / 640
KORGUS = 480 # 1080 / 480
ekraan = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Ping Pong 2")

# Värvid
TAUST = (220, 235, 255)
TEKST_VARV = (30, 30, 80)

# Pildid
PALL_SUURUS = 20
pall_img = pygame.image.load("img/ball.png").convert_alpha()
pall_img = pygame.transform.scale(pall_img, (PALL_SUURUS, PALL_SUURUS))

ALUS_LAIUS = 140
ALUS_KORGUS = 20
alus_img = pygame.image.load("img/pad.png").convert_alpha()
alus_img = pygame.transform.scale(alus_img, (ALUS_LAIUS, ALUS_KORGUS))

font = pygame.font.SysFont("Arial", 28)

# Üks kindel kiirus, mis ei muutu
CONST_SPEED_X = 8
CONST_SPEED_Y = 8

def reset_game():
    # Seab palli, aluse ja skoori algseisu
    global pall_x, pall_y, pall_kiirus_x, pall_kiirus_y
    global alus_x, alus_y, skoor, game_over

    # X suvaline üle ekraani, Y umbes 50 (480 puhul)
    pall_x = random.randint(0, LAIUS - PALL_SUURUS)
    pall_y = 50

    # Suund alla, horisontaalne suund suvaline (vasak/parem), aga kiirus sama
    pall_kiirus_x = CONST_SPEED_X * random.choice([-1, 1])
    pall_kiirus_y = CONST_SPEED_Y

    alus_x = (LAIUS - ALUS_LAIUS) // 2
    alus_y = int(KORGUS / 1.1)

    skoor = 0
    game_over = False

reset_game()
kell = pygame.time.Clock()

while True:
    for sundmus in pygame.event.get():
        if sundmus.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if sundmus.type == pygame.KEYDOWN and game_over:
            # Pärast kaotust: ENTER → restart, ESC → exit
            if sundmus.key == pygame.K_RETURN:
                reset_game()
            if sundmus.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if not game_over:
        # Aluse juhtimine
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            alus_x -= 7
        if keys[pygame.K_RIGHT]:
            alus_x += 7

        # Alus ei tohi väljuda ekraanist
        if alus_x < 0:
            alus_x = 0
        if alus_x + ALUS_LAIUS > LAIUS:
            alus_x = LAIUS - ALUS_LAIUS

        # Palli liikumine
        pall_x += pall_kiirus_x
        pall_y += pall_kiirus_y

        # Vasak / parem sein
        if pall_x <= 0:
            pall_x = 0
            pall_kiirus_x = abs(pall_kiirus_x)
        elif pall_x + PALL_SUURUS >= LAIUS:
            pall_x = LAIUS - PALL_SUURUS
            pall_kiirus_x = -abs(pall_kiirus_x)

        # Ülemine sein
        if pall_y <= 0:
            pall_y = 0
            pall_kiirus_y = abs(pall_kiirus_y)

        # Alumine äär
        if pall_y + PALL_SUURUS >= KORGUS:
            game_over = True

        # Rectid
        pall_rect = pygame.Rect(pall_x, pall_y, PALL_SUURUS, PALL_SUURUS)
        alus_rect = pygame.Rect(alus_x, alus_y, ALUS_LAIUS, ALUS_KORGUS)

        # Kokkupõrge alusega
        if pall_rect.colliderect(alus_rect) and pall_kiirus_y > 0:
            pall_kiirus_y = -CONST_SPEED_Y # üles
            # tabamiskoht
            alus_kesk = alus_x + ALUS_LAIUS / 2
            pall_kesk = pall_x + PALL_SUURUS / 2
            offset = pall_kesk - alus_kesk  # negatiivne = vasak, positiivne = parem
            # Normaliseeri offset vahemikku -1 ... 1
            offset_norm = offset / (ALUS_LAIUS / 2)
            # Määra X‑kiirus vastavalt tabamiskohale
            pall_kiirus_x = int(CONST_SPEED_X * offset_norm)
            # Väldi nullkiirust (et pall ei liiguks täiesti sirgelt)
            if pall_kiirus_x == 0:
                pall_kiirus_x = random.choice([-2, 2])
            skoor += 1
            pall_y = alus_y - PALL_SUURUS

    # Joonistamine
    ekraan.fill(TAUST)
    ekraan.blit(pall_img, (pall_x, pall_y))
    ekraan.blit(alus_img, (alus_x, alus_y))

    skoor_tekst = font.render(f"Skoor: {skoor}", True, TEKST_VARV)
    ekraan.blit(skoor_tekst, (10, 10))

    if game_over:
        tekst1 = font.render("Mäng läbi!", True, (200, 0, 0))
        tekst2 = font.render("Vajuta ENTER, et restartida", True, TEKST_VARV)
        tekst3 = font.render("ESC sulgeb mängu", True, TEKST_VARV)
        ekraan.blit(tekst1, (LAIUS // 2 - 80, KORGUS // 2 - 40))
        ekraan.blit(tekst2, (LAIUS // 2 - 170, KORGUS // 2))
        ekraan.blit(tekst3, (LAIUS // 2 - 130, KORGUS // 2 + 40))

    pygame.display.flip()
    kell.tick(60)
