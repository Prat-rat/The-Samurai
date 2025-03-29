#We used Copilot to help us make the bats follow the player, simplify long functions, and swith screens

import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
PLATFORM_COLOR = (139, 69, 19)
GROUND_COLOR = (20, 21, 20)

clock = pygame.time.Clock()
FPS = 60

player_width, player_height = 50, 50
player_x, player_y = WIDTH // 2, HEIGHT - 60
player_speed = 5
player_jump = -15
player_velocity_y = 0
gravity = 0.8
on_ground = False

player_idle_right_image = pygame.image.load("Character\\Player\\Sprites\\idle_right.png").convert_alpha()
player_idle_left_image = pygame.image.load("Character\\Player\\Sprites\\idle_left.png").convert_alpha()
player_run_right_sheet = pygame.image.load("Character\\Player\\Sprites\\Run\\Run Right.png").convert_alpha()
player_run_left_sheet = pygame.image.load("Character\\Player\\Sprites\\Run\\Run Left.png").convert_alpha()

run_frame_width = player_run_right_sheet.get_width() // 16
run_frame_height = player_run_right_sheet.get_height()
run_frame_index = 0
run_animation_speed = 5
frame_counter = 0

player_attack_right_sheet = pygame.image.load("Character\\Player\\Sprites\\attack_right.png").convert_alpha()
player_attack_left_sheet = pygame.image.load("Character\\Player\\Sprites\\attack_left.png").convert_alpha()
attack_frame_width = player_attack_right_sheet.get_width() // 7
attack_frame_height = player_attack_right_sheet.get_height()
attack_frame_index = 0
attack_animation_speed = 3
is_attacking = False
attack_frame_counter = 0

player_health = 100
health_bar_width = 200
health_bar_height = 20
health_regen_timer = 0
HEALTH_REGEN_INTERVAL = FPS * 10

def get_run_frame(sheet, index):
    index %= sheet.get_width() // run_frame_width
    return sheet.subsurface(pygame.Rect(index * run_frame_width, 0, run_frame_width, run_frame_height))

def get_attack_frame(sheet, index):
    index %= sheet.get_width() // attack_frame_width
    return sheet.subsurface(pygame.Rect(index * attack_frame_width, 0, attack_frame_width, attack_frame_height))

ground_y = HEIGHT - 50
player_y = ground_y - run_frame_height
player_direction = "right"

bat_idle_sheet = pygame.image.load("Character\\Enemies\\Bat\\Bat with VFX\\Bat-WakeUp.png").convert_alpha()
bat_frame_width = bat_idle_sheet.get_width() // 16
bat_frame_height = bat_idle_sheet.get_height()
bat_animation_speed = 5

bat_idle_fly_sheet = pygame.image.load("Character\\Enemies\\Bat\\Bat with VFX\\Bat-IdleFly.png").convert_alpha()
bat_idle_fly_frame_width = bat_idle_fly_sheet.get_width() // 9
bat_idle_fly_frame_height = bat_idle_fly_sheet.get_height()

bat_attack_sheet = pygame.image.load("Character\\Enemies\\Bat\\Bat with VFX\\Bat-Attack1.png").convert_alpha()
bat_attack_frame_width = bat_attack_sheet.get_width() // 8
bat_attack_frame_height = bat_attack_sheet.get_height()

def get_bat_frame(sheet, index):
    index %= sheet.get_width() // bat_frame_width
    return sheet.subsurface(pygame.Rect(index * bat_frame_width, 0, bat_frame_width, bat_frame_height))

def get_bat_idle_fly_frame(sheet, index):
    index %= sheet.get_width() // bat_idle_fly_frame_width
    return sheet.subsurface(pygame.Rect(index * bat_idle_fly_frame_width, 0, bat_idle_fly_frame_width, bat_idle_fly_frame_height))

def get_bat_attack_frame(sheet, index):
    index %= sheet.get_width() // bat_attack_frame_width
    return sheet.subsurface(pygame.Rect(index * bat_attack_frame_width, 0, bat_attack_frame_width, bat_attack_frame_height))

bats = []
bat_width, bat_height = bat_frame_width, bat_frame_height
BAT_STATE_WAKE_UP = "wake_up"
BAT_STATE_IDLE_FLY = "idle_fly"
BAT_STATE_CHASE = "chase"
BAT_ATTACK_COOLDOWN = 180
BAT_DAMAGE = 2 
BAT_ATTACK_DELAY = FPS * 2
BAT_ATTACK_FRAME_DAMAGE = 5
BAT_ATTACK_SPEED = 3
BAT_FOLLOW_SPEED = 3
BAT_WAKE_UP_MIN_TIME = 0
BAT_WAKE_UP_MAX_TIME = 3

platforms = [(136, 454, 278, 20)]

