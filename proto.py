import pygame
import random
import os

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
PLATFORM_COLOR = (139, 69, 19)
GROUND_COLOR = (20, 21, 20)
PLAYER_COLOR = (0, 0, 255)
ENEMY_COLOR = (255, 69, 0)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Player settings
player_width, player_height = 50, 50
player_x, player_y = WIDTH // 2, HEIGHT - 60
player_speed = 5
player_jump = -15
player_velocity_y = 0
gravity = 0.8
on_ground = False
# Load player animations for idle and run
player_idle_right_image = pygame.image.load("Character\\Player\\Sprites\\idle_right.png").convert_alpha()
player_idle_left_image = pygame.image.load("Character\\Player\\Sprites\\idle_left.png").convert_alpha()
player_run_right_sheet = pygame.image.load("Character\\Player\\Sprites\\Run\\Run Right.png").convert_alpha()
player_run_left_sheet = pygame.image.load("Character\\Player\\Sprites\\Run\\Run Left.png").convert_alpha()

# Update frame dimensions for both run animations
run_frame_width = player_run_right_sheet.get_width() // 16  # Assuming 6 frames in the sprite sheet
run_frame_height = player_run_right_sheet.get_height()
run_frame_index = 0
run_animation_speed = 5
frame_counter = 0

# Load attack animations
player_attack_right_sheet = pygame.image.load("Character\\Player\\Sprites\\attack_right.png").convert_alpha()
player_attack_left_sheet = pygame.image.load("Character\\Player\\Sprites\\attack_left.png").convert_alpha()
attack_frame_width = player_attack_right_sheet.get_width() // 7  # 7 frames in the sprite sheet
attack_frame_height = player_attack_right_sheet.get_height()
attack_frame_index = 0
attack_animation_speed = 3  # Adjust speed of attack animation
is_attacking = False
attack_frame_counter = 0

# Player health settings
player_health = 100
health_bar_width = 200
health_bar_height = 20
health_regen_timer = 0
HEALTH_REGEN_INTERVAL = FPS * 10  # 10 seconds

# Remove block settings
# is_blocking = False
# block_timer = 0
# BLOCK_DURATION = FPS * 2  # 2 seconds

# Function to extract a frame from the sprite sheet
def get_run_frame(sheet, index):
    index %= sheet.get_width() // run_frame_width  # Ensure index is within bounds
    return sheet.subsurface(pygame.Rect(
        index * run_frame_width, 0, run_frame_width, run_frame_height
    ))

# Function to extract a frame from the attack sprite sheet
def get_attack_frame(sheet, index):
    index %= sheet.get_width() // attack_frame_width  # Ensure index is within bounds
    return sheet.subsurface(pygame.Rect(
        index * attack_frame_width, 0, attack_frame_width, attack_frame_height
    ))

# Ground floor settings
ground_y = HEIGHT - 50

# Adjust player_y to ensure the bottom of the image perfectly touches the ground
player_y = ground_y - run_frame_height  # Use the height of the sprite sheet frames

# Remove space_pressed variable
# space_pressed = False
player_direction = "right"

# Load bat idle animation
bat_idle_sheet = pygame.image.load("Character\\Enemies\\Bat\\Bat with VFX\\Bat-WakeUp.png").convert_alpha()
# Update bat idle animation settings
bat_frame_width = bat_idle_sheet.get_width() // 16  # Assuming 16 frames in the sprite sheet
bat_frame_height = bat_idle_sheet.get_height()
bat_frame_index = 0
bat_animation_speed = 5  # Reduce the value to make the bat flap faster
bat_frame_counter = 0

# Load bat idle fly animation
bat_idle_fly_sheet = pygame.image.load("Character\\Enemies\\Bat\\Bat with VFX\\Bat-IdleFly.png").convert_alpha()
bat_idle_fly_frame_width = bat_idle_fly_sheet.get_width() // 9  # Assuming 9 frames in the sprite sheet
bat_idle_fly_frame_height = bat_idle_fly_sheet.get_height()

# Load bat attack animation
bat_attack_sheet = pygame.image.load("Character\\Enemies\\Bat\\Bat with VFX\\Bat-Attack1.png").convert_alpha()
bat_attack_frame_width = bat_attack_sheet.get_width() // 8  # Assuming 8 frames in the sprite sheet
bat_attack_frame_height = bat_attack_sheet.get_height()

