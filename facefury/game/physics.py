"""Physics system for FaceFury game engine."""

import pygame
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Physics:
    """Physics constants and state."""
    gravity: float = 0.8
    friction: float = 0.85
    air_resistance: float = 0.98
    terminal_velocity: float = 15.0
    jump_strength: float = -15.0
    move_speed: float = 6.0


class Platform:
    """Static platform for collision."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 color: Tuple[int, int, int] = (100, 100, 100)):
        """
        Initialize platform.
        
        Args:
            x: X position
            y: Y position
            width: Platform width
            height: Platform height
            color: RGB color tuple
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0):
        """Draw platform on surface."""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_x
        pygame.draw.rect(surface, self.color, draw_rect)
        
        # Add highlight
        highlight = pygame.Rect(draw_rect.x, draw_rect.y, draw_rect.width, 4)
        highlight_color = tuple(min(c + 40, 255) for c in self.color)
        pygame.draw.rect(surface, highlight_color, highlight)
        
        # Add shadow
        shadow = pygame.Rect(draw_rect.x, draw_rect.bottom - 4, draw_rect.width, 4)
        shadow_color = tuple(max(c - 40, 0) for c in self.color)
        pygame.draw.rect(surface, shadow_color, shadow)
    
    def collides_with(self, rect: pygame.Rect) -> bool:
        """Check if rect collides with platform."""
        return self.rect.colliderect(rect)


class CollisionDetector:
    """Handles collision detection between game objects."""
    
    @staticmethod
    def check_ground_collision(entity_rect: pygame.Rect, 
                               platforms: List[Platform]) -> Tuple[bool, Optional[Platform]]:
        """
        Check if entity is on ground.
        
        Args:
            entity_rect: Entity bounding box
            platforms: List of platforms to check
            
        Returns:
            Tuple of (is_on_ground, platform_collided_with)
        """
        # Check slightly below entity
        check_rect = entity_rect.copy()
        check_rect.y += 2
        
        for platform in platforms:
            if platform.rect.colliderect(check_rect):
                return True, platform
        
        return False, None
    
    @staticmethod
    def resolve_platform_collision(entity_rect: pygame.Rect,
                                    velocity_y: float,
                                    platforms: List[Platform]) -> Tuple[pygame.Rect, float, bool]:
        """
        Resolve collision between entity and platforms.
        
        Args:
            entity_rect: Entity bounding box
            velocity_y: Vertical velocity
            platforms: List of platforms
            
        Returns:
            Tuple of (new_rect, new_velocity_y, landed)
        """
        landed = False
        
        for platform in platforms:
            if platform.rect.colliderect(entity_rect):
                # Check if landing on top
                if velocity_y > 0 and entity_rect.bottom <= platform.rect.centery:
                    entity_rect.bottom = platform.rect.top
                    velocity_y = 0
                    landed = True
                # Check if hitting from below
                elif velocity_y < 0 and entity_rect.top >= platform.rect.centery:
                    entity_rect.top = platform.rect.bottom
                    velocity_y = 0
                # Check side collision
                else:
                    # Determine which side
                    overlap_left = entity_rect.right - platform.rect.left
                    overlap_right = platform.rect.right - entity_rect.left
                    
                    if overlap_left < overlap_right:
                        entity_rect.right = platform.rect.left
                    else:
                        entity_rect.left = platform.rect.right
        
        return entity_rect, velocity_y, landed
    
    @staticmethod
    def check_entity_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """Check collision between two entities."""
        return rect1.colliderect(rect2)


class Camera:
    """Game camera for scrolling levels."""
    
    def __init__(self, screen_width: int, level_width: int):
        """
        Initialize camera.
        
        Args:
            screen_width: Width of screen viewport
            level_width: Total width of level
        """
        self.x = 0
        self.screen_width = screen_width
        self.level_width = level_width
    
    def update(self, target_x: int):
        """
        Update camera position to follow target.
        
        Args:
            target_x: X position to center on
        """
        # Center target on screen
        target_camera_x = target_x - self.screen_width // 2
        
        # Smooth camera follow
        self.x += (target_camera_x - self.x) * 0.1
        
        # Clamp to level bounds
        self.x = max(0, min(self.x, self.level_width - self.screen_width))
    
    def world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        return (world_x - int(self.x), world_y)
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to world coordinates."""
        return (screen_x + int(self.x), screen_y)
