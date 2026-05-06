#Kristjan IS25 (;
import pygame, sys, random
pygame.init()

# Ekraan
screenX = 640
screenY = 480
screen = pygame.display.set_mode((screenX, screenY))
pygame.display.set_caption("Autode animatsioon")
clock = pygame.time.Clock()

# Pildid
taust = pygame.image.load("img/bg_rally.jpg")
punane = pygame.image.load("img/f1_red.png")
sinine = pygame.image.load("img/f1_blue.png")

# Sõidurajad
rajad = [180, 300, 420]

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
base_speed_min = 4
base_speed_max = 20

# Punane auto
punane_rect = punane.get_rect()
punane_rect.centerx = screenX // 2
punane_rect.bottom = screenY - 20
punane_speed = 10

# Mängu olek
sinised = []
score = 0
paused = False

# Menüü
menu_items = ["Jätka", "Autode arv", "Kiiruse vahemik", "Restart", "Exit"]
menu_index = 0

# Värvikaart (eestikeelsed nimed)
def color(name):
    if not name:
        return None
    name = name.lower()
    mapping = {
        "punane": (255, 0, 0),
        "kollane": (255, 255, 0),
        "roheline": (0, 255, 0),
        "sinine": (0, 0, 255),
        "valge": (255, 255, 255),
        "must": (0, 0, 0),
        "hall": (120, 120, 120),
        "helehall": (200, 200, 200),
        "tumehall": (40, 40, 40)
    }
    return mapping.get(name, None)

# Menüü värvid
menu_colors = {
    "overlay_alpha": 100,
    "selected": "kollane",
    "text": "valge",
    "info": "helehall",
    "instr": "valge"
}

# Sinise auto loomine
def spawn_blue_car(existing, min_spacing=120, attempts=50):
    for _ in range(attempts):
        lane = random.choice(rajad)
        spawn_y = random.randint(-400, -80)
        car_speed = random.randint(base_speed_min, base_speed_max)

        too_close = any(
            car[0] == lane and abs(car[1] - spawn_y) < min_spacing
            for car in existing
        )
        if not too_close:
            return [lane, spawn_y, car_speed]

    return [random.choice(rajad), random.randint(-400, -80),
            random.randint(base_speed_min, base_speed_max)]

# Mängu reset
def reset_game_full():
    global sinised, score
    score = 0
    sinised = [spawn_blue_car([]) for _ in range(blue_car_count)]

# Autode arvu muutmine
def adjust_blue_count(new_count):
    global sinised, blue_car_count
    new_count = max(MIN_CARS, min(MAX_CARS, new_count))

    if new_count > len(sinised):
        for _ in range(new_count - len(sinised)):
            sinised.append(spawn_blue_car(sinised))
    else:
        sinised = sinised[:new_count]

    blue_car_count = new_count

# Kiiruse min muutmine
def adjust_speed_min(new_min):
    global base_speed_min, base_speed_max
    base_speed_min = max(MIN_SPEED, min(MAX_SPEED, new_min))

    if base_speed_min > base_speed_max:
        base_speed_max = base_speed_min

    for i in range(len(sinised)):
        sinised[i][2] = random.randint(base_speed_min, base_speed_max)

# Kiiruse max muutmine
def adjust_speed_max(new_max):
    global base_speed_min, base_speed_max
    base_speed_max = max(MIN_SPEED, min(MAX_SPEED, new_max))

    if base_speed_max < base_speed_min:
        base_speed_min = base_speed_max

    for i in range(len(sinised)):
        sinised[i][2] = random.randint(base_speed_min, base_speed_max)

# HUD (lisatud "Liigu ←→")
def draw_hud():
    avg_speed = sum(c[2] for c in sinised) / len(sinised) if sinised else 0

    screen.blit(font.render(f"Skoor: {score}", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"~kiirus: {avg_speed:.1f}", True, (255, 255, 255)), (10, 40))
    screen.blit(font.render(f"Autod: {len(sinised)}", True, (255, 255, 255)), (10, 70))
    screen.blit(font.render("Liigu ←→", True, (255, 255, 255)), (10, 100))

# Menüü
def draw_menu():
    overlay = pygame.Surface((screenX, screenY), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))

    start_y = 120
    center_x = screenX // 2 - 160

    for i, text in enumerate(menu_items):
        color_val = (255, 220, 0) if i == menu_index else (255, 255, 255)
        screen.blit(menu_font.render(text, True, color_val), (center_x, start_y + i * 48))

    screen.blit(font.render(f"Autode arv: {blue_car_count}/{MAX_CARS}", True, (200, 200, 200)),
                (center_x, start_y + len(menu_items) * 48 + 10))
    screen.blit(font.render(f"Kiirus: {base_speed_min}/{base_speed_max}", True, (200, 200, 200)),
                (center_x, start_y + len(menu_items) * 48 + 40))

    instr = "↑↓ valikud,     ←→ min,     Shift+←→ max,   Enter kinnita"
    screen.blit(font.render(instr, True, (0, 0, 0)),
                (screenX // 2 - font.size(instr)[0] // 2, start_y + len(menu_items) * 48 + 80))

# Siniste autode liikumine
def update_blue_cars():
    global score
    for i in range(len(sinised)):
        lane, car_y, car_speed = sinised[i]
        car_y += car_speed
        sinised[i][1] = car_y

        if car_y > screenY:
            score += 1
            sinised[i] = spawn_blue_car(sinised)

# Käivitus
reset_game_full()

gameover = False
while not gameover:
    clock.tick(60)

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
                    shift = pygame.key.get_mods() & pygame.KMOD_SHIFT

                    if menu_items[menu_index] == "Autode arv":
                        adjust_blue_count(blue_car_count + direction)

                    elif menu_items[menu_index] == "Kiiruse vahemik":
                        if shift:
                            adjust_speed_max(base_speed_max + direction)
                        else:
                            adjust_speed_min(base_speed_min + direction)

                if event.key == pygame.K_RETURN:
                    choice = menu_items[menu_index]
                    if choice == "Jätka":
                        paused = False
                    elif choice == "Restart":
                        reset_game_full()
                        paused = False
                    elif choice == "Exit":
                        sys.exit()

    if paused:
        screen.blit(taust, (0, 0))
        draw_menu()
        pygame.display.flip()
        continue

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and punane_rect.left > 150:
        punane_rect.x -= punane_speed
    if keys[pygame.K_RIGHT] and punane_rect.right < 480:
        punane_rect.x += punane_speed

    screen.blit(taust, (0, 0))
    update_blue_cars()

    for lane, car_y, car_speed in sinised:
        screen.blit(sinine, (lane, car_y))

    screen.blit(punane, punane_rect)
    draw_hud()

    pygame.display.flip()

pygame.quit()
