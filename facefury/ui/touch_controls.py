"""Touch controls for Android devices."""

import pygame
import sys
from typing import Optional, Tuple

# Detect Android
IS_ANDROID = hasattr(sys, 'getandroidapilevel') or 'ANDROID_ARGUMENT' in __import__('os').environ


class TouchControls:
    """Virtual on-screen D-pad and action buttons for touch devices."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sw = screen.get_width()
        self.sh = screen.get_height()
        self.enabled = IS_ANDROID
        self.opacity = 100

        # Touch state
        self.left_pressed = False
        self.right_pressed = False
        self.jump_pressed = False
        self.jump_just_pressed = False
        self.pause_pressed = False

        # Track active finger IDs
        self._active_touches: dict = {}

        # Button sizes scale with screen
        btn_size = max(60, min(self.sw, self.sh) // 8)
        pad = max(20, btn_size // 3)

        # D-pad (bottom-left)
        dpad_y = self.sh - btn_size - pad
        self.left_rect = pygame.Rect(pad, dpad_y, btn_size, btn_size)
        self.right_rect = pygame.Rect(pad + btn_size + pad // 2, dpad_y,
                                      btn_size, btn_size)

        # Jump button (bottom-right)
        self.jump_rect = pygame.Rect(
            self.sw - btn_size - pad, dpad_y,
            int(btn_size * 1.3), int(btn_size * 1.3)
        )

        # Pause button (top-right)
        pause_size = max(40, btn_size // 2)
        self.pause_rect = pygame.Rect(
            self.sw - pause_size - pad, pad,
            pause_size, pause_size
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle touch events. Returns True if event was consumed."""
        if not self.enabled:
            return False

        if event.type == pygame.FINGERDOWN:
            x = int(event.x * self.sw)
            y = int(event.y * self.sh)
            finger_id = event.finger_id
            self._process_touch_down(finger_id, x, y)
            return True

        elif event.type == pygame.FINGERUP:
            finger_id = event.finger_id
            self._process_touch_up(finger_id)
            return True

        elif event.type == pygame.FINGERMOTION:
            x = int(event.x * self.sw)
            y = int(event.y * self.sh)
            finger_id = event.finger_id
            self._process_touch_move(finger_id, x, y)
            return True

        return False

    def _process_touch_down(self, finger_id: int, x: int, y: int):
        pos = (x, y)
        if self.left_rect.collidepoint(pos):
            self._active_touches[finger_id] = 'left'
            self.left_pressed = True
        elif self.right_rect.collidepoint(pos):
            self._active_touches[finger_id] = 'right'
            self.right_pressed = True
        elif self.jump_rect.collidepoint(pos):
            self._active_touches[finger_id] = 'jump'
            self.jump_pressed = True
            self.jump_just_pressed = True
        elif self.pause_rect.collidepoint(pos):
            self._active_touches[finger_id] = 'pause'
            self.pause_pressed = True

    def _process_touch_up(self, finger_id: int):
        action = self._active_touches.pop(finger_id, None)
        if action == 'left':
            self.left_pressed = 'left' in self._active_touches.values()
        elif action == 'right':
            self.right_pressed = 'right' in self._active_touches.values()
        elif action == 'jump':
            self.jump_pressed = 'jump' in self._active_touches.values()
        elif action == 'pause':
            self.pause_pressed = False

    def _process_touch_move(self, finger_id: int, x: int, y: int):
        old_action = self._active_touches.get(finger_id)
        pos = (x, y)

        new_action = None
        if self.left_rect.collidepoint(pos):
            new_action = 'left'
        elif self.right_rect.collidepoint(pos):
            new_action = 'right'
        elif self.jump_rect.collidepoint(pos):
            new_action = 'jump'

        if new_action != old_action:
            if old_action:
                self._process_touch_up(finger_id)
            if new_action:
                self._active_touches[finger_id] = new_action
                if new_action == 'left':
                    self.left_pressed = True
                elif new_action == 'right':
                    self.right_pressed = True
                elif new_action == 'jump':
                    self.jump_pressed = True
                    self.jump_just_pressed = True

    def get_movement(self) -> int:
        """Return -1 (left), 0 (none), or 1 (right)."""
        if self.left_pressed and not self.right_pressed:
            return -1
        elif self.right_pressed and not self.left_pressed:
            return 1
        return 0

    def draw(self):
        """Draw touch control overlays."""
        if not self.enabled:
            return

        # Semi-transparent surface
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)

        # D-pad left
        left_c = (255, 255, 255, self.opacity + 40) if self.left_pressed else (255, 255, 255, self.opacity)
        pygame.draw.rect(overlay, left_c, self.left_rect, border_radius=12)
        # Arrow
        cx, cy = self.left_rect.center
        s = self.left_rect.width // 4
        pygame.draw.polygon(overlay, (50, 50, 50, 180), [
            (cx + s, cy - s), (cx - s, cy), (cx + s, cy + s)
        ])

        # D-pad right
        right_c = (255, 255, 255, self.opacity + 40) if self.right_pressed else (255, 255, 255, self.opacity)
        pygame.draw.rect(overlay, right_c, self.right_rect, border_radius=12)
        cx, cy = self.right_rect.center
        pygame.draw.polygon(overlay, (50, 50, 50, 180), [
            (cx - s, cy - s), (cx + s, cy), (cx - s, cy + s)
        ])

        # Jump button
        jump_c = (100, 255, 100, self.opacity + 40) if self.jump_pressed else (100, 255, 100, self.opacity)
        pygame.draw.ellipse(overlay, jump_c, self.jump_rect)
        font = pygame.font.Font(None, max(24, self.jump_rect.width // 3))
        jt = font.render("JUMP", True, (0, 80, 0, 200))
        overlay.blit(jt, jt.get_rect(center=self.jump_rect.center))

        # Pause button
        pause_c = (200, 200, 200, self.opacity)
        pygame.draw.rect(overlay, pause_c, self.pause_rect, border_radius=8)
        pcx, pcy = self.pause_rect.center
        bar_w = max(4, self.pause_rect.width // 6)
        bar_h = self.pause_rect.height // 2
        pygame.draw.rect(overlay, (50, 50, 50, 180),
                         (pcx - bar_w - 2, pcy - bar_h // 2, bar_w, bar_h))
        pygame.draw.rect(overlay, (50, 50, 50, 180),
                         (pcx + 2, pcy - bar_h // 2, bar_w, bar_h))

        self.screen.blit(overlay, (0, 0))
