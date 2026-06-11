"""
PAC-MAN - Python / Pygame
Run:  python pacman.py
Requires: pip install pygame
Controls: Arrow keys or WASD  |  P = pause  |  R = restart  |  ESC = quit
"""

import pygame
import sys
import random
from collections import deque

# ─── Constants ────────────────────────────────────────────────────────────────
CELL   = 24          # pixels per grid cell
COLS   = 21
ROWS   = 23
W      = COLS * CELL
H      = ROWS * CELL + 60   # extra bar for score/lives

FPS    = 60

# Colours
BLACK  = (  0,   0,   0)
BLUE   = (  0,   0, 180)
WHITE  = (255, 255, 255)
YELLOW = (255, 220,   0)
RED    = (220,   0,   0)
PINK   = (255, 180, 200)
CYAN   = (  0, 220, 220)
ORANGE = (255, 160,   0)
DKBLUE = (  0,   0,  80)
DGRAY  = ( 40,  40,  40)
LBLUE  = (100, 100, 255)

# Tile types
WALL = 0
DOT  = 1
EMPTY= 2
POWER= 3
GATE = 4   # ghost-house door

# Direction vectors
UP    = ( 0,-1)
DOWN  = ( 0, 1)
LEFT  = (-1, 0)
RIGHT = ( 1, 0)
DIRS  = [UP, DOWN, LEFT, RIGHT]

# ─── Level layout (21 wide × 23 tall) ────────────────────────────────────────
# W=wall  .=dot  o=power  ' '=empty  G=gate
RAW_MAP = [
    "WWWWWWWWWWWWWWWWWWWWW",
    "W.........W.........W",
    "W.WWW.WWW.W.WWW.WWW.W",
    "Wo................oW",
    "W.WWW.W.WWWWW.W.WWW.W",
    "W.....W.......W.....W",
    "WWWWW.WWWWWWWWW.WWWWW",
    "    W.W       W.W    ",
    "WWWWW.W  GGG  W.WWWWW",
    "      .  GGG  .      ",
    "WWWWW.W WWGWW W.WWWWW",
    "    W.          W    ",
    "WWWWW.WWWWWWWWW.WWWWW",
    "W.........W.........W",
    "W.WWW.WWW.W.WWW.WWW.W",
    "Wo....W.......W....oW",
    "WWW.W.W.WWWWW.W.W.WWW",
    "W.....W.......W.....W",
    "W.WWWWWWW.W.WWWWWWW.W",
    "W...................W",
    "W.WWW.WWW.W.WWW.WWW.W",
    "W.........W.........W",
    "WWWWWWWWWWWWWWWWWWWWW",
]

# ─── Map builder ──────────────────────────────────────────────────────────────
def build_map():
    """Convert RAW_MAP strings into a 2-D integer grid."""
    grid = []
    for raw in RAW_MAP:
        row = []
        for ch in raw:
            if   ch == 'W': row.append(WALL)
            elif ch == '.': row.append(DOT)
            elif ch == 'o': row.append(POWER)
            elif ch == 'G': row.append(GATE)
            else:           row.append(EMPTY)
        # Pad / trim to COLS
        while len(row) < COLS: row.append(EMPTY)
        row = row[:COLS]
        grid.append(row)
    while len(grid) < ROWS: grid.append([EMPTY]*COLS)
    return grid

# ─── BFS pathfinding (for ghosts) ────────────────────────────────────────────
def bfs(grid, start, goal, allow_gate=False):
    """Return next step direction from start toward goal, or None."""
    sx, sy = start
    gx, gy = goal
    if (sx, sy) == (gx, gy):
        return None
    visited = {(sx, sy)}
    queue   = deque()
    for d in DIRS:
        nx, ny = sx+d[0], sy+d[1]
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            t = grid[ny][nx]
            if t != WALL and (allow_gate or t != GATE):
                queue.append((nx, ny, d))
                visited.add((nx, ny))
    while queue:
        cx, cy, first_dir = queue.popleft()
        if (cx, cy) == (gx, gy):
            return first_dir
        for d in DIRS:
            nx, ny = cx+d[0], cy+d[1]
            if 0 <= nx < COLS and 0 <= ny < ROWS and (nx,ny) not in visited:
                t = grid[ny][nx]
                if t != WALL and (allow_gate or t != GATE):
                    visited.add((nx, ny))
                    queue.append((nx, ny, d))
    return None

