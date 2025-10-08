"""
StreamForge Desktop Interface

This module provides the PyQt6-based desktop interface for StreamForge.
It includes a modern, dark-themed UI with video preview and playback controls.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QListWidget, QListWidgetItem,
    QStatusBar, QSlider, QStyle, QMessageBox, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread, QObject, QProcess
from PyQt6.QtGui import QPixmap, QImage, QIcon, QFont, QColor, QPalette
import qtawesome as qta

from core.virtual_av import VirtualAVEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom QListWidget for drag and drop support
class MediaListWidget(QListWidget):
    """Custom QListWidget that supports drag and drop for media files."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setIconSize(QSize(32, 32))
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = [url.toLocalFile() for url in event.mimeData().urls()]
            self.parent().add_media_files(urls)
            event.acceptProposedAction()
        else:
            event.ignore()

# Main application window
class StreamForgeDesktop(QMainWindow):
    """Main application window for the StreamForge desktop interface."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StreamForge - Desktop")
        self.setMinimumSize(1200, 800)
        
        # Check for required dependencies
        self.check_dependencies()
        
        # Initialize engine
        self.engine = VirtualAVEngine()
        self.engine.register_status_callback(self.update_status)
        self.engine.register_error_callback(self.show_error)
        
        # Theme settings
        self.dark_mode = True
        self.current_theme = 'dark'  # 'dark' or 'light'
        
        # Setup UI
        self.setup_ui()
        self.setup_styles()
        
        # Check audio device
        self.check_audio_device()
        
        # Update timer for video preview
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self.update_preview)
        self.preview_timer.start(30)  # ~33 FPS
        
        # Status update timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_ui_state)
        self.status_timer.start(1000)  # Update every second
        
        logger.info("StreamForge Desktop initialized")
    
    def check_dependencies(self):
        """Check for required dependencies and virtual devices."""
        missing = []
        
        # Check for VB-Audio Virtual Cable
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            cable_found = any('CABLE Input' in str(device.get('name', '')) for device in devices)
            if not cable_found:
                missing.append("VB-Audio Virtual Cable is not installed or not set as default")
        except Exception as e:
            missing.append(f"Error checking audio devices: {str(e)}")
        
        # Check for pyvirtualcam
        try:
            import pyvirtualcam
        except ImportError:
            missing.append("pyvirtualcam is not installed. Virtual webcam will not work.")
        
        if missing:
            msg = "The following issues were found:\n\n" + "\n".join(f"• {m}" for m in missing)
            msg += "\n\nPlease install the required dependencies and restart the application."
            QMessageBox.critical(self, "Missing Dependencies", msg)
    
    def check_audio_device(self):
        """Verify audio device is available."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            cable_found = any('CABLE Input' in str(device.get('name', '')) for device in devices)
            
            if not cable_found:
                self.show_error(
                    "VB-Audio Virtual Cable not found. "
                    "Please install it from https://vb-audio.com/Cable/"
                )
        except Exception as e:
            self.show_error(f"Error checking audio devices: {str(e)}")
    
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.theme_action.setText(f"{'☀️' if self.current_theme == 'dark' else '🌙'} Toggle Theme")
        self.setup_styles()
    
    def setup_ui(self):
        """Set up the main UI components."""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create main horizontal splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create vertical splitters for webcam and audio sections
        webcam_splitter = QSplitter(Qt.Orientation.Vertical)
        audio_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Set stretch factors
        main_splitter.addWidget(webcam_splitter)
        main_splitter.addWidget(audio_splitter)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)
        
        # Add main splitter to layout
        main_layout.addWidget(main_splitter, 1)  # 1 is stretch factor
        
        # Left panel - Media list and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Add media button
        btn_add = QPushButton("Add Media")
        btn_add.setIcon(qta.icon('fa5s.plus', color='white'))
        btn_add.clicked.connect(self.browse_media)
        
        # Media list
        self.media_list = MediaListWidget()
        self.media_list.itemDoubleClicked.connect(self.play_selected_media)
        
        # Playback controls
        control_layout = QHBoxLayout()
        
        self.btn_play = QPushButton()
        self.btn_play.setIcon(qta.icon('fa5s.play', color='white'))
        self.btn_play.clicked.connect(self.toggle_playback)
        
        self.btn_stop = QPushButton()
        self.btn_stop.setIcon(qta.icon('fa5s.stop', color='white'))
        self.btn_stop.clicked.connect(self.stop_playback)
        
        self.btn_prev = QPushButton()
        self.btn_prev.setIcon(qta.icon('fa5s.step-backward', color='white'))
        self.btn_prev.clicked.connect(self.previous_media)
        
        self.btn_next = QPushButton()
        self.btn_next.setIcon(qta.icon('fa5s.step-forward', color='white'))
        self.btn_next.clicked.connect(self.next_media)
        
        self.btn_loop = QPushButton()
        self.btn_loop.setIcon(qta.icon('fa5s.redo', color='white'))
        self.btn_loop.setCheckable(True)
        self.btn_loop.toggled.connect(self.toggle_loop)
        
        control_layout.addWidget(self.btn_prev)
        control_layout.addWidget(self.btn_play)
        control_layout.addWidget(self.btn_stop)
        control_layout.addWidget(self.btn_next)
        control_layout.addWidget(self.btn_loop)
        
        # Add widgets to left layout
        left_layout.addWidget(btn_add)
        left_layout.addWidget(QLabel("Media Queue:"))
        left_layout.addWidget(self.media_list)
        left_layout.addLayout(control_layout)
        
        # Right panel - Video preview and status
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Video preview
        self.video_preview = QLabel()
        self.video_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_preview.setStyleSheet("background-color: #1e1e1e; border-radius: 8px;")
        self.video_preview.setMinimumSize(640, 360)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Add widgets to right layout
        right_layout.addWidget(self.video_preview)
        
        # Add panels to main_splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        
        # Add main_splitter to main layout
        main_layout.addWidget(main_splitter)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Update UI state
        self.update_ui_state()
        
        # Show initial status
        self.update_status("Ready. Add media files to begin.")
    
    def create_menu_bar(self):
        """Create the menu bar with actions."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        add_media_action = file_menu.addAction("📁 Add Media")
        add_media_action.setShortcut("Ctrl+O")
        add_media_action.triggered.connect(self.browse_media)
        
        clear_queue_action = file_menu.addAction("🗑️ Clear Queue")
        clear_queue_action.triggered.connect(self.clear_queue)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("🚪 Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        self.theme_action = view_menu.addAction("🌙 Toggle Theme")
        self.theme_action.setShortcut("Ctrl+T")
        self.theme_action.triggered.connect(self.toggle_theme)
        
        # Help menu
        help_menu = menubar.addMenu("ℹ️ Help")
        
        about_action = help_menu.addAction("ℹ️ About")
        about_action.triggered.connect(self.show_about)
    
    def load_stylesheet(self, theme_name):
        """Load and return the stylesheet for the given theme."""
        try:
            styles_dir = os.path.join(os.path.dirname(__file__), 'styles')
            stylesheet_path = os.path.join(styles_dir, f"{theme_name}.qss")
            
            with open(stylesheet_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading {theme_name} stylesheet: {e}")
            return ""
    
    def setup_styles(self):
        """Set up the application stylesheet."""
        stylesheet = self.load_stylesheet(self.current_theme)
        self.setStyleSheet(stylesheet)
    
    # ===== Media Management =====
    
    def browse_media(self):
        """Open a file dialog to select media files."""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Media Files (*.mp4 *.avi *.mov *.mkv *.webm *.mp3 *.wav *.flac *.ogg *.aac)")
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            self.add_media_files(files)
    
    def add_media_files(self, file_paths):
        """Add media files to the queue."""
        if not file_paths:
            return
        
        loaded, errors = self.engine.load_media(file_paths)
        
        # Update media list
        self.media_list.clear()
        for file_path in loaded:
            item = QListWidgetItem(file_path)
            
            # Set appropriate icon based on file type
            if file_path.lower().endswith(tuple(self.engine.VIDEO_EXTS)):
                item.setIcon(qta.icon('fa5s.film', color='#ff6b6b'))
            else:
                item.setIcon(qta.icon('fa5s.music', color='#6b9eff'))
            
            self.media_list.addItem(item)
        
        # Show errors if any
        if errors:
            QMessageBox.warning(self, "Error Loading Files", "\n".join(errors))
        
        self.update_ui_state()
    
    def clear_queue(self):
        """Clear the media queue."""
        self.engine.stop_streaming()
        self.media_list.clear()
        self.engine.video_queue.clear()
        self.engine.audio_queue.clear()
        self.update_ui_state()
    
    # ===== Playback Control =====
    
    def toggle_playback(self):
        """Toggle between play and pause."""
        if self.engine.video_playing or self.engine.audio_playing:
            self.engine.stop_streaming()
        else:
            self.engine.start_streaming()
        
        self.update_ui_state()
    
    def stop_playback(self):
        """Stop playback and reset to the beginning."""
        self.engine.stop_streaming()
        self.update_ui_state()
    
    def next_media(self):
        """Skip to the next media in the queue."""
        # For simplicity, we'll just stop and restart streaming
        self.engine.stop_streaming()
        if self.engine.video_queue or self.engine.audio_queue:
            self.engine.start_streaming()
        self.update_ui_state()
    
    def previous_media(self):
        """Go back to the previous media in the queue."""
        # For simplicity, we'll just stop and restart streaming
        self.engine.stop_streaming()
        if self.engine.video_queue or self.engine.audio_queue:
            self.engine.start_streaming()
        self.update_ui_state()
    
    def toggle_loop(self, checked):
        """Toggle loop mode."""
        self.engine.set_video_loop(checked)
        self.engine.set_audio_loop(checked)
    
    def play_selected_media(self, item):
        """Play the selected media file."""
        # For simplicity, we'll just start playing from the beginning
        self.engine.stop_streaming()
        self.engine.start_streaming()
        self.update_ui_state()
    
    # ===== UI Updates =====
    
    def update_ui_state(self):
        """Update the UI based on the current state."""
        # Update play/pause button
        if self.engine.video_playing or self.engine.audio_playing:
            self.btn_play.setIcon(qta.icon('fa5s.pause', color='white'))
            self.btn_play.setToolTip("Pause")
        else:
            self.btn_play.setIcon(qta.icon('fa5s.play', color='white'))
            self.btn_play.setToolTip("Play")
        
        # Update button states
        has_media = bool(self.engine.video_queue or self.engine.audio_queue)
        self.btn_play.setEnabled(has_media)
        self.btn_stop.setEnabled(has_media)
        self.btn_next.setEnabled(has_media and len(self.engine.video_queue) > 1)
        self.btn_prev.setEnabled(has_media and bool(self.engine.current_video_path or self.engine.current_audio_path))
        self.btn_loop.setEnabled(has_media)
        
        # Update status bar
        status = []
        if self.engine.current_video_path:
            status.append(f"Video: {Path(self.engine.current_video_path).name}")
        if self.engine.current_audio_path:
            status.append(f"Audio: {Path(self.engine.current_audio_path).name}")
        
        if status:
            self.status_bar.showMessage(" | ".join(status))
    
    def update_preview(self):
        """Update the video preview."""
        if not hasattr(self, 'engine') or not self.engine.video_capture:
            return
        
        try:
            ret, frame = self.engine.video_capture.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to QImage
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                
                # Scale image to fit the preview while maintaining aspect ratio
                scaled_pixmap = QPixmap.fromImage(q_img).scaled(
                    self.video_preview.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                self.video_preview.setPixmap(scaled_pixmap)
        except Exception as e:
            logger.error(f"Error updating preview: {e}")
    
    def update_status(self, message):
        """Update the status bar with a message."""
        self.status_bar.showMessage(message, 5000)  # Show for 5 seconds
        logger.info(message)
    
    def show_error(self, error):
        """Show an error message to the user."""
        QMessageBox.critical(self, "Error", error)
        logger.error(error)
    
    # ===== Theme Management =====
    
    def toggle_theme(self, dark_mode):
        """Toggle between dark and light themes."""
        self.dark_mode = dark_mode
        self.setup_styles()
    
    # ===== Window Events =====
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.engine.cleanup()
        event.accept()
    
    # ===== About Dialog =====
    
    def show_about(self):
        """Show the about dialog."""
        about_text = """
        <div style="text-align: center;">
            <h1 style="color: #6b9eff; margin-bottom: 10px;">StreamForge</h1>
            <p style="font-size: 14px; color: #888888; margin-top: 0;">Version 1.0.0</p>
            
            <p style="margin: 15px 0;">
                A virtual webcam and microphone streaming application<br>
                for Windows that just works.
            </p>
            
            <div style="margin: 20px 0; padding: 15px; background: rgba(107, 158, 255, 0.1); border-radius: 8px;">
                <p style="margin: 0; font-size: 13px; color: #6b9eff;">
                    Made with ❤️ by Wednesday
                </p>
            </div>
            
            <p style="font-size: 12px; color: #888888; margin-top: 20px;">
                Powered by Python, PyQt6, and OpenCV
            </p>
        </div>
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("About StreamForge")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        msg_box.setIconPixmap(qta.icon('fa5s.rocket', color='#6b9eff').pixmap(80, 80))
        
        # Set fixed size
        msg_box.setFixedSize(400, 400)
        
        # Center the dialog
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - msg_box.width()) // 2
        y = (screen.height() - msg_box.height()) // 2
        msg_box.move(x, y)
        
        msg_box.exec()

# Main function
def main():
    """Main function to start the application."""
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName("StreamForge")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("StreamForge")
    
    # Create and show main window
    window = StreamForgeDesktop()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
