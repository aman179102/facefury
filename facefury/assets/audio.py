"""Audio management system for FaceFury."""

import pygame
import os
import math
import io
from typing import Optional, Dict

# Try to import pydub for MP3 support
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class AudioManager:
    """Manages game audio - sounds and music."""
    
    def __init__(self, sounds_dir: str = None):
        """
        Initialize audio manager.
        
        Args:
            sounds_dir: Directory containing sound files
        """
        if sounds_dir is None:
            # Default to package sounds directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sounds_dir = os.path.join(os.path.dirname(current_dir), 'assets', 'sounds')
        
        self.sounds_dir = sounds_dir
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_loaded = False
        self.music_playing = False
        
        # Volume settings
        self.sound_volume = 1.0  # MAX volume for sound effects (100%)
        self.music_volume = 0.15  # BGM very low (15%)
        self.volume_boost = 2.0  # Boost recorded sounds by 2x (200%)
        
        # Initialize mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Load or generate sounds
        self._load_sounds()
    
    def _load_sounds(self):
        """Load sound files or generate placeholder sounds."""
        # Try to load sounds from files (supports both WAV and MP3)
        sound_configs = [
            ('jump', ['jump.wav', 'jump.mp3']),
            ('hit', ['hit.wav', 'hit.mp3']),
            ('damage', ['damage.wav', 'damage.mp3']),
            ('win', ['win.wav', 'win.mp3']),
            ('game_over', ['gameover.wav', 'gameover.mp3']),
            ('click', ['click.wav', 'click.mp3']),
            ('initial', ['initial.wav', 'initial.mp3']),
            ('bgm', ['bgm.mp3', 'bgm.wav', 'bgm.ogg'])
        ]
        
        for sound_name, filenames in sound_configs:
            for filename in filenames:
                filepath = os.path.join(self.sounds_dir, filename)
                if os.path.exists(filepath):
                    if sound_name == 'bgm':
                        # Music is handled separately
                        self.music_loaded = True
                        self.music_path = filepath
                        print(f"[Audio] Found BGM: {filename}")
                    else:
                        try:
                            print(f"[Audio] Loading sound: {filename}")
                            sound = pygame.mixer.Sound(filepath)
                            # Boost volume for quiet recordings
                            boosted_volume = min(1.0, self.sound_volume * self.volume_boost)
                            sound.set_volume(boosted_volume)
                            self.sounds[sound_name] = sound
                            print(f"[Audio] Loaded: {sound_name} from {filename} (vol: {boosted_volume:.0%})")
                            break  # Stop trying other formats once loaded
                        except pygame.error as e:
                            print(f"[Audio] Failed to load {filename}: {e}")
                            # Try to convert MP3 to WAV if pydub is available
                            if filename.endswith('.mp3') and PYDUB_AVAILABLE:
                                try:
                                    print(f"[Audio] Converting {filename} to WAV...")
                                    sound = self._convert_mp3_to_wav(filepath)
                                    if sound:
                                        # Apply volume boost to converted sounds too
                                        boosted_volume = min(1.0, self.sound_volume * self.volume_boost)
                                        sound.set_volume(boosted_volume)
                                        self.sounds[sound_name] = sound
                                        print(f"[Audio] Loaded converted: {sound_name} (vol: {boosted_volume:.0%})")
                                        break
                                except Exception as conv_e:
                                    print(f"[Audio] Conversion failed: {conv_e}")
                            continue
        
        # Generate procedural sounds for missing ones
        self._generate_missing_sounds()
    
    def _generate_missing_sounds(self):
        """Generate procedural sound effects for any missing sounds."""
        if 'jump' not in self.sounds:
            self.sounds['jump'] = self._generate_tone(440, 0.15, fade_out=True)
        
        if 'hit' not in self.sounds:
            self.sounds['hit'] = self._generate_noise(0.1, frequency=800)
        
        if 'damage' not in self.sounds:
            self.sounds['damage'] = self._generate_tone(150, 0.3, 
                                                        wave_type='sawtooth')
        
        if 'win' not in self.sounds:
            self.sounds['win'] = self._generate_melody([(523, 0.2), (659, 0.2), 
                                                       (784, 0.2), (1047, 0.4)])
        
        if 'game_over' not in self.sounds:
            self.sounds['game_over'] = self._generate_melody([(523, 0.3), (494, 0.3), 
                                                            (466, 0.4), (440, 0.6)])
        
        if 'click' not in self.sounds:
            self.sounds['click'] = self._generate_tone(800, 0.05, fade_out=True)
        
        if 'initial' not in self.sounds:
            # Game start sound - fanfare style
            self.sounds['initial'] = self._generate_melody([(523, 0.15), (659, 0.15), 
                                                         (784, 0.15), (1047, 0.4)])
    
    def _generate_tone(self, frequency: float, duration: float,
                       wave_type: str = 'sine',
                       fade_out: bool = False) -> pygame.mixer.Sound:
        """
        Generate a simple tone.
        
        Args:
            frequency: Tone frequency in Hz
            duration: Duration in seconds
            wave_type: 'sine', 'square', or 'sawtooth'
            fade_out: Whether to fade out the tone
            
        Returns:
            Generated sound
        """
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        
        # Generate wave
        import array
        samples = array.array('h')  # Signed short
        
        for i in range(num_samples):
            t = i / sample_rate
            
            if wave_type == 'sine':
                value = math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'square':
                value = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0
            elif wave_type == 'sawtooth':
                value = 2 * (t * frequency - math.floor(t * frequency + 0.5))
            else:
                value = math.sin(2 * math.pi * frequency * t)
            
            # Apply fade out
            if fade_out and i > num_samples * 0.7:
                value *= (num_samples - i) / (num_samples * 0.3)
            
            # Scale to 16-bit range
            samples.append(int(value * 32767 * 0.5))
        
        # Create sound from samples
        sound = pygame.mixer.Sound(buffer=samples)
        sound.set_volume(self.sound_volume)
        return sound
    
    def _generate_noise(self, duration: float, frequency: float = 440) -> pygame.mixer.Sound:
        """Generate noise burst sound."""
        import random
        import array
        
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        
        samples = array.array('h')
        
        for i in range(num_samples):
            # Low pass filtered noise
            noise = random.uniform(-1, 1)
            # Simple filter
            value = noise * math.exp(-i / (sample_rate * 0.05))
            samples.append(int(value * 32767 * 0.5))
        
        sound = pygame.mixer.Sound(buffer=samples)
        sound.set_volume(self.sound_volume)
        return sound
    
    def _generate_melody(self, notes: list) -> pygame.mixer.Sound:
        """Generate a melody from list of (frequency, duration) tuples."""
        import array
        
        sample_rate = 44100
        all_samples = array.array('h')
        
        for frequency, duration in notes:
            num_samples = int(sample_rate * duration)
            
            for i in range(num_samples):
                t = i / sample_rate
                value = math.sin(2 * math.pi * frequency * t)
                # Fade out at end of each note
                if i > num_samples * 0.8:
                    value *= (num_samples - i) / (num_samples * 0.2)
                all_samples.append(int(value * 32767 * 0.4))
        
        sound = pygame.mixer.Sound(buffer=all_samples)
        sound.set_volume(self.sound_volume)
        return sound
    
    def _convert_mp3_to_wav(self, mp3_path: str) -> Optional[pygame.mixer.Sound]:
        """
        Convert MP3 file to WAV format for pygame compatibility.
        
        Args:
            mp3_path: Path to MP3 file
            
        Returns:
            pygame.mixer.Sound object or None
        """
        if not PYDUB_AVAILABLE:
            return None
        
        try:
            # Load MP3 and export to WAV in memory
            audio = AudioSegment.from_mp3(mp3_path)
            
            # Ensure correct format for pygame (44.1kHz, 16-bit, stereo)
            audio = audio.set_frame_rate(44100).set_sample_width(2).set_channels(2)
            
            # Export to bytes buffer
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format='wav')
            wav_buffer.seek(0)
            
            # Load into pygame
            return pygame.mixer.Sound(file=wav_buffer)
        except Exception as e:
            print(f"[Audio] MP3 conversion error: {e}")
            return None
    
    def play_sound(self, sound_name: str):
        """
        Play a sound effect.
        
        Args:
            sound_name: Name of the sound to play
        """
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_music(self, music_file: Optional[str] = None):
        """
        Play background music - always loops continuously.
        
        Args:
            music_file: Path to music file, or None to use loaded music
        """
        # Use provided file or pre-loaded music path
        filepath = music_file if music_file else getattr(self, 'music_path', None)
        
        if filepath and os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.music_volume)  # Low volume (15%)
                pygame.mixer.music.play(-1)  # Loop forever (-1 = infinite)
                self.music_playing = True
                self.music_loaded = True
                print(f"BGM playing: {os.path.basename(filepath)} (vol: {self.music_volume:.0%})")
            except pygame.error as e:
                print(f"BGM error: {e}")
        else:
            # No music file available - could implement procedural music here
            pass
    
    def stop_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()
        self.music_playing = False
    
    def pause_music(self):
        """Pause background music."""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Unpause background music."""
        pygame.mixer.music.unpause()
    
    def set_sound_volume(self, volume: float):
        """Set sound effect volume (0.0 to 1.0)."""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
