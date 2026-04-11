"""Menu system for FaceFury."""

import pygame
import os
from typing import Callable, Optional, Tuple
from tkinter import filedialog
import tkinter as tk


class Button:
    """Interactive button widget."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, font_size: int = 32,
                 color: Tuple[int, int, int] = (80, 80, 150),
                 hover_color: Tuple[int, int, int] = (120, 120, 200),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        """
        Initialize button.
        
        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button text
            font_size: Text size
            color: Normal button color
            hover_color: Hover button color
            text_color: Text color
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.callback: Optional[Callable] = None
    
    def set_callback(self, callback: Callable):
        """Set button click callback."""
        self.callback = callback
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input event.
        
        Returns:
            True if button was clicked
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and self.callback:
                self.callback()
                return True
        
        return False
    
    def draw(self, surface: pygame.Surface):
        """Draw button on surface."""
        color = self.hover_color if self.hovered else self.color
        
        # Draw button background
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        
        # Draw border
        border_color = (255, 255, 255) if self.hovered else (150, 150, 150)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=10)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class UploadButton(Button):
    """Button for uploading images with file dialog."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str = "Upload Image",
                 file_types: Tuple[Tuple[str, str], ...] = (("Images", "*.png *.jpg *.jpeg"),)):
        """
        Initialize upload button.
        
        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button label
            file_types: Allowed file types
        """
        super().__init__(x, y, width, height, text)
        self.file_types = file_types
        self.selected_path: Optional[str] = None
        self.preview: Optional[pygame.Surface] = None
        self.preview_rect = pygame.Rect(x + width + 20, y, height, height)
        
        # Initialize tkinter for file dialog
        self._root = tk.Tk()
        self._root.withdraw()
    
    def set_callback(self, callback: Callable[[str], None]):
        """Set callback that receives file path."""
        self.callback = callback
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle click to open file dialog."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self._open_dialog()
                return True
        return False
    
    def _open_dialog(self):
        """Open file selection dialog."""
        path = filedialog.askopenfilename(
            title=f"Select {self.text}",
            filetypes=self.file_types
        )
        
        if path and os.path.exists(path):
            self.selected_path = path
            self._create_preview()
            
            if self.callback:
                self.callback(path)
    
    def _create_preview(self):
        """Create preview of selected image."""
        if self.selected_path:
            try:
                img = pygame.image.load(self.selected_path)
                # Scale to preview size
                self.preview = pygame.transform.scale(img, 
                                                     (self.preview_rect.width,
                                                      self.preview_rect.height))
            except Exception:
                self.preview = None
    
    def draw(self, surface: pygame.Surface):
        """Draw button and preview."""
        super().draw(surface)
        
        # Draw preview box
        pygame.draw.rect(surface, (60, 60, 60), self.preview_rect, border_radius=5)
        pygame.draw.rect(surface, (150, 150, 150), self.preview_rect, 2, border_radius=5)
        
        if self.preview:
            # Clip preview to box
            surface.blit(self.preview, self.preview_rect.topleft)
        else:
            # Draw placeholder text
            font = pygame.font.Font(None, 20)
            text = font.render("?", True, (200, 200, 200))
            text_rect = text.get_rect(center=self.preview_rect.center)
            surface.blit(text, text_rect)
    
    def get_selected_path(self) -> Optional[str]:
        """Get selected file path."""
        return self.selected_path
    
    def cleanup(self):
        """Cleanup tkinter resources."""
        self._root.destroy()


class StartMenu:
    """Main start menu screen."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize start menu.
        
        Args:
            screen: Main surface to draw on
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 36)
        
        # Buttons
        center_x = self.screen_width // 2 - 150
        
        self.player_upload = UploadButton(
            center_x, 200, 300, 60, 
            "Upload Player Face"
        )
        
        self.enemy_upload = UploadButton(
            center_x, 280, 300, 60,
            "Upload Enemy Face"
        )
        
        self.start_button = Button(
            center_x, 400, 300, 70,
            "START GAME",
            font_size=40,
            color=(50, 150, 50),
            hover_color=(70, 200, 70)
        )
        
        self.help_button = Button(
            center_x, 490, 300, 50,
            "How to Play",
            font_size=28,
            color=(100, 100, 100)
        )
        
        self.buttons = [
            self.player_upload,
            self.enemy_upload,
            self.start_button,
            self.help_button
        ]
        
        # State
        self.showing_help = False
        self.player_face_path: Optional[str] = None
        self.enemy_face_path: Optional[str] = None
        
        # Background
        self.bg_color = (30, 30, 50)
    
    def set_callbacks(self, 
                     on_player_upload: Callable[[str], None],
                     on_enemy_upload: Callable[[str], None],
                     on_start: Callable,
                     on_help: Optional[Callable] = None):
        """Set button callbacks."""
        self.player_upload.set_callback(on_player_upload)
        self.enemy_upload.set_callback(on_enemy_upload)
        self.start_button.set_callback(on_start)
        if on_help:
            self.help_button.set_callback(on_help)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle menu events.
        
        Returns:
            True if event was consumed
        """
        if self.showing_help:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.showing_help = False
                return True
        
        for button in self.buttons:
            if button.handle_event(event):
                return True
        
        return False
    
    def draw(self):
        """Draw menu screen."""
        # Background
        self.screen.fill(self.bg_color)
        
        # Draw title
        title = self.title_font.render("FaceFury", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.subtitle_font.render("Battle Platformer", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 130))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        # Draw status
        self._draw_status()
        
        # Draw help overlay
        if self.showing_help:
            self._draw_help()
    
    def _draw_status(self):
        """Draw upload status indicators."""
        font = pygame.font.Font(None, 24)
        
        # Player status
        if self.player_upload.selected_path:
            status = "Player Face: Ready"
            color = (100, 255, 100)
        else:
            status = "Player Face: Default"
            color = (255, 200, 100)
        
        text = font.render(status, True, color)
        self.screen.blit(text, (self.screen_width // 2 - 140, 265))
        
        # Enemy status
        if self.enemy_upload.selected_path:
            status = "Enemy Face: Ready"
            color = (100, 255, 100)
        else:
            status = "Enemy Face: Default"
            color = (255, 200, 100)
        
        text = font.render(status, True, color)
        self.screen.blit(text, (self.screen_width // 2 - 140, 345))
    
    def _draw_help(self):
        """Draw help overlay."""
        # Semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(220)
        overlay.fill((20, 20, 30))
        self.screen.blit(overlay, (0, 0))
        
        # Help text
        help_lines = [
            ("How to Play", 72, (255, 100, 100)),
            ("", 36, (255, 255, 255)),
            ("Controls:", 36, (200, 200, 200)),
            ("  LEFT/RIGHT or A/D - Move", 28, (255, 255, 255)),
            ("  SPACE or UP - Jump", 28, (255, 255, 255)),
            ("  P - Pause game", 28, (255, 255, 255)),
            ("  F12 - Take screenshot", 28, (255, 255, 255)),
            ("  ESC - Quit game", 28, (255, 100, 100)),
            ("", 28, (255, 255, 255)),
            ("Objective:", 36, (200, 200, 200)),
            ("  Jump on enemies to defeat them!", 28, (255, 255, 255)),
            ("  Reach the yellow flag to complete level", 28, (255, 255, 255)),
            ("  Avoid touching enemies from sides", 28, (255, 255, 255)),
            ("", 28, (255, 255, 255)),
            ("Click or press any key to close", 24, (150, 150, 150))
        ]
        
        y = 100
        for text, size, color in help_lines:
            font = pygame.font.Font(None, size)
            surface = font.render(text, True, color)
            rect = surface.get_rect(center=(self.screen_width // 2, y))
            self.screen.blit(surface, rect)
            y += size + 10
    
    def show_help(self):
        """Show help screen."""
        self.showing_help = True
    
    def get_face_paths(self) -> Tuple[Optional[str], Optional[str]]:
        """Get selected face image paths."""
        return (self.player_upload.selected_path, 
                self.enemy_upload.selected_path)


class MenuSystem:
    """Manages all game menus."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize menu system.
        
        Args:
            screen: Main surface
        """
        self.screen = screen
        self.start_menu = StartMenu(screen)
        self.active_menu: Optional[StartMenu] = self.start_menu
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle menu events."""
        if self.active_menu:
            return self.active_menu.handle_event(event)
        return False
    
    def draw(self):
        """Draw active menu."""
        if self.active_menu:
            self.active_menu.draw()
    
    def close_menu(self):
        """Close all menus."""
        self.active_menu = None
    
    def open_start_menu(self):
        """Open start menu."""
        self.active_menu = self.start_menu
