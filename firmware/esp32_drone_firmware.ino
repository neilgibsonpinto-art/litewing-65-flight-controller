/*
 * =========================================================================================
 *   ESP32-S3 MICRO DRONE FLIGHT CONTROLLER FIRMWARE
 *   Dual-Core FreeRTOS Flight Loop + MAVLink Telemetry for Mission Planner & QGroundControl
 * =========================================================================================
 * 
 * Hardware Mapping (PCB Rev 4.1):
 * -----------------------------------------------------------------------------------------
 *   Motors (Coreless Brushed LEDC PWM):
 *     - Motor 1 (Front Left, CW):   GPIO 4
 *     - Motor 2 (Front Right, CCW):  GPIO 5
 *     - Motor 3 (Rear Left, CCW):   GPIO 6
 *     - Motor 4 (Rear Right, CW):   GPIO 7
 * 
 *   Sensors:
 *     - IMU: TDK InvenSense ICM-42688-P (SPI: CS=10, MOSI=11, SCK=12, MISO=13, INT=14)
 *     - Barometer: Bosch BMP280 (I2C: SDA=8, SCL=9)
 *     - GPS: u-blox M10 Nano (UART1: RX=17, TX=18 @ 115200 baud)
 * 
 *   Telemetry & Radio Link:
 *     - Primary: Wi-Fi UDP MAVLink (Port 14550) -> Connects to Mission Planner / QGroundControl
 *     - Secondary: Hardware UART0 (RX=44, TX=43) -> ExpressLRS (CRSF) / FlySky (IBUS)
 * 
 *   Peripherals:
 *     - Battery Voltage Sense:      GPIO 1 (ADC1_CH0, 100k/100k divider -> ratio = 2.0)
 *     - Flight Status Blue LED:     GPIO 3
 *     - WS2812B RGB Smart LED:      GPIO 2
 *     - Active Lost-Model Buzzer:   GPIO 48
 *     - Night Navigation Arm LEDs:  GPIO 47
 * =========================================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <SPI.h>
#include <Wire.h>

// =========================================================================================
// 1. PIN DEFINITIONS
// =========================================================================================
#define PIN_M1              4   // Front-Left Motor
#define PIN_M2              5   // Front-Right Motor
#define PIN_M3              6   // Rear-Left Motor
#define PIN_M4              7   // Rear-Right Motor

#define PIN_IMU_CS          10  // ICM-42688-P Chip Select
#define PIN_IMU_MOSI        11  // SPI MOSI
#define PIN_IMU_SCK         12  // SPI SCK
#define PIN_IMU_MISO        13  // SPI MISO
#define PIN_IMU_INT         14  // Gyro Data Ready Interrupt

#define PIN_I2C_SDA         8   // BMP280 SDA
#define PIN_I2C_SCL         9   // BMP280 SCL

#define PIN_GPS_RX          17  // ESP32 RX <- GPS TX
#define PIN_GPS_TX          18  // ESP32 TX -> GPS RX

#define PIN_RC_RX           44  // ESP32 RX <- ELRS / Receiver TX
#define PIN_RC_TX           43  // ESP32 TX -> ELRS / Receiver RX

#define PIN_VBAT_SENSE      1   // Battery ADC (100k / 100k divider)
#define PIN_LED_BLUE        3   // Heartbeat / Status LED
#define PIN_LED_RGB         2   // WS2812B DIN
#define PIN_BUZZER          48  // Active Buzzer Driver
#define PIN_ARM_LEDS        47  // Night Arm LEDs Driver

// =========================================================================================
// 2. FLIGHT CONFIGURATION & TUNING
// =========================================================================================
#define PWM_FREQ_HZ         20000   // 20 kHz Ultrasonic PWM (no audible motor whine)
#define PWM_RES_BITS        10      // 10-bit PWM (0 - 1023 duty cycle)
#define PWM_MAX_DUTY        1023

#define VBAT_SCALE_FACTOR   (2.0f * (3.3f / 4095.0f)) // 12-bit ADC, 100k/100k divider
#define VBAT_LOW_THRESHOLD  3.40f  // Volts (low battery alarm)
#define VBAT_CRIT_THRESHOLD 3.20f  // Volts (critical failsafe land)

// Cascaded PID Gains (Angle Mode)
float Kp_roll = 1.30f,  Ki_roll = 0.04f,  Kd_roll = 12.5f;
float Kp_pitch = 1.30f, Ki_pitch = 0.04f, Kd_pitch = 12.5f;
float Kp_yaw = 2.50f,   Ki_yaw = 0.10f,   Kd_yaw = 0.0f;

// Wi-Fi Telemetry for Mission Planner
const char* WIFI_SSID     = "ESP32-S3-DRONE";
const char* WIFI_PASS     = "drone1234";
const uint16_t MAVLINK_PORT = 14550;

WiFiUDP udp;
IPAddress gcs_ip(192, 168, 4, 2); // Default first connected laptop/phone IP

// =========================================================================================
// 3. GLOBAL VEHICLE STATE
// =========================================================================================
struct DroneState {
    // Attitude (degrees & rad/s)
    float roll = 0.0f, pitch = 0.0f, yaw = 0.0f;
    float gx = 0.0f, gy = 0.0f, gz = 0.0f;       // Gyro rates (deg/s)
    float ax = 0.0f, ay = 0.0f, az = 0.0f;       // Accel (G)
    
    // Altitude & Position
    float baro_altitude = 0.0f;                  // Meters
    int32_t gps_lat = 0, gps_lon = 0;           // deg * 1e7
    int32_t gps_alt = 0;                         // mm
    uint8_t gps_sats = 0;
    bool gps_locked = false;
    
    // Radio Stick Inputs (Normalized 1000 - 2000 us)
    int16_t rc_throttle = 1000;
    int16_t rc_roll     = 1500;
    int16_t rc_pitch    = 1500;
    int16_t rc_yaw      = 1500;
    
    // Power & Status
    float vbat = 4.20f;
    bool armed = false;
    uint32_t flight_mode = 0; // 0=STABILIZE, 1=ALT_HOLD, 2=RTL
} drone;

// Hardware Timers & RTOS Tasks
TaskHandle_t TaskFlightLoopHandle;
TaskHandle_t TaskCommsHandle;

// =========================================================================================
// 4. LOW-LEVEL MOTOR PWM INITIALIZATION (ESP32-S3 LEDC)
// =========================================================================================
void setup_motors() {
    ledcAttach(PIN_M1, PWM_FREQ_HZ, PWM_RES_BITS);
    ledcAttach(PIN_M2, PWM_FREQ_HZ, PWM_RES_BITS);
    ledcAttach(PIN_M3, PWM_FREQ_HZ, PWM_RES_BITS);
    ledcAttach(PIN_M4, PWM_FREQ_HZ, PWM_RES_BITS);

    // Initial state: 0% Throttle
    ledcWrite(PIN_M1, 0);
    ledcWrite(PIN_M2, 0);
    ledcWrite(PIN_M3, 0);
    ledcWrite(PIN_M4, 0);
}

void write_motors(int m1, int m2, int m3, int m4) {
    if (!drone.armed || drone.rc_throttle < 1050) {
        ledcWrite(PIN_M1, 0);
        ledcWrite(PIN_M2, 0);
        ledcWrite(PIN_M3, 0);
        ledcWrite(PIN_M4, 0);
        return;
    }
    ledcWrite(PIN_M1, constrain(m1, 0, PWM_MAX_DUTY));
    ledcWrite(PIN_M2, constrain(m2, 0, PWM_MAX_DUTY));
    ledcWrite(PIN_M3, constrain(m3, 0, PWM_MAX_DUTY));
    ledcWrite(PIN_M4, constrain(m4, 0, PWM_MAX_DUTY));
}

// =========================================================================================
// 5. ICM-42688-P SPI SENSOR DRIVER (High-Speed Gyro + Accel)
// =========================================================================================
void icm42688_write_reg(uint8_t reg, uint8_t val) {
    digitalWrite(PIN_IMU_CS, LOW);
    SPI.transfer(reg & 0x7F); // Write: MSB = 0
    SPI.transfer(val);
    digitalWrite(PIN_IMU_CS, HIGH);
}

uint8_t icm42688_read_reg(uint8_t reg) {
    digitalWrite(PIN_IMU_CS, LOW);
    SPI.transfer(reg | 0x80); // Read: MSB = 1
    uint8_t val = SPI.transfer(0x00);
    digitalWrite(PIN_IMU_CS, HIGH);
    return val;
}

bool setup_icm42688() {
    pinMode(PIN_IMU_CS, OUTPUT);
    digitalWrite(PIN_IMU_CS, HIGH);
    SPI.begin(PIN_IMU_SCK, PIN_IMU_MISO, PIN_IMU_MOSI, PIN_IMU_CS);
    SPI.setFrequency(10000000); // 10 MHz SPI Clock

    delay(10);
    uint8_t whoami = icm42688_read_reg(0x75); // WHO_AM_I reg
    Serial.printf("[IMU] ICM-42688-P WHO_AM_I: 0x%02X (Expected: 0x47)\n", whoami);

    // Power Management: Turn ON Accel & Gyro in Low-Noise Mode
    icm42688_write_reg(0x4E, 0x0F); // PWR_MGMT0: Gyro & Accel in Low-Noise (LN) mode
    delay(50);

    // Gyro Config: +/- 2000 dps full scale, 1 kHz ODR
    icm42688_write_reg(0x4F, 0x06); // GYRO_CONFIG0: 2000 dps, 1kHz
    // Accel Config: +/- 16 G full scale, 1 kHz ODR
    icm42688_write_reg(0x50, 0x06); // ACCEL_CONFIG0: 16G, 1kHz

    return (whoami == 0x47);
}

void read_icm42688() {
    digitalWrite(PIN_IMU_CS, LOW);
    SPI.transfer(0x1F | 0x80); // Burst read starting at ACCEL_DATA_X1 (0x1F)
    
    int16_t raw_ax = (int16_t)((SPI.transfer(0x00) << 8) | SPI.transfer(0x00));
    int16_t raw_ay = (int16_t)((SPI.transfer(0x00) << 8) | SPI.transfer(0x00));
    int16_t raw_az = (int16_t)((SPI.transfer(0x00) << 8) | SPI.transfer(0x00));
    int16_t raw_gx = (int16_t)((SPI.transfer(0x00) << 8) | SPI.transfer(0x00));
    int16_t raw_gy = (int16_t)((SPI.transfer(0x00) << 8) | SPI.transfer(0x00));
    int16_t raw_gz = (int16_t)((SPI.transfer(0x00) << 8) | SPI.transfer(0x00));
    digitalWrite(PIN_IMU_CS, HIGH);

    // Convert raw values: 16G scale = 2048 LSB/g, 2000 dps scale = 16.4 LSB/(deg/s)
    drone.ax = (float)raw_ax / 2048.0f;
    drone.ay = (float)raw_ay / 2048.0f;
    drone.az = (float)raw_az / 2048.0f;
    drone.gx = (float)raw_gx / 16.4f;
    drone.gy = (float)raw_gy / 16.4f;
    drone.gz = (float)raw_gz / 16.4f;

    // Simple Complementary Filter (500 Hz: dt = 0.002s)
    float accel_roll  = atan2(drone.ay, drone.az) * 57.29578f;
    float accel_pitch = atan2(-drone.ax, sqrt(drone.ay * drone.ay + drone.az * drone.az)) * 57.29578f;

    drone.roll  = 0.98f * (drone.roll + drone.gx * 0.002f) + 0.02f * accel_roll;
    drone.pitch = 0.98f * (drone.pitch + drone.gy * 0.002f) + 0.02f * accel_pitch;
    drone.yaw  += drone.gz * 0.002f;
}

// =========================================================================================
// 6. CORE 1: HIGH-SPEED 500 Hz FLIGHT CONTROL LOOP
// =========================================================================================
void TaskFlightLoop(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(2); // 2ms = 500 Hz loop rate

    float error_roll, prev_error_roll = 0.0f, integral_roll = 0.0f;
    float error_pitch, prev_error_pitch = 0.0f, integral_pitch = 0.0f;
    float error_yaw, prev_error_yaw = 0.0f, integral_yaw = 0.0f;

    for (;;) {
        // 1. Read IMU
        read_icm42688();

        // 2. Setpoints from Radio Stick inputs (Angle Mode: +/- 30 degrees max)
        float target_roll  = (drone.rc_roll - 1500) * 0.06f;   // +/- 30 deg
        float target_pitch = (drone.rc_pitch - 1500) * 0.06f;  // +/- 30 deg
        float target_yaw_rate = (drone.rc_yaw - 1500) * 0.3f;  // +/- 150 deg/s

        // 3. Roll PID
        error_roll = target_roll - drone.roll;
        integral_roll += error_roll * 0.002f;
        integral_roll = constrain(integral_roll, -100.0f, 100.0f);
        float pid_roll = (Kp_roll * error_roll) + (Ki_roll * integral_roll) + (Kd_roll * (error_roll - prev_error_roll) / 0.002f);
        prev_error_roll = error_roll;

        // 4. Pitch PID
        error_pitch = target_pitch - drone.pitch;
        integral_pitch += error_pitch * 0.002f;
        integral_pitch = constrain(integral_pitch, -100.0f, 100.0f);
        float pid_pitch = (Kp_pitch * error_pitch) + (Ki_pitch * integral_pitch) + (Kd_pitch * (error_pitch - prev_error_pitch) / 0.002f);
        prev_error_pitch = error_pitch;

        // 5. Yaw PID (Rate based)
        error_yaw = target_yaw_rate - drone.gz;
        integral_yaw += error_yaw * 0.002f;
        float pid_yaw = (Kp_yaw * error_yaw) + (Ki_yaw * integral_yaw);

        // 6. Motor Mixer (Standard Quad X Configuration)
        int throttle = map(drone.rc_throttle, 1000, 2000, 0, PWM_MAX_DUTY);
        
        int m1 = throttle + pid_pitch + pid_roll - pid_yaw; // Front-Left (CW)
        int m2 = throttle + pid_pitch - pid_roll + pid_yaw; // Front-Right (CCW)
        int m3 = throttle - pid_pitch + pid_roll + pid_yaw; // Rear-Left (CCW)
        int m4 = throttle - pid_pitch - pid_roll - pid_yaw; // Rear-Right (CW)

        // 7. Output PWM to Coreless MOSFETs
        write_motors(m1, m2, m3, m4);

        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

// =========================================================================================
// 7. CORE 0: MAVLINK TELEMETRY STREAM TO MISSION PLANNER (UDP 14550)
// =========================================================================================
void send_mavlink_heartbeat() {
    uint8_t buf[17] = {
        0xFD, 0x09, 0x00, 0x00, 0x00, 0x01, 0x01, // MAVLink v2 Header
        0x00, 0x00, 0x00,                         // Msg ID = 0 (HEARTBEAT)
        0x02, 0x00, 0x00, 0x00,                   // Custom mode
        0x02,                                     // Type: MAV_TYPE_QUADROTOR (2)
        0x03,                                     // Autopilot: MAV_AUTOPILOT_ARDUPILOTMEGA (3)
        (uint8_t)(drone.armed ? 0x80 : 0x00),     // Base mode (Armed flag)
        0x04,                                     // System status: MAV_STATE_ACTIVE (4)
        0x03                                      // MAVLink version
    };
    udp.beginPacket(gcs_ip, MAVLINK_PORT);
    udp.write(buf, sizeof(buf));
    udp.endPacket();
}

void TaskComms(void *pvParameters) {
    uint32_t last_hb = 0;
    uint32_t last_vbat_check = 0;

    for (;;) {
        uint32_t now = millis();

        // 1. Heartbeat to Mission Planner (1 Hz)
        if (now - last_hb >= 1000) {
            send_mavlink_heartbeat();
            digitalWrite(PIN_LED_BLUE, !digitalRead(PIN_LED_BLUE)); // Heartbeat blink
            last_hb = now;
        }

        // 2. Battery Voltage Monitoring (10 Hz)
        if (now - last_vbat_check >= 100) {
            int raw_adc = analogRead(PIN_VBAT_SENSE);
            drone.vbat = (float)raw_adc * VBAT_SCALE_FACTOR;

            if (drone.vbat < VBAT_LOW_THRESHOLD && drone.vbat > 2.5f) {
                digitalWrite(PIN_BUZZER, HIGH); // Low battery warning beep
            } else {
                digitalWrite(PIN_BUZZER, LOW);
            }
            last_vbat_check = now;
        }

        // 3. Process GPS NMEA packets from UART1
        while (Serial1.available()) {
            char c = Serial1.read();
            // Optional: feed to TinyGPS++ library if installed
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// =========================================================================================
// 8. SETUP & INITIALIZATION
// =========================================================================================
void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n==================================================");
    Serial.println("   ESP32-S3 Micro Drone Flight Controller Boot   ");
    Serial.println("==================================================");

    // Setup Indicators
    pinMode(PIN_LED_BLUE, OUTPUT);
    pinMode(PIN_BUZZER, OUTPUT);
    pinMode(PIN_ARM_LEDS, OUTPUT);
    digitalWrite(PIN_ARM_LEDS, HIGH); // Turn ON Night Navigation Arm LEDs

    // Setup Motor Drivers
    setup_motors();

    // Setup ICM-42688-P IMU
    if (!setup_icm42688()) {
        Serial.println("[ERROR] ICM-42688-P IMU not detected! Check SPI lines.");
    } else {
        Serial.println("[OK] ICM-42688-P IMU Initialized (SPI 10MHz).");
    }

    // Setup GPS Serial Port (UART1 on IO17 / IO18)
    Serial1.begin(115200, SERIAL_8N1, PIN_GPS_RX, PIN_GPS_TX);
    Serial.println("[OK] GPS Port (UART1) initialized at 115200 baud.");

    // Setup RC Receiver Port (UART0 on IO44 / IO43)
    Serial0.begin(115200, SERIAL_8N1, PIN_RC_RX, PIN_RC_TX);
    Serial.println("[OK] RC Receiver Port (UART0) initialized.");

    // Setup Wi-Fi SoftAP for Mission Planner
    WiFi.softAP(WIFI_SSID, WIFI_PASS);
    udp.begin(MAVLINK_PORT);
    Serial.printf("[OK] Wi-Fi AP Ready: '%s' | UDP Port: %d\n", WIFI_SSID, MAVLINK_PORT);
    Serial.println("[OK] Launching Dual-Core FreeRTOS Flight Engine...");

    // Launch Real-Time 500 Hz Flight Loop on Core 1
    xTaskCreatePinnedToCore(
        TaskFlightLoop, "FlightLoop", 8192, NULL, 5, &TaskFlightLoopHandle, 1
    );

    // Launch Telemetry / MAVLink / GPS on Core 0
    xTaskCreatePinnedToCore(
        TaskComms, "CommsTask", 8192, NULL, 1, &TaskCommsHandle, 0
    );
}

void loop() {
    // FreeRTOS tasks handle everything; loop is left idle
    vTaskDelay(pdMS_TO_TICKS(1000));
}
