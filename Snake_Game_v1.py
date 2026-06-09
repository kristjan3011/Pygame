"""
Snake Game
Autor:   Kristjan – IS25
Versioon: 2.0
Kirjeldus: Klassipõhine Snake mäng PyGame'iga.
           Sisaldab navigeeritavat menüüd, seadete ekraani,
           raskusastet, ruudustikku, pulseerivat toitu,
           silmadega mao pead ning game over fade-in efekti.
"""

import pygame   # Mängumootori teek
import random   # Juhusliku toidu spawnimiseks
import math     # Pulseerimisanimatsiooni sinusfunktsiooniks

# Pygame'i moodulite initsialiseerimine
pygame.init()

# -------------------------------------------------------
# GLOBAALSED KONSTANDID
# -------------------------------------------------------

LAIUS  = 640   # Mänguakna laius pikslites
KORGUS = 480   # Mänguakna kõrgus pikslites
PLOKK  = 20    # Ühe ruudustiku ruudu külje suurus pikslites

# Värvid RGB-formaadis
VALGE       = (255, 255, 255)   # Valge – põhitekstid
MUST        = (0,   0,   0)     # Must – pupillid
PUNANE      = (180, 20,  20)    # Punane – game over taust
ROHELINE    = (34,  180, 80)    # Roheline – tavaline toit
KULDNE      = (255, 215, 0)     # Kuldne – boonustoit ja rekord
TAUST       = (20,  60,  120)   # Tumesinine – mänguvälja taust
RUUDUSTIK_V = (25,  70,  135)   # Veidi heledam sinine – ruudustiku jooned
MAO_PEA     = (50,  220, 100)   # Heledam roheline – mao pea
MAO_KEHA    = (0,   170, 55)    # Tumedam roheline – mao keha
HALL        = (180, 180, 180)   # Hall – teisejärgulised tekstid
TUME_HALL   = (90,  90,  90)    # Tume hall – menüü mitteaktiivne valik
MENUU_TAUST = (15,  45,  95)    # Väga tumesinine – menüü taust

# Raskusastmed: iga kiri sisaldab (algkiirus, kiiruse kasv söögil, max kiirus)
RASKUSED = {
    "Lihtne":   (6,  0.3, 12),
    "Keskmine": (10, 0.5, 18),
    "Raske":    (15, 0.8, 25),
}
RASKUSED_JARJESTUS = list(RASKUSED.keys())   # Järjestatud loend navigeerimiseks

# Fondid – laetakse üks kord, kasutatakse terves programmis
font_suur     = pygame.font.SysFont("Arial", 40)   # Pealkirjad
font_tavaline = pygame.font.SysFont("Arial", 25)   # Skoor, menüüvalikud
font_vike     = pygame.font.SysFont("Arial", 18)   # Juhised, väiksed sildid

# Peaaken ja kellaobjekt
ekraan = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("Snake Game – Kristjan IS25")
kell = pygame.time.Clock()   # Piirab FPS-i


# -------------------------------------------------------
# ABIFUNKTSIOON – teksti kuvamine ekraani keskel
# -------------------------------------------------------

def tekst_tsentris(pind, sisu, font, varv, y_nihutus=0):
    """
    Joonista tekst antud pinnale horisontaalselt keskel.
    pind       – sihtpind (tavaliselt peaekraan)
    sisu       – kuvatav string
    font       – pygame.font.Font objekt
    varv       – RGB tuple
    y_nihutus  – vertikaalne nihutus ekraani keskpunktist (pikslites)
    """
    renderdatud = font.render(sisu, True, varv)                 # Renderda tekst pinnale
    x = LAIUS  // 2 - renderdatud.get_width()  // 2            # Horisontaalne keskel
    y = KORGUS // 2 + y_nihutus                                  # Vertikaalne nihutusega
    pind.blit(renderdatud, (x, y))                               # Joonista ekraanile


# -------------------------------------------------------
# KLASS: Snake – mao olek ja loogika
# -------------------------------------------------------

