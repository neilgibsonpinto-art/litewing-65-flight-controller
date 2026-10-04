# LiteWing 65 Micro Drone Flight Controller

An ultra-compact, high-performance flight controller engineered for 65mm diagonal wheelbase brushed micro-quadcopters. Developed by **Neil Gibson Pinto** as part of the hardware engineering internship at **Technical Career Education (TCE)**.

---

## Key Hardware Specifications

* **Microcontroller:** ESP32-S3 Dual-Core Xtensa LX7 @ 240 MHz (512KB SRAM, 8MB Flash, 2.4 GHz Wi-Fi 4 & BLE 5.0 Mesh).
* **Inertial & Environmental Sensing:**
  * **Primary IMU:** 16-bit 6-Axis MotionTracking IMU (ICM-42688-P / BMI270, LGA-14).
  * **Barometric Altimeter:** Bosch Sensortec BMP280 (High-Precision Pressure Sensor, &plusmn;0.12 hPa).
* **Motor Actuation:**
  * 4&times; AO3400A N-Channel MOSFETs (30V, 5.7A continuous, $R_{DS(on)} = 30\,\text{m}\Omega$).
  * 4&times; B5819W Schottky flyback diodes (40V, 1A) + 100nF RC snubbers.
  * Dedicated $0.75\,\text{mm}$ ($30\,\text{mil}$) high-current motor power bus rails.
* **Power & Battery Management:**
  * **Input:** 1S LiPo (3.7V nominal, 4.2V max) via JST-PH 2.0mm connector.
  * **Regulator:** Diodes Inc AP2112K-3.3 (600mA Low-Dropout Regulator, 55mV dropout @ 200mA).
  * **Onboard Charger:** NanJing Top Power TP4056 (1000mA fast-charge via USB Type-C).
  * **Voltage Sensing:** 100k&Omega; / 100k&Omega; precision voltage divider into ESP32 ADC1 Channel 0 (IO1).
* **Audio & Visual Feedback:**
  * Active magnetic piezo buzzer (90dB SPL @ 2.7kHz, driven by AO3400A).
  * Worldsemi WS2812B addressable RGB status indicator LED.
  * Headlight & taillight navigation LEDs.
* **PCB Architecture:**
  * 28 &times; 28 mm central chassis with symmetrical quad-arm layout (65 mm diagonal motor span).
  * 20 &times; 20 mm M2 vibration dampening mount pattern.
  * **222 smooth circular arc tracks** (`PCB_ARC`) eliminating sharp corners and signal reflections.
  * Dual solid ground planes on Top (`F.Cu`) and Bottom (`B.Cu`) with thermal relief spokes.
  * **KiCad 10 DRC Sign-off:** 0 Violations, 0 Unconnected Nets.

---

## Repository Structure

```
├── internship.kicad_sch                    # KiCad 10 Schematic
├── internship.kicad_pcb                    # KiCad 10 PCB Layout (Organic Curved Routing)
├── internship.kicad_pro                    # KiCad 10 Project Configuration
├── LiteWing_65_Engineering_Verification_Report.pdf # 7-Page Hardware Verification & Simulation Report
├── LiteWing_65_Schematic.pdf               # Vector Schematic PDF
├── LiteWing_65_PCB_Layers.pdf              # Multipage PCB Fabrication Layers PDF
├── LiteWing_65_BOM.xlsx                    # Master Bill of Materials (Excel)
├── LiteWing_65_BOM_Grouped.csv             # Grouped BOM for SMT Assembly Ordering
├── LiteWing_65_BOM.csv                     # Raw Schematic Export BOM
├── pcb_3d_turntable.mp4                    # 360-Degree Raytraced 3D Turntable Video
├── pcb_3d_turntable.gif                    # 3D Turntable Animated GIF
├── pcb_curved_top.png                      # High-Resolution Top 3D Render
├── pcb_curved_iso.png                      # High-Resolution Isometric 3D Render
├── pcb_curved_bottom.png                   # High-Resolution Bottom 3D Render
└── README.md                               # Project Overview & Documentation
```

---

## Author & Certification

* **Design Engineer:** Neil Gibson Pinto
* **Institution:** Technical Career Education (TCE) Hardware Engineering Internship
* **Board Revision:** Rev 2.0 (Curved Routing, High-Current Power Bus)
* **Status:** Certified Production Ready &bull; 100% DRC Clean
