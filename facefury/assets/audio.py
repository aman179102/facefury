"""Audio management system for FaceFury with voice effect packs."""

import pygame
import os
import math
import io
import array
import random
from typing import Optional, Dict, List, Tuple

# Try to import pydub for MP3 support
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class SoundPack:
    """A collection of procedurally generated sound effects."""

    def __init__(self, name: str, description: str,
                 specs: Dict[str, dict]):
        self.name = name
        self.description = description
        self.specs = specs


# Built-in sound pack definitions
SOUND_PACK_SPECS: Dict[str, dict] = {
    "default": {
        "name": "Default",
        "description": "Classic beep-boop sounds",
        "jump": {"type": "tone", "freq": 440, "dur": 0.15, "wave": "sine", "fade": True},
        "hit": {"type": "noise", "dur": 0.1, "freq": 800},
        "damage": {"type": "tone", "freq": 150, "dur": 0.3, "wave": "sawtooth"},
        "win": {"type": "melody", "notes": [(523, 0.2), (659, 0.2), (784, 0.2), (1047, 0.4)]},
        "game_over": {"type": "melody", "notes": [(523, 0.3), (494, 0.3), (466, 0.4), (440, 0.6)]},
        "click": {"type": "tone", "freq": 800, "dur": 0.05, "wave": "sine", "fade": True},
        "initial": {"type": "melody", "notes": [(523, 0.15), (659, 0.15), (784, 0.15), (1047, 0.4)]},
    },
    "funny": {
        "name": "Funny Voices",
        "description": "Silly cartoon sounds",
        "jump": {"type": "sweep", "start": 200, "end": 800, "dur": 0.2},
        "hit": {"type": "sweep", "start": 1200, "end": 200, "dur": 0.15},
        "damage": {"type": "wobble", "freq": 200, "dur": 0.4, "wobble_rate": 15},
        "win": {"type": "melody", "notes": [(262, 0.1), (330, 0.1), (392, 0.1), (523, 0.1), (659, 0.1), (784, 0.3)]},
        "game_over": {"type": "sweep", "start": 800, "end": 50, "dur": 1.0},
        "click": {"type": "tone", "freq": 1200, "dur": 0.03, "wave": "square", "fade": True},
        "initial": {"type": "melody", "notes": [(392, 0.1), (523, 0.1), (659, 0.1), (784, 0.2), (1047, 0.3)]},
    },
    "retro": {
        "name": "Retro 8-bit",
        "description": "Classic chiptune style",
        "jump": {"type": "tone", "freq": 600, "dur": 0.1, "wave": "square", "fade": True},
        "hit": {"type": "tone", "freq": 1000, "dur": 0.08, "wave": "square", "fade": True},
        "damage": {"type": "melody", "notes": [(300, 0.1), (200, 0.15)], "wave": "square"},
        "win": {"type": "melody", "notes": [(523, 0.15), (659, 0.15), (784, 0.15), (1047, 0.3)], "wave": "square"},
        "game_over": {"type": "melody", "notes": [(400, 0.2), (350, 0.2), (300, 0.2), (250, 0.4)], "wave": "square"},
        "click": {"type": "tone", "freq": 900, "dur": 0.04, "wave": "square", "fade": True},
        "initial": {"type": "melody", "notes": [(523, 0.1), (784, 0.1), (1047, 0.1), (1319, 0.3)], "wave": "square"},
    },
    "meme": {
        "name": "Meme Sounds",
        "description": "Internet meme inspired",
        "jump": {"type": "sweep", "start": 150, "end": 1500, "dur": 0.25},
        "hit": {"type": "noise_burst", "dur": 0.12, "freq": 600},
        "damage": {"type": "wobble", "freq": 100, "dur": 0.5, "wobble_rate": 8},
        "win": {"type": "melody", "notes": [(880, 0.15), (1109, 0.15), (1319, 0.15), (1760, 0.4)]},
        "game_over": {"type": "melody", "notes": [(440, 0.3), (349, 0.3), (294, 0.4), (220, 0.6)]},
        "click": {"type": "sweep", "start": 1500, "end": 800, "dur": 0.04},
        "initial": {"type": "melody", "notes": [(440, 0.1), (554, 0.1), (659, 0.1), (880, 0.1), (1109, 0.1), (1319, 0.3)]},
    },
    "epic": {
        "name": "Epic Battle",
        "description": "Deep dramatic sounds",
        "jump": {"type": "sweep", "start": 100, "end": 400, "dur": 0.18},
        "hit": {"type": "noise_burst", "dur": 0.15, "freq": 300},
        "damage": {"type": "tone", "freq": 80, "dur": 0.4, "wave": "sawtooth"},
        "win": {"type": "melody", "notes": [(262, 0.2), (330, 0.2), (392, 0.3), (523, 0.5)]},
        "game_over": {"type": "melody", "notes": [(262, 0.4), (247, 0.4), (220, 0.5), (196, 0.7)]},
        "click": {"type": "tone", "freq": 500, "dur": 0.06, "wave": "sine", "fade": True},
        "initial": {"type": "melody", "notes": [(196, 0.2), (262, 0.2), (330, 0.2), (392, 0.2), (523, 0.4)]},
    },
}

