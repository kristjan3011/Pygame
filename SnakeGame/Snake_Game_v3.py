"""
Snake Game – Kristjan IS25
Versioon: 3.0 LITE
"""

import pygame
import random

pygame.init()

# -------------------------------------------------------
# KONSTANDID
# -------------------------------------------------------
LAIUS = 1280
KORGUS = 720
PLOKK = 20

TEEMAD: dict[str, dict[str, tuple[int, int, int]]] = {
    "Klassikaline": {
        "taust": (20, 60, 120),
        "ruudustik": (25, 70, 135),
        "mao_pea": (50, 220, 100),
        "mao_keha": (0, 170, 55),
        "toit": (34, 180, 80),
        "boonus": (255, 215, 0),
    },
    "Neon": {
        "taust": (10, 10, 30),
        "ruudustik": (40, 0, 60),
        "mao_pea": (0, 255, 255),
        "mao_keha": (0, 150, 200),
        "toit": (255, 0, 255),
        "boonus": (255, 255, 0),
    },
    "Punane": {
        "taust": (60, 10, 10),
        "ruudustik": (100, 20, 20),
        "mao_pea": (255, 100, 100),
        "mao_keha": (200, 50, 50),
        "toit": (100, 255, 100),
        "boonus": (255, 255, 100),
    },
}

VALGE = (255, 255, 255)
MUST = (0, 0, 0)
HALL = (180, 180, 180)
TUME_HALL = (90, 90, 90)
MENUU_TAUST = (15, 45, 95)
KULDNE = (255, 215, 0)

RASKUSED: dict[str, tuple[float, float, float]] = {
    "Lihtne":   (6,  0.3, 12),
    "Keskmine": (10, 0.5, 18),
    "Raske":    (15, 0.8, 25),
}
RASKUSED_JARJESTUS = list(RASKUSED.keys())

font_suur = pygame.font.SysFont("Arial", 40)
font_tavaline = pygame.font.SysFont("Arial", 25)
font_vike = pygame.font.SysFont("Arial", 18)

_fullscreen = False
ekraan = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Snake Game – Kristjan IS25 v3 LITE")
kell = pygame.time.Clock()


# -------------------------------------------------------
# ABIFUNKTSIOONID
# -------------------------------------------------------
def toggle_fullscreen() -> None:
    global ekraan, _fullscreen
    _fullscreen = not _fullscreen
    if _fullscreen:
        ekraan = pygame.display.set_mode((LAIUS, KORGUS), pygame.FULLSCREEN)
    else:
        ekraan = pygame.display.set_mode((LAIUS, KORGUS))


def tekst_tsentris(pind: pygame.Surface, sisu: str,
                   font: pygame.font.Font, varv, y_nihutus: int = 0) -> None:
    renderdatud = font.render(sisu, True, varv)
    x = LAIUS // 2 - renderdatud.get_width() // 2
    y = KORGUS // 2 + y_nihutus
    pind.blit(renderdatud, (x, y))


def juhuslik_koht(keelatud: set[tuple[int, int]] | list[tuple[int, int]]):
    koik = [(x, y) for x in range(0, LAIUS, PLOKK)
                    for y in range(0, KORGUS, PLOKK)]
    keelatud_set = set(keelatud)
    vabad = [pos for pos in koik if pos not in keelatud_set]
    return random.choice(vabad) if vabad else None


def loo_ruudustiku_pind(teema_nimi: str) -> pygame.Surface:
    pind = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
    joone_varv = (*TEEMAD[teema_nimi]["ruudustik"], 70)
    for x in range(0, LAIUS, PLOKK):
        pygame.draw.line(pind, joone_varv, (x, 0), (x, KORGUS))
    for y in range(0, KORGUS, PLOKK):
        pygame.draw.line(pind, joone_varv, (0, y), (LAIUS, y))
    return pind