# Function to extract a frame from the bat idle sprite sheet
def get_bat_frame(sheet, index):
    index %= sheet.get_width() // bat_frame_width  # Ensure index is within bounds
    return sheet.subsurface(pygame.Rect(
        index * bat_frame_width, 0, bat_frame_width, bat_frame_height
    ))

# Function to extract a frame from the bat idle fly sprite sheet
def get_bat_idle_fly_frame(sheet, index):
    index %= sheet.get_width() // bat_idle_fly_frame_width  # Ensure index is within bounds
    return sheet.subsurface(pygame.Rect(
        index * bat_idle_fly_frame_width, 0, bat_idle_fly_frame_width, bat_idle_fly_frame_height
    ))

# Function to extract a frame from the bat attack sprite sheet
def get_bat_attack_frame(sheet, index):
    index %= sheet.get_width() // bat_attack_frame_width  # Ensure index is within bounds
    return sheet.subsurface(pygame.Rect(
        index * bat_attack_frame_width, 0, bat_attack_frame_width, bat_attack_frame_height
    ))

# Replace enemy settings with bat settings
# Update bat settings to include a timer for idle flying
# Update bat settings to include a flag for damage dealt
bats = []  # Each bat will now have [x, y, state, frame_index, frame_counter, idle_timer, swoop_direction, swoop_cooldown, damage_dealt]
bat_width, bat_height = bat_frame_width, bat_frame_height
bat_spawn_timer = 0
bat_spawn_interval = 120
BAT_STATE_WAKE_UP = "wake_up"
BAT_STATE_IDLE_FLY = "idle_fly"
CHASE_SPEED = 2  # Speed at which the bat chases the player

BAT_ATTACK_COOLDOWN = 180  # 180 frames (3 seconds) cooldown between attacks
BAT_DAMAGE = 5  # Damage dealt by bats

# Add a timer for bat damage intervals
BAT_DAMAGE_INTERVAL = FPS  # 1 second
bat_damage_timer = 0

# Update bat settings
BAT_ATTACK_DELAY = FPS * 2  # 2 seconds delay before attacking
BAT_ATTACK_FRAME_DAMAGE = 5  # 6th frame (index 5) deals damage
BAT_ATTACK_SPEED = 3  # Speed of attack animation
BAT_DAMAGE = 5  # Damage dealt by bats

BAT_STATE_CHASE = "chase"  # Define the chase state for bats

# Update bat settings
BAT_FOLLOW_SPEED = 3  # Speed at which the bat follows the player

# Update bat settings to include a random wake-up duration
BAT_WAKE_UP_MIN_TIME = 0  # Minimum time in seconds
BAT_WAKE_UP_MAX_TIME = 3  # Maximum time in seconds

# Score settings
# score = 0
# font = pygame.font.Font(pygame.font.match_font('arial'), 36)

# High score settings
# high_score_file = "highscore.txt"
# if os.path.exists(high_score_file):
#     with open(high_score_file, "r") as file:
#         high_score = int(file.read().strip())
# else:
#     high_score = 0

# Platform settings
platforms = [
    (136, 454, 278, 20)  # A single platform at (x=300, y=400) with width=200 and height=20
]

running = True

def update_high_score(new_score):
    # global high_score
    # if new_score > high_score:
    #     high_score = new_score
    #     with open(high_score_file, "w") as file:
    #         file.write(str(high_score))
    pass

def end_game_screen():
    # global score
    # update_high_score(score)

    # font_large = pygame.font.Font(None, 74)
    # font_medium = pygame.font.Font(None, 50)
    # text = font_large.render("Game Over", True, (255, 0, 0))
    # score_text = font_medium.render(f"Final Score: {score}", True, (255, 255, 255))
    # high_score_text = font_medium.render(f"High Score: {high_score}", True, (255, 255, 0))
    # retry_text = font_medium.render("Press R to Retry", True, (0, 0, 0))

    # screen.fill((0, 0, 0))
    # screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))
    # screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2.5))
    # screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2))

    # retry_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 60)
    # pygame.draw.rect(screen, (255, 255, 255), retry_rect)
    # pygame.draw.rect(screen, (255, 0, 0), retry_rect, 5)
    # screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + 60))

    # pygame.display.flip()
    pass