class Snake:
    """
    Esindab madu: tema keha, liikumissuunda ja kollisiooniloogikat.
    Sisaldab suunabufferit, mis takistab kiire klahvivajutuse kaotsimist.
    """

    def __init__(self):
        """Loo uus madu ja lähtesta algolekusse."""
        self.reset()

    def reset(self):
        """Lähtesta kõik mao atribuudid mängu alguseks."""
        self.x = LAIUS  // 2   # Pea X-koordinaat (algab ekraani keskel)
        self.y = KORGUS // 2   # Pea Y-koordinaat (algab ekraani keskel)
        self.suund_x = 0       # Horisontaalne liikumissuund (0 = paigal)
        self.suund_y = 0       # Vertikaalne liikumissuund (0 = paigal)
        self.keha    = [(self.x, self.y)]   # Kehapositsioonide loend (saba → pea)
        self.pikkus  = 1                     # Lubatud pikkus, kasvab toidu söömisel
        self.buffer  = None                  # Järgmine suunamuutus (bufferdatud)
        self.alustanud = False               # Kas mängija on esimese klahvi vajutanud

    def muuda_suund(self, uus_dx, uus_dy):
        """
        Bufferdab järgmise suunamuutuse.
        Tagasikeerimine (nt paremalt kohe vasakule) blokeeritakse.
        """
        # Blokeeri otse vastassuunda pöördumine
        if uus_dx != 0 and uus_dx == -self.suund_x:
            return
        if uus_dy != 0 and uus_dy == -self.suund_y:
            return
        # Blokeeri korduvad sama suuna muutused
        if uus_dx == self.suund_x and uus_dy == self.suund_y:
            return

        self.buffer    = (uus_dx, uus_dy)   # Salvesta järgmiseks kaadri jaoks
        self.alustanud = True               # Märgi, et mäng on alanud

    def liiguta(self):
        """
        Uuenda mao positsiooni ühe sammu võrra.
        Tagastab True kui madu on elus, False kui põrkas seinaga/iseendaga.
        """
        # Rakenda bufferdatud suunamuutus enne liikumist
        if self.buffer is not None:
            self.suund_x, self.suund_y = self.buffer
            self.buffer = None   # Tühjenda buffer peale rakendamist

        # Uuenda pea koordinaadid
        self.x += self.suund_x
        self.y += self.suund_y

        # Kontrolli seinaga kokkupõrget
        if self.x < 0 or self.x >= LAIUS or self.y < 0 or self.y >= KORGUS:
            return False   # Surm: seinaga kokkupõrge

        # Lisa uus pea asend keha lõppu
        self.keha.append((self.x, self.y))

        # Eemalda saba kui keha on pikem kui lubatud pikkus
        if len(self.keha) > self.pikkus:
            self.keha.pop(0)

        # Kontrolli iseendaga kokkupõrget (pea ei tohi kattuda kehaga)
        if (self.x, self.y) in self.keha[:-1]:
            return False   # Surm: iseendaga kokkupõrge

        return True   # Madu on elus

    def joonista(self, pind):
        """
        Joonista madu pinnale.
        Pea on kehast eristuva värviga ja kannab silmi.
        """
        for i, (bx, by) in enumerate(self.keha):
            on_pea = (i == len(self.keha) - 1)          # Viimane element = pea
            varv   = MAO_PEA if on_pea else MAO_KEHA    # Pea heledam, keha tumedam

            # Joonista täidetud ruut 1px sissetõmbega (eraldab segmendid visuaalselt)
            pygame.draw.rect(pind, varv, (bx + 1, by + 1, PLOKK - 2, PLOKK - 2))

            # Pea silmad – ainult siis kui mäng on alanud
            if on_pea and self.alustanud:
                self._joonista_silmad(pind, bx, by)

    def _joonista_silmad(self, pind, x, y):
        """
        Joonista kaks väikest silma mao peal.
        Silmade asend sõltub hetkel liikumissuunast.
        """
        # Vali silmade asendid vastavalt suunale
        if self.suund_x == PLOKK:      # Liigub paremale
            s1, s2 = (x + 14, y + 4), (x + 14, y + 12)
        elif self.suund_x == -PLOKK:   # Liigub vasakule
            s1, s2 = (x + 4,  y + 4), (x + 4,  y + 12)
        elif self.suund_y == -PLOKK:   # Liigub üles
            s1, s2 = (x + 4,  y + 4), (x + 12, y + 4)
        else:                           # Liigub alla (vaikimisi)
            s1, s2 = (x + 4,  y + 14), (x + 12, y + 14)

        # Joonista valge silmamuna ja must pupill
        for silm in (s1, s2):
            pygame.draw.circle(pind, VALGE, silm, 3)   # Silmamuna
            pygame.draw.circle(pind, MUST,  silm, 1)   # Pupill