# -------------------------------------------------------
# SNAKE
# -------------------------------------------------------
class Snake:
    def __init__(self) -> None:
        self.x: int = 0
        self.y: int = 0
        self.suund_x: int = 0
        self.suund_y: int = 0
        self.keha: list[tuple[int, int]] = []
        self.pikkus: int = 1
        self.buffer: tuple[int, int] | None = None
        self.alustanud: bool = False
        self.reset()

    def reset(self) -> None:
        self.x = LAIUS // 2
        self.y = KORGUS // 2
        self.suund_x = 0
        self.suund_y = 0
        self.keha = [(self.x, self.y)]
        self.pikkus = 1
        self.buffer = None
        self.alustanud = False

    def muuda_suund(self, dx: int, dy: int) -> None:
        if dx != 0 and dx == -self.suund_x:
            return
        if dy != 0 and dy == -self.suund_y:
            return
        if dx == self.suund_x and dy == self.suund_y:
            return
        self.buffer = (dx, dy)
        self.alustanud = True

    def liiguta(self) -> bool:
        if self.buffer:
            self.suund_x, self.suund_y = self.buffer
            self.buffer = None

        self.x += self.suund_x
        self.y += self.suund_y

        if self.x < 0 or self.x >= LAIUS or self.y < 0 or self.y >= KORGUS:
            return False

        self.keha.append((self.x, self.y))
        if len(self.keha) > self.pikkus:
            self.keha.pop(0)

        if (self.x, self.y) in self.keha[:-1]:
            return False

        return True

    def joonista(self, pind: pygame.Surface, teema: dict) -> None:
        pea_varv = teema["mao_pea"]
        keha_varv = teema["mao_keha"]

        for i, (bx, by) in enumerate(self.keha):
            varv = pea_varv if i == len(self.keha) - 1 else keha_varv
            pygame.draw.rect(pind, varv, (bx + 1, by + 1, PLOKK - 2, PLOKK - 2))

        if self.alustanud:
            self._joonista_silmad(pind, self.x, self.y)

    def _joonista_silmad(self, pind: pygame.Surface, x: int, y: int) -> None:
        if self.suund_x == PLOKK:
            s1, s2 = (x + 14, y + 4), (x + 14, y + 12)
        elif self.suund_x == -PLOKK:
            s1, s2 = (x + 4, y + 4), (x + 4, y + 12)
        elif self.suund_y == -PLOKK:
            s1, s2 = (x + 4, y + 4), (x + 12, y + 4)
        else:
            s1, s2 = (x + 4, y + 14), (x + 12, y + 14)

        for silm in (s1, s2):
            pygame.draw.circle(pind, VALGE, silm, 3)
            pygame.draw.circle(pind, MUST, silm, 1)


# -------------------------------------------------------
# TOIT
# -------------------------------------------------------
class Toit:
    def __init__(self, tyyp: str = "tavaline") -> None:
        self.tyyp: str = tyyp
        self.punktid: int = 1 if tyyp == "tavaline" else 3
        self.kiiruse_kasv: float = 0.5 if tyyp == "tavaline" else 1.0
        self.elu_iga: int | None = None
        self.x: int = 0
        self.y: int = 0
        self.spawn_aeg: int = 0

    def spawni(self, keelatud: set[tuple[int, int]] | list[tuple[int, int]]) -> None:
        koht = juhuslik_koht(keelatud)
        if koht:
            self.x, self.y = koht
            self.spawn_aeg = pygame.time.get_ticks()

    def on_aegunud(self) -> bool:
        if self.elu_iga is None:
            return False
        return pygame.time.get_ticks() - self.spawn_aeg > self.elu_iga

    def joonista(self, pind: pygame.Surface, teema: dict) -> None:
        varv = teema["toit"] if self.tyyp == "tavaline" else teema["boonus"]
        pygame.draw.rect(pind, varv, (self.x + 2, self.y + 2, PLOKK - 4, PLOKK - 4))


