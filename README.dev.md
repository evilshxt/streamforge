# 🧩 StreamForge — Developer Documentation

## 📘 Project Context
StreamForge is a Windows-based hybrid multimedia project that functions as a virtual webcam and microphone, enabling streaming of pre-selected videos and audio into system-level devices. It's designed to be used with applications like Zoom, Meet, and OBS.

### Project Goals
- **System-Level Engineering**: Demonstrates hardware/driver-level understanding
- **Full-Stack Showcase**: Features both desktop and web interfaces
- **Modular Architecture**: Clean separation of concerns between components

## 🏗️ Architecture Overview

```
main.py
└── Launcher (PyQt6 choice dialog)
      ├── Desktop Mode → desktop/app_desktop.py
      │                 └─ PyQt6 + QSS + QtAwesome GUI
      └── Web Mode → web/app_web.py
                         └─ Flask + HTML/CSS/JS frontend
core/
└── virtual_av.py → shared backend engine
       ├─ Video: OpenCV + pyvirtualcam
       ├─ Audio: sounddevice + soundfile
       ├─ Queue & Playback Management
       └─ Thread-safe sync & validation
```

## 🛠️ Core Components

### 1. Backend Engine (`core/virtual_av.py`)
- **API Endpoints**:
  ```python
  load_files(paths: list[str])
  start_video_feed()
  start_audio_feed()
  pause()
  resume()
  next()
  previous()
  stop()
  ```
- **Thread Management**: Ensures non-blocking UI operations
- **Error Handling**: Graceful degradation on unsupported formats

### 2. Desktop Interface (`desktop/`)
- **Framework**: PyQt6 with QtAwesome icons
- **Features**:
  - Video preview panel
  - Interactive playlist
  - Styled controls with QSS
  - Status indicators

### 3. Web Interface (`web/`)
- **Backend**: Flask server
- **Frontend**: Vanilla JS with Fetch API
- **Endpoints**:
  - `/load`, `/play`, `/pause`, `/next`, `/prev`, `/status`

## 🚀 Development Setup

### Prerequisites
- Python 3.8+
- VB-Audio Virtual Cable (for audio routing)

### Installation
```bash
# Clone repository
git clone https://github.com/evilshxt/streamforge.git
cd streamforge

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Desktop Mode
python main.py --desktop

# Web Mode
python main.py --web
# Access at http://localhost:5000
```

## 🧪 Testing
- Unit tests: `pytest tests/`
- Manual testing: Verify all controls work in both interfaces
- Audio/Video sync: Test with multiple file formats

## 🛠️ Extending the Backend
1. **Add New Features**:
   - Implement new methods in `virtual_av.py`
   - Add corresponding UI controls in both interfaces
   - Update API documentation

2. **Add Support for New Formats**:
   - Update format validation in `_validate_media_file()`
   - Add appropriate file extensions to supported formats

## 📦 Dependencies

### Core
- `opencv-python` - Video processing
- `pyvirtualcam` - Virtual webcam output
- `sounddevice`/`soundfile` - Audio processing
- `numpy` - Array operations

### Desktop
- `PyQt6` - GUI framework
- `QtAwesome` - Icon pack

### Web
- `Flask` - Web server
- `gevent` - WSGI server (optional)

## 🚧 Known Issues
- Limited to Windows due to VB-Audio dependency
- Some video codecs may require additional FFmpeg installation
- High CPU usage with multiple HD streams

## 📝 Contribution Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License
MIT - See [LICENSE](LICENSE) for details

## 🔮 Future Enhancements
- OBS WebSocket integration
- Custom overlays and filters
- Real-time waveform visualization
- Cross-platform support
- One-click packaging

## 🤝 Contributors
- [evilshxt](https://github.com/evilshxt) - Project Maintainer

---
*Last Updated: October 2023*
