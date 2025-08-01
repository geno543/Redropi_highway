# Radropi - Asteroid and Meteor Detection System

## Project Description

Radropi is an advanced astronomical monitoring system designed to detect and classify celestial objects including asteroids and meteors. The system utilizes high-quality cameras and radar detection methods combined with AI models for accurate analysis and classification.

## Why This Project Was Created

With the increasing interest in space debris monitoring and planetary defense, there's a growing need for accessible, cost-effective detection systems. Radropi aims to democratize asteroid and meteor detection by providing a Raspberry Pi-based solution that can be deployed by amateur astronomers, educational institutions, and research facilities.

## System Overview

Radropi consists of two integrated monitoring systems:

1. **Solar Power Monitoring System** - Ensures continuous operation with renewable energy
2. **Asteroid Monitoring System** - Primary detection and classification system

### Classification Categories

The AI model classifies detected objects into three categories:
- **Non-meteor**: Background objects, aircraft, satellites
- **Meteor**: Burning debris entering Earth's atmosphere
- **Asteroid**: Larger rocky bodies in space

### Additional Features

- Shape and size detection for meteors
- Real-time tracking and analysis
- GPS positioning for accurate coordinate logging
- Automatic satellite dish tracking
- Low-light astrophotography capabilities

## Hardware Components

### Main Processing Unit
- Raspberry Pi 5 (8GB) - High-performance computing platform

### Detection Equipment
- IMX462 Starvis All-Sky Camera - Outstanding low-light performance
- Compact Automatic Satellite Dish - Auto-tracking capabilities
- Ublox NEO-6M GPS Module - Precise positioning

### Mechanical Components
- 4x MG995 Servo Motors - Robust tracking mechanisms
- Light Dependent Resistors (LDR) - Environmental sensing

## Project Images

### 3D CAD Model
![3D Assembly](./3D%20Design/Assem1.SLDASM)
*Complete 3D model showing all components integrated*

### PCB Design
![PCB Layout](./PCB/Ras%20pi%20hat/Ras%20pi%20hat/Ras%20pi%20hat.kicad_pcb)
*Custom Raspberry Pi HAT for sensor integration*

### System Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   All-Sky Cam   │────│  Raspberry Pi 5  │────│  Satellite Dish │
└─────────────────┘    │   + Custom HAT   │    └─────────────────┘
                       └──────────────────┘
                              │
                       ┌──────────────────┐
                       │   GPS + Servos   │
                       │   + LDR Sensors  │
                       └──────────────────┘
```

## Bill of Materials

| Item | Quantity | Description | Unit Price (USD) | Purchase Link |
|------|----------|-------------|------------------|---------------|
| Raspberry Pi 5 (8GB) | 1 | Latest flagship board with high performance | $120 | [Raspberry Pi Foundation](https://www.raspberrypi.com/products/raspberry-pi-5/) |
| IMX462 Starvis All-Sky Cam | 1 | Outstanding low-light astrophotography camera | $120 | [AliExpress](https://www.aliexpress.com/item/1005004258249394.html) |
| Compact Automatic Satellite Dish | 1 | Small, vehicle-friendly auto-tracking dish | $130 | [Alibaba](https://www.alibaba.com/showroom/auto-satellite-dish.html) |
| Ublox NEO-6M GPS Module | 1 | Popular hobby GPS with stable performance | $15 | [Amazon](https://www.amazon.com/dp/B01MTU9KDM) |
| MG995 Servo Motor (Full metal gear) | 4 | Robust, high-torque servos, $6 each | $24 | [Amazon](https://www.amazon.com/s?k=mg995+servo) |
| LDR (Light Dependent Resistor, pack) | 1 | Standard 5mm LDRs (10-pack) | $7 | [Amazon](https://www.amazon.com/dp/B07QK4XR98) |
| Project wiring/connectors/dupont kit | 1 | Assorted wires, jumper packs, tools | $15 | [Amazon](https://www.amazon.com/s?k=jumper+wires+kit) |

**Total Estimated Cost: $431 USD**