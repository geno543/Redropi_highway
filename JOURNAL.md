# Radropi Development Journal

**Total Time Spent: 18.5 hours**

## Project Idea and Motivation

The idea for Radropi came from my fascination with space and the growing concern about near-Earth objects. After reading about recent asteroid discoveries and meteor events, I realized there was a gap in accessible detection systems for amateur astronomers and educational institutions. Most existing systems are either too expensive or too complex for widespread deployment. 
## Project Timeline

### July 24, 2025 - Project Start
**Time Spent: 4 hours**

**Focus: PCB Design and Development**
- Started the Radropi project with initial concept planning
- Began designing the custom Raspberry Pi HAT for sensor integration
- Created initial schematic for connecting all sensors and components
- Worked on component placement and routing optimization
- Established power distribution network for the various sensors

**Progress Made:**
- Initial KiCad project setup
- Component library creation for custom parts
- Basic schematic design with Raspberry Pi 5 interface
- Power management circuit design
---

### July 25, 2025 - Continued Development
**Time Spent: 9 hours**

**Focus: 3D Design and Mechanical Integration**
- Extensive work on 3D CAD modeling using SolidWorks
- Designed mechanical housing for all-sky camera
- Created mounting system for automatic satellite dish
- Developed servo motor mounting brackets
- Integrated GPS module housing with weather protection

**Progress Made:**
- Complete 3D assembly (Assem1.SLDASM) with all components
- Mechanical stress analysis for outdoor deployment
- Weather-resistant enclosure design
- Cable management and routing solutions
- Mounting hardware specifications

**Key Design Decisions:**
- Modular design for easy maintenance and upgrades
- IP65 rating for outdoor weather resistance
- Tool-free assembly for field deployment
- Integrated cable management to prevent tangling

---

### July 26, 2025 - Documentation and BOM
**Time Spent: 0.5 hours**

**Focus: Bill of Materials Creation**
- Finalized component selection and sourcing
- Created comprehensive BOM with supplier links
- Cost optimization and alternative component research
- Verified component compatibility and availability

**Progress Made:**
- Complete BOM.csv with pricing and links
- Component specifications verification
- Supply chain risk assessment
- Cost analysis and budget planning

---

### July 27, 2025 - Firmware Development
**Time Spent: 5 hours**

**Focus: Software Architecture and Implementation**
- Designed modular firmware architecture for the detection system
- Implemented main control system with threading for concurrent operations
- Developed AI detection algorithms using OpenCV and background subtraction
- Created camera controller for IMX462 with low-light optimizations
- Built GPS module interface for positioning and timing
- Implemented servo controller for precise tracking movements
- Designed comprehensive data logging system for detection events

**Progress Made:**
- Complete Python firmware package with 7 modules
- Main system controller with graceful shutdown handling
- AI detection with three-category classification
- Camera interface with CLAHE enhancement for low-light
- GPS controller with NMEA parsing and mock mode
- Servo controller supporting 4 motors with smooth movement
- Data logger with CSV export and image annotation
- Requirements file with all dependencies

**Technical Decisions:**
- Used threading for concurrent camera capture and detection
- Implemented mock controllers for testing without hardware
- Added comprehensive error handling and logging
- Designed modular architecture for easy maintenance
- Included background subtraction for motion detection

---

## Development Photos and Progress

### PCB Development (July 24)
![PCB Schematic Progress](./PCB/Ras%20pi%20hat/Ras%20pi%20hat/Ras%20pi%20hat.kicad_sch)
*Initial schematic design showing sensor integration*

![PCB Layout](./PCB/Ras%20pi%20hat/Ras%20pi%20hat/Ras%20pi%20hat.kicad_pcb)
*Final PCB layout with optimized routing*

### 3D Design Progress (July 25)
![3D Assembly](./3D%20Design/Assem1.SLDASM)
*Complete mechanical assembly with all components*

![STEP Model](./PCB/Ras%20pi%20hat/Ras%20pi%20hat/Ras%20pi%20hat.step)
*3D model of the custom PCB for integration verification*

