# Bill of Materials (BOM) - ESP32-S3 Micro Drone Flight Controller

**Revision:** Rev 4.1  
**Total Components:** 83  
**Unique Line Items:** 37  

## Semiconductors & ICs

| Item | Qty | Designators | Part / Value | Package | Description |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 1 | **5** | `D3, D4, D5, D6, D9` | **B5819W-TP** | `D_SOD-123` | 40V 1A Schottky Barrier Rectifier Diode (Motor & Buzzer Flyback Suppression) |
| 2 | **6** | `Q1, Q2, Q3, Q4, Q5, Q6` | **AO3400A** | `SOT-23` | 30V 5.7A N-Channel MOSFET, RDS(on) < 28mOhm (Motor M1-M4, Buzzer, Arm LEDs) |
| 3 | **1** | `U1` | **ESP32-S3-WROOM-1-N8R8** | `ESP32-S3-WROOM-1` | Espressif Dual-Core 240MHz Wi-Fi/BLE Microcontroller Module (PCB Antenna) |
| 4 | **1** | `U2` | **ICM-42688-P** | `LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` | TDK InvenSense 6-Axis MotionTracking IMU (SPI, 32kHz Gyro/Accel, LGA-14) |
| 5 | **1** | `U4` | **TP4056** | `SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm` | 1A Standalone Linear Li-Po Battery Charger (ESOP-8 Thermal Pad) |
| 6 | **1** | `U5` | **AP2112K-3.3TRG1** | `SOT-23-5` | Diodes Inc. 600mA Ultra-Low Dropout LDO 3.3V Regulator (SOT-23-5) |
| 7 | **1** | `U6` | **BMP280** | `Bosch_LGA-8_2x2.5mm_P0.65mm_ClockwisePinNumbering` | Bosch Sensortec High-Precision Barometric Pressure Sensor (I2C/SPI, LGA-8) |

## Passive (Resistors)

| Item | Qty | Designators | Part / Value | Package | Description |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 8 | **2** | `R1, R2` | **5.1k Ohm +/-1% 0603** | `R_0603_1608Metric` | USB Type-C CC1 & CC2 Standard Downstream Port Configuration |
| 9 | **8** | `R3, R4, R9, R11, R13, R15, R31, R40` | **10k Ohm +/-5% 0603** | `R_0603_1608Metric` | MOSFET Gate Pull-Down (Q1-Q6) & ESP32 EN / IO0 Pull-Up |
| 10 | **1** | `R5` | **1.2k Ohm +/-1% 0603** | `R_0603_1608Metric` | TP4056 PROG resistor setting fast charge current = 1000mA (1A) |
| 11 | **5** | `R6, R7, R29, R30, R39` | **1k Ohm +/-5% 0603** | `R_0603_1608Metric` | Status LED current limiter & Buzzer/Arm MOSFET gate resistors |
| 12 | **4** | `R8, R10, R12, R14` | **47 Ohm +/-5% 0603** | `R_0603_1608Metric` | Motor MOSFET gate damping (suppresses high-speed switching ringing & EMI) |
| 13 | **2** | `R26, R27` | **100k Ohm +/-1% 0603** | `R_0603_1608Metric` | Precision Battery Voltage Sense Divider (1/2 scaling to ADC1_CH0 / IO1) |
| 14 | **1** | `R28` | **330 Ohm +/-5% 0603** | `R_0603_1608Metric` | WS2812B DIN Anti-Ringing Signal Damping Resistor |
| 15 | **2** | `R32, R33` | **4.7k Ohm +/-5% 0603** | `R_0603_1608Metric` | I2C Bus SCL (IO9) and SDA (IO8) Pull-Up Resistors |
| 16 | **2** | `R35, R36` | **56 Ohm +/-5% 0603** | `R_0603_1608Metric` | Front White Arm navigation LED current limiters |
| 17 | **2** | `R37, R38` | **120 Ohm +/-5% 0603** | `R_0603_1608Metric` | Rear Red Arm navigation LED current limiters |

## Passive (Capacitors)

