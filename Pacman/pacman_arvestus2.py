"""
PAC-MAN arvestustöö Kristjan IS25.

Juhtimine:
    Menüü: 1 = klassikaline režiim, 2 = algaja režiim
    Mäng: nooleklahvid või WASD = liikumine, P = paus, R = taaskäivitus,
          M = menüü, ESC = välju
"""

import random
import sys
import math
from array import array
from collections import deque
from pathlib import Path

import pygame


# Ekraani ja ruudustiku põhiseaded.
CELL = 24
COLS = 21
ROWS = 23
W = COLS * CELL
H = ROWS * CELL + 72
FPS = 60

# Värvid.
BLACK = (0, 0, 0)
BLUE = (0, 0, 180)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
RED = (220, 0, 0)
PINK = (255, 180, 200)
CYAN = (0, 220, 220)
ORANGE = (255, 160, 0)
DKBLUE = (0, 0, 80)
LBLUE = (100, 100, 255)
GREEN = (0, 190, 90)
CHERRY = (230, 35, 65)

# Plaadi tüübid.
WALL = 0
DOT = 1
EMPTY = 2
POWER = 3
GATE = 4

# Suunavektorid.
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRS = [UP, DOWN, LEFT, RIGHT]
BASE_DIR = Path(__file__).resolve().parent
SOUND_DIR = BASE_DIR


# Klassikaline kaart.
# Kummitusmaja (G) asub ridadel 8-10, veergudel 9-11.
# Kummitused väljuvad läbi GATE rea 7 (veerg 10).
RAW_MAP_CLASSIC = [
    "WWWWWWWWWWWWWWWWWWWWW",  # 0
    "W.........W.........W",  # 1
    "W.WWW.WWW.W.WWW.WWW.W",  # 2
    "Wo.................oW",  # 3
    "W.WWW.W.WWWWW.W.WWW.W",  # 4
    "W.....W.......W.....W",  # 5
    "WWWWW.WWWWWWWWW.WWWWW",  # 6
    "    W.WGGGGGGGW.W    ",  # 7  -- GATE rida: kummitused väljuvad siit üles
    "WWWWW.WWWWGWWWW.WWWWW",  # 8
    "     ...........     ",  # 9  -- kummitusmaja sisemus
    "WWWWW.W.......W.WWWWW",  # 10 -- kummitusmaja põhi
    "    W...........W    ",  # 11
    "WWWWW.WWWWWWWWW.WWWWW",  # 12
    "W.........W.........W",  # 13
    "W.WWW.WWW.W.WWW.WWW.W",  # 14
    "Wo....W.......W....oW",  # 15
    "WWW.W.W.WWWWW.W.W.WWW",  # 16
    "W.....W.......W.....W",  # 17
    "W.WWWWWWW.W.WWWWWWW.W",  # 18
    "W...................W",  # 19
    "W.WWW.WWW.W.WWW.WWW.W",  # 20
    "W.........W.........W",  # 21
    "WWWWWWWWWWWWWWWWWWWWW",  # 22
]

