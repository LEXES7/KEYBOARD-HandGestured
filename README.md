# Virtual Keyboard with Hand Gestures

A computer vision-based virtual keyboard that allows typing using hand gestures. Built with OpenCV, MediaPipe, and Python.

## Features

- 🖐️ **Hand Gesture Recognition** - Uses MediaPipe for accurate hand tracking
- ⌨️ **Virtual QWERTY Keyboard** - Full keyboard layout with special keys
- 👆 **Pinch to Type** - Pinch thumb and index finger to type letters
- 📱 **Responsive Design** - Adapts to different screen sizes
- 🎯 **Hover Detection** - Visual feedback when hovering over keys
- ⏱️ **Progress Indicators** - Shows typing progress with visual cues
- 🔧 **Optimized Performance** - Smooth real-time operation

## Demo

![Virtual Keyboard Demo](demo.gif)

## Installation

### Prerequisites

- Python 3.8 - 3.12 (MediaPipe compatibility)
- Webcam or external camera
- macOS/Windows/Linux

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/LEXES7/KEYBOARD-HandGestured.git
cd KEYBOARD-HandGestured
```

2. **Create virtual environment**
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

1. **Run the application**
```bash
cd src
python main.py
```

2. **How to use:**
   - Position your hand in front of the camera
   - Hover your index finger over a key (you'll see it highlight)
   - Pinch your thumb and index finger together to type
   - Use special keys: SPACE, BACKSPACE, CLEAR
   - Press 'q' to quit, 'f' for fullscreen, 'w' for windowed mode

## Controls

| Action | Description |
|--------|-------------|
| Hover | Move index finger over keys |
| Pinch | Touch thumb and index finger to type |
| Q key | Quit application |
| F key | Toggle fullscreen |
| W key | Windowed mode |
| C key | Clear text (keyboard shortcut) |

## Project Structure

```
KEYBOARD-HandGestured/
├── src/
│   ├── main.py              # Main application
│   ├── hand_detector.py     # Hand detection logic
│   ├── virtual_keyboard.py  # Keyboard interface
│   └── test_camera.py       # Camera testing utility
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## Dependencies

- `opencv-python` - Computer vision library
- `mediapipe` - Hand tracking and gesture recognition
- `numpy` - Numerical computations

## Troubleshooting

### Camera Issues
- Make sure no other applications are using the camera
- Try different camera indices (0, 1, 2) in the code
- Check camera permissions in system settings

### Performance Issues
- Ensure good lighting for better hand detection
- Close other applications to free up resources
- Lower the FPS if needed in main.py

### Hand Detection Issues
- Keep hand clearly visible in frame
- Ensure good contrast between hand and background
- Maintain steady hand position for better tracking

## Configuration

You can modify these settings in the code:

```python
# In virtual_keyboard.py
self.hover_duration = 0.8    # Time to hover before typing
self.press_cooldown = 0.3    # Delay between key presses
self.key_size = 120          # Size of keyboard keys

# In hand_detector.py
detection_confidence=0.8     # Hand detection sensitivity
tracking_confidence=0.8      # Hand tracking accuracy
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Word prediction and autocomplete
- [ ] Multiple language support
- [ ] Voice feedback
- [ ] Gesture shortcuts
- [ ] Custom keyboard layouts
- [ ] Mobile app version

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking
- [OpenCV](https://opencv.org/) for computer vision
- Inspired by accessibility technology and gesture-based interfaces

## Author

**Sachintha Bhashitha** - [LEXES7](https://github.com/LEXES7)

---

⭐ Star this repository if you found it helpful!