# 🧩 StreamForge — Developer Documentation

## 📘 Project Context
StreamForge is a native Windows virtual camera and microphone solution that creates system-level virtual devices without requiring OBS or other third-party virtual camera software. It's designed to be a standalone solution for streaming media to any application that supports webcams or microphones.

### 🎯 Project Goals
- **Native Device Creation**: Implement virtual devices at the system level
- **Zero Dependencies**: No requirement for OBS or other virtual camera software
- **Extensible Architecture**: Easy to add new features and integrations
- **Cross-Platform Ready**: Core architecture designed for future cross-platform support

## 🏗️ Architecture Overview

```
main.py
└── Application Launcher
     ├── Desktop Mode → desktop/app_desktop.py
     │                 └─ PyQt6 + QSS + QtAwesome GUI
     └── Web Mode → web/app_web.py
                         └─ Flask + HTML/CSS/JS frontend
core/
└── virtual_av.py
    ├── Video Pipeline: DirectShow Virtual Device
    └── Audio Pipeline: VB-Cable Integration
```

## 🛠️ Development Setup
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
