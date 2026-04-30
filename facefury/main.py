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
from ui.sound_settings import SoundSettingsScreen
from ui.touch_controls import TouchControls, IS_ANDROID
from face.processor import FaceProcessor
from assets.audio import AudioManager, SOUND_PACK_SPECS


class FaceFuryGame:
    """Main game application."""

    # Default desktop resolution
    DESKTOP_WIDTH = 1280
    DESKTOP_HEIGHT = 720
    FPS = 60

    def __init__(self):
        """Initialize the game application."""
        pygame.init()
        pygame.display.set_caption("FaceFury: Battle Platformer")

        # Determine screen size - auto-scale for Android
        if IS_ANDROID:
            info = pygame.display.Info()
            self.SCREEN_WIDTH = info.current_w
            self.SCREEN_HEIGHT = info.current_h
            flags = pygame.FULLSCREEN | pygame.SCALED
        else:
            self.SCREEN_WIDTH = self.DESKTOP_WIDTH
            self.SCREEN_HEIGHT = self.DESKTOP_HEIGHT
            flags = pygame.SCALED

        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), flags
        )
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
        self.sound_settings = SoundSettingsScreen(self.screen)
        self.touch_controls = TouchControls(self.screen)

        # Audio
        self.audio = AudioManager()

        # Setup callbacks
        self._setup_menu_callbacks()
        self._setup_game_callbacks()
        self._setup_game_over_callbacks()
        self._setup_sound_settings_callbacks()

        # Face processor
        self.face_processor = FaceProcessor()

        # Auto-load default faces on Android (no file dialogs)
        if IS_ANDROID:
            self._load_default_faces()

    def _load_default_faces(self):
        """Load bundled default face images when file dialogs are unavailable."""
        base = os.path.dirname(os.path.abspath(__file__))
        player_path = os.path.join(base, 'player.jpeg')
        enemy_path = os.path.join(base, 'enemy.jpeg')
        if os.path.exists(player_path):
            self._on_player_upload(player_path)
        if os.path.exists(enemy_path):
            self._on_enemy_upload(enemy_path)

    def _setup_menu_callbacks(self):
        """Setup menu button callbacks."""
        self.menu_system.start_menu.set_callbacks(
            on_player_upload=self._on_player_upload,
            on_enemy_upload=self._on_enemy_upload,
            on_start=self._start_game,
            on_help=self._show_help,
            on_sound_settings=self._open_sound_settings
        )

    def _setup_game_callbacks(self):
        pass

    def _setup_game_over_callbacks(self):
        self.game_over_screen.set_callbacks(
            on_restart=self._restart_game,
            on_menu=self._return_to_menu
        )

    def _setup_sound_settings_callbacks(self):
        self.sound_settings.set_callbacks(
            on_close=self._close_sound_settings,
            on_next_pack=self._next_sound_pack,
            on_prev_pack=self._prev_sound_pack,
            on_preview=self._preview_sound,
            on_upload_custom=self._upload_custom_sound
        )
        # Sync initial pack info
        self._sync_pack_info()

    def _sync_pack_info(self):
        pid = self.audio.current_pack_id
        spec = SOUND_PACK_SPECS.get(pid, {})
        self.sound_settings.update_pack_info(
            spec.get("name", "Unknown"),
            spec.get("description", "")
        )

    def _open_sound_settings(self):
        self.audio.play_sound('click')
        self._sync_pack_info()
        self.sound_settings.show()

    def _close_sound_settings(self):
        self.audio.play_sound('click')
        self.sound_settings.hide()

    def _next_sound_pack(self):
        self.audio.next_pack()
        self._sync_pack_info()
        self.audio.play_sound('click')

    def _prev_sound_pack(self):
        self.audio.prev_pack()
        self._sync_pack_info()
        self.audio.play_sound('click')

    def _preview_sound(self, sound_name: str):
        self.audio.preview_sound(sound_name)

    def _upload_custom_sound(self, sound_name: str, filepath: str):
        """Handle a user-uploaded custom voice file for a specific event."""
        if self.audio.load_custom_sound(sound_name, filepath):
            self.sound_settings.set_custom_status(
                sound_name, os.path.basename(filepath)
            )
            self.audio.play_sound(sound_name)  # preview immediately

    def _on_player_upload(self, path: str):
        try:
            processed = self.face_processor.process_image(path, circular_crop=True)
            if processed:
                self.player_face = self._pil_to_pygame(processed)
                self.audio.play_sound('click')
            else:
                self.player_face = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error loading player face: {e}")

    def _on_enemy_upload(self, path: str):
        try:
            processed = self.face_processor.process_image(path, circular_crop=True)
            if processed:
                enemy_face = self._pil_to_pygame(processed)
                self.enemy_faces.append(enemy_face)
                self.audio.play_sound('click')
            else:
                self.enemy_faces.append(pygame.image.load(path).convert_alpha())
        except Exception as e:
            print(f"Error loading enemy face: {e}")

    def _pil_to_pygame(self, pil_image: Image.Image) -> pygame.Surface:
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
        data = pil_image.tobytes()
        size = pil_image.size
        return pygame.image.fromstring(data, size, 'RGBA')

    def _start_game(self):
        self.audio.play_sound('click')
        self.menu_system.close_menu()
        self._init_game_engine()
        self.in_game = True
        self.audio.play_sound('initial')
        self.audio.play_music()

    def _init_game_engine(self):
        self.game_engine = GameEngine(
            self.screen,
            player_face=self.player_face,
            enemy_faces=self.enemy_faces if self.enemy_faces else None
        )
        self.game_engine.on_score_change = self._on_score_change
        self.game_engine.on_health_change = self._on_health_change
        self.game_engine.on_level_complete = self._on_level_complete
        self.game_engine.on_game_over = self._on_game_over
        self.game_engine.on_screenshot = self._take_screenshot
        self.game_engine.on_play_sound = self._on_play_sound

    def _on_score_change(self, score: int):
        self.hud.update_stats(score, self.hud.health, self.hud.time, self.hud.level)

    def _on_health_change(self, health: int):
        self.hud.update_stats(self.hud.score, health, self.hud.time, self.hud.level)

    def _on_play_sound(self, sound_name: str):
        self.audio.play_sound(sound_name)

    def _on_level_complete(self, level: int, score: int):
        self.audio.play_sound('win')
        import threading

        def play_start_sound():
            import time
            time.sleep(0.5)
            self.audio.play_sound('initial')
        threading.Thread(target=play_start_sound, daemon=True).start()
        self.hud.update_stats(score, self.hud.health, self.hud.time, level)

    def _on_game_over(self, score: int, victory: bool):
        if victory:
            self.audio.play_sound('win')
        else:
            self.audio.play_sound('game_over')
        self.audio.stop_music()
        self.in_game = False
        self.game_over_screen.show(score, victory)

    def _restart_game(self):
        self.audio.play_sound('click')
        if self.game_engine:
            self.game_engine.restart()
        self.in_game = True
        self.audio.play_music()

    def _return_to_menu(self):
        self.audio.play_sound('click')
        self.in_game = False
        self.menu_system.open_start_menu()

    def _show_help(self):
        self.menu_system.start_menu.show_help()

    def _take_screenshot(self, surface: pygame.Surface):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"facefury_screenshot_{timestamp}.png"
            save_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(save_dir, filename)
            pygame.image.save(surface, filepath)
            self.audio.play_sound('click')
        except Exception:
            pass

    def run(self):
        """Main game loop."""
        print("=" * 50)
        print("FaceFury: Battle Platformer")
        print("=" * 50)
        if IS_ANDROID:
            print("Running on Android - touch controls enabled")
        print("Starting game...")
        print("=" * 50)

        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Handle Android lifecycle
                if event.type == pygame.APP_WILLENTERBACKGROUND:
                    self.audio.pause_music()
                    if self.in_game and self.game_engine:
                        self.game_engine.paused = True
                elif event.type == pygame.APP_DIDENTERFOREGROUND:
                    if self.in_game and self.game_engine and self.audio.music_playing:
                        self.audio.unpause_music()

                # Sound settings takes priority
                if self.sound_settings.visible:
                    if self.sound_settings.handle_event(event):
                        continue

                # Touch controls (always process on Android)
                if self.touch_controls.enabled:
                    self.touch_controls.handle_event(event)

                # Menu events
                if not self.in_game:
                    if self.menu_system.handle_event(event):
                        continue
                    if self.game_over_screen.handle_event(event):
                        continue

                # Game events
                if self.in_game and self.game_engine:
                    self.game_engine.handle_event(event)

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.running = False

            # Apply touch controls to game engine
            if self.in_game and self.game_engine and self.touch_controls.enabled:
                movement = self.touch_controls.get_movement()
                if movement != 0:
                    self.game_engine.player.move(movement)
                if self.touch_controls.jump_just_pressed:
                    if self.game_engine.player.jump():
                        self.game_engine._play_sound('jump')
                    self.touch_controls.jump_just_pressed = False
                if self.touch_controls.pause_pressed:
                    self.game_engine.paused = not self.game_engine.paused
                    self.touch_controls.pause_pressed = False

            # Update
            if self.in_game and self.game_engine:
                self.game_engine.update(dt)
                stats = self.game_engine.get_stats()
                self.hud.update_stats(
                    stats['score'], stats['health'],
                    stats['time'], stats['level']
                )

            # Draw
            if self.in_game and self.game_engine:
                self.game_engine.draw()
                self.hud.draw()
                if self.touch_controls.enabled:
                    self.touch_controls.draw()
                if self.game_engine.game_over:
                    self.game_over_screen.draw()
            else:
                self.menu_system.draw()

            # Sound settings overlay draws on top
            if self.sound_settings.visible:
                self.sound_settings.draw()

            pygame.display.flip()

        pygame.quit()


def main():
    """Game entry point."""
    game = FaceFuryGame()
    game.run()


if __name__ == "__main__":
    main()
