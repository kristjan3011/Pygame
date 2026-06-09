"""
Snake Game
Autor:   Kristjan – IS25
Versioon: 2.8
Kirjeldus: Uuendatud Snake mäng PyGame'iga.
           Parandatud PyCharmi hoiatused: atribuudid __init__-s,
           selgem süntaks, staatilised meetodid, type hints,
           refaktoreeritud korduv kood, kitsendatud except-blokid.
           v2.3: Game over ekraan järgib aktiivset teemat;
                 fullscreen/akna režiim seadetes (F-klahv).
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
LAIUS: int = 1280
KORGUS: int = 720
PLOKK: int = 20

# Värviteemad (saab menüüst vahetada)
TEEMAD: dict[str, dict[str, tuple[int, int, int]]] = {
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
VALGE: tuple[int, int, int] = (255, 255, 255)
MUST: tuple[int, int, int] = (0, 0, 0)
PUNANE: tuple[int, int, int] = (180, 20, 20)
HALL: tuple[int, int, int] = (180, 180, 180)
TUME_HALL: tuple[int, int, int] = (90, 90, 90)
MENUU_TAUST: tuple[int, int, int] = (15, 45, 95)
KULDNE: tuple[int, int, int] = (255, 215, 0)

# Raskusastmed (algkiirus, kiiruse kasv, max kiirus)
RASKUSED: dict[str, tuple[float, float, float]] = {
    "Lihtne":   (6,  0.3, 12),
    "Keskmine": (10, 0.5, 18),
    "Raske":    (15, 0.8, 25),
}
RASKUSED_JARJESTUS: list[str] = list(RASKUSED.keys())

# Fondid
font_suur     = pygame.font.SysFont("Arial", 40)
font_tavaline = pygame.font.SysFont("Arial", 25)
font_vike     = pygame.font.SysFont("Arial", 18)

# Aken ja kell
_fullscreen: bool = False
ekraan: pygame.Surface = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Snake Game – Kristjan IS25 v2.3")
kell = pygame.time.Clock()


def toggle_fullscreen() -> None:
    """Lülita täisekraani ja aknarežiimi vahel."""
    global ekraan, _fullscreen
    _fullscreen = not _fullscreen
    if _fullscreen:
        ekraan = pygame.display.set_mode((LAIUS, KORGUS), pygame.FULLSCREEN)
    else:
        ekraan = pygame.display.set_mode((LAIUS, KORGUS))


# -------------------------------------------------------
# ABIFUNKTSIOONID
# -------------------------------------------------------
def tekst_tsentris(pind: pygame.Surface, sisu: str, font: pygame.font.Font,
                   varv: tuple[int, int, int], y_nihutus: int = 0) -> None:
    """Joonista tekst horisontaalselt keskele."""
    renderdatud = font.render(sisu, True, varv)
    x = LAIUS // 2 - renderdatud.get_width() // 2
    y = KORGUS // 2 + y_nihutus
    pind.blit(renderdatud, (x, y))


def varvi_interpoleerimine(varv1: tuple[int, int, int],
                           varv2: tuple[int, int, int],
                           suhe: float) -> tuple[int, int, int]:
    """Tagasta kahe RGB värvi vaheline väärtus suhte järgi (0.0 ... 1.0)."""
    return tuple(int(v1 + (v2 - v1) * suhe) for v1, v2 in zip(varv1, varv2))  # type: ignore[return-value]


def juhuslik_koht(keelatud: set[tuple[int, int]] | list[tuple[int, int]]) -> tuple[int, int] | None:
    """Leia juhuslik vaba koht ruudustikul."""
    koik = [(x, y) for x in range(0, LAIUS, PLOKK) for y in range(0, KORGUS, PLOKK)]
    vabad = [pos for pos in koik if pos not in keelatud]
    if vabad:
        return random.choice(vabad)
    return None


def fade_in_kate(varv_rgb: tuple[int, int, int], max_alpha: int = 200,
                 samm: int = 7, fps: int = 60) -> None:
    """Üldine fade-in efekt – täidab ekraani läbipaistvas kihis."""
    for alpha in range(0, max_alpha + 1, samm):
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
        kate.fill((*varv_rgb, alpha))
        ekraan.blit(kate, (0, 0))
        pygame.display.flip()
        kell.tick(fps)


def loo_ruudustiku_pind(teema_nimi: str) -> pygame.Surface:
    """Loo eelrenderdatud ruudustiku pind antud teema jaoks."""
    pind = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
    joone_varv = (*TEEMAD[teema_nimi]["ruudustik"][:3], 70)
    for x in range(0, LAIUS, PLOKK):
        pygame.draw.line(pind, joone_varv, (x, 0), (x, KORGUS))
    for y in range(0, KORGUS, PLOKK):
        pygame.draw.line(pind, joone_varv, (0, y), (LAIUS, y))
    return pind


def koosta_keelatud_hulk(madu_keha: list[tuple[int, int]],
                         lisad: list[tuple[int, int]] | None = None) -> set[tuple[int, int]]:
    """Koosta keelatud positsioonide hulk mao kehast ja lisapositsioonidest."""
    keelatud: set[tuple[int, int]] = set(madu_keha)
    if lisad:
        keelatud.update(lisad)
    return keelatud


# -------------------------------------------------------
# STATISTIKA HALDUS (salvestatakse JSON-faili)
# -------------------------------------------------------
class Statistika:
    def __init__(self, fail: str = "snake_stats.json") -> None:
        self.fail: str = os.path.join(os.path.dirname(__file__), fail)
        self.andmed: dict = self.lae()

    @staticmethod
    def _vaikimisi() -> dict:
        """Tagasta täielik vaikimisi andmestruktuur (statistika + seaded)."""
        return {
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
            },
            "seaded": {
                "heli_sees": True,
                "ruudustik_sees": True,
                "raskus": "Keskmine",
                "teema_nimi": "Klassikaline",
                "algus_reziim": "oota",
                "helitugevus": 5,
            },
        }

    def lae(self) -> dict:
        vaikimisi = self._vaikimisi()
        try:
            with open(self.fail, "r", encoding="utf-8") as f:
                andmed: dict = json.load(f)
            # täienda puuduvad võtmed (ühilduvus vanema salvestusega)
            for key, val in vaikimisi.items():
                andmed.setdefault(key, val)
            for skey, sval in vaikimisi["seaded"].items():
                andmed["seaded"].setdefault(skey, sval)
            return andmed
        except (FileNotFoundError, json.JSONDecodeError):
            return vaikimisi

    # ---- Seadete salvestus / laadimine ----

    def lae_seaded(self) -> dict:
        """Tagasta salvestatud seadete sõnastik."""
        return dict(self.andmed.get("seaded", self._vaikimisi()["seaded"]))

    def salvesta_seaded(self, seaded: dict) -> None:
        """Salvesta seadete sõnastik faili."""
        self.andmed["seaded"] = seaded
        self.salvesta()

    def salvesta(self) -> None:
        with open(self.fail, "w", encoding="utf-8") as f:
            json.dump(self.andmed, f, ensure_ascii=False, indent=2)

    def lisa_mang(self, skoor: int, tase: int) -> None:
        self.andmed["mangude_arv"] += 1
        self.andmed["skooride_summa"] += skoor
        self.andmed["parim_skoor"] = max(self.andmed["parim_skoor"], skoor)
        self.andmed["parim_tase"] = max(self.andmed["parim_tase"], tase)
        self.andmed["ajalugu"].append({
            "aeg": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "skoor": skoor,
            "tase": tase,
        })
        self.andmed["ajalugu"] = self.andmed["ajalugu"][-20:]
        self.salvesta()

    def uuenda_saavutus(self, nimi: str) -> bool:
        if not self.andmed["saavutused"].get(nimi, False):
            self.andmed["saavutused"][nimi] = True
            self.salvesta()
            return True
        return False

    def keskmine_skoor(self) -> float:
        if self.andmed["mangude_arv"] == 0:
            return 0.0
        return round(self.andmed["skooride_summa"] / self.andmed["mangude_arv"], 1)


# -------------------------------------------------------
# KLASS: Snake
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
        """Lähtesta kõik mao atribuudid mängu alguseks."""
        self.x = LAIUS // 2
        self.y = KORGUS // 2
        self.suund_x = 0
        self.suund_y = 0
        self.keha = [(self.x, self.y)]
        self.pikkus = 1
        self.buffer = None
        self.alustanud = False

    def muuda_suund(self, uus_dx: int, uus_dy: int) -> None:
        """Bufferdab järgmise suunamuutuse. Tagasikeeramine blokeeritakse."""
        if uus_dx != 0 and uus_dx == -self.suund_x:
            return
        if uus_dy != 0 and uus_dy == -self.suund_y:
            return
        if uus_dx == self.suund_x and uus_dy == self.suund_y:
            return
        self.buffer = (uus_dx, uus_dy)
        self.alustanud = True

    def liiguta(self) -> bool:
        """Uuenda mao positsiooni. Tagasta False kui surm."""
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

    def joonista(self, pind: pygame.Surface, teema: dict, aeg_ms: int) -> None:
        """Joonista madu koos gradienti ja wiggle efektiga."""
        pea_varv = teema["mao_pea"]
        saba_varv = teema["mao_keha"]
        keha_pikkus = len(self.keha)

        for i, (bx, by) in enumerate(self.keha):
            on_pea = (i == keha_pikkus - 1)

            if on_pea:
                varv = pea_varv
            else:
                suhe = i / max(keha_pikkus - 1, 1)
                varv = varvi_interpoleerimine(saba_varv, pea_varv, suhe)

            joonista_x: float = float(bx) + 1.0
            joonista_y: float = float(by) + 1.0

            if not on_pea and keha_pikkus > 2:
                wiggle = math.sin((aeg_ms / 150) + i * 0.8) * 1.5
                if abs(self.suund_x) > 0:
                    joonista_y += wiggle
                else:
                    joonista_x += wiggle

            pygame.draw.rect(pind, varv,
                             (joonista_x, joonista_y, PLOKK - 2, PLOKK - 2))

            if on_pea and self.alustanud:
                self._joonista_silmad(pind, bx, by)

    def _joonista_silmad(self, pind: pygame.Surface, x: int, y: int) -> None:
        """Joonista madu silmad liikumissuunale vastavalt."""
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
    def __init__(self, tyyp: str = "tavaline") -> None:
        self.tyyp: str = tyyp
        self.punktid: int = 1 if tyyp == "tavaline" else 3
        self.kiiruse_kasv: float = 0.5 if tyyp == "tavaline" else 1.0
        self.x: int = 0
        self.y: int = 0
        self.spawn_aeg: int = 0
        self.elu_iga: int | None = None

    def spawni(self, keelatud: set[tuple[int, int]] | list[tuple[int, int]]) -> None:
        """Aseta toit juhuslikule vabale positsioonile."""
        koht = juhuslik_koht(keelatud)
        if koht is None:
            return
        self.x, self.y = koht
        self.spawn_aeg = pygame.time.get_ticks()

    def on_aegunud(self) -> bool:
        """Kontrolli, kas ajaline boonus on aegunud."""
        if self.elu_iga is None:
            return False
        return pygame.time.get_ticks() - self.spawn_aeg > self.elu_iga

    def joonista(self, pind: pygame.Surface, teema: dict) -> None:
        """Joonista toit koos pulseerimise ja helendusega."""
        aeg = pygame.time.get_ticks()
        pulss = math.sin(aeg / 300) * 2
        suurus = int(PLOKK - 4 + pulss)
        nihutus = (PLOKK - suurus) // 2

        glow_suurus = suurus + 8
        glow_nihutus = (PLOKK - glow_suurus) // 2
        glow = pygame.Surface((glow_suurus, glow_suurus), pygame.SRCALPHA)
        glow_varv = (*teema["toit"][:3], 60) if self.tyyp == "tavaline" else (*teema["boonus"][:3], 80)
        pygame.draw.ellipse(glow, glow_varv, (0, 0, glow_suurus, glow_suurus))
        pind.blit(glow, (self.x + glow_nihutus, self.y + glow_nihutus))

        varv = teema["toit"] if self.tyyp == "tavaline" else teema["boonus"]
        pygame.draw.rect(pind, varv,
                         (self.x + nihutus, self.y + nihutus, suurus, suurus),
                         border_radius=3)

        if self.tyyp == "boonus":
            heledus = int(abs(math.sin(aeg / 200)) * 90)
            kiht = pygame.Surface((suurus, suurus), pygame.SRCALPHA)
            kiht.fill((255, 255, 255, heledus))
            pind.blit(kiht, (self.x + nihutus, self.y + nihutus))


# -------------------------------------------------------
# KLASS: Takistus
# -------------------------------------------------------
class Takistus:
    def __init__(self) -> None:
        self.x: int = 0
        self.y: int = 0

    def spawni(self, keelatud: set[tuple[int, int]] | list[tuple[int, int]]) -> None:
        """Aseta takistus juhuslikule vabale positsioonile."""
        koht = juhuslik_koht(keelatud)
        if koht is None:
            return
        self.x, self.y = koht

    def joonista(self, pind: pygame.Surface, teema: dict) -> None:
        """Joonista takistus koos X-mustriga."""
        pygame.draw.rect(pind, teema["takistus"],
                         (self.x + 1, self.y + 1, PLOKK - 2, PLOKK - 2))
        pygame.draw.line(pind, TUME_HALL,
                         (self.x + 4, self.y + 4),
                         (self.x + PLOKK - 4, self.y + PLOKK - 4), 2)
        pygame.draw.line(pind, TUME_HALL,
                         (self.x + PLOKK - 4, self.y + 4),
                         (self.x + 4, self.y + PLOKK - 4), 2)


# -------------------------------------------------------
# KLASS: Mang (peamine mänguhaldur)
# -------------------------------------------------------
class Mang:
    def __init__(self) -> None:
        # Statistika ja seadete laadimine (seaded loetakse failist)
        self.statistika: Statistika = Statistika()
        _s = self.statistika.lae_seaded()

        # Seaded (failist laetud või vaikimisi)
        self.heli_sees: bool = bool(_s.get("heli_sees", True))
        self.ruudustik_sees: bool = bool(_s.get("ruudustik_sees", True))
        self.raskus: str = str(_s.get("raskus", "Keskmine"))
        self.teema_nimi: str = str(_s.get("teema_nimi", "Klassikaline"))
        self.algus_reziim: str = str(_s.get("algus_reziim", "oota"))
        self.helitugevus: int = int(_s.get("helitugevus", 5))

        # Helifailid
        self.soomis_heli: pygame.mixer.Sound | None = None
        self.gameover_heli: pygame.mixer.Sound | None = None
        self._laadi_helid()

        # Visuaal
        self.ruudustiku_pind: pygame.Surface = loo_ruudustiku_pind(self.teema_nimi)

        # Mänguobjektid
        self.madu: Snake = Snake()
        self.toit: Toit = Toit("tavaline")
        self.boonus: Toit = Toit("boonus")
        self.boonus.elu_iga = 5000
        self.takistused: list[Takistus] = []

        # Mängu olekumuutujad
        self.skoor: int = 0
        self.tase: int = 1
        self.rekord: int = self.statistika.andmed["parim_skoor"]
        self.kiirus: float = float(RASKUSED[self.raskus][0])
        self.kiiruse_kasv: float = float(RASKUSED[self.raskus][1])
        self.kiiruse_maks: float = float(RASKUSED[self.raskus][2])
        self.paus: bool = False
        self.saavutuste_teated: list[tuple[str, int]] = []

    # ---- Sisemised abimeetodid ----

    def _laadi_helid(self) -> None:
        """Lae helifailid; kui ebaõnnestub, jätka vaikivalt."""
        try:
            pygame.mixer.music.load("music/soundtrack.mp3")
            pygame.mixer.music.play(-1)
            self.soomis_heli = pygame.mixer.Sound("music/apple-crunch.mp3")
            self.gameover_heli = pygame.mixer.Sound("music/gameover.mp3")
        except (FileNotFoundError, pygame.error) as e:
            print(f"Heli laadimine ebaõnnestus: {e}")

    def _uuenda_helitugevus(self) -> None:
        vol = self.helitugevus / 10.0
        try:
            pygame.mixer.music.set_volume(vol * 0.5)
        except pygame.error:
            pass
        if self.soomis_heli:
            self.soomis_heli.set_volume(vol)
        if self.gameover_heli:
            self.gameover_heli.set_volume(vol)

    def _taasta_ruudustik(self) -> None:
        self.ruudustiku_pind = loo_ruudustiku_pind(self.teema_nimi)

    @property
    def teema(self) -> dict:
        return TEEMAD[self.teema_nimi]

    def _helista(self, heli: pygame.mixer.Sound | None) -> None:
        if heli is not None and self.heli_sees:
            heli.play()

    def _salvesta_seaded(self) -> None:
        """Kirjuta aktiivsed seaded JSON-faili."""
        self.statistika.salvesta_seaded({
            "heli_sees":      self.heli_sees,
            "ruudustik_sees": self.ruudustik_sees,
            "raskus":         self.raskus,
            "teema_nimi":     self.teema_nimi,
            "algus_reziim":   self.algus_reziim,
            "helitugevus":    self.helitugevus,
        })

    # ---- Mängu lähtestamine ----

    def reset(self) -> None:
        """Lähtesta mäng uue vooru alguseks."""
        alg, kasv, maks = RASKUSED[self.raskus]
        self.kiirus = float(alg)
        self.kiiruse_kasv = float(kasv)
        self.kiiruse_maks = float(maks)
        self.skoor = 0
        self.tase = 1
        self.paus = False
        self.takistused = []
        self.saavutuste_teated = []
        self.madu.reset()

        keelatud_alg = koosta_keelatud_hulk(self.madu.keha)
        self.toit.spawni(keelatud_alg)
        keelatud_alg.add((self.toit.x, self.toit.y))
        self.boonus.spawni(keelatud_alg)
        self._uuenda_helitugevus()

    # ---- Takistuste, toidu ja boonuse haldus ----

    def _spawni_takistus(self) -> None:
        """Spawni üks uus takistus vabale kohale."""
        t = Takistus()
        keelatud = koosta_keelatud_hulk(
            self.madu.keha,
            [(self.toit.x, self.toit.y), (self.boonus.x, self.boonus.y)]
            + [(tak.x, tak.y) for tak in self.takistused],
        )
        t.spawni(keelatud)
        self.takistused.append(t)

    def _spawni_toit(self) -> None:
        """Respawni tavaline toit."""
        keelatud = koosta_keelatud_hulk(
            self.madu.keha,
            [(self.boonus.x, self.boonus.y)]
            + [(tak.x, tak.y) for tak in self.takistused],
        )
        self.toit.spawni(keelatud)

    def _spawni_boonus(self) -> None:
        """Respawni boonustoit."""
        keelatud = koosta_keelatud_hulk(
            self.madu.keha,
            [(self.toit.x, self.toit.y)]
            + [(tak.x, tak.y) for tak in self.takistused],
        )
        self.boonus.spawni(keelatud)

    # ---- Mängu loogika ----

    def _kontrolli_tase(self) -> None:
        uus_tase = (self.skoor // 10) + 1
        if uus_tase > self.tase:
            self.tase = uus_tase
            self._spawni_takistus()
            self._spawni_takistus()

    def _kontrolli_saavutused(self, toit_tyyp: str) -> None:
        uued: list[str] = []
        kontrollid: list[tuple[bool, str]] = [
            (self.skoor >= 1,                         "Esimene suutäis"),
            (self.skoor >= 10,                        "10 punkti klubis"),
            (self.tase >= 3,                          "Ellujääja"),
            (self.kiirus >= self.kiiruse_maks * 0.9, "Kiirusemeister"),
            (toit_tyyp == "boonus",                   "Boonusekütt"),
            (self.skoor >= 50,                        "Suurmeister"),
        ]
        for tingimus, nimi in kontrollid:
            if tingimus and self.statistika.uuenda_saavutus(nimi):
                uued.append(f"{nimi}!")

        aeg = pygame.time.get_ticks()
        for u in uued:
            self.saavutuste_teated.append((u, aeg + 3000))

    def _kontrolli_toit(self) -> None:
        px, py = self.madu.x, self.madu.y

        if px == self.toit.x and py == self.toit.y:
            self._soo(self.toit)
            self._spawni_toit()

        if px == self.boonus.x and py == self.boonus.y:
            self._soo(self.boonus)
            self._spawni_boonus()

        if self.boonus.on_aegunud():
            self._spawni_boonus()

    def _soo(self, toit_obj: Toit) -> None:
        self._helista(self.soomis_heli)
        self.madu.pikkus += toit_obj.punktid
        self.skoor += toit_obj.punktid
        self.kiirus = min(self.kiirus + toit_obj.kiiruse_kasv, self.kiiruse_maks)
        self._kontrolli_tase()
        self._kontrolli_saavutused(toit_obj.tyyp)

    def _kontrolli_takistused(self) -> bool:
        for t in self.takistused:
            if self.madu.x == t.x and self.madu.y == t.y:
                return False
        return True

    # ---- Joonistamine ----

    def _joonista_saavutused(self) -> None:
        aeg = pygame.time.get_ticks()
        aktiivsed = [(tekst, lopp - aeg)
                     for tekst, lopp in self.saavutuste_teated if aeg < lopp]
        self.saavutuste_teated = [(t, l) for t, l in self.saavutuste_teated if aeg < l]

        for i, (tekst, jarel) in enumerate(aktiivsed):
            alpha = min(255, int((jarel / 3000) * 255))
            pind = font_tavaline.render(tekst, True, KULDNE)
            kiht = pygame.Surface(pind.get_size(), pygame.SRCALPHA)
            kiht.blit(pind, (0, 0))
            kiht.set_alpha(alpha)
            ekraan.blit(kiht, (10, 70 + i * 30))

    def _joonista_hud(self) -> None:
        s_pind = font_tavaline.render(f"Skoor: {self.skoor}", True, VALGE)
        r_pind = font_tavaline.render(f"Rekord: {self.rekord}", True, KULDNE)
        t_pind = font_vike.render(f"Tase: {self.tase}", True, HALL)
        d_pind = font_vike.render(self.raskus, True, HALL)

        ekraan.blit(s_pind, (10, 10))
        ekraan.blit(r_pind, (10, 38))
        ekraan.blit(t_pind, (10, 66))
        ekraan.blit(d_pind, (LAIUS - d_pind.get_width() - 10, 10))

    def _joonista_valja(self) -> None:
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

    @staticmethod
    def _paus_kate() -> None:
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
        kate.fill((0, 0, 0, 150))
        ekraan.blit(kate, (0, 0))
        tekst_tsentris(ekraan, "PAUS", font_suur, VALGE, -25)
        tekst_tsentris(ekraan, "P – jätka mängu", font_tavaline, HALL, 25)

    # ---- Ekraanid ----

    def algus_meniu(self) -> str | None:
        valikud = ["Alusta mängu", "Seaded", "Statistika", "Credits", "Välju"]
        valitud = 0

        while True:
            ekraan.fill(MENUU_TAUST)
            tekst_tsentris(ekraan, "SNAKE GAME", font_suur, KULDNE, -150)
            tekst_tsentris(ekraan, "Kristjan – IS25  |  v2.3", font_vike, HALL, -100)

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
                        valik_tekst = valikud[valitud]
                        if valik_tekst == "Alusta mängu":
                            return "alusta"
                        elif valik_tekst == "Seaded":
                            return "seaded"
                        elif valik_tekst == "Statistika":
                            return "statistika"
                        elif valik_tekst == "Credits":
                            return "credits"
                        elif valik_tekst == "Välju":
                            return None
            kell.tick(30)

    def _seadete_kuva(self) -> None:
        """Joonista seadete ekraani sisu."""
        ekraan.fill(MENUU_TAUST)
        tekst_tsentris(ekraan, "SEADED", font_suur, KULDNE, -180)

        heli_tekst = f"Heli:       {'SEES  ✓' if self.heli_sees else 'VÄLJAS ✗'}"
        heli_varv: tuple[int, int, int] = (34, 180, 80) if self.heli_sees else (220, 60, 60)
        tekst_tsentris(ekraan, heli_tekst, font_tavaline, heli_varv, -110)

        grid_tekst = f"Ruudustik: {'SEES  ✓' if self.ruudustik_sees else 'VÄLJAS ✗'}"
        grid_varv: tuple[int, int, int] = (34, 180, 80) if self.ruudustik_sees else (220, 60, 60)
        tekst_tsentris(ekraan, grid_tekst, font_tavaline, grid_varv, -60)

        tekst_tsentris(ekraan, f"Raskus:    {self.raskus}", font_tavaline, VALGE, -10)
        tekst_tsentris(ekraan, f"Teema:     {self.teema_nimi}", font_tavaline, VALGE, 40)
        tekst_tsentris(ekraan, f"Helitugevus: {self.helitugevus}", font_tavaline, VALGE, 90)

        algus_tekst = "Algus:     " + ("Kohe" if self.algus_reziim == "kohe" else "Oota klahvi")
        tekst_tsentris(ekraan, algus_tekst, font_tavaline, VALGE, 140)

        fs_tekst = f"Ekraan:    {'Täisekraan ✓' if _fullscreen else 'Aken ✗'}"
        fs_varv: tuple[int, int, int] = (34, 180, 80) if _fullscreen else (220, 60, 60)
        tekst_tsentris(ekraan, fs_tekst, font_tavaline, fs_varv, 190)

        tekst_tsentris(ekraan, "1–Heli  2–Ruudustik  3–Raskus  4–Teema  7–Algus",
                       font_vike, HALL, 235)
        tekst_tsentris(ekraan, "5–Vol–   6–Vol+   F–Ekraan   ESC–tagasi",
                       font_vike, HALL, 258)

    def _seadete_klahv(self, key: int) -> None:
        """Töötle seadete ekraani klahvivajutust."""
        if key == pygame.K_1:
            self.heli_sees = not self.heli_sees
            try:
                if self.heli_sees:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
            except pygame.error:
                pass
        elif key == pygame.K_2:
            self.ruudustik_sees = not self.ruudustik_sees
        elif key == pygame.K_3:
            praegune = RASKUSED_JARJESTUS.index(self.raskus)
            self.raskus = RASKUSED_JARJESTUS[(praegune + 1) % len(RASKUSED_JARJESTUS)]
        elif key == pygame.K_4:
            teemad = list(TEEMAD.keys())
            idx = teemad.index(self.teema_nimi)
            self.teema_nimi = teemad[(idx + 1) % len(teemad)]
            self._taasta_ruudustik()
        elif key == pygame.K_5:
            self.helitugevus = max(0, self.helitugevus - 1)
            self._uuenda_helitugevus()
        elif key == pygame.K_6:
            self.helitugevus = min(10, self.helitugevus + 1)
            self._uuenda_helitugevus()
        elif key == pygame.K_7:
            self.algus_reziim = "kohe" if self.algus_reziim == "oota" else "oota"
        elif key == pygame.K_f:
            toggle_fullscreen()
        self._salvesta_seaded()

    def seadete_ekraan(self) -> bool | None:
        while True:
            self._seadete_kuva()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
                    self._seadete_klahv(event.key)
            kell.tick(30)

    def _statistika_read(self) -> list[str]:
        """Koosta statistika ekraani tekstiread."""
        andmed = self.statistika.andmed
        read: list[str] = [
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
        return read

    def statistika_ekraan(self) -> bool | None:
        while True:
            ekraan.fill(MENUU_TAUST)
            tekst_tsentris(ekraan, "STATISTIKA", font_suur, KULDNE, -200)

            read = self._statistika_read()
            for i, rida in enumerate(read):
                varv = VALGE if i < 5 else HALL
                tekst_tsentris(ekraan, rida, font_vike, varv, -130 + i * 25)

            tekst_tsentris(ekraan, "ESC – tagasi", font_vike, HALL, 220)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
            kell.tick(30)

    def credits_ekraan(self) -> bool | None:
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

    def _gameover_varv(self) -> tuple[int, int, int]:
        """Vali game over ülekatte värv aktiivse teema järgi.

        Klassikaline → tumeroheline,  Neon → tumesinine,  Punane → tumepunane.
        Kõigil muudel teemadel kasutatakse teema taustavärvi tumedamat versiooni.
        """
        taust = self.teema["taust"]
        # tumenda teema taustavärvi ~60 % – annab temaatilise overlay
        return tuple(max(0, int(c * 0.55)) for c in taust)  # type: ignore[return-value]

    def gameover_ekraan(self) -> bool:
        self.statistika.lisa_mang(self.skoor, self.tase)
        if self.skoor > self.rekord:
            self.rekord = self.skoor

        go_varv = self._gameover_varv()
        pealkiri_varv = self.teema.get("mao_pea", VALGE)
        fade_in_kate(go_varv, max_alpha=200, samm=7, fps=60)

        while True:
            # temaatiline poolläbipaistev ülekate
            kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
            kate.fill((*go_varv, 215))
            ekraan.blit(kate, (0, 0))

            # kerge helendav raam pealkirja ümber
            raami_varv = (*pealkiri_varv, 40)
            raami_pind = pygame.Surface((380, 60), pygame.SRCALPHA)
            raami_pind.fill(raami_varv)
            ekraan.blit(raami_pind, (LAIUS // 2 - 190, KORGUS // 2 - 110))

            tekst_tsentris(ekraan, "MÄNG LÄBI!", font_suur, pealkiri_varv, -90)
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

    # ---- Sisendi töötlus mängutsüklis ----

    def _töötle_sisend(self) -> None:
        """Töötle klahvivajutused mängu ajal."""
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

    # ---- Mängutsükkel ----

    def jooksu(self) -> bool:
        self.reset()

        while True:
            self._töötle_sisend()

            peab_ootama = (not self.madu.alustanud and self.algus_reziim == "oota")

            if self.paus or peab_ootama:
                self._joonista_valja()
                if self.paus:
                    self._paus_kate()
                else:
                    tekst_tsentris(ekraan, "Vajuta nooleklahvi alustamiseks",
                                   font_vike, HALL, 215)
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
def peaprogramm() -> None:
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