| Item | Qty | Designators | Part / Value | Package | Description |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 18 | **3** | `C1, C9, C10` | **10uF 10V X5R/X7R 0603** | `C_0603_1608Metric` | Power rail decoupling (3.3V LDO out & TP4056 VBUS/BAT) |
| 19 | **9** | `C2, C6, C13, C14, C15, C16, C25, C26, C27` | **100nF (0.1uF) 16V X7R 0603** | `C_0603_1608Metric` | High-frequency bypass (ICs) & Motor RC snubbers (C13-C16) |
| 20 | **2** | `C3, C11` | **1.0uF 16V X7R 0603** | `C_0603_1608Metric` | ESP32-S3 EN reset RC delay and LDO input decoupling |
| 21 | **2** | `C7, C12` | **2.2uF 10V X5R/X7R 0603** | `C_0603_1608Metric` | ICM-42688-P VDD charge-pump stabilization cap |
| 22 | **1** | `C24` | **100uF 10V Low-ESR Bulk Capacitor** | `CP_Elec_5x5.3` | High-capacity bulk filter for motor transient voltage suppression |

## Optoelectronics

| Item | Qty | Designators | Part / Value | Package | Description |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 23 | **1** | `D1` | **Red SMD 0603 LED** | `LED_0603_1608Metric` | TP4056 Battery Charging Status Indicator |
| 24 | **1** | `D2` | **Green SMD 0603 LED** | `LED_0603_1608Metric` | TP4056 Battery Standby / Full Charge Indicator |
| 25 | **1** | `D7` | **WS2812B-B/W (5050)** | `LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm` | Intelligent RGB Smart LED (Flight Mode & Diagnostics Indicator, IO48) |
| 26 | **1** | `D8` | **Blue SMD 0603 LED** | `LED_0603_1608Metric` | ESP32-S3 Flight Controller Heartbeat Indicator (IO38) |
| 27 | **2** | `D10, D11` | **White SMD 0603 LED** | `LED_0603_1608Metric` | Front Navigation Headlights (Arm Left & Right) |
| 28 | **2** | `D12, D13` | **Red SMD 0603 LED** | `LED_0603_1608Metric` | Rear Navigation Tail Lights (Arm Left & Right) |

## Audio & Transducers

| Item | Qty | Designators | Part / Value | Package | Description |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 29 | **1** | `BZ1` | **Active 3.7V - 5V Magnetic Buzzer** | `Buzzer_12x9.5RM7.6` | Acoustic Lost-Drone Locator & Low-Battery Alarm Beeper |

## Connectors & Headers

| Item | Qty | Designators | Part / Value | Package | Description |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 30 | **1** | `J1` | **JST-PH S2B-PH-K (2-Pin 2.0mm)** | `JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal` | 1S 3.7V Li-Po Battery JST Input Connector |
| 31 | **1** | `J2` | **TYPE-C-31-M-12 (USB-C 16-Pin)** | `USB_C_Receptacle_HRO_TYPE-C-31-M-12` | USB Type-C Receptacle for Battery Charging & ESP32-S3 USB D+/D- Flashing |
| 32 | **1** | `J3` | **2.54mm Pitch 1x04 Pin Header** | `PinHeader_1x04_P2.54mm_Vertical` | Dedicated RC Receiver Port (3V3, U0TXD, U0RXD, GND) - ELRS / CRSF / SBUS |
| 33 | **4** | `J4, J5, J6, J7` | **1.27mm 1x02 Pin Header / Micro JST Socket** | `PinHeader_1x02_P1.27mm_Vertical` | Motor M1-M4 Quick-Disconnect Sockets (Coreless Brushed) |
| 34 | **1** | `J8` | **1.27mm Pitch 1x04 Micro Pin Header** | `PinHeader_1x04_P1.27mm_Vertical` | Dedicated Micro GPS Module Port (3V3, U1TXD/IO17, U1RXD/IO18, GND) |
| 35 | **1** | `J9` | **1.27mm Pitch 1x02 Micro Header / Solder Pads** | `PinHeader_1x02_P1.27mm_Vertical` | External I2C Magnetometer / Compass Port (SDA/IO8, SCL/IO9) |

## Electromechanical

| Item | Qty | Designators | Part / Value | Package | Description |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 36 | **2** | `SW1, SW2` | **PTS645SMTR92 Tactile Pushbutton** | `SW_SPST_PTS645Sx43SMTR92` | Pushbutton Switch (SW1=Reset / EN, SW2=Boot / IO0) |
| 37 | **1** | `SW3` | **PCM12SMTR Subminiature SPDT Slide Switch** | `SW_SPDT_PCM12` | Master Battery Power ON/OFF Slide Switch |
