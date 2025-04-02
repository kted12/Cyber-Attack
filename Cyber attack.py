# Import handling with SimpleGUI fallback
try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import random
import math

# ===== GAME CONSTANTS =====
WIDTH, HEIGHT = 1200, 800  # Game window dimensions

class Vector:
    """
    2D Vector class for all position/velocity calculations
    Handles vector math operations and conversions
    """
    def __init__(self, x, y):
        """Initialize with x,y coordinates"""
        self.x, self.y = x, y

    def __add__(self, other):
        """Vector addition - returns new Vector"""
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Vector subtraction - returns new Vector"""
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        """Scalar multiplication - returns new Vector"""
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        """Scalar division - returns new Vector"""
        return Vector(self.x / scalar, self.y / scalar)

    def distance_to(self, other):
        """Calculate Euclidean distance to another Vector"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def to_tuple(self):
        """Convert to (x,y) tuple for drawing functions"""
        return (self.x, self.y)

class Player:
    """
    Player spaceship with movement, shooting, and health systems
    Handles animation frames and boundary checking
    """
    def __init__(self):
        """Initialize player at center with 3 health"""
        self.pos = Vector(WIDTH // 2, HEIGHT // 2)
        self.size = Vector(100, 100)
        self.frame_index = 0    # Current animation frame
        self.frame_counter = 0  # Frame counter for animation timing
        self.hearts = 3         # Player health

    def move(self, direction, speed):
        """
        Move player based on keyboard input direction
        Args:
            direction: dict {'up','down','left','right'} bools
            speed: movement speed in pixels/frame
        """
        movement = Vector(0, 0)
        # Accumulate movement vectors
        if direction["up"]: movement.y -= speed
        if direction["down"]: movement.y += speed
        if direction["left"]: movement.x -= speed
        if direction["right"]: movement.x += speed
        
        # Update position with boundary checking
        self.pos += movement
        self.pos.x = max(0, min(WIDTH, self.pos.x))
        self.pos.y = max(0, min(HEIGHT, self.pos.y))

        # Handle animation
        if movement.x != 0 or movement.y != 0:
            self.frame_counter += 1
            if self.frame_counter % 5 == 0:  # Every 5 frames
                self.frame_index = (self.frame_index + 1) % 8  # 8-frame animation
        else:
            self.frame_index = 1  # Default frame when not moving

class Interaction:
    """
    Collision detection utilities
    Static methods for game object interactions
    """
    @staticmethod
    def check_collision(a, b, distance):
        """
        Check if two Vector positions are within collision distance
        Args:
            a, b: Vector objects to check
            distance: minimum collision distance
        Returns:
            bool: True if collision detected
        """
        return a.distance_to(b) < distance

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
        self.pos = Vector(WIDTH // 2, -100)  # Start above screen
        self.size = Vector(150, 150)
        self.image = image
        self.boss_type = boss_type
        
        # Wave-scaled stats
        base_health = 25 if boss_type == "tank" else 20
        self.health = base_health + (wave - 1) * 3  # +3 HP per wave
        
        base_speed = 1 if boss_type == "tank" else 2
        self.speed = min(base_speed + wave * 0.1, 5)  # Speed cap at 5
        
        # Combat systems
        self.bullets = []  # Active projectiles
        base_delay = 90 if boss_type != "shooter" else 60
        self.fire_delay = max(base_delay - wave * 2, 20)  # Faster attacks
        
        # State tracking
        self.entered_screen = False
        self.direction = 1  # Left/right movement
        self.fire_timer = 0
        self.pattern_timer = 0
        
        # Boss metadata
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
            self._update_evader()
        elif self.boss_type == "tank":
            self._update_tank()
        elif self.boss_type == "shooter":
            self._update_shooter()

        # Update projectiles
        for bullet in self.bullets[:]:  # Iterate copy for safe removal
            bullet["pos"] += bullet["vel"]
            if (bullet["pos"].y > HEIGHT or 
                bullet["pos"].x < 0 or 
                bullet["pos"].x > WIDTH):
                self.bullets.remove(bullet)

    def _update_evader(self):
        """Evader-specific update logic"""
        # Dodge player bullets
        for bullet in GAME.bullets:
            if (abs(bullet.y - self.pos.y) < 150 and 
                abs(bullet.x - self.pos.x) < 60):
                self.pos.x += random.choice([-20, 20])
                break
        
        # Random teleport
        if self.pattern_timer % 240 == 0:
            self.pos.x = random.randint(100, WIDTH - 100)
            self.pos.y = 150 + random.randint(-50, 50)

    def _update_tank(self):
        """Tank-specific update logic"""
        # Circular attack pattern
        if self.pattern_timer % 180 == 0:
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                dx = math.cos(rad) * 5
                dy = math.sin(rad) * 5
                self.bullets.append({
                    "pos": Vector(self.pos.x, self.pos.y),
                    "vel": Vector(dx, dy)
                })

    def _update_shooter(self):
        """Shooter-specific update logic"""
        # Triple-shot attack
        if self.fire_timer >= self.fire_delay:
            self.fire_timer = 0
            for dx in [-2, 0, 2]:
                self.bullets.append({
                    "pos": Vector(self.pos.x, self.pos.y + 50),
                    "vel": Vector(dx, 5)
                })

    def draw(self, canvas):
        """Draw boss sprite and health bar"""
        # Boss sprite
        canvas.draw_image(
            self.image,
            (self.image.get_width() / 2, self.image.get_height() / 2),
            (self.image.get_width(), self.image.get_height()),
            self.pos.to_tuple(), 
            self.size.to_tuple()
        )
        
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
        canvas.draw_polygon([
            (bar_x, bar_y),
            (bar_x + bar_width, bar_y),
            (bar_x + bar_width, bar_y + bar_height),
            (bar_x, bar_y + bar_height)
        ], 1, "White", "Gray")
        
        # Health fill
        canvas.draw_polygon([
            (bar_x, bar_y),
            (bar_x + bar_width * health_ratio, bar_y),
            (bar_x + bar_width * health_ratio, bar_y + bar_height),
            (bar_x, bar_y + bar_height)
        ], 1, "Red", "Red")
        
        
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
        self.state = "welcome"  # welcome/playing/game_over
        self.game_over = False
        self.paused = False
        
        # Game objects
        self.player = Player()
        self.bullets = []    # Player projectiles
        self.enemies = []    # Regular enemies (pos, image)
        self.powerups = []   # Active power-ups
        self.boss = None     # Current boss instance
        self.in_boss_fight = False
        
        # Game progression
        self.score = 0
        self.high_score = 0
        self.kills = 0
        self.wave = 1
        self.frames = 0      # Total frames elapsed
        
        # Player systems
        self.move_direction = {
            "up": False, 
            "down": False, 
            "left": False, 
            "right": False
        }
        self.speed = 5       # Player movement speed
        self.fire_rate = 12  # Frames between shots
        
        # Wave systems
        self.wave_popup_timer = 0
        self.wave_popup_text = ""
        
        # Power-up systems
        self.powertype = ["Shield", "Rapid Fire", "Slow time"]
        self.powerup_rate = 500  # Frames between power-ups
        self.powertime = 600     # Duration of power-ups
        self.rapid_active = False
        self.slow_active = False
        self.shield_active = False
        self.rapid_timer = 0
        self.slow_timer = 0
        self.shield_timer = 0
        
        # Enemy systems
        self.enemy_speed = 1
        self.enemy_spawn_rate = 100  # Frames between spawns
        
        # Load all game assets
        self._load_images()
        
        # UI elements
        self.start_button_pos = (WIDTH // 2 - 100, HEIGHT // 2 + 20)
        self.start_button_size = (200, 50)

    def _load_images(self):
        """Load all game assets from URLs"""
        # Backgrounds
        self.game_background_img = simplegui.load_image(
            "https://i.postimg.cc/sDQ6rvVd/FDE305-EE-FE9-E-4238-8-C89-6-C1-C522-C7-E09.png")
        self.menu_background_img = simplegui.load_image(
            "https://i.postimg.cc/T1Qk3DKf/85918340-0-C0-A-487-D-AC3-D-E8-B44-B6-D541-C.png")
        
        # Player
        self.player_img = simplegui.load_image(
            "https://i.postimg.cc/8zrqTJX8/FEEFEE13-2510-4598-897-F-A63-B40230-C05.png")
        
        # Power-ups
        self.slow_clock_img = simplegui.load_image(
            "https://i.postimg.cc/tCdBk3c4/4-DDB9-D92-6-F92-43-C5-BB4-F-223-D8-E94-E661.png")
        self.shield_img = simplegui.load_image(
            "https://i.postimg.cc/65FVwnMy/SHIELDTRAN.png")
        self.rapid_img = simplegui.load_image(
            "https://i.postimg.cc/2SpWgm5W/BULLETTRAN.png")
        
        # Enemies
        self.enemy_images = [
            simplegui.load_image("https://i.postimg.cc/PJ7HSyJB/7-DBB1-F73-01-EF-4194-A354-161-C218-C98-A3.png"),
            simplegui.load_image("https://i.postimg.cc/PJJhb9XW/429-B7-BDA-D325-487-A-BFC4-E6-B979588972.png"),
            simplegui.load_image("https://i.postimg.cc/qvjLSF4h/1-C4348-EC-C578-4747-B20-D-75-F6-FD192-FDE.png"),
            simplegui.load_image("https://i.postimg.cc/5NJyryXk/C75-FC200-F2-D3-4158-9759-2-CC825-E710-E9.png")
        ]
        
        # Bosses
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
        self.bullets = []
        self.enemies = []
        self.powerups = []
        self.score = 0
        self.kills = 0
        self.wave = 1
        self.frames = 0
        self.speed = 5
        self.fire_rate = 12
        self.enemy_speed = 1
        self.player = Player()
        self.game_over = False
        self.paused = False
        self.rapid_active = False
        self.slow_active = False
        self.shield_active = False
        self.rapid_timer = 0
        self.slow_timer = 0
        self.shield_timer = 0
        self.wave_popup_timer = 0
        self.move_direction = {
            "up": False, 
            "down": False, 
            "left": False, 
            "right": False
        }

    def shoot(self):
        """Fire a new player projectile"""
        bullet_x = self.player.pos.x
        bullet_y = self.player.pos.y - self.player.size.y / 2
        self.bullets.append(Vector(bullet_x, bullet_y))

    def spawn_enemy(self):
        """Create a new enemy at random top position"""
        img = random.choice(self.enemy_images)
        spawn_x = random.randint(0, WIDTH)
        self.enemies.append((Vector(spawn_x, 0), img))

    def spawn_powerup(self):
        """Create a random power-up at random position"""
        pos = Vector(
            random.randint(50, WIDTH - 50),
            random.randint(50, HEIGHT - 50)
        )
        power_type = random.choice(self.powertype)
        self.powerups.append({"type": power_type, "pos": pos})

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
            
        # Handle wave popup display
        if self.wave_popup_timer > 0:
            self.wave_popup_timer -= 1
            
        # Pause logic
        if self.paused and self.wave_popup_timer <= 0:
            return
            
        self.frames += 1
        
        # Boss systems
        if self.in_boss_fight and self.boss:
            self._update_boss()
            
        # Power-up timers
        self._update_powerups()
        
        # Player systems
        self.player.move(self.move_direction, self.speed)
        self._update_bullets()
        
        # Enemy systems
        self._update_enemies()
        
        # Collision detection
        self._check_collisions()
        
        # Spawning systems
        self._handle_spawning()

    def _update_boss(self):
        """Handle all boss-related updates"""
        self.boss.update()
        
        # Check boss bullets
        for bullet in self.boss.bullets[:]:
            if Interaction.check_collision(bullet["pos"], self.player.pos, 30):
                if not self.shield_active:
                    self.player.hearts -= 1
                self.boss.bullets.remove(bullet)
                if self.player.hearts <= 0:
                    self.game_over = True
                    return
                    
        # Check player bullets hitting boss
        for bullet in self.bullets[:]:
            if Interaction.check_collision(bullet, self.boss.pos, 80):
                self.bullets.remove(bullet)
                self.boss.health -= 1
                if self.boss.health <= 0:
                    self.boss = None
                    self.in_boss_fight = False
                    self.enemy_speed *= 1.1
                    break

    def _update_powerups(self):
        """Update all power-up states"""
        if self.rapid_active: 
            self.rapid_timer -= 1
            self.rapid_active = self.rapid_timer > 0
            
        if self.slow_active: 
            self.slow_timer -= 1
            self.slow_active = self.slow_timer > 0
            
        if self.shield_active: 
            self.shield_timer -= 1
            self.shield_active = self.shield_timer > 0

    def _update_bullets(self):
        """Update all player projectiles"""
        for bullet in self.bullets[:]:
            bullet.y -= 7  # Move upward
            if bullet.y < 0:  # Off-screen check
                self.bullets.remove(bullet)

    def _update_enemies(self):
        """Update all enemy positions"""
        current_speed = self.enemy_speed * 0.5 if self.slow_active else self.enemy_speed
        
        for enemy in self.enemies[:]:
            pos, _ = enemy
            pos.y += current_speed
            if pos.y > HEIGHT:  # Off-screen check
                self.enemies.remove(enemy)

    def _check_collisions(self):
        """Handle all collision detection"""
        # Player bullets vs enemies
        for enemy in self.enemies[:]:
            pos, _ = enemy
            for bullet in self.bullets[:]:
                if Interaction.check_collision(pos, bullet, 30):
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    self.score += 1
                    self.kills += 1
                    self._handle_wave_progression()
                    break
                    
        # Enemies vs player
        for enemy in self.enemies[:]:
            pos, _ = enemy
            if Interaction.check_collision(pos, self.player.pos, 50):
                if not self.shield_active:
                    self.player.hearts -= 1
                self.enemies.remove(enemy)
                if self.player.hearts <= 0:
                    self.game_over = True
                    return
                    
        # Power-ups collection
        for power in self.powerups[:]:
            if Interaction.check_collision(self.player.pos, power["pos"], 30):
                self._apply_powerup(power["type"])
                self.powerups.remove(power)

    def _handle_wave_progression(self):
        """Check and handle wave completion"""
        if self.kills % 10 == 0:
            self.wave += 1
            self.wave_popup_text = f"WAVE {self.wave}"
            self.wave_popup_timer = 60
            
            if self.wave % 5 == 0:  # Boss wave
                self.in_boss_fight = True
                boss_type = random.choice(["tank", "shooter", "evader"])
                self.boss = Boss(boss_type, self.boss_images[boss_type], self.wave)
            else:
                self.enemy_speed *= 1.1  # Difficulty increase
                
            if self.score > self.high_score:
                self.high_score = self.score

    def _apply_powerup(self, power_type):
        """Activate a collected power-up"""
        if power_type == "Shield":
            self.shield_active = True
            self.shield_timer = self.powertime
        elif power_type == "Rapid Fire":
            self.rapid_active = True
            self.rapid_timer = self.powertime
        elif power_type == "Slow time":
            self.slow_active = True
            self.slow_timer = self.powertime

    def _handle_spawning(self):
        """Manage enemy and power-up spawning"""
        if not self.in_boss_fight:
            if self.frames % self.enemy_spawn_rate == 0:
                self.spawn_enemy()
                
        if self.frames % self.powerup_rate == 0:
            self.spawn_powerup()
            
        if self.frames % (4 if self.rapid_active else self.fire_rate) == 0:
            self.shoot()

# Initialize global game instance
GAME = Game()

# ========== DRAW HANDLER ==========
def draw(canvas):
    """
    Main rendering function called each frame
    Handles all visual rendering based on game state:
    - Welcome screen
    - Main gameplay
    - Pause screen
    - Game over screen
    """
    # Update game logic first
    GAME.update()

    # ===== WELCOME SCREEN =====
    if GAME.state == "welcome":
        # Draw menu background
        bg_center = (GAME.menu_background_img.get_width() / 2, 
                    GAME.menu_background_img.get_height() / 2)
        bg_size = (GAME.menu_background_img.get_width(), 
                  GAME.menu_background_img.get_height())
        canvas.draw_image(GAME.menu_background_img, bg_center, bg_size,
                         (WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
        
        # Title text
        canvas.draw_text("CYBER ATTACK", 
                        (WIDTH/2 - 250, HEIGHT/2 - 100), 
                        64, "Cyan", "sans-serif")
        canvas.draw_text("Click the button to start", 
                        (WIDTH/2 - 200, HEIGHT/2 - 50), 
                        36, "White", "sans-serif")
        
        # Start button
        x, y = GAME.start_button_pos
        w, h = GAME.start_button_size
        canvas.draw_polygon(
            [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
            2, "White", "Gray"
        )
        canvas.draw_text("START", (x + 45, y + 35), 30, "Black", "sans-serif")
        return

    # ===== GAME BACKGROUND =====
    bg_center = (GAME.game_background_img.get_width() / 2,
                GAME.game_background_img.get_height() / 2)
    bg_size = (GAME.game_background_img.get_width(),
              GAME.game_background_img.get_height())
    canvas.draw_image(GAME.game_background_img, bg_center, bg_size,
                     (WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # ===== PLAYER RENDERING =====
    image_width = GAME.player_img.get_width()
    image_height = GAME.player_img.get_height()
    image_center = (image_width / 2, image_height / 2)
    canvas.draw_image(
        GAME.player_img,
        image_center,
        (image_width, image_height),
        GAME.player.pos.to_tuple(),
        (100, 100)
    )

    # ===== BULLETS RENDERING =====
    for bullet in GAME.bullets:
        canvas.draw_circle(bullet.to_tuple(), 5, 1, "White", "White")

    # ===== ENEMIES RENDERING =====
    for pos, img in GAME.enemies:
        canvas.draw_image(
            img,
            (img.get_width() / 2, img.get_height() / 2),
            (img.get_width(), img.get_height()),
            pos.to_tuple(),
            (50, 50)
        )

    # ===== POWERUPS RENDERING =====
    for power in GAME.powerups:
        pos = power["pos"].to_tuple()
        if power["type"] == "Shield":
            canvas.draw_image(
                GAME.shield_img,
                (GAME.shield_img.get_width()/2, GAME.shield_img.get_height()/2),
                (GAME.shield_img.get_width(), GAME.shield_img.get_height()),
                pos, (40, 40))
        elif power["type"] == "Rapid Fire":
            canvas.draw_image(
                GAME.rapid_img,
                (GAME.rapid_img.get_width()/2, GAME.rapid_img.get_height()/2),
                (GAME.rapid_img.get_width(), GAME.rapid_img.get_height()),
                pos, (40, 40))
        elif power["type"] == "Slow time":
            canvas.draw_image(
                GAME.slow_clock_img,
                (GAME.slow_clock_img.get_width()/2, GAME.slow_clock_img.get_height()/2),
                (GAME.slow_clock_img.get_width(), GAME.slow_clock_img.get_height()),
                pos, (50, 40))

    # ===== BOSS RENDERING =====
    if GAME.boss:
        GAME.boss.draw(canvas)

    # ===== UI ELEMENTS =====
    # Score/Wave/Kills display
    canvas.draw_polygon(
        [(10, 10), (340, 10), (340, 50), (10, 50)],
        2, "Teal", "Teal"
    )
    canvas.draw_text(
        f"Wave: {GAME.wave} | Kills: {GAME.kills} | Hearts: {GAME.player.hearts}",
        (20, 40), 24, "White", "sans-serif"
    )

    # Boss health display (if in boss fight)
    if GAME.boss:
        boss = GAME.boss
        canvas.draw_text(
            f"Boss: {boss.name}",
            (WIDTH / 2 - 150, 40), 28, "Cyan", "sans-serif"
        )
        
        # Boss health bar
        hud_bar_width = 300
        hud_bar_height = 20
        hud_bar_x = WIDTH / 2 - hud_bar_width / 2
        hud_bar_y = 60
        
        max_health = 25 if boss.boss_type == "tank" else 20
        health_ratio = boss.health / max_health
        
        # Background
        canvas.draw_polygon([
            (hud_bar_x, hud_bar_y),
            (hud_bar_x + hud_bar_width, hud_bar_y),
            (hud_bar_x + hud_bar_width, hud_bar_y + hud_bar_height),
            (hud_bar_x, hud_bar_y + hud_bar_height)
        ], 1, "White", "Gray")
        
        # Health
        canvas.draw_polygon([
            (hud_bar_x, hud_bar_y),
            (hud_bar_x + hud_bar_width * health_ratio, hud_bar_y),
            (hud_bar_x + hud_bar_width * health_ratio, hud_bar_y + hud_bar_height),
            (hud_bar_x, hud_bar_y + hud_bar_height)
        ], 1, "Red", "Red")

    # Controls display
    canvas.draw_polygon(
        [(690, 10), (1190, 10), (1190, 50), (690, 50)],
        2, "White", "Black"
    )
    canvas.draw_text(
        "Press R to Restart | Press P to Pause/Resume",
        (700, 35), 24, "White", "sans-serif"
    )

    # ===== POWERUP INDICATORS =====
    y_offset = 110
    if GAME.shield_active:
        canvas.draw_text(
            "Shield Active", 
            (60, y_offset), 24, "Yellow", "sans-serif"
        )
        canvas.draw_image(
            GAME.shield_img,
            (GAME.shield_img.get_width()/2, GAME.shield_img.get_height()/2),
            (GAME.shield_img.get_width(), GAME.shield_img.get_height()),
            (30, y_offset + 10), (30, 30))
        y_offset += 30

    if GAME.rapid_active:
        canvas.draw_text(
            "Rapid Fire Active", 
            (60, y_offset), 24, "Sky blue", "sans-serif"
        )
        canvas.draw_image(
            GAME.rapid_img,
            (GAME.rapid_img.get_width()/2, GAME.rapid_img.get_height()/2),
            (GAME.rapid_img.get_width(), GAME.rapid_img.get_height()),
            (30, y_offset + 10), (30, 30))
        y_offset += 30

    if GAME.slow_active:
        canvas.draw_text(
            "Slow Time Active", 
            (60, y_offset), 24, "Light grey", "sans-serif"
        )
        canvas.draw_image(
            GAME.slow_clock_img,
            (GAME.slow_clock_img.get_width()/2, GAME.slow_clock_img.get_height()/2),
            (GAME.slow_clock_img.get_width(), GAME.slow_clock_img.get_height()),
            (30, y_offset + 10), (40, 30))

    # ===== WAVE POPUP =====
    if GAME.wave_popup_timer > 0:
        canvas.draw_text(
            GAME.wave_popup_text,
            (WIDTH // 2 - 100, HEIGHT // 2), 
            60, "Orange", "sans-serif"
        )

    # ===== PAUSE SCREEN =====
    if GAME.paused and GAME.wave_popup_timer <= 0:
        # Dark overlay
        canvas.draw_polygon(
            [(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)],
            1, "Black", "rgba(0, 0, 0, 0.5)"
        )
        canvas.draw_text(
            "PAUSED", 
            (WIDTH / 2 - 80, HEIGHT / 2), 
            50, "White", "sans-serif"
        )
        canvas.draw_text(
            "Press M to Return to Menu", 
            (WIDTH / 2 - 200, HEIGHT / 2 + 110), 
            30, "White", "sans-serif"
        )

    # ===== GAME OVER SCREEN =====
    if GAME.game_over:
        # Darker overlay
        canvas.draw_polygon(
            [(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT)],
            1, "Black", "rgba(0, 0, 0, 0.7)"
        )
        canvas.draw_text(
            "GAME OVER", 
            (WIDTH / 2 - 150, HEIGHT / 2), 
            50, "Red", "sans-serif"
        )
        canvas.draw_text(
            "Press R to Restart", 
            (WIDTH / 2 - 170, HEIGHT / 2 + 60), 
            30, "White", "sans-serif"
        )
        canvas.draw_text(
            "Press M to Return to Menu", 
            (WIDTH / 2 - 200, HEIGHT / 2 + 110), 
            30, "White", "sans-serif"
        )

# ========== INPUT HANDLERS ==========
def keydown(key):
    """
    Handle keyboard key presses:
    - Movement controls (WASD)
    - Game controls (P for pause, R for restart)
    """
    if GAME.state == "playing":
        # Movement controls
        if key == simplegui.KEY_MAP['w']: 
            GAME.move_direction["up"] = True
        if key == simplegui.KEY_MAP['s']: 
            GAME.move_direction["down"] = True
        if key == simplegui.KEY_MAP['a']: 
            GAME.move_direction["left"] = True
        if key == simplegui.KEY_MAP['d']: 
            GAME.move_direction["right"] = True
            
        # Pause control (only when not showing wave popup)
        if key == simplegui.KEY_MAP['p'] and GAME.wave_popup_timer <= 0:
            GAME.paused = not GAME.paused

def keyup(key):
    """
    Handle keyboard key releases:
    - Movement controls (WASD)
    - Game controls (R for restart, M for menu)
    """
    if GAME.state == "playing":
        # Movement controls
        if key == simplegui.KEY_MAP['w']: 
            GAME.move_direction["up"] = False
        if key == simplegui.KEY_MAP['s']: 
            GAME.move_direction["down"] = False
        if key == simplegui.KEY_MAP['a']: 
            GAME.move_direction["left"] = False
        if key == simplegui.KEY_MAP['d']: 
            GAME.move_direction["right"] = False
            
    # Global controls (work in any state)
    if key == simplegui.KEY_MAP['r']:  # Restart game
        GAME.restart()
    if key == simplegui.KEY_MAP['m']:  # Return to menu
        GAME.restart()
        GAME.state = "welcome"

def click(pos):
    """
    Handle mouse clicks:
    - Start button on welcome screen
    """
    if GAME.state == "welcome":
        x, y = GAME.start_button_pos
        w, h = GAME.start_button_size
        # Check if click is within button bounds
        if x <= pos[0] <= x + w and y <= pos[1] <= y + h:
            GAME.start_game()

# ========== FRAME SETUP ==========
frame = simplegui.create_frame("Cyber Attack", WIDTH, HEIGHT)
frame.set_draw_handler(draw)              # Set render function
frame.set_keydown_handler(keydown)        # Set key press handler
frame.set_keyup_handler(keyup)            # Set key release handler
frame.set_mouseclick_handler(click)       # Set mouse click handler
frame.start()  # Start the game loop