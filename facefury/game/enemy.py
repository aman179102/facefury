"""Enemy characters for FaceFury."""

import pygame
import random
from typing import Optional, List
from .physics import Platform, CollisionDetector


class Enemy:
    """Enemy character with face sprite."""
    
    WIDTH = 64
    HEIGHT = 64
    
    def __init__(self, x: int, y: int, 
                 face_sprite: Optional[pygame.Surface] = None,
                 speed: float = 2.0,
                 patrol_distance: int = 200):
        """
        Initialize enemy.
        
        Args:
            x: Starting X position
            y: Starting Y position
            face_sprite: Enemy face image
            speed: Movement speed
            patrol_distance: Distance to patrol before turning
        """
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.start_x = x
        self.speed = speed
        self.velocity_x = speed
        self.velocity_y = 0
        self.patrol_distance = patrol_distance
        self.gravity = 0.8
        
        # State
        self.facing_right = speed > 0
        self.alive = True
        self.health = 1
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Sprite
        self.face_sprite = face_sprite
        self.default_color = (255, 80, 80)
        self._create_sprite()
        
        # Score value
        self.score_value = 100
    
    def _create_sprite(self):
        """Create enemy sprite."""
        self.sprite = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        if self.face_sprite:
            scaled = pygame.transform.scale(self.face_sprite, (self.WIDTH, self.HEIGHT))
            self.sprite.blit(scaled, (0, 0))
        else:
            # Draw angry enemy face
            pygame.draw.ellipse(self.sprite, self.default_color, 
                              (0, 0, self.WIDTH, self.HEIGHT))
            
            # Angry eyes (diagonal)
            pygame.draw.line(self.sprite, (255, 255, 255), (12, 12), (28, 20), 3)
            pygame.draw.line(self.sprite, (255, 255, 255), (28, 12), (12, 20), 3)
            pygame.draw.line(self.sprite, (255, 255, 255), (36, 12), (52, 20), 3)
            pygame.draw.line(self.sprite, (255, 255, 255), (52, 12), (36, 20), 3)
            
            # Angry mouth
            pygame.draw.arc(self.sprite, (0, 0, 0), 
                          (15, 30, 34, 15), 3.14, 0, 3)
            
            # Add horns
            pygame.draw.polygon(self.sprite, (150, 50, 50), 
                              [(10, 15), (5, 0), (20, 10)])
            pygame.draw.polygon(self.sprite, (150, 50, 50), 
                              [(54, 15), (59, 0), (44, 10)])
    
    def update(self, platforms: List[Platform]):
        """
        Update enemy AI and physics.
        
        Args:
            platforms: List of platforms for collision
        """
        if not self.alive:
            return
        
        # Apply gravity
        self.velocity_y += self.gravity
        
        # Update position
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)
        
        # Check platform collision
        self.rect, self.velocity_y, landed = CollisionDetector.resolve_platform_collision(
            self.rect, self.velocity_y, platforms
        )
        
        # Patrol logic - turn around at edges or after patrol distance
        distance_moved = abs(self.rect.x - self.start_x)
        
        # Check if at edge (not on ground ahead)
        check_ahead = 10
        if self.velocity_x > 0:
            check_rect = pygame.Rect(self.rect.right, self.rect.bottom + 5, 
                                  check_ahead, 10)
        else:
            check_rect = pygame.Rect(self.rect.left - check_ahead, 
                                  self.rect.bottom + 5, check_ahead, 10)
        
        on_ground_ahead = any(p.rect.colliderect(check_rect) for p in platforms)
        
        if distance_moved >= self.patrol_distance or not on_ground_ahead:
            # Check if we're near start position (allow some tolerance)
            if distance_moved > 50:
                self.velocity_x = -self.velocity_x
                self.facing_right = self.velocity_x > 0
        
        # Animation
        self.animation_timer += 1
        if self.animation_timer > 8:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2
    
    def take_damage(self, amount: int = 1) -> bool:
        """
        Apply damage to enemy.
        
        Returns:
            True if enemy died
        """
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            return True
        return False
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0):
        """
        Draw enemy on surface.
        
        Args:
            surface: Surface to draw on
            camera_x: Camera offset
        """
        if not self.alive:
            return
        
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y
        
        # Flip sprite based on direction
        sprite_to_draw = self.sprite
        if not self.facing_right:
            sprite_to_draw = pygame.transform.flip(self.sprite, True, False)
        
        # Walking animation
        bounce = self.animation_frame * 3 if abs(self.velocity_x) > 0.5 else 0
        
        surface.blit(sprite_to_draw, (draw_x, draw_y - bounce))
    
    def get_rect(self) -> pygame.Rect:
        """Get enemy bounding box."""
        return self.rect.copy()
    
    def set_face_sprite(self, sprite: pygame.Surface):
        """Update enemy face sprite."""
        self.face_sprite = sprite
        self._create_sprite()


class EnemySpawner:
    """Manages enemy spawning."""
    
    def __init__(self, enemy_face_sprites: List[Optional[pygame.Surface]]):
        """
        Initialize spawner.
        
        Args:
            enemy_face_sprites: List of available enemy face sprites
        """
        self.sprites = enemy_face_sprites if enemy_face_sprites else [None]
    
    def spawn(self, x: int, y: int, difficulty: int = 1) -> Enemy:
        """
        Spawn an enemy.
        
        Args:
            x: Spawn X position
            y: Spawn Y position
            difficulty: Difficulty level (affects speed)
            
        Returns:
            New Enemy instance
        """
        # Select random face
        sprite = random.choice(self.sprites)
        
        # Calculate speed based on difficulty
        base_speed = 1.5 + (difficulty * 0.5)
        speed = random.uniform(base_speed, base_speed + 1.0)
        
        # Random direction
        if random.random() < 0.5:
            speed = -speed
        
        # Vary patrol distance
        patrol = random.randint(100, 300)
        
        enemy = Enemy(x, y, sprite, speed, patrol)
        
        # Increase score value with difficulty
        enemy.score_value = 100 * difficulty
        
        return enemy
