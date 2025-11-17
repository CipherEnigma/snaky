import pygame
import random
from heapq import heappush, heappop
from typing import List, Tuple
import math

# Initialize Pygame
pygame.init()

# Game constants - FIXED WINDOW SIZE
WINDOW_SIZE = 800  # Fixed 800x800 window
TASKBAR_HEIGHT = 60
HUD_HEIGHT = 80

# Colors - Modern palette
BG_TOP = (15, 20, 40)
BG_BOTTOM = (30, 40, 70)
GRID_LINE = (40, 50, 80)
FOOD_COLOR = (255, 85, 100)
FOOD_GLOW = (255, 120, 130)
SNAKE_HEAD = (50, 220, 150)
SNAKE_BODY = (40, 180, 120)
SNAKE_GLOW = (80, 255, 180)
TEXT_PRIMARY = (240, 245, 255)
TEXT_SECONDARY = (180, 190, 210)
HUD_BG = (20, 25, 45, 220)
ACCENT_COLOR = (100, 150, 255)
HIGHLIGHT_COLOR = (120, 200, 255)

# Initialize the window
window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + HUD_HEIGHT))
pygame.display.set_caption("🐍 Advanced AI Snake")

# Clock and fonts
clock = pygame.time.Clock()
font_small = pygame.font.SysFont('Segoe UI', 18)
font_medium = pygame.font.SysFont('Segoe UI', 24)
font_large = pygame.font.SysFont('Segoe UI', 32, bold=True)
font_title = pygame.font.SysFont('Segoe UI', 48, bold=True)

# Game-over messages
GAME_OVER_MESSAGES = [
    "AI Hit Itself!",
    "Game Over!",
    "The Snake's Journey Ends!",
    "Better Strategy Needed!",
    "Try Again!"
]


def draw_gradient_background(surface, top_color, bottom_color):
    """Draw a smooth vertical gradient background."""
    for y in range(WINDOW_SIZE + HUD_HEIGHT):
        ratio = y / (WINDOW_SIZE + HUD_HEIGHT)
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_SIZE, y))


def draw_text_with_shadow(surface, text, font, color, pos, shadow_offset=2):
    """Draw text with a subtle shadow for better readability."""
    # Shadow
    shadow_surf = font.render(text, True, (0, 0, 0))
    shadow_rect = shadow_surf.get_rect(center=(pos[0] + shadow_offset, pos[1] + shadow_offset))
    surface.blit(shadow_surf, shadow_rect)
    # Main text
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=pos)
    surface.blit(text_surf, text_rect)