# ─── Pacman ────────────────────────────────────────────────────────────────────
class Pacman:
    SPEED = 3  # pixels per frame (must divide CELL)

    def __init__(self, grid):
        self.grid   = grid
        self.reset()

    def reset(self):
        self.px      = 10 * CELL + CELL//2   # pixel-centre
        self.py      = 17 * CELL + CELL//2
        self.dir     = RIGHT
        self.next_dir= RIGHT
        self.alive   = True
        self.mouth   = 0          # animation angle
        self.mdir    = 1

    # grid cell the centre sits in
    @property
    def gx(self): return self.px // CELL
    @property
    def gy(self): return self.py // CELL

    def set_dir(self, d):
        self.next_dir = d

    def _can_move(self, dx, dy, speed=None):
        sp = speed or self.SPEED
        nx = self.px + dx * sp
        ny = self.py + dy * sp
        # Check all four corners of a (CELL-4)×(CELL-4) hitbox
        r = CELL//2 - 2
        for cx, cy in [(nx-r, ny-r),(nx+r,ny-r),(nx-r,ny+r),(nx+r,ny+r)]:
            gx, gy = cx // CELL, cy // CELL
            if not (0 <= gx < COLS and 0 <= gy < ROWS):
                return False
            if self.grid[gy][gx] == WALL:
                return False
        return True

    def _align(self, axis):
        """Snap position to grid on the given axis ('x' or 'y')."""
        if axis == 'x':
            self.px = (self.px // CELL) * CELL + CELL//2
        else:
            self.py = (self.py // CELL) * CELL + CELL//2

    def update(self):
        if not self.alive:
            return

        # Try to switch to next_dir when aligned
        ndx, ndy = self.next_dir
        dx,  dy  = self.dir
        aligned_x = abs(self.px % CELL - CELL//2) < self.SPEED + 1
        aligned_y = abs(self.py % CELL - CELL//2) < self.SPEED + 1

        if self.next_dir != self.dir:
            if aligned_x and aligned_y:
                if self._can_move(ndx, ndy):
                    if ndx != 0: self._align('y')
                    if ndy != 0: self._align('x')
                    self.dir = self.next_dir
                    dx, dy = ndx, ndy

        # Move in current dir
        if self._can_move(dx, dy):
            self.px += dx * self.SPEED
            self.py += dy * self.SPEED
        else:
            # Align to grid on collision
            if dx != 0: self._align('y')
            if dy != 0: self._align('x')

        # Wrap-around tunnel (rows 9-15 left/right edges)
        if self.px < 0:         self.px = W - CELL//2
        if self.px >= W:        self.px = CELL//2

        # Mouth animation
        self.mouth += 4 * self.mdir
        if self.mouth >= 40: self.mdir = -1
        if self.mouth <= 0:  self.mdir =  1

    def draw(self, surf):
        if not self.alive:
            return
        cx, cy = self.px, self.py
        angle_map = {RIGHT:0, LEFT:180, UP:90, DOWN:270}
        ang = angle_map.get(self.dir, 0)
        r = CELL//2 - 1
        # Body
        rect = pygame.Rect(cx-r, cy-r, r*2, r*2)
        start_a = ang + self.mouth
        end_a   = ang + 360 - self.mouth
        pygame.draw.circle(surf, YELLOW, (cx, cy), r)
        # Draw "mouth" as black pie
        if self.mouth > 2:
            points = [(cx, cy)]
            for a in range(start_a, end_a, 5):
                rad = pygame.math.Vector2(r, 0).rotate(-a)
                points.append((cx + int(rad.x), cy + int(rad.y)))
            points.append((cx, cy))
            if len(points) > 2:
                pygame.draw.polygon(surf, BLACK, points)
        # Eye
        ex = int(cx + r*0.4 * pygame.math.Vector2(0,-1).rotate(-ang).x
                    - r*0.3 * pygame.math.Vector2(1, 0).rotate(-ang).x)
        ey = int(cy + r*0.4 * pygame.math.Vector2(0,-1).rotate(-ang).y
                    - r*0.3 * pygame.math.Vector2(1, 0).rotate(-ang).y)
        pygame.draw.circle(surf, BLACK, (ex, ey), 2)

# ─── Ghost ────────────────────────────────────────────────────────────────────
class Ghost:
    SPEED       = 2
    FRIGHT_TIME = 8 * FPS   # frames of fright
    SCATTER_CORNERS = [(0,0),(COLS-1,0),(0,ROWS-1),(COLS-1,ROWS-1)]

    def __init__(self, grid, gid, home):
        self.grid   = grid
        self.gid    = gid
        self.home   = home        # (gx,gy) pixel-centre spawn
        self.colour = [RED, PINK, CYAN, ORANGE][gid]
        self.scatter_target = self.SCATTER_CORNERS[gid]
        self.reset()

    def reset(self):
        self.px, self.py = self.home
        self.dir         = UP
        self.fright      = 0      # frames remaining in fright mode
        self.eaten       = False
        self.in_house    = True
        self.exit_timer  = gid_exit_delay(self.gid)   # frames before leaving house

    @property
    def gx(self): return self.px // CELL
    @property
    def gy(self): return self.py // CELL

    def frighten(self):
        if not self.eaten:
            self.fright = self.FRIGHT_TIME

    def eat(self):
        self.eaten  = True
        self.fright = 0

    def _choose_dir(self, target_gx, target_gy):
        """BFS toward target, avoid reversing."""
        rdx, rdy = -self.dir[0], -self.dir[1]   # reverse
        best = bfs(self.grid, (self.gx, self.gy), (target_gx, target_gy),
                   allow_gate=self.eaten)
        if best and best != (rdx, rdy):
            return best
        # Fallback: any valid non-reverse direction
        for d in DIRS:
            if d == (rdx, rdy): continue
            nx, ny = self.gx+d[0], self.gy+d[1]
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                t = self.grid[ny][nx]
                if t != WALL and t != GATE:
                    return d
        return self.dir

    def update(self, pacman):
        # Exit house
        if self.in_house:
            self.exit_timer -= 1
            if self.exit_timer <= 0:
                self.in_house = False
            else:
                return  # stay put while waiting

        # If eaten → go home
        if self.eaten:
            hx, hy = self.home[0]//CELL, self.home[1]//CELL
            if self.gx == hx and self.gy == hy:
                self.eaten = False
                self.in_house = True
                self.exit_timer = 180
            else:
                d = self._choose_dir(hx, hy)
                self._move(d)
            return

        # Fright mode → random walk
        if self.fright > 0:
            self.fright -= 1
            # Random valid direction each cell-centre
            if abs(self.px % CELL - CELL//2) < self.SPEED+1 and \
               abs(self.py % CELL - CELL//2) < self.SPEED+1:
                options = []
                rdx, rdy = -self.dir[0], -self.dir[1]
                for d in DIRS:
                    if d == (rdx, rdy): continue
                    nx, ny = self.gx+d[0], self.gy+d[1]
                    if 0 <= nx < COLS and 0 <= ny < ROWS:
                        t = self.grid[ny][nx]
                        if t not in (WALL, GATE):
                            options.append(d)
                if options:
                    self.dir = random.choice(options)
            self._move(self.dir)
            return

        # Chase / scatter
        tx, ty = pacman.gx, pacman.gy
        d = self._choose_dir(tx, ty)
        self._move(d)

    def _move(self, d):
        self.dir = d
        nx = self.px + d[0] * self.SPEED
        ny = self.py + d[1] * self.SPEED
        # Wall check
        r = CELL//2 - 2
        blocked = False
        for cx2, cy2 in [(nx-r,ny-r),(nx+r,ny-r),(nx-r,ny+r),(nx+r,ny+r)]:
            gx2, gy2 = cx2//CELL, cy2//CELL
            if not (0<=gx2<COLS and 0<=gy2<ROWS): blocked=True; break
            t = self.grid[gy2][gx2]
            if t == WALL: blocked=True; break
            if t == GATE and not self.eaten: blocked=True; break
        if not blocked:
            self.px, self.py = nx, ny
        # Wrap tunnel
        if self.px < 0:    self.px = W - CELL//2
        if self.px >= W:   self.px = CELL//2

    def draw(self, surf):
        cx, cy = self.px, self.py
        r = CELL//2 - 1

        if self.fright > 0:
            col = LBLUE if self.fright > 2*FPS else \
                  (WHITE if (pygame.time.get_ticks()//300)%2==0 else LBLUE)
        elif self.eaten:
            col = DKBLUE
        else:
            col = self.colour

        # Body – rounded top
        body = pygame.Rect(cx-r, cy-r, r*2, r*2+4)
        pygame.draw.rect(surf, col, body, border_radius=r)
        pygame.draw.rect(surf, col, (cx-r, cy, r*2, r))
        # Wavy bottom
        wave_y = cy + r
        for i in range(3):
            wx = cx - r + i*(r*2//3)
            pygame.draw.circle(surf, col, (wx + r//3, wave_y), r//3)
        # Eyes
        if not self.fright and not self.eaten:
            for ex_off in (-r//3, r//3):
                pygame.draw.circle(surf, WHITE, (cx+ex_off, cy-r//4), r//4)
                dx_off = self.dir[0]*(r//6)
                dy_off = self.dir[1]*(r//6)
                pygame.draw.circle(surf, BLUE,
                    (cx+ex_off+dx_off, cy-r//4+dy_off), r//7)
        elif self.eaten:
            for ex_off in (-r//3, r//3):
                pygame.draw.line(surf, WHITE,
                    (cx+ex_off-r//5, cy-r//4+r//5),
                    (cx+ex_off+r//5, cy-r//4-r//5), 2)

# ─── Helper ───────────────────────────────────────────────────────────────────
def gid_exit_delay(gid):
    return [0, 60, 120, 200][gid]

# ─── Main Game ────────────────────────────────────────────────────────────────
class Game:
    GHOST_HOMES = [
        (10*CELL+CELL//2, 11*CELL+CELL//2),
        ( 9*CELL+CELL//2, 11*CELL+CELL//2),
        (11*CELL+CELL//2, 11*CELL+CELL//2),
        (10*CELL+CELL//2, 13*CELL+CELL//2),
    ]

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("PAC-MAN")
        self.clock  = pygame.time.Clock()
        self.font_big   = pygame.font.SysFont("couriernew", 22, bold=True)
        self.font_small = pygame.font.SysFont("couriernew", 16)
        self.new_game()

    def new_game(self):
        self.orig_grid = build_map()
        self.grid      = [row[:] for row in self.orig_grid]
        self.total_dots= sum(c in (DOT, POWER) for row in self.grid for c in row)
        self.dots_eaten= 0
        self.score     = 0
        self.lives     = 3
        self.level     = 1
        self.state     = "playing"   # playing / dead / win / gameover
        self.state_timer=0
        self.ghost_score_mult = 1
        self.pacman    = Pacman(self.grid)
        self.ghosts    = [Ghost(self.grid, i, self.GHOST_HOMES[i])
                          for i in range(4)]

    def reset_positions(self):
        self.pacman.reset()
        for g in self.ghosts:
            g.reset()
        self.state = "playing"
        self.ghost_score_mult = 1

    # ── Input ─────────────────────────────────────────────────────────────────
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if e.key == pygame.K_r:
                    self.new_game(); return
                if e.key == pygame.K_p:
                    self.state = "paused" if self.state=="playing" else "playing"

                if self.state == "playing":
                    if e.key in (pygame.K_UP,    pygame.K_u): self.pacman.set_dir(UP)
                    if e.key in (pygame.K_DOWN,  pygame.K_d): self.pacman.set_dir(DOWN)
                    if e.key in (pygame.K_LEFT,  pygame.K_l): self.pacman.set_dir(LEFT)
                    if e.key in (pygame.K_RIGHT, pygame.K_r): self.pacman.set_dir(RIGHT)

    # ── Logic ─────────────────────────────────────────────────────────────────
    def update(self):
        if self.state != "playing":
            self.state_timer += 1
            if self.state == "dead":
                if self.state_timer > 90:
                    if self.lives <= 0:
                        self.state = "gameover"
                    else:
                        self.reset_positions()
            if self.state == "win":
                if self.state_timer > 120:
                    self.level += 1
                    self.grid  = [row[:] for row in self.orig_grid]
                    self.dots_eaten = 0
                    self.reset_positions()
            return

        self.pacman.update()
        for g in self.ghosts:
            g.update(self.pacman)

        # Collect dots
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
            for g in self.ghosts:
                g.frighten()
            self.ghost_score_mult = 1

        # Ghost collision
        for g in self.ghosts:
            dist = abs(g.px - self.pacman.px) + abs(g.py - self.pacman.py)
            if dist < CELL - 2:
                if g.fright > 0:
                    g.eat()
                    pts = 200 * self.ghost_score_mult
                    self.score += pts
                    self.ghost_score_mult *= 2
                elif not g.eaten:
                    self.pacman.alive = False
                    self.lives -= 1
                    self.state = "dead"
                    self.state_timer = 0
                    return

        # Win check
        if self.dots_eaten >= self.total_dots:
            self.state = "win"
            self.state_timer = 0

    # ── Drawing ───────────────────────────────────────────────────────────────
    def draw_maze(self):
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                rx, ry = x*CELL, y*CELL
                if tile == WALL:
                    pygame.draw.rect(self.screen, DKBLUE, (rx,ry,CELL,CELL))
                    pygame.draw.rect(self.screen, BLUE,   (rx,ry,CELL,CELL), 2)
                elif tile == DOT:
                    pygame.draw.circle(self.screen, WHITE,
                        (rx+CELL//2, ry+CELL//2), 2)
                elif tile == POWER:
                    r2 = 5 + int(3*abs(pygame.math.Vector2(1,0).rotate(
                        pygame.time.get_ticks()/10).x))
                    pygame.draw.circle(self.screen, YELLOW,
                        (rx+CELL//2, ry+CELL//2), r2)
                elif tile == GATE:
                    pygame.draw.rect(self.screen, PINK,
                        (rx+2, ry+CELL//2-2, CELL-4, 4))

    def draw_hud(self):
        y0 = ROWS * CELL + 6
        # Score
        surf = self.font_big.render(f"SCORE  {self.score:06d}", True, WHITE)
        self.screen.blit(surf, (10, y0))
        # Level
        surf2 = self.font_small.render(f"LVL {self.level}", True, YELLOW)
        self.screen.blit(surf2, (W//2 - 30, y0+4))
        # Lives (draw mini pac-mans)
        for i in range(self.lives):
            cx = W - 20 - i*22
            pygame.draw.circle(self.screen, YELLOW, (cx, y0+10), 8)
            pygame.draw.polygon(self.screen, BLACK,
                [(cx,y0+10),(cx+9,y0+5),(cx+9,y0+15)])

    def draw_overlay(self, text, sub=""):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        self.screen.blit(overlay, (0,0))
        t  = self.font_big.render(text, True, YELLOW)
        self.screen.blit(t, (W//2 - t.get_width()//2, H//2 - 30))
        if sub:
            s = self.font_small.render(sub, True, WHITE)
            self.screen.blit(s, (W//2 - s.get_width()//2, H//2 + 10))

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_maze()
        for g in self.ghosts:
            g.draw(self.screen)
        self.pacman.draw(self.screen)
        self.draw_hud()

        if self.state == "paused":
            self.draw_overlay("PAUSED", "P to resume")
        elif self.state == "dead":
            self.draw_overlay("OUCH!", f"Lives left: {self.lives}")
        elif self.state == "win":
            self.draw_overlay(f"LEVEL {self.level} CLEAR!", "Get ready…")
        elif self.state == "gameover":
            self.draw_overlay("GAME OVER", f"Final score: {self.score}   R to restart")

        pygame.display.flip()

    # ── Run ───────────────────────────────────────────────────────────────────
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        import pygame
    except ImportError:
        print("Pygame not found.  Install it with:  pip install pygame")
        sys.exit(1)

    Game().run()