# 🎥 StreamForge: Standalone Virtual Webcam & Microphone

A Python-based solution that creates native virtual webcam and microphone devices on Windows without requiring OBS or other third-party virtual camera software.

## 🚀 Features

- **Native Virtual Devices**: Creates system-level virtual webcam and microphone
- **No OBS Required**: Works independently without OBS or other virtual camera software
- **Flexible Inputs**: Supports video files, screen capture, and live camera feeds
- **Audio Routing**: Seamless audio integration with VB-Cable
- **Modern UI**: Clean, responsive interface with dark/light themes
- **Cross-Platform Ready**: Designed with Windows in mind, but built for extensibility

## 🛠️ Architecture

```
main.py
└── Application Launcher
     ├── Desktop Mode → desktop/app_desktop.py (PyQt6)
     └── Web Mode → web/app_web.py (Flask)
core/
└── virtual_av.py
    ├── DirectShow Virtual Device (video)
    └── VB-Cable Integration (audio)
```

## 🚀 Getting Started

### Prerequisites

- Windows 10/11 (64-bit)
- Python 3.8 or higher
- VB-Audio Virtual Cable (for audio routing)
- Administrator privileges (for device installation)

### Installation

1. **Install VB-Audio Virtual Cable**
   - Download from [vb-audio.com/Cable](https://vb-audio.com/Cable/)
   - Run the installer and follow the prompts
   - No additional configuration needed

2. **Set up Python environment**
   ```bash
   # Clone the repository
   git clone https://github.com/evilshxt/streamforge.git
   cd streamforge
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # Desktop mode (recommended)
   python main.py --desktop
   
   # Or run as administrator for first-time setup
   # Right-click Command Prompt/PowerShell and select "Run as administrator"
   # Then run the application
   ```

## 💡 Usage

### Adding Media
1. Click "Add Media" or drag-and-drop files into the application
2. Select video and/or audio files
3. Use the playback controls to manage your stream

### Virtual Device Setup
1. In your video conferencing app (Zoom, Teams, etc.):
   - Select "StreamForge Webcam" as your camera
   - Select "CABLE Output" as your microphone

## 🛠️ Troubleshooting

### Common Issues

- **Virtual camera not showing up**
  - Run the application as Administrator
  - Ensure no other virtual camera software is running
  - Check Windows Device Manager for any driver issues

- **Audio not working**
  - Verify VB-Cable is installed correctly
  - Set "CABLE Output" as your default microphone in Windows settings
  - Check application-specific audio settings

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- VB-Audio for their excellent virtual audio cable software
- The OpenCV and PyQt communities for their amazing tools
