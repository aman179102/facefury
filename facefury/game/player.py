"""Player character for FaceFury."""

import pygame
from typing import Optional, Tuple, List
from .physics import Physics, Platform, CollisionDetector


class Player:
    """Player character with face sprite."""
    
    WIDTH = 64
    HEIGHT = 64
    INVINCIBILITY_FRAMES = 60  # 1 second at 60 FPS
    
    def __init__(self, x: int, y: int, face_sprite: Optional[pygame.Surface] = None):
        """
        Initialize player.
        
        Args:
            x: Starting X position
            y: Starting Y position
            face_sprite: Player face image (or None for default)
        """
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.physics = Physics()
        
        # State
        self.on_ground = False
        self.facing_right = True
        self.is_jumping = False
        self.health = 3
        self.max_health = 3
        self.invincible_timer = 0
        self.alive = True
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Sprite
        self.face_sprite = face_sprite
        self.default_color = (50, 150, 255)
        self._create_default_sprite()
    
    def _create_default_sprite(self):
        """Create default sprite if no face provided."""
        self.sprite = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        if self.face_sprite:
            # Scale face sprite to fit
            scaled = pygame.transform.scale(self.face_sprite, (self.WIDTH, self.HEIGHT))
            self.sprite.blit(scaled, (0, 0))
        else:
            # Draw default player shape
            pygame.draw.ellipse(self.sprite, self.default_color, 
                              (0, 0, self.WIDTH, self.HEIGHT))
            pygame.draw.ellipse(self.sprite, (255, 255, 255), 
                              (10, 10, 20, 20))  # Left eye
            pygame.draw.ellipse(self.sprite, (255, 255, 255), 
                              (34, 10, 20, 20))  # Right eye
            pygame.draw.ellipse(self.sprite, (0, 0, 0), 
                              (16, 16, 8, 8))  # Left pupil
            pygame.draw.ellipse(self.sprite, (0, 0, 0), 
                              (40, 16, 8, 8))  # Right pupil
            pygame.draw.arc(self.sprite, (255, 100, 100), 
                          (15, 25, 34, 20), 0, 3.14, 3)  # Smile
    
    def update(self, platforms: List[Platform]):
        """
        Update player physics and state.
        
        Args:
            platforms: List of platforms for collision
        """
        if not self.alive:
            return
        
        # Apply gravity
        self.velocity_y += self.physics.gravity
        self.velocity_y = min(self.velocity_y, self.physics.terminal_velocity)
        
        # Apply friction
        if self.on_ground:
            self.velocity_x *= self.physics.friction
        else:
            self.velocity_x *= self.physics.air_resistance
        
        # Update position
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)
        
        # Check ground collision
        self.on_ground, _ = CollisionDetector.check_ground_collision(self.rect, platforms)
        
        # Resolve platform collisions
        self.rect, self.velocity_y, landed = CollisionDetector.resolve_platform_collision(
            self.rect, self.velocity_y, platforms
        )
        
        if landed:
            self.on_ground = True
            self.is_jumping = False
        
        # Update invincibility
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        # Animation
        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2
    
    def move(self, direction: int):
        """
        Move player horizontally.
        
        Args:
            direction: -1 for left, 1 for right
        """
        self.velocity_x += direction * self.physics.move_speed * 0.3
        self.velocity_x = max(-self.physics.move_speed, 
                             min(self.physics.move_speed, self.velocity_x))
        self.facing_right = direction > 0
    
    def jump(self):
        """Make player jump if on ground."""
        if self.on_ground and not self.is_jumping:
            self.velocity_y = self.physics.jump_strength
            self.is_jumping = True
            self.on_ground = False
            return True
        return False
    
    def take_damage(self, amount: int = 1):
        """
        Apply damage to player.
        
        Args:
            amount: Damage amount
            
        Returns:
            True if damage was applied, False if invincible
        """
        if self.invincible_timer > 0:
            return False
        
        self.health -= amount
        self.invincible_timer = self.INVINCIBILITY_FRAMES
        
        if self.health <= 0:
            self.alive = False
        
        return True
    
    def heal(self, amount: int = 1):
        """Heal player."""
        self.health = min(self.max_health, self.health + amount)
    
    def respawn(self, x: int, y: int):
        """Respawn player at position."""
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.health = self.max_health
        self.alive = True
        self.invincible_timer = self.INVINCIBILITY_FRAMES
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0):
        """
        Draw player on surface.
        
        Args:
            surface: Surface to draw on
            camera_x: Camera offset
        """
        if not self.alive:
            return
        
        # Flash when invincible
        if self.invincible_timer > 0 and self.invincible_timer % 10 < 5:
            return
        
        # Calculate draw position
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y
        
        # Flip sprite if facing left
        sprite_to_draw = self.sprite
        if not self.facing_right:
            sprite_to_draw = pygame.transform.flip(self.sprite, True, False)
        
        # Add slight bounce animation when moving
        bounce = 0
        if abs(self.velocity_x) > 1 and self.on_ground:
            bounce = self.animation_frame * 2
        
        surface.blit(sprite_to_draw, (draw_x, draw_y - bounce))
        
        # Draw health indicators
        for i in range(self.max_health):
            heart_color = (255, 50, 50) if i < self.health else (100, 100, 100)
            heart_x = draw_x + i * 12
            heart_y = draw_y - 15
            pygame.draw.circle(surface, heart_color, (heart_x + 5, heart_y + 5), 4)
    
    def get_rect(self) -> pygame.Rect:
        """Get player bounding box."""
        return self.rect.copy()
    
    def set_face_sprite(self, sprite: pygame.Surface):
        """Update player face sprite."""
        self.face_sprite = sprite
        self._create_default_sprite()