# -------------------------------------------------------
# MÄNG
# -------------------------------------------------------
class Mang:
    def __init__(self) -> None:
        # Seaded
        self.heli_sees: bool = True
        self.ruudustik_sees: bool = True
        self.raskus: str = "Keskmine"
        self.teema_nimi: str = "Klassikaline"
        self.algus_reziim: str = "oota"
        self.helitugevus: int = 5

        # Helid
        self.soomis_heli: pygame.mixer.Sound | None = None
        self.gameover_heli: pygame.mixer.Sound | None = None
        self._laadi_helid()

        # Visuaal
        self.ruudustiku_pind: pygame.Surface = loo_ruudustiku_pind(self.teema_nimi)

        # Objektid
        self.madu: Snake = Snake()
        self.toit: Toit = Toit("tavaline")
        self.boonus: Toit = Toit("boonus")
        self.boonus.elu_iga = 5000  # 5 sekundit

        # Olek
        self.skoor: int = 0
        self.tase: int = 1
        self.rekord: int = 0
        alg, kasv, maks = RASKUSED[self.raskus]
        self.kiirus: float = alg
        self.kiiruse_kasv: float = kasv
        self.kiiruse_maks: float = maks
        self.paus: bool = False

    # ---------------------------------------------------
    # HELID
    # ---------------------------------------------------
    def _laadi_helid(self) -> None:
        try:
            pygame.mixer.music.load("music/soundtrack.mp3")
            pygame.mixer.music.play(-1)
            self.soomis_heli = pygame.mixer.Sound("music/apple-crunch.mp3")
            self.gameover_heli = pygame.mixer.Sound("music/gameover.mp3")
            self._uuenda_helitugevus()
        except Exception:
            # Kui helisid pole, mäng töötab ikkagi
            self.soomis_heli = None
            self.gameover_heli = None

    def _uuenda_helitugevus(self) -> None:
        vol = self.helitugevus / 10.0
        try:
            pygame.mixer.music.set_volume(vol * 0.5)
        except Exception:
            pass
        if self.soomis_heli:
            self.soomis_heli.set_volume(vol)
        if self.gameover_heli:
            self.gameover_heli.set_volume(vol)

    def _helista(self, heli: pygame.mixer.Sound | None) -> None:
        if heli and self.heli_sees:
            heli.play()

    # ---------------------------------------------------
    # RESET
    # ---------------------------------------------------
    def reset(self) -> None:
        alg, kasv, maks = RASKUSED[self.raskus]
        self.kiirus = alg
        self.kiiruse_kasv = kasv
        self.kiiruse_maks = maks

        self.skoor = 0
        self.tase = 1
        self.paus = False
        self.madu.reset()

        keelatud = set(self.madu.keha)
        self.toit.spawni(keelatud)

        keelatud.add((self.toit.x, self.toit.y))
        self.boonus.spawni(keelatud)

        self._uuenda_helitugevus()

    # ---------------------------------------------------
    # TOIT
    # ---------------------------------------------------
    def _kontrolli_toit(self) -> None:
        px, py = self.madu.x, self.madu.y

        if (px, py) == (self.toit.x, self.toit.y):
            self._soo(self.toit)
            self._spawni_toit()

        if (px, py) == (self.boonus.x, self.boonus.y):
            self._soo(self.boonus)
            self._spawni_boonus()

        if self.boonus.on_aegunud():
            self._spawni_boonus()

    def _spawni_toit(self) -> None:
        keelatud = set(self.madu.keha)
        keelatud.add((self.boonus.x, self.boonus.y))
        self.toit.spawni(keelatud)

    def _spawni_boonus(self) -> None:
        keelatud = set(self.madu.keha)
        keelatud.add((self.toit.x, self.toit.y))
        self.boonus.spawni(keelatud)

    # ---------------------------------------------------
    # SÖÖMINE
    # ---------------------------------------------------
    def _soo(self, toit: Toit) -> None:
        self._helista(self.soomis_heli)
        self.madu.pikkus += toit.punktid
        self.skoor += toit.punktid
        self.kiirus = min(self.kiirus + toit.kiiruse_kasv, self.kiiruse_maks)

        uus_tase = (self.skoor // 10) + 1
        if uus_tase > self.tase:
            self.tase = uus_tase

    # ---------------------------------------------------
    # GAME OVER
    # ---------------------------------------------------
    def game_over(self):
        self._helista(self.gameover_heli)

        while True:
            ekraan.fill(self.teema["taust"])
            tekst_tsentris(ekraan, "GAME OVER", font_suur, VALGE, -80)
            tekst_tsentris(ekraan, f"Skoor: {self.skoor}", font_tavaline, VALGE, -20)
            tekst_tsentris(ekraan, "ENTER – uuesti", font_tavaline, HALL, 40)
            tekst_tsentris(ekraan, "ESC – menüüsse", font_tavaline, HALL, 80)
            pygame.display.flip()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN:
                        self.reset()
                        return "restart"
                    if e.key == pygame.K_ESCAPE:
                        return "menu"

    # ---------------------------------------------------
    # JOONISTAMINE
    # ---------------------------------------------------
    @property
    def teema(self) -> dict:
        return TEEMAD[self.teema_nimi]

    def _joonista_hud(self) -> None:
        s_pind = font_tavaline.render(f"Skoor: {self.skoor}", True, VALGE)
        r_pind = font_tavaline.render(f"Rekord: {self.rekord}", True, KULDNE)
        t_pind = font_vike.render(f"Tase: {self.tase}", True, HALL)
        p_pind = font_vike.render("P – paus", True, HALL)
        d_pind = font_vike.render(self.raskus, True, HALL)

        ekraan.blit(s_pind, (10, 10))
        ekraan.blit(r_pind, (10, 38))
        ekraan.blit(t_pind, (10, 66))
        ekraan.blit(p_pind, (10, 94))
        ekraan.blit(d_pind, (LAIUS - d_pind.get_width() - 10, 10))

    def _joonista_valja(self) -> None:
        ekraan.fill(self.teema["taust"])
        if self.ruudustik_sees:
            ekraan.blit(self.ruudustiku_pind, (0, 0))
        self.toit.joonista(ekraan, self.teema)
        self.boonus.joonista(ekraan, self.teema)
        self.madu.joonista(ekraan, self.teema)
        self._joonista_hud()

    @staticmethod
    def _paus_kate() -> None:
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
        kate.fill((0, 0, 0, 150))
        ekraan.blit(kate, (0, 0))
        tekst_tsentris(ekraan, "PAUS", font_suur, VALGE, -25)
        tekst_tsentris(ekraan, "P – jätka mängu", font_tavaline, HALL, 25)

    # ---------------------------------------------------
    # MENÜÜ
    # ---------------------------------------------------
    def algus_meniu(self):
        valikud = ["Alusta mängu", "Seaded", "Credits", "Välju"]
        valitud = 0

        while True:
            ekraan.fill(MENUU_TAUST)
            tekst_tsentris(ekraan, "SNAKE GAME", font_suur, KULDNE, -150)
            tekst_tsentris(ekraan, "Kristjan – IS25 | v3 LITE", font_vike, HALL, -100)

            for i, v in enumerate(valikud):
                varv = VALGE if i == valitud else TUME_HALL
                tekst_tsentris(ekraan, v, font_tavaline, varv, -30 + i * 50)

            tekst_tsentris(ekraan, "↑ ↓ – vali   ENTER – kinnita", font_vike, HALL, 150)
            pygame.display.flip()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_UP:
                        valitud = (valitud - 1) % len(valikud)
                    elif e.key == pygame.K_DOWN:
                        valitud = (valitud + 1) % len(valikud)
                    elif e.key == pygame.K_RETURN:
                        return valikud[valitud].lower()

            kell.tick(30)

    # ---------------------------------------------------
    # SEADED
    # ---------------------------------------------------
    def _seadete_kuva(self) -> None:
        ekraan.fill(MENUU_TAUST)
        tekst_tsentris(ekraan, "SEADED", font_suur, KULDNE, -180)

        heli_tekst = f"Heli:       {'SEES  ✓' if self.heli_sees else 'VÄLJAS ✗'}"
        heli_varv = (34, 180, 80) if self.heli_sees else (220, 60, 60)
        tekst_tsentris(ekraan, heli_tekst, font_tavaline, heli_varv, -110)

        grid_tekst = f"Ruudustik: {'SEES  ✓' if self.ruudustik_sees else 'VÄLJAS ✗'}"
        grid_varv = (34, 180, 80) if self.ruudustik_sees else (220, 60, 60)
        tekst_tsentris(ekraan, grid_tekst, font_tavaline, grid_varv, -60)

        tekst_tsentris(ekraan, f"Raskus:    {self.raskus}", font_tavaline, VALGE, -10)
        tekst_tsentris(ekraan, f"Teema:     {self.teema_nimi}", font_tavaline, VALGE, 40)
        tekst_tsentris(ekraan, f"Helitugevus: {self.helitugevus}", font_tavaline, VALGE, 90)

        algus_tekst = "Algus:     " + ("Kohe" if self.algus_reziim == "kohe" else "Oota klahvi")
        tekst_tsentris(ekraan, algus_tekst, font_tavaline, VALGE, 140)

        fs_tekst = f"Ekraan:    {'Täisekraan ✓' if _fullscreen else 'Aken ✗'}"
        fs_varv = (34, 180, 80) if _fullscreen else (220, 60, 60)
        tekst_tsentris(ekraan, fs_tekst, font_tavaline, fs_varv, 190)

        tekst_tsentris(
            ekraan,
            "1–Heli  2–Ruudustik  3–Raskus  4–Teema  7–Algus",
            font_vike,
            HALL,
            235,
        )
        tekst_tsentris(
            ekraan,
            "5–Vol–   6–Vol+   F–Ekraan   ESC–tagasi",
            font_vike,
            HALL,
            258,
        )

    def _seadete_klahv(self, key: int) -> None:
        if key == pygame.K_1:
            self.heli_sees = not self.heli_sees
            try:
                if self.heli_sees:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
            except Exception:
                pass

        elif key == pygame.K_2:
            self.ruudustik_sees = not self.ruudustik_sees

        elif key == pygame.K_3:
            idx = RASKUSED_JARJESTUS.index(self.raskus)
            self.raskus = RASKUSED_JARJESTUS[(idx + 1) % len(RASKUSED_JARJESTUS)]

        elif key == pygame.K_4:
            teemad = list(TEEMAD.keys())
            idx = teemad.index(self.teema_nimi)
            self.teema_nimi = teemad[(idx + 1) % len(teemad)]
            self.ruudustiku_pind = loo_ruudustiku_pind(self.teema_nimi)

        elif key == pygame.K_5:
            self.helitugevus = max(0, self.helitugevus - 1)
            self._uuenda_helitugevus()

        elif key == pygame.K_6:
            self.helitugevus = min(10, self.helitugevus + 1)
            self._uuenda_helitugevus()

        elif key == pygame.K_7:
            self.algus_reziim = "kohe" if self.algus_reziim == "oota" else "oota"

    def seaded(self) -> None:
        while True:
            self._seadete_kuva()
            pygame.display.flip()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        return
                    if e.key == pygame.K_f:
                        toggle_fullscreen()
                    else:
                        self._seadete_klahv(e.key)

    # ---------------------------------------------------
    # CREDITS
    # ---------------------------------------------------
    def credits_ekraan(self) -> None:
        while True:
            ekraan.fill(MENUU_TAUST)
            tekst_tsentris(ekraan, "CREDITS", font_suur, KULDNE, -150)
            tekst_tsentris(ekraan, "Autor: Kristjan – IS25", font_tavaline, VALGE, -50)
            tekst_tsentris(ekraan, "Snake Game v3 LITE", font_tavaline, VALGE, 0)
            tekst_tsentris(ekraan, "ESC – tagasi", font_vike, HALL, 150)

            pygame.display.flip()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return

    # ---------------------------------------------------
    # MÄNGUTSÜKKEL
    # ---------------------------------------------------
    def run(self) -> None:
        while True:
            valik = self.algus_meniu()
            if valik is None or valik == "välju":
                return
            if valik == "seaded":
                self.seaded()
            elif valik == "credits":
                self.credits_ekraan()
            elif valik == "alusta mängu":
                self.mangu_loop()

    # ---------------------------------------------------
    # MÄNGU LOOP
    # ---------------------------------------------------
    def mangu_loop(self) -> None:
        self.reset()

        if self.algus_reziim == "oota":
            self._oota_algust()

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_p:
                        self.paus = not self.paus
                    elif e.key == pygame.K_f:
                        toggle_fullscreen()
                    elif e.key == pygame.K_UP:
                        self.madu.muuda_suund(0, -PLOKK)
                    elif e.key == pygame.K_DOWN:
                        self.madu.muuda_suund(0, PLOKK)
                    elif e.key == pygame.K_LEFT:
                        self.madu.muuda_suund(-PLOKK, 0)
                    elif e.key == pygame.K_RIGHT:
                        self.madu.muuda_suund(PLOKK, 0)

            if self.paus:
                self._joonista_valja()
                self._paus_kate()
                pygame.display.flip()
                kell.tick(10)
                continue

            elus = self.madu.liiguta()
            if not elus:
                tulemus = self.game_over()
                if tulemus == "restart":
                    self.reset()
                    continue
                return

            self._kontrolli_toit()
            self._joonista_valja()
            pygame.display.flip()
            kell.tick(int(self.kiirus))

    # ---------------------------------------------------
    # OOTA ALGUST
    # ---------------------------------------------------
    def _oota_algust(self) -> None:
        while True:
            ekraan.fill(self.teema["taust"])
            tekst_tsentris(
                ekraan,
                "Vajuta suvalist klahvi alustamiseks",
                font_tavaline,
                VALGE,
                0,
            )
            pygame.display.flip()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN:
                    return


# -------------------------------------------------------
# KÄIVITAMINE
# -------------------------------------------------------
if __name__ == "__main__":
    Mang().run()
    pygame.quit()