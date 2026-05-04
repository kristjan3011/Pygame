import pygame
import sys

pygame.init()

# seaded
seaded = {
    "laius":        640,
    "korgus":       480,
    "ruudu_suurus": 20,
    "kiirus":       5,
    "suund":        "alla",   # joonistamise suund
    "värv_indeks":  0,        # aktiivne värv
}

# värvid
palett = [
    (255,   0,   0),   # punane
    (0,     0, 255),   # sinine
    (255, 165,   0),   # oranž
    (148,   0, 211),   # lilla
    (0,     0,   0),   # must
    (255, 255, 255),   # valge
]

# värvinimed (pikad)
värvinimed = {
    (255, 0, 0): "PUNANE",
    (0, 0, 255): "SININE",
    (255, 165, 0): "ORANŽ",
    (148, 0, 211): "LILLA",
    (0, 0, 0): "MUST",
    (255, 255, 255): "VALGE",
}

# lühenda värvinimi 4 tähemärgini
def lühenda(tekst, pikkus=4):
    return tekst[:pikkus].ljust(pikkus)

tausta_värv = (144, 255, 144)
hud_tekst   = (255, 255, 255)
hud_vari    = (0, 0, 0)

# klahvikaart
klahvid = {
    pygame.K_UP:    ("ruudu_suurus", +2,  4,   100),
    pygame.K_DOWN:  ("ruudu_suurus", -2,  4,   100),
    pygame.K_RIGHT: ("kiirus",       +1,  1,    50),
    pygame.K_LEFT:  ("kiirus",       -1,  1,    50),
    pygame.K_w:     ("korgus",      +20, 200,  900),
    pygame.K_x:     ("korgus",      -20, 200,  900),
    pygame.K_d:     ("laius",       +20, 300, 1400),
    pygame.K_a:     ("laius",       -20, 300, 1400),
}

# ruudustiku koordinaadid
def arvuta_ruudud(laius, korgus, suurus, suund):
    veerud = laius  // suurus
    read   = korgus // suurus
    if suund == "alla":
        return [(v * suurus, r * suurus) for v in range(veerud) for r in range(read)]
    else:
        return [(v * suurus, r * suurus) for v in range(veerud) for r in range(read - 1, -1, -1)]

# ekraani loomine
def loo_ekraan(s):
    ekraan = pygame.display.set_mode((s["laius"], s["korgus"]))
    pygame.display.set_caption("Harjutamine")
    ekraan.fill(tausta_värv)
    return ekraan

# HUD tekst
def hud_ridad(s):
    värv = palett[s["värv_indeks"]]
    värvitekst = lühenda(värvinimed.get(värv, "TUND"))
    return [
        f"ruudu suurus: {s['ruudu_suurus']}px            [↑/↓]",
        f"kiirus:       {s['kiirus']} ruutu/kaader  [←/→]",
        f"suund:        {s['suund']}            [s]",
        f"laius:        {s['laius']}px           [a/d]",
        f"kõrgus:       {s['korgus']}px           [w/x]",
        f"joonevärv:    {värvitekst}            [v]",
        f"taaskäivita:                  [r]",
        f"välju mängust:                [ESC]",
    ]

# algseis
ekraan      = loo_ekraan(seaded)
ruudud      = arvuta_ruudud(seaded["laius"], seaded["korgus"], seaded["ruudu_suurus"], seaded["suund"])
joonistatud = 0
font        = pygame.font.SysFont("Consolas", 18)
kell        = pygame.time.Clock()
pygame.key.set_repeat(300, 60)
vilgutuse_aeg = 0

HUD_LAIUS  = 360
HUD_KORGUS = 200

# põhiloop
while True:
    taaskäivita = False

    # sündmused
    for sündmus in pygame.event.get():
        if sündmus.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if sündmus.type == pygame.KEYDOWN:

            if sündmus.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            if sündmus.key == pygame.K_s:
                seaded["suund"] = "üles" if seaded["suund"] == "alla" else "alla"
                taaskäivita = True

            elif sündmus.key == pygame.K_r:
                taaskäivita = True

            elif sündmus.key == pygame.K_v:
                seaded["värv_indeks"] = (seaded["värv_indeks"] + 1) % len(palett)
                vilgutuse_aeg = pygame.time.get_ticks()

            elif sündmus.key in klahvid:
                seade, muutus, mini, maxi = klahvid[sündmus.key]
                seaded[seade] = max(mini, min(maxi, seaded[seade] + muutus))
                taaskäivita = True
                vilgutuse_aeg = pygame.time.get_ticks()

    # ekraani uuendus
    if taaskäivita:
        ekraan      = loo_ekraan(seaded)
        ruudud      = arvuta_ruudud(seaded["laius"], seaded["korgus"], seaded["ruudu_suurus"], seaded["suund"])
        joonistatud = 0

    joonevärv = palett[seaded["värv_indeks"]]

    # ruudustik
    for _ in range(seaded["kiirus"]):
        if joonistatud < len(ruudud):
            x, y = ruudud[joonistatud]
            pygame.draw.rect(ekraan, joonevärv, (x, y, seaded["ruudu_suurus"], seaded["ruudu_suurus"]), 1)
            joonistatud += 1

    # HUD taust
    hud_pind = pygame.Surface((HUD_LAIUS, HUD_KORGUS), pygame.SRCALPHA)
    hud_pind.fill((220, 220, 220, 200))
    ekraan.blit(hud_pind, (5, 5))

    # HUD tekst
    if pygame.time.get_ticks() - vilgutuse_aeg < 200:
        tekstivärv = (255, 200, 0)
    else:
        tekstivärv = hud_tekst

    for i, rida in enumerate(hud_ridad(seaded)):
        ekraan.blit(font.render(rida, True, hud_vari), (11, 11 + i * 22))
        ekraan.blit(font.render(rida, True, tekstivärv), (10, 10 + i * 22))

    pygame.display.flip()
    kell.tick(60)
