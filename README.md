# Cyber-Attack

*USE TO https://py3.codeskulptor.org/ RUN CODE

Overview:
Cyber Attack is a top-down shooter game set in a cyberpunk-themed world where players defend against waves of enemies. 
The goal is to survive as long as possible by defeating enemies, collecting power-ups, and battling unique bosses.


Features:
Player Controls: Move using WASD keys and shoot automatically.
Enemy Waves: Endless waves of enemies with increasing speed and spawn rates.
Power-ups: Collect temporary shields, rapid fire, and slow time abilities.
Boss Fights: Encounter unique bosses every 5 waves, each with distinct behaviors.
Dynamic Difficulty: Enemy speed and spawn rates scale with each wave.
Game States: Includes welcome screen, gameplay, pause, and game over screens.


Controls:
WASD: Move the player.  
P: Pause/resume the game.
R: Restart the game.
M: Return to the main menu.
Mouse Click: Click the "START" button on the welcome screen to begin.


Game Mechanics:
Player Movement: Smooth movement with boundary checks to keep the player on-screen.
Shooting: Automatic firing with adjustable fire rates.
Collision Detection: Uses Euclidean distance for precise bullet-enemy and player-enemy collisions.


Power-ups:
Shield: Protects the player from damage.
Rapid Fire: Increases the player's fire rate.
Slow Time: Halves enemy movement speed.


Boss Fights:
Tank Boss: High health with circular attack patterns.
Shooter Boss: Rapid triple-shot attacks.
Evader Boss: Dodges player bullets.


Technical Details:
Vector Class: Handles 2D position and velocity calculations, including distance checks for collisions.
Game Loop: Manages object spawning, updates, and rendering.
Sprite Handling: Loads and renders sprites for the player, enemies, and power-ups.
Dynamic Scaling: Adjusts enemy speed, spawn rates, and boss health based on the current wave.


Team Collaboration:
This project was developed collaboratively using GitHub for version control and task management. Key contributions included:
Player movement and shooting mechanics.
Enemy spawning and wave progression.
Boss behaviors and power-up systems.
Sprite design and integration.
