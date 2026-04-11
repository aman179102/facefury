"""FaceFury: Battle Platformer - Main Entry Point"""

import pygame
import sys
import os
import io
from datetime import datetime
from PIL import Image

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.engine import GameEngine
from game.player import Player
from ui.menu import MenuSystem
from ui.hud import HUD, GameOverScreen
from face.processor import FaceProcessor
from assets.audio import AudioManager


class FaceFuryGame:
    """Main game application."""
    
    # Screen settings
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    
    def __init__(self):
        """Initialize the game application."""
        pygame.init()
        pygame.display.set_caption("FaceFury: Battle Platformer")
        
        # Create main window
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        self.in_game = False
        self.game_engine: GameEngine = None
        
        # Face images
        self.player_face: pygame.Surface = None
        self.enemy_faces: list = []
        
        # UI systems
        self.menu_system = MenuSystem(self.screen)
        self.hud = HUD(self.screen)
        self.game_over_screen = GameOverScreen(self.screen)
        
        # Audio
        self.audio = AudioManager()
        
        # Setup callbacks
        self._setup_menu_callbacks()
        self._setup_game_callbacks()
        self._setup_game_over_callbacks()
        
        # Face processor
        self.face_processor = FaceProcessor()
    
    def _setup_menu_callbacks(self):
        """Setup menu button callbacks."""
        self.menu_system.start_menu.set_callbacks(
            on_player_upload=self._on_player_upload,
            on_enemy_upload=self._on_enemy_upload,
            on_start=self._start_game,
            on_help=self._show_help
        )
    
    def _setup_game_callbacks(self):
        """Setup game engine callbacks."""
        pass  # Set when engine is created
    
    def _setup_game_over_callbacks(self):
        """Setup game over screen callbacks."""
        self.game_over_screen.set_callbacks(
            on_restart=self._restart_game,
            on_menu=self._return_to_menu
        )
    
    def _on_player_upload(self, path: str):
        """Handle player face upload."""
        try:
            # Process face
            processed = self.face_processor.process_image(path, circular_crop=True)
            if processed:
                # Convert PIL to pygame surface
                self.player_face = self._pil_to_pygame(processed)
                print(f"Player face loaded from: {path}")
                self.audio.play_sound('click')
            else:
                print(f"No face detected in: {path}")
                # Try to load anyway as fallback
                self.player_face = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error loading player face: {e}")
    
    def _on_enemy_upload(self, path: str):
        """Handle enemy face upload."""
        try:
            processed = self.face_processor.process_image(path, circular_crop=True)
            if processed:
                enemy_face = self._pil_to_pygame(processed)
                self.enemy_faces.append(enemy_face)
                print(f"Enemy face loaded from: {path}")
                self.audio.play_sound('click')
            else:
                print(f"No face detected in: {path}")
                self.enemy_faces.append(pygame.image.load(path).convert_alpha())
        except Exception as e:
            print(f"Error loading enemy face: {e}")
    
    def _pil_to_pygame(self, pil_image: Image.Image) -> pygame.Surface:
        """Convert PIL Image to pygame Surface."""
        # Convert to RGBA mode
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
        
        # Get image data
        data = pil_image.tobytes()
        size = pil_image.size
        
        # Create pygame surface
        return pygame.image.fromstring(data, size, 'RGBA')
    
    def _start_game(self):
        """Start the game."""
        self.audio.play_sound('click')
        self.menu_system.close_menu()
        self._init_game_engine()
        self.in_game = True
        self.audio.play_sound('initial')  # Game start sound
        self.audio.play_music()
    
    def _init_game_engine(self):
        """Initialize game engine with current faces."""
        self.game_engine = GameEngine(
            self.screen,
            player_face=self.player_face,
            enemy_faces=self.enemy_faces if self.enemy_faces else None
        )
        
        # Connect callbacks
        self.game_engine.on_score_change = self._on_score_change
        self.game_engine.on_health_change = self._on_health_change
        self.game_engine.on_level_complete = self._on_level_complete
        self.game_engine.on_game_over = self._on_game_over
        self.game_engine.on_screenshot = self._take_screenshot
        self.game_engine.on_play_sound = self._on_play_sound
    
    def _on_score_change(self, score: int):
        """Handle score update."""
        self.hud.update_stats(score, self.hud.health, self.hud.time, self.hud.level)
    
    def _on_health_change(self, health: int):
        """Handle health update."""
        self.hud.update_stats(self.hud.score, health, self.hud.time, self.hud.level)
    
    def _on_play_sound(self, sound_name: str):
        """Handle sound playback request."""
        self.audio.play_sound(sound_name)
    
    def _on_level_complete(self, level: int, score: int):
        """Handle level completion."""
        self.audio.play_sound('win')
        # Play initial sound for new level (after a short delay)
        import threading
        def play_start_sound():
            import time
            time.sleep(0.5)  # Small delay after win sound
            self.audio.play_sound('initial')
        threading.Thread(target=play_start_sound).start()
        self.hud.update_stats(score, self.hud.health, self.hud.time, level)
    
    def _on_game_over(self, score: int, victory: bool):
        """Handle game over."""
        if victory:
            self.audio.play_sound('win')
        else:
            self.audio.play_sound('game_over')
        
        self.audio.stop_music()
        self.in_game = False
        self.game_over_screen.show(score, victory)
    
    def _restart_game(self):
        """Restart current game."""
        self.audio.play_sound('click')
        if self.game_engine:
            self.game_engine.restart()
        self.in_game = True
        self.audio.play_music()
    
    def _return_to_menu(self):
        """Return to main menu."""
        self.audio.play_sound('click')
        self.in_game = False
        self.menu_system.open_start_menu()
    
    def _show_help(self):
        """Show help screen."""
        self.menu_system.start_menu.show_help()
    
    def _take_screenshot(self, surface: pygame.Surface):
        """Save gameplay screenshot."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"facefury_screenshot_{timestamp}.png"
            
            # Get current directory
            save_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(save_dir, filename)
            
            pygame.image.save(surface, filepath)
            print(f"Screenshot saved: {filepath}")
            self.audio.play_sound('click')
        except Exception as e:
            print(f"Screenshot failed: {e}")
    
    def run(self):
        """Main game loop."""
        print("=" * 50)
        print("FaceFury: Battle Platformer")
        print("=" * 50)
        print("\nControls:")
        print("  LEFT/RIGHT or A/D - Move")
        print("  SPACE or UP - Jump")
        print("  P - Pause")
        print("  F12 - Screenshot")
        print("\nStarting game...")
        print("=" * 50)
        
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0  # Delta time in seconds
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Menu events
                if not self.in_game:
                    if self.menu_system.handle_event(event):
                        continue
                    if self.game_over_screen.handle_event(event):
                        continue
                
                # Game events
                if self.in_game and self.game_engine:
                    self.game_engine.handle_event(event)
                    
                    # ESC to quit game
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Update
            if self.in_game and self.game_engine:
                self.game_engine.update(dt)
                
                # Update HUD with current stats
                stats = self.game_engine.get_stats()
                self.hud.update_stats(
                    stats['score'],
                    stats['health'],
                    stats['time'],
                    stats['level']
                )
            
            # Draw
            if self.in_game and self.game_engine:
                self.game_engine.draw()
                self.hud.draw()
                
                if self.game_engine.game_over:
                    self.game_over_screen.draw()
            else:
                self.menu_system.draw()
            
            # Update display
            pygame.display.flip()
        
        # Cleanup
        pygame.quit()
        print("\nThanks for playing FaceFury!")


def main():
    """Game entry point."""
    game = FaceFuryGame()
    game.run()


if __name__ == "__main__":
    main()
