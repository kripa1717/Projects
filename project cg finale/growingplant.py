import pygame
import random
import cv2

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
FPS = 60
win_threshold = 100
icon = pygame.image.load('pine.png')
pygame.display.set_icon(icon)

# Load Background Video
video = cv2.VideoCapture("backv.mp4")

# Load Images
seed_img = pygame.image.load("seed.png")
growing_plant_imgs = [
    pygame.image.load("growing_plant1.png"),
    pygame.image.load("growing_plant2.png"),
    pygame.image.load("growing_plant3.png"),
    pygame.image.load("grown.png")
]
water_img = pygame.image.load("water.png")
nutrient_img = pygame.image.load("nutrient.png")
rock_img = pygame.image.load("rocks.png")
drought_img = pygame.image.load("drought.png")

# Load Fruits for Burst Effect
fruit_images = [
    pygame.image.load("apple.png"), pygame.image.load("bananas.png"), pygame.image.load("cherries.png"),
    pygame.image.load("grapes.png"), pygame.image.load("pineapple.png"), pygame.image.load("strawberry.png"),
    pygame.image.load("watermelon.png"), pygame.image.load("orange.png")
]

# Resize Images
seed_img = pygame.transform.scale(seed_img, (40, 40))
growing_plant_imgs = [pygame.transform.scale(img, (50, 50)) for img in growing_plant_imgs]
water_img = pygame.transform.scale(water_img, (30, 30))
nutrient_img = pygame.transform.scale(nutrient_img, (30, 30))
rock_img = pygame.transform.scale(rock_img, (40, 40))
drought_img = pygame.transform.scale(drought_img, (50, 30))
fruit_images = [pygame.transform.scale(fruit, (50, 50)) for fruit in fruit_images]

# Game Variables
score = 20
speed = 5
obstacle_speed = 3
fruits = []

# Screen Setup
game_screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Growing Plant Game")
clock = pygame.time.Clock()

def spawn_resources():
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 200)
    type_ = random.choice(['water', 'nutrient'])
    resources.append({'rect': pygame.Rect(x, y, 20, 20), 'type': type_})

def spawn_obstacles():
    x = random.randint(50, WIDTH - 50)
    y = 0
    obstacle_type = random.choice(['rock', 'drought'])
    obstacle_rect = pygame.Rect(x, y, 40, 40) if obstacle_type == 'rock' else pygame.Rect(x, y, 50, 30)
    obstacles.append({'rect': obstacle_rect, 'type': obstacle_type})

# Game Elements
seed = pygame.Rect(WIDTH // 2, HEIGHT - 100, 40, 40)
resources = []
obstacles = []
for _ in range(5):
    spawn_resources()
    spawn_obstacles()

# Main Loop
running = True
won = False
while running:
    clock.tick(FPS)
    
    # Load video frame
    ret, frame = video.read()
    if not ret:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    
    # Display video as background
    game_screen.blit(frame_surface, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and seed.x > 0:
        seed.x -= speed
    if keys[pygame.K_RIGHT] and seed.x < WIDTH - seed.width:
        seed.x += speed
    if keys[pygame.K_UP] and seed.y > 0:
        seed.y -= speed
    if keys[pygame.K_DOWN] and seed.y < HEIGHT - seed.height:
        seed.y += speed

    for resource in resources[:]:
        if seed.colliderect(resource['rect']):
            score += 5 if resource['type'] == 'nutrient' else 3
            resources.remove(resource)
            spawn_resources()

    for obstacle in obstacles[:]:
        obstacle['rect'].y += obstacle_speed
        if obstacle['rect'].y > HEIGHT:
            obstacles.remove(obstacle)
            spawn_obstacles()

    for obstacle in obstacles[:]:
        if seed.colliderect(obstacle['rect']):
            if obstacle['type'] == 'rock':
                score -= 10
            elif obstacle['type'] == 'drought':
                speed = max(2, speed - 1)
            obstacles.remove(obstacle)
            spawn_obstacles()

    if score <= 0:
        font = pygame.font.Font(None, 50)
        game_over_text = font.render("Game Over!!!", True, "RED")
        game_screen.blit(game_over_text, (250, 250))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

    if score >= win_threshold and not won:
        won = True
        for _ in range(50):  # Spawn 50 fruits for burst effect
            x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            fruit = random.choice(fruit_images)
            fruits.append({'image': fruit, 'pos': (x, y)})

    if won:
        for fruit in fruits:
            game_screen.blit(fruit['image'], fruit['pos'])
        font = pygame.font.Font(None, 50)
        win_text = font.render("You have won! Your plant has fully grown!", True, "BLACK")
        game_screen.blit(win_text, (70, 250))
        pygame.display.flip()
        pygame.time.delay(5000)
        running = False

    if score >= 81:
        current_seed_img = growing_plant_imgs[3]
    elif score >= 61:
        current_seed_img = growing_plant_imgs[2]
    elif score >= 41:
        current_seed_img = growing_plant_imgs[1]
    elif score >= 21:
        current_seed_img = growing_plant_imgs[0]
    else:
        current_seed_img = seed_img

    game_screen.blit(current_seed_img, (seed.x, seed.y))
    for resource in resources:
        img = nutrient_img if resource['type'] == 'nutrient' else water_img
        game_screen.blit(img, (resource['rect'].x, resource['rect'].y))
    for obstacle in obstacles:
        img = rock_img if obstacle['type'] == 'rock' else drought_img
        game_screen.blit(img, (obstacle['rect'].x, obstacle['rect'].y))
    score_text = pygame.font.Font(None, 36).render(f"Score: {score}", True, WHITE)
    game_screen.blit(score_text, (10, 10))
    pygame.display.flip()

video.release()
pygame.quit()