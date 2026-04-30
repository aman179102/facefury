"""Sound effects settings screen for FaceFury.

Users can:
1. Choose a built-in sound pack (Default, Funny, Retro, Meme, Epic)
2. Manually upload their own voice/sound file for ANY individual event
   (jump, kill, damage, win, game over, click, game start).
   Custom uploads override the active pack for that event.
"""

import pygame
import os
import sys
from typing import Callable, Optional

IS_ANDROID = hasattr(sys, 'getandroidapilevel') or 'ANDROID_ARGUMENT' in os.environ
if not IS_ANDROID:
    try:
        from tkinter import filedialog
        import tkinter as tk
        _TK_AVAILABLE = True
    except ImportError:
        _TK_AVAILABLE = False
else:
    _TK_AVAILABLE = False


class SoundSettingsScreen:
    """In-game UI for changing voice effect packs and uploading custom sounds."""

    SOUND_LABELS = {
        'jump': 'Jump Sound',
        'hit': 'Kill Enemy Sound',
        'damage': 'Damage Sound',
        'win': 'Level Win Sound',
        'game_over': 'Game Over Sound',
        'click': 'Menu Click Sound',
        'initial': 'Game Start Sound',
    }
    SOUND_ORDER = ['jump', 'hit', 'damage', 'win', 'game_over', 'click', 'initial']

    _AUDIO_FILETYPES = (
        ("Audio files", "*.wav *.mp3 *.ogg"),
        ("WAV", "*.wav"),
        ("MP3", "*.mp3"),
        ("OGG", "*.ogg"),
    )

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sw = screen.get_width()
        self.sh = screen.get_height()

        # Fonts
        self.title_font = pygame.font.Font(None, 52)
        self.label_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.pack_font = pygame.font.Font(None, 40)
        self.tiny_font = pygame.font.Font(None, 18)

        # State
        self.visible = False
        self.hovered: Optional[str] = None

        # Callbacks
        self.on_close: Optional[Callable] = None
        self.on_next_pack: Optional[Callable] = None
        self.on_prev_pack: Optional[Callable] = None
        self.on_preview: Optional[Callable] = None
        self.on_upload_custom: Optional[Callable] = None  # (sound_name, filepath)

        # Current pack info
        self.pack_name = "Default"
        self.pack_description = "Classic beep-boop sounds"

        # Per-sound custom file status (sound_name -> basename or None)
        self.custom_files: dict = {}

        # Tkinter root (desktop only)
        self._tk_root = None
        if _TK_AVAILABLE:
            self._tk_root = tk.Tk()
            self._tk_root.withdraw()

        self._build_layout()

    def _build_layout(self):
        cx = self.sw // 2
        self.title_y = 30
        self.pack_y = 85

        # Pack selector arrows
        self.prev_rect = pygame.Rect(cx - 220, self.pack_y - 5, 40, 40)
        self.next_rect = pygame.Rect(cx + 180, self.pack_y - 5, 40, 40)

        # Per-sound rows: [label]  [Preview btn]  [Upload btn]  [status]
        self.rows: dict = {}
        start_y = 160
        row_h = 50
        for i, sname in enumerate(self.SOUND_ORDER):
            by = start_y + i * row_h
            preview_rect = pygame.Rect(cx + 20, by + 5, 90, 34)
            upload_rect = pygame.Rect(cx + 120, by + 5, 130, 34)
            label_rect = pygame.Rect(cx - 240, by + 10, 250, 28)
            self.rows[sname] = {
                'preview': preview_rect,
                'upload': upload_rect,
                'label': label_rect,
                'y': by,
            }

        # Back button
        last_y = start_y + len(self.SOUND_ORDER) * row_h + 15
        self.back_rect = pygame.Rect(cx - 80, last_y, 160, 50)

    # ---- public API ----

    def set_callbacks(self, on_close: Callable, on_next_pack: Callable,
                      on_prev_pack: Callable, on_preview: Callable,
                      on_upload_custom: Optional[Callable] = None):
        self.on_close = on_close
        self.on_next_pack = on_next_pack
        self.on_prev_pack = on_prev_pack
        self.on_preview = on_preview
        self.on_upload_custom = on_upload_custom

    def update_pack_info(self, name: str, description: str):
        self.pack_name = name
        self.pack_description = description

    def set_custom_status(self, sound_name: str, filename: Optional[str]):
        """Mark a sound slot as having a custom file loaded."""
        if filename:
            self.custom_files[sound_name] = filename
        else:
            self.custom_files.pop(sound_name, None)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    # ---- event handling ----

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.hovered = None
            if self.prev_rect.collidepoint(pos):
                self.hovered = 'prev'
            elif self.next_rect.collidepoint(pos):
                self.hovered = 'next'
            elif self.back_rect.collidepoint(pos):
                self.hovered = 'back'
            else:
                for sname, rects in self.rows.items():
                    if rects['preview'].collidepoint(pos):
                        self.hovered = f'preview_{sname}'
                        break
                    if rects['upload'].collidepoint(pos):
                        self.hovered = f'upload_{sname}'
                        break

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered == 'prev' and self.on_prev_pack:
                self.on_prev_pack()
                return True
            elif self.hovered == 'next' and self.on_next_pack:
                self.on_next_pack()
                return True
            elif self.hovered == 'back' and self.on_close:
                self.on_close()
                return True
            elif self.hovered and self.hovered.startswith('preview_'):
                sname = self.hovered[len('preview_'):]
                if self.on_preview:
                    self.on_preview(sname)
                return True
            elif self.hovered and self.hovered.startswith('upload_'):
                sname = self.hovered[len('upload_'):]
                self._upload_custom_sound(sname)
                return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.on_close:
                    self.on_close()
                return True
            elif event.key == pygame.K_LEFT:
                if self.on_prev_pack:
                    self.on_prev_pack()
                return True
            elif event.key == pygame.K_RIGHT:
                if self.on_next_pack:
                    self.on_next_pack()
                return True

        return self.visible  # consume all events while visible

    def _upload_custom_sound(self, sound_name: str):
        """Open a file picker so user can choose a custom sound file."""
        if not _TK_AVAILABLE:
            return
        label = self.SOUND_LABELS.get(sound_name, sound_name)
        path = filedialog.askopenfilename(
            title=f"Choose custom {label}",
            filetypes=self._AUDIO_FILETYPES,
        )
        if path and os.path.exists(path):
            self.custom_files[sound_name] = os.path.basename(path)
            if self.on_upload_custom:
                self.on_upload_custom(sound_name, path)

    # ---- drawing ----

    def draw(self):
        if not self.visible:
            return

        overlay = pygame.Surface((self.sw, self.sh))
        overlay.set_alpha(235)
        overlay.fill((25, 25, 40))
        self.screen.blit(overlay, (0, 0))

        cx = self.sw // 2

        # Title
        title = self.title_font.render("Voice Effects", True, (255, 200, 100))
        self.screen.blit(title, title.get_rect(center=(cx, self.title_y)))

        # ---- Pack selector ----
        # Left arrow
        ac = (255, 255, 100) if self.hovered == 'prev' else (200, 200, 200)
        pygame.draw.polygon(self.screen, ac, [
            (self.prev_rect.right - 5, self.prev_rect.top + 5),
            (self.prev_rect.left + 5, self.prev_rect.centery),
            (self.prev_rect.right - 5, self.prev_rect.bottom - 5),
        ])
        # Pack name
        pt = self.pack_font.render(self.pack_name, True, (255, 255, 255))
        self.screen.blit(pt, pt.get_rect(center=(cx, self.pack_y + 15)))
        # Right arrow
        ac = (255, 255, 100) if self.hovered == 'next' else (200, 200, 200)
        pygame.draw.polygon(self.screen, ac, [
            (self.next_rect.left + 5, self.next_rect.top + 5),
            (self.next_rect.right - 5, self.next_rect.centery),
            (self.next_rect.left + 5, self.next_rect.bottom - 5),
        ])
        # Description
        desc = self.small_font.render(self.pack_description, True, (180, 180, 180))
        self.screen.blit(desc, desc.get_rect(center=(cx, self.pack_y + 45)))

        # ---- Per-sound rows ----
        for sname in self.SOUND_ORDER:
            rects = self.rows[sname]
            label_text = self.SOUND_LABELS.get(sname, sname)

            # Label
            lbl = self.label_font.render(label_text, True, (220, 220, 220))
            self.screen.blit(lbl, rects['label'])

            # Preview button
            hover_preview = self.hovered == f'preview_{sname}'
            pc = (60, 130, 60) if hover_preview else (50, 90, 50)
            pygame.draw.rect(self.screen, pc, rects['preview'], border_radius=6)
            bc = (150, 255, 150) if hover_preview else (90, 140, 90)
            pygame.draw.rect(self.screen, bc, rects['preview'], 2, border_radius=6)
            ptxt = self.small_font.render("Preview", True, (255, 255, 255))
            self.screen.blit(ptxt, ptxt.get_rect(center=rects['preview'].center))

            # Upload button
            hover_upload = self.hovered == f'upload_{sname}'
            has_custom = sname in self.custom_files
            if has_custom:
                uc = (80, 80, 160) if hover_upload else (60, 60, 130)
            else:
                uc = (100, 80, 50) if hover_upload else (80, 60, 40)
            pygame.draw.rect(self.screen, uc, rects['upload'], border_radius=6)
            bcu = (200, 200, 255) if hover_upload else (130, 130, 170)
            pygame.draw.rect(self.screen, bcu, rects['upload'], 2, border_radius=6)
            upload_label = "Change Voice" if has_custom else "Add Your Voice"
            utxt = self.small_font.render(upload_label, True, (255, 255, 255))
            self.screen.blit(utxt, utxt.get_rect(center=rects['upload'].center))

            # Custom file status
            if has_custom:
                fname = self.custom_files[sname]
                # Truncate long names
                display = fname if len(fname) <= 18 else fname[:15] + "..."
                st = self.tiny_font.render(f"Custom: {display}", True, (130, 255, 130))
                self.screen.blit(st, (rects['upload'].right + 8, rects['upload'].y + 10))

        # ---- Back button ----
        back_hover = self.hovered == 'back'
        bkc = (150, 80, 80) if back_hover else (100, 60, 60)
        pygame.draw.rect(self.screen, bkc, self.back_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255) if back_hover else (150, 150, 150),
                         self.back_rect, 2, border_radius=10)
        btxt = self.label_font.render("Back", True, (255, 255, 255))
        self.screen.blit(btxt, btxt.get_rect(center=self.back_rect.center))

        # Hint
        hint = self.tiny_font.render(
            "LEFT/RIGHT: switch packs | Click 'Add Your Voice' to use your own sound files",
            True, (120, 120, 120))
        self.screen.blit(hint, hint.get_rect(center=(cx, self.sh - 20)))
