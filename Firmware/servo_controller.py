import time
import logging
import threading
from typing import List, Dict, Tuple
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available, using mock servo controller")

class ServoController:
    def __init__(self):
        self.logger = logging.getLogger('ServoController')
        self.initialized = False
        self.servo_lock = threading.Lock()
        
        self.servo_pins = {
            'dish_azimuth': 18,
            'dish_elevation': 19,
            'camera_pan': 20,
            'camera_tilt': 21
        }
        
        self.current_positions = {
            'dish_azimuth': 90,
            'dish_elevation': 45,
            'camera_pan': 90,
            'camera_tilt': 90
        }
        
        self.servo_pwm = {}
        
        self.limits = {
            'dish_azimuth': (0, 180),
            'dish_elevation': (0, 90),
            'camera_pan': (0, 180),
            'camera_tilt': (30, 150)
        }
        
        self.logger.info("ServoController initialized")
    
    def initialize(self) -> bool:
        if not GPIO_AVAILABLE:
            self.logger.warning("GPIO not available, using mock mode")
            self.initialized = True
            return True
        
        try:
            self.logger.info("Initializing servo motors...")
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            for servo_name, pin in self.servo_pins.items():
                GPIO.setup(pin, GPIO.OUT)
                pwm = GPIO.PWM(pin, 50)
                pwm.start(0)
                self.servo_pwm[servo_name] = pwm
                self._move_servo_to_position(servo_name, self.current_positions[servo_name])
                time.sleep(0.5)
            
            self.initialized = True
            self.logger.info("All servo motors initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing servos: {e}")
            return False
    
    def _move_servo_to_position(self, servo_name: str, angle: float):
        """
        Move a specific servo to the given angle
        
        Args:
            servo_name (str): Name of the servo
            angle (float): Target angle in degrees (0-180)
        """
        if not self.initialized or not GPIO_AVAILABLE:
            return
        
        try:
            # Clamp angle to valid range
            min_angle, max_angle = self.limits[servo_name]
            angle = max(min_angle, min(max_angle, angle))
            
            # Convert angle to duty cycle
            # Standard servo: 1ms (0°) to 2ms (180°) pulse width
            # At 50Hz: 1ms = 5% duty, 2ms = 10% duty
            duty_cycle = 2.5 + (angle / 180.0) * 10.0
            
            # Set PWM duty cycle
            pwm = self.servo_pwm[servo_name]
            pwm.ChangeDutyCycle(duty_cycle)
            
            # Update current position
            self.current_positions[servo_name] = angle
            
        except Exception as e:
            self.logger.error(f"Error moving servo {servo_name}: {e}")
    
    def move_servo(self, servo_name: str, angle: float, smooth: bool = True) -> bool:
        """
        Move a servo to a specific angle
        
        Args:
            servo_name (str): Name of the servo to move
            angle (float): Target angle in degrees
            smooth (bool): Whether to move smoothly or jump directly
            
        Returns:
            bool: True if movement successful
        """
        if servo_name not in self.servo_pins:
            self.logger.error(f"Unknown servo: {servo_name}")
            return False
        
        try:
            with self.servo_lock:
                if smooth:
                    self._smooth_move(servo_name, angle)
                else:
                    self._move_servo_to_position(servo_name, angle)
            
            self.logger.debug(f"Moved {servo_name} to {angle}°")
            return True
            
        except Exception as e:
            self.logger.error(f"Error moving servo {servo_name}: {e}")
            return False
    
    def _smooth_move(self, servo_name: str, target_angle: float, step_size: float = 2.0):
        """
        Move servo smoothly to target position
        
        Args:
            servo_name (str): Name of the servo
            target_angle (float): Target angle
            step_size (float): Step size for smooth movement
        """
        current_angle = self.current_positions[servo_name]
        
        # Calculate direction and steps
        direction = 1 if target_angle > current_angle else -1
        steps = abs(target_angle - current_angle) / step_size
        
        # Move in small increments
        for i in range(int(steps)):
            new_angle = current_angle + (direction * step_size * (i + 1))
            self._move_servo_to_position(servo_name, new_angle)
            time.sleep(0.05)  # Small delay for smooth movement
        
        # Final position
        self._move_servo_to_position(servo_name, target_angle)
    
    def move_dish_to_coordinates(self, azimuth: float, elevation: float) -> bool:
        """
        Move satellite dish to specific coordinates
        
        Args:
            azimuth (float): Azimuth angle in degrees (0-360)
            elevation (float): Elevation angle in degrees (0-90)
            
        Returns:
            bool: True if movement successful
        """
        try:
            # Convert azimuth to servo range (0-180)
            servo_azimuth = (azimuth % 360) * 180 / 360
            
            # Move both servos
            success_az = self.move_servo('dish_azimuth', servo_azimuth)
            success_el = self.move_servo('dish_elevation', elevation)
            
            if success_az and success_el:
                self.logger.info(f"Dish positioned to Az: {azimuth}°, El: {elevation}°")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error positioning dish: {e}")
            return False
    
    def move_camera_to_coordinates(self, pan: float, tilt: float) -> bool:
        """
        Move camera to specific pan/tilt coordinates
        
        Args:
            pan (float): Pan angle in degrees (0-180)
            tilt (float): Tilt angle in degrees (30-150)
            
        Returns:
            bool: True if movement successful
        """
        try:
            success_pan = self.move_servo('camera_pan', pan)
            success_tilt = self.move_servo('camera_tilt', tilt)
            
            if success_pan and success_tilt:
                self.logger.info(f"Camera positioned to Pan: {pan}°, Tilt: {tilt}°")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error positioning camera: {e}")
            return False
    
    def track_objects(self, detections: List[Dict]):
        """
        Track detected objects by adjusting camera and dish positions
        
        Args:
            detections (List[Dict]): List of detected objects with coordinates
        """
        if not detections:
            return
        
        try:
            # Find the most significant detection (highest confidence)
            primary_detection = max(detections, key=lambda x: x.get('confidence', 0))
            
            # Extract object coordinates (assuming normalized 0-1 coordinates)
            x, y = primary_detection['coordinates']
            
            # Convert to servo angles
            # X coordinate maps to pan (0-180 degrees)
            pan_angle = x * 180
            
            # Y coordinate maps to tilt (30-150 degrees)
            tilt_angle = 30 + (y * 120)
            
            # Move camera to track object
            self.move_camera_to_coordinates(pan_angle, tilt_angle)
            
            # For significant detections, also point dish in same direction
            if primary_detection.get('confidence', 0) > 0.8:
                # Convert camera coordinates to dish coordinates
                dish_azimuth = pan_angle * 2  # Scale to 0-360 range
                dish_elevation = min(90, tilt_angle - 30)  # Adjust for dish limits
                
                self.move_dish_to_coordinates(dish_azimuth, dish_elevation)
            
        except Exception as e:
            self.logger.error(f"Error tracking objects: {e}")
    
    def home_all_servos(self) -> bool:
        """
        Move all servos to their home positions
        
        Returns:
            bool: True if all servos homed successfully
        """
        try:
            self.logger.info("Homing all servos...")
            
            # Home positions
            home_positions = {
                'dish_azimuth': 90,
                'dish_elevation': 45,
                'camera_pan': 90,
                'camera_tilt': 90
            }
            
            success = True
            for servo_name, angle in home_positions.items():
                if not self.move_servo(servo_name, angle):
                    success = False
            
            if success:
                self.logger.info("All servos homed successfully")
            else:
                self.logger.warning("Some servos failed to home")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error homing servos: {e}")
            return False
    
    def get_positions(self) -> Dict[str, float]:
        """
        Get current positions of all servos
        
        Returns:
            Dict[str, float]: Current servo positions
        """
        with self.servo_lock:
            return self.current_positions.copy()
    
    def get_status(self) -> Dict:
        """
        Get current servo controller status
        
        Returns:
            Dict: Servo controller status
        """
        return {
            'initialized': self.initialized,
            'gpio_available': GPIO_AVAILABLE,
            'servo_count': len(self.servo_pins),
            'current_positions': self.get_positions(),
            'limits': self.limits.copy()
        }
    
    def shutdown(self):
        """
        Shutdown servo controller and cleanup GPIO
        """
        self.logger.info("Shutting down servo controller...")
        
        try:
            # Home all servos before shutdown
            self.home_all_servos()
            time.sleep(1)
            
            # Stop all PWM signals
            for pwm in self.servo_pwm.values():
                pwm.stop()
            
            # Cleanup GPIO
            if GPIO_AVAILABLE:
                GPIO.cleanup()
            
            self.initialized = False
            self.logger.info("Servo controller shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during servo shutdown: {e}")

# Mock servo controller for testing without hardware
class MockServoController(ServoController):
    """
    Mock servo controller for testing without actual hardware
    """
    
    def __init__(self):
        self.logger = logging.getLogger('MockServoController')
        self.initialized = False
        self.servo_lock = threading.Lock()
        
        # Same configuration as real controller
        self.current_positions = {
            'dish_azimuth': 90,
            'dish_elevation': 45,
            'camera_pan': 90,
            'camera_tilt': 90
        }
        
        self.logger.info("MockServoController initialized")
    
    def initialize(self) -> bool:
        self.initialized = True
        self.logger.info("Mock servo controller initialized")
        return True
    
    def _move_servo_to_position(self, servo_name: str, angle: float):
        # Just update the position without actual hardware control
        self.current_positions[servo_name] = angle
        self.logger.debug(f"Mock servo {servo_name} moved to {angle}°")
    
    def shutdown(self):
        self.initialized = False
        self.logger.info("Mock servo controller shutdown")