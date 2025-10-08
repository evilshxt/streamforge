#!/usr/bin/env python3
"""
StreamForge - Main Entry Point

This module serves as the launcher for the StreamForge application,
providing both desktop and web interfaces for virtual webcam and microphone streaming.
"""
import sys
import argparse
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt

# Add project root to path
sys.path.append(str(Path(__file__).parent.absolute()))

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='StreamForge - Virtual Webcam and Microphone')
    parser.add_argument('--desktop', action='store_true', help='Launch desktop interface')
    parser.add_argument('--web', action='store_true', help='Launch web interface')
    parser.add_argument('--port', type=int, default=5000, help='Port for web interface (default: 5000)')
    return parser.parse_args()

def launch_desktop():
    """Launch the desktop PyQt6 interface."""
    from PyQt6.QtWidgets import QApplication
    from desktop.app_desktop import StreamForgeDesktop
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform look
    
    # Create and show main window
    window = StreamForgeDesktop()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

def launch_web(port: int):
    """Launch the web interface."""
    from web.app_web import create_app
    
    app = create_app()
    app.run(debug=True, port=port, use_reloader=False)

def main():
    """Main entry point for StreamForge."""
    args = parse_args()
    
    if args.desktop:
        launch_desktop()
    elif args.web:
        launch_web(args.port)
    else:
        # Default to desktop if no mode specified
        launch_desktop()

if __name__ == "__main__":
    main()
