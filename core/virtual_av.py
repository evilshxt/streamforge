"""
Virtual Audio/Video Engine

This module provides the core functionality for streaming video and audio
through virtual devices. It's designed to be used by both the desktop and web interfaces.
"""
import logging
import time
import threading
import queue
from typing import Optional, List, Tuple, Callable
from pathlib import Path

import cv2
import numpy as np
import sounddevice as sd
import soundfile as sf
from loguru import logger

class VirtualAVEngine:
    """Core engine for handling virtual audio and video streaming.
    
    This class manages the virtual webcam and microphone feeds, including
    file loading, playback control, and device management.
    """
    
    # Supported file formats
    VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    AUDIO_EXTS = {'.wav', '.mp3', '.flac', '.ogg', '.aac'}
    
    def __init__(self):
        # Video properties
        self.video_capture: Optional[cv2.VideoCapture] = None
        self.virtual_cam = None
        self.current_video_path: Optional[str] = None
        self.video_queue: List[str] = []
        self.video_playing = False
        self.video_loop = False
        self.video_thread: Optional[threading.Thread] = None
        self.video_stop_event = threading.Event()
        
        # Audio properties
        self.audio_stream: Optional[sd.OutputStream] = None
        self.audio_data = None
        self.audio_samplerate = 44100
        self.current_audio_path: Optional[str] = None
        self.audio_queue: List[str] = []
        self.audio_playing = False
        self.audio_loop = False
        self.audio_thread: Optional[threading.Thread] = None
        self.audio_stop_event = threading.Event()
        
        # Callbacks for UI updates
        self.status_callbacks = []
        self.error_callbacks = []
        
        logger.info("VirtualAVEngine initialized")
    
    # ===== Core Methods =====
    
    def load_media(self, paths: List[str]) -> Tuple[List[str], List[str]]:
        """Load media files from the given paths.
        
        Args:
            paths: List of file or directory paths to load media from
            
        Returns:
            Tuple of (loaded_paths, error_messages)
        """
        loaded = []
        errors = []
        
        for path in paths:
            path = str(Path(path).absolute())
            path_obj = Path(path)
            
            if path_obj.is_file():
                if self._is_video_file(path):
                    self.video_queue.append(path)
                    loaded.append(f"Video: {path}")
                elif self._is_audio_file(path):
                    self.audio_queue.append(path)
                    loaded.append(f"Audio: {path}")
                else:
                    errors.append(f"Unsupported file format: {path}")
            elif path_obj.is_dir():
                # Recursively find all media files in directory
                for ext in self.VIDEO_EXTS.union(self.AUDIO_EXTS):
                    for file_path in path_obj.rglob(f"*{ext}"):
                        file_path = str(file_path.absolute())
                        if self._is_video_file(file_path):
                            self.video_queue.append(file_path)
                            loaded.append(f"Video: {file_path}")
                        elif self._is_audio_file(file_path):
                            self.audio_queue.append(file_path)
                            loaded.append(f"Audio: {file_path}")
            else:
                errors.append(f"File or directory not found: {path}")
        
        # If we have video but no audio, or vice versa, notify
        if self.video_queue and not self.audio_queue:
            logger.warning("Video files loaded but no audio files found")
        elif self.audio_queue and not self.video_queue:
            logger.warning("Audio files loaded but no video files found")
        
        return loaded, errors
    
    def start_streaming(self):
        """Start both video and audio streaming."""
        if not self.video_playing and self.video_queue:
            self._start_video_stream()
        
        if not self.audio_playing and self.audio_queue:
            self._start_audio_stream()
    
    def stop_streaming(self):
        """Stop both video and audio streaming."""
        self._stop_video_stream()
        self._stop_audio_stream()
    
    # ===== Video Methods =====
    
    def _start_video_stream(self):
        """Start the video streaming thread."""
        if self.video_playing or not self.video_queue:
            return
        
        self.video_stop_event.clear()
        self.video_thread = threading.Thread(target=self._video_stream_worker, daemon=True)
        self.video_thread.start()
        self.video_playing = True
        self._notify_status("Video streaming started")
    
    def _stop_video_stream(self):
        """Stop the video streaming thread."""
        if not self.video_playing:
            return
        
        self.video_stop_event.set()
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=2.0)
        
        if self.virtual_cam:
            try:
                self.virtual_cam.close()
            except Exception as e:
                logger.error(f"Error closing virtual camera: {e}")
            self.virtual_cam = None
        
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        
        self.video_playing = False
        self._notify_status("Video streaming stopped")
    
    def _video_stream_worker(self):
        """Worker thread for streaming video frames."""
        try:
            import pyvirtualcam
            
            while not self.video_stop_event.is_set() and self.video_queue:
                self.current_video_path = self.video_queue.pop(0)
                
                try:
                    self.video_capture = cv2.VideoCapture(self.current_video_path)
                    if not self.video_capture.isOpened():
                        raise IOError(f"Could not open video file: {self.current_video_path}")
                    
                    # Get video properties
                    width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = self.video_capture.get(cv2.CAP_PROP_FPS)
                    
                    # Initialize virtual camera
                    self.virtual_cam = pyvirtualcam.Camera(width=width, height=height, fps=fps)
                    
                    logger.info(f"Streaming video: {self.current_video_path} ({width}x{height} @ {fps}fps)")
                    
                    # Main video loop
                    while not self.video_stop_event.is_set():
                        ret, frame = self.video_capture.read()
                        if not ret:
                            if self.video_loop and self.video_queue:
                                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                                continue
                            break
                        
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        self.virtual_cam.send(frame_rgb)
                        self.virtual_cam.sleep_until_next_frame()
                    
                except Exception as e:
                    logger.error(f"Error in video stream: {e}")
                    self._notify_error(f"Video error: {str(e)}")
                    time.sleep(1)  # Prevent tight loop on error
                
                finally:
                    if self.video_capture:
                        self.video_capture.release()
                        self.video_capture = None
                    
                    if self.virtual_cam:
                        self.virtual_cam.close()
                        self.virtual_cam = None
                    
                    # If looping, add the video back to the queue
                    if self.video_loop and self.current_video_path:
                        self.video_queue.append(self.current_video_path)
                
                if not self.video_loop:
                    break
            
        except ImportError:
            error_msg = "pyvirtualcam not installed. Virtual webcam will not work."
            logger.error(error_msg)
            self._notify_error(error_msg)
        
        self.video_playing = False
        self._notify_status("Video streaming ended")
    
    # ===== Audio Methods =====
    
    def _start_audio_stream(self):
        """Start the audio streaming thread."""
        if self.audio_playing or not self.audio_queue:
            return
        
        self.audio_stop_event.clear()
        self.audio_thread = threading.Thread(target=self._audio_stream_worker, daemon=True)
        self.audio_thread.start()
        self.audio_playing = True
        self._notify_status("Audio streaming started")
    
    def _stop_audio_stream(self):
        """Stop the audio streaming thread."""
        if not self.audio_playing:
            return
        
        self.audio_stop_event.set()
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2.0)
        
        if self.audio_stream:
            try:
                self.audio_stream.stop()
                self.audio_stream.close()
            except Exception as e:
                logger.error(f"Error stopping audio stream: {e}")
            self.audio_stream = None
        
        self.audio_playing = False
        self.audio_data = None
        self._notify_status("Audio streaming stopped")
    
    def _audio_stream_worker(self):
        """Worker thread for streaming audio."""
        try:
            while not self.audio_stop_event.is_set() and self.audio_queue:
                self.current_audio_path = self.audio_queue.pop(0)
                
                try:
                    # Load audio file
                    self.audio_data, self.audio_samplerate = sf.read(
                        self.current_audio_path, 
                        always_2d=True,  # Force stereo if mono
                        dtype='float32'  # Required by sounddevice
                    )
                    
                    # Convert to interleaved format if needed
                    if len(self.audio_data.shape) == 1:
                        self.audio_data = np.column_stack((self.audio_data, self.audio_data))
                    
                    logger.info(f"Streaming audio: {self.current_audio_path} ({self.audio_samplerate}Hz, {len(self.audio_data)} samples)")
                    
                    # Start audio stream
                    self.audio_stream = sd.OutputStream(
                        samplerate=self.audio_samplerate,
                        channels=2,  # Force stereo output
                        dtype='float32',
                        device='CABLE Input (VB-Audio Virtual Cable)'
                    )
                    
                    self.audio_stream.start()
                    
                    # Main audio loop
                    position = 0
                    while not self.audio_stop_event.is_set() and position < len(self.audio_data):
                        chunk_size = 1024  # Process in chunks to remain responsive
                        chunk = self.audio_data[position:position + chunk_size]
                        
                        # Pad with zeros if needed (shouldn't happen with proper chunking)
                        if len(chunk) < chunk_size:
                            padding = np.zeros((chunk_size - len(chunk), 2), dtype='float32')
                            chunk = np.vstack((chunk, padding))
                        
                        self.audio_stream.write(chunk)
                        position += chunk_size
                        
                        # Small sleep to prevent CPU hogging
                        time.sleep(0.001)
                    
                    # If we've reached the end and loop is enabled, add back to queue
                    if self.audio_loop and position >= len(self.audio_data) and self.current_audio_path:
                        self.audio_queue.append(self.current_audio_path)
                    
                except Exception as e:
                    logger.error(f"Error in audio stream: {e}")
                    self._notify_error(f"Audio error: {str(e)}")
                    time.sleep(1)  # Prevent tight loop on error
                
                finally:
                    if self.audio_stream:
                        self.audio_stream.stop()
                        self.audio_stream.close()
                        self.audio_stream = None
                    
                    self.audio_data = None
                
                if not self.audio_loop:
                    break
            
        except Exception as e:
            logger.error(f"Fatal error in audio worker: {e}")
            self._notify_error(f"Fatal audio error: {str(e)}")
        
        self.audio_playing = False
        self._notify_status("Audio streaming ended")
    
    # ===== Helper Methods =====
    
    def _is_video_file(self, path: str) -> bool:
        """Check if the given path points to a supported video file."""
        return Path(path).suffix.lower() in self.VIDEO_EXTS
    
    def _is_audio_file(self, path: str) -> bool:
        """Check if the given path points to a supported audio file."""
        return Path(path).suffix.lower() in self.AUDIO_EXTS
    
    def _notify_status(self, message: str):
        """Notify all registered status callbacks."""
        logger.info(message)
        for callback in self.status_callbacks:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def _notify_error(self, error: str):
        """Notify all registered error callbacks."""
        logger.error(error)
        for callback in self.error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
    
    # ===== Public API =====
    
    def register_status_callback(self, callback: Callable[[str], None]):
        """Register a callback for status updates."""
        if callback not in self.status_callbacks:
            self.status_callbacks.append(callback)
    
    def register_error_callback(self, callback: Callable[[str], None]):
        """Register a callback for error messages."""
        if callback not in self.error_callbacks:
            self.error_callbacks.append(callback)
    
    def set_video_loop(self, loop: bool):
        """Enable or disable video looping."""
        self.video_loop = loop
        logger.info(f"Video loop {'enabled' if loop else 'disabled'}")
    
    def set_audio_loop(self, loop: bool):
        """Enable or disable audio looping."""
        self.audio_loop = loop
        logger.info(f"Audio loop {'enabled' if loop else 'disabled'}")
    
    def get_status(self) -> dict:
        """Get the current status of the engine."""
        return {
            'video': {
                'playing': self.video_playing,
                'current': self.current_video_path,
                'queue_size': len(self.video_queue),
                'loop': self.video_loop
            },
            'audio': {
                'playing': self.audio_playing,
                'current': self.current_audio_path,
                'queue_size': len(self.audio_queue),
                'loop': self.audio_loop
            }
        }
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_streaming()
        self.status_callbacks.clear()
        self.error_callbacks.clear()
        logger.info("VirtualAVEngine cleaned up")
