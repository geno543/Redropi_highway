import time
import threading
import logging
from datetime import datetime
import json

from camera_controller import CameraController
from gps_module import GPSController
from servo_controller import ServoController
from detection_ai import AsteroidDetector
from data_logger import DataLogger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/radropi.log'),
        logging.StreamHandler()
    ]
)

class RadropiSystem:
    def __init__(self):
        self.logger = logging.getLogger('RadropiSystem')
        self.running = False
        
        self.camera = CameraController()
        self.gps = GPSController()
        self.servos = ServoController()
        self.detector = AsteroidDetector()
        self.data_logger = DataLogger()
        
        self.detection_count = {
            'meteor': 0,
            'asteroid': 0,
            'non_meteor': 0
        }
        
        self.logger.info("Radropi system initialized")
    
    def start_system(self):
        try:
            self.logger.info("Starting Radropi detection system...")
            
            self.gps.start()
            location = self.gps.get_location()
            self.logger.info(f"GPS Location: {location}")
            
            self.camera.start()
            self.logger.info("Camera system started")
            
            self.servos.initialize()
            self.logger.info("Servo tracking system initialized")
            
            self.detector.load_model()
            self.logger.info("AI detection model loaded")
            
            self.running = True
            self.main_detection_loop()
            
        except Exception as e:
            self.logger.error(f"Error starting system: {e}")
            self.shutdown()
    
    def main_detection_loop(self):
        self.logger.info("Starting main detection loop")
        
        while self.running:
            try:
                frame = self.camera.capture_frame()
                
                if frame is not None:
                    detections = self.detector.analyze_frame(frame)
                    
                    for detection in detections:
                        self.process_detection(detection, frame)
                    
                    if detections:
                        self.servos.track_objects(detections)
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.logger.info("Received shutdown signal")
                break
            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                time.sleep(1)
        
        self.shutdown()
    
    def process_detection(self, detection, frame):
        try:
            object_type = detection['type']
            confidence = detection['confidence']
            coordinates = detection['coordinates']
            
            if object_type in self.detection_count:
                self.detection_count[object_type] += 1
            
            timestamp = datetime.now().isoformat()
            gps_location = self.gps.get_location()
            
            detection_data = {
                'timestamp': timestamp,
                'type': object_type,
                'confidence': confidence,
                'coordinates': coordinates,
                'gps_location': gps_location,
                'frame_id': id(frame)
            }
            
            self.data_logger.log_detection(detection_data)
            
            self.logger.info(
                f"Detection: {object_type} (confidence: {confidence:.2f}) "
                f"at {coordinates}"
            )
            
            if confidence > 0.8 and object_type in ['meteor', 'asteroid']:
                self.data_logger.save_frame(frame, detection_data)
            
        except Exception as e:
            self.logger.error(f"Error processing detection: {e}")
    
    def get_system_status(self):
        return {
            'running': self.running,
            'detection_count': self.detection_count,
            'gps_status': self.gps.get_status(),
            'camera_status': self.camera.get_status(),
            'servo_status': self.servos.get_status(),
            'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
        }
    
    def shutdown(self):
        self.logger.info("Shutting down Radropi system...")
        
        self.running = False
        
        if hasattr(self, 'camera'):
            self.camera.stop()
        
        if hasattr(self, 'gps'):
            self.gps.stop()
        
        if hasattr(self, 'servos'):
            self.servos.shutdown()
        
        self.logger.info(f"Final detection count: {self.detection_count}")
        self.logger.info("Radropi system shutdown complete")

def main():
    print("Radropi - Asteroid and Meteor Detection System")
    print("Version 1.0 - July 2025")
    print("="*50)
    
    radropi = RadropiSystem()
    radropi.start_time = time.time()
    
    try:
        radropi.start_system()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"System error: {e}")
    finally:
        radropi.shutdown()

if __name__ == "__main__":
    main()