# Klassikalise kaardi kummitusmaja: G-d on ridadel 8-10, veergudel 8-12.
# Neli kummitust paigutatakse 2x2 ruudustikku maja keskel.
GHOST_HOMES_CLASSIC = [
    (9  * CELL + CELL // 2,  9 * CELL + CELL // 2),  # punane
    (11 * CELL + CELL // 2,  9 * CELL + CELL // 2),  # roosa
    (9  * CELL + CELL // 2, 10 * CELL + CELL // 2),  # tsüaan
    (11 * CELL + CELL // 2, 10 * CELL + CELL // 2),  # oranž
]
# Kummitused väljuvad rea 7 keskmisest lahtrist ülespoole.
GHOST_EXIT_CELL_CLASSIC = (10, 7)


# Algaja kaart.
# Kaks kummitust paigutatakse maja sisemusse.
RAW_MAP_BEGINNER = [
    "WWWWWWWWWWWWWWWWWWWWW",  # 0
    "W.........W.........W",  # 1
    "W.WWW.WWW.W.WWW.WWW.W",  # 2
    "Wo.................oW",  # 3
    "W.W.W...........W.W.W",  # 4
    "W...W.WWWWWWWWW.W...W",  # 5
    "W.W.W.W       W.W.W.W",  # 6
    "W.....WGGGGGGGW.....W",  # 7  -- GATE rida
    "W.W.W.WWWWGWWWW.W.W.W",  # 8
    "W...W...........W...W",  # 9  -- kummitusmaja sisemus
    "W.W.W.W.......W.W.W.W",  # 10 -- kummitusmaja põhi
    "W...................W",  # 11
    "W.WWW.WWW.W.WWW.WWW.W",  # 12
    "W.....W.......W.....W",  # 13
    "W.WWW.W.WWWWW.W.WWW.W",  # 14
    "Wo.................oW",  # 15
    "W.WWW.WWW.W.WWW.WWW.W",  # 16
    "W.........W.........W",  # 17
    "W.WWW.W.......W.WWW.W",  # 18
    "W...................W",  # 19
    "W.WWW.WWW.W.WWW.WWW.W",  # 20
    "W.........W.........W",  # 21
    "WWWWWWWWWWWWWWWWWWWWW",  # 22
]

# Algaja kaardi kaks kummitust paigutatakse maja sisemusse.
GHOST_HOMES_BEGINNER = [
    (9  * CELL + CELL // 2,  9 * CELL + CELL // 2),  # punane
    (11 * CELL + CELL // 2,  9 * CELL + CELL // 2),  # roosa
]
GHOST_EXIT_CELL_BEGINNER = (10, 7)


MODES = {
    "classic": {
        "title": "Klassikaline režiim",
        "map": RAW_MAP_CLASSIC,
        "ghost_count": 4,
        "pacman_speed": 3,
        "ghost_speed": 2,
        "ghost_ai": "bfs",
        "player_start": (10, 17),
        "ghost_homes": GHOST_HOMES_CLASSIC,
        "ghost_exit_cell": GHOST_EXIT_CELL_CLASSIC,
        "info": "Algupärane labürint, 4 kummitust ja kiirem tagaajamine.",
    },
    "beginner": {
        "title": "Algaja režiim",
        "map": RAW_MAP_BEGINNER,
        "ghost_count": 2,
        "pacman_speed": 3,
        "ghost_speed": 1,
        "ghost_ai": "random",
        "player_start": (10, 19),
        "ghost_homes": GHOST_HOMES_BEGINNER,
        "ghost_exit_cell": GHOST_EXIT_CELL_BEGINNER,
        "info": "Lihtsam labürint, 2 aeglasemat juhuslikku kummitust.",
    },
}


def build_map(raw_map):
    """Teisenda tekstkaart kahemõõtmeliseks plaatide ruudustikuks."""
    grid = []
    for raw in raw_map[:ROWS]:
        row = []
        for ch in raw[:COLS]:
            if ch == "W":
                row.append(WALL)
            elif ch == ".":
                row.append(DOT)
            elif ch == "o":
                row.append(POWER)
            elif ch == "G":
                row.append(GATE)
            else:
                row.append(EMPTY)
        while len(row) < COLS:
            row.append(WALL)
        grid.append(row)

    while len(grid) < ROWS:
        grid.append([WALL] * COLS)

    return grid


def is_tunnel_row(grid, gy):
    """Tagasta True, kui rea vasak või parem külg on avatud (tunnel)."""
    if not 0 <= gy < ROWS:
        return False
    return grid[gy][0] != WALL or grid[gy][COLS - 1] != WALL


def bfs(grid, start, goal, allow_gate=False):
    """Tagasta lühima tee esimene suund alguspunktist sihtpunkti."""
    sx, sy = start
    gx, gy = goal
    if (sx, sy) == (gx, gy):
        return None

    visited = {(sx, sy)}
    queue = deque()

    for direction in DIRS:
        nx, ny = sx + direction[0], sy + direction[1]
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            tile = grid[ny][nx]
            if tile != WALL and (allow_gate or tile != GATE):
                visited.add((nx, ny))
                queue.append((nx, ny, direction))

    while queue:
        cx, cy, first_dir = queue.popleft()
        if (cx, cy) == (gx, gy):
            return first_dir

        for direction in DIRS:
            nx, ny = cx + direction[0], cy + direction[1]
            if not (0 <= nx < COLS and 0 <= ny < ROWS):
                continue
            if (nx, ny) in visited:
                continue

            tile = grid[ny][nx]
            if tile != WALL and (allow_gate or tile != GATE):
                visited.add((nx, ny))
                queue.append((nx, ny, first_dir))

    return None


class Pacman:
    """Mängija tegelane: haldab liikumist, kollisiooni ja suu animatsiooni."""

    def __init__(self, grid, start_cell, speed):
        self.grid = grid
        self.start_cell = start_cell
        self.speed = speed
        self.reset()

    def reset(self):
        self.px = self.start_cell[0] * CELL + CELL // 2
        self.py = self.start_cell[1] * CELL + CELL // 2
        self.dir = RIGHT
        self.next_dir = RIGHT
        self.alive = True
        self.mouth = 0
        self.mouth_dir = 1

    @property
    def gx(self):
        return self.px // CELL

    @property
    def gy(self):
        return self.py // CELL

    def set_dir(self, direction):
        self.next_dir = direction

    def _align(self, axis):
        if axis == "x":
            self.px = (self.px // CELL) * CELL + CELL // 2
        else:
            self.py = (self.py // CELL) * CELL + CELL // 2

    def _blocked_pixel(self, x, y):
        gx = x // CELL
        gy = y // CELL

        if gx < 0 or gx >= COLS:
            return not is_tunnel_row(self.grid, gy)
        if not 0 <= gy < ROWS:
            return True

        return self.grid[gy][gx] in (WALL, GATE)

    def _can_move(self, dx, dy):
        nx = self.px + dx * self.speed
        ny = self.py + dy * self.speed
        radius = CELL // 2 - 2

        corners = [
            (nx - radius, ny - radius),
            (nx + radius, ny - radius),
            (nx - radius, ny + radius),
            (nx + radius, ny + radius),
        ]
        return not any(self._blocked_pixel(x, y) for x, y in corners)

    def update(self):
        if not self.alive:
            return

        ndx, ndy = self.next_dir
        dx, dy = self.dir
        aligned_x = abs(self.px % CELL - CELL // 2) < self.speed + 1
        aligned_y = abs(self.py % CELL - CELL // 2) < self.speed + 1

        if self.next_dir != self.dir and aligned_x and aligned_y:
            if self._can_move(ndx, ndy):
                if ndx != 0:
                    self._align("y")
                if ndy != 0:
                    self._align("x")
                self.dir = self.next_dir
                dx, dy = ndx, ndy

        if self._can_move(dx, dy):
            self.px += dx * self.speed
            self.py += dy * self.speed
        else:
            if dx != 0:
                self._align("y")
            if dy != 0:
                self._align("x")

        if self.px < 0:
            self.px = W - CELL // 2
        elif self.px >= W:
            self.px = CELL // 2

        self.mouth += 4 * self.mouth_dir
        if self.mouth >= 40:
            self.mouth_dir = -1
        elif self.mouth <= 0:
            self.mouth_dir = 1

    def draw(self, surface):
        if not self.alive:
            return

        cx, cy = self.px, self.py
        radius = CELL // 2 - 1
        angle_map = {RIGHT: 0, LEFT: 180, UP: 90, DOWN: 270}
        angle = angle_map.get(self.dir, 0)

        pygame.draw.circle(surface, YELLOW, (cx, cy), radius)

        if self.mouth > 2:
            points = [(cx, cy)]
            for a in range(angle - self.mouth, angle + self.mouth + 1, 5):
                rotated = pygame.math.Vector2(radius, 0).rotate(-a)
                points.append((cx + int(rotated.x), cy + int(rotated.y)))
            points.append((cx, cy))
            if len(points) > 2:
                pygame.draw.polygon(surface, BLACK, points)

        eye_base = pygame.math.Vector2(0, -1).rotate(-angle)
        eye_side = pygame.math.Vector2(1, 0).rotate(-angle)
        ex = int(cx + radius * 0.4 * eye_base.x - radius * 0.3 * eye_side.x)
        ey = int(cy + radius * 0.4 * eye_base.y - radius * 0.3 * eye_side.y)
        pygame.draw.circle(surface, BLACK, (ex, ey), 2)


class Ghost:
    """Vaenlase tegelane: režiimipõhine AI ning ühine joonistus- ja kollisiooniloogika."""

    FRIGHT_TIME = 8 * FPS

    def __init__(self, grid, gid, home, exit_cell, speed):
        self.grid = grid
        self.gid = gid
        self.home = home
        self.exit_cell = exit_cell  # lahkumissihtmärk (veerg, rida)
        self.speed = speed
        self.ai_mode = "bfs"
        self.colour = [RED, PINK, CYAN, ORANGE][gid]
        self.reset()

    def reset(self):
        self.px, self.py = self.home
        self.dir = UP
        self.fright = 0
        self.eaten = False
        self.in_house = True
        self.exit_timer = ghost_exit_delay(self.gid)

    @property
    def gx(self):
        return self.px // CELL

    @property
    def gy(self):
        return self.py // CELL

    def frighten(self):
        if not self.eaten:
            self.fright = self.FRIGHT_TIME

    def eat(self):
        self.eaten = True
        self.fright = 0

    def _at_cell_center(self):
        return (
            abs(self.px % CELL - CELL // 2) < self.speed + 1
            and abs(self.py % CELL - CELL // 2) < self.speed + 1
        )

    def _blocked_pixel(self, x, y):
        gx = x // CELL
        gy = y // CELL

        if gx < 0 or gx >= COLS:
            return not is_tunnel_row(self.grid, gy)
        if not 0 <= gy < ROWS:
            return True

        return self.grid[gy][gx] == WALL

    def _valid_direction(self, direction):
        nx = self.gx + direction[0]
        ny = self.gy + direction[1]
        if nx < 0 or nx >= COLS:
            return is_tunnel_row(self.grid, self.gy)
        if not 0 <= ny < ROWS:
            return False
        return self.grid[ny][nx] != WALL

    def _choose_dir(self, target):
        reverse = (-self.dir[0], -self.dir[1])
        best = bfs(self.grid, (self.gx, self.gy), target, allow_gate=True)
        if best and best != reverse:
            return best

        options = [d for d in DIRS if d != reverse and self._valid_direction(d)]
        if options:
            return random.choice(options)

        reverse_options = [d for d in DIRS if self._valid_direction(d)]
        if reverse_options:
            return random.choice(reverse_options)

        return self.dir

    def _choose_random_dir(self):
        reverse = (-self.dir[0], -self.dir[1])
        options = [d for d in DIRS if d != reverse and self._valid_direction(d)]
        if not options:
            options = [d for d in DIRS if self._valid_direction(d)]
        return random.choice(options) if options else self.dir

    def _move(self, direction):
        self.dir = direction
        nx = self.px + direction[0] * self.speed
        ny = self.py + direction[1] * self.speed
        radius = CELL // 2 - 2

        corners = [
            (nx - radius, ny - radius),
            (nx + radius, ny - radius),
            (nx - radius, ny + radius),
            (nx + radius, ny + radius),
        ]
        blocked = any(self._blocked_pixel(x, y) for x, y in corners)
        if not blocked:
            self.px, self.py = nx, ny

        if self.px < 0:
            self.px = W - CELL // 2
        elif self.px >= W:
            self.px = CELL // 2

    def update(self, pacman):
        if self.in_house:
            self.exit_timer -= 1
            if self.exit_timer > 0:
                return
            self.in_house = False

        if self.eaten:
            home_cell = (self.home[0] // CELL, self.home[1] // CELL)
            if (self.gx, self.gy) == home_cell and self._at_cell_center():
                self.eaten = False
                self.in_house = True
                self.exit_timer = 120
                return
            if self._at_cell_center():
                if self.ai_mode == "random":
                    self.dir = self._choose_random_dir()
                else:
                    self.dir = self._choose_dir(home_cell)
            self._move(self.dir)
            return

        if self.fright > 0:
            self.fright -= 1
            if self._at_cell_center():
                self.dir = self._choose_random_dir()
            self._move(self.dir)
            return

        if self.ai_mode == "random":
            if self._at_cell_center():
                self.dir = self._choose_random_dir()
            self._move(self.dir)
            return

        if self._at_cell_center():
            self.dir = self._choose_dir((pacman.gx, pacman.gy))
        self._move(self.dir)

    def draw(self, surface):
        cx, cy = self.px, self.py
        radius = CELL // 2 - 1

        if self.fright > 0:
            colour = LBLUE if self.fright > 2 * FPS else (
                WHITE if (pygame.time.get_ticks() // 300) % 2 == 0 else LBLUE
            )
        elif self.eaten:
            colour = DKBLUE
        else:
            colour = self.colour

        body = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2 + 4)
        pygame.draw.rect(surface, colour, body, border_radius=radius)
        pygame.draw.rect(surface, colour, (cx - radius, cy, radius * 2, radius))

        wave_y = cy + radius
        for i in range(3):
            wx = cx - radius + i * (radius * 2 // 3)
            pygame.draw.circle(surface, colour, (wx + radius // 3, wave_y), radius // 3)

        if not self.fright and not self.eaten:
            for ex_off in (-radius // 3, radius // 3):
                pygame.draw.circle(surface, WHITE, (cx + ex_off, cy - radius // 4), radius // 4)
                dx_off = self.dir[0] * (radius // 6)
                dy_off = self.dir[1] * (radius // 6)
                pygame.draw.circle(
                    surface,
                    BLUE,
                    (cx + ex_off + dx_off, cy - radius // 4 + dy_off),
                    radius // 7,
                )
        elif self.eaten:
            for ex_off in (-radius // 3, radius // 3):
                pygame.draw.line(
                    surface,
                    WHITE,
                    (cx + ex_off - radius // 5, cy - radius // 4 + radius // 5),
                    (cx + ex_off + radius // 5, cy - radius // 4 - radius // 5),
                    2,
                )


def ghost_exit_delay(gid):
    """Hajuta kummituste väljumist, et kõik ei lahkuks majast korraga."""
    return [0, 60, 120, 200][gid]


class BonusFruit:
    """Ajutine boonusese, mis ilmub pärast piisava arvu täppide kogumist."""

    def __init__(self):
        self.active = False
        self.px = 10 * CELL + CELL // 2
        self.py = 15 * CELL + CELL // 2
        self.timer = 0

    def spawn(self):
        self.active = True
        self.timer = 10 * FPS

    def update(self):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False

    def draw(self, surface):
        if not self.active:
            return

        cx, cy = self.px, self.py
        pygame.draw.circle(surface, CHERRY, (cx - 4, cy + 2), 5)
        pygame.draw.circle(surface, CHERRY, (cx + 4, cy + 2), 5)
        pygame.draw.line(surface, GREEN, (cx - 2, cy - 2), (cx + 4, cy - 10), 2)
        pygame.draw.line(surface, GREEN, (cx + 4, cy - 10), (cx + 10, cy - 7), 2)


class SoundManager:
    """Lae ja mängi muusikat/efekte nii, et mäng töötaks ka puuduvate failidega."""

    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.sounds = {}
        self.music_started = False
        self.waka_channel = None
        if not self.enabled:
            return

        self.sounds = {
            "waka": self._load_sound("pac-man-waka.mp3", 0.20),
            "power": self._load_sound("eat-dot.mp3", 0.45),
            "eat_ghost": self._load_sound("pac-man-ghost-eaten.mp3", 0.55),
            "death": self._load_sound("pac-man-death.mp3", 0.60),
            "fruit": self._load_sound("eat-dot.mp3", 0.45),
            "level": self._tone(880, 0.14, 0.28),
        }
        self._load_music()

    def _load_sound(self, filename, volume):
        path = SOUND_DIR / filename
        if not path.exists():
            return None
        try:
            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(volume)
            return sound
        except pygame.error:
            return None

    def _tone(self, frequency, duration, volume):
        sample_rate = 44100
        sample_count = int(sample_rate * duration)
        samples = array("h")
        amplitude = int(32767 * volume)
        for i in range(sample_count):
            phase = i * frequency * 2 * math.pi / sample_rate
            samples.append(int(amplitude * math.sin(phase)))
        try:
            return pygame.mixer.Sound(buffer=samples.tobytes())
        except pygame.error:
            return None

    def _load_music(self):
        path = SOUND_DIR / "music.mp3"
        if not path.exists():
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(0.24)
        except pygame.error:
            pass

    def start_music(self):
        if not self.enabled or self.music_started:
            return
        try:
            pygame.mixer.music.play(-1)
            self.music_started = True
        except pygame.error:
            pass

    def update_waka(self, active):
        if not self.enabled:
            return

        sound = self.sounds.get("waka")
        if sound is None:
            return

        if active:
            if self.waka_channel is None or not self.waka_channel.get_busy():
                self.waka_channel = sound.play(loops=-1)
        elif self.waka_channel is not None:
            self.waka_channel.stop()
            self.waka_channel = None

    def play(self, name):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        sound.play()


class Game:
    """Peamine mängukontroller: olek, režiimid, sisend, punktiarvestus ja joonistamine."""

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("PAC-MAN arvestustöö")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("couriernew", 24, bold=True)
        self.font_mid = pygame.font.SysFont("couriernew", 18, bold=True)
        self.font_small = pygame.font.SysFont("couriernew", 15)
        self.high_score = 0
        self.mode = "classic"
        self.sound = SoundManager()
        self.sound.start_music()
        self.new_game("classic")
        self.state = "menu"

    def update_high_score(self):
        """Jälgi parimat tulemust ainult praeguse programmi jooksutamise ajal."""
        if self.score > self.high_score:
            self.high_score = self.score

    def new_game(self, mode=None):
        if mode is not None:
            self.mode = mode

        config = MODES[self.mode]
        self.orig_grid = build_map(config["map"])
        self.grid = [row[:] for row in self.orig_grid]
        self.total_dots = sum(tile in (DOT, POWER) for row in self.grid for tile in row)
        self.dots_eaten = 0
        self.score = 0
        self.lives = 3
        self.level = 1
        self.state = "playing"
        self.state_timer = 0
        self.ghost_score_mult = 1
        self.fruit = BonusFruit()
        self.fruit_spawned_at = set()

        self.pacman = Pacman(
            self.grid,
            config["player_start"],
            config["pacman_speed"],
        )

        # Iga mängukaart kasutab oma kummitusmaja koordinaate ja väljumislahtrit.
        ghost_homes = config["ghost_homes"]
        ghost_exit = config["ghost_exit_cell"]

        self.ghosts = []
        for i in range(config["ghost_count"]):
            ghost = Ghost(
                self.grid,
                i,
                ghost_homes[i],
                ghost_exit,
                config["ghost_speed"],
            )
            ghost.ai_mode = config["ghost_ai"]
            self.ghosts.append(ghost)

    def reset_positions(self):
        self.pacman.reset()
        for ghost in self.ghosts:
            ghost.reset()
        self.state = "playing"
        self.state_timer = 0
        self.ghost_score_mult = 1

    def next_level(self):
        self.level += 1
        self.grid = [row[:] for row in self.orig_grid]
        self.dots_eaten = 0
        self.total_dots = sum(tile in (DOT, POWER) for row in self.grid for tile in row)
        self.fruit = BonusFruit()
        self.fruit_spawned_at = set()
        self.reset_positions()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if self.state == "menu":
                if event.key == pygame.K_1:
                    self.new_game("classic")
                elif event.key == pygame.K_2:
                    self.new_game("beginner")
                elif event.key == pygame.K_r:
                    self.new_game(self.mode)
                continue

            if event.key == pygame.K_m:
                self.state = "menu"
                continue
            if event.key == pygame.K_r:
                self.new_game(self.mode)
                continue
            if event.key == pygame.K_p:
                if self.state == "playing":
                    self.state = "paused"
                elif self.state == "paused":
                    self.state = "playing"
                continue

            if self.state == "playing":
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.pacman.set_dir(UP)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.pacman.set_dir(DOWN)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.pacman.set_dir(LEFT)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.pacman.set_dir(RIGHT)

    def collect_current_tile(self):
        gx, gy = self.pacman.gx, self.pacman.gy
        tile = self.grid[gy][gx]
        if tile == DOT:
            self.grid[gy][gx] = EMPTY
            self.score += 10
            self.dots_eaten += 1
        elif tile == POWER:
            self.grid[gy][gx] = EMPTY
            self.score += 50
            self.dots_eaten += 1
            self.sound.play("power")
            for ghost in self.ghosts:
                ghost.frighten()
            self.ghost_score_mult = 1

    def update_bonus_fruit(self):
        for threshold in (0.35, 0.70):
            required = int(self.total_dots * threshold)
            if self.dots_eaten >= required and required not in self.fruit_spawned_at:
                self.fruit.spawn()
                self.fruit_spawned_at.add(required)

        self.fruit.update()
        if self.fruit.active:
            dist = abs(self.fruit.px - self.pacman.px) + abs(self.fruit.py - self.pacman.py)
            if dist < CELL:
                self.score += 100
                self.fruit.active = False
                self.sound.play("fruit")

    def check_ghost_collisions(self):
        for ghost in self.ghosts:
            dist = abs(ghost.px - self.pacman.px) + abs(ghost.py - self.pacman.py)
            if dist >= CELL - 2:
                continue

            if ghost.fright > 0:
                ghost.eat()
                self.score += 200 * self.ghost_score_mult
                self.ghost_score_mult *= 2
                self.sound.play("eat_ghost")
            elif not ghost.eaten:
                self.pacman.alive = False
                self.lives -= 1
                self.state = "dead"
                self.state_timer = 0
                self.sound.play("death")
                return

    def update(self):
        self.sound.update_waka(self.state == "playing")

        if self.state == "menu":
            return

        if self.state != "playing":
            self.state_timer += 1
            if self.state == "dead" and self.state_timer > 90:
                if self.lives <= 0:
                    self.state = "gameover"
                else:
                    self.reset_positions()
            elif self.state == "win" and self.state_timer > 120:
                self.next_level()
            return

        self.pacman.update()
        for ghost in self.ghosts:
            ghost.update(self.pacman)

        self.collect_current_tile()
        self.update_bonus_fruit()
        self.check_ghost_collisions()
        self.update_high_score()

        if self.dots_eaten >= self.total_dots:
            self.state = "win"
            self.state_timer = 0
            self.sound.play("level")

    def draw_maze(self):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                rx, ry = x * CELL, y * CELL
                if tile == WALL:
                    pygame.draw.rect(self.screen, DKBLUE, (rx, ry, CELL, CELL))
                    pygame.draw.rect(self.screen, BLUE, (rx, ry, CELL, CELL), 2)
                elif tile == DOT:
                    pygame.draw.circle(self.screen, WHITE, (rx + CELL // 2, ry + CELL // 2), 2)
                elif tile == POWER:
                    pulse = 5 + int(2 * abs(pygame.math.Vector2(1, 0).rotate(
                        pygame.time.get_ticks() / 10
                    ).x))
                    pygame.draw.circle(self.screen, YELLOW, (rx + CELL // 2, ry + CELL // 2), pulse)
                elif tile == GATE:
                    pygame.draw.rect(self.screen, PINK, (rx + 2, ry + CELL // 2 - 2, CELL - 4, 4))

    def draw_hud(self):
        y0 = ROWS * CELL + 6
        score_text = self.font_mid.render(f"SCORE {self.score:06d}", True, WHITE)
        high_text = self.font_small.render(f"HI {self.high_score:06d}", True, YELLOW)
        mode_text = self.font_small.render(MODES[self.mode]["title"], True, CYAN)
        level_text = self.font_small.render(f"LVL {self.level}", True, WHITE)

        self.screen.blit(score_text, (10, y0))
        self.screen.blit(high_text, (10, y0 + 24))
        self.screen.blit(mode_text, (W // 2 - mode_text.get_width() // 2, y0 + 4))
        self.screen.blit(level_text, (W // 2 - level_text.get_width() // 2, y0 + 28))

        for i in range(self.lives):
            cx = W - 20 - i * 22
            pygame.draw.circle(self.screen, YELLOW, (cx, y0 + 16), 8)
            pygame.draw.polygon(self.screen, BLACK, [(cx, y0 + 16), (cx + 9, y0 + 11), (cx + 9, y0 + 21)])

    def draw_overlay(self, text, sub=""):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.screen.blit(overlay, (0, 0))

        title = self.font_big.render(text, True, YELLOW)
        self.screen.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 36))

        if sub:
            subtitle = self.font_small.render(sub, True, WHITE)
            self.screen.blit(subtitle, (W // 2 - subtitle.get_width() // 2, H // 2 + 4))

    def draw_menu(self):
        self.screen.fill(BLACK)
        self.draw_maze()
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        title = self.font_big.render("PAC-MAN", True, YELLOW)
        self.screen.blit(title, (W // 2 - title.get_width() // 2, 130))

        lines = [
            "1 - Klassikaline režiim",
            "2 - Algaja režiim",
            "Nooled / WASD - liikumine",
            "P paus  R taaskäivitus  M menüü",
        ]
        y = 190
        for line in lines:
            text = self.font_small.render(line, True, WHITE)
            self.screen.blit(text, (W // 2 - text.get_width() // 2, y))
            y += 28

        info = self.font_small.render(MODES[self.mode]["info"], True, CYAN)
        self.screen.blit(info, (W // 2 - info.get_width() // 2, y + 8))
        pygame.display.flip()

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
            return

        self.screen.fill(BLACK)
        self.draw_maze()
        self.fruit.draw(self.screen)
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        self.pacman.draw(self.screen)
        self.draw_hud()

        if self.state == "paused":
            self.draw_overlay("PAUS", "Jätkamiseks vajuta P")
        elif self.state == "dead":
            self.draw_overlay("KAOTASID ÜHE ELU", f"Elusid järel: {self.lives}")
        elif self.state == "win":
            self.draw_overlay(f"TASE {self.level} LÄBITUD", "Järgmine tase algab varsti")
        elif self.state == "gameover":
            self.draw_overlay("MÄNG LÄBI", f"Lõpptulemus: {self.score}   R taaskäivitamiseks")

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
