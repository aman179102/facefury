"""Main game engine for FaceFury."""

import pygame
from typing import Optional, Tuple
from .player import Player
from .enemy import EnemySpawner
from .physics import Camera
from .level import LevelManager


class GameEngine:
    """Main game controller."""
    
    def __init__(self, screen: pygame.Surface, 
                 player_face: Optional[pygame.Surface] = None,
                 enemy_faces: Optional[list] = None):
        """
        Initialize game engine.
        
        Args:
            screen: Main game surface
            player_face: Player face sprite
            enemy_faces: List of enemy face sprites
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Game state
        self.running = False
        self.paused = False
        self.game_over = False
        self.victory = False
        
        # Score and stats
        self.score = 0
        self.time_elapsed = 0
        self.enemies_defeated = 0
        
        # Create player
        self.player = Player(100, self.screen_height - 200, player_face)
        
        # Level management
        self.level_manager = LevelManager(self.screen_height)
        enemy_spawner = EnemySpawner(enemy_faces if enemy_faces else [None])
        self.current_level = self.level_manager.load_level(1, enemy_spawner)
        
        # Camera
        self.camera = Camera(self.screen_width, self.current_level.width)
        
        # Input state
        self.keys_pressed = {}
        
        # Event callbacks
        self.on_score_change = None
        self.on_health_change = None
        self.on_level_complete = None
        self.on_game_over = None
        
        # Sound callback
        self.on_play_sound = None
        
        # Screenshot callback
        self.on_screenshot = None
    
    def handle_event(self, event: pygame.event.Event):
        """Process input events."""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed[event.key] = True
            
            if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                if self.player.jump() and not self.game_over:
                    self._play_sound('jump')
            
            elif event.key == pygame.K_p:
                self.paused = not self.paused
            
            elif event.key == pygame.K_F12:
                self._take_screenshot()
            
            elif event.key == pygame.K_r and self.game_over:
                self.restart()
                
        elif event.type == pygame.KEYUP:
            self.keys_pressed[event.key] = False
    
    def update(self, dt: float):
        """
        Update game state.
        
        Args:
            dt: Delta time in seconds
        """
        if self.paused or self.game_over:
            return
        
        self.time_elapsed += dt
        
        # Handle input
        if self.keys_pressed.get(pygame.K_LEFT) or self.keys_pressed.get(pygame.K_a):
            self.player.move(-1)
        if self.keys_pressed.get(pygame.K_RIGHT) or self.keys_pressed.get(pygame.K_d):
            self.player.move(1)
        
        # Update player
        platforms = self.current_level.get_platforms()
        self.player.update(platforms)
        
        # Update level (enemies)
        self.current_level.update()
        
        # Update camera
        self.camera.update(self.player.rect.centerx)
        
        # Check enemy collisions
        self._check_enemy_collisions()
        
        # Check pit death
        if self.player.rect.top > self.screen_height:
            self.player.take_damage(3)  # Instant kill
            if not self.player.alive:
                self._trigger_game_over()
        
        # Check level complete
        if self.current_level.check_level_complete(self.player.rect):
            self._complete_level()
        
        # Update callbacks
        if self.on_health_change:
            self.on_health_change(self.player.health)
    
    def _check_enemy_collisions(self):
        """Handle player-enemy interactions."""
        enemies = self.current_level.get_enemies()
        
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            if self.player.get_rect().colliderect(enemy.get_rect()):
                # Check if jumping on enemy
                if (self.player.velocity_y > 0 and 
                    self.player.rect.bottom <= enemy.rect.centery + 10):
                    # Kill enemy
                    enemy.take_damage(1)
                    self.enemies_defeated += 1
                    self.score += enemy.score_value
                    
                    # Bounce player
                    self.player.velocity_y = -10
                    self._play_sound('hit')
                    
                    if self.on_score_change:
                        self.on_score_change(self.score)
                else:
                    # Player takes damage
                    if self.player.take_damage(1):
                        self._play_sound('damage')
                        
                        # Knockback
                        knockback_dir = -1 if self.player.rect.centerx < enemy.rect.centerx else 1
                        self.player.velocity_x = knockback_dir * -10
                        self.player.velocity_y = -5
                        
                        if self.on_health_change:
                            self.on_health_change(self.player.health)
                        
                        if not self.player.alive:
                            self._trigger_game_over()
    
    def _complete_level(self):
        """Handle level completion."""
        # Bonus for completing level
        time_bonus = max(0, 300 - int(self.time_elapsed)) * 10
        self.score += 500 + time_bonus
        
        if self.on_level_complete:
            self.on_level_complete(self.level_manager.level_number, self.score)
        
        # Try to load next level
        enemy_spawner = self.current_level.enemy_spawner
        next_level = self.level_manager.next_level(enemy_spawner)
        
        if next_level:
            self.current_level = next_level
            self.camera = Camera(self.screen_width, self.current_level.width)
            self.player.respawn(100, self.screen_height - 200)
            self._play_sound('win')
        else:
            # Victory!
            self.victory = True
            self._trigger_game_over(victory=True)
    
    def _trigger_game_over(self, victory: bool = False):
        """Trigger game over state."""
        self.game_over = True
        self.victory = victory
        
        if self.on_game_over:
            self.on_game_over(self.score, self.victory)
    
    def _take_screenshot(self):
        """Capture current screen."""
        if self.on_screenshot:
            self.on_screenshot(self.screen)
    
    def _play_sound(self, sound_type: str):
        """Request sound playback."""
        if self.on_play_sound:
            self.on_play_sound(sound_type)
    
    def draw(self):
        """Render game frame."""
        # Clear screen with level background
        self.screen.fill(self.current_level.bg_color)
        
        # Draw level
        self.current_level.draw(self.screen, int(self.camera.x))
        
        # Draw player
        self.player.draw(self.screen, int(self.camera.x))
        
        # Draw pause overlay
        if self.paused:
            self._draw_pause_overlay()
    
    def _draw_pause_overlay(self):
        """Draw pause screen overlay."""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 74)
        text = font.render("PAUSED", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen_width // 2, 
                                          self.screen_height // 2))
        self.screen.blit(text, text_rect)
        
        font_small = pygame.font.Font(None, 36)
        hint = font_small.render("Press P to resume", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(self.screen_width // 2, 
                                          self.screen_height // 2 + 50))
        self.screen.blit(hint, hint_rect)
    
    def restart(self):
        """Restart the game."""
        self.score = 0
        self.time_elapsed = 0
        self.enemies_defeated = 0
        self.game_over = False
        self.victory = False
        self.paused = False
        
        self.player.respawn(100, self.screen_height - 200)
        
        # Reload first level
        enemy_spawner = self.current_level.enemy_spawner if self.current_level else None
        if enemy_spawner:
            self.level_manager.reset()
            self.current_level = self.level_manager.load_level(1, enemy_spawner)
            self.camera = Camera(self.screen_width, self.current_level.width)
    
    def get_stats(self) -> dict:
        """Get current game statistics."""
        return {
            'score': self.score,
            'health': self.player.health,
            'time': int(self.time_elapsed),
            'level': self.level_manager.level_number,
            'enemies_defeated': self.enemies_defeated
        }
