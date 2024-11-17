import pygame
from sys import exit
import random
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 400
GROUND_HEIGHT = HEIGHT - 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Onid")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)

DINO = pygame.image.load('./assets/dino.png').convert_alpha()
DINO = pygame.transform.scale(DINO, (60, 60))
BG = pygame.image.load('./assets/bg.jpg').convert()
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT))
CACTUS = pygame.image.load('./assets/cactus.png').convert_alpha()
CACTUS = pygame.transform.scale(CACTUS, (40, 60))
BIRD = pygame.image.load('./assets/bird.png').convert_alpha()
BIRD = pygame.transform.scale(BIRD, (60, 40))

dino_rect = DINO.get_rect(midbottom=(100, GROUND_HEIGHT))
obstacles = []

music_path = './assets/dino_music.mp3'
jump_music_path = './assets/jump_music.mp3'
game_over_path = './assets/game_over_music.mp3'
jump_sound = None
game_over_sound = None

if os.path.exists(jump_music_path):
    jump_sound = pygame.mixer.Sound(jump_music_path)
else:
    print(f"Warning: Jump sound file not found at {jump_music_path}")

if os.path.exists(game_over_path):
    game_over_sound = pygame.mixer.Sound(game_over_path)
else:
    print(f"Warning: Game over sound file not found at {game_over_path}")

if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
else:
    print(f"Warning: Music file not found at {music_path}")

# Game state
game_active = True
score = 0
jump_speed = 0
gravity = 0.8
obstacle_spawn_timer = 0
game_speed = 5
speed_increase_rate = 0.01
game_over_played = False

def display_score():
    score_surf = font.render(f'Score: {int(score)}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(topleft=(10, 10))
    screen.blit(score_surf, score_rect)

def check_collision(dino, obstacles):
    for obstacle in obstacles:
        if dino.colliderect(obstacle['rect']):
            return False
    return True

def spawn_obstacle():
    obstacle_type = random.choice(['cactus', 'bird'])
    if obstacle_type == 'cactus':
        return {
            'rect': CACTUS.get_rect(midbottom=(WIDTH + random.randint(100, 200), GROUND_HEIGHT)), #spawing obstacle at random width
            'type': 'cactus'
        }
    else:
        return {
            'rect': BIRD.get_rect(midleft=(WIDTH + random.randint(200, 500), 
                                           random.randint(GROUND_HEIGHT - 120, GROUND_HEIGHT - 60))), #spawing obstacle at random width and and height betweeen 2
            'type': 'bird'
        }

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and dino_rect.bottom >= GROUND_HEIGHT:
                    if jump_sound:
                        jump_sound.play()
                    #subtracting because it will decrease y which means going up , as we subtract y we go up in pygame
                    jump_speed = -16
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                pygame.mixer.music.play(-1)
                obstacles.clear()
                score = 0 
                obstacle_spawn_timer = 0
                game_speed = 5
                game_over_played = False

    if game_active:
        screen.blit(BG, (0, 0))
        
        # Dino
        jump_speed += gravity #adding because it will increase y which means going down , as we add y we go down in pygame
        #subtracting jump_speed and adding adding gravity gives a realistic jump effect as gravtiy pulls us down in every frame
        dino_rect.y += jump_speed
        if dino_rect.bottom >= GROUND_HEIGHT:
            dino_rect.bottom = GROUND_HEIGHT #to make sure dino does not go below ground level
        screen.blit(DINO, dino_rect)
        
        # Obstacles
        obstacle_spawn_timer += 1 #spawing obstacle at random gaps if random.randInt is 70 till obstacle_spawn reaches it nothing will spawn
        if obstacle_spawn_timer >= random.randint(60, 150):  # Randomized spawn interval
            obstacles.append(spawn_obstacle())
            obstacle_spawn_timer = 0
        
        for obstacle in obstacles:
            obstacle['rect'].x -= game_speed #moving obstacles towards left
            if obstacle['type'] == 'cactus':
                screen.blit(CACTUS, obstacle['rect'])
            else:
                screen.blit(BIRD, obstacle['rect'])
            if obstacle['rect'].right <= 0: #removing obstacles that are off screen
                obstacles.remove(obstacle)
                score += 1
        
        # Remove off-screen obstacles
        obstacles = [obs for obs in obstacles if obs['rect'].right > 0]
        
        game_speed += speed_increase_rate
        
        game_active = check_collision(dino_rect, obstacles)
        
        display_score()
    else:
        screen.fill((255, 255, 255))
        pygame.mixer.music.stop() 
        if game_over_sound and not game_over_played:
            game_over_sound.play()
            game_over_played = True
        game_over_surf = font.render('Game Over! Press SPACE to restart', False, (64, 64, 64))
        game_over_rect = game_over_surf.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.blit(game_over_surf, game_over_rect)
        final_score_surf = font.render(f'Final Score: {int(score)}', False, (64, 64, 64))
        final_score_rect = final_score_surf.get_rect(midtop=(WIDTH/2, game_over_rect.bottom + 10))
        screen.blit(final_score_surf, final_score_rect)

    pygame.display.flip()
    clock.tick(60) #60 frames per second