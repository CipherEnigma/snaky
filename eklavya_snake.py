import pygame
import random
from heapq import heappush, heappop
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Game constants  
N = 30  # Increased grid size
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
SNAKE_HEAD_COLOR = (0, 200, 0)  # Bright green
SNAKE_BODY_COLOR = (50, 205, 50)  # Lime green
HIGHLIGHT_COLOR = (0, 150, 255)
PATH_COLOR = (100, 150, 255, 100)  # Light blue with transparency
RANDOM_COLORS = [(255, 255, 0), (255, 165, 0), (0, 255, 255), (255, 20, 147), (0, 255, 0)]
BORDER_COLORS = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]

# Initialize the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + TASKBAR_HEIGHT))
pygame.display.set_caption("AI Snake Game with A* Path")

# Clock and fonts
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
title_font = pygame.font.SysFont(None, 60)
game_over_font = pygame.font.SysFont("arial", 50, bold=True)

# Game-over messages
GAME_OVER_MESSAGES = [
    "Oops! Game Over!",
    "Better luck next time!",
    "The snake's journey ends here!",
    "You've been bitten!",
    "Time to start anew!"
]


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
        title = title_font.render("AI Snake Game", True, (0, 255, 100))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        window.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "How to Play:",
            "",
            "• The snake is controlled by AI using A* algorithm",
            "• Blue path shows where the snake will go",
            "• Snake automatically finds and eats the red food",
            "• Snake grows longer with each food eaten",
            "• Game ends if snake collides with itself",
            "• Speed increases every 5 points",
            "",
            "Keyboard Controls:",
            "",
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
    def __init__(self):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.block_size = BLOCK_SIZE
        self.snake_speed = 10
        self.high_score = 0
        self.border_offset = 0
        self.reset_game()

    def reset_game(self):
        self.snake = [[self.width // 2, self.height // 2]]
        self.direction = "RIGHT"
        self.score = 0
        self.generate_food()
        self.game_close = False
        self.path = []  # Store the current path

    def generate_food(self):
        while True:
            self.food = [
                random.randrange(0, self.width // self.block_size) * self.block_size,
                random.randrange(0, self.height // self.block_size) * self.block_size,
            ]
            if self.food not in self.snake:
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

    def get_neighbors(self, pos: List[int]) -> List[List[int]]:
        neighbors = []
        moves = [(0, -self.block_size), (0, self.block_size), 
                (-self.block_size, 0), (self.block_size, 0)]
        
        for dx, dy in moves:
            new_x = pos[0] + dx
            new_y = pos[1] + dy
            new_pos = self.wrap_position([new_x, new_y])
            
            if new_pos not in self.snake[1:]:
                neighbors.append(new_pos)
        
        return neighbors

    def a_star_pathfinding(self) -> List[List[int]]:
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
                return path

            for neighbor in map(tuple, self.get_neighbors(list(current))):
                tentative_g_score = g_score[current] + self.block_size

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.manhattan_distance(
                        list(neighbor), self.food
                    )
                    heappush(open_set, (f_score[neighbor], neighbor))

        return []

    def update_direction(self, next_pos: List[int]):
        head = self.snake[0]
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
            if self.score % 5 == 0:
                self.snake_speed = min(30, self.snake_speed + 2)
        else:
            self.snake[0] = new_head
            for i in range(1, len(self.snake)):
                self.snake[i] = prev_positions[i-1]

    def check_collision(self) -> bool:
        head = self.snake[0]
        return head in self.snake[1:]

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

    def draw_snake(self):
        for idx, segment in enumerate(self.snake):
            if idx == 0:
                pygame.draw.rect(
                    window,
                    SNAKE_HEAD_COLOR,
                    [segment[0], segment[1] + TASKBAR_HEIGHT, self.block_size, self.block_size],
                    border_radius=8,
                )
            else:
                pygame.draw.rect(
                    window,
                    SNAKE_BODY_COLOR,
                    [segment[0], segment[1] + TASKBAR_HEIGHT, self.block_size, self.block_size],
                    border_radius=4,
                )

    def display_game_over(self):
        window.fill(BLACK)
        random_message = random.choice(GAME_OVER_MESSAGES)
        random_color = random.choice(RANDOM_COLORS)

        game_over_text = game_over_font.render(random_message, True, random_color)
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        window.blit(game_over_text, game_over_rect)

        score_text = font.render(f"Your Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        window.blit(score_text, score_rect)

        high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
        window.blit(high_score_text, high_score_rect)

        play_again_text = font.render("Play Again (SPACE)", True, WHITE)
        quit_text = font.render("Quit (ESC)", True, WHITE)
        play_again_rect = play_again_text.get_rect(center=(self.width // 2, self.height // 2 + 120))
        quit_rect = quit_text.get_rect(center=(self.width // 2, self.height // 2 + 160))

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
            window.blit(score_text, score_rect)
            window.blit(high_score_text, high_score_rect)
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

            if not self.path:
                self.path = self.a_star_pathfinding()

            if self.path:
                next_step = self.path.pop(0)
                self.update_direction(next_step)

            self.move_snake()

            if self.check_collision():
                self.high_score = max(self.high_score, self.score)
                self.game_close = True

            window.fill(BLACK)
            
            # Draw path first (so it appears under everything else)
            self.draw_path()
            
            # Draw food
            pygame.draw.rect(
                window,
                RED,
                [self.food[0], self.food[1] + TASKBAR_HEIGHT, self.block_size, self.block_size],
                border_radius=6,
            )
            
            # Draw snake
            self.draw_snake()

            # Draw taskbar
            pygame.draw.rect(window, GRAY, [0, 0, self.width, TASKBAR_HEIGHT])
            score_text = font.render(f"Score: {self.score}  |  High Score: {self.high_score}  |  Speed: {self.snake_speed}", True, WHITE)
            window.blit(score_text, [10, TASKBAR_HEIGHT // 2 - score_text.get_height() // 2])

            pygame.display.update()
            clock.tick(self.snake_speed)


if __name__ == "__main__":
    show_instructions()
    game = SnakeGame()
    game.game_loop()