def entrance_page():
    title_font = pygame.font.Font(None, 74)
    button_font = pygame.font.Font(None, 50)
    title_text = title_font.render("Samurai Warrior", True, (255, 255, 255))
    play_text = button_font.render("Play", True, (0, 0, 0))

    play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)

    while True:
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

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
                    return  # Proceed directly to the game screen

# Remove the guide screen call and proceed directly to the game
entrance_page()

def death_screen():
    """Display the 'You Died' screen for 10 seconds and return to the home screen."""
    font_large = pygame.font.Font(None, 74)
    text = font_large.render("You Died", True, (255, 0, 0))
    screen.fill((0, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(10000)  # Wait for 10 seconds
    entrance_page()  # Return to the home screen

# Wave settings
wave_number = 1
bats_per_wave = {1: 3, 2: 5, 3: 7}  # Ensure wave 2 spawns 5 bats
wave_font = pygame.font.Font(None, 36)
wave_started = False

# Load background image
background_image = pygame.image.load("Background\\back.png").convert()

# Kill counter settings
kills = 0

while running:
    # Draw the background image first
    screen.blit(background_image, (0, 150))

    # Remove the blue background fill
    # screen.fill(BACKGROUND_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Remove spacebar shooting
                pass
            if event.key == pygame.K_q:
                is_attacking = True
                attack_frame_index = 0
                attack_frame_counter = 0
            # Remove block trigger
            # if event.key == pygame.K_k:
            #     is_blocking = True
            #     block_timer = BLOCK_DURATION
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:  # Remove spacebar shooting
                pass

    keys = pygame.key.get_pressed()
    if is_attacking:
        attack_frame_counter += 1
        if attack_frame_counter >= attack_animation_speed:
            attack_frame_index += 1
            attack_frame_counter = 0
        if attack_frame_index >= 7:  # End attack animation
            is_attacking = False
            attack_frame_index = 0
        else:
            if player_direction == "right":
                current_player_image = get_attack_frame(player_attack_right_sheet, attack_frame_index)
            else:
                current_player_image = get_attack_frame(player_attack_left_sheet, attack_frame_index)

            # Ensure the player's position remains unchanged during the attack
            attack_y = player_y

            # Check for collisions with enemies during attack
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
                    bats.remove(bat)  # Remove bat if hit
                    kills += 1  # Increment kill counter

    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= player_speed
        player_direction = "left"
        frame_counter += 1
        if frame_counter >= run_animation_speed:
            run_frame_index = (run_frame_index + 1) % 7  # Cycle through 6 frames
            frame_counter = 0
        current_player_image = get_run_frame(player_run_left_sheet, run_frame_index)  # Use Run Left animation
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += player_speed
        player_direction = "right"
        frame_counter += 1
        if frame_counter >= run_animation_speed:
            run_frame_index = (run_frame_index + 1) % 7  # Cycle through 6 frames
            frame_counter = 0
        current_player_image = get_run_frame(player_run_right_sheet, run_frame_index)  # Use Run Right animation
    else:
        if player_direction == "right":
            current_player_image = player_idle_right_image  # Idle facing right
        else:
            current_player_image = player_idle_left_image  # Idle facing left
        idle_y_offset = 15  # Move idle image 10 pixels lower

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

    # Remove platform collision checks for the player
    # for platform in platforms:
    #     px, py, pw, ph = platform
    #     if px < player_x + player_width and player_x < px + pw:  # Horizontal collision
    #         if py < player_y + run_frame_height <= py + ph:  # Vertical collision
    #             player_y = py - run_frame_height  # Align the bottom of the player with the top of the platform
    #             player_velocity_y = 0
    #             on_ground = True
    #             break

    if not on_ground:
        on_ground = False

    # Regenerate player health every 10 seconds
    health_regen_timer += 1
    if health_regen_timer >= HEALTH_REGEN_INTERVAL:
        player_health = min(player_health + 5, 100)  # Cap health at 100
        health_regen_timer = 0

    bat_damage_timer += 1


    # Check for collisions with bats during attack
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
                bats.remove(bat)  # Remove bat if hit by an attack

    # Update bat animations and behavior
    for bat in bats:
        if bat[2] == BAT_STATE_WAKE_UP:  # Wake-up animation
            bat[4] += 1
            if bat[4] >= bat_animation_speed:
                bat[3] += 1
                bat[4] = 0
            if bat[3] >= 16 or bat[5] <= 0:  # Transition to idle fly after wake-up completes or time expires
                bat[2] = BAT_STATE_IDLE_FLY
                bat[3] = 0
                bat[5] = 0  # Reset idle timer
            else:
                bat[5] -= 1  # Decrease wake-up timer
        elif bat[2] == BAT_STATE_IDLE_FLY or bat[2] == BAT_STATE_CHASE:  # Idle fly or chase animation
            bat[4] += 1
            if bat[4] >= bat_animation_speed:
                bat[3] = (bat[3] + 1) % 9  # Cycle through 9 frames
                bat[4] = 0

            if bat[2] == BAT_STATE_IDLE_FLY:
                # Increment idle timer
                bat[5] += 1
                if bat[5] >= BAT_ATTACK_DELAY:  # After 2 seconds, transition to follow the player
                    bat[2] = BAT_STATE_CHASE
                    bat[3] = 0  # Reset frame index
                    bat[4] = 0  # Reset frame counter
            elif bat[2] == BAT_STATE_CHASE:
                # Move horizontally toward the middle of the player
                target_x = player_x + player_width // 2 - bat_width // 2
                if bat[0] < target_x:
                    bat[0] += BAT_FOLLOW_SPEED
                elif bat[0] > target_x:
                    bat[0] -= BAT_FOLLOW_SPEED

                # Move vertically toward the middle of the player
                target_y = player_y + player_height // 2 - bat_height // 2
                if bat[1] < target_y:
                    bat[1] += BAT_FOLLOW_SPEED
                elif bat[1] > target_y:
                    bat[1] -= BAT_FOLLOW_SPEED

                # Prevent bats from flying through platforms
                # for platform in platforms:
                #     px, py, pw, ph = platform
                #     if px < bat[0] + bat_width and bat[0] < px + pw:  # Horizontal collision
                #         if py < bat[1] + bat_height <= py + ph:  # Vertical collision
                #             bat[1] = py - bat_height  # Align the bottom of the bat with the top of the platform
                #             break

                # Check if the bat is close enough to the player's middle
                if abs(bat[0] - target_x) <= 5 and abs(bat[1] - target_y) <= 5:
                    # Play attack animation
                    bat[4] += 1
                    if bat[4] >= BAT_ATTACK_SPEED:
                        bat[3] = (bat[3] + 1) % 8  # Cycle through 8 frames
                        bat[4] = 0

                    # Deal damage on the 6th frame
                    if bat[3] == BAT_ATTACK_FRAME_DAMAGE:
                        if (
                            bat[0] < player_x + player_width and
                            bat[0] + bat_width > player_x and
                            bat[1] < player_y + player_height and
                            bat[1] + bat_height > player_y
                        ):
                            player_health -= BAT_DAMAGE
                            player_health = max(player_health, 0)  # Ensure health doesn't go below 0

                    # Return to idle fly after completing the attack animation
                    if bat[3] == 7:  # Last frame of the attack animation
                        bat[2] = BAT_STATE_IDLE_FLY
                        bat[3] = 0
                        bat[4] = 0
                        bat[5] = 0  # Reset idle timer

    # Spawn bats for the current wave
    if not bats and not wave_started:
        wave_started = True
        if wave_number in bats_per_wave:
            bat_positions = []  # Track positions to avoid overlap
            for i in range(bats_per_wave[wave_number]):
                while True:
                    bat_x = random.randint(0, WIDTH - bat_width)  # Random x position within screen width
                    bat_y = 200 - bat_height  # Bottom of the rectangle (0, 0, WIDTH, 200)
                    # Check for overlap with existing bats
                    if all(abs(bat_x - bx) > bat_width for bx, by in bat_positions):
                        bat_positions.append((bat_x, bat_y))
                        wake_up_duration = random.randint(
                            BAT_WAKE_UP_MIN_TIME * FPS, BAT_WAKE_UP_MAX_TIME * FPS
                        )  # Random duration in frames
                        bats.append([bat_x, bat_y, BAT_STATE_WAKE_UP, 0, 0, wake_up_duration, 0, BAT_ATTACK_COOLDOWN, False])  # Initialize bat state
                        break
            player_health = min(player_health + 20, 100)  # Increase health by 20, cap at 100

    # Check if all bats are defeated to move to the next wave
    if wave_started and not bats:
        wave_started = False
        wave_number += 1
        kills = 0  # Reset kill counter
        if wave_number > 3:  # End game after 3 waves
            death_screen()
            wave_number = 1  # Reset wave number
            player_health = 100  # Reset player health
            bats.clear()  # Clear all bats
            continue

    pygame.draw.rect(screen, GROUND_COLOR, (0, ground_y, WIDTH, HEIGHT - ground_y - 100))
    pygame.draw.rect(screen, GROUND_COLOR, (0, 0, WIDTH, 200))
    # Draw player
    if current_player_image in [player_idle_right_image, player_idle_left_image]:
        screen.blit(current_player_image, (player_x, player_y + idle_y_offset))
    else:
        screen.blit(current_player_image, (player_x, player_y))

    # Draw bats
    for bat in bats:
        if bat[2] == BAT_STATE_WAKE_UP:
            current_bat_image = get_bat_frame(bat_idle_sheet, bat[3])
        elif bat[2] == BAT_STATE_IDLE_FLY:
            current_bat_image = get_bat_idle_fly_frame(bat_idle_fly_sheet, bat[3])
        elif bat[2] == BAT_STATE_CHASE:  # Use attack animation
            current_bat_image = get_bat_attack_frame(bat_attack_sheet, bat[3])
        screen.blit(current_bat_image, (bat[0], bat[1]))

    # Remove the platform drawing
    # for platform in platforms:
    #     pygame.draw.rect(screen, PLATFORM_COLOR, platform)

    # Check for collisions with the platform
    for platform in platforms:
        px, py, pw, ph = platform
        if px < player_x + player_width and player_x < px + pw:  # Horizontal collision
            if py < player_y + player_height <= py + ph:  # Vertical collision
                player_y = py - player_height  # Align the bottom of the player with the top of the platform
                player_velocity_y = 0
                on_ground = True
                break

    # Draw health bar
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, health_bar_width, health_bar_height))  # Background (red)
    
    pygame.draw.rect(screen, (0, 255, 0), (10, 10, health_bar_width * (player_health / 100), health_bar_height))  # Foreground (green)

    # Draw wave number
    wave_text = wave_font.render(f"Wave: {wave_number}", True, (255, 255, 255))
    screen.blit(wave_text, (WIDTH - wave_text.get_width() - 10, 10))

    # Draw kill counter
    kill_counter_text = wave_font.render(f"Kills: {kills}/{bats_per_wave[wave_number]}", True, (255, 255, 255))
    screen.blit(kill_counter_text, (WIDTH - kill_counter_text.get_width() - 10, 40))

    # Remove block indicator drawing
    # if is_blocking:
    #     pygame.draw.rect(screen, (0, 0, 255), (10, 40, 100, 20))  # Blue bar indicating block is active

    # Comment out score display
    # score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    # screen.blit(score_text, (12, 12))
    # score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    # screen.blit(score_text, (10, 10))

    # high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
    # screen.blit(high_score_text, (12, 42))
    # high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    # screen.blit(high_score_text, (10, 40))

    # Prevent player from going through the ground or top barrier
    if player_y + player_height > ground_y:
        player_y = ground_y - player_height
        player_velocity_y = 0
        on_ground = True
    if player_y < 200:
        player_y = 200
        player_velocity_y = 0

    # Prevent bats from going through the ground or top barrier
    for bat in bats:
        if bat[1] + bat_height > ground_y:
            bat[1] = ground_y - bat_height
        if bat[1] < 200:
            bat[1] = 200

    # Check if player health is 0
    if player_health <= 0:
        death_screen()
        player_health = 100  # Reset player health
        player_x, player_y = WIDTH // 2, ground_y - player_height  # Reset player position
        bats.clear()  # Clear all bats
        bat_damage_timer = 0  # Reset the damage timer
        continue

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
