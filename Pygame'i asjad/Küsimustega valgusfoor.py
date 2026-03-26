import pygame
pygame.init()

# Kasutajasõbralik värvikaart
def color(nimi):
    if not nimi:
        return None
    nimi = nimi.lower()
    kaardistus = {
        "punane": (255, 0, 0),
        "kollane": (255, 255, 0),
        "roheline": (0, 255, 0),
        "sinine": (0, 0, 255),
        "valge": (255, 255, 255),
        "must": (0, 0, 0),
        "hall": (80, 80, 80)
    }
    return kaardistus.get(nimi, None)

# Turvalised sisendi abifunktsioonid
def safe_int(prompt, default):
    valik = input(prompt).strip()
    if valik.isdigit():
        return int(valik)
    return default

def safe_color(prompt, default):
    valik = input(prompt).strip()
    if valik == "":
        return default
    c = color(valik)
    return c if c is not None else default

# Kasutaja sisend
width = safe_int("Sisesta akna laius: ", 300)
height = safe_int("Sisesta akna kõrgus: ", 400)
radius = safe_int("Sisesta foori ringide raadius: ", 25)

# Piirangud akna suurusele
width = max(300, min(width, 600))
height = max(300, min(height, 1000))

# Foori tuled (vaikevärvid kui kasutaja ei sisesta)
first_light = safe_color("1. tule värv (punane?): ", (255, 0, 0))
second_light = safe_color("2. tule värv (kollane?): ", (255, 255, 0))
third_light = safe_color("3. tule värv (roheline?): ", (0, 255, 0))

# Taustavärv (kasutame safe_color, vaike must)
BACKGROUND = safe_color("Sisesta taustavärv (nt 'must', 'sinine') või jäta tühjaks: ", (255, 255, 255))

# Defineeri ekraan ja konstantsed värvid ENNE loopi
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Foor – Kristjan")
GREY = (80, 80, 80)
screen.fill(BACKGROUND)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Keskpunkt foorile
    cx = width // 2
    top_y = 20

    # Foori korpus (keskendatud)
    pygame.draw.rect(screen, GREY, (cx - radius, top_y, radius*2, radius*6))
    pygame.draw.circle(screen, first_light, (cx, top_y + radius), radius)
    pygame.draw.circle(screen, second_light, (cx, top_y + radius*3), radius)
    pygame.draw.circle(screen, third_light, (cx, top_y + radius*5), radius)

    # Post (paigutatud foori alla, suhtelised koordinaadid)
    post_x = cx - 10
    post_y = top_y + radius*6
    pygame.draw.rect(screen, GREY, (post_x, post_y, 20, 140))

    # Postialus (45° küljed) - paigutame suhteliselt akna keskuse alla
    base_top_y = post_y + 130
    pygame.draw.polygon(screen, (0, 0, 0), [
        (cx - 30, base_top_y),   # vasak ülemine
        (cx + 30, base_top_y),   # parem ülemine
        (cx + 50, base_top_y + 40),  # parem alumine
        (cx - 50, base_top_y + 40)   # vasak alumine
    ])

    # Eesti lipp postialuse sees (suhtelised koordinaadid)
    flag_x = cx - 35
    flag_y = base_top_y + 5
    flag_w = 70
    flag_h = 10
    pygame.draw.rect(screen, (0, 114, 206), (flag_x, flag_y, flag_w, flag_h))   # sinine
    pygame.draw.rect(screen, (0, 0, 0),     (flag_x, flag_y + flag_h, flag_w, flag_h))  # must
    pygame.draw.rect(screen, (255, 255, 255),(flag_x, flag_y + 2*flag_h, flag_w, flag_h)) # valge

    pygame.display.flip()

pygame.quit()
