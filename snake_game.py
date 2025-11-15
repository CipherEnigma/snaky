"""
Advanced Snake Game (Pygame)

Features in this version:
- Configurable N x N grid (choose on start screen or via --grid argument)
- Wrap-around edges: the snake exits one side and appears on the opposite side
- Polished UI: Start screen with grid-size chooser, highscore display, pause, restart
- Smooth cell scaling so window fits typical displays; optional fixed cell size via --cell
- Visual polish: subtle background gradient, semi-transparent HUD, animated start logo
- Keyboard controls: Arrow keys to move, SPACE to start, P to pause, R to restart, G to toggle grid lines
- Highscore saved to highscore.txt
- Clean, modular Python code with functions and comments for easy teamwork

How to run:
1) Install pygame: pip install pygame
2) Save as snake_game.py (it's in the canvas)
3) Run: python snake_game.py
   or: python snake_game.py --grid 24

Team-friendly notes:
- The code is split into well-named functions so team members can work on UI, game logic, persistence, and assets independently.
- See the top of the file for suggestions which functions to modify for UI/visuals/audio/controls.

"""

import pygame
import random
import os
import argparse
import math

# --------------------- Configuration & Arguments ---------------------
parser = argparse.ArgumentParser(description='Advanced Snake game with NxN grid and wrap-around')
parser.add_argument('--grid', type=int, default=None, help='Grid size N (NxN). If omitted, choose on start screen.')
parser.add_argument('--cell', type=int, default=None, help='Optional: fixed cell size in pixels (overrides automatic sizing)')
args = parser.parse_args()

# sensible minimum / maximum grid
MIN_GRID = 6
MAX_GRID = 60

# Highscore file
HIGHSCORE_FILE = 'highscore.txt'

# initial move delay (ms)
MOVE_DELAY_INIT = 200

# --------------------- Utility: highscore persistence ---------------------

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0


def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            f.write(str(score))
    except Exception:
        pass

# --------------------- Game logic helpers ---------------------

def clamp_grid(n):
    return max(MIN_GRID, min(MAX_GRID, n))


def generate_food(snake, GRID):
    # positions are 1-based (1..GRID)
    while True:
        x = random.randint(1, GRID)
        y = random.randint(1, GRID)
        pos = (x, y)
        if pos not in snake:
            return pos


def decrease_delay(delay):
    # match JS logic: reduce delay based on thresholds
    if delay > 150:
        return delay - 5
    elif delay > 100:
        return delay - 3
    elif delay > 50:
        return delay - 2
    elif delay > 25:
        return delay - 1
    return delay

# --------------------- Visual helpers ---------------------

def draw_text(surface, text, font, color, center):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    surface.blit(surf, rect)


def fill_vertical_gradient(surface, top_color, bottom_color):
    """Fill surface with a vertical gradient (top->bottom)."""
    height = surface.get_height()
    for y in range(height):
        ratio = y / (height - 1)
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))

