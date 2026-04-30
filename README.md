# FaceFury: Battle Platformer

A fun, meme-worthy 2D platformer where your face becomes the hero! Upload your photo and battle enemies with custom faces in this Mario-style platformer game. Now with **Android support** and **customizable voice effects**!

## Features

- **Face-based gameplay**: Use your own face as the player sprite
- **Custom enemies**: Upload any face to create unique enemies
- **Mario-style platforming**: Jump, dodge, and defeat enemies
- **Multiple levels**: Progress through increasingly difficult stages
- **Smooth physics**: Realistic gravity and collision detection
- **Screenshot feature**: Capture your meme-worthy moments
- **Procedural audio**: Generated sound effects if no files provided
- **5 Built-in Sound Packs**: Default, Funny Voices, Retro 8-bit, Meme Sounds, Epic Battle
- **Custom Voice Upload**: Manually add your own voice/sound for each game event (jump, kill, damage, etc.)
- **Android 6+ Support**: Touch controls, auto-scaling, full APK build
- **Touch Controls**: Virtual D-pad and jump button for mobile

## Requirements

### Desktop
- Python 3.10 or higher
- Webcam or image files (for face upload)
- See `requirements.txt` for package dependencies

### Android APK Build
- Python 3.10+
- Buildozer (`pip install buildozer`)
- Java JDK 17
- Android SDK & NDK (auto-downloaded by Buildozer)

## Installation

### Desktop

1. **Clone or download** the project:
```bash
git clone https://github.com/aman179102/facefury.git
cd facefury
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the game**:
```bash
python facefury/main.py
```

Or use the launcher:
```bash
python run_game.py
```

### Android APK Build

1. **Install Buildozer**:
```bash
pip install buildozer cython
```

2. **Install system dependencies** (Ubuntu/Debian):
```bash
sudo apt-get install -y openjdk-17-jdk autoconf automake libtool zip unzip
```

3. **Build the APK**:
```bash
cd facefury
buildozer android debug
```

4. The APK will be in `bin/` folder. Transfer to your Android 6+ device and install.

## How to Play

### Desktop Controls

| Key | Action |
|-----|--------|
| **LEFT / A** | Move left |
| **RIGHT / D** | Move right |
| **SPACE / UP** | Jump |
| **P** | Pause game |
| **F12** | Take screenshot |
| **R** | Restart (on game over) |
| **ESC** | Return to menu |

### Android Touch Controls

| Control | Action |
|---------|--------|
| **Left arrow** (bottom-left) | Move left |
| **Right arrow** (bottom-left) | Move right |
| **JUMP button** (bottom-right) | Jump |
| **Pause button** (top-right) | Pause/Resume |

### Gameplay Tips

1. **Upload faces in the menu** (or play with defaults)
   - Upload your photo for the player character
   - Upload friend/enemy photos for enemies

2. **Defeat enemies** by jumping on their heads

3. **Avoid side contact** - you'll take damage!

4. **Reach the yellow flag** to complete each level

5. **Don't fall in pits** - instant death!

### Face Upload Tips

- Use clear, front-facing photos
- Good lighting helps face detection
- Works with or without glasses
- The game will auto-detect and crop faces

## Voice Effects System

FaceFury has a powerful voice effects system with **5 built-in sound packs** plus the ability to **add your own custom voice files** for each game event.

### Built-in Sound Packs

| Pack | Style |
|------|-------|
| **Default** | Classic beep-boop sounds |
| **Funny Voices** | Silly cartoon sounds with sweeps and wobbles |
| **Retro 8-bit** | Classic chiptune square wave style |
| **Meme Sounds** | Internet meme inspired effects |
| **Epic Battle** | Deep dramatic tones |

Use the **"Voice Effects"** button on the main menu to:
- Switch between built-in packs using the **left/right arrows**
- **Preview** each sound (jump, kill, damage, win, etc.)
- **Upload your own voice file** for any individual sound event

### Adding Your Own Voice/Sound Files

#### In-Game Upload (Recommended)
1. Click **"Voice Effects"** from the main menu
2. For each sound event (Jump, Kill Enemy, Damage, etc.), click **"Add Your Voice"**
3. Select a `.wav`, `.mp3`, or `.ogg` file from your device
4. The sound plays immediately as a preview
5. Your custom sound overrides the pack's default for that event

#### Manual File Placement
Create a `facefury/assets/sounds/` folder and add these files:

| File | Event | Format |
|------|-------|--------|
| `jump.wav/.mp3` | Player jumps | WAV/MP3/OGG |
| `hit.wav/.mp3` | Enemy defeated | WAV/MP3/OGG |
| `damage.wav/.mp3` | Player takes damage | WAV/MP3/OGG |
| `win.wav/.mp3` | Level complete | WAV/MP3/OGG |
| `gameover.wav/.mp3` | Game over | WAV/MP3/OGG |
| `click.wav/.mp3` | Menu click | WAV/MP3/OGG |
| `initial.wav/.mp3` | Game start & level transition | WAV/MP3/OGG |
| `bgm.mp3/.wav` | Background music (low vol, loops) | MP3/WAV/OGG |

#### Recording Your Own Voice

**IMPORTANT: Record at MAXIMUM volume!**

1. Set your microphone volume to maximum
2. Speak loud and clear
3. Suggested voice lines:
   - **Game Start**: "Let's go!", "Game on!", "Face Fury!"
   - **Jump**: "Boing!", "Wheee!", "Up we go!"
   - **Kill Enemy**: "Gotcha!", "Take that!", "Boom!"
   - **Damage**: "Ouch!", "Why me?!", "Not fair!"
   - **Win**: "Victory!", "I'm the best!", "EZ game!"
   - **Game Over**: "Nooo!", "Try again!", custom meme clips
4. Save as `.wav` or `.ogg` format
5. Use the in-game uploader or copy to `facefury/assets/sounds/`

### Audio Format Requirements

- **Format**: WAV (best), OGG, or MP3
- **Sample rate**: 44100 Hz recommended
- **Channels**: Mono or Stereo
- **Duration**: Keep short (0.1-2 seconds for SFX)

## Project Structure

```
facefury/
├── main.py              # Entry point (Android + Desktop)
├── game/
│   ├── engine.py        # Main game controller
│   ├── player.py        # Player character
│   ├── enemy.py         # Enemy AI
│   ├── physics.py       # Physics & collision
│   └── level.py         # Level system
├── ui/
│   ├── menu.py          # Menu screens
│   ├── hud.py           # HUD & game over
│   ├── sound_settings.py  # Voice effects settings UI
│   └── touch_controls.py  # Android touch controls
├── face/
│   ├── detector.py      # OpenCV face detection
│   └── processor.py     # Pillow image processing
├── assets/
│   ├── audio.py         # Audio manager with sound packs
│   ├── sounds/          # Custom audio files (optional)
│   └── images/          # Image assets
└── __init__.py
buildozer.spec           # Android APK build config
```

## Android Specific Notes

- **Minimum Android version**: 6.0 (API 23)
- **Target Android version**: API 33
- **Supported architectures**: arm64-v8a, armeabi-v7a
- Touch controls appear automatically on Android
- File dialogs use Android native file picker
- The game auto-scales to your device's screen resolution
- App pauses/resumes properly when switching apps
- Default face images are bundled for immediate play

## Troubleshooting

### Face not detected
- Try a clearer photo with good lighting
- Face should be facing forward
- Use JPG or PNG format

### Game runs slow
- Close other applications
- The game runs at 60 FPS by default

### Sound not working
- Check your system volume
- The game uses pygame mixer - ensure audio drivers are working
- Procedural sounds work without any sound files

### APK Build Issues
- Make sure Java JDK 17 is installed: `java -version`
- Run `buildozer android clean` before rebuilding
- Check `buildozer.spec` for correct settings
- Logs are in `.buildozer/` directory

## Development

### Adding New Levels

Edit `game/level.py` and add to `_build_level()` method:

```python
def _build_level_3(self):
    # Your level design here
    self.platforms.append(Platform(300, 400, 100, 20))
```

### Adding New Sound Packs

Edit `assets/audio.py` and add to `SOUND_PACK_SPECS`:

```python
"my_pack": {
    "name": "My Custom Pack",
    "description": "My awesome sounds",
    "jump": {"type": "tone", "freq": 500, "dur": 0.1, "wave": "sine", "fade": True},
    # ... define all sound events
}
```

### Custom Face Processing

Modify `face/processor.py` to change:
- Face crop size
- Mask style (circular, square, etc.)
- Sprite effects

## License

MIT License - Feel free to use, modify, and share!

## Credits

- Built with **Pygame** - https://www.pygame.org/
- Face detection with **OpenCV** - https://opencv.org/
- Image processing with **Pillow** - https://python-pillow.org/
- Android packaging with **Buildozer** - https://buildozer.readthedocs.io/

---

**Have fun and share your meme screenshots!**
