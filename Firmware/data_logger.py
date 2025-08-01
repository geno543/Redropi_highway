import os
import json
import csv
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional
import cv2
import numpy as np

class DataLogger:
    def __init__(self, base_path: str = "/var/log/radropi"):
        self.logger = logging.getLogger('DataLogger')
        self.base_path = base_path
        self.data_lock = threading.Lock()
        
        self.paths = {
            'detections': os.path.join(base_path, 'detections'),
            'images': os.path.join(base_path, 'images'),
            'system_logs': os.path.join(base_path, 'system'),
            'exports': os.path.join(base_path, 'exports')
        }
        
        self._create_directories()
        
        self.detection_log_file = os.path.join(
            self.paths['detections'], 
            f"detections_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        
        self.session_stats = {
            'session_start': datetime.now().isoformat(),
            'total_detections': 0,
            'detection_types': {
                'meteor': 0,
                'asteroid': 0,
                'non_meteor': 0
            },
            'images_saved': 0,
            'system_events': 0
        }
        
        self._initialize_detection_log()
        self.logger.info(f"DataLogger initialized with base path: {base_path}")
    
    def _create_directories(self):
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)
        self.logger.info("Directory structure created")
    
    def _initialize_detection_log(self):
        try:
            file_exists = os.path.exists(self.detection_log_file)
            
            with open(self.detection_log_file, 'a', newline='') as csvfile:
                if not file_exists or os.path.getsize(self.detection_log_file) == 0:
                    fieldnames = [
                        'timestamp', 'type', 'confidence', 'coordinates_x', 'coordinates_y',
                        'bbox_x', 'bbox_y', 'bbox_w', 'bbox_h', 'area', 'aspect_ratio',
                        'brightness', 'gps_lat', 'gps_lon', 'gps_alt', 'frame_id', 'image_path'
                    ]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
            
            self.logger.info(f"Detection log initialized: {self.detection_log_file}")
            
        except Exception as e:
            self.logger.error(f"Error initializing detection log: {e}")
    
    def log_detection(self, detection_data: Dict):
        """
        Log a detection event to CSV file
        
        Args:
            detection_data (Dict): Detection event data
        """
        try:
            with self.data_lock:
                # Prepare CSV row
                csv_row = {
                    'timestamp': detection_data.get('timestamp', datetime.now().isoformat()),
                    'type': detection_data.get('type', 'unknown'),
                    'confidence': detection_data.get('confidence', 0.0),
                    'coordinates_x': detection_data.get('coordinates', [0, 0])[0],
                    'coordinates_y': detection_data.get('coordinates', [0, 0])[1],
                    'bbox_x': detection_data.get('bbox', [0, 0, 0, 0])[0],
                    'bbox_y': detection_data.get('bbox', [0, 0, 0, 0])[1],
                    'bbox_w': detection_data.get('bbox', [0, 0, 0, 0])[2],
                    'bbox_h': detection_data.get('bbox', [0, 0, 0, 0])[3],
                    'area': detection_data.get('area', 0),
                    'aspect_ratio': detection_data.get('properties', {}).get('aspect_ratio', 0),
                    'brightness': detection_data.get('properties', {}).get('brightness', 0),
                    'gps_lat': detection_data.get('gps_location', {}).get('latitude'),
                    'gps_lon': detection_data.get('gps_location', {}).get('longitude'),
                    'gps_alt': detection_data.get('gps_location', {}).get('altitude'),
                    'frame_id': detection_data.get('frame_id', ''),
                    'image_path': detection_data.get('image_path', '')
                }
                
                # Write to CSV
                with open(self.detection_log_file, 'a', newline='') as csvfile:
                    fieldnames = list(csv_row.keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(csv_row)
                
                # Update session statistics
                self.session_stats['total_detections'] += 1
                detection_type = detection_data.get('type', 'unknown')
                if detection_type in self.session_stats['detection_types']:
                    self.session_stats['detection_types'][detection_type] += 1
                
                self.logger.debug(f"Detection logged: {detection_type}")
                
        except Exception as e:
            self.logger.error(f"Error logging detection: {e}")
    
    def save_frame(self, frame: np.ndarray, detection_data: Dict) -> Optional[str]:
        """
        Save camera frame with detection overlay
        
        Args:
            frame (np.ndarray): Camera frame
            detection_data (Dict): Associated detection data
            
        Returns:
            Optional[str]: Path to saved image or None if failed
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            detection_type = detection_data.get('type', 'unknown')
            confidence = detection_data.get('confidence', 0.0)
            
            filename = f"{timestamp}_{detection_type}_{confidence:.2f}.jpg"
            filepath = os.path.join(self.paths['images'], filename)
            
            # Create annotated frame
            annotated_frame = self._annotate_frame(frame, detection_data)
            
            # Save image
            success = cv2.imwrite(filepath, annotated_frame)
            
            if success:
                self.session_stats['images_saved'] += 1
                self.logger.info(f"Frame saved: {filename}")
                
                # Update detection data with image path
                detection_data['image_path'] = filepath
                
                return filepath
            else:
                self.logger.error(f"Failed to save frame: {filename}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error saving frame: {e}")
            return None
    
    def _annotate_frame(self, frame: np.ndarray, detection_data: Dict) -> np.ndarray:
        """
        Add detection annotations to frame
        
        Args:
            frame (np.ndarray): Original frame
            detection_data (Dict): Detection information
            
        Returns:
            np.ndarray: Annotated frame
        """
        try:
            annotated = frame.copy()
            
            # Get detection info
            bbox = detection_data.get('bbox', [0, 0, 0, 0])
            detection_type = detection_data.get('type', 'unknown')
            confidence = detection_data.get('confidence', 0.0)
            
            if bbox and bbox[2] > 0 and bbox[3] > 0:  # Valid bounding box
                x, y, w, h = bbox
                
                # Choose color based on detection type
                colors = {
                    'meteor': (0, 255, 255),      # Yellow
                    'asteroid': (0, 0, 255),      # Red
                    'non_meteor': (128, 128, 128) # Gray
                }
                color = colors.get(detection_type, (255, 255, 255))
                
                # Draw bounding box
                cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
                
                # Add label
                label = f"{detection_type}: {confidence:.2f}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                
                # Background for text
                cv2.rectangle(annotated, (x, y - label_size[1] - 10), 
                            (x + label_size[0], y), color, -1)
                
                # Text
                cv2.putText(annotated, label, (x, y - 5), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # Add timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cv2.putText(annotated, timestamp, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            return annotated
            
        except Exception as e:
            self.logger.error(f"Error annotating frame: {e}")
            return frame
    
    def log_system_event(self, event_type: str, event_data: Dict):
        """
        Log system events (startup, shutdown, errors, etc.)
        
        Args:
            event_type (str): Type of system event
            event_data (Dict): Event details
        """
        try:
            event_log = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'data': event_data
            }
            
            # Save to JSON file
            log_file = os.path.join(
                self.paths['system_logs'], 
                f"system_events_{datetime.now().strftime('%Y%m%d')}.json"
            )
            
            # Append to file
            events = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        events = json.load(f)
                except json.JSONDecodeError:
                    events = []
            
            events.append(event_log)
            
            with open(log_file, 'w') as f:
                json.dump(events, f, indent=2)
            
            self.session_stats['system_events'] += 1
            self.logger.debug(f"System event logged: {event_type}")
            
        except Exception as e:
            self.logger.error(f"Error logging system event: {e}")
    
    def export_session_data(self, export_format: str = 'json') -> Optional[str]:
        """
        Export session data in specified format
        
        Args:
            export_format (str): Export format ('json', 'csv')
            
        Returns:
            Optional[str]: Path to exported file
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_format.lower() == 'json':
                filename = f"session_export_{timestamp}.json"
                filepath = os.path.join(self.paths['exports'], filename)
                
                export_data = {
                    'session_info': self.session_stats,
                    'export_timestamp': datetime.now().isoformat(),
                    'detection_log_file': self.detection_log_file
                }
                
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
            elif export_format.lower() == 'csv':
                filename = f"session_summary_{timestamp}.csv"
                filepath = os.path.join(self.paths['exports'], filename)
                
                with open(filepath, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Metric', 'Value'])
                    writer.writerow(['Session Start', self.session_stats['session_start']])
                    writer.writerow(['Total Detections', self.session_stats['total_detections']])
                    writer.writerow(['Meteor Detections', self.session_stats['detection_types']['meteor']])
                    writer.writerow(['Asteroid Detections', self.session_stats['detection_types']['asteroid']])
                    writer.writerow(['Non-meteor Detections', self.session_stats['detection_types']['non_meteor']])
                    writer.writerow(['Images Saved', self.session_stats['images_saved']])
                    writer.writerow(['System Events', self.session_stats['system_events']])
            
            else:
                self.logger.error(f"Unsupported export format: {export_format}")
                return None
            
            self.logger.info(f"Session data exported: {filename}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error exporting session data: {e}")
            return None
    
    def get_session_statistics(self) -> Dict:
        """
        Get current session statistics
        
        Returns:
            Dict: Session statistics
        """
        with self.data_lock:
            stats = self.session_stats.copy()
            stats['session_duration'] = (
                datetime.now() - datetime.fromisoformat(stats['session_start'])
            ).total_seconds()
            return stats
    
    def cleanup_old_files(self, days_to_keep: int = 30):
        """
        Clean up old log files and images
        
        Args:
            days_to_keep (int): Number of days to keep files
        """
        try:
            import time
            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
            
            cleaned_count = 0
            
            # Clean up images and logs
            for path in [self.paths['images'], self.paths['detections'], self.paths['system_logs']]:
                for filename in os.listdir(path):
                    filepath = os.path.join(path, filename)
                    if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} old files")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old files: {e}")
    
    def get_status(self) -> Dict:
        """
        Get data logger status
        
        Returns:
            Dict: Data logger status
        """
        return {
            'base_path': self.base_path,
            'detection_log_file': self.detection_log_file,
            'session_stats': self.get_session_statistics(),
            'directories_created': all(os.path.exists(path) for path in self.paths.values())
        }