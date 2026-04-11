"""Level system for FaceFury."""

import random
import pygame
from typing import List, Tuple, Optional
from .physics import Platform
from .enemy import Enemy, EnemySpawner


class Level:
    """Single game level."""
    
    def __init__(self, level_number: int, width: int, height: int):
        """
        Initialize level.
        
        Args:
            level_number: Level identifier
            width: Level width in pixels
            height: Level height in pixels
        """
        self.level_number = level_number
        self.width = width
        self.height = height
        
        self.platforms: List[Platform] = []
        self.enemies: List[Enemy] = []
        self.enemy_spawner: Optional[EnemySpawner] = None
        
        # Player start position
        self.player_start = (100, height - 200)
        
        # Level end (flag position)
        self.end_x = width - 100
        
        # Background color
        self.bg_color = self._get_level_color()
        
        self._build_level()
    
    def _get_level_color(self) -> Tuple[int, int, int]:
        """Get background color based on level number."""
        colors = [
            (135, 206, 235),  # Sky blue - Level 1
            (255, 200, 150),  # Sunset orange - Level 2
            (100, 100, 150),  # Twilight purple - Level 3
            (200, 230, 200),  # Forest green - Level 4
        ]
        return colors[(self.level_number - 1) % len(colors)]
    
    def _build_level(self):
        """Build level geometry based on level number."""
        # Ground
        self.platforms.append(Platform(0, self.height - 50, self.width, 50, 
                                       (100, 70, 50)))
        
        if self.level_number == 1:
            self._build_level_1()
        elif self.level_number == 2:
            self._build_level_2()
        else:
            self._build_procedural_level()
    
    def _build_level_1(self):
        """Build tutorial level."""
        # Starting platform area (safe zone)
        pass  # Just ground
        
        # Small platforms
        self.platforms.append(Platform(300, self.height - 150, 100, 20))
        self.platforms.append(Platform(500, self.height - 200, 100, 20))
        self.platforms.append(Platform(700, self.height - 150, 100, 20))
        
        # Higher platform
        self.platforms.append(Platform(900, self.height - 280, 150, 20))
        
        # Bridge section
        for i in range(3):
            self.platforms.append(Platform(1100 + i * 120, 
                                          self.height - 200 - i * 30, 
                                          80, 20))
        
        # Final stretch
        self.platforms.append(Platform(1500, self.height - 180, 100, 20))
        self.platforms.append(Platform(1700, self.height - 250, 120, 20))
        
        # Enemy spawn points (will be populated by spawner)
        self.enemy_spawn_points = [
            (500, self.height - 264),  # On platform
            (900, self.height - 344),  # On higher platform
            (1200, self.height - 200),  # Ground level
            (1600, self.height - 100),  # Ground
        ]
    
    def _build_level_2(self):
        """Build harder level with more verticality."""
        # Floating platforms
        heights = [150, 250, 200, 300, 180, 320, 220]
        x_positions = [250, 450, 650, 850, 1100, 1350, 1600]
        
        for x, h in zip(x_positions, heights):
            width = random.choice([80, 100, 120])
            self.platforms.append(Platform(x, self.height - h, width, 20))
        
        # Moving platform challenge
        self.platforms.append(Platform(900, self.height - 400, 80, 20))
        self.platforms.append(Platform(1050, self.height - 450, 80, 20))
        
        # Wall platforms
        self.platforms.append(Platform(750, self.height - 350, 60, 20))
        
        # Enemy spawn points
        self.enemy_spawn_points = [
            (450, self.height - 314),
            (850, self.height - 364),
            (1100, self.height - 100),
            (1350, self.height - 384),
            (1600, self.height - 284),
        ]
    
    def _build_procedural_level(self):
        """Build procedurally harder levels."""
        import random
        
        # Generate platforms
        num_platforms = 10 + self.level_number * 2
        for i in range(num_platforms):
            x = 200 + i * (self.width - 400) // num_platforms
            y = self.height - random.randint(100, 350)
            width = random.randint(60, 150)
            self.platforms.append(Platform(x, y, width, 20))
        
        # Generate enemy spawn points
        self.enemy_spawn_points = []
        for i in range(5 + self.level_number):
            x = random.randint(300, self.width - 200)
            y = self.height - 100
            self.enemy_spawn_points.append((x, y))
    
    def spawn_enemies(self, spawner: EnemySpawner):
        """Spawn enemies using provided spawner."""
        self.enemy_spawner = spawner
        
        for point in getattr(self, 'enemy_spawn_points', []):
            enemy = spawner.spawn(point[0], point[1], self.level_number)
            self.enemies.append(enemy)
    
    def update(self):
        """Update level entities."""
        for enemy in self.enemies:
            enemy.update(self.platforms)
        
        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.alive]
    
    def draw(self, surface: pygame.Surface, camera_x: int = 0):
        """
        Draw level on surface.
        
        Args:
            surface: Surface to draw on
            camera_x: Camera offset
        """
        # Draw background elements
        # (parallax clouds or decorations could go here)
        
        # Draw platforms
        for platform in self.platforms:
            platform.draw(surface, camera_x)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(surface, camera_x)
        
        # Draw level end flag
        flag_x = self.end_x - camera_x
        pygame.draw.rect(surface, (200, 50, 50), 
                        (flag_x, self.height - 250, 10, 200))
        pygame.draw.polygon(surface, (255, 255, 0), [
            (flag_x + 10, self.height - 250),
            (flag_x + 60, self.height - 230),
            (flag_x + 10, self.height - 210)
        ])
    
    def check_level_complete(self, player_rect: pygame.Rect) -> bool:
        """Check if player has reached level end."""
        return player_rect.x >= self.end_x
    
    def get_platforms(self) -> List[Platform]:
        """Get all platforms in level."""
        return self.platforms
    
    def get_enemies(self) -> List[Enemy]:
        """Get all enemies in level."""
        return self.enemies


class LevelManager:
    """Manages multiple game levels."""
    
    def __init__(self, screen_height: int):
        """
        Initialize level manager.
        
        Args:
            screen_height: Screen height for level construction
        """
        self.screen_height = screen_height
        self.current_level: Optional[Level] = None
        self.level_number = 1
        self.max_levels = 5
    
    def load_level(self, level_number: int, 
                   enemy_spawner: EnemySpawner) -> Level:
        """
        Load a level by number.
        
        Args:
            level_number: Level to load
            enemy_spawner: Spawner for enemy faces
            
        Returns:
            Loaded Level instance
        """
        self.level_number = level_number
        
        # Calculate level width based on difficulty
        level_width = 2000 + level_number * 500
        
        self.current_level = Level(level_number, level_width, self.screen_height)
        self.current_level.spawn_enemies(enemy_spawner)
        
        return self.current_level
    
    def next_level(self, enemy_spawner: EnemySpawner) -> Optional[Level]:
        """
        Advance to next level.
        
        Args:
            enemy_spawner: Spawner for enemy faces
            
        Returns:
            Next level or None if no more levels
        """
        if self.level_number < self.max_levels:
            return self.load_level(self.level_number + 1, enemy_spawner)
        return None
    
    def get_current_level(self) -> Optional[Level]:
        """Get currently loaded level."""
        return self.current_level
    
    def reset(self):
        """Reset to first level."""
        self.level_number = 1
        self.current_level = None
