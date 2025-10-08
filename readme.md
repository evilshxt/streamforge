# StreamForge: Hybrid Virtual Webcam + Microphone

A Python-based multimedia routing tool that creates virtual webcam and microphone feeds on Windows. StreamForge supports both desktop and web interfaces for flexible control over your streaming setup.

## Features

- **Virtual Webcam**: Stream video files or live camera to any application
- **Virtual Microphone**: Route audio through a virtual microphone device
- **Dual Interface**: Choose between desktop (PyQt6) or web (Flask) control panels
- **File Management**: Open individual files or entire folders of media
- **Playback Controls**: Play, pause, skip, loop, and shuffle media
- **Error Handling**: Graceful handling of unsupported formats and errors

## Architecture

```
main.py
└── StreamForge Launcher
     ├── Desktop Mode → desktop/app_desktop.py (PyQt6)
     └── Web Mode → web/app_web.py (Flask)
core/
└── virtual_av.py
    ├── OpenCV + pyvirtualcam (video)
    └── sounddevice + soundfile (audio)
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/evilshxt/streamforge.git
   cd streamforge
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install VB-Audio Virtual Cable from [vb-audio.com/Cable](https://vb-audio.com/Cable/)
   - Use **CABLE Input** for StreamForge audio output
   - Select **CABLE Output** as microphone in your applications

## Usage

### Desktop Mode
```bash
python main.py --desktop
```

### Web Mode
```bash
python main.py --web
# Then open http://localhost:5000 in your browser
```

## Tech Stack

- **Core**: Python, OpenCV, pyvirtualcam, sounddevice, soundfile
- **Desktop**: PyQt6, QtAwesome
- **Web**: Flask, HTML/CSS/JavaScript
- **Audio**: VB-Audio Virtual Cable

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
