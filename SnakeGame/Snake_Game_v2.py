"""
Snake Game
Autor:   Kristjan – IS25
Versioon: 2.0
Kirjeldus: Uuendatud Snake mäng PyGame'iga.
           Sisaldab tasemesüsteemi, takistusi, ajapõhiseid boonuseid,
           visuaalseid efekte, saavutusi, statistikat ja credits-ekraani.
"""

import pygame
import random
import math
import json
import os
from datetime import datetime

# -------------------------------------------------------
# PYGAME INITSIALISEERIMINE
# -------------------------------------------------------
pygame.init()

# -------------------------------------------------------
# GLOBAALSED KONSTANDID
# -------------------------------------------------------
LAIUS = 640
KORGUS = 480
PLOKK = 20

# Värviteemad (saab menüüst vahetada)
TEEMAD = {
    "Klassikaline": {
        "taust": (20, 60, 120),
        "ruudustik": (25, 70, 135),
        "mao_pea": (50, 220, 100),
        "mao_keha": (0, 170, 55),
        "toit": (34, 180, 80),
        "boonus": (255, 215, 0),
        "takistus": (139, 69, 19),
    },
    "Neon": {
        "taust": (10, 10, 30),
        "ruudustik": (40, 0, 60),
        "mao_pea": (0, 255, 255),
        "mao_keha": (0, 150, 200),
        "toit": (255, 0, 255),
        "boonus": (255, 255, 0),
        "takistus": (255, 80, 0),
    },
    "Punane": {
        "taust": (60, 10, 10),
        "ruudustik": (100, 20, 20),
        "mao_pea": (255, 100, 100),
        "mao_keha": (200, 50, 50),
        "toit": (100, 255, 100),
        "boonus": (255, 255, 100),
        "takistus": (80, 80, 80),
    },
}

# Üldised värvid
VALGE = (255, 255, 255)
MUST = (0, 0, 0)
PUNANE = (180, 20, 20)
HALL = (180, 180, 180)
TUME_HALL = (90, 90, 90)
MENUU_TAUST = (15, 45, 95)

# Raskusastmed (algkiirus, kiiruse kasv, max kiirus)
RASKUSED = {
    "Lihtne": (6, 0.3, 12),
    "Keskmine": (10, 0.5, 18),
    "Raske": (15, 0.8, 25),
}
RASKUSED_JARJESTUS = list(RASKUSED.keys())

# Fondid
font_suur = pygame.font.SysFont("Arial", 40)
font_tavaline = pygame.font.SysFont("Arial", 25)
font_vike = pygame.font.SysFont("Arial", 18)

# Aken ja kell
ekraan = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Snake Game – Kristjan IS25 v2.0")
kell = pygame.time.Clock()

