import pygame, sys, random
# Kristjan IS25

pygame.init()

# HELI
try:
    pygame.mixer.init()

    # Taustamuusika
    pygame.mixer.music.load("music/tausta_muss.mp3")
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(-1)

    # Heliefektid (põrge + game over)
    bounce_sound = pygame.mixer.Sound("music/hit_sound.mp3")
    gameover_sound = pygame.mixer.Sound("music/gameover.mp3")
    bounce_sound.set_volume(0.4)
    gameover_sound.set_volume(1)

except Exception as e:
    print("Heli ei saanud käivituda:", e)

# EKRAAN
LAIUS = 640
KORGUS = 480
ekraan = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Ping Pong 2")

# VÄRVID
TAUST = (220, 235, 255)   # hele taust
TEKST_VARV = (30, 30, 80) # tume tekst

# PILDID
PALL_SUURUS = 20
pall_img = pygame.image.load("img/ball.png").convert_alpha()
pall_img = pygame.transform.scale(pall_img, (PALL_SUURUS, PALL_SUURUS))

ALUS_LAIUS = 140
ALUS_KORGUS = 20
alus_img = pygame.image.load("img/pad.png").convert_alpha()
alus_img = pygame.transform.scale(alus_img, (ALUS_LAIUS, ALUS_KORGUS))

font = pygame.font.SysFont("Arial", 28)

# KONSTANTSED KIIRUSED (et pall ei kiirene lõputult)
CONST_SPEED_X = 8
CONST_SPEED_Y = 8

# RESET FUNKTSIOON
def reset_game():
    # Palli algpositsioon
    global pall_x, pall_y, pall_kiirus_x, pall_kiirus_y
    # Aluse algpositsioon
    global alus_x, alus_y
    # Skoor ja mängu olek
    global skoor, game_over

    # Palli algasend
    pall_x = random.randint(0, LAIUS - PALL_SUURUS)
    pall_y = 50

    # Palli algkiirus (suvaline vasak/parem suund)
    pall_kiirus_x = CONST_SPEED_X * random.choice([-1, 1])
    pall_kiirus_y = CONST_SPEED_Y

    # Alus keskele
    alus_x = (LAIUS - ALUS_LAIUS) // 2
    alus_y = int(KORGUS / 1.1)

    # Skoor nulli
    skoor = 0
    game_over = False

    # Taustamuusika tagasi
    pygame.mixer.music.play(-1)

reset_game()
kell = pygame.time.Clock()

# MÄNGUTSÜKKEL
while True:
    for sundmus in pygame.event.get():
        if sundmus.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Restart / Exit game over ekraanilt
        if sundmus.type == pygame.KEYDOWN and game_over:
            if sundmus.key == pygame.K_RETURN:
                reset_game()
            if sundmus.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if not game_over:

        # ALUSE JUHTIMINE
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            alus_x -= 7
        if keys[pygame.K_RIGHT]:
            alus_x += 7

        # Alus ei tohi väljuda ekraanist
        alus_x = max(0, min(alus_x, LAIUS - ALUS_LAIUS))

        # PALLI LIIKUMINE
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

        # Alumine äär ja GAME OVER
        if pall_y + PALL_SUURUS >= KORGUS:
            game_over = True
            pygame.mixer.music.stop()  # peatab taustamuusika
            gameover_sound.play()      # game over heli

        # RECTID (kokkupõrke tuvastamiseks)
        pall_rect = pygame.Rect(pall_x, pall_y, PALL_SUURUS, PALL_SUURUS)
        alus_rect = pygame.Rect(alus_x, alus_y, ALUS_LAIUS, ALUS_KORGUS)

        # KOKKUPÕRGE ALUSEGA
        if pall_rect.colliderect(alus_rect) and pall_kiirus_y > 0:

            bounce_sound.play()  # põrkeheli

            # Põrge üles
            pall_kiirus_y = -CONST_SPEED_Y

            # Tabamiskoht (mõjutab X-kiirust)
            alus_kesk = alus_x + ALUS_LAIUS / 2
            pall_kesk = pall_x + PALL_SUURUS / 2
            offset = pall_kesk - alus_kesk
            offset_norm = offset / (ALUS_LAIUS / 2)

            # X-kiirus sõltub tabamiskohast
            pall_kiirus_x = int(CONST_SPEED_X * offset_norm)

            # Väldi nullkiirust
            if pall_kiirus_x == 0:
                pall_kiirus_x = random.choice([-2, 2])

            # Skoor +1
            skoor += 1

            # Et pall ei jääks aluse sisse
            pall_y = alus_y - PALL_SUURUS

    # JOONISTAMINE
    ekraan.fill(TAUST)
    ekraan.blit(pall_img, (pall_x, pall_y))
    ekraan.blit(alus_img, (alus_x, alus_y))

    # Skoor ekraanile
    skoor_tekst = font.render(f"Skoor: {skoor}", True, TEKST_VARV)
    ekraan.blit(skoor_tekst, (10, 10))

    # GAME OVER EKRAAN
    if game_over:
        tekst1 = font.render("Mäng läbi!", True, (200, 0, 0))
        tekst2 = font.render("ENTER = restart", True, TEKST_VARV)
        tekst3 = font.render("ESC = välju", True, TEKST_VARV)
        ekraan.blit(tekst1, (LAIUS // 2 - 80, KORGUS // 2 - 40))
        ekraan.blit(tekst2, (LAIUS // 2 - 120, KORGUS // 2))
        ekraan.blit(tekst3, (LAIUS // 2 - 90, KORGUS // 2 + 40))

    pygame.display.flip()
    kell.tick(60)