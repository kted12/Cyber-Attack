try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import random
import math

# Canvas size
WIDTH, HEIGHT = 1200, 800

class Vector:
    """A simple 2D vector class for handling positions and movement."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

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


# Game variables
player_pos = Vector(WIDTH // 2, HEIGHT // 2)
player_size = Vector(100, 100)  # Adjusted size for sprite
bullets = []
enemies = []
score = 0
high_score = 0
fire_rate = 12  
speed = 5  
move_direction = {"up": False, "down": False, "left": False, "right": False}
frames = 0
hearts = 3
game_over = False 


powerup_rate = 500
powertime = 300
powerups = []
powertype = ["Shield","Rapid Fire","Slow time"]
rapid_active = False
rapid_timer = 0
slow_active = False
slow_timer = 0
shield_active = False
shield_timer = 0

# Enemy settings
enemy_speed = 1
enemy_spawn_rate = 100
wave = 1
kills = 0

# Load sprite sheet (dummy link for demonstration)
SPRITE_URL = "https://i.postimg.cc/KcHbNphK/f5f9c273-d809-4446-ad4c-16ff9d255c6d-removalai-preview.png"  # Replace with actual PNG direct link
sprite_sheet = simplegui.load_image(SPRITE_URL)

# Sprite properties
SPRITE_WIDTH, SPRITE_HEIGHT = 600, 453  # Full sprite sheet size
SPRITE_ROWS = 8  
SPRITE_COLS = 8  
FRAME_WIDTH = SPRITE_WIDTH / SPRITE_COLS  # Each frame width
FRAME_HEIGHT = SPRITE_HEIGHT / SPRITE_ROWS  # Each frame height
frame_index = 0  
frame_counter = 0  

def restart():
    global bullets, enemies, score, high_score, enemy_speed, frames, speed, fire_rate, wave, kills, player_pos,hearts,game_over,powerups
    global rapid_active, rapid_timer, slow_timer, slow_active,  shield_active, shield_timer
    powerups = []
    bullets = []
    enemies = []

    score = 0
    kills = 0
    wave = 1
    enemy_speed = 1
    frames = 0
    speed = 5
    fire_rate = 12
    player_pos = Vector(WIDTH // 2, HEIGHT // 2)
    hearts = 3
    game_over = False 
    powerups = []
    rapid_active = False
    rapid_timer = 0
    slow_active = False
    slow_timer = 0
    shield_active = False
    shield_timer = 0




def update():
    global frames, score, player_pos, enemy_speed, high_score, kills, wave, frame_index, frame_counter,hearts,game_over,powerup_rate
    global rapid_active, rapid_timer, slow_timer, slow_active,  shield_active, shield_timer 

    frames += 1

    if game_over:
        return
    
    if rapid_active:
        rapid_timer -= 1
        if rapid_timer <= 0:
            rapid_active = False
    if slow_active:
        slow_timer -= 1
        if slow_timer<= 0:
            slow_active = False
    if shield_active:
        shield_timer -= 1
        if shield_timer <= 0:
            shield_active = False

    # Move player with keys
    movement = Vector(0, 0)
    moving = False  # Check if player is moving
    if move_direction["up"] and player_pos.y > 0:
        movement.y -= speed
        moving = True
    if move_direction["down"] and player_pos.y < HEIGHT:
        movement.y += speed
        moving = True
    if move_direction["left"] and player_pos.x > 0:
        movement.x -= speed
        moving = True
    if move_direction["right"] and player_pos.x < WIDTH:
        movement.x += speed
        moving = True

    # Apply movement
    player_pos = player_pos + movement

    # Update animation frame
    if moving:
        frame_counter += 1
        if frame_counter % 5 == 0:  # Slow down animation
            frame_index = (frame_index + 1) % 8  # Loop through first row
    else:
        frame_index = 1  # Set to standing frame

    # Bullet movement
    for bullet in bullets[:]:
        bullet.y -= 7  
        if bullet.y < 0:
            bullets.remove(bullet)

    
    if slow_active:
        currentenem_speed = enemy_speed * 0.5
    else:
        currentenem_speed = enemy_speed

    
    # Enemy movement
    for enemy in enemies[:]:
        enemy.y += currentenem_speed
        if enemy.y > HEIGHT:
            enemies.remove(enemy)

    # Collision detection
    for enemy in enemies[:]:
        for bullet in bullets[:]:
            if enemy.distance_to(bullet) < 15:
                enemies.remove(enemy)
                bullets.remove(bullet)
                kills += 1
                score += 1
                if kills % 50 == 0:
                    wave += 1
                    enemy_speed *= 1.5
                if score > high_score:
                    high_score = score
                break
    
    for enemy in enemies[:]:
        if enemy.distance_to(Vector(player_pos.x + 10, player_pos.y)) < 55 :
            if not(shield_active):
                hearts -= 1
            enemies.remove(enemy)
            if hearts <= 0:
                game_over = True
                break
    
    for power in powerups[:]:
        if player_pos.distance_to(power["pos"]) < 30:
            if power["type"] == "Shield":
                shield_active = True
                shield_timer = powertime
            elif power["type"] == "Rapid Fire":
                rapid_active = True
                rapid_timer = powertime
            elif power["type"] == "Slow time":
                slow_active = True
                slow_timer = powertime
            powerups.remove(power)

    # Enemy spawning
    if frames % enemy_spawn_rate == 0:
        spawn_enemy()

    # Bullet firing
    if rapid_active:
        currentfire = 4
    else:
        currentfire = fire_rate

    
    if frames % currentfire == 0:
        shoot()
    
    if frames % powerup_rate == 0:
        spawn_powerup()
    


def shoot():
    bullets.append(Vector(player_pos.x +17, player_pos.y - 50))

def spawn_enemy():
    pos = Vector(random.randint(0, WIDTH), 0)  
    enemies.append(pos)


def spawn_powerup():
     
     pos = Vector(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
     powtype = random.choice(powertype)

     powerups.append({"type": powtype, "pos": pos})


         


    



def draw(canvas):
    update()

    # Draw player sprite with a 90° anticlockwise rotation (-pi/2)
    sprite_center = (FRAME_WIDTH * frame_index + FRAME_WIDTH / 2, FRAME_HEIGHT / 2)
    sprite_dest = (player_pos.x, player_pos.y)
    canvas.draw_image(sprite_sheet, sprite_center, (FRAME_WIDTH, FRAME_HEIGHT), sprite_dest, (100, 100), -math.pi/2)  # <-- Rotates anticlockwise

    # Draw bullets
    for bullet in bullets:
        canvas.draw_circle(bullet.to_tuple(), 5, 1, "White", "White")

    # Draw enemies
    for enemy in enemies:
        for i in range(wave):
            canvas.draw_circle(enemy.to_tuple(), 15, 1, "Green", "Green")

    for power in powerups:
        if power["type"] == "Shield":
            color = "Yellow"
        elif power["type"] == "Rapid Fire":
            color = "Blue"
        elif power["type"] == "Slow time":
            color = "Red"
        canvas.draw_circle(power["pos"].to_tuple(), 15, 1, color, color)
        
    if shield_active:
        canvas.draw_text("Shield Active", (20, 110), 24, "Yellow")
    if rapid_active:
        canvas.draw_text("Rapid Fire Active", (20, 140), 24, "Blue")
    if slow_active:
        canvas.draw_text("Slow Time Active", (20, 170), 24, "Red")


    # Draw score, wave
    canvas.draw_text(f"Wave: {wave} | Kills: {kills} | Hearts: {hearts}", (20, 40), 24, "White")
    canvas.draw_text("Press R to restart", (20, 70), 24, "White")
    if shield_active:
        canvas.draw_circle(player_pos.to_tuple(), 60, 2, "Yellow")

    if game_over:
        canvas.draw_polygon([(0,0), (WIDTH,0), (WIDTH,HEIGHT), (0,HEIGHT)], 1, "Black", "rgba(0, 0, 0, 0.7)")
        canvas.draw_text("GAME OVER", (WIDTH / 2 - 150, HEIGHT / 2), 50, "Red")
        canvas.draw_text("Press R to restart", (WIDTH / 2 - 170, HEIGHT / 2 + 60), 30, "White")


def keydown(key):
    if key == simplegui.KEY_MAP['w']:
        move_direction["up"] = True
    elif key == simplegui.KEY_MAP['s']:
        move_direction["down"] = True
    elif key == simplegui.KEY_MAP['a']:
        move_direction["left"] = True
    elif key == simplegui.KEY_MAP['d']:
        move_direction["right"] = True

def keyup(key):
    if key == simplegui.KEY_MAP['w']:
        move_direction["up"] = False
    elif key == simplegui.KEY_MAP['s']:
        move_direction["down"] = False
    elif key == simplegui.KEY_MAP['a']:
        move_direction["left"] = False
    elif key == simplegui.KEY_MAP['d']:
        move_direction["right"] = False
    elif key == simplegui.KEY_MAP['r']:
        restart()

# Start the game
frame = simplegui.create_frame("Shooter Game", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.start()



#dejvjkdfbvjkfbvjkdfnvjkdfnji fdnk nfdj modf