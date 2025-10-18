import pygame
import random
import math
import sys

pygame.init()

# Screen setup
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shadow Hunter 🕹️")

# Clock
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 60, 60)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Player
player_img = pygame.Surface((40, 40))
player_img.fill(GREEN)
player_rect = player_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
player_speed = 5
player_health = 100

# Bullet
bullet_img = pygame.Surface((10, 10))
bullet_img.fill(RED)
bullets = []

# Enemy
enemy_img = pygame.Surface((40, 40))
enemy_img.fill((255, 120, 0))
enemies = []
enemy_speed = 2
enemy_spawn_time = 2000  # milliseconds
last_spawn = pygame.time.get_ticks()

# Power-ups
powerups = []
powerup_img = pygame.Surface((20, 20))
powerup_img.fill((0, 255, 255))
powerup_timer = 0

# Game variables
score = 0
level = 1
font = pygame.font.Font(None, 36)

# Boss
boss_active = False
boss_img = pygame.Surface((100, 100))
boss_img.fill((255, 0, 100))
boss_rect = boss_img.get_rect(center=(WIDTH // 2, 100))
boss_health = 300


def spawn_enemy():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x, y = random.randint(0, WIDTH), -50
    elif side == 'bottom':
        x, y = random.randint(0, WIDTH), HEIGHT + 50
    elif side == 'left':
        x, y = -50, random.randint(0, HEIGHT)
    else:
        x, y = WIDTH + 50, random.randint(0, HEIGHT)
    enemies.append(pygame.Rect(x, y, 40, 40))


def move_enemy(enemy_rect):
    # AI pathfinding (simple vector movement towards player)
    dx = player_rect.x - enemy_rect.x
    dy = player_rect.y - enemy_rect.y
    distance = math.hypot(dx, dy)
    if distance != 0:
        dx, dy = dx / distance, dy / distance
    enemy_rect.x += dx * enemy_speed
    enemy_rect.y += dy * enemy_speed


def draw_health_bar(x, y, health, max_health=100):
    ratio = health / max_health
    pygame.draw.rect(screen, RED, (x, y, 100, 10))
    pygame.draw.rect(screen, GREEN, (x, y, 100 * ratio, 10))


running = True
while running:
    clock.tick(60)
    screen.fill((15, 15, 30))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Fire bullet
                bullet = bullet_img.get_rect(center=player_rect.center)
                bullets.append(bullet)

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_rect.x -= player_speed
    if keys[pygame.K_d]:
        player_rect.x += player_speed
    if keys[pygame.K_w]:
        player_rect.y -= player_speed
    if keys[pygame.K_s]:
        player_rect.y += player_speed

    # Keep player in bounds
    player_rect.clamp_ip(screen.get_rect())

    # Bullet movement
    for bullet in bullets[:]:
        bullet.y -= 8
        if bullet.y < 0:
            bullets.remove(bullet)

    # Enemy spawning
    now = pygame.time.get_ticks()
    if now - last_spawn > enemy_spawn_time and not boss_active:
        spawn_enemy()
        last_spawn = now

    # Move enemies
    for enemy in enemies[:]:
        move_enemy(enemy)
        if enemy.colliderect(player_rect):
            player_health -= 5
            enemies.remove(enemy)
        # Bullet collision
        for bullet in bullets[:]:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 10
                break

    # Power-up logic
    if random.random() < 0.002 and powerup_timer <= 0:
        x, y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
        powerups.append(pygame.Rect(x, y, 20, 20))
        powerup_timer = 5000  # prevent spam

    for p in powerups[:]:
        if p.colliderect(player_rect):
            player_health = min(100, player_health + 20)
            powerups.remove(p)

    if powerup_timer > 0:
        powerup_timer -= 10

    # Level progression
    if score > level * 100 and not boss_active:
        level += 1
        enemy_speed += 0.5
        enemy_spawn_time = max(800, enemy_spawn_time - 200)
        if level % 3 == 0:
            boss_active = True

    # Boss fight
    if boss_active:
        if boss_rect.y < 150:
            boss_rect.y += 1
        else:
            boss_rect.x += random.choice([-3, 3])

        if random.random() < 0.02:
            spawn_enemy()

        # Boss movement limits
        if boss_rect.x <= 0 or boss_rect.x >= WIDTH - boss_rect.width:
            boss_rect.x = max(0, min(boss_rect.x, WIDTH - boss_rect.width))

        # Bullet collision
        for bullet in bullets[:]:
            if bullet.colliderect(boss_rect):
                bullets.remove(bullet)
                boss_health -= 10
                score += 5

        if boss_health <= 0:
            boss_active = False
            boss_health = 300
            score += 200

        screen.blit(boss_img, boss_rect)
        draw_health_bar(boss_rect.x, boss_rect.y - 15, boss_health, 300)

    # Draw everything
    screen.blit(player_img, player_rect)
    for bullet in bullets:
        screen.blit(bullet_img, bullet)
    for enemy in enemies:
        screen.blit(enemy_img, enemy)
    for p in powerups:
        screen.blit(powerup_img, p)

    draw_health_bar(10, 10, player_health)
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 30))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 60))

    if player_health <= 0:
        game_over = font.render("GAME OVER - Press R to Restart", True, RED)
        screen.blit(game_over, (WIDTH // 2 - 200, HEIGHT // 2))
        pygame.display.flip()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            enemies.clear()
            bullets.clear()
            powerups.clear()
            player_health = 100
            score = 0
            level = 1
            boss_active = False
            boss_health = 300
        continue

    pygame.display.update()

pygame.quit()
sys.exit()
