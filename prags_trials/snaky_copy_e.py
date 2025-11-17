import pygame
import random
from heapq import heappush, heappop
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Game constants  
N = 20  # Default grid size (will be set by user input)
BLOCK_SIZE = 20
WINDOW_WIDTH  = N * BLOCK_SIZE
WINDOW_HEIGHT = N * BLOCK_SIZE
TASKBAR_HEIGHT = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (50, 50, 50)
# Player colors (Cyan/Blue)
PLAYER_HEAD_COLOR = (0, 200, 255)  # Cyan
PLAYER_BODY_COLOR = (50, 150, 255)  # Light blue
# AI colors (Green)
AI_HEAD_COLOR = (0, 200, 0)  # Bright green
AI_BODY_COLOR = (50, 205, 50)  # Lime green
HIGHLIGHT_COLOR = (0, 150, 255)
PATH_COLOR = (100, 150, 255, 100)  # Light blue with transparency
RANDOM_COLORS = [(255, 255, 0), (255, 165, 0), (0, 255, 255), (255, 20, 147), (0, 255, 0)]
BORDER_COLORS = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]

# Initialize the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + TASKBAR_HEIGHT))
pygame.display.set_caption("Human vs AI Snake Battle")

# Clock and fonts
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
title_font = pygame.font.SysFont(None, 60)
game_over_font = pygame.font.SysFont("arial", 50, bold=True)

# Game-over messages
WIN_MESSAGES = [
    "You Win! 🎉",
    "Victory is Yours!",
    "AI Defeated!",
    "Human Supremacy!",
]

LOSE_MESSAGES = [
    "AI Wins! 🤖",
    "Better Luck Next Time!",
    "AI Outsmarted You!",
    "The Machines Rise!",
]

TIE_MESSAGES = [
    "It's a Tie!",
    "Both Defeated!",
    "Draw Game!",
]


