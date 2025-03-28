try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import random
import math

# Canvas size
WIDTH, HEIGHT = 1200, 800

# Vector class
class Vector:
    def __init__(self, x, y): 
        self.x, self.y = x, y
    def __add__(self, other): 
        return Vector(self.x + other.x, self.y + other.y)
    def __sub__(self, other): 
        return Vector(self.x - other.x, self.y - other.y)
    def __mul__(self, scalar): 
        return Vector(self.x * scalar, self.y * scalar)
    def __truediv__(self, scalar): 
        return Vector(self.x / scalar, self.y / scalar)
    def distance_to(self, other): 
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    def to_tuple(self): 
        return (self.x, self.y)

# Game states
game_state = "welcome"
game_over = False
paused = False

# Game variables
player_pos = Vector(WIDTH // 2, HEIGHT // 2)
bullets, enemies, powerups = [], [], []
player_size = Vector(100, 100)
score, high_score, kills, wave = 0, 0, 0, 1
fire_rate, speed, frames = 12, 5, 0
move_direction = {"up": False, "down": False, "left": False, "right": False}
hearts = 3

# Powerups
powerup_rate, powertime = 500, 600
powertype = ["Shield", "Rapid Fire", "Slow time"]
rapid_active = slow_active = shield_active = False
rapid_timer = slow_timer = shield_timer = 0

# Enemy settings
enemy_speed, enemy_spawn_rate = 1, 100

# Background image
BACKGROUND_URL = "https://i.postimg.cc/MGKW3XzS/C64-F7-E71-FF55-4993-B546-169-BD3-F0445-D.jpg"
background_img = simplegui.load_image(BACKGROUND_URL)

# Sprite sheet
PLAYER_SPRITE_URL = "https://i.postimg.cc/KcHbNphK/f5f9c273-d809-4446-ad4c-16ff9d255c6d-removalai-preview.png"
ENEMY1_URL = "https://i.postimg.cc/PJ7HSyJB/7-DBB1-F73-01-EF-4194-A354-161-C218-C98-A3.png"
ENEMY2_URL = "https://i.postimg.cc/PJJhb9XW/429-B7-BDA-D325-487-A-BFC4-E6-B979588972.png"   
ENEMY3_URL = "https://i.postimg.cc/qvjLSF4h/1-C4348-EC-C578-4747-B20-D-75-F6-FD192-FDE.png"
ENEMY4_URL = "https://i.postimg.cc/5NJyryXk/C75-FC200-F2-D3-4158-9759-2-CC825-E710-E9.png"

sprite_sheet = simplegui.load_image(PLAYER_SPRITE_URL)
enemy1_img = simplegui.load_image(ENEMY1_URL)
enemy2_img = simplegui.load_image(ENEMY2_URL)
enemy3_img = simplegui.load_image(ENEMY3_URL)
enemy4_img = simplegui.load_image(ENEMY4_URL)
enemy_images = [enemy1_img, enemy2_img, enemy3_img, enemy4_img]


SPRITE_WIDTH, SPRITE_HEIGHT, SPRITE_ROWS, SPRITE_COLS = 600, 453, 8, 8
FRAME_WIDTH, FRAME_HEIGHT = SPRITE_WIDTH / SPRITE_COLS, SPRITE_HEIGHT / SPRITE_ROWS
frame_index, frame_counter = 0, 0

# Clock sprite for Slow Time
SLOW_CLOCK_URL = "https://i.postimg.cc/wBM3jk6D/Chat-GPT-Image-Mar-27-2025-04-16-56-PM.png"
slow_clock_img = simplegui.load_image(SLOW_CLOCK_URL)

# Custom start button area (centered)
start_button_pos = (WIDTH // 2 - 100, HEIGHT // 2 + 20)
start_button_size = (200, 50)

def restart():
    global bullets, enemies, score, wave, kills, enemy_speed, frames, speed, fire_rate
    global player_pos, hearts, game_over, powerups
    global rapid_active, slow_active, shield_active, rapid_timer, slow_timer, shield_timer, paused
    bullets, enemies, powerups = [], [], []
    score, kills, wave, enemy_speed, frames = 0, 0, 1, 1, 0
    speed, fire_rate, hearts = 5, 12, 3
    player_pos = Vector(WIDTH // 2, HEIGHT // 2)
    game_over = False
    paused = False
    rapid_active = slow_active = shield_active = False
    rapid_timer = slow_timer = shield_timer = 0

def shoot():
    bullets.append(Vector(player_pos.x + 17, player_pos.y - 50))

def spawn_enemy():
    enemy_img = random.choice(enemy_images)
    enemies.append((Vector(random.randint(0, WIDTH), 0), enemy_img))

def spawn_powerup():
    pos = Vector(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
    ptype = random.choice(powertype)
    powerups.append({"type": ptype, "pos": pos})

def update():
    global frames, score, player_pos, enemy_speed, high_score, kills, wave
    global frame_index, frame_counter, hearts, game_over
    global rapid_active, rapid_timer, slow_timer, slow_active, shield_active, shield_timer

    if game_over or game_state != "playing" or paused:
        return

    frames += 1

    if rapid_active: rapid_timer -= 1; rapid_active &= rapid_timer > 0
    if slow_active: slow_timer -= 1; slow_active &= slow_timer > 0
    if shield_active: shield_timer -= 1; shield_active &= shield_timer > 0

    movement = Vector(0, 0)
    if move_direction["up"]: movement.y -= speed
    if move_direction["down"]: movement.y += speed
    if move_direction["left"]: movement.x -= speed
    if move_direction["right"]: movement.x += speed
    player_pos += movement

    # Clamp player position to edges (can move all the way to borders)
    player_pos.x = max(0, min(WIDTH, player_pos.x))
    player_pos.y = max(0, min(HEIGHT, player_pos.y))

    if movement.x != 0 or movement.y != 0:
        frame_counter += 1
        if frame_counter % 5 == 0:
            frame_index = (frame_index + 1) % 8
    else:
        frame_index = 1

    for bullet in bullets[:]:
        bullet.y -= 7
        if bullet.y < 0: bullets.remove(bullet)

    current_enemy_speed = enemy_speed * 0.5 if slow_active else enemy_speed
    for enemy in enemies[:]:
        pos, img = enemy
        pos.y += enemy_speed
        if pos.y > HEIGHT:
            enemies.remove(enemy)

    for enemy in enemies[:]:
        pos, img = enemy
        for bullet in bullets[:]:
            if pos.distance_to(bullet) < 30:
               enemies.remove(enemy)
               bullets.remove(bullet)
               score += 1
               kills += 1
               if kills % 30 == 0:
                  wave += 1
                  enemy_speed *= 1.2
               if score > high_score:
                    high_score = score
               break

    for enemy in enemies[:]:
        pos, img = enemy
        if pos.distance_to(player_pos) < 50:
            hearts -= 1
            enemies.remove(enemy)
            if hearts <= 0:
                game_over = True
                breakr = True
                return

    for power in powerups[:]:
        if player_pos.distance_to(power["pos"]) < 30:
            if power["type"] == "Shield":
                shield_active, shield_timer = True, powertime
            elif power["type"] == "Rapid Fire":
                rapid_active, rapid_timer = True, powertime
            elif power["type"] == "Slow time":
                slow_active, slow_timer = True, powertime
            powerups.remove(power)

    if frames % enemy_spawn_rate == 0:
        spawn_enemy()
    if frames % powerup_rate == 0:
        spawn_powerup()
    if frames % (4 if rapid_active else fire_rate) == 0:
        shoot()

def draw(canvas):
    update()

    bg_center = (background_img.get_width() / 2, background_img.get_height() / 2)
    bg_size = (background_img.get_width(), background_img.get_height())
    
    if background_img.get_width() > 0 and background_img.get_height() > 0:
        canvas.draw_image(background_img, bg_center, bg_size, (WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    else:
        canvas.draw_text("Loading background...", (WIDTH / 2 - 150, HEIGHT / 2), 36, "White")

    if game_state == "welcome":
        canvas.draw_text("CYBER ATTACK", (WIDTH/2 - 250, HEIGHT/2 - 100), 64, "Cyan")
        canvas.draw_text("Click the button to start", (WIDTH/2 - 200, HEIGHT/2 - 50), 36, "White")
        x, y = start_button_pos
        w, h = start_button_size
        canvas.draw_polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], 2, "White", "Gray")
        canvas.draw_text("START", (x + 45, y + 35), 30, "Black")
        return

    sprite_center = (FRAME_WIDTH * frame_index + FRAME_WIDTH / 2, FRAME_HEIGHT / 2)
    canvas.draw_image(sprite_sheet, sprite_center, (FRAME_WIDTH, FRAME_HEIGHT), player_pos.to_tuple(), (100, 100), -math.pi/2)

    for bullet in bullets:
        canvas.draw_circle(bullet.to_tuple(), 5, 1, "White", "White")

    for enemy in enemies:
        pos, img = enemy
        canvas.draw_image(img, (img.get_width() / 2, img.get_height() / 2), 
                (img.get_width(), img.get_height()), pos.to_tuple(), (50, 50))

    for power in powerups:
        color = {"Shield": "Yellow", "Rapid Fire": "Blue", "Slow time": "Red"}[power["type"]]
        canvas.draw_circle(power["pos"].to_tuple(), 15, 1, color, color)

    if shield_active:
        canvas.draw_circle(player_pos.to_tuple(), 60, 2, "Yellow")
        canvas.draw_text("Shield Active", (20, 110), 24, "Yellow")
    if rapid_active:
        canvas.draw_text("Rapid Fire Active", (20, 140), 24, "Blue")
    if slow_active:
        canvas.draw_text("Slow Time Active", (60, 170), 24, "Red")
        if slow_clock_img.get_width() > 0:
            canvas.draw_image(
                slow_clock_img,
                (slow_clock_img.get_width() / 2, slow_clock_img.get_height() / 2),
                (slow_clock_img.get_width(), slow_clock_img.get_height()),
                (30, 180),
                (30, 30)
            )

    canvas.draw_text(f"Wave: {wave} | Kills: {kills} | Hearts: {hearts}", (20, 40), 24, "White")
    canvas.draw_text("Press P to Pause/Resume", (20, 70), 24, "White")

    if paused:
        canvas.draw_polygon([(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)], 1, "Black", "rgba(0, 0, 0, 0.5)")
        canvas.draw_text("PAUSED", (WIDTH / 2 - 80, HEIGHT / 2), 50, "White")
        canvas.draw_text("Press P to Resume", (WIDTH / 2 - 170, HEIGHT / 2 + 60), 30, "White")
        canvas.draw_text("Press R to Restart", (WIDTH / 2 - 170, HEIGHT / 2 + 90), 30, "White")
        canvas.draw_text("Press M to Return to Menu", (WIDTH / 2 - 170, HEIGHT / 2 + 120), 30, "White")

    if game_over:
        canvas.draw_polygon([(0,0), (WIDTH,0), (WIDTH,HEIGHT), (0,HEIGHT)], 1, "Black", "rgba(0, 0, 0, 0.7)")
        canvas.draw_text("GAME OVER", (WIDTH / 2 - 150, HEIGHT / 2), 50, "Red")
        canvas.draw_text("Press R to Restart", (WIDTH / 2 - 170, HEIGHT / 2 + 90), 30, "White")
        canvas.draw_text("Press M to Return to Menu", (WIDTH / 2 - 200, HEIGHT / 2 + 120), 30, "White")

def keydown(key):
    global paused
    if game_state == "playing" and not paused:
        if key == simplegui.KEY_MAP['w']: move_direction["up"] = True
        if key == simplegui.KEY_MAP['s']: move_direction["down"] = True
        if key == simplegui.KEY_MAP['a']: move_direction["left"] = True
        if key == simplegui.KEY_MAP['d']: move_direction["right"] = True
    if game_state == "playing" and key == simplegui.KEY_MAP['p']:
        paused = not paused

def keyup(key):
    global game_state, paused
    if game_state == "playing":
        if key == simplegui.KEY_MAP['w']: move_direction["up"] = False
        if key == simplegui.KEY_MAP['s']: move_direction["down"] = False
        if key == simplegui.KEY_MAP['a']: move_direction["left"] = False
        if key == simplegui.KEY_MAP['d']: move_direction["right"] = False
        if key == simplegui.KEY_MAP['r'] and (game_over or paused):
            restart()
        if key == simplegui.KEY_MAP['m'] and (game_over or paused):
            game_state = "welcome"
            paused = False

def start_game():
    global game_state
    game_state = "playing"
    restart()

def click(pos):
    global game_state
    if game_state == "welcome":
        x, y = start_button_pos
        w, h = start_button_size
        if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
            start_game()

# Run game
frame = simplegui.create_frame("Cyber Attack", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)
frame.start()
