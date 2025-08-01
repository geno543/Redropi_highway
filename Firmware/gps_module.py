import serial
import threading
import time
import logging
from typing import Optional, Dict, Tuple
import pynmea2

class GPSController:
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 9600):
        self.logger = logging.getLogger('GPSController')
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
        
        self.gps_lock = threading.Lock()
        self.current_location = {
            'latitude': None,
            'longitude': None,
            'altitude': None,
            'timestamp': None,
            'satellites': 0,
            'fix_quality': 0,
            'hdop': None
        }
        
        self.logger.info(f"GPSController initialized for port {port}")
    
    def start(self) -> bool:
        try:
            self.logger.info("Starting GPS module...")
            
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            
            if not self.serial_conn.is_open:
                self.logger.error("Failed to open GPS serial connection")
                return False
            
            self.running = True
            self.gps_thread = threading.Thread(target=self._gps_read_loop)
            self.gps_thread.daemon = True
            self.gps_thread.start()
            
            self.logger.info("GPS module started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting GPS module: {e}")
            return False
    
    def _gps_read_loop(self):
        """
        Continuous GPS data reading loop
        """
        self.logger.info("GPS reading loop started")
        
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting > 0:
                    # Read NMEA sentence
                    line = self.serial_conn.readline().decode('ascii', errors='replace').strip()
                    
                    if line.startswith('$'):
                        self._parse_nmea_sentence(line)
                
                time.sleep(0.1)  # Small delay to prevent CPU overload
                
            except Exception as e:
                self.logger.error(f"Error in GPS reading loop: {e}")
                time.sleep(1)
        
        self.logger.info("GPS reading loop stopped")
    
    def _parse_nmea_sentence(self, sentence: str):
        """
        Parse NMEA sentence and update GPS data
        
        Args:
            sentence (str): NMEA sentence string
        """
        try:
            msg = pynmea2.parse(sentence)
            
            # Handle different NMEA message types
            if isinstance(msg, pynmea2.GGA):  # Global Positioning System Fix Data
                self._update_gga_data(msg)
            elif isinstance(msg, pynmea2.RMC):  # Recommended Minimum Course
                self._update_rmc_data(msg)
            elif isinstance(msg, pynmea2.GSA):  # GPS DOP and active satellites
                self._update_gsa_data(msg)
                
        except pynmea2.ParseError:
            # Ignore parse errors for malformed sentences
            pass
        except Exception as e:
            self.logger.warning(f"Error parsing NMEA sentence: {e}")
    
    def _update_gga_data(self, msg):
        """
        Update GPS data from GGA message
        
        Args:
            msg: Parsed GGA message
        """
        with self.gps_lock:
            if msg.latitude and msg.longitude:
                self.current_location['latitude'] = float(msg.latitude)
                self.current_location['longitude'] = float(msg.longitude)
                self.current_location['altitude'] = float(msg.altitude) if msg.altitude else None
                self.current_location['satellites'] = int(msg.num_sats) if msg.num_sats else 0
                self.current_location['fix_quality'] = int(msg.gps_qual) if msg.gps_qual else 0
                self.current_location['hdop'] = float(msg.horizontal_dil) if msg.horizontal_dil else None
                self.current_location['timestamp'] = time.time()
    
    def _update_rmc_data(self, msg):
        """
        Update GPS data from RMC message
        
        Args:
            msg: Parsed RMC message
        """
        with self.gps_lock:
            if msg.latitude and msg.longitude:
                self.current_location['latitude'] = float(msg.latitude)
                self.current_location['longitude'] = float(msg.longitude)
                self.current_location['timestamp'] = time.time()
    
    def _update_gsa_data(self, msg):
        """
        Update GPS data from GSA message
        
        Args:
            msg: Parsed GSA message
        """
        with self.gps_lock:
            if msg.hdop:
                self.current_location['hdop'] = float(msg.hdop)
    
    def get_location(self) -> Dict:
        """
        Get current GPS location data
        
        Returns:
            Dict: Current location information
        """
        with self.gps_lock:
            return self.current_location.copy()
    
    def get_coordinates(self) -> Optional[Tuple[float, float]]:
        """
        Get current latitude and longitude coordinates
        
        Returns:
            Optional[Tuple[float, float]]: (latitude, longitude) or None if no fix
        """
        location = self.get_location()
        
        if location['latitude'] is not None and location['longitude'] is not None:
            return (location['latitude'], location['longitude'])
        
        return None
    
    def has_fix(self) -> bool:
        """
        Check if GPS has a valid position fix
        
        Returns:
            bool: True if GPS has valid fix
        """
        location = self.get_location()
        return (
            location['latitude'] is not None and 
            location['longitude'] is not None and
            location['fix_quality'] > 0
        )
    
    def get_fix_quality_description(self) -> str:
        """
        Get human-readable description of GPS fix quality
        
        Returns:
            str: Fix quality description
        """
        quality = self.current_location['fix_quality']
        
        quality_descriptions = {
            0: "No fix",
            1: "GPS fix (SPS)",
            2: "DGPS fix",
            3: "PPS fix",
            4: "Real Time Kinematic",
            5: "Float RTK",
            6: "Estimated (dead reckoning)",
            7: "Manual input mode",
            8: "Simulation mode"
        }
        
        return quality_descriptions.get(quality, "Unknown")
    
    def wait_for_fix(self, timeout: int = 60) -> bool:
        """
        Wait for GPS to acquire a valid fix
        
        Args:
            timeout (int): Maximum time to wait in seconds
            
        Returns:
            bool: True if fix acquired within timeout
        """
        self.logger.info(f"Waiting for GPS fix (timeout: {timeout}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.has_fix():
                location = self.get_location()
                self.logger.info(
                    f"GPS fix acquired: {location['latitude']:.6f}, "
                    f"{location['longitude']:.6f} (Quality: {self.get_fix_quality_description()})"
                )
                return True
            
            time.sleep(1)
        
        self.logger.warning(f"GPS fix not acquired within {timeout} seconds")
        return False
    
    def get_satellite_info(self) -> Dict:
        """
        Get information about visible satellites
        
        Returns:
            Dict: Satellite information
        """
        location = self.get_location()
        
        return {
            'satellites_used': location['satellites'],
            'fix_quality': location['fix_quality'],
            'fix_description': self.get_fix_quality_description(),
            'hdop': location['hdop'],
            'has_fix': self.has_fix()
        }
    
    def get_status(self) -> Dict:
        """
        Get current GPS module status
        
        Returns:
            Dict: GPS status information
        """
        location = self.get_location()
        
        return {
            'running': self.running,
            'connected': self.serial_conn is not None and self.serial_conn.is_open,
            'has_fix': self.has_fix(),
            'satellites': location['satellites'],
            'fix_quality': location['fix_quality'],
            'last_update': location['timestamp']
        }
    
    def stop(self):
        """
        Stop GPS module and cleanup resources
        """
        self.logger.info("Stopping GPS module...")
        
        self.running = False
        
        # Wait for GPS thread to finish
        if hasattr(self, 'gps_thread'):
            self.gps_thread.join(timeout=5)
        
        # Close serial connection
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.serial_conn = None
        
        self.logger.info("GPS module stopped")

# Fallback GPS controller for testing without hardware
class MockGPSController(GPSController):
    """
    Mock GPS controller for testing without actual GPS hardware
    """
    
    def __init__(self):
        self.logger = logging.getLogger('MockGPSController')
        self.running = False
        
        # Mock location (example coordinates)
        self.gps_lock = threading.Lock()
        self.current_location = {
            'latitude': 40.7128,   # New York City
            'longitude': -74.0060,
            'altitude': 10.0,
            'timestamp': time.time(),
            'satellites': 8,
            'fix_quality': 1,
            'hdop': 1.2
        }
        
        self.logger.info("MockGPSController initialized")
    
    def start(self) -> bool:
        self.running = True
        self.logger.info("Mock GPS started with simulated location")
        return True
    
    def stop(self):
        self.running = False
        self.logger.info("Mock GPS stopped")