SOUND_NAMES = ['jump', 'hit', 'damage', 'win', 'game_over', 'click', 'initial']


class AudioManager:
    """Manages game audio with switchable voice effect packs."""

    def __init__(self, sounds_dir: str = None):
        if sounds_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sounds_dir = os.path.join(os.path.dirname(current_dir), 'assets', 'sounds')

        self.sounds_dir = sounds_dir
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_loaded = False
        self.music_playing = False
        self.music_path: Optional[str] = None

        # Volume settings
        self.sound_volume = 1.0
        self.music_volume = 0.15
        self.volume_boost = 2.0

        # Voice effect pack system
        self.current_pack_id = "default"
        self.available_packs = list(SOUND_PACK_SPECS.keys())
        self.custom_sounds: Dict[str, pygame.mixer.Sound] = {}

        # Initialize mixer
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self._load_sounds()

    def _load_sounds(self):
        """Load sound files from disk, then fill gaps with current pack."""
        self.custom_sounds.clear()
        self._load_file_sounds()
        self._apply_sound_pack(self.current_pack_id)

    def _load_file_sounds(self):
        """Load sound files from the sounds directory."""
        sound_configs = [
            ('jump', ['jump.wav', 'jump.mp3', 'jump.ogg']),
            ('hit', ['hit.wav', 'hit.mp3', 'hit.ogg']),
            ('damage', ['damage.wav', 'damage.mp3', 'damage.ogg']),
            ('win', ['win.wav', 'win.mp3', 'win.ogg']),
            ('game_over', ['gameover.wav', 'gameover.mp3', 'gameover.ogg']),
            ('click', ['click.wav', 'click.mp3', 'click.ogg']),
            ('initial', ['initial.wav', 'initial.mp3', 'initial.ogg']),
            ('bgm', ['bgm.mp3', 'bgm.wav', 'bgm.ogg']),
        ]

        for sound_name, filenames in sound_configs:
            for filename in filenames:
                filepath = os.path.join(self.sounds_dir, filename)
                if not os.path.exists(filepath):
                    continue
                if sound_name == 'bgm':
                    self.music_loaded = True
                    self.music_path = filepath
                    break
                try:
                    sound = pygame.mixer.Sound(filepath)
                    boosted = min(1.0, self.sound_volume * self.volume_boost)
                    sound.set_volume(boosted)
                    self.custom_sounds[sound_name] = sound
                    self.sounds[sound_name] = sound
                    break
                except pygame.error:
                    if filename.endswith('.mp3') and PYDUB_AVAILABLE:
                        converted = self._convert_mp3_to_wav(filepath)
                        if converted:
                            boosted = min(1.0, self.sound_volume * self.volume_boost)
                            converted.set_volume(boosted)
                            self.custom_sounds[sound_name] = converted
                            self.sounds[sound_name] = converted
                            break

    def _apply_sound_pack(self, pack_id: str):
        """Generate procedural sounds from a pack, skipping custom files."""
        if pack_id not in SOUND_PACK_SPECS:
            pack_id = "default"
        self.current_pack_id = pack_id
        spec = SOUND_PACK_SPECS[pack_id]

        for sname in SOUND_NAMES:
            if sname in self.custom_sounds:
                self.sounds[sname] = self.custom_sounds[sname]
                continue
            if sname not in spec:
                continue
            s = spec[sname]
            sound = self._generate_from_spec(s)
            if sound:
                sound.set_volume(self.sound_volume)
                self.sounds[sname] = sound

    def _generate_from_spec(self, spec: dict) -> Optional[pygame.mixer.Sound]:
        """Generate a sound from a specification dictionary."""
        stype = spec.get("type", "tone")
        if stype == "tone":
            return self._generate_tone(
                spec.get("freq", 440),
                spec.get("dur", 0.15),
                spec.get("wave", "sine"),
                spec.get("fade", False),
            )
        elif stype == "noise":
            return self._generate_noise(spec.get("dur", 0.1), spec.get("freq", 440))
        elif stype == "noise_burst":
            return self._generate_noise_burst(spec.get("dur", 0.12), spec.get("freq", 600))
        elif stype == "melody":
            return self._generate_melody(
                spec.get("notes", []),
                spec.get("wave", "sine"),
            )
        elif stype == "sweep":
            return self._generate_sweep(
                spec.get("start", 200),
                spec.get("end", 800),
                spec.get("dur", 0.2),
            )
        elif stype == "wobble":
            return self._generate_wobble(
                spec.get("freq", 200),
                spec.get("dur", 0.4),
                spec.get("wobble_rate", 10),
            )
        return None

    # --- Sound pack switching API ---

    def get_pack_names(self) -> List[Tuple[str, str, str]]:
        """Return list of (pack_id, name, description) tuples."""
        result = []
        for pid in self.available_packs:
            spec = SOUND_PACK_SPECS[pid]
            result.append((pid, spec["name"], spec["description"]))
        return result

    def set_sound_pack(self, pack_id: str):
        """Switch to a different sound effect pack."""
        if pack_id in SOUND_PACK_SPECS:
            self._apply_sound_pack(pack_id)

    def next_pack(self) -> str:
        """Cycle to the next sound pack and return its name."""
        idx = self.available_packs.index(self.current_pack_id)
        idx = (idx + 1) % len(self.available_packs)
        self.set_sound_pack(self.available_packs[idx])
        return SOUND_PACK_SPECS[self.current_pack_id]["name"]

    def prev_pack(self) -> str:
        """Cycle to the previous sound pack and return its name."""
        idx = self.available_packs.index(self.current_pack_id)
        idx = (idx - 1) % len(self.available_packs)
        self.set_sound_pack(self.available_packs[idx])
        return SOUND_PACK_SPECS[self.current_pack_id]["name"]

    def get_current_pack_name(self) -> str:
        return SOUND_PACK_SPECS[self.current_pack_id]["name"]

    def preview_sound(self, sound_name: str):
        """Play a specific sound for preview purposes."""
        self.play_sound(sound_name)

    def load_custom_sound(self, sound_name: str, filepath: str) -> bool:
        """Load a user-chosen sound file for a specific event.

        The custom sound overrides both the active pack and any file
        previously loaded from the sounds directory for that event.

        Returns True on success.
        """
        try:
            sound = pygame.mixer.Sound(filepath)
        except pygame.error:
            # Try MP3 conversion as fallback
            if filepath.lower().endswith('.mp3'):
                sound = self._convert_mp3_to_wav(filepath)
            else:
                sound = None
        if sound is None:
            return False
        boosted = min(1.0, self.sound_volume * self.volume_boost)
        sound.set_volume(boosted)
        self.custom_sounds[sound_name] = sound
        self.sounds[sound_name] = sound
        return True

    def remove_custom_sound(self, sound_name: str):
        """Remove a user-uploaded custom sound, reverting to pack default."""
        self.custom_sounds.pop(sound_name, None)
        self._apply_sound_pack(self.current_pack_id)

    # --- Procedural sound generators ---

    def _generate_tone(self, frequency: float, duration: float,
                       wave_type: str = 'sine',
                       fade_out: bool = False) -> pygame.mixer.Sound:
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        samples = array.array('h')

        for i in range(num_samples):
            t = i / sample_rate
            if wave_type == 'square':
                value = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0
            elif wave_type == 'sawtooth':
                value = 2 * (t * frequency - math.floor(t * frequency + 0.5))
            else:
                value = math.sin(2 * math.pi * frequency * t)

            if fade_out and i > num_samples * 0.7:
                value *= (num_samples - i) / (num_samples * 0.3)

            samples.append(int(value * 32767 * 0.5))

        sound = pygame.mixer.Sound(buffer=samples)
        sound.set_volume(self.sound_volume)
        return sound

    def _generate_noise(self, duration: float, frequency: float = 440) -> pygame.mixer.Sound:
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        samples = array.array('h')

        for i in range(num_samples):
            noise = random.uniform(-1, 1)
            value = noise * math.exp(-i / (sample_rate * 0.05))
            samples.append(int(value * 32767 * 0.5))

        sound = pygame.mixer.Sound(buffer=samples)
        sound.set_volume(self.sound_volume)
        return sound

    def _generate_noise_burst(self, duration: float, frequency: float = 600) -> pygame.mixer.Sound:
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        samples = array.array('h')

        for i in range(num_samples):
            t = i / sample_rate
            noise = random.uniform(-1, 1)
            tone = math.sin(2 * math.pi * frequency * t)
            value = (noise * 0.3 + tone * 0.7) * math.exp(-i / (sample_rate * 0.08))
            samples.append(int(value * 32767 * 0.5))

        sound = pygame.mixer.Sound(buffer=samples)
        sound.set_volume(self.sound_volume)
        return sound

    def _generate_melody(self, notes: list,
                         wave_type: str = 'sine') -> pygame.mixer.Sound:
        sample_rate = 44100
        all_samples = array.array('h')

        for frequency, duration in notes:
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                if wave_type == 'square':
                    value = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0
                else:
                    value = math.sin(2 * math.pi * frequency * t)
                if i > num_samples * 0.8:
                    value *= (num_samples - i) / (num_samples * 0.2)
                all_samples.append(int(value * 32767 * 0.4))

        sound = pygame.mixer.Sound(buffer=all_samples)
        sound.set_volume(self.sound_volume)
        return sound

    def _generate_sweep(self, start_freq: float, end_freq: float,
                        duration: float) -> pygame.mixer.Sound:
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        samples = array.array('h')

        for i in range(num_samples):
            t = i / sample_rate
            progress = i / num_samples
            freq = start_freq + (end_freq - start_freq) * progress
            value = math.sin(2 * math.pi * freq * t)
            # Fade out last 20%
            if progress > 0.8:
                value *= (1.0 - progress) / 0.2
            samples.append(int(value * 32767 * 0.5))

        sound = pygame.mixer.Sound(buffer=samples)
        sound.set_volume(self.sound_volume)
        return sound

    def _generate_wobble(self, frequency: float, duration: float,
                         wobble_rate: float = 10) -> pygame.mixer.Sound:
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        samples = array.array('h')

        for i in range(num_samples):
            t = i / sample_rate
            wobble = math.sin(2 * math.pi * wobble_rate * t) * frequency * 0.5
            value = math.sin(2 * math.pi * (frequency + wobble) * t)
            value *= math.exp(-i / (sample_rate * duration * 0.7))
            samples.append(int(value * 32767 * 0.5))

        sound = pygame.mixer.Sound(buffer=samples)
        sound.set_volume(self.sound_volume)
        return sound

    def _convert_mp3_to_wav(self, mp3_path: str) -> Optional[pygame.mixer.Sound]:
        if not PYDUB_AVAILABLE:
            return None
        try:
            audio_seg = AudioSegment.from_mp3(mp3_path)
            audio_seg = audio_seg.set_frame_rate(44100).set_sample_width(2).set_channels(2)
            wav_buffer = io.BytesIO()
            audio_seg.export(wav_buffer, format='wav')
            wav_buffer.seek(0)
            return pygame.mixer.Sound(file=wav_buffer)
        except Exception:
            return None

    # --- Playback API ---

    def play_sound(self, sound_name: str):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def play_music(self, music_file: Optional[str] = None):
        filepath = music_file if music_file else self.music_path
        if filepath and os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                self.music_playing = True
                self.music_loaded = True
            except pygame.error:
                pass

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False

    def pause_music(self):
        pygame.mixer.music.pause()

    def unpause_music(self):
        pygame.mixer.music.unpause()

    def set_sound_volume(self, volume: float):
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)

    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.music_volume)
