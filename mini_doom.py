import pygame
import math
import sys
import random

# --- Config ---
WIDTH, HEIGHT = 800, 600
FPS = 60
MAP = [
    "1111111111",
    "1000000001",
    "1011001001",
    "1000000001",
    "1111111111"
]
TILE = 64
FOV = math.pi / 3
NUM_RAYS = 120
MAX_DEPTH = 20

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Player
player_x, player_y = 3.0, 3.0
player_angle = 0
player_speed = 2.0
ammo = 10
health = 100

# Enemy
enemies = [(5.5, 2.5), (2.5, 3.5)]
enemy_alive = [True for _ in enemies]

# Shooting
def shoot():
    global ammo
    if ammo <= 0:
        return
    ammo -= 1
    for i, (ex, ey) in enumerate(enemies):
        if not enemy_alive[i]:
            continue
        dx, dy = ex - player_x, ey - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx) - player_angle
        if abs(angle) < 0.1 and dist < 5:
            enemy_alive[i] = False

def map_at(x, y):
    if 0 <= x < len(MAP[0]) and 0 <= y < len(MAP):
        return MAP[int(y)][int(x)]
    return '1'

# --- Raycasting ---
def cast_rays():
    start_angle = player_angle - FOV/2
    for ray in range(NUM_RAYS):
        ray_angle = start_angle + ray * (FOV / NUM_RAYS)
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)
        depth = 0
        while depth < MAX_DEPTH:
            x = player_x + cos_a * depth
            y = player_y + sin_a * depth
            if map_at(int(x), int(y)) != '0':
                depth *= math.cos(player_angle - ray_angle)
                h = min(HEIGHT, int(HEIGHT / (depth + 0.0001)))
                color = (255 - min(255, int(depth*12)), 0, 0)
                pygame.draw.rect(screen, color, (ray*(WIDTH//NUM_RAYS), HEIGHT//2 - h//2, WIDTH//NUM_RAYS, h))
                break
            depth += 0.05

# --- Enemies ---
def draw_enemies():
    global health
    for i, (ex, ey) in enumerate(enemies):
        if not enemy_alive[i]:
            continue
        dx, dy = ex - player_x, ey - player_y
        dist = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx) - player_angle
        if -FOV/2 < angle < FOV/2:
            size = min(200, int(300 / (dist + 0.1)))
            x = WIDTH//2 + int(angle * (WIDTH / FOV)) - size//2
            y = HEIGHT//2 - size//2
            pygame.draw.rect(screen, (200, 50, 50), (x, y, size, size))

        # Enemy attacks if too close
        if dist < 1.0:
            health -= 0.2  # slow drain

# --- Touch input ---
def handle_touch():
    global player_x, player_y, player_angle
    for e in pygame.event.get([pygame.FINGERDOWN, pygame.FINGERMOTION]):
        x = e.x * WIDTH
        y = e.y * HEIGHT
        if x < WIDTH/3:  # left third = move forward
            nx = player_x + math.cos(player_angle) * 0.1
            ny = player_y + math.sin(player_angle) * 0.1
            if map_at(int(nx), int(player_y)) == '0': player_x = nx
            if map_at(int(player_x), int(ny)) == '0': player_y = ny
        elif x > WIDTH*2/3:  # right third = turn
            if x > WIDTH*0.85:  # far right corner = shoot
                shoot()
            else:
                player_angle += (x - WIDTH/2) / WIDTH * 0.02

# --- Main loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            shoot()

    # Touch
    handle_touch()

    # Keyboard controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        nx = player_x + math.cos(player_angle) * player_speed * dt
        ny = player_y + math.sin(player_angle) * player_speed * dt
        if map_at(int(nx), int(player_y)) == '0': player_x = nx
        if map_at(int(player_x), int(ny)) == '0': player_y = ny
    if keys[pygame.K_s]:
        nx = player_x - math.cos(player_angle) * player_speed * dt
        ny = player_y - math.sin(player_angle) * player_speed * dt
        if map_at(int(nx), int(player_y)) == '0': player_x = nx
        if map_at(int(player_x), int(ny)) == '0': player_y = ny
    if keys[pygame.K_a]:
        player_angle -= 2 * dt
    if keys[pygame.K_d]:
        player_angle += 2 * dt

    # Draw world
    screen.fill((100, 100, 100))
    pygame.draw.rect(screen, (50, 50, 50), (0, HEIGHT//2, WIDTH, HEIGHT//2))
    cast_rays()
    draw_enemies()

    # HUD
    ammo_text = font.render(f"Ammo: {ammo}", True, (255, 255, 255))
    health_text = font.render(f"Health: {int(health)}", True, (255, 255, 255))
    screen.blit(ammo_text, (10, 10))
    screen.blit(health_text, (10, 30))

    # Check death
    if health <= 0:
        death_text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(death_text, (WIDTH//2 - 50, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    pygame.display.flip()

pygame.quit()
sys.exit()