# --------------------- Main Game Class (group responsibilities) ---------------------
class SnakeGame:
    def __init__(self, GRID=None, CELL_SIZE=None):
        # determine grid size (CLI override, otherwise choose on start screen)
        if GRID is None and args.grid is not None:
            GRID = args.grid
        self.GRID = clamp_grid(GRID or 20)

        # compute cell size to keep a reasonable window size (unless overridden)
        if CELL_SIZE is None and args.cell and args.cell > 4:
            CELL_SIZE = args.cell
        if CELL_SIZE is None:
            CELL_SIZE = max(12, min(36, 720 // self.GRID))

        self.CELL = CELL_SIZE
        self.WIDTH = self.GRID * self.CELL
        self.HEIGHT = self.GRID * self.CELL + 56  # extra HUD area

        # Pygame init
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Snake — Advanced')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Segoe UI', 18)
        self.bigfont = pygame.font.SysFont('Segoe UI', 28, bold=True)

        # Game state
        self.start_x = max(1, self.GRID // 2)
        self.start_y = max(1, self.GRID // 2)
        self.snake = [(self.start_x, self.start_y)]
        self.direction = 'right'
        self.food = generate_food(self.snake, self.GRID)
        self.move_delay = MOVE_DELAY_INIT
        self.last_move_time = 0
        self.started = False
        self.paused = False
        self.show_grid = False
        self.highscore = load_highscore()
        self.running = True

        # UI state (start screen selection)
        self.on_start_screen = True
        self.pending_grid_choice = self.GRID

        # animation / polish
        self.logo_pulse = 0.0

    # --------------------- Game helpers ---------------------
    def wrap_position(self, x, y):
        # wrap-around edges: result in 1..GRID
        x = ((x - 1) % self.GRID) + 1
        y = ((y - 1) % self.GRID) + 1
        return x, y

    def reset_game(self):
        curr = len(self.snake) - 1
        if curr > self.highscore:
            self.highscore = curr
            save_highscore(self.highscore)
        self.snake = [(self.start_x, self.start_y)]
        self.direction = 'right'
        self.food = generate_food(self.snake, self.GRID)
        self.move_delay = MOVE_DELAY_INIT
        self.started = False
        self.paused = False

    # --------------------- Input handling ---------------------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if self.on_start_screen:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # start game with selected grid
                    self.apply_grid_choice()
                    self.started = True
                    self.on_start_screen = False
                    self.last_move_time = pygame.time.get_ticks()
                elif event.key == pygame.K_UP:
                    self.pending_grid_choice = clamp_grid(self.pending_grid_choice + 1)
                elif event.key == pygame.K_DOWN:
                    self.pending_grid_choice = clamp_grid(self.pending_grid_choice - 1)
            else:
                if event.key == pygame.K_SPACE:
                    if not self.started:
                        self.started = True
                        self.last_move_time = pygame.time.get_ticks()
                elif event.key == pygame.K_p:
                    if self.started:
                        self.paused = not self.paused
                elif event.key == pygame.K_r:
                    # restart
                    self.reset_game()
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_UP:
                    if self.direction != 'down':
                        self.direction = 'up'
                elif event.key == pygame.K_DOWN:
                    if self.direction != 'up':
                        self.direction = 'down'
                elif event.key == pygame.K_LEFT:
                    if self.direction != 'right':
                        self.direction = 'left'
                elif event.key == pygame.K_RIGHT:
                    if self.direction != 'left':
                        self.direction = 'right'

    def apply_grid_choice(self):
        # apply pending grid choice (re-init sizes, state)
        self.GRID = clamp_grid(self.pending_grid_choice)
        # recompute cell size to fit
        self.CELL = max(12, min(36, 720 // self.GRID))
        self.WIDTH = self.GRID * self.CELL
        self.HEIGHT = self.GRID * self.CELL + 56
        # recreate screen so size updates
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.start_x = max(1, self.GRID // 2)
        self.start_y = max(1, self.GRID // 2)
        self.snake = [(self.start_x, self.start_y)]
        self.food = generate_food(self.snake, self.GRID)

    # --------------------- Movement / Update ---------------------
    def update(self):
        if not self.started or self.paused:
            return
        now = pygame.time.get_ticks()
        if now - self.last_move_time >= self.move_delay:
            self.last_move_time = now
            head_x, head_y = self.snake[0]
            if self.direction == 'up':
                head_y -= 1
            elif self.direction == 'down':
                head_y += 1
            elif self.direction == 'left':
                head_x -= 1
            elif self.direction == 'right':
                head_x += 1

            # wrap-around behavior
            head_x, head_y = self.wrap_position(head_x, head_y)
            new_head = (head_x, head_y)
            self.snake.insert(0, new_head)

            # eat food
            if new_head == self.food:
                self.food = generate_food(self.snake, self.GRID)
                self.move_delay = decrease_delay(self.move_delay)
            else:
                self.snake.pop()

            # self-collision
            for i in range(1, len(self.snake)):
                if self.snake[i] == self.snake[0]:
                    # if snake hits itself, reset
                    self.reset_game()
                    break

    # --------------------- Drawing ---------------------
    def draw_cell(self, pos, color, border_radius=2):
        x, y = pos
        rect = pygame.Rect((x - 1) * self.CELL, (y - 1) * self.CELL, self.CELL, self.CELL)
        # draw rounded-ish by drawing a smaller rect with alpha
        pygame.draw.rect(self.screen, color, rect, border_radius=0)

    def draw_hud(self):
        # semi-transparent HUD background
        hud_rect = pygame.Surface((self.WIDTH, 56), pygame.SRCALPHA)
        hud_rect.fill((10, 10, 10, 180))
        self.screen.blit(hud_rect, (0, self.HEIGHT - 56))

        score = len(self.snake) - 1
        draw_text(self.screen, f'Score: {str(score).zfill(3)}', self.bigfont, (230, 230, 230), (100, self.HEIGHT - 28))
        draw_text(self.screen, f'Highscore: {str(self.highscore).zfill(3)}', self.font, (200, 200, 200), (100, self.HEIGHT - 10))

        # controls
        draw_text(self.screen, 'SPACE:start  P:pause  R:restart  G:grid', self.font, (200, 200, 200), (self.WIDTH - 240, self.HEIGHT - 28))
        draw_text(self.screen, f'Grid: {self.GRID}  Delay: {self.move_delay}ms', self.font, (200, 200, 200), (self.WIDTH - 240, self.HEIGHT - 10))

    def draw(self):
        # background gradient
        fill_vertical_gradient(self.screen, (8, 10, 30), (18, 30, 60))

        # optional grid lines
        if self.show_grid:
            for gx in range(self.GRID + 1):
                x = gx * self.CELL
                pygame.draw.line(self.screen, (30, 30, 50), (x, 0), (x, self.GRID * self.CELL))
            for gy in range(self.GRID + 1):
                y = gy * self.CELL
                pygame.draw.line(self.screen, (30, 30, 50), (0, y), (self.GRID * self.CELL, y))

        # draw food (visible only after start to mimic JS)
        if self.started:
            self.draw_cell(self.food, (220, 80, 80))

        # draw snake body with subtle shading
        for i, seg in enumerate(self.snake):
            # head brighter
            shade = 200 - min(150, i * 6)
            color = (0, shade, 0) if i == 0 else (0, 150 - min(120, i * 3), 0)
            self.draw_cell(seg, color)

        # HUD
        self.draw_hud()

        # if on start screen overlay
        if self.on_start_screen:
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))
            # animated logo (pulse)
            self.logo_pulse += 0.02
            pulse = 1.0 + 0.05 * math.sin(self.logo_pulse * 2.0)
            title = self.bigfont.render('Snake — Advanced', True, (255, 255, 255))
            trect = title.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 60))
            self.screen.blit(title, trect)

            info = f'Choose grid (Up/Down): {self.pending_grid_choice}  Press Enter/Space to start'
            draw_text(self.screen, info, self.font, (230, 230, 230), (self.WIDTH // 2, self.HEIGHT // 2))
            draw_text(self.screen, f'Highscore: {str(self.highscore).zfill(3)}', self.font, (200, 200, 200), (self.WIDTH // 2, self.HEIGHT // 2 + 28))

    # --------------------- Main loop ---------------------
    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            if not self.on_start_screen:
                self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

# --------------------- Entrypoint ---------------------

def main():
    # If user supplied CLI grid, use it; otherwise start screen will ask
    initial_grid = None
    if args.grid is not None:
        initial_grid = clamp_grid(args.grid)
    game = SnakeGame(GRID=initial_grid)
    game.run()

if __name__ == '__main__':
    main()