# -------------------------------------------------------
# KLASS: Toit – toidu olek, spawnimine ja joonistamine
# -------------------------------------------------------

class Toit:
    """
    Esindab ühte toitu mänguväljas.
    Toetab kahte tüüpi: tavaline (roheline) ja boonus (kuldne).
    """

    def __init__(self, tyyp="tavaline"):
        """
        tyyp: "tavaline" – roheline toit, +1 punkt
              "boonus"   – kuldne toit,   +3 punkti
        """
        self.tyyp        = tyyp                                         # Toidu tüüp
        self.varv        = ROHELINE if tyyp == "tavaline" else KULDNE  # Värv tüübi järgi
        self.punktid     = 1 if tyyp == "tavaline" else 3              # Skoori väärtus
        self.kiiruse_kasv = 0.5 if tyyp == "tavaline" else 1.0        # Kiiruse muutus söömisel
        self.x = 0   # X-koordinaat (määratakse spawnimisel)
        self.y = 0   # Y-koordinaat (määratakse spawnimisel)

    def spawni(self, keelatud):
        """
        Aseta toit juhuslikule vabale ruudustiku positsioonile.
        keelatud – loend (x, y) koordinaatidest, kuhu toit ei tohi ilmuda.
        Kasutab eelnevalt arvutatud vabade kohtade loendit, mitte lõputut tsüklit.
        """
        # Kogu kõik võimalikud ruudustiku positsioonid loendisse
        koik = [
            (x, y)
            for x in range(0, LAIUS, PLOKK)
            for y in range(0, KORGUS, PLOKK)
        ]
        # Filtreeri välja keelatud positsioonid
        vabad = [pos for pos in koik if pos not in keelatud]

        if vabad:
            self.x, self.y = random.choice(vabad)   # Vali juhuslik vaba koht
        # Kui vabu kohti ei ole (väga harv olukord), jää paigale

    def joonista(self, pind):
        """
        Joonista toit pulseeriva suuruse animatsiooniga.
        Boonus toit saab lisaks heleduse vilkumise.
        """
        aeg   = pygame.time.get_ticks()                      # Millisekunde alates käivitusest
        pulss = math.sin(aeg / 300) * 2                      # Vahemik –2 … +2 pikslit
        suurus   = int(PLOKK - 4 + pulss)                   # Ruudu külje suurus pulseerib
        nihutus  = (PLOKK - suurus) // 2                    # Tsentreeritud nihutus ruudustiku ruudus

        # Joonista põhiruut ümardatud nurkadega
        pygame.draw.rect(
            pind, self.varv,
            (self.x + nihutus, self.y + nihutus, suurus, suurus),
            border_radius=3
        )

        # Boonustoidule lisatakse valge heleduse kiht, mis vilgub sagedamini
        if self.tyyp == "boonus":
            heledus = int(abs(math.sin(aeg / 200)) * 90)        # 0–90 läbipaistvus
            kiht = pygame.Surface((suurus, suurus), pygame.SRCALPHA)
            kiht.fill((255, 255, 255, heledus))                  # Valge kiht läbipaistvusega
            pind.blit(kiht, (self.x + nihutus, self.y + nihutus))


# -------------------------------------------------------
# KLASS: Mang – mängu haldur (loogika, ekraanid, seaded)
# -------------------------------------------------------

class Mang:
    """
    Peaklass, mis haldab mängu olekut, ekraane ja seadeid.
    Sisaldab: algusmenüü, seadete ekraan, mängutsükkel, game over ekraan.
    """

    def __init__(self):
        """Initsialiseeri mängu seaded, helifailid ja mänguobjektid."""
        # --- Kasutaja seaded (muudetavad Options ekraanilt) ---
        self.heli_sees      = True          # Kas helid on sisse lülitatud
        self.ruudustik_sees = True          # Kas ruudustik on nähtav
        self.raskus         = "Keskmine"    # Valitud raskusaste

        # --- Helifailide laadimine (vead ei krahhi mängu) ---
        self.soomis_heli   = None   # Söömise heli objekt (või None)
        self.gameover_heli = None   # Game over heli objekt (või None)
        self._laadi_helid()

        # --- Ruudustiku pind (loodud üks kord, kasutatud korduvalt) ---
        self.ruudustiku_pind = self._loo_ruudustiku_pind()

        # --- Mänguobjektid ---
        self.madu   = Snake()           # Mao objekt
        self.toit   = Toit("tavaline")  # Roheline tavaline toit
        self.boonus = Toit("boonus")    # Kuldne boonustoit

        # --- Mängu käimasolev olek ---
        self.skoor   = 0    # Praeguse mängu skoor
        self.rekord  = 0    # Sessiooni parim tulemus
        self.kiirus  = RASKUSED[self.raskus][0]   # Praegune kiirus (FPS)
        self.paus    = False   # Kas mäng on pausis

    # ---- Helid ----

    def _laadi_helid(self):
        """Lae helifailid; kui ebaõnnestub, jätka vaikivalt."""
        try:
            pygame.mixer.music.load("music/taust.mp3")   # Taustamuusika
            pygame.mixer.music.play(-1)                   # Mängi lõputsüklis
            self.soomis_heli   = pygame.mixer.Sound("music/eat.wav")
            self.gameover_heli = pygame.mixer.Sound("music/gameover.wav")
        except Exception as e:
            print(f"Heli laadimine ebaõnnestus: {e}")   # Teade konsooli, mäng jätkub

    def _helista(self, heli):
        """Mängi heli ainult siis, kui see on laaditud ja heli on lubatud seadetest."""
        if heli is not None and self.heli_sees:
            heli.play()

    # ---- Ruudustik ----

    def _loo_ruudustiku_pind(self):
        """
        Loo ruudustiku pind üks kord programmikäivituse alguses.
        Läbipaistev pind koos horisontaalsete ja vertikaalsete joontega.
        Joonistame selle iga kaadri alguses taustale, mitte ei genereeri uuesti.
        """
        pind = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)   # Läbipaistev pind
        joone_varv = (*RUUDUSTIK_V, 70)   # Ruudustiku värv koos läbipaistvusega (alpha=70)

        for x in range(0, LAIUS, PLOKK):
            pygame.draw.line(pind, joone_varv, (x, 0), (x, KORGUS))   # Vertikaalsed jooned

        for y in range(0, KORGUS, PLOKK):
            pygame.draw.line(pind, joone_varv, (0, y), (LAIUS, y))    # Horisontaalsed jooned

        return pind   # Tagasta valmis pind

    # ---- Mängu lähtestamine ----

    def reset(self):
        """Lähtesta mäng uue vooru alguseks (säilitab rekordi ja seaded)."""
        alg, kasv, maks    = RASKUSED[self.raskus]   # Laadi raskusastme parameetrid
        self.kiirus        = alg    # Alg kiirus
        self.kiiruse_kasv  = kasv   # Kiiruse juurdekasv söögil
        self.kiiruse_maks  = maks   # Kiiruse ülempiir
        self.skoor         = 0      # Skoor nullist
        self.paus          = False  # Ei alusta pausis

        self.madu.reset()   # Lähtesta mao olek

        # Spawni toit kohta, kus madu ei asu
        self.toit.spawni(self.madu.keha)
        self.boonus.spawni(self.madu.keha + [(self.toit.x, self.toit.y)])

    # ---- Joonistamisabifunktsioonid ----

    def _joonista_hud(self):
        """Kuva ekraani servades skoor, rekord ja raskusaste."""
        s_pind = font_tavaline.render(f"Skoor: {self.skoor}",   True, VALGE)
        r_pind = font_tavaline.render(f"Rekord: {self.rekord}", True, KULDNE)
        d_pind = font_vike.render(self.raskus, True, HALL)

        ekraan.blit(s_pind, (10, 10))                                        # Skoor vasakul ülal
        ekraan.blit(r_pind, (10, 38))                                        # Rekord skoori all
        ekraan.blit(d_pind, (LAIUS - d_pind.get_width() - 10, 10))         # Raskus paremal ülal

    def _joonista_valja(self):
        """Joonista täielik mänguväli: taust, ruudustik, toit, madu, HUD."""
        ekraan.fill(TAUST)                              # Täida taust värviga

        if self.ruudustik_sees:
            ekraan.blit(self.ruudustiku_pind, (0, 0))  # Kanna ruudustik peale (eelrenderitud)

        self.toit.joonista(ekraan)                      # Roheline toit
        self.boonus.joonista(ekraan)                    # Kuldne boonustoit
        self.madu.joonista(ekraan)                      # Madu (pea + keha + silmad)
        self._joonista_hud()                            # Skoor ja muud andmed

    def _paus_kate(self):
        """Kuva paus-olek: tumendab ekraani ja näitab tekste."""
        kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)   # Läbipaistev pind
        kate.fill((0, 0, 0, 150))                                   # Must, ~60% läbipaistvus
        ekraan.blit(kate, (0, 0))                                   # Kata kogu ekraan

        tekst_tsentris(ekraan, "PAUS",              font_suur,     VALGE, -25)
        tekst_tsentris(ekraan, "P – jätka mängu",   font_tavaline, HALL,  25)

    # ---- Ekraanid ----

    def algus_meniu(self):
        """
        Peamenüü kolme valikuga: Alusta mängu, Seaded, Välju.
        Navigeerimine nooleklahvidega, kinnitus ENTERiga.
        Tagastab: "alusta", "seaded" või None (välju programmi).
        """
        valikud = ["Alusta mängu", "Seaded", "Välju"]   # Menüüvalikute loend
        valitud = 0                                       # Praegu esile tõstetud valik

        while True:
            ekraan.fill(MENUU_TAUST)   # Menüü taust

            # Pealkiri ja alapealkiri
            tekst_tsentris(ekraan, "SNAKE GAME",        font_suur,     KULDNE, -150)
            tekst_tsentris(ekraan, "Kristjan – IS25",   font_vike,     HALL,   -100)

            # Joonista valikud – aktiivne valik on valge, teised hallid
            for i, valik in enumerate(valikud):
                varv = VALGE if i == valitud else TUME_HALL
                tekst_tsentris(ekraan, valik, font_tavaline, varv, -30 + i * 50)

            # Navigeerimisinfo
            tekst_tsentris(ekraan, "↑ ↓ – vali   ENTER – kinnita", font_vike, HALL, 150)

            pygame.display.flip()   # Uuenda ekraan

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None   # Aken suleti

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        valitud = (valitud - 1) % len(valikud)    # Liigu üles (ring)
                    elif event.key == pygame.K_DOWN:
                        valitud = (valitud + 1) % len(valikud)    # Liigu alla (ring)
                    elif event.key == pygame.K_RETURN:
                        # Kinnita valitud valik
                        if valitud == 0: return "alusta"
                        if valitud == 1: return "seaded"
                        if valitud == 2: return None

            kell.tick(30)   # Madal FPS menüüs

    def seadete_ekraan(self):
        """
        Seadete ekraan kolme seadistusega:
          1 – Heli sisse/välja
          2 – Ruudustik sisse/välja
          3 – Raskusastme vahetus (tsükliline)
        Tagastab True (tagasi menüüsse) või None (välju programmi).
        """
        while True:
            ekraan.fill(MENUU_TAUST)   # Seadete ekraani taust

            tekst_tsentris(ekraan, "SEADED", font_suur, KULDNE, -160)

            # Heli – roheline kui sees, punane kui väljas
            heli_tekst = f"Heli:       {'SEES  ✓' if self.heli_sees else 'VÄLJAS ✗'}"
            heli_varv  = ROHELINE if self.heli_sees else (220, 60, 60)
            tekst_tsentris(ekraan, heli_tekst, font_tavaline, heli_varv, -80)

            # Ruudustik – sama värviskeem
            grid_tekst = f"Ruudustik: {'SEES  ✓' if self.ruudustik_sees else 'VÄLJAS ✗'}"
            grid_varv  = ROHELINE if self.ruudustik_sees else (220, 60, 60)
            tekst_tsentris(ekraan, grid_tekst, font_tavaline, grid_varv, -20)

            # Raskusaste – alati valge
            rask_tekst = f"Raskus:    {self.raskus}"
            tekst_tsentris(ekraan, rask_tekst, font_tavaline, VALGE, 40)

            # Klahvijuhised
            tekst_tsentris(ekraan, "1 – Heli        2 – Ruudustik        3 – Raskus",
                           font_vike, HALL, 120)
            tekst_tsentris(ekraan, "ESC – tagasi peamenüüsse", font_vike, HALL, 150)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None   # Programm suletakse

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True   # Tagasi peamenüüsse

                    elif event.key == pygame.K_1:
                        # Lülita heli sisse/välja
                        self.heli_sees = not self.heli_sees
                        try:
                            if self.heli_sees:
                                pygame.mixer.music.unpause()   # Jätka taustamuusikat
                            else:
                                pygame.mixer.music.pause()     # Peata taustamuusika
                        except Exception:
                            pass   # Muusika ei pruugi olla laaditud

                    elif event.key == pygame.K_2:
                        # Lülita ruudustik sisse/välja
                        self.ruudustik_sees = not self.ruudustik_sees

                    elif event.key == pygame.K_3:
                        # Vaheta raskusastet tsükliliselt
                        praegune = RASKUSED_JARJESTUS.index(self.raskus)
                        self.raskus = RASKUSED_JARJESTUS[(praegune + 1) % len(RASKUSED_JARJESTUS)]

            kell.tick(30)

    def gameover_ekraan(self):
        """
        Game over ekraan koos fade-in animatsiooniga.
        Punane kate libiseb järk-järgult sisse külmutatud mängukaadri peale.
        Tagastab True (mängi uuesti) või False (tagasi peamenüüsse).
        """
        # Fade-in: suurenda punase katte läbipaistvust 0-st 200-ni
        for alpha in range(0, 201, 7):
            kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
            kate.fill((PUNANE[0], PUNANE[1], PUNANE[2], alpha))   # Punane kasvava läbipaistvusega
            ekraan.blit(kate, (0, 0))    # Kata külmutatud mängukaadri peale
            pygame.display.flip()
            kell.tick(60)               # Piisavalt kiire et animatsioon sujuv oleks

        # Statiline game over ekraan pärast fade-in lõppu
        while True:
            kate = pygame.Surface((LAIUS, KORGUS), pygame.SRCALPHA)
            kate.fill((*PUNANE, 210))   # Lõplik punane kaas
            ekraan.blit(kate, (0, 0))

            tekst_tsentris(ekraan, "MÄNG LÄBI!",          font_suur,     VALGE, -80)
            tekst_tsentris(ekraan, f"Skoor:  {self.skoor}",  font_tavaline, VALGE, -20)
            tekst_tsentris(ekraan, f"Rekord: {self.rekord}", font_tavaline, KULDNE, 15)
            tekst_tsentris(ekraan, "ENTER – mängi uuesti",  font_tavaline, VALGE, 75)
            tekst_tsentris(ekraan, "ESC – peamenüü",        font_tavaline, HALL, 110)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return True    # Mängi uuesti
                    elif event.key == pygame.K_ESCAPE:
                        return False   # Tagasi peamenüüsse

            kell.tick(30)

    # ---- Peamine mängutsükkel ----

    def jooksu(self):
        """
        Käivita üks mänguvoor: lähtestab, töötleb sündmusi, liigutab madu,
        kontrollib söömist ja kollisioone.
        Tagastab True kui mängija soovib uuesti mängida, False peamenüüsse.
        """
        self.reset()   # Lähtesta olek enne mängu algust

        while True:
            # --- Sündmuste töötlemine ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()   # Kohe väljub

                elif event.type == pygame.KEYDOWN:
                    # P-klahv lülitab pausi ainult siis kui mäng on alanud
                    if event.key == pygame.K_p and self.madu.alustanud:
                        self.paus = not self.paus

                    # Suunaklahvid (toimivad ainult pausiväliselt)
                    if not self.paus:
                        if event.key == pygame.K_LEFT:
                            self.madu.muuda_suund(-PLOKK, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.madu.muuda_suund( PLOKK, 0)
                        elif event.key == pygame.K_UP:
                            self.madu.muuda_suund(0, -PLOKK)
                        elif event.key == pygame.K_DOWN:
                            self.madu.muuda_suund(0,  PLOKK)

            # --- Paus või ootab esimest klahvi ---
            if self.paus or not self.madu.alustanud:
                self._joonista_valja()                     # Joonista mäng taha

                if self.paus:
                    self._paus_kate()                      # Tumenda ja kuva PAUS
                else:
                    tekst_tsentris(
                        ekraan,
                        "Vajuta nooleklahvi alustamiseks",
                        font_vike, HALL, 215
                    )

                pygame.display.flip()
                kell.tick(30)   # Madal FPS pausis – protsessor tänab
                continue        # Jäta mänguloogika vahele

            # --- Mao liigutamine ---
            elus = self.madu.liiguta()

            if not elus:
                # Madu suri – uuenda rekord ja kuva game over ekraan
                self._helista(self.gameover_heli)
                self.rekord = max(self.skoor, self.rekord)   # Uuenda sessiooni rekord
                self._joonista_valja()                        # Joonista viimane kaader
                pygame.display.flip()                         # Kinnista ekraan enne fade-in
                return self.gameover_ekraan()                 # Käivita game over animatsioon

            # --- Toidu söömise kontroll ---
            self._kontrolli_toit()

            # --- Joonistamine ---
            self._joonista_valja()
            pygame.display.flip()
            kell.tick(int(self.kiirus))   # FPS = kiirus (kasvab aja jooksul)

    def _kontrolli_toit(self):
        """Kontrolli kas mao pea kattub toidu asukohaga ja rakenda mõjud."""
        px, py = self.madu.x, self.madu.y   # Mao pea hetke koordinaadid

        # Tavaline toit
        if px == self.toit.x and py == self.toit.y:
            self._soo(self.toit)
            # Spawni uus toit – mitte mao ega boonuse peale
            self.toit.spawni(self.madu.keha + [(self.boonus.x, self.boonus.y)])

        # Boonustoit
        if px == self.boonus.x and py == self.boonus.y:
            self._soo(self.boonus)
            # Spawni uus boonus – mitte mao ega tavalise toidu peale
            self.boonus.spawni(self.madu.keha + [(self.toit.x, self.toit.y)])

    def _soo(self, toit_obj):
        """Rakenda toidu söömise tagajärjed: heli, skoori lisamine, kiiruse tõus."""
        self._helista(self.soomis_heli)                                    # Söömise heli
        self.madu.pikkus += toit_obj.punktid                              # Kasvata madu
        self.skoor        += toit_obj.punktid                             # Lisa skoorile
        self.kiirus = min(self.kiirus + self.kiiruse_kasv, self.kiiruse_maks)  # Tõsta kiirust


# -------------------------------------------------------
# PEAPROGRAMM
# -------------------------------------------------------

def peaprogramm():
    """
    Haldab mängu üldist voogu:
    algusmenüü → (seaded | mängutsükkel → game over) → tagasi menüüsse.
    """
    mang = Mang()   # Loo mängu peaobjekt

    while True:
        tulemus = mang.algus_meniu()   # Kuva peamenüü ja oota valikut

        if tulemus is None:
            break   # Mängija valis Välju või sulges akna

        elif tulemus == "seaded":
            # Ava seadete ekraan; None tähendab, et aken suleti
            if mang.seadete_ekraan() is None:
                break

        elif tulemus == "alusta":
            # Mängutsükkel: mängi kuni mängija valib peamenüüsse mineku
            jatka = True
            while jatka:
                jatka = mang.jooksu()   # True = mängi uuesti, False = peamenüüsse

    pygame.quit()   # Sulge pygame


# Käivita ainult siis, kui fail on peafail (mitte imporditud moodul)
if __name__ == "__main__":
    peaprogramm()