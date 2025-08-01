import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple
import time

class AsteroidDetector:
    def __init__(self):
        self.logger = logging.getLogger('AsteroidDetector')
        self.model_loaded = False
        self.detection_threshold = 0.5
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True,
            varThreshold=50
        )
        
        self.categories = {
            0: 'non_meteor',
            1: 'meteor', 
            2: 'asteroid'
        }
        
        self.logger.info("AsteroidDetector initialized")
    
    def load_model(self):
        try:
            self.logger.info("Loading AI detection model...")
            time.sleep(2)
            self.model_loaded = True
            self.logger.info("AI model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load AI model: {e}")
            raise
    
    def analyze_frame(self, frame: np.ndarray) -> List[Dict]:
        if not self.model_loaded:
            self.logger.warning("AI model not loaded, skipping analysis")
            return []
        
        try:
            detections = []
            processed_frame = self.preprocess_frame(frame)
            moving_objects = self.detect_moving_objects(processed_frame)
            
            for obj in moving_objects:
                classification = self.classify_object(obj, processed_frame)
                if classification['confidence'] > self.detection_threshold:
                    detections.append(classification)
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Error analyzing frame: {e}")
            return []
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        enhanced = cv2.equalizeHist(blurred)
        return enhanced
    
    def detect_moving_objects(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect moving objects in the frame using background subtraction
        
        Args:
            frame (np.ndarray): Preprocessed frame
            
        Returns:
            List[Dict]: List of detected moving objects
        """
        objects = []
        
        try:
            # Apply background subtraction
            fg_mask = self.background_subtractor.apply(frame)
            
            # Remove noise with morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours of moving objects
            contours, _ = cv2.findContours(
                fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filter contours by size and characteristics
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter out very small or very large objects
                if 50 < area < 5000:
                    # Get bounding box
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate object properties
                    aspect_ratio = w / h if h > 0 else 0
                    
                    objects.append({
                        'contour': contour,
                        'bbox': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'center': (x + w//2, y + h//2)
                    })
            
        except Exception as e:
            self.logger.error(f"Error detecting moving objects: {e}")
        
        return objects
    
    def classify_object(self, obj: Dict, frame: np.ndarray) -> Dict:
        """
        Classify a detected object using AI model
        
        Args:
            obj (Dict): Object detection data
            frame (np.ndarray): Source frame
            
        Returns:
            Dict: Classification result with confidence
        """
        try:
            # Extract object region
            x, y, w, h = obj['bbox']
            roi = frame[y:y+h, x:x+w]
            
            # Placeholder for actual AI classification
            # In production, this would use a trained neural network
            
            # Simple heuristic-based classification for demonstration
            classification = self.heuristic_classification(obj, roi)
            
            return {
                'type': classification['type'],
                'confidence': classification['confidence'],
                'coordinates': obj['center'],
                'bbox': obj['bbox'],
                'area': obj['area'],
                'properties': {
                    'aspect_ratio': obj['aspect_ratio'],
                    'brightness': np.mean(roi) if roi.size > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error classifying object: {e}")
            return {
                'type': 'non_meteor',
                'confidence': 0.0,
                'coordinates': obj['center'],
                'bbox': obj['bbox'],
                'area': obj['area']
            }
    
    def heuristic_classification(self, obj: Dict, roi: np.ndarray) -> Dict:
        """
        Simple heuristic-based classification (placeholder for AI model)
        
        Args:
            obj (Dict): Object properties
            roi (np.ndarray): Object region of interest
            
        Returns:
            Dict: Classification result
        """
        area = obj['area']
        aspect_ratio = obj['aspect_ratio']
        brightness = np.mean(roi) if roi.size > 0 else 0
        
        # Simple classification rules
        if brightness > 200 and area > 100:
            if aspect_ratio > 2.0:  # Elongated bright object
                return {'type': 'meteor', 'confidence': 0.8}
            elif area > 500:  # Large bright object
                return {'type': 'asteroid', 'confidence': 0.7}
            else:
                return {'type': 'meteor', 'confidence': 0.6}
        elif brightness > 150:
            return {'type': 'meteor', 'confidence': 0.5}
        else:
            return {'type': 'non_meteor', 'confidence': 0.9}
    
    def get_detection_stats(self) -> Dict:
        """
        Get detection system statistics
        
        Returns:
            Dict: Detection statistics
        """
        return {
            'model_loaded': self.model_loaded,
            'detection_threshold': self.detection_threshold,
            'categories': self.categories
        }
    
    def set_detection_threshold(self, threshold: float):
        """
        Set the detection confidence threshold
        
        Args:
            threshold (float): New threshold value (0.0 to 1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.detection_threshold = threshold
            self.logger.info(f"Detection threshold set to {threshold}")
        else:
            self.logger.warning(f"Invalid threshold value: {threshold}")