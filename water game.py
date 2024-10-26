import pygame
import random
import sys
import time
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BUCKET_WIDTH = 80
BUCKET_HEIGHT = 50
DROP_SIZE = 30
FPS = 60

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Clean Water Collector')
clock = pygame.time.Clock()


# Load and scale images
def load_image(filename, size):
    try:
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for image: {filename} in {os.path.abspath(filename)}")

        if not os.path.exists(filename):
            print(f"File does not exist: {filename}")
            raise FileNotFoundError(f"{filename} not found")

        # Load image with alpha transparency support
        image = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(image, size)
    except pygame.error as e:
        print(f"Pygame couldn't load {filename}: {str(e)}")
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")

    # Create fallback colored rectangle if image fails to load
    print(f"Creating fallback image for: {filename}")
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((255, 0, 0, 128))  # Semi-transparent red
    return surface



# Print current directory contents to verify file presence
print("\nFiles in current directory:")
for file in os.listdir():
    print(file)

print("\nTrying to load images...")

# Load all game images with relative paths
background = load_image('./background.jpg', (WINDOW_WIDTH, WINDOW_HEIGHT))
bucket_image = load_image('./bucket.png', (BUCKET_WIDTH, BUCKET_HEIGHT))
clean_drop_image = load_image('./clean_droplet.png', (DROP_SIZE, DROP_SIZE))
dirty_drop_image = load_image('./polluted_droplet.png', (DROP_SIZE, DROP_SIZE))

# Difficulty settings
class DifficultyManager:
    def __init__(self):
        self.start_time = time.time()
        self.base_pollution_chance = 0.2
        self.base_drop_speed = 2
        self.active_drops = 2

    def get_current_difficulty(self):
        elapsed_time = time.time() - self.start_time

        pollution_chance = min(0.5, self.base_pollution_chance + (elapsed_time / 60) * 0.2)
        drop_speed = min(6, self.base_drop_speed + (elapsed_time / 30))
        active_drops = min(5, self.active_drops + int(elapsed_time / 30))

        return {
            'pollution_chance': pollution_chance,
            'drop_speed': drop_speed,
            'active_drops': active_drops
        }

    def reset(self):
        self.start_time = time.time()


# Drop class
class Drop:
    def __init__(self, difficulty_manager):
        self.difficulty_manager = difficulty_manager
        self.reset()

    def reset(self):
        difficulty = self.difficulty_manager.get_current_difficulty()
        self.x = random.randint(DROP_SIZE, WINDOW_WIDTH - DROP_SIZE)
        self.y = -DROP_SIZE
        self.speed = random.uniform(difficulty['drop_speed'], difficulty['drop_speed'] + 1)
        self.is_clean = random.random() > difficulty['pollution_chance']

    def move(self):
        self.y += self.speed
        if self.y > WINDOW_HEIGHT:
            self.reset()

    def draw(self):
        drop_image = clean_drop_image if self.is_clean else dirty_drop_image
        screen.blit(drop_image, (self.x - DROP_SIZE // 2, self.y - DROP_SIZE // 2))


# Game state
difficulty_manager = DifficultyManager()
drops = []
score = 0
game_over = False
font = pygame.font.Font(None, 36)
level = 1

# Bucket properties
bucket_x = WINDOW_WIDTH // 2 - BUCKET_WIDTH // 2
bucket_y = WINDOW_HEIGHT - BUCKET_HEIGHT - 10
bucket_speed = 8

# Game loop
while True:
    current_difficulty = difficulty_manager.get_current_difficulty()

    # Adjust number of drops based on difficulty
    while len(drops) < current_difficulty['active_drops']:
        drops.append(Drop(difficulty_manager))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                # Reset game
                score = 0
                game_over = False
                difficulty_manager.reset()
                drops = []
                level = 1

    if not game_over:
        # Bucket movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and bucket_x > 0:
            bucket_x -= bucket_speed
        if keys[pygame.K_RIGHT] and bucket_x < WINDOW_WIDTH - BUCKET_WIDTH:
            bucket_x += bucket_speed

        # Update drops
        for drop in drops:
            drop.move()

            # Collision detection
            bucket_rect = pygame.Rect(bucket_x + 10, bucket_y, BUCKET_WIDTH - 20, BUCKET_HEIGHT)
            drop_rect = pygame.Rect(drop.x - DROP_SIZE // 2, drop.y - DROP_SIZE // 2,
                                    DROP_SIZE, DROP_SIZE)

            if bucket_rect.colliderect(drop_rect):
                if drop.is_clean:
                    score += 1
                    # Level up every 10 points
                    level = score // 10 + 1
                else:
                    game_over = True
                drop.reset()

    # Drawing
    screen.blit(background, (0, 0))

    # Draw drops
    for drop in drops:
        drop.draw()

    # Draw bucket
    screen.blit(bucket_image, (bucket_x, bucket_y))

    # Draw score and level
    score_text = font.render(f'Score: {score}', True, (0, 0, 0))
    level_text = font.render(f'Level: {level}', True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))

    # Game over screen
    if game_over:
        game_over_surface = pygame.Surface((400, 100))
        game_over_surface.fill((0, 0, 0))
        game_over_text = font.render('Game Over! Press R to restart', True, (255, 255, 255))
        final_score_text = font.render(f'Final Score: {score}', True, (255, 255, 255))
        text_rect = game_over_text.get_rect(center=(200, 30))
        score_rect = final_score_text.get_rect(center=(200, 70))
        game_over_surface.blit(game_over_text, text_rect)
        game_over_surface.blit(final_score_text, score_rect)
        screen.blit(game_over_surface,
                    ((WINDOW_WIDTH - 400) // 2, (WINDOW_HEIGHT - 100) // 2))

    pygame.display.flip()
    clock.tick(FPS)
