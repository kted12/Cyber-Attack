# Import handling with SimpleGUI fallback
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
    """
    2D Vector class for all position/velocity calculations
    Handles vector math operations and conversions
    """
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

# Player class
class Player:
    """
    Player spaceship with movement, shooting, and health systems
    Handles animation frames and boundary checking
    """
    def __init__(self):
        """Initialize player at center with 3 health"""
        self.pos = Vector(WIDTH // 2, HEIGHT // 2)
        self.size = Vector(100, 100)
        self.frame_index = 0
        self.frame_counter = 0
        self.hearts = 3

    def move(self, direction, speed):
        """
        Move player based on keyboard input direction
        Args:
            direction: dict {'up','down','left','right'} bools
            speed: movement speed in pixels/frame
        """
        movement = Vector(0, 0)
        if direction["up"]: movement.y -= speed
        if direction["down"]: movement.y += speed
        if direction["left"]: movement.x -= speed
        if direction["right"]: movement.x += speed
        self.pos += movement
        self.pos.x = max(0, min(WIDTH, self.pos.x))
        self.pos.y = max(0, min(HEIGHT, self.pos.y))

# Interaction class
class Interaction:
    """
    Collision detection utilities
    Static methods for game object interactions
    """
    @staticmethod
    def check_collision(a, b, distance):
        return a.distance_to(b) < distance
    
# Boss class
class Boss:
    """
    Boss enemy class with specialized behaviors per boss type:
    - Tank: High health, circular attack pattern
    - Shooter: Rapid triple-shot attacks  
    - Evader: Dodges player bullets
    """
    def __init__(self, boss_type, image, wave):
        """
        Initialize boss with wave-scaled stats
        Args:
            boss_type: 'tank', 'shooter', or 'evader'
            image: sprite image
            wave: current wave for difficulty scaling
        """
        self.pos = Vector(WIDTH // 2, -100)
        self.size = Vector(150, 150)
        self.image = image
        
        # Wave-scaled stats
        base_health = 25 if boss_type == "tank" else 20
        self.health = base_health + (wave - 1) * 3 

        base_speed = 1 if boss_type == "tank" else 2
        self.speed = min(base_speed + wave * 0.1, 5) 
        
        # Combat systems
        self.boss_type = boss_type
        self.entered_screen = False
        self.direction = 1
        self.bullets = []

        base_delay = 90 if boss_type != "shooter" else 60
        self.fire_delay = max(base_delay - wave * 2, 20)

        self.fire_timer = 0
        self.pattern_timer = 0

        self.name = {
            "tank": "FIREWALL.EXE",
            "shooter": "PACKET STORM",
            "evader": "GLITCH WRAITH"
        }[boss_type]

    def update(self):
        """Update boss position, attacks, and patterns"""
        # Entry animation
        if not self.entered_screen:
            self.pos.y += self.speed
            if self.pos.y >= 150:
                self.entered_screen = True
            return
        
        # Horizontal movement with bouncing
        self.pos.x += self.direction * 3
        if self.pos.x < 100 or self.pos.x > WIDTH - 100:
            self.direction *= -1
        
        # Type-specific behaviors
        if self.boss_type == "evader":
            for bullet in GAME.bullets:
                if abs(bullet.y - self.pos.y) < 150 and abs(bullet.x - self.pos.x) < 60:
                    self.pos.x += random.choice([-20, 20])
                    break

        self.fire_timer += 1
        self.pattern_timer += 1

        if self.boss_type == "tank":
            if self.pattern_timer % 180 == 0:
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    dx = math.cos(rad) * 5
                    dy = math.sin(rad) * 5
                    self.bullets.append({"pos": Vector(self.pos.x, self.pos.y), "vel": Vector(dx, dy)})

        elif self.boss_type == "shooter":
            if self.fire_timer >= self.fire_delay:
                self.fire_timer = 0
                for dx in [-2, 0, 2]:
                    self.bullets.append({"pos": Vector(self.pos.x, self.pos.y + 50), "vel": Vector(dx, 5)})

        elif self.boss_type == "evader":
            if self.pattern_timer % 240 == 0:
                self.pos.x = random.randint(100, WIDTH - 100)
                self.pos.y = 150 + random.randint(-50, 50)

        for bullet in self.bullets[:]:
            bullet["pos"] += bullet["vel"]
            if bullet["pos"].y > HEIGHT or bullet["pos"].x < 0 or bullet["pos"].x > WIDTH:
                self.bullets.remove(bullet)

    def draw(self, canvas):
        """Draw boss sprite and health bar"""
        # Boss sprite
        canvas.draw_image(self.image,
            (self.image.get_width() / 2, self.image.get_height() / 2),
            (self.image.get_width(), self.image.get_height()),
            self.pos.to_tuple(), self.size.to_tuple())
        
        # Projectiles
        for bullet in self.bullets:
            canvas.draw_circle(bullet["pos"].to_tuple(), 7, 1, "Red", "Red")
        
        # Health bar
        bar_width = 200
        bar_height = 20
        bar_x = self.pos.x - bar_width / 2
        bar_y = self.pos.y - self.size.y / 2 - 30
        max_health = 25 if self.boss_type == "tank" else 20
        health_ratio = self.health / max_health
        
        # Background bar
        canvas.draw_polygon([(bar_x, bar_y), (bar_x + bar_width, bar_y),
                            (bar_x + bar_width, bar_y + bar_height), (bar_x, bar_y + bar_height)], 1, "White", "Gray")
        
        # Health fill
        canvas.draw_polygon([(bar_x, bar_y), (bar_x + bar_width * health_ratio, bar_y),
                            (bar_x + bar_width * health_ratio, bar_y + bar_height), (bar_x, bar_y + bar_height)], 1, "Red", "Red")



# Game class
class Game:
    """
    Main game controller class managing:
    - Game state (menu/playing/game over)
    - Object spawning
    - Wave progression
    - Power-up systems
    - Collision handling
    - Rendering pipeline
    """
    def __init__(self):
        """Initialize all game systems and load assets"""
        # Game state tracking
        self.state = "welcome"
        self.game_over = False
        self.paused = False
        self.player = Player()
        self.bullets, self.enemies, self.powerups = [], [], []
        self.move_direction = {"up": False, "down": False, "left": False, "right": False}
    
        self.score = self.high_score = self.kills = 0
        self.wave = 1
        self.speed, self.fire_rate, self.frames = 5, 12, 0
        self.wave_popup_timer = 0
        self.wave_popup_text = ""

        self.powerup_rate, self.powertime = 500, 600
        self.powertype = ["Shield", "Rapid Fire", "Slow time"]
        self.rapid_active = self.slow_active = self.shield_active = False
        self.rapid_timer = self.slow_timer = self.shield_timer = 0

        self.enemy_speed, self.enemy_spawn_rate = 1, 100

        # Load images
        self.background_img = simplegui.load_image("https://i.postimg.cc/sDQ6rvVd/FDE305-EE-FE9-E-4238-8-C89-6-C1-C522-C7-E09.png")
        self.player_img = simplegui.load_image("https://i.postimg.cc/8zrqTJX8/FEEFEE13-2510-4598-897-F-A63-B40230-C05.png")
        self.slow_clock_img = simplegui.load_image("https://i.postimg.cc/Y2sXHQ34/clock-e.png")
        self.shield_img = simplegui.load_image("https://i.postimg.cc/65FVwnMy/SHIELDTRAN.png")
        self.rapid_img = simplegui.load_image("https://i.postimg.cc/2SpWgm5W/BULLETTRAN.png")
        
        self.enemy_images = [
            simplegui.load_image(url) for url in [
                "https://i.postimg.cc/PJ7HSyJB/7-DBB1-F73-01-EF-4194-A354-161-C218-C98-A3.png",
                "https://i.postimg.cc/PJJhb9XW/429-B7-BDA-D325-487-A-BFC4-E6-B979588972.png",
                "https://i.postimg.cc/qvjLSF4h/1-C4348-EC-C578-4747-B20-D-75-F6-FD192-FDE.png",
                "https://i.postimg.cc/5NJyryXk/C75-FC200-F2-D3-4158-9759-2-CC825-E710-E9.png"
            ]
        ]

        self.start_button_pos = (WIDTH // 2 - 100, HEIGHT // 2 + 20)
        self.start_button_size = (200, 50)
        
        self.boss = None
        self.in_boss_fight = False
        self.boss_images = {
            "tank": simplegui.load_image("https://i.postimg.cc/FKMN04Jb/image.png"),
            "shooter": simplegui.load_image("https://i.postimg.cc/mrHGL56P/image.png"),
            "evader": simplegui.load_image("https://i.postimg.cc/7L6fKw6p/image.png")
        }

    def start_game(self):
        """Transition from menu to gameplay state"""
        self.state = "playing"
        self.restart()

    def restart(self):
        """Reset all game systems for a new game"""
        self.bullets, self.enemies, self.powerups = [], [], []
        self.score = self.kills = self.wave = self.frames = 0
        self.speed, self.fire_rate, self.enemy_speed = 5, 12, 1
        self.player = Player()
        self.game_over = False
        self.paused = False
        self.rapid_active = self.slow_active = self.shield_active = False
        self.rapid_timer = self.slow_timer = self.shield_timer = 0
        self.wave_popup_timer = 0
        self.move_direction = {"up": False, "down": False, "left": False, "right": False} 

    def shoot(self):
        """Fire a new player projectile"""
        bullet_x = self.player.pos.x
        bullet_y = self.player.pos.y - self.player.size.y / 2
        self.bullets.append(Vector(bullet_x, bullet_y))

    def spawn_enemy(self):
        """Create a new enemy at random top position"""
        img = random.choice(self.enemy_images)
        self.enemies.append((Vector(random.randint(0, WIDTH), 0), img))

    def spawn_powerup(self):
        """Create a random power-up at random position"""
        pos = Vector(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.powerups.append({"type": random.choice(self.powertype), "pos": pos})

    def update(self):
        """
        Main game update loop called every frame:
        1. Handle game state
        2. Update all objects
        3. Check collisions
        4. Spawn new objects
        """
        
        # State checks
        if self.game_over or self.state != "playing":
            return

        # Handle wave popup timer (no longer pauses the game)
        if self.wave_popup_timer > 0:
            self.wave_popup_timer -= 1

        # Don't return early if paused - we want the wave popup to show during "paused" state
        if self.paused and self.wave_popup_timer <= 0:
            return

        self.frames += 1
        
        # Boss logic
        if self.in_boss_fight and self.boss:
            self.boss.update()
            for bullet in self.bullets[:]:
                if Interaction.check_collision(bullet, self.boss.pos, 80):
                    self.bullets.remove(bullet)
                    self.boss.health -= 1
                    

                    if self.boss.health <= 0:
                        self.boss = None
                        self.in_boss_fight = False
                        self.enemy_speed *= 1.1
                        break
            if self.boss:
                for bullet in self.boss.bullets[:]:
                    if Interaction.check_collision(bullet["pos"], self.player.pos, 30):
                        if not self.shield_active:
                            self.player.hearts -= 1
                        self.boss.bullets.remove(bullet)
                        if self.player.hearts <= 0:
                            self.game_over = True
                            break
        if self.rapid_active: self.rapid_timer -= 1; self.rapid_active &= self.rapid_timer > 0
        if self.slow_active: self.slow_timer -= 1; self.slow_active &= self.slow_timer > 0
        if self.shield_active: self.shield_timer -= 1; self.shield_active &= self.shield_timer > 0

        self.player.move(self.move_direction, self.speed)

        for bullet in self.bullets[:]:
            bullet.y -= 7
            if bullet.y < 0:
                self.bullets.remove(bullet)

        # Enemy logic
        current_enemy_speed = self.enemy_speed * 0.5 if self.slow_active else self.enemy_speed
        for enemy in self.enemies[:]:
            pos, _ = enemy
            pos.y += current_enemy_speed
            if pos.y > HEIGHT:
                self.enemies.remove(enemy)

        for enemy in self.enemies[:]:
            pos, _ = enemy
            for bullet in self.bullets[:]:
                if Interaction.check_collision(pos, bullet, 30):
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    self.score += 1
                    self.kills += 1

                    if self.kills % 10 == 0:
                        self.wave += 1
                        self.wave_popup_text = f"WAVE {self.wave}"
                        self.wave_popup_timer = 60

                        if self.wave % 5 == 0:
                            self.in_boss_fight = True
                            boss_type = random.choice(["tank", "shooter", "evader"])
                            self.boss = Boss(boss_type, self.boss_images[boss_type], self.wave)

                            
                        else:
                            self.enemy_speed *= 1.1

                    if self.score > self.high_score:
                        self.high_score = self.score
                    break


        for enemy in self.enemies[:]:
            pos, _ = enemy
            if Interaction.check_collision(pos, self.player.pos, 50):
                if not self.shield_active:
                    self.player.hearts -= 1
                self.enemies.remove(enemy)
                if self.player.hearts <= 0:
                    self.game_over = True
                    break
        
        # Powerup logic
        for power in self.powerups[:]:
            if Interaction.check_collision(self.player.pos, power["pos"], 30):
                if power["type"] == "Shield":
                    self.shield_active, self.shield_timer = True, self.powertime
                elif power["type"] == "Rapid Fire":
                    self.rapid_active, self.rapid_timer = True, self.powertime
                elif power["type"] == "Slow time":
                    self.slow_active, self.slow_timer = True, self.powertime
                self.powerups.remove(power)

        if not self.in_boss_fight:
            if self.frames % self.enemy_spawn_rate == 0:
                self.spawn_enemy()
        if self.frames % self.powerup_rate == 0:
            self.spawn_powerup()
        if self.frames % (4 if self.rapid_active else self.fire_rate) == 0:
            self.shoot()

# Game instance
GAME = Game()

def draw(canvas):
    GAME.update()

    # Background
    bg_center = (GAME.background_img.get_width() / 2, GAME.background_img.get_height() / 2)
    bg_size = (GAME.background_img.get_width(), GAME.background_img.get_height())
    if GAME.background_img.get_width() > 0:
        canvas.draw_image(GAME.background_img, bg_center, bg_size, (WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # Welcome screen
    if GAME.state == "welcome":
        canvas.draw_text("CYBER ATTACK", (WIDTH/2 - 250, HEIGHT/2 - 100), 64, "Cyan")
        canvas.draw_text("Click the button to start", (WIDTH/2 - 200, HEIGHT/2 - 50), 36, "White")
        x, y = GAME.start_button_pos
        w, h = GAME.start_button_size
        canvas.draw_polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], 2, "White", "Gray")
        canvas.draw_text("START", (x + 45, y + 35), 30, "Black")
        return

    # Player
    image_width = GAME.player_img.get_width()
    image_height = GAME.player_img.get_height()
    image_center = (image_width / 2, image_height / 2)
    canvas.draw_image(GAME.player_img, image_center, (image_width, image_height), GAME.player.pos.to_tuple(), (100, 100), 0)

    # Bullets
    for bullet in GAME.bullets:
        canvas.draw_circle(bullet.to_tuple(), 5, 1, "White", "White")

    # Enemies
    for pos, img in GAME.enemies:
        canvas.draw_image(img, (img.get_width() / 2, img.get_height() / 2), (img.get_width(), img.get_height()), pos.to_tuple(), (50, 50))

    # Powerups
    for power in GAME.powerups:
        pos = power["pos"].to_tuple()
        if power["type"] == "Shield":
            canvas.draw_image(GAME.shield_img, (GAME.shield_img.get_width()/2, GAME.shield_img.get_height()/2), (GAME.shield_img.get_width(), GAME.shield_img.get_height()), pos, (40, 40))
        elif power["type"] == "Rapid Fire":
            canvas.draw_image(GAME.rapid_img, (GAME.rapid_img.get_width()/2, GAME.rapid_img.get_height()/2), (GAME.rapid_img.get_width(), GAME.rapid_img.get_height()), pos, (40, 40))
        elif power["type"] == "Slow time":
            canvas.draw_image(GAME.slow_clock_img, (GAME.slow_clock_img.get_width()/2, GAME.slow_clock_img.get_height()/2), (GAME.slow_clock_img.get_width(), GAME.slow_clock_img.get_height()), pos, (50, 37.5))

    # Boss
    if GAME.boss:
        GAME.boss.draw(canvas)

    # UI Elements
    canvas.draw_polygon([(10, 10), (380, 10), (380, 50), (10, 50)], 2, "Blue", "Blue")
    canvas.draw_text(f"Wave: {GAME.wave} | Kills: {GAME.kills} | Hearts: {GAME.player.hearts}", (20, 40), 24, "White")

    # Boss HUD
    if GAME.boss:
        boss = GAME.boss
        canvas.draw_text(f"Boss: {boss.name}", (WIDTH / 2 - 150, 40), 28, "Cyan")
        hud_bar_width = 300
        hud_bar_height = 20
        hud_bar_x = WIDTH / 2 - hud_bar_width / 2
        hud_bar_y = 60
        max_health = 25 if boss.boss_type == "tank" else 20
        health_ratio = boss.health / max_health
        canvas.draw_polygon([
            (hud_bar_x, hud_bar_y),
            (hud_bar_x + hud_bar_width, hud_bar_y),
            (hud_bar_x + hud_bar_width, hud_bar_y + hud_bar_height),
            (hud_bar_x, hud_bar_y + hud_bar_height)
        ], 1, "White", "Gray")
        canvas.draw_polygon([
            (hud_bar_x, hud_bar_y),
            (hud_bar_x + hud_bar_width * health_ratio, hud_bar_y),
            (hud_bar_x + hud_bar_width * health_ratio, hud_bar_y + hud_bar_height),
            (hud_bar_x, hud_bar_y + hud_bar_height)
        ], 1, "Red", "Red")

    canvas.draw_polygon([(690, 10), (1190, 10), (1190, 50), (690, 50)], 2, "White", "Black")
    canvas.draw_text("Press R to Restart | Press P to Pause/Resume", (700, 35), 24, "White")

    # Powerup indicators
    y_offset = 110
    if GAME.shield_active:
        canvas.draw_text("Shield Active", (60, y_offset), 24, "Yellow")
        canvas.draw_image(GAME.shield_img, (GAME.shield_img.get_width()/2, GAME.shield_img.get_height()/2), (GAME.shield_img.get_width(), GAME.shield_img.get_height()), (30, y_offset), (30, 30))
        y_offset += 30

    if GAME.rapid_active:
        canvas.draw_text("Rapid Fire Active", (60, y_offset), 24, "Yellow")
        canvas.draw_image(GAME.rapid_img, (GAME.rapid_img.get_width()/2, GAME.rapid_img.get_height()/2), (GAME.rapid_img.get_width(), GAME.rapid_img.get_height()), (30, y_offset), (30, 30))
        y_offset += 30

    if GAME.slow_active:
        canvas.draw_text("Slow Time Active", (60, y_offset), 24, "Yellow")
        canvas.draw_image(GAME.slow_clock_img, (GAME.slow_clock_img.get_width()/2, GAME.slow_clock_img.get_height()/2), (GAME.slow_clock_img.get_width(), GAME.slow_clock_img.get_height()), (30, y_offset), (40, 30))

    # Wave popup
    if GAME.wave_popup_timer > 0:
        canvas.draw_text(GAME.wave_popup_text, (WIDTH // 2 - 100, HEIGHT // 2), 60, "Orange")

    # Paused screen
    if GAME.paused and GAME.wave_popup_timer <= 0:
        canvas.draw_polygon([(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)], 1, "Black", "rgba(0, 0, 0, 0.5)")
        canvas.draw_text("PAUSED", (WIDTH / 2 - 80, HEIGHT / 2), 50, "White")
        canvas.draw_text("Press M to Return to Menu", (WIDTH / 2 - 200, HEIGHT / 2 + 110), 30, "White")

    # Game over screen
    if GAME.game_over:
        canvas.draw_polygon([(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)], 1, "Black", "rgba(0, 0, 0, 0.7)")
        canvas.draw_text("GAME OVER", (WIDTH / 2 - 150, HEIGHT / 2), 50, "Red")
        canvas.draw_text("Press R to Restart", (WIDTH / 2 - 170, HEIGHT / 2 + 60), 30, "White")
        canvas.draw_text("Press M to Return to Menu", (WIDTH / 2 - 200, HEIGHT / 2 + 110), 30, "White")

def keydown(key):
    if GAME.state == "playing":
        if key == simplegui.KEY_MAP['w']: GAME.move_direction["up"] = True
        if key == simplegui.KEY_MAP['s']: GAME.move_direction["down"] = True
        if key == simplegui.KEY_MAP['a']: GAME.move_direction["left"] = True
        if key == simplegui.KEY_MAP['d']: GAME.move_direction["right"] = True
        if key == simplegui.KEY_MAP['p']:
            # Only toggle pause if we're not showing a wave popup
            if GAME.wave_popup_timer <= 0:
                GAME.paused = not GAME.paused

def keyup(key):
    if GAME.state == "playing":
        if key == simplegui.KEY_MAP['w']: GAME.move_direction["up"] = False
        if key == simplegui.KEY_MAP['s']: GAME.move_direction["down"] = False
        if key == simplegui.KEY_MAP['a']: GAME.move_direction["left"] = False
        if key == simplegui.KEY_MAP['d']: GAME.move_direction["right"] = False
        if key == simplegui.KEY_MAP['r']:
            GAME.restart()
        if key == simplegui.KEY_MAP['m']:
            GAME.restart()
            GAME.state = "welcome"

def click(pos):
    if GAME.state == "welcome":
        x, y = GAME.start_button_pos
        w, h = GAME.start_button_size
        if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
            GAME.start_game()

# Run game
frame = simplegui.create_frame("Cyber Attack", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)
frame.start()