import cv2
import numpy as np
import logging
import threading
import time
from typing import Optional

class CameraController:
    def __init__(self, camera_id: int = 0):
        self.logger = logging.getLogger('CameraController')
        self.camera_id = camera_id
        self.cap = None
        self.running = False
        self.frame_lock = threading.Lock()
        self.latest_frame = None
        
        self.settings = {
            'width': 1920,
            'height': 1080,
            'fps': 30,
            'exposure': -6,
            'gain': 50,
            'brightness': 50,
            'contrast': 50,
            'saturation': 50
        }
        
        self.logger.info(f"CameraController initialized for camera {camera_id}")
    
    def start(self) -> bool:
        try:
            self.logger.info("Starting camera system...")
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                self.logger.error(f"Failed to open camera {self.camera_id}")
                return False
            
            self._configure_camera()
            
            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            self.logger.info("Camera system started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting camera: {e}")
            return False
    
    def _configure_camera(self):
        """
        Configure camera settings for optimal astrophotography
        """
        try:
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings['width'])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings['height'])
            
            # Set frame rate
            self.cap.set(cv2.CAP_PROP_FPS, self.settings['fps'])
            
            # Set exposure (negative values for auto exposure)
            self.cap.set(cv2.CAP_PROP_EXPOSURE, self.settings['exposure'])
            
            # Set gain for low-light performance
            self.cap.set(cv2.CAP_PROP_GAIN, self.settings['gain'])
            
            # Set other image properties
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.settings['brightness'])
            self.cap.set(cv2.CAP_PROP_CONTRAST, self.settings['contrast'])
            self.cap.set(cv2.CAP_PROP_SATURATION, self.settings['saturation'])
            
            # Enable auto white balance for varying lighting conditions
            self.cap.set(cv2.CAP_PROP_AUTO_WB, 1)
            
            self.logger.info("Camera configured for astrophotography")
            
        except Exception as e:
            self.logger.warning(f"Some camera settings may not be supported: {e}")
    
    def _capture_loop(self):
        """
        Continuous frame capture loop running in separate thread
        """
        self.logger.info("Camera capture loop started")
        
        while self.running:
            try:
                ret, frame = self.cap.read()
                
                if ret:
                    # Apply image enhancements for low-light conditions
                    enhanced_frame = self._enhance_frame(frame)
                    
                    # Store latest frame thread-safely
                    with self.frame_lock:
                        self.latest_frame = enhanced_frame
                else:
                    self.logger.warning("Failed to capture frame")
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Error in capture loop: {e}")
                time.sleep(1)
        
        self.logger.info("Camera capture loop stopped")
    
    def _enhance_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply image enhancements for better low-light performance
        
        Args:
            frame (np.ndarray): Raw camera frame
            
        Returns:
            np.ndarray: Enhanced frame
        """
        try:
            # Convert to LAB color space for better processing
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            # to the L channel for better contrast in low light
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels back
            enhanced_lab = cv2.merge([l, a, b])
            enhanced_frame = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            # Apply slight denoising
            enhanced_frame = cv2.bilateralFilter(enhanced_frame, 9, 75, 75)
            
            return enhanced_frame
            
        except Exception as e:
            self.logger.warning(f"Frame enhancement failed: {e}")
            return frame
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Get the latest captured frame
        
        Returns:
            Optional[np.ndarray]: Latest camera frame or None if not available
        """
        with self.frame_lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None
    
    def save_frame(self, filename: str, frame: Optional[np.ndarray] = None) -> bool:
        """
        Save a frame to disk
        
        Args:
            filename (str): Output filename
            frame (Optional[np.ndarray]): Frame to save, uses latest if None
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if frame is None:
                frame = self.capture_frame()
            
            if frame is not None:
                cv2.imwrite(filename, frame)
                self.logger.info(f"Frame saved to {filename}")
                return True
            else:
                self.logger.warning("No frame available to save")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saving frame: {e}")
            return False
    
    def get_camera_info(self) -> dict:
        """
        Get current camera information and settings
        
        Returns:
            dict: Camera information
        """
        if self.cap is None:
            return {'status': 'not_initialized'}
        
        try:
            info = {
                'status': 'running' if self.running else 'stopped',
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': self.cap.get(cv2.CAP_PROP_FPS),
                'exposure': self.cap.get(cv2.CAP_PROP_EXPOSURE),
                'gain': self.cap.get(cv2.CAP_PROP_GAIN),
                'brightness': self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
                'contrast': self.cap.get(cv2.CAP_PROP_CONTRAST)
            }
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting camera info: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def adjust_exposure(self, exposure_value: int):
        """
        Adjust camera exposure setting
        
        Args:
            exposure_value (int): Exposure value (-13 to -1 for auto, or manual value)
        """
        try:
            if self.cap is not None:
                self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure_value)
                self.settings['exposure'] = exposure_value
                self.logger.info(f"Exposure adjusted to {exposure_value}")
        except Exception as e:
            self.logger.error(f"Error adjusting exposure: {e}")
    
    def adjust_gain(self, gain_value: int):
        """
        Adjust camera gain setting
        
        Args:
            gain_value (int): Gain value (0-100)
        """
        try:
            if self.cap is not None and 0 <= gain_value <= 100:
                self.cap.set(cv2.CAP_PROP_GAIN, gain_value)
                self.settings['gain'] = gain_value
                self.logger.info(f"Gain adjusted to {gain_value}")
        except Exception as e:
            self.logger.error(f"Error adjusting gain: {e}")
    
    def get_status(self) -> dict:
        """
        Get current camera status
        
        Returns:
            dict: Camera status information
        """
        return {
            'running': self.running,
            'camera_id': self.camera_id,
            'has_frame': self.latest_frame is not None,
            'settings': self.settings.copy()
        }
    
    def stop(self):
        """
        Stop the camera and cleanup resources
        """
        self.logger.info("Stopping camera system...")
        
        self.running = False
        
        # Wait for capture thread to finish
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=5)
        
        # Release camera resources
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        self.logger.info("Camera system stopped")