def get_grid_size():
    """Get grid size from user with improved UI."""
    input_value = ""
    title_pulse = 0.0

    while True:
        title_pulse += 0.05
        
        # Draw gradient background
        draw_gradient_background(window, BG_TOP, BG_BOTTOM)
        
        # Animated title with pulse effect
        pulse_scale = 1.0 + 0.05 * math.sin(title_pulse)
        title_font = pygame.font.SysFont('Segoe UI', int(52 * pulse_scale), bold=True)
        draw_text_with_shadow(window, "🐍 AI Snake Game", title_font, ACCENT_COLOR, 
                            (WINDOW_SIZE // 2, 150))
        
        # Instructions
        draw_text_with_shadow(window, "Enter Grid Size (N×N)", font_large, TEXT_PRIMARY,
                            (WINDOW_SIZE // 2, 280))
        draw_text_with_shadow(window, "Recommended: 10-40", font_small, TEXT_SECONDARY,
                            (WINDOW_SIZE // 2, 320))
        
        # Input box
        input_box_rect = pygame.Rect(WINDOW_SIZE // 2 - 100, 370, 200, 60)
        pygame.draw.rect(window, (40, 50, 80), input_box_rect, border_radius=10)
        pygame.draw.rect(window, ACCENT_COLOR, input_box_rect, 3, border_radius=10)
        
        # Input text
        if input_value:
            input_surf = font_title.render(input_value, True, SNAKE_HEAD)
        else:
            input_surf = font_medium.render("Type here...", True, TEXT_SECONDARY)
        input_rect = input_surf.get_rect(center=input_box_rect.center)
        window.blit(input_surf, input_rect)
        
        # Press Enter hint
        draw_text_with_shadow(window, "Press ENTER to start", font_small, TEXT_SECONDARY,
                            (WINDOW_SIZE // 2, 480))
        
        pygame.display.update()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_value.isdigit() and 5 <= int(input_value) <= 100:
                        return int(input_value)
                elif event.key == pygame.K_BACKSPACE:
                    input_value = input_value[:-1]
                else:
                    if event.unicode.isdigit() and len(input_value) < 3:
                        input_value += event.unicode


class SnakeGame:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        # Dynamic block size based on grid - smaller blocks for larger grids
        self.block_size = WINDOW_SIZE // grid_size
        self.snake_speed = 8
        self.high_score = 0
        self.food_pulse = 0.0
        self.reset_game()

    def reset_game(self):
        center = self.grid_size // 2
        self.snake = [[center * self.block_size, center * self.block_size]]
        self.direction = "RIGHT"
        self.score = 0
        self.generate_food()
        self.game_close = False

    def generate_food(self):
        while True:
            self.food = [
                random.randrange(0, self.grid_size) * self.block_size,
                random.randrange(0, self.grid_size) * self.block_size,
            ]
            if self.food not in self.snake:
                break

    def manhattan_distance(self, pos1: List[int], pos2: List[int]) -> int:
        x1, y1 = pos1
        x2, y2 = pos2
        
        dx1 = abs(x1 - x2)
        dx2 = WINDOW_SIZE - dx1
        dx = min(dx1, dx2)
        
        dy1 = abs(y1 - y2)
        dy2 = WINDOW_SIZE - dy1
        dy = min(dy1, dy2)
        
        return dx + dy

    def wrap_position(self, pos: List[int]) -> List[int]:
        x, y = pos
        x = (x + WINDOW_SIZE) % WINDOW_SIZE
        y = (y + WINDOW_SIZE) % WINDOW_SIZE
        x = (x // self.block_size) * self.block_size
        y = (y // self.block_size) * self.block_size
        return [x, y]

    def get_neighbors(self, pos: List[int], exclude_body: List[List[int]] = None) -> List[List[int]]:
        neighbors = []
        moves = [(0, -self.block_size), (0, self.block_size), 
                (-self.block_size, 0), (self.block_size, 0)]
        
        if exclude_body is None:
            exclude_body = self.snake[1:]
        
        for dx, dy in moves:
            new_x = pos[0] + dx
            new_y = pos[1] + dy
            new_pos = self.wrap_position([new_x, new_y])
            
            if new_pos not in exclude_body:
                neighbors.append(new_pos)
        
        return neighbors

    def bfs_pathfinding(self, start: List[int], goal: List[int], exclude_body: List[List[int]] = None) -> List[List[int]]:
        """BFS pathfinding - finds shortest path, used for safety checks."""
        from collections import deque
        
        if exclude_body is None:
            exclude_body = self.snake[1:]
        
        queue = deque([tuple(start)])
        came_from = {tuple(start): None}
        
        while queue:
            current = queue.popleft()
            
            if list(current) == goal:
                path = []
                while current is not None:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()
                return path[1:]  # Exclude starting position
            
            for neighbor in self.get_neighbors(list(current), exclude_body):
                neighbor_tuple = tuple(neighbor)
                if neighbor_tuple not in came_from:
                    came_from[neighbor_tuple] = current
                    queue.append(neighbor_tuple)
        
        return []
    
    def is_safe_move(self, path_to_food: List[List[int]]) -> bool:
        """Check if taking path to food will leave escape route (can reach tail)."""
        if not path_to_food:
            return False
        
        # Simulate snake after eating food
        simulated_snake = [path_to_food[-1]] + self.snake  # New head at food position
        simulated_tail = simulated_snake[-1]
        
        # Check if head can reach tail position after eating
        escape_path = self.bfs_pathfinding(
            simulated_snake[0], 
            simulated_tail, 
            exclude_body=simulated_snake[1:-1]
        )
        
        return len(escape_path) > 0
    
    def find_tail_path(self) -> List[List[int]]:
        """Survival mode: chase own tail to buy time."""
        if len(self.snake) < 2:
            return []
        
        tail = self.snake[-1]
        path = self.bfs_pathfinding(self.snake[0], tail)
        return path

    def a_star_pathfinding(self) -> List[List[int]]:
        """Optimized A* with safety check and fallback strategies."""
        start = tuple(self.snake[0])
        goal = tuple(self.food)

        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.manhattan_distance(self.snake[0], self.food)}

        while open_set:
            current = heappop(open_set)[1]

            if current == goal:
                path = []
                while current in came_from:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()
                
                # SAFETY CHECK: Verify path doesn't trap snake
                if self.is_safe_move(path):
                    return path
                else:
                    # Path leads to trap - use tail-following instead
                    tail_path = self.find_tail_path()
                    return tail_path if tail_path else path

            for neighbor in map(tuple, self.get_neighbors(list(current))):
                tentative_g_score = g_score[current] + self.block_size

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    # Add penalty for tight spaces to prefer open areas
                    space_penalty = 0
                    if len(self.get_neighbors(list(neighbor))) < 3:
                        space_penalty = self.block_size * 2
                    f_score[neighbor] = tentative_g_score + self.manhattan_distance(
                        list(neighbor), self.food
                    ) + space_penalty
                    heappush(open_set, (f_score[neighbor], neighbor))

        # No path to food - follow tail for survival
        return self.find_tail_path()

    def update_direction(self, next_pos: List[int]):
        head = self.snake[0]
        x1, y1 = head
        x2, y2 = next_pos
        
        dx1 = x2 - x1
        dx2 = x2 - x1 + WINDOW_SIZE
        dx3 = x2 - x1 - WINDOW_SIZE
        dx = min(dx1, dx2, dx3, key=abs)
        
        dy1 = y2 - y1
        dy2 = y2 - y1 + WINDOW_SIZE
        dy3 = y2 - y1 - WINDOW_SIZE
        dy = min(dy1, dy2, dy3, key=abs)
        
        if abs(dx) > abs(dy):
            self.direction = "LEFT" if dx < 0 else "RIGHT"
        else:
            self.direction = "UP" if dy < 0 else "DOWN"

    def move_snake(self):
        x, y = self.snake[0]
        prev_positions = self.snake.copy()
        
        if self.direction == "UP":
            y -= self.block_size
        elif self.direction == "DOWN":
            y += self.block_size
        elif self.direction == "LEFT":
            x -= self.block_size
        elif self.direction == "RIGHT":
            x += self.block_size
        
        new_head = self.wrap_position([x, y])
        
        if new_head == self.food:
            self.snake.insert(0, new_head)
            self.score += 1
            self.generate_food()
            # Gradual speed increase
            if self.score % 3 == 0 and self.snake_speed < 20:
                self.snake_speed += 1
        else:
            self.snake[0] = new_head
            for i in range(1, len(self.snake)):
                self.snake[i] = prev_positions[i-1]

    def check_collision(self) -> bool:
        head = self.snake[0]
        return head in self.snake[1:]

    def draw_snake(self):
        """Draw snake with glow effect and rounded corners."""
        for idx, segment in enumerate(self.snake):
            if idx == 0:
                # Draw glow around head
                glow_radius = int(self.block_size * 0.7)
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*SNAKE_GLOW, 30), (glow_radius, glow_radius), glow_radius)
                window.blit(glow_surf, (segment[0] + self.block_size // 2 - glow_radius,
                                       segment[1] + self.block_size // 2 - glow_radius))
                
                # Draw head with rounded corners
                head_rect = pygame.Rect(segment[0], segment[1], self.block_size, self.block_size)
                pygame.draw.rect(window, SNAKE_HEAD, head_rect, border_radius=max(4, self.block_size // 5))
            else:
                # Draw body segments
                body_rect = pygame.Rect(segment[0], segment[1], self.block_size, self.block_size)
                # Fade effect for tail
                alpha = max(100, 255 - (idx * 5))
                color = tuple(int(c * alpha / 255) for c in SNAKE_BODY)
                pygame.draw.rect(window, color, body_rect, border_radius=max(3, self.block_size // 6))

    def draw_food(self):
        """Draw food with pulsing glow animation."""
        self.food_pulse += 0.15
        pulse = 1.0 + 0.2 * math.sin(self.food_pulse)
        
        # Outer glow
        glow_size = int(self.block_size * pulse)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*FOOD_GLOW, 40), (glow_size, glow_size), glow_size)
        window.blit(glow_surf, (self.food[0] + self.block_size // 2 - glow_size,
                               self.food[1] + self.block_size // 2 - glow_size))
        
        # Food item
        food_rect = pygame.Rect(self.food[0], self.food[1], self.block_size, self.block_size)
        pygame.draw.rect(window, FOOD_COLOR, food_rect, border_radius=max(4, self.block_size // 4))

    def draw_hud(self):
        """Draw modern HUD with semi-transparent background."""
        # HUD background
        hud_surf = pygame.Surface((WINDOW_SIZE, HUD_HEIGHT), pygame.SRCALPHA)
        hud_surf.fill(HUD_BG)
        window.blit(hud_surf, (0, WINDOW_SIZE))
        
        # Divider line
        pygame.draw.line(window, ACCENT_COLOR, (0, WINDOW_SIZE), (WINDOW_SIZE, WINDOW_SIZE), 2)
        
        # Score on left
        score_text = f"Score: {self.score}"
        draw_text_with_shadow(window, score_text, font_large, TEXT_PRIMARY,
                            (150, WINDOW_SIZE + HUD_HEIGHT // 2), shadow_offset=1)
        
        # High score on right
        high_text = f"Best: {self.high_score}"
        draw_text_with_shadow(window, high_text, font_medium, TEXT_SECONDARY,
                            (WINDOW_SIZE - 150, WINDOW_SIZE + HUD_HEIGHT // 2), shadow_offset=1)
        
        # Grid info center
        grid_info = f"{self.grid_size}×{self.grid_size} | A* + Safety Check"
        draw_text_with_shadow(window, grid_info, font_small, ACCENT_COLOR,
                            (WINDOW_SIZE // 2, WINDOW_SIZE + HUD_HEIGHT // 2 + 20), shadow_offset=1)

    def display_game_over(self):
        """Modern game over screen."""
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE + HUD_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        window.blit(overlay, (0, 0))
        
        random_message = random.choice(GAME_OVER_MESSAGES)
        
        # Game over title
        draw_text_with_shadow(window, random_message, font_title, FOOD_COLOR,
                            (WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 80), shadow_offset=3)
        
        # Score display
        score_text = f"Final Score: {self.score}"
        draw_text_with_shadow(window, score_text, font_large, TEXT_PRIMARY,
                            (WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 10))
        
        # High score
        high_text = f"High Score: {self.high_score}"
        draw_text_with_shadow(window, high_text, font_medium, TEXT_SECONDARY,
                            (WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 30))
        
        # Menu options
        play_text = "Play Again"
        quit_text = "Quit"
        
        selected = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % 2
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % 2
                    elif event.key == pygame.K_RETURN:
                        return selected == 0

            # Redraw overlay
            window.blit(overlay, (0, 0))
            draw_text_with_shadow(window, random_message, font_title, FOOD_COLOR,
                                (WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 80), shadow_offset=3)
            draw_text_with_shadow(window, score_text, font_large, TEXT_PRIMARY,
                                (WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 10))
            draw_text_with_shadow(window, high_text, font_medium, TEXT_SECONDARY,
                                (WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 30))
            
            # Highlight selected option
            play_color = HIGHLIGHT_COLOR if selected == 0 else TEXT_PRIMARY
            quit_color = HIGHLIGHT_COLOR if selected == 1 else TEXT_PRIMARY
            
            draw_text_with_shadow(window, play_text, font_large, play_color,
                                (WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 90))
            draw_text_with_shadow(window, quit_text, font_large, quit_color,
                                (WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 135))

            pygame.display.update()
            clock.tick(30)

    def game_loop(self):
        """Main game loop."""
        path = []
        
        while True:
            while self.game_close:
                if self.display_game_over():
                    self.reset_game()
                    path = []
                else:
                    pygame.quit()
                    quit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            # AI pathfinding
            if not path:
                path = self.a_star_pathfinding()

            if path:
                next_step = path.pop(0)
                self.update_direction(next_step)

            self.move_snake()

            if self.check_collision():
                self.high_score = max(self.high_score, self.score)
                self.game_close = True

            # Draw everything
            draw_gradient_background(window, BG_TOP, BG_BOTTOM)
            
            # Optional: Draw subtle grid lines for smaller blocks
            if self.block_size < 30:
                for i in range(self.grid_size + 1):
                    pos = i * self.block_size
                    pygame.draw.line(window, GRID_LINE, (pos, 0), (pos, WINDOW_SIZE), 1)
                    pygame.draw.line(window, GRID_LINE, (0, pos), (WINDOW_SIZE, pos), 1)
            
            self.draw_food()
            self.draw_snake()
            self.draw_hud()

            pygame.display.update()
            clock.tick(self.snake_speed)


if __name__ == "__main__":
    grid_size = get_grid_size()
    game = SnakeGame(grid_size)
    game.game_loop()