def get_grid_size():
    """Get grid size from user."""
    input_value = ""
    prompt_font = pygame.font.SysFont(None, 50)
    
    while True:
        window.fill(BLACK)
        
        prompt = prompt_font.render("Enter Grid Size (N×N):", True, WHITE)
        window.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, 150))
        
        hint = font.render("Recommended: 10-50", True, GRAY)
        window.blit(hint, (WINDOW_WIDTH // 2 - hint.get_width() // 2, 210))
        
        user_text = prompt_font.render(input_value, True, (0, 255, 0))
        window.blit(user_text, (WINDOW_WIDTH // 2 - user_text.get_width() // 2, 280))
        
        instruction = font.render("Press ENTER to continue", True, (150, 150, 150))
        window.blit(instruction, (WINDOW_WIDTH // 2 - instruction.get_width() // 2, 380))
        
        pygame.display.update()
        
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
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                else:
                    if event.unicode.isdigit() and len(input_value) < 3:
                        input_value += event.unicode


def show_instructions():
    """Display instructions before starting the game"""
    instruction_screen = True
    border_offset = 0
    
    while instruction_screen:
        window.fill(BLACK)
        
        # Draw colorful animated border
        border_width = 5
        for i, color in enumerate(BORDER_COLORS):
            offset = (border_offset + i * 20) % (2 * (WINDOW_WIDTH + WINDOW_HEIGHT))
            if offset < WINDOW_WIDTH:
                pygame.draw.rect(window, color, [offset, 0, 20, border_width])
            elif offset < WINDOW_WIDTH + WINDOW_HEIGHT:
                pygame.draw.rect(window, color, [WINDOW_WIDTH - border_width, offset - WINDOW_WIDTH, border_width, 20])
            elif offset < 2 * WINDOW_WIDTH + WINDOW_HEIGHT:
                pygame.draw.rect(window, color, [WINDOW_WIDTH - (offset - WINDOW_WIDTH - WINDOW_HEIGHT), WINDOW_HEIGHT + TASKBAR_HEIGHT - border_width, 20, border_width])
            else:
                pygame.draw.rect(window, color, [0, WINDOW_HEIGHT + TASKBAR_HEIGHT - (offset - 2 * WINDOW_WIDTH - WINDOW_HEIGHT), border_width, 20])
        
        border_offset = (border_offset + 2) % (2 * (WINDOW_WIDTH + WINDOW_HEIGHT))
        
        # Title
        title = title_font.render("Human vs AI Snake", True, (0, 255, 100))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        window.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "How to Play:",
            "",
            "• YOU control the CYAN snake with WASD keys",
            "• AI controls the GREEN snake using A* algorithm",
            "• Blue path shows AI's planned route",
            "• Both snakes compete for the RED food",
            "• First to eat grows longer and faster",
            "• Game ends when a snake:",
            "   - Hits itself",
            "   - Hits the other snake",
            "   - Crashes head-to-head (both die)",
            "",
            "Player Controls:",
            "",
            "• W - Move Up",
            "• A - Move Left", 
            "• S - Move Down",
            "• D - Move Right",
            "• SPACE - Start the game",
            "• ESC - Quit the game",
            "",
            "Press SPACE to start!"
        ]
        
        y_offset = 150
        for line in instructions:
            if line.startswith("•"):
                text = font.render(line, True, WHITE)
            elif line == "How to Play:" or line == "Keyboard Controls:":
                text = font.render(line, True, (255, 200, 0))
            elif line == "Press SPACE to start!":
                text = font.render(line, True, (0, 255, 0))
            else:
                text = font.render(line, True, GRAY if line == "" else WHITE)
            
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            window.blit(text, text_rect)
            y_offset += 35
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    instruction_screen = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
        
        clock.tick(30)


class SnakeGame:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.block_size = BLOCK_SIZE
        self.width = self.grid_size * self.block_size
        self.height = self.grid_size * self.block_size
        self.snake_speed = 10
        self.high_score = 0
        self.border_offset = 0
        self.reset_game()

    def reset_game(self):
        # Player snake (starts left side)
        player_start_x = (self.grid_size // 4) * self.block_size
        player_start_y = (self.grid_size // 2) * self.block_size
        self.player_snake = [[player_start_x, player_start_y]]
        self.player_direction = "RIGHT"
        self.player_alive = True
        self.player_score = 0
        
        # AI snake (starts right side)
        ai_start_x = (3 * self.grid_size // 4) * self.block_size
        ai_start_y = (self.grid_size // 2) * self.block_size
        self.ai_snake = [[ai_start_x, ai_start_y]]
        self.ai_direction = "LEFT"
        self.ai_alive = True
        self.ai_score = 0
        
        self.generate_food()
        self.game_close = False
        self.path = []  # Store the AI's current path
        self.winner = None  # Track who won

    def generate_food(self):
        while True:
            self.food = [
                random.randrange(0, self.grid_size) * self.block_size,
                random.randrange(0, self.grid_size) * self.block_size,
            ]
            if (self.food not in self.player_snake and 
                self.food not in self.ai_snake):
                break

    def manhattan_distance(self, pos1: List[int], pos2: List[int]) -> int:
        x1, y1 = pos1
        x2, y2 = pos2
        
        dx1 = abs(x1 - x2)
        dx2 = self.width - dx1
        dx = min(dx1, dx2)
        
        dy1 = abs(y1 - y2)
        dy2 = self.height - dy1
        dy = min(dy1, dy2)
        
        return dx + dy

    def wrap_position(self, pos: List[int]) -> List[int]:
        x, y = pos
        x = (x + self.width) % self.width
        y = (y + self.height) % self.height
        x = (x // self.block_size) * self.block_size
        y = (y // self.block_size) * self.block_size
        return [x, y]

    def get_neighbors(self, pos: List[int], snake_body: List[List[int]]) -> List[List[int]]:
        neighbors = []
        moves = [(0, -self.block_size), (0, self.block_size), 
                (-self.block_size, 0), (self.block_size, 0)]
        
        for dx, dy in moves:
            new_x = pos[0] + dx
            new_y = pos[1] + dy
            new_pos = self.wrap_position([new_x, new_y])
            
            # Avoid both snakes
            if (new_pos not in snake_body[1:] and 
                new_pos not in self.player_snake):
                neighbors.append(new_pos)
        
        return neighbors

    def a_star_pathfinding(self) -> List[List[int]]:
        """AI pathfinding avoiding both snakes."""
        start = tuple(self.ai_snake[0])
        goal = tuple(self.food)

        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.manhattan_distance(self.ai_snake[0], self.food)}

        while open_set:
            current = heappop(open_set)[1]

            if current == goal:
                path = []
                while current in came_from:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in map(tuple, self.get_neighbors(list(current), self.ai_snake)):
                tentative_g_score = g_score[current] + self.block_size

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.manhattan_distance(
                        list(neighbor), self.food
                    )
                    heappush(open_set, (f_score[neighbor], neighbor))

        return []

    def update_direction(self, next_pos: List[int], is_ai: bool = True):
        """Update direction for AI snake."""
        snake = self.ai_snake if is_ai else self.player_snake
        head = snake[0]
        x1, y1 = head
        x2, y2 = next_pos
        
        dx1 = x2 - x1
        dx2 = x2 - x1 + self.width
        dx3 = x2 - x1 - self.width
        dx = min(dx1, dx2, dx3, key=abs)
        
        dy1 = y2 - y1
        dy2 = y2 - y1 + self.height
        dy3 = y2 - y1 - self.height
        dy = min(dy1, dy2, dy3, key=abs)
        
        if abs(dx) > abs(dy):
            direction = "LEFT" if dx < 0 else "RIGHT"
        else:
            direction = "UP" if dy < 0 else "DOWN"
        
        if is_ai:
            self.ai_direction = direction
        else:
            self.player_direction = direction

    def move_snake(self, is_player: bool):
        """Move either player or AI snake."""
        if is_player:
            if not self.player_alive:
                return
            snake = self.player_snake
            direction = self.player_direction
        else:
            if not self.ai_alive:
                return
            snake = self.ai_snake
            direction = self.ai_direction
            
        x, y = snake[0]
        prev_positions = snake.copy()
        
        if direction == "UP":
            y -= self.block_size
        elif direction == "DOWN":
            y += self.block_size
        elif direction == "LEFT":
            x -= self.block_size
        elif direction == "RIGHT":
            x += self.block_size
        
        new_head = self.wrap_position([x, y])
        
        if new_head == self.food:
            snake.insert(0, new_head)
            if is_player:
                self.player_score += 1
            else:
                self.ai_score += 1
            self.generate_food()
            # Speed up every 3 points
            if (self.player_score + self.ai_score) % 3 == 0:
                self.snake_speed = min(25, self.snake_speed + 1)
        else:
            snake[0] = new_head
            for i in range(1, len(snake)):
                snake[i] = prev_positions[i-1]

    def check_collisions(self):
        """Check all collision scenarios."""
        player_head = self.player_snake[0]
        ai_head = self.ai_snake[0]
        
        player_died = False
        ai_died = False
        
        # Head-to-head collision check first (both die = tie)
        if player_head == ai_head:
            player_died = True
            ai_died = True
            self.winner = "Tie"
        else:
            # Player self-collision
            if player_head in self.player_snake[1:]:
                player_died = True
            
            # AI self-collision
            if ai_head in self.ai_snake[1:]:
                ai_died = True
            
            # Player hits AI body
            if player_head in self.ai_snake[1:]:
                player_died = True
            
            # AI hits player body
            if ai_head in self.player_snake[1:]:
                ai_died = True
            
            # Determine winner based on who died
            if player_died and not ai_died:
                self.winner = "AI"
            elif ai_died and not player_died:
                self.winner = "Player"
            elif player_died and ai_died:
                self.winner = "Tie"
        
        # Update alive status
        if player_died:
            self.player_alive = False
        if ai_died:
            self.ai_alive = False
        
        # Game over if either snake is dead
        if not self.player_alive or not self.ai_alive:
            self.game_close = True

    def draw_colorful_border(self):
        """Draw animated rainbow border"""
        border_width = 8
        for i, color in enumerate(BORDER_COLORS):
            offset = (self.border_offset + i * 30) % (2 * (self.width + self.height))
            
            if offset < self.width:
                pygame.draw.rect(window, color, [offset, TASKBAR_HEIGHT, 25, border_width])
            elif offset < self.width + self.height:
                y_pos = offset - self.width + TASKBAR_HEIGHT
                pygame.draw.rect(window, color, [self.width - border_width, y_pos, border_width, 25])
            elif offset < 2 * self.width + self.height:
                x_pos = self.width - (offset - self.width - self.height)
                pygame.draw.rect(window, color, [x_pos, self.height + TASKBAR_HEIGHT - border_width, 25, border_width])
            else:
                y_pos = self.height + TASKBAR_HEIGHT - (offset - 2 * self.width - self.height)
                pygame.draw.rect(window, color, [0, y_pos, border_width, 25])
        
        self.border_offset = (self.border_offset + 3) % (2 * (self.width + self.height))

    def draw_path(self):
        """Draw the A* path from snake head to food"""
        if self.path:
            # Create a surface with transparency for the path
            path_surface = pygame.Surface((self.block_size, self.block_size))
            path_surface.set_alpha(128)  # Semi-transparent
            path_surface.fill(PATH_COLOR[:3])
            
            for pos in self.path:
                window.blit(path_surface, (pos[0], pos[1] + TASKBAR_HEIGHT))
                # Draw a small circle in the center to make it more visible
                center_x = pos[0] + self.block_size // 2
                center_y = pos[1] + self.block_size // 2 + TASKBAR_HEIGHT
                pygame.draw.circle(window, (150, 200, 255), (center_x, center_y), 3)

    def draw_snake(self, snake: List[List[int]], head_color: tuple, body_color: tuple):
        """Draw a snake with specified colors."""
        for idx, segment in enumerate(snake):
            if idx == 0:
                pygame.draw.rect(
                    window,
                    head_color,
                    [segment[0], segment[1] + TASKBAR_HEIGHT, self.block_size, self.block_size],
                    border_radius=8,
                )
            else:
                pygame.draw.rect(
                    window,
                    body_color,
                    [segment[0], segment[1] + TASKBAR_HEIGHT, self.block_size, self.block_size],
                    border_radius=4,
                )

    def display_game_over(self):
        window.fill(BLACK)
        
        # Determine message based on winner
        if self.winner == "Player":
            random_message = random.choice(WIN_MESSAGES)
            random_color = (0, 255, 100)
        elif self.winner == "AI":
            random_message = random.choice(LOSE_MESSAGES)
            random_color = (255, 100, 100)
        else:  # Tie
            random_message = random.choice(TIE_MESSAGES)
            random_color = (255, 255, 0)

        game_over_text = game_over_font.render(random_message, True, random_color)
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 80))
        window.blit(game_over_text, game_over_rect)

        player_text = font.render(f"Player Score: {self.player_score}", True, PLAYER_HEAD_COLOR)
        player_rect = player_text.get_rect(center=(self.width // 2, self.height // 2 - 10))
        window.blit(player_text, player_rect)

        ai_text = font.render(f"AI Score: {self.ai_score}", True, AI_HEAD_COLOR)
        ai_rect = ai_text.get_rect(center=(self.width // 2, self.height // 2 + 30))
        window.blit(ai_text, ai_rect)

        play_again_text = font.render("Play Again (SPACE)", True, WHITE)
        quit_text = font.render("Quit (ESC)", True, WHITE)
        play_again_rect = play_again_text.get_rect(center=(self.width // 2, self.height // 2 + 100))
        quit_rect = quit_text.get_rect(center=(self.width // 2, self.height // 2 + 140))

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
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return selected == 0
                    elif event.key == pygame.K_ESCAPE:
                        return False

            play_again_color = HIGHLIGHT_COLOR if selected == 0 else WHITE
            quit_color = HIGHLIGHT_COLOR if selected == 1 else WHITE

            play_again_text = font.render("Play Again (SPACE)", True, play_again_color)
            quit_text = font.render("Quit (ESC)", True, quit_color)

            window.fill(BLACK)
            window.blit(game_over_text, game_over_rect)
            window.blit(player_text, player_rect)
            window.blit(ai_text, ai_rect)
            window.blit(play_again_text, play_again_rect)
            window.blit(quit_text, quit_rect)

            pygame.display.update()
            clock.tick(15)

    def game_loop(self):
        while True:
            while self.game_close:
                if self.display_game_over():
                    self.reset_game()
                else:
                    pygame.quit()
                    quit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()
                    # Player controls (WASD)
                    elif event.key == pygame.K_w and self.player_direction != "DOWN":
                        self.player_direction = "UP"
                    elif event.key == pygame.K_s and self.player_direction != "UP":
                        self.player_direction = "DOWN"
                    elif event.key == pygame.K_a and self.player_direction != "RIGHT":
                        self.player_direction = "LEFT"
                    elif event.key == pygame.K_d and self.player_direction != "LEFT":
                        self.player_direction = "RIGHT"

            # AI pathfinding
            if self.ai_alive and not self.path:
                self.path = self.a_star_pathfinding()

            if self.ai_alive and self.path:
                next_step = self.path.pop(0)
                self.update_direction(next_step, is_ai=True)

            # Move both snakes
            self.move_snake(is_player=True)   # Player
            self.move_snake(is_player=False)  # AI

            # Check collisions
            self.check_collisions()

            # Draw everything
            window.fill(BLACK)
            
            # Draw AI path first (so it appears under everything else)
            self.draw_path()
            
            # Draw food
            pygame.draw.rect(
                window,
                RED,
                [self.food[0], self.food[1] + TASKBAR_HEIGHT, self.block_size, self.block_size],
                border_radius=6,
            )
            
            # Draw both snakes
            if self.player_alive:
                self.draw_snake(self.player_snake, PLAYER_HEAD_COLOR, PLAYER_BODY_COLOR)
            if self.ai_alive:
                self.draw_snake(self.ai_snake, AI_HEAD_COLOR, AI_BODY_COLOR)

            # Draw taskbar
            pygame.draw.rect(window, GRAY, [0, 0, self.width, TASKBAR_HEIGHT])
            score_text = font.render(
                f"Grid: {self.grid_size}×{self.grid_size}  |  Player: {self.player_score}  |  AI: {self.ai_score}  |  Speed: {self.snake_speed}", 
                True, WHITE
            )
            window.blit(score_text, [10, TASKBAR_HEIGHT // 2 - score_text.get_height() // 2])

            pygame.display.update()
            clock.tick(self.snake_speed)


if __name__ == "__main__":
    # Get grid size first
    grid_size = get_grid_size()
    
    # Update window size based on grid
    WINDOW_WIDTH = grid_size * BLOCK_SIZE
    WINDOW_HEIGHT = grid_size * BLOCK_SIZE
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + TASKBAR_HEIGHT))
    
    # Show instructions
    show_instructions()
    
    # Start game with selected grid size
    game = SnakeGame(grid_size)
    game.game_loop()