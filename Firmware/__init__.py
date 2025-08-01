__version__ = "1.0.0"
__author__ = "Radropi Team"
__email__ = "team@radropi.org"
__description__ = "Asteroid and Meteor Detection System Firmware"

try:
    from .main import RadropiSystem
    from .detection_ai import AsteroidDetector
    from .camera_controller import CameraController
    from .gps_module import GPSController, MockGPSController
    from .servo_controller import ServoController, MockServoController
    from .data_logger import DataLogger
    
    __all__ = [
        'RadropiSystem',
        'AsteroidDetector',
        'CameraController',
        'GPSController',
        'MockGPSController',
        'ServoController',
        'MockServoController',
        'DataLogger'
    ]
    
except ImportError as e:
    import logging
    logging.warning(f"Some firmware modules could not be imported: {e}")
    __all__ = []

SYSTEM_INFO = {
    'name': 'Radropi',
    'version': __version__,
    'description': __description__,
    'components': {
        'camera': 'IMX462 Starvis All-Sky Camera',
        'gps': 'Ublox NEO-6M GPS Module',
        'servos': '4x MG995 Servo Motors',
        'processor': 'Raspberry Pi 5 (8GB)',
        'ai_model': 'Custom Asteroid Detection CNN'
    },
    'capabilities': [
        'Real-time asteroid detection',
        'Meteor classification',
        'GPS positioning',
        'Automatic tracking',
        'Data logging',
        'Low-light imaging'
    ]
}

def get_system_info():
    return SYSTEM_INFO.copy()

def check_dependencies():
    dependencies = {
        'opencv': False,
        'numpy': False,
        'pynmea2': False,
        'serial': False,
        'gpio': False
    }
    
    try:
        import cv2
        dependencies['opencv'] = True
    except ImportError:
        pass
    
    try:
        import numpy
        dependencies['numpy'] = True
    except ImportError:
        pass
    
    try:
        import pynmea2
        dependencies['pynmea2'] = True
    except ImportError:
        pass
    
    try:
        import serial
        dependencies['serial'] = True
    except ImportError:
        pass
    
    try:
        import RPi.GPIO
        dependencies['gpio'] = True
    except ImportError:
        pass
    
    return dependencies

def print_banner():
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                         RADROPI v{__version__}                         ║
║              Asteroid and Meteor Detection System           ║
║                                                              ║
║  🌌 Real-time celestial object detection and tracking       ║
║  📡 GPS-enabled astronomical positioning                     ║
║  🤖 AI-powered classification system                         ║
║  📊 Comprehensive data logging and analysis                  ║
║                                                              ║
║  Hardware: Raspberry Pi 5 + IMX462 Camera + GPS + Servos   ║
║  Author: {__author__}                                    ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

if __name__ == "__main__":
    print_banner()
    
    print("\nSystem Information:")
    for key, value in get_system_info().items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        elif isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    - {item}")
        else:
            print(f"  {key}: {value}")
    
    print("\nDependency Check:")
    deps = check_dependencies()
    for dep, available in deps.items():
        status = "✓" if available else "✗"
        print(f"  {status} {dep}")