def start_page():
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 50)
    title_text = font_large.render("Survivor Game", True, (255, 255, 255))
    play_text = font_medium.render("Play", True, (0, 0, 0))
    play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)
    
    welcome_background = pygame.image.load("welcome.jpg").convert()
    
    while True:
        screen.blit(welcome_background, (0, 0))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
        pygame.draw.rect(screen, (255, 255, 255), play_button)
        pygame.draw.rect(screen, (0, 0, 0), play_button, 3)
        screen.blit(play_text, (play_button.x + play_button.width // 2 - play_text.get_width() // 2, play_button.y + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return

def you_win_page():
    font_large = pygame.font.Font(None, 74)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    return

def you_lose_page():
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 50)
    text = font_large.render("You Lose!", True, (255, 0, 0))
    play_again_text = font_medium.render("Press R to Play Again", True, (255, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
    screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    return

def reset_game():
    global wave_number, player_health, player_x, player_y, bats, kills, wave_started
    wave_number = 1
    player_health = 100
    player_x, player_y = WIDTH // 2, ground_y - player_height
    bats.clear()
    kills = 0
    wave_started = False

start_page()

wave_number = 1
bats_per_wave = {1: 3, 2: 5, 3: 7}
wave_font = pygame.font.Font(None, 36)
wave_started = False

background_image = pygame.image.load("Background\\back.png").convert()
kills = 0

while True:
    screen.blit(background_image, (0, 150))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                is_attacking = True
                attack_frame_index = 0
                attack_frame_counter = 0

    keys = pygame.key.get_pressed()
    if is_attacking:
        attack_frame_counter += 1
        if attack_frame_counter >= attack_animation_speed:
            attack_frame_index += 1
            attack_frame_counter = 0
        if attack_frame_index >= 7:
            is_attacking = False
            attack_frame_index = 0
        else:
            if player_direction == "right":
                current_player_image = get_attack_frame(player_attack_right_sheet, attack_frame_index)
            else:
                current_player_image = get_attack_frame(player_attack_left_sheet, attack_frame_index)
            attack_y = player_y
            for bat in bats[:]:
                if (
                    player_direction == "right" and
                    player_x + player_width >= bat[0] and
                    player_x <= bat[0] + bat_width and
                    attack_y + run_frame_height >= bat[1] and
                    attack_y <= bat[1] + bat_height
                ) or (
                    player_direction == "left" and
                    player_x <= bat[0] + bat_width and
                    player_x + player_width >= bat[0] and
                    attack_y + run_frame_height >= bat[1] and
                    attack_y <= bat[1] + bat_height
                ):
                    bats.remove(bat)
                    kills += 1
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= player_speed
        player_direction = "left"
        frame_counter += 1
        if frame_counter >= run_animation_speed:
            run_frame_index = (run_frame_index + 1) % 7
            frame_counter = 0
        current_player_image = get_run_frame(player_run_left_sheet, run_frame_index)
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += player_speed
        player_direction = "right"
        frame_counter += 1
        if frame_counter >= run_animation_speed:
            run_frame_index = (run_frame_index + 1) % 7
            frame_counter = 0
        current_player_image = get_run_frame(player_run_right_sheet, run_frame_index)
    else:
        if player_direction == "right":
            current_player_image = player_idle_right_image
        else:
            current_player_image = player_idle_left_image
        idle_y_offset = 15

    player_x = max(0, min(player_x, WIDTH - player_width))
    if (keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:
        player_velocity_y = player_jump
        on_ground = False
    player_velocity_y += gravity
    player_y += player_velocity_y
    if player_y + run_frame_height >= ground_y:
        player_y = ground_y - run_frame_height
        player_velocity_y = 0
        on_ground = True
    if not on_ground:
        on_ground = False
    health_regen_timer += 1
    if health_regen_timer >= HEALTH_REGEN_INTERVAL:
        player_health = min(player_health + 5, 100)
        health_regen_timer = 0
    if is_attacking:
        for bat in bats[:]:
            if (
                player_direction == "right" and
                player_x + player_width >= bat[0] and
                player_x <= bat[0] + bat_width and
                player_y + run_frame_height >= bat[1] and
                player_y <= bat[1] + bat_height
            ) or (
                player_direction == "left" and
                player_x <= bat[0] + bat_width and
                player_x + player_width >= bat[0] and
                player_y + run_frame_height >= bat[1] and
                player_y <= bat[1] + bat_height
            ):
                bats.remove(bat)
                kills += 1
    for bat in bats:
        if bat[2] == BAT_STATE_WAKE_UP:
            bat[4] += 1
            if bat[4] >= bat_animation_speed:
                bat[3] += 1
                bat[4] = 0
            if bat[3] >= 16 or bat[5] <= 0:
                bat[2] = BAT_STATE_IDLE_FLY
                bat[3] = 0
                bat[5] = 0
            else:
                bat[5] -= 1
        elif bat[2] == BAT_STATE_IDLE_FLY or bat[2] == BAT_STATE_CHASE:
            bat[4] += 1
            if bat[4] >= bat_animation_speed:
                bat[3] = (bat[3] + 1) % 9
                bat[4] = 0
            if bat[2] == BAT_STATE_IDLE_FLY:
                bat[5] += 1
                if bat[5] >= BAT_ATTACK_DELAY:
                    bat[2] = BAT_STATE_CHASE
                    bat[3] = 0
                    bat[4] = 0
            elif bat[2] == BAT_STATE_CHASE:
                target_x = player_x + player_width // 2 - bat_width // 2
                target_y = player_y + player_height // 2 - bat_height // 2
                if bat[0] < target_x:
                    bat[0] += BAT_FOLLOW_SPEED
                elif bat[0] > target_x:
                    bat[0] -= BAT_FOLLOW_SPEED
                if bat[1] < target_y:
                    bat[1] += BAT_FOLLOW_SPEED
                elif bat[1] > target_y:
                    bat[1] -= BAT_FOLLOW_SPEED
                if (
                    abs(bat[0] - target_x) <= 5 and
                    abs(bat[1] - target_y) <= 5 and
                    player_x < bat[0] + bat_width and
                    player_x + player_width > bat[0] and
                    player_y < bat[1] + bat_height and
                    player_y + player_height > bat[1]
                ):
                    player_health -= BAT_DAMAGE
                    player_health = max(player_health, 0)
    if not bats and not wave_started:
        wave_started = True
        if wave_number in bats_per_wave:
            bat_positions = []
            for i in range(bats_per_wave[wave_number]):
                while True:
                    bat_x = random.randint(0, WIDTH - bat_width)
                    bat_y = 280 - bat_height 
                    if all(abs(bat_x - bx) > bat_width for bx, by in bat_positions):
                        bat_positions.append((bat_x, bat_y))
                        wake_up_duration = random.randint(BAT_WAKE_UP_MIN_TIME * FPS, BAT_WAKE_UP_MAX_TIME * FPS)
                        bats.append([bat_x, bat_y, BAT_STATE_WAKE_UP, 0, 0, wake_up_duration, 0, BAT_ATTACK_COOLDOWN, False])
                        break
            player_health = min(player_health + 20, 100)
    if player_health <= 0:
        you_lose_page()
        wave_number = 1
        player_health = 100
        player_x, player_y = WIDTH // 2, ground_y - player_height
        bats.clear()
        kills = 0
        continue
    if wave_started and not bats:
        wave_started = False
        if wave_number < 3:
            wave_number += 1
            kills = 0
        else:
            you_win_page()
            wave_number = 1
            player_health = 100
            bats.clear()
            kills = 0
            player_x, player_y = WIDTH // 2, ground_y - player_height
    pygame.draw.rect(screen, GROUND_COLOR, (0, ground_y, WIDTH, HEIGHT - ground_y - 100))
    pygame.draw.rect(screen, GROUND_COLOR, (0, 0, WIDTH, 200))
    if current_player_image in [player_idle_right_image, player_idle_left_image]:
        screen.blit(current_player_image, (player_x, player_y + idle_y_offset))
    else:
        screen.blit(current_player_image, (player_x, player_y))
    for bat in bats:
        if bat[2] == BAT_STATE_WAKE_UP:
            current_bat_image = get_bat_frame(bat_idle_sheet, bat[3])
        elif bat[2] == BAT_STATE_IDLE_FLY:
            current_bat_image = get_bat_idle_fly_frame(bat_idle_fly_sheet, bat[3])
        elif bat[2] == BAT_STATE_CHASE:
            current_bat_image = get_bat_attack_frame(bat_attack_sheet, bat[3])
        screen.blit(current_bat_image, (bat[0], bat[1]))
    for platform in platforms:
        px, py, pw, ph = platform
        if px < player_x + player_width and player_x < px + pw:
            if py < player_y + player_height <= py + ph:
                player_y = py - player_height
                player_velocity_y = 0
                on_ground = True
                break
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (10, 10, health_bar_width * (player_health / 100), health_bar_height))
    wave_text = wave_font.render(f"Wave: {wave_number}", True, (255, 255, 255))
    screen.blit(wave_text, (WIDTH - wave_text.get_width() - 10, 10))
    kill_counter_text = wave_font.render(f"Kills: {kills}/{bats_per_wave[wave_number]}", True, (255, 255, 255))
    screen.blit(kill_counter_text, (WIDTH - kill_counter_text.get_width() - 10, 40))
    if player_health <= 0:
        wave_number = 1
        player_health = 100
        player_x, player_y = WIDTH // 2, ground_y - player_height
        bats.clear()
        kills = 0
        continue
    pygame.display.flip()
    clock.tick(FPS)