# -------------------------------------------------------
# STATISTIKA HALDUS (salvestatakse JSON-faili)
# -------------------------------------------------------
class Statistika:
    def __init__(self, fail="snake_stats.json"):
        self.fail = os.path.join(os.path.dirname(__file__), fail)
        self.andmed = self.lae()

    def lae(self):
        vaikimisi = {
            "mangude_arv": 0,
            "parim_skoor": 0,
            "parim_tase": 0,
            "skooride_summa": 0,
            "ajalugu": [],
            "saavutused": {
                "Esimene suutäis": False,
                "10 punkti klubis": False,
                "Ellujääja": False,
                "Kiirusemeister": False,
                "Boonusekütt": False,
                "Suurmeister": False,
            }
        }
        try:
            with open(self.fail, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return vaikimisi

    def salvesta(self):
        with open(self.fail, "w", encoding="utf-8") as f:
            json.dump(self.andmed, f, ensure_ascii=False, indent=2)

    def lisa_mang(self, skoor, tase):
        self.andmed["mangude_arv"] += 1
        self.andmed["skooride_summa"] += skoor
        self.andmed["parim_skoor"] = max(self.andmed["parim_skoor"], skoor)
        self.andmed["parim_tase"] = max(self.andmed["parim_tase"], tase)
        self.andmed["ajalugu"].append({
            "aeg": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "skoor": skoor,
            "tase": tase,
        })
        # Säilita viimased 20 kirjet
        self.andmed["ajalugu"] = self.andmed["ajalugu"][-20:]
        self.salvesta()

    def uuenda_saavutus(self, nimi):
        if not self.andmed["saavutused"].get(nimi, False):
            self.andmed["saavutused"][nimi] = True
            self.salvesta()
            return True
        return False

    def keskmine_skoor(self):
        if self.andmed["mangude_arv"] == 0:
            return 0
        return round(self.andmed["skooride_summa"] / self.andmed["mangude_arv"], 1)


# -------------------------------------------------------
# ABIFUNKTSIOONID
# -------------------------------------------------------
def tekst_tsentris(pind, sisu, font, varv, y_nihutus=0):
    renderdatud = font.render(sisu, True, varv)
    x = LAIUS // 2 - renderdatud.get_width() // 2
    y = KORGUS // 2 + y_nihutus
    pind.blit(renderdatud, (x, y))


def varvi_interpoleerimine(varv1, varv2, suhe):
    """Tagasta kahe RGB värvi vaheline värtus suhte järgi (0.0 ... 1.0)."""
    return tuple(int(v1 + (v2 - v1) * suhe) for v1, v2 in zip(varv1, varv2))


# -------------------------------------------------------
# KLASS: Snake
# -------------------------------------------------------
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = LAIUS // 2
        self.y = KORGUS // 2
        self.suund_x = 0
        self.suund_y = 0
        self.keha = [(self.x, self.y)]
        self.pikkus = 1
        self.buffer = None
        self.alustanud = False

    def muuda_suund(self, uus_dx, uus_dy):
        if uus_dx != 0 and uus_dx == -self.suund_x:
            return
        if uus_dy != 0 and uus_dy == -self.suund_y:
            return
        if uus_dx == self.suund_x and uus_dy == self.suund_y:
            return
        self.buffer = (uus_dx, uus_dy)
        self.alustanud = True

    def liiguta(self):
        if self.buffer is not None:
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

    def joonista(self, pind, teema, aeg_ms):
        pea_varv = teema["mao_pea"]
        saba_varv = teema["mao_keha"]
        keha_pikkus = len(self.keha)

        for i, (bx, by) in enumerate(self.keha):
            on_pea = (i == keha_pikkus - 1)

            if on_pea:
                varv = pea_varv
            else:
                # Saba gradient: mida kaugemal sabast, seda lähemal pea värvile
                suhe = i / max(keha_pikkus - 1, 1)
                varv = varvi_interpoleerimine(saba_varv, pea_varv, suhe)

            # Jõnksuv/wiggle efekt – ainult kehal, mitte peas
            wiggle_x, wiggle_y = 0, 0
            if not on_pea and keha_pikkus > 2:
                wiggle = math.sin((aeg_ms / 150) + i * 0.8) * 1.5
                if abs(self.suund_x) > 0:
                    wiggle_y = wiggle
                else:
                    wiggle_x = wiggle

            joonista_x = bx + 1 + wiggle_x
            joonista_y = by + 1 + wiggle_y
            pygame.draw.rect(pind, varv, (joonista_x, joonista_y, PLOKK - 2, PLOKK - 2))

            if on_pea and self.alustanud:
                self._joonista_silmad(pind, bx, by)

    def _joonista_silmad(self, pind, x, y):
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
# KLASS: Toit
# -------------------------------------------------------
class Toit:
    def __init__(self, tyyp="tavaline"):
        self.tyyp = tyyp
        self.punktid = 1 if tyyp == "tavaline" else 3
        self.kiiruse_kasv = 0.5 if tyyp == "tavaline" else 1.0
        self.x = 0
        self.y = 0
        self.spawn_aeg = 0
        self.elu_iga = None  # None = ei kao kunagi (tavaline toit)

    def spawni(self, keelatud):
        koik = [(x, y) for x in range(0, LAIUS, PLOKK) for y in range(0, KORGUS, PLOKK)]
        vabad = [pos for pos in koik if pos not in keelatud]
        if vabad:
            self.x, self.y = random.choice(vabad)
            self.spawn_aeg = pygame.time.get_ticks()

    def on_aegunud(self):
        if self.elu_iga is None:
            return False
        return pygame.time.get_ticks() - self.spawn_aeg > self.elu_iga

    def joonista(self, pind, teema):
        aeg = pygame.time.get_ticks()
        pulss = math.sin(aeg / 300) * 2
        suurus = int(PLOKK - 4 + pulss)
        nihutus = (PLOKK - suurus) // 2

        # Toidu "helendus" – suurem läbipaistev ring all
        glow_suurus = suurus + 8
        glow_nihutus = (PLOKK - glow_suurus) // 2
        glow = pygame.Surface((glow_suurus, glow_suurus), pygame.SRCALPHA)
        glow_varv = (*teema["toit"][:3], 60) if self.tyyp == "tavaline" else (*teema["boonus"][:3], 80)
        pygame.draw.ellipse(glow, glow_varv, (0, 0, glow_suurus, glow_suurus))
        pind.blit(glow, (self.x + glow_nihutus, self.y + glow_nihutus))

        # Toidu ruut
        varv = teema["toit"] if self.tyyp == "tavaline" else teema["boonus"]
        pygame.draw.rect(pind, varv, (self.x + nihutus, self.y + nihutus, suurus, suurus), border_radius=3)

        if self.tyyp == "boonus":
            heledus = int(abs(math.sin(aeg / 200)) * 90)
            kiht = pygame.Surface((suurus, suurus), pygame.SRCALPHA)
            kiht.fill((255, 255, 255, heledus))
            pind.blit(kiht, (self.x + nihutus, self.y + nihutus))


# -------------------------------------------------------
# KLASS: Takistus
# -------------------------------------------------------
class Takistus:
    def __init__(self):
        self.x = 0
        self.y = 0

    def spawni(self, keelatud):
        koik = [(x, y) for x in range(0, LAIUS, PLOKK) for y in range(0, KORGUS, PLOKK)]
        vabad = [pos for pos in koik if pos not in keelatud]
        if vabad:
            self.x, self.y = random.choice(vabad)

    def joonista(self, pind, teema):
        pygame.draw.rect(pind, teema["takistus"], (self.x + 1, self.y + 1, PLOKK - 2, PLOKK - 2))
        # Väike X-muster peale
        pygame.draw.line(pind, TUME_HALL, (self.x + 4, self.y + 4), (self.x + PLOKK - 4, self.y + PLOKK - 4), 2)
        pygame.draw.line(pind, TUME_HALL, (self.x + PLOKK - 4, self.y + 4), (self.x + 4, self.y + PLOKK - 4), 2)


# -------------------------------------------------------
# KLASS: Mang (peamine mänguhaldur)
# -------------------------------------------------------
class Mang:
    def __init__(self):
        self.heli_sees = True
        self.ruudustik_sees = True
        self.raskus = "Keskmine"
        self.teema_nimi = "Klassikaline"
        self.algus_reziim = "oota"  # "oota" või "kohe"
        self.helitugevus = 5  # 0–10

        self.soomis_heli = None
        self.gameover_heli = None
        self._laadi_helid()

        self.ruudustiku_pind = self._loo_ruudustiku_pind()
        self.statistika = Statistika()

        self.madu = Snake()
        self.toit = Toit("tavaline")
        self.boonus = Toit("boonus")
        self.boonus.elu_iga = 5000  # 5 sekundit
        self.takistused = []

        self.skoor = 0
        self.tase = 1
        self.rekord = self.statistika.andmed["parim_skoor"]
        self.kiirus = RASKUSED[self.raskus][0]
        self.paus = False
        self.saavutuste_teated = []  # (tekst, aeg_ms)

    def _laadi_helid(self):
        try:
            pygame.mixer.music.load("music/taust.mp3")
            pygame.mixer.music.play(-1)
            self.soomis_heli = pygame.mixer.Sound("music/eat.wav")
            self.gameover_heli = pygame.mixer.Sound("music/gameover.wav")
        except Exception as e:
            print(f"Heli laadimine ebaõnnestus: {e}")

    def _uuenda_helitugevus(self):
        vol = self.helitugevus / 10.0
        pygame.mixer.music.set_volume(vol * 0.5)
        if self.soomis_heli:
            self.soomis_heli.set_volume(vol)
        if self.gameover_heli:
            self.gameover_heli.set_volume(vol)

    def _helista(self, heli):
        if heli is not None and self.heli_sees:
            heli.play()

    def _loo_ruudustiku_pind(self):
        pind = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
        joone_varv = (*TEEMAD[self.teema_nimi]["ruudustik"][:3], 70)
        for x in range(0, LAIUS, PLOKK):
            pygame.draw.line(pind, joone_varv, (x, 0), (x, KORGUS))
        for y in range(0, KORGUS, PLOKK):
            pygame.draw.line(pind, joone_varv, (0, y), (LAIUS, y))
        return pind

    def _taasta_ruudustik(self):
        self.ruudustiku_pind = self._loo_ruudustiku_pind()

    @property
    def teema(self):
        return TEEMAD[self.teema_nimi]

    def reset(self):
        alg, kasv, maks = RASKUSED[self.raskus]
        self.kiirus = alg
        self.kiiruse_kasv = kasv
        self.kiiruse_maks = maks
        self.skoor = 0
        self.tase = 1
        self.paus = False
        self.takistused = []
        self.saavutuste_teated = []
        self.madu.reset()
        self.toit.spawni(self.madu.keha)
        self.boonus.spawni(self.madu.keha + [(self.toit.x, self.toit.y)])
        self._uuenda_helitugevus()

    def _kontrolli_tase(self):
        uus_tase = (self.skoor // 10) + 1
        if uus_tase > self.tase:
            self.tase = uus_tase
            # Lisa uusi takistusi
            for _ in range(2):
                t = Takistus()
                keelatud = set(self).madu.keha + [(self.toit.x, self.toit.y), (self.boonus.x, self.boonus.y)]
                for tak in self.takistused:
                    keelatud.add((tak.x, tak.y))
                t.spawni(keelatud)
                self.takistused.append(t)

    def _kontrolli_saavutused(self, toit_tyyp):
        uued = []
        if self.skoor >= 1:
            if self.statistika.uuenda_saavutus("Esimene suutäis"):
                uued.append("Esimene suutäis!")
        if self.skoor >= 10:
            if self.statistika.uuenda_saavutus("10 punkti klubis"):
                uued.append("10 punkti klubis!")
        if self.tase >= 3:
            if self.statistika.uuenda_saavutus("Ellujääja"):
                uued.append("Ellujääja!")
        if self.kiirus >= self.kiiruse_maks * 0.9:
            if self.statistika.uuenda_saavutus("Kiirusemeister"):
                uued.append("Kiirusemeister!")
        if toit_tyyp == "boonus":
            if self.statistika.uuenda_saavutus("Boonusekütt"):
                uued.append("Boonusekütt!")
        if self.skoor >= 50:
            if self.statistika.uuenda_saavutus("Suurmeister"):
                uued.append("Suurmeister!")

        aeg = pygame.time.get_ticks()
        for u in uued:
            self.saavutuste_teated.append((u, aeg + 3000))

    def _joonista_saavutused(self):
        aeg = pygame.time.get_ticks()
        aktiivsed = []
        for tekst, lopp in self.saavutuste_teated:
            if aeg < lopp:
                aktiivsed.append((tekst, lopp - aeg))
        self.saavutuste_teated = [(t, l) for t, l in self.saavutuste_teated if aeg < l]

        for i, (tekst, jarel) in enumerate(aktivsed):
            alpha = min(255, int((jarel / 3000) * 255))
            pind = font_tavaline.render(tekst, True, KULDNE)
            kiht = pygame.Surface(pind.get_size(), pygame.SRCALPHA)
            kiht.blit(pind, (0, 0))
            kiht.set_alpha(alpha)
            y_pos = 70 + i * 30
            ekraan.blit(kiht, (10, y_pos))

    def _joonista_hud(self):
        s_pind = font_tavaline.render(f"Skoor: {self.skoor}", True, VALGE)
        r_pind = font_tavaline.render(f"Rekord: {self.rekord}", True, KULDNE)
        t_pind = font_vike.render(f"Tase: {self.tase}", True, HALL)
        d_pind = font_vike.render(self.raskus, True, HALL)

        ekraan.blit(s_pind, (10, 10))
        ekraan.blit(r_pind, (10, 38))
        ekraan.blit(t_pind, (10, 66))
        ekraan.blit(d_pind, (LAIUS - d_pind.get_width() - 10, 10))

    def _joonista_valja(self):
        ekraan.fill(self.teema["taust"])
        if self.ruudustik_sees:
            ekraan.blit(self.ruudustiku_pind, (0, 0))

        for t in self.takistused:
            t.joonista(ekraan, self.teema)

        self.toit.joonista(ekraan, self.teema)
        self.boonus.joonista(ekraan, self.teema)
        self.madu.joonista(ekraan, self.teema, pygame.time.get_ticks())
        self._joonista_hud()
        self._joonista_saavutused()

    def _paus_kate(self):
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
        kate.fill((0, 0, 0, 150))
        ekraan.blit(kate, (0, 0))
        tekst_tsentris(ekraan, "PAUS", font_suur, VALGE, -25)
        tekst_tsentris(ekraan, "P – jätka mängu", font_tavaline, HALL, 25)

    def _kontrolli_toit(self):
        px, py = self.madu.x, self.madu.y

        if px == self.toit.x and py == self.toit.y:
            self._soo(self.toit)
            self.toit.spawni(self.madu.keha + [(self.boonus.x, self.boonus.y)] + [(t.x, t.y) for t in self.takistused])

        if px == self.boonus.x and py == self.boonus.y:
            self._soo(self.boonus)
            self.boonus.spawni(self.madu.keha + [(self.toit.x, self.toit.y)] + [(t.x, t.y) for t in self.takistused])

        # Kontrolli boonuse aegumist
        if self.boonus.on_aegunud():
            self.boonus.spawni(self.madu.keha + [(self.toit.x, self.toit.y)] + [(t.x, t.y) for t in self.takistused])

    def _soo(self, toit_obj):
        self._helista(self.soomis_heli)
        self.madu.pikkus += toit_obj.punktid
        self.skoor += toit_obj.punktid
        self.kiirus = min(self.kiirus + self.kiiruse_kasv, self.kiiruse_maks)
        self._kontrolli_tase()
        self._kontrolli_saavutused(toit_obj.tyyp)

    def _kontrolli_takistused(self):
        for t in self.takistused:
            if self.madu.x == t.x and self.madu.y == t.y:
                return False
        return True

    # ---- Ekraanid ----

    def algus_meniu(self):
        valikud = ["Alusta mängu", "Seaded", "Statistika", "Credits", "Välju"]
        valitud = 0

        while True:
            ekraan.fill(MENUU_TAUST)
            tekst_tsentris(ekraan, "SNAKE GAME", font_suur, KULDNE, -150)
            tekst_tsentris(ekraan, "Kristjan – IS25  |  v2.0", font_vike, HALL, -100)

            for i, valik in enumerate(valikud):
                varv = VALGE if i == valitud else TUME_HALL
                tekst_tsentris(ekraan, valik, font_tavaline, varv, -30 + i * 50)

            tekst_tsentris(ekraan, "↑ ↓ – vali   ENTER – kinnita", font_vike, HALL, 150)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        valitud = (valitud - 1) % len(valikud)
                    elif event.key == pygame.K_DOWN:
                        valitud = (valitud + 1) % len(valikud)
                    elif event.key == pygame.K_RETURN:
                        valik = valikud[valitud]
                        if valik == "Alusta mängu":
                            return "alusta"
                        elif valik == "Seaded":
                            return "seaded"
                        elif valik == "Statistika":
                            return "statistika"
                        elif valik == "Credits":
                            return "credits"
                        elif valik == "Välju":
                            return None
            kell.tick(30)

    def seadete_ekraan(self):
        while True:
            ekraan.fill(MENUU_TAUST)
            tekst_tsentris(ekraan, "SEADED", font_suur, KULDNE, -180)

            heli_tekst = f"Heli:       {'SEES  ✓' if self.heli_sees else 'VÄLJAS ✗'}"
            heli_varv = (34, 180, 80) if self.heli_sees else (220, 60, 60)
            tekst_tsentris(ekraan, heli_tekst, font_tavaline, heli_varv, -110)

            grid_tekst = f"Ruudustik: {'SEES  ✓' if self.ruudustik_sees else 'VÄLJAS ✗'}"
            grid_varv = (34, 180, 80) if self.ruudustik_sees else (220, 60, 60)
            tekst_tsentris(ekraan, grid_tekst, font_tavaline, grid_varv, -60)

            rask_tekst = f"Raskus:    {self.raskus}"
            tekst_tsentris(ekraan, rask_tekst, font_tavaline, VALGE, -10)

            teema_tekst = f"Teema:     {self.teema_nimi}"
            tekst_tsentris(ekraan, teema_tekst, font_tavaline, VALGE, 40)

            vol_tekst = f"Helitugevus: {self.helitugevus}"
            tekst_tsentris(ekraan, vol_tekst, font_tavaline, VALGE, 90)

            algus_tekst = f"Algus:     {'Kohe' if self.algus_reziim == 'kohe' else 'Oota klahvi'}"
            tekst_tsentris(ekraan, algus_tekst, font_tavaline, VALGE, 140)

            tekst_tsentris(ekraan, "1 – Heli   2 – Ruudustik   3 – Raskus   4 – Teema", font_vike, HALL, 190)
            tekst_tsentris(ekraan, "5 – Vol –   6 – Vol +   7 – Algus   ESC – tagasi", font_vike, HALL, 215)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
                    elif event.key == pygame.K_1:
                        self.heli_sees = not self.heli_sees
                        try:
                            if self.heli_sees:
                                pygame.mixer.music.unpause()
                            else:
                                pygame.mixer.music.pause()
                        except Exception:
                            pass
                    elif event.key == pygame.K_2:
                        self.ruudustik_sees = not self.ruudustik_sees
                    elif event.key == pygame.K_3:
                        praegune = RASKUSED_JARJESTUS.index(self.raskus)
                        self.raskus = RASKUSED_JARJESTUS[(praegune + 1) % len(RASKUSED_JARJESTUS)]
                    elif event.key == pygame.K_4:
                        teemad = list(TEEMAD.keys())
                        idx = teemad.index(self.teema_nimi)
                        self.teema_nimi = teemad[(idx + 1) % len(teemad)]
                        self._taasta_ruudustik()
                    elif event.key == pygame.K_5:
                        self.helitugevus = max(0, self.helitugevus - 1)
                        self._uuenda_helitugevus()
                    elif event.key == pygame.K_6:
                        self.helitugevus = min(10, self.helitugevus + 1)
                        self._uuenda_helitugevus()
                    elif event.key == pygame.K_7:
                        self.algus_reziim = "kohe" if self.algus_reziim == "oota" else "oota"
            kell.tick(30)

    def statistika_ekraan(self):
        while True:
            ekraan.fill(MENUU_TAUST)
            tekst_tsentris(ekraan, "STATISTIKA", font_suur, KULDNE, -200)

            andmed = self.statistika.andmed
            read = [
                f"Mänge mängitud: {andmed['mangude_arv']}",
                f"Parim skoor: {andmed['parim_skoor']}",
                f"Parim tase: {andmed['parim_tase']}",
                f"Keskmine skoor: {self.statistika.keskmine_skoor()}",
                "",
                "Saavutused:",
            ]
            for nimi, olek in andmed["saavutused"].items():
                mark = "✓" if olek else "○"
                read.append(f"  {mark} {nimi}")

            for i, rida in enumerate(read):
                tekst_tsentris(ekraan, rida, font_vike, VALGE if i < 5 else HALL, -130 + i * 25)

            tekst_tsentris(ekraan, "ESC – tagasi", font_vike, HALL, 220)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
            kell.tick(30)

    def credits_ekraan(self):
        while True:
            ekraan.fill(MENUU_TAUST)
            tekst_tsentris(ekraan, "CREDITS", font_suur, KULDNE, -150)
            tekst_tsentris(ekraan, "Autor: Kristjan", font_tavaline, VALGE, -70)
            tekst_tsentris(ekraan, "Klass: IS25", font_tavaline, VALGE, -30)
            tekst_tsentris(ekraan, "Aasta: 2025/2026", font_tavaline, VALGE, 10)
            tekst_tsentris(ekraan, "Täname, et mängisid!", font_vike, HALL, 70)
            tekst_tsentris(ekraan, "(Easter egg: madu on tegelikult vegan)", font_vike, TUME_HALL, 100)
            tekst_tsentris(ekraan, "ESC – tagasi", font_vike, HALL, 200)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
            kell.tick(30)

    def gameover_ekraan(self):
        # Salvesta statistika
        self.statistika.lisa_mang(self.skoor, self.tase)
        if self.skoor > self.rekord:
            self.rekord = self.skoor

        for alpha in range(0, 201, 7):
            kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
            kate.fill((PUNANE[0], PUNANE[1], PUNANE[2], alpha))
            ekraan.blit(kate, (0, 0))
            pygame.display.flip()
            kell.tick(60)

        while True:
            kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
            kate.fill((*PUNANE, 210))
            ekraan.blit(kate, (0, 0))

            tekst_tsentris(ekraan, "MÄNG LÄBI!", font_suur, VALGE, -90)
            tekst_tsentris(ekraan, f"Skoor:  {self.skoor}", font_tavaline, VALGE, -30)
            tekst_tsentris(ekraan, f"Tase:   {self.tase}", font_tavaline, VALGE, 0)
            tekst_tsentris(ekraan, f"Rekord: {self.rekord}", font_tavaline, KULDNE, 30)
            tekst_tsentris(ekraan, "ENTER – mängi uuesti", font_tavaline, VALGE, 85)
            tekst_tsentris(ekraan, "ESC – peamenüü", font_tavaline, HALL, 120)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return True
                    elif event.key == pygame.K_ESCAPE:
                        return False
            kell.tick(30)

    # ---- Mängutsükkel ----

    def jooksu(self):
        self.reset()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and self.madu.alustanud:
                        self.paus = not self.paus

                    if not self.paus:
                        if event.key == pygame.K_LEFT:
                            self.madu.muuda_suund(-PLOKK, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.madu.muuda_suund(PLOKK, 0)
                        elif event.key == pygame.K_UP:
                            self.madu.muuda_suund(0, -PLOKK)
                        elif event.key == pygame.K_DOWN:
                            self.madu.muuda_suund(0, PLOKK)

            # Kui ootame esimest klahvi ja režiim on "oota"
            peab_ootama = (not self.madu.alustanud and self.algus_reziim == "oota")

            if self.paus or peab_ootama:
                self._joonista_valja()
                if self.paus:
                    self._paus_kate()
                else:
                    tekst_tsentris(ekraan, "Vajuta nooleklahvi alustamiseks", font_vike, HALL, 215)
                pygame.display.flip()
                kell.tick(30)
                continue

            elus = self.madu.liiguta()
            if not elus or not self._kontrolli_takistused():
                self._helista(self.gameover_heli)
                self.rekord = max(self.skoor, self.rekord)
                self._joonista_valja()
                pygame.display.flip()
                return self.gameover_ekraan()

            self._kontrolli_toit()
            self._joonista_valja()
            pygame.display.flip()
            kell.tick(int(self.kiirus))


# -------------------------------------------------------
# PEAPROGRAMM
# -------------------------------------------------------
def peaprogramm():
    mang = Mang()

    while True:
        tulemus = mang.algus_meniu()

        if tulemus is None:
            break
        elif tulemus == "seaded":
            if mang.seadete_ekraan() is None:
                break
        elif tulemus == "statistika":
            if mang.statistika_ekraan() is None:
                break
        elif tulemus == "credits":
            if mang.credits_ekraan() is None:
                break
        elif tulemus == "alusta":
            jatka = True
            while jatka:
                jatka = mang.jooksu()

    pygame.quit()


if __name__ == "__main__":
    peaprogramm()
