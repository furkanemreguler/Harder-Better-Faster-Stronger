# 🎹 Kanye Hands

A hand gesture-controlled audio sampler inspired by Daft Punk's "Harder, Better, Faster, Stronger". Control music samples using hand gestures detected by your webcam!

## ✨ Features

- 🖐️ **Hand Gesture Control**: Touch your thumb to different fingers to play audio samples
- 🎵 **8 Audio Samples**: 4 samples per hand (Harder, Better, Faster, Stronger, Work It, Make It, Do It, Makes Us)
- 🎶 **Full Song Trigger**: Touch both thumbs together to play the complete track
- 📹 **Real-time Hand Tracking**: Powered by MediaPipe
- ⚡ **Low Latency**: Fast response times for live performance
- 🎨 **Visual Feedback**: Color-coded circles show collision detection

## 🎮 Controls

| Action | Result |
|--------|--------|
| Touch finger to thumb | Play corresponding sample |
| Touch both thumbs together | Play full song |
| `+` / `=` | Increase box size |
| `-` | Decrease box size |
| `S` | Toggle skeleton view |
| `ESC` | Quit |

## 🎯 Hand Mapping

### Left Hand
- **Index** → Harder
- **Middle** → Better
- **Ring** → Faster
- **Pinky** → Stronger

### Right Hand
- **Index** → Work It
- **Middle** → Make It
- **Ring** → Do It
- **Pinky** → Makes Us

## 📋 Requirements

- Python 3.8+
- Webcam
- macOS / Linux / Windows

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/furkanemreguler/Harder-Better-Faster-Stronger.git
cd Harder-Better-Faster-Stronger
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Add your audio files**

Place your audio files in the `audio/` directory with these exact names:
```
audio/
├── harder.wav
├── better.wav
├── faster.wav
├── stronger.wav
├── work_it.wav
├── make_it.wav
├── do_it.wav
├── makes_us.wav
└── kanye_stronger.wav  (full song)
```

## 🎬 Usage
```bash
python kanye_hands.py
```

Position your hands in front of the webcam and start making music!

## 🛠️ Configuration

Edit these settings in `kanye_hands.py`:
```python
FRAME_W, FRAME_H = 640, 480       # Camera resolution
BOX_SIZE_FINGER = 20              # Finger detection box size
BOX_SIZE_THUMB = 25               # Thumb detection box size
COOLDOWN_SEC = 0.2                # Time between sample triggers
FULL_SONG_COOLDOWN = 2.0          # Cooldown for full song trigger
```

## 📁 Project Structure
```
Harder-Better-Faster-Stronger/
├── kanye_hands.py          # Main application
├── audio/                  # Audio files directory
│   ├── harder.wav
│   ├── better.wav
│   ├── faster.wav
│   ├── stronger.wav
│   ├── work_it.wav
│   ├── make_it.wav
│   ├── do_it.wav
│   ├── makes_us.wav
│   └── kanye_stronger.wav
├── README.md
├── requirements.txt
└── .gitignore
```

## 🐛 Troubleshooting

### Camera not opening
- Check if another application is using the webcam
- Try changing `CAMERA_INDEX` to `1` or `2` in the code

### Audio not playing
- Ensure audio files are in WAV format (44.1kHz recommended)
- Check system volume settings
- Verify audio file paths and names match exactly

### Slow performance
- Reduce camera resolution: `FRAME_W, FRAME_H = 320, 240`
- Lower `MODEL_COMPLEXITY` to `0`
- Close other resource-heavy applications

### Hand not detected
- Ensure good lighting conditions
- Keep hands clearly visible in frame
- Try adjusting `MIN_DET_CONF` and `MIN_TRK_CONF` values (increase for stricter detection)

## 🎥 How It Works

1. **MediaPipe Hand Tracking**: Detects 21 hand landmarks in real-time
2. **Collision Detection**: Calculates distance between thumb and finger tips
3. **Audio Playback**: Triggers corresponding audio sample when collision detected
4. **Debounce System**: Prevents multiple triggers with cooldown timer

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📝 License

MIT License - feel free to use this project however you'd like!

## 🙏 Acknowledgments

- Inspired by Daft Punk's "Harder, Better, Faster, Stronger"
- Built with [MediaPipe](https://google.github.io/mediapipe/)
- Hand tracking powered by Google's ML technology

## 👨‍💻 Author

**Furkan Emre Guler**
- GitHub: [@furkanemreguler](https://github.com/furkanemreguler)

---

Made with ❤️ and 🎵

*POV: You're Kanye in 2007* 🎤
