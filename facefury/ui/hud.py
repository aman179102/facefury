"""HUD and game over screen for FaceFury."""

import math
import pygame
from typing import Tuple, Optional, Callable


class HUD:
    """In-game heads-up display."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize HUD.
        
        Args:
            screen: Main surface to draw on
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        
        # Fonts
        self.score_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # State
        self.score = 0
        self.health = 3
        self.time = 0
        self.level = 1
    
    def update_stats(self, score: int, health: int, time: int, level: int):
        """Update displayed statistics."""
        self.score = score
        self.health = health
        self.time = time
        self.level = level
    
    def draw(self):
        """Draw HUD elements."""
        # Semi-transparent background bar
        bar = pygame.Surface((self.screen_width, 50))
        bar.set_alpha(180)
        bar.fill((20, 20, 30))
        self.screen.blit(bar, (0, 0))
        
        # Score
        score_text = self.score_font.render(f"Score: {self.score}", True, (255, 255, 100))
        self.screen.blit(score_text, (20, 12))
        
        # Health (hearts)
        health_x = 250
        for i in range(3):
            if i < self.health:
                color = (255, 50, 50)  # Red heart
            else:
                color = (100, 100, 100)  # Gray heart
            
            self._draw_heart(health_x + i * 30, 25, 10, color)
        
        # Time
        minutes = self.time // 60
        seconds = self.time % 60
        time_str = f"Time: {minutes}:{seconds:02d}"
        time_text = self.score_font.render(time_str, True, (100, 255, 255))
        self.screen.blit(time_text, (400, 12))
        
        # Level
        level_text = self.score_font.render(f"Level {self.level}", True, (100, 255, 100))
        self.screen.blit(level_text, (600, 12))
        
        # Help hint
        hint = self.small_font.render("P: Pause | F12: Screenshot | ESC: Quit", True, (150, 150, 150))
        self.screen.blit(hint, (self.screen_width - 300, 15))
    
    def _draw_heart(self, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Draw a heart shape."""
        points = []
        for angle in range(360):
            rad = angle * 3.14159 / 180
            # Heart formula
            hx = size * 16 * (math.sin(rad) ** 3)
            hy = -size * (13 * math.cos(rad) - 
                         5 * math.cos(2 * rad) - 
                         2 * math.cos(3 * rad) - 
                         math.cos(4 * rad))
            points.append((x + hx / 16, y + hy / 16))
        
        pygame.draw.polygon(self.screen, color, points)


class GameOverScreen:
    """Game over and victory screen."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize game over screen.
        
        Args:
            screen: Main surface
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.score_font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 36)
        
        # Buttons
        self.restart_rect = pygame.Rect(self.screen_width // 2 - 100, 400, 200, 60)
        self.menu_rect = pygame.Rect(self.screen_width // 2 - 100, 480, 200, 60)
        
        # Callbacks
        self.on_restart: Optional[Callable] = None
        self.on_menu: Optional[Callable] = None
        
        # State
        self.victory = False
        self.score = 0
        self.hovered_button: Optional[str] = None
    
    def show(self, score: int, victory: bool = False):
        """
        Show game over screen.
        
        Args:
            score: Final score
            victory: True if player won, False if game over
        """
        self.score = score
        self.victory = victory
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle screen events.
        
        Returns:
            True if event was consumed
        """
        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.hovered_button = None
            if self.restart_rect.collidepoint(pos):
                self.hovered_button = 'restart'
            elif self.menu_rect.collidepoint(pos):
                self.hovered_button = 'menu'
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered_button == 'restart' and self.on_restart:
                self.on_restart()
                return True
            elif self.hovered_button == 'menu' and self.on_menu:
                self.on_menu()
                return True
        
        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if self.on_restart:
                    self.on_restart()
                    return True
            elif event.key == pygame.K_ESCAPE:
                if self.on_menu:
                    self.on_menu()
                    return True
        
        return False
    
    def draw(self):
        """Draw game over screen."""
        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        if self.victory:
            title_text = "VICTORY!"
            title_color = (100, 255, 100)
        else:
            title_text = "GAME OVER"
            title_color = (255, 100, 100)
        
        title = self.title_font.render(title_text, True, title_color)
        title_rect = title.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Final score
        score_text = self.score_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 250))
        self.screen.blit(score_text, score_rect)
        
        # High score indicator
        congrats = self.button_font.render("New High Score!" if self.score > 1000 else "", 
                                          True, (255, 255, 100))
        congrats_rect = congrats.get_rect(center=(self.screen_width // 2, 300))
        self.screen.blit(congrats, congrats_rect)
        
        # Restart button
        restart_color = (70, 150, 70) if self.hovered_button == 'restart' else (50, 100, 50)
        pygame.draw.rect(self.screen, restart_color, self.restart_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.restart_rect, 2, border_radius=10)
        
        restart_text = self.button_font.render("Restart (R)", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=self.restart_rect.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # Menu button
        menu_color = (100, 100, 150) if self.hovered_button == 'menu' else (80, 80, 120)
        pygame.draw.rect(self.screen, menu_color, self.menu_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.menu_rect, 2, border_radius=10)
        
        menu_text = self.button_font.render("Main Menu (Esc)", True, (255, 255, 255))
        menu_text_rect = menu_text.get_rect(center=self.menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)
        
        # Meme text
        meme_font = pygame.font.Font(None, 28)
        if self.victory:
            meme = "Your face conquered all!"
        else:
            meme = "Skill issue? Try uploading a stronger face!"
        
        meme_text = meme_font.render(meme, True, (200, 200, 200))
        meme_rect = meme_text.get_rect(center=(self.screen_width // 2, 580))
        self.screen.blit(meme_text, meme_rect)
    
    def set_callbacks(self, on_restart: Callable, on_menu: Callable):
        """Set button callbacks."""
        self.on_restart = on_restart
        self.on_menu = on_menu
