# Kristjan IS25 (;
import pygame, sys, random
pygame.init()

# Ekraani seaded
SCREEN_W, SCREEN_H = 640, 480
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Autode animatsioon")
clock = pygame.time.Clock()

# Pildid
background = pygame.image.load("img/bg_rally.jpg")
car_red = pygame.image.load("img/f1_red.png")
car_blue = pygame.image.load("img/f1_blue.png")

# Sõidurajad (fikseeritud)
LANES = [180, 300, 420]

# Fondid
font = pygame.font.SysFont("Arial", 24)
menu_font = pygame.font.SysFont("Arial", 34)

# Piirangud
MIN_CARS = 1
MAX_CARS = 8
MIN_SPEED = 4
MAX_SPEED = 20

# Algseaded
blue_car_count = 3
blue_speed = 8  # Kõik sinised autod kasutavad sama kiirust

# Punase auto seaded
red_rect = car_red.get_rect()
red_rect.centerx = SCREEN_W // 2
red_rect.bottom = SCREEN_H - 20
red_speed = 10

# Mängu olek
blue_cars = []
score = 0
paused = False

# Menüü
menu_items = ["Jätka", "Autode arv", "Kiirus", "Restart", "Exit"]
menu_index = 0


# Sinise auto loomine ilma overlapinguta
def spawn_blue_car(existing, speed, min_spacing=300, attempts=200):
    # Loob sinise auto nii, et ükski auto ei oleks teisega samal rajal liiga lähedal
    for _ in range(attempts):
        lane = random.choice(LANES)
        spawn_y = random.randint(-600, -120)

        too_close = any(
            car[0] == lane and abs(car[1] - spawn_y) < min_spacing
            for car in existing
        )

        if not too_close:
            return [lane, spawn_y, speed]

    # Kui ruumi ei leita, paigutame auto kindlalt eelmisest kõrgemale
    lane = random.choice(LANES)
    highest = min((car[1] for car in existing if car[0] == lane), default=-600)
    return [lane, highest - min_spacing, speed]

# Mängu täielik reset
def reset_game():
    # Nullib skoori ja loob sinised autod uuesti ühe kiirusega
    global blue_cars, score
    score = 0
    blue_cars = []

    for _ in range(blue_car_count):
        blue_cars.append(spawn_blue_car(blue_cars, blue_speed))

# Siniste autode arvu muutmine
def set_blue_car_count(new_count):
    # Uuendab siniste autode arvu ja teeb mängu reseti
    global blue_car_count
    blue_car_count = max(MIN_CARS, min(MAX_CARS, new_count))
    reset_game()

# Siniste autode kiiruse muutmine
def set_blue_speed(new_speed):
    # Uuendab kõigi siniste autode kiirust ja teeb mängu reseti
    global blue_speed
    blue_speed = max(MIN_SPEED, min(MAX_SPEED, new_speed))
    reset_game()

# HUD joonistamine
def draw_hud():
    # Kuvab skoori, kiiruse, autode arvu ja liikumisjuhise
    screen.blit(font.render(f"Skoor: {score}", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Kiirus: {blue_speed}", True, (255, 255, 255)), (10, 40))
    screen.blit(font.render(f"Autod: {len(blue_cars)}", True, (255, 255, 255)), (10, 70))
    screen.blit(font.render("Liigu ←→", True, (255, 255, 255)), (10, 100))

# Menüü joonistamine
def draw_menu():
    # Kuvab menüü koos läbipaistva taustaga
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))

    start_y = 120
    center_x = SCREEN_W // 2 - 160

    for i, text in enumerate(menu_items):
        color = (255, 220, 0) if i == menu_index else (255, 255, 255)
        screen.blit(menu_font.render(text, True, color), (center_x, start_y + i * 48))

    # Lisainfo min/max väärtustega
    screen.blit(font.render(
        f"Autode arv: {blue_car_count} (min {MIN_CARS} / max {MAX_CARS})",
        True, (200, 200, 200)),
        (center_x, start_y + len(menu_items) * 48 + 10)
    )

    screen.blit(font.render(
        f"Kiirus: {blue_speed} (min {MIN_SPEED} / max {MAX_SPEED})",
        True, (200, 200, 200)),
        (center_x, start_y + len(menu_items) * 48 + 40)
    )

# Siniste autode liigutamine
def update_blue_cars():
    # Liigutab siniseid autosid alla ja respawnib need ekraanilt lahkudes
    global score
    for i in range(len(blue_cars)):
        lane, y, speed = blue_cars[i]
        y += speed
        blue_cars[i][1] = y

        if y > SCREEN_H:
            score += 1
            blue_cars[i] = spawn_blue_car(blue_cars, blue_speed)

# Mängu käivitamine
reset_game()

gameover = False
while not gameover:
    clock.tick(60)

    # Sündmuste töötlemine
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused

            if paused:
                if event.key == pygame.K_UP:
                    menu_index = (menu_index - 1) % len(menu_items)
                if event.key == pygame.K_DOWN:
                    menu_index = (menu_index + 1) % len(menu_items)

                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    direction = 1 if event.key == pygame.K_RIGHT else -1

                    if menu_items[menu_index] == "Autode arv":
                        set_blue_car_count(blue_car_count + direction)

                    elif menu_items[menu_index] == "Kiirus":
                        set_blue_speed(blue_speed + direction)

                if event.key == pygame.K_RETURN:
                    choice = menu_items[menu_index]
                    if choice == "Jätka":
                        paused = False
                    elif choice == "Restart":
                        reset_game()
                        paused = False
                    elif choice == "Exit":
                        sys.exit()

    # Pausirežiim
    if paused:
        screen.blit(background, (0, 0))
        draw_menu()
        pygame.display.flip()
        continue

    # Punase auto liikumine
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and red_rect.left > 150:
        red_rect.x -= red_speed
    if keys[pygame.K_RIGHT] and red_rect.right < 480:
        red_rect.x += red_speed

    # Kaadri joonistamine
    screen.blit(background, (0, 0))
    update_blue_cars()

    for lane, y, speed in blue_cars:
        screen.blit(car_blue, (lane, y))

    screen.blit(car_red, red_rect)
    draw_hud()

    pygame.display.flip()

pygame.quit()