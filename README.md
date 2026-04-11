# FaceFury: Battle Platformer

A fun, meme-worthy 2D platformer where your face becomes the hero! Upload your photo and battle enemies with custom faces in this Mario-style platformer game.

![Game Title](assets/images/title_placeholder.png)

## Features

- **Face-based gameplay**: Use your own face as the player sprite
- **Custom enemies**: Upload any face to create unique enemies
- **Mario-style platforming**: Jump, dodge, and defeat enemies
- **Multiple levels**: Progress through increasingly difficult stages
- **Smooth physics**: Realistic gravity and collision detection
- **Screenshot feature**: Capture your meme-worthy moments
- **Procedural audio**: Generated sound effects if no files provided

## Requirements

- Python 3.10 or higher
- Webcam or image files (for face upload)
- See `requirements.txt` for package dependencies

## Installation

1. **Clone or download** the project:
```bash
git clone <repository-url>
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

## How to Play

### Controls

| Key | Action |
|-----|--------|
| **LEFT / A** | Move left |
| **RIGHT / D** | Move right |
| **SPACE / UP** | Jump |
| **P** | Pause game |
| **F12** | Take screenshot |
| **R** | Restart (on game over) |
| **ESC** | Return to menu |

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

## Project Structure

```
facefury/
├── main.py              # Entry point
├── game/
│   ├── engine.py        # Main game controller
│   ├── player.py        # Player character
│   ├── enemy.py         # Enemy AI
│   ├── physics.py       # Physics & collision
│   └── level.py         # Level system
├── ui/
│   ├── menu.py          # Menu screens
│   └── hud.py           # HUD & game over
├── face/
│   ├── detector.py      # OpenCV face detection
│   └── processor.py     # Pillow image processing
├── assets/
│   ├── sounds/          # Audio files (optional)
│   └── images/          # Image assets
└── __init__.py
```

## Customizing Audio & Voice Effects

FaceFury supports custom sound effects and voice files! You can replace the default procedural sounds with your own recordings, memes, or funny voice clips.

### Supported Sound Files

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

### Adding Your Own Voice/Meme Sounds

#### Method 1: Record Your Own Voice

**IMPORTANT: Record at MAXIMUM volume!**

1. **Before recording:**
   - Set your **microphone volume to MAXIMUM** 🔊
   - Check phone settings → Sound → Microphone level
   - Speak **LOUD and CLEAR** - don't be shy!
   - Test recording first to check volume

2. **Record on your phone** or use any recording software

3. **Say funny things** like:
   - **Initial/Start**: "Let's go!", "Game on!", "Here we go!", "Face Fury!"
   - Jump: "Boing!", "Wheee!", "Up we go!"
   - Hit: "Gotcha!", "Take that!", "Boom!"
   - Damage: "Ouch!", "Why me?!", "Not fair!"
   - Win: "Victory!", "I'm the best!", "EZ game!"
3. **Save as `.wav` or `.ogg`** format
4. **Copy to** `facefury/assets/sounds/`

#### Method 2: Use Meme Sound Clips

1. **Download meme sounds** from sites like:
   - MyInstants.com
   - Freesound.org
   - YouTube (use converter to get audio)
2. **Rename to match** the file names above
3. **Place in** `facefury/assets/sounds/`

#### Method 3: Text-to-Speech (Free)

Use free TTS tools to generate voice:
- **Windows**: Use built-in "Narrator" or Balabolka
- **Mac**: Use "Say" command in Terminal
- **Online**: TTSMP3.com, VoiceMaker.in

Example (Mac Terminal):
```bash
say -v "Alex" "Boing!" -o jump.aiff
# Convert to wav using any converter
```

### Audio Format Requirements

- **Format**: WAV (best), OGG, or MP3
- **Sample rate**: 44100 Hz recommended
- **Channels**: Mono or Stereo
- **Duration**: Keep short (0.1-2 seconds for SFX)

### Where to Get Free Sound Effects

| Website | Type |
|---------|------|
| freesound.org | Free community sounds |
| mixkit.co | Free sound effects |
| zapsplat.com | Free with account |
| soundbible.com | Free sounds |
| myinstants.com | Meme sounds |

### Procedural Sounds (Default)

If no sound files are provided, the game **automatically generates** beep/boop sounds using code. Custom files will override these!

### Troubleshooting Audio

**Sound not playing?**
- Check file format (WAV is most reliable)
- Verify file is in correct folder: `facefury/assets/sounds/`
- Check system volume and pygame mixer

**Sound too loud/quiet?**
- Adjust volume in your audio editor
- Or modify `assets/audio.py` - change `sound_volume` value (0.0 to 1.0)

**Game crashes with custom sounds?**
- Ensure file isn't corrupted
- Try converting to standard WAV: 44.1kHz, 16-bit, mono

## Troubleshooting

### Face not detected
- Try a clearer photo with good lighting
- Face should be facing forward
- Use JPG or PNG format

### Game runs slow
- Close other applications
- Lower your screen resolution
- The game runs at 60 FPS by default

### Sound not working
- Check your system volume
- The game uses pygame mixer - ensure audio drivers are working
- Procedural sounds work without any sound files

## Development

### Adding New Levels

Edit `game/level.py` and add to `_build_level()` method:

```python
def _build_level_3(self):
    # Your level design here
    self.platforms.append(Platform(300, 400, 100, 20))
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

---

**Have fun and share your meme screenshots!**
