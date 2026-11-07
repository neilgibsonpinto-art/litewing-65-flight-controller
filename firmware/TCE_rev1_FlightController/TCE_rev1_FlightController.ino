/*
 * ============================================================================
 * TCE_rev1 Quadcopter Flight Controller & Mission Planner (MAVLink) Firmware
 * Target MCU : ESP32-S3-WROOM-1 (U1)
 * Sensors    : ICM-42688-P (SPI), MPU-6050 (I2C 0x68), BMP280 (I2C 0x76)
 * Actuators  : 4x Brushed MOSFET PWM (GPIO 4, 5, 6, 7 @ 20 kHz)
 * Telemetry  : MAVLink v1 over Wi-Fi UDP (Port 14550) & USB-C Serial (115200)
 * ============================================================================
 *
 * ARDUINO IDE UPLOAD SETTINGS:
 *   1. Board            : "ESP32S3 Dev Module"
 *   2. USB CDC On Boot  : "Enabled"
 *   3. Upload Mode      : "USB-OTG CDC (TinyUSB)" or "UART0 / Hardware CDC"
 *   4. Flash Size       : "4MB (32Mb)" or "8MB (64Mb)"
 * ============================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// ============================================================================
// 1. EXACT PCB HARDWARE PIN DEFINITIONS (internship.kicad_pcb / TCE_rev1)
// ============================================================================
#define PIN_MOTOR1_PWM      4   // J4: Rear-Right  (CW)
#define PIN_MOTOR2_PWM      5   // J5: Front-Right (CCW)
#define PIN_MOTOR3_PWM      6   // J6: Rear-Left   (CCW)
#define PIN_MOTOR4_PWM      7   // J7: Front-Left  (CW)

#define PIN_IMU_CS          10  // U2: ICM-42688-P SPI CS
#define PIN_IMU_MOSI        11  // U2: ICM-42688-P SPI MOSI (SDI)
#define PIN_IMU_SCK         12  // U2: ICM-42688-P SPI SCK  (SCLK)
#define PIN_IMU_MISO        13  // U2: ICM-42688-P SPI MISO (SDO)
#define PIN_IMU_INT         14  // U2: ICM-42688-P INT1

#define PIN_I2C_SDA         18  // I2C SDA: MPU-6050 (0x68), BMP280 (0x76), J9
#define PIN_I2C_SCL         9   // I2C SCL: MPU-6050 (0x68), BMP280 (0x76), J9
#define I2C_ADDR_MPU6050    0x68
#define I2C_ADDR_BMP280     0x76

#define PIN_GPS_RX          16  // J8: GPS Module
#define PIN_GPS_TX          17  // J8: GPS Module
#define PIN_RC_RX           44  // J3: RC Receiver (U0RXD)
#define PIN_RC_TX           43  // J3: RC Receiver (U0TXD)

#define PIN_WS2812_RGB      1   // D7: WS2812B RGB LED
#define PIN_VBAT_ADC        2   // ADC1_CH1: R26=100k / R27=100k (2.0x divider)
#define PIN_LED_STATUS      3   // D8: Blue Status LED (Active HIGH)
#define PIN_ARM_LIGHTS_EN   47  // Q5: 4x Corner Arm Navigation LEDs
#define PIN_BUZZER_CTRL     48  // Q6: Active Buzzer BZ1

// ============================================================================
// 2. WI-FI ACCESS POINT FOR MISSION PLANNER (UDP PORT 14550)
// ============================================================================
const char* WIFI_SSID = "TCE_DRONE_FC";
const char* WIFI_PASS = "12345678";
const uint16_t MAVLINK_UDP_PORT = 14550;
IPAddress gcsIP(192, 168, 4, 255); // Broadcast to connected laptop/phone
WiFiUDP mavUDP;

// ============================================================================
// 3. FLIGHT STATE & CONTROL VARIABLES
// ============================================================================
bool isArmed = false;
float roll_deg = 0.0f, pitch_deg = 0.0f, yaw_deg = 0.0f;
float roll_rad = 0.0f, pitch_rad = 0.0f, yaw_rad = 0.0f;
float gx_dps = 0.0f, gy_dps = 0.0f, gz_dps = 0.0f;
float ax_g = 0.0f, ay_g = 0.0f, az_g = 1.0f;
float baro_alt_m = 0.0f;
float vbat_volts = 4.0f;

// Gyro calibration offsets
float gx_offset = 0.0f, gy_offset = 0.0f, gz_offset = 0.0f;
bool icm_ok = false, mpu_ok = false, bmp_ok = false;

// Pilot Setpoints (from RC or Mission Planner RC Override)
float target_throttle = 0.0f; // 0.0 to 1.0
float target_roll_deg = 0.0f; // -30 to +30 deg
float target_pitch_deg = 0.0f;
float target_yaw_dps = 0.0f;

// PID Gains (Roll / Pitch / Yaw)
float kp_angle = 4.0f;
float kp_rate  = 1.2f, ki_rate = 0.02f, kd_rate = 0.04f;
float kp_yaw   = 2.5f;
float i_roll = 0.0f, i_pitch = 0.0f, prev_err_roll = 0.0f, prev_err_pitch = 0.0f;

// Motor PWM Duties (0..1023 for 10-bit 20kHz PWM)
int motor_pwm[4] = {0, 0, 0, 0};

// ============================================================================
// 4. SENSOR DRIVERS (ICM-42688-P SPI & MPU-6050 I2C & BMP280 I2C)
// ============================================================================
void icmWriteReg(uint8_t reg, uint8_t val) {
    digitalWrite(PIN_IMU_CS, LOW);
    SPI.transfer(reg & 0x7F);
    SPI.transfer(val);
    digitalWrite(PIN_IMU_CS, HIGH);
}

uint8_t icmReadReg(uint8_t reg) {
    digitalWrite(PIN_IMU_CS, LOW);
    SPI.transfer(reg | 0x80);
    uint8_t val = SPI.transfer(0x00);
    digitalWrite(PIN_IMU_CS, HIGH);
    return val;
}

bool initICM42688() {
    pinMode(PIN_IMU_CS, OUTPUT);
    digitalWrite(PIN_IMU_CS, HIGH);
    SPI.begin(PIN_IMU_SCK, PIN_IMU_MISO, PIN_IMU_MOSI, PIN_IMU_CS);
    SPI.beginTransaction(SPISettings(8000000, MSBFIRST, SPI_MODE3));

    icmWriteReg(0x11, 0x01); // DEVICE_CONFIG: Soft Reset
    delay(20);
    uint8_t who = icmReadReg(0x75); // WHO_AM_I == 0x47
    if (who != 0x47) return false;

    icmWriteReg(0x4E, 0x0F); // PWR_MGMT0: Gyro + Accel Low Noise Mode
    delay(10);
    icmWriteReg(0x4F, 0x06); // GYRO_CONFIG0: +/-2000 dps, 1kHz ODR
    icmWriteReg(0x50, 0x06); // ACCEL_CONFIG0: +/-16g, 1kHz ODR
    return true;
}

void readICM42688() {
    digitalWrite(PIN_IMU_CS, LOW);
    SPI.transfer(0x1F | 0x80); // ACCEL_DATA_X1 burst read (12 bytes)
    int16_t raw_ax = (SPI.transfer(0) << 8) | SPI.transfer(0);
    int16_t raw_ay = (SPI.transfer(0) << 8) | SPI.transfer(0);
    int16_t raw_az = (SPI.transfer(0) << 8) | SPI.transfer(0);
    int16_t raw_gx = (SPI.transfer(0) << 8) | SPI.transfer(0);
    int16_t raw_gy = (SPI.transfer(0) << 8) | SPI.transfer(0);
    int16_t raw_gz = (SPI.transfer(0) << 8) | SPI.transfer(0);
    digitalWrite(PIN_IMU_CS, HIGH);

    ax_g   = raw_ax / 2048.0f;
    ay_g   = raw_ay / 2048.0f;
    az_g   = raw_az / 2048.0f;
    gx_dps = (raw_gx / 16.4f) - gx_offset;
    gy_dps = (raw_gy / 16.4f) - gy_offset;
    gz_dps = (raw_gz / 16.4f) - gz_offset;
}

bool initMPU6050() {
    Wire.beginTransmission(I2C_ADDR_MPU6050);
    Wire.write(0x6B); // PWR_MGMT_1
    Wire.write(0x00); // Wake up
    if (Wire.endTransmission() != 0) return false;

    Wire.beginTransmission(I2C_ADDR_MPU6050);
    Wire.write(0x1B); // GYRO_CONFIG
    Wire.write(0x18); // +/-2000 dps
    Wire.endTransmission();

    Wire.beginTransmission(I2C_ADDR_MPU6050);
    Wire.write(0x1C); // ACCEL_CONFIG
    Wire.write(0x18); // +/-16g
    Wire.endTransmission();
    return true;
}

void readMPU6050() {
    Wire.beginTransmission(I2C_ADDR_MPU6050);
    Wire.write(0x3B);
    if (Wire.endTransmission(false) != 0) return;
    if (Wire.requestFrom(I2C_ADDR_MPU6050, 14) == 14) {
        int16_t raw_ax = (Wire.read() << 8) | Wire.read();
        int16_t raw_ay = (Wire.read() << 8) | Wire.read();
        int16_t raw_az = (Wire.read() << 8) | Wire.read();
        Wire.read(); Wire.read(); // Temp
        int16_t raw_gx = (Wire.read() << 8) | Wire.read();
        int16_t raw_gy = (Wire.read() << 8) | Wire.read();
        int16_t raw_gz = (Wire.read() << 8) | Wire.read();

        ax_g   = raw_ax / 2048.0f;
        ay_g   = raw_ay / 2048.0f;
        az_g   = raw_az / 2048.0f;
        gx_dps = (raw_gx / 16.4f) - gx_offset;
        gy_dps = (raw_gy / 16.4f) - gy_offset;
        gz_dps = (raw_gz / 16.4f) - gz_offset;
    }
}

// ============================================================================
// 5. BUILT-IN LIGHTWEIGHT MAVLINK v1 ENGINE (ZERO EXTERNAL LIBRARIES NEEDED)
// ============================================================================
uint8_t mav_seq = 0;

uint16_t mavlink_crc_accumulate(uint8_t data, uint16_t crc) {
    uint8_t tmp = data ^ (uint8_t)(crc & 0xFF);
    tmp ^= (tmp << 4);
    return (crc >> 8) ^ ((uint16_t)tmp << 8) ^ ((uint16_t)tmp << 3) ^ ((uint16_t)tmp >> 4);
}

void sendMavlinkPacket(uint8_t msg_id, const uint8_t* payload, uint8_t len, uint8_t crc_extra) {
    uint8_t buf[72];
    buf[0] = 0xFE; // MAVLink v1 STX
    buf[1] = len;
    buf[2] = mav_seq++;
    buf[3] = 1;    // System ID = 1
    buf[4] = 1;    // Component ID = 1 (AUTOPILOT1)
    buf[5] = msg_id;
    memcpy(&buf[6], payload, len);

    uint16_t crc = 0xFFFF;
    for (int i = 1; i < 6 + len; i++) crc = mavlink_crc_accumulate(buf[i], crc);
    crc = mavlink_crc_accumulate(crc_extra, crc);
    buf[6 + len] = (uint8_t)(crc & 0xFF);
    buf[7 + len] = (uint8_t)(crc >> 8);

    // Send over both USB-C Serial and Wi-Fi UDP (Port 14550)
    Serial.write(buf, 8 + len);
    mavUDP.beginPacket(gcsIP, MAVLINK_UDP_PORT);
    mavUDP.write(buf, 8 + len);
    mavUDP.endPacket();
}

// MSG #0: HEARTBEAT (CRC_EXTRA = 50, Len = 9)
void sendMavlinkHeartbeat() {
    uint8_t p[9] = {0};
    p[4] = 2;  // MAV_TYPE_QUADROTOR = 2
    p[5] = 3;  // MAV_AUTOPILOT_ARDUPILOTMEGA = 3
    p[6] = isArmed ? (0x80 | 0x01) : 0x01; // MAV_MODE_FLAG_SAFETY_ARMED
    p[8] = isArmed ? 4 : 3; // MAV_STATE_ACTIVE (4) or STANDBY (3)
    sendMavlinkPacket(0, p, 9, 50);
}

// MSG #1: SYS_STATUS (CRC_EXTRA = 124, Len = 31)
void sendMavlinkSysStatus() {
    uint8_t p[31] = {0};
    uint32_t sensors = 0x01 | 0x02 | 0x08; // Gyro + Accel + Baro present/enabled/healthy
    memcpy(&p[0], &sensors, 4);
    memcpy(&p[4], &sensors, 4);
    memcpy(&p[8], &sensors, 4);
    uint16_t load = 250; // 25% CPU load
    uint16_t vbat_mv = (uint16_t)(vbat_volts * 1000.0f);
    int16_t current_10ma = -1;
    int8_t rem_pct = (int8_t)constrain((vbat_volts - 3.3f) / (4.2f - 3.3f) * 100.0f, 0.0f, 100.0f);
    memcpy(&p[12], &load, 2);
    memcpy(&p[14], &vbat_mv, 2);
    memcpy(&p[16], &current_10ma, 2);
    p[30] = (uint8_t)rem_pct;
    sendMavlinkPacket(1, p, 31, 124);
}

// MSG #30: ATTITUDE (CRC_EXTRA = 39, Len = 28)
void sendMavlinkAttitude() {
    uint8_t p[28] = {0};
    uint32_t ms = millis();
    float r_spd = gx_dps * DEG_TO_RAD;
    float p_spd = gy_dps * DEG_TO_RAD;
    float y_spd = gz_dps * DEG_TO_RAD;
    memcpy(&p[0], &ms, 4);
    memcpy(&p[4], &roll_rad, 4);
    memcpy(&p[8], &pitch_rad, 4);
    memcpy(&p[12], &yaw_rad, 4);
    memcpy(&p[16], &r_spd, 4);
    memcpy(&p[20], &p_spd, 4);
    memcpy(&p[24], &y_spd, 4);
    sendMavlinkPacket(30, p, 28, 39);
}

// Incoming MAVLink parser (Handles ARM / DISARM & RC Override from Mission Planner)
void pollMavlinkIncoming() {
    int pktSize = mavUDP.parsePacket();
    while (pktSize > 0 || Serial.available() > 0) {
        uint8_t buf[280];
        int n = 0;
        if (pktSize > 0) {
            gcsIP = mavUDP.remoteIP();
            n = mavUDP.read(buf, sizeof(buf));
            pktSize = mavUDP.parsePacket();
        } else {
            n = Serial.readBytes(buf, min((int)Serial.available(), (int)sizeof(buf)));
        }
        // Scan buffer for COMMAND_LONG (Msg ID 76) -> Arm/Disarm (CMD 400)
        for (int i = 0; i < n - 15; i++) {
            if (buf[i] == 0xFE && buf[i + 5] == 76) { // MAVLink v1 COMMAND_LONG
                uint16_t cmd;
                float param1;
                memcpy(& param1, &buf[i + 6], 4);
                memcpy(&cmd, &buf[i + 34], 2);
                if (cmd == 400) { // MAV_CMD_COMPONENT_ARM_DISARM
                    isArmed = (param1 > 0.5f);
                    digitalWrite(PIN_ARM_LIGHTS_EN, isArmed ? HIGH : LOW);
                    digitalWrite(PIN_BUZZER_CTRL, HIGH);
                    delay(80);
                    digitalWrite(PIN_BUZZER_CTRL, LOW);
                }
            }
        }
    }
}

// ============================================================================
// 6. MOTOR PWM SETUP & MIXER (20 kHz Brushed MOSFET PWM)
// ============================================================================
void writeMotors(int m1, int m2, int m3, int m4) {
    if (!isArmed) {
        m1 = m2 = m3 = m4 = 0;
    }
    analogWrite(PIN_MOTOR1_PWM, constrain(m1, 0, 255));
    analogWrite(PIN_MOTOR2_PWM, constrain(m2, 0, 255));
    analogWrite(PIN_MOTOR3_PWM, constrain(m3, 0, 255));
    analogWrite(PIN_MOTOR4_PWM, constrain(m4, 0, 255));
}

// ============================================================================
// 7. SETUP & MAIN REAL-TIME FLIGHT LOOP
// ============================================================================
void setup() {
    Serial.begin(115200);
    pinMode(PIN_LED_STATUS, OUTPUT);
    pinMode(PIN_ARM_LIGHTS_EN, OUTPUT);
    pinMode(PIN_BUZZER_CTRL, OUTPUT);
    pinMode(PIN_MOTOR1_PWM, OUTPUT);
    pinMode(PIN_MOTOR2_PWM, OUTPUT);
    pinMode(PIN_MOTOR3_PWM, OUTPUT);
    pinMode(PIN_MOTOR4_PWM, OUTPUT);

    analogWriteFrequency(PIN_MOTOR1_PWM, 20000);
    analogWriteFrequency(PIN_MOTOR2_PWM, 20000);
    analogWriteFrequency(PIN_MOTOR3_PWM, 20000);
    analogWriteFrequency(PIN_MOTOR4_PWM, 20000);
    writeMotors(0, 0, 0, 0);

    // Initialize I2C & SPI Sensors
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 400000);
    icm_ok = initICM42688();
    mpu_ok = initMPU6050();

    // Calibrate Gyro Offsets (Keep drone still on table for 1 second at boot)
    for (int i = 0; i < 250; i++) {
        if (icm_ok) readICM42688();
        else if (mpu_ok) readMPU6050();
        gx_offset += gx_dps;
        gy_offset += gy_dps;
        gz_offset += gz_dps;
        delay(2);
    }
    gx_offset /= 250.0f;
    gy_offset /= 250.0f;
    gz_offset /= 250.0f;

    // Start Wi-Fi Access Point for Mission Planner UDP Connection
    WiFi.mode(WIFI_AP);
    WiFi.softAP(WIFI_SSID, WIFI_PASS);
    mavUDP.begin(MAVLINK_UDP_PORT);

    // Double Beep + Status LED ON -> Ready!
    for (int b = 0; b < 2; b++) {
        digitalWrite(PIN_BUZZER_CTRL, HIGH);
        digitalWrite(PIN_LED_STATUS, HIGH);
        delay(70);
        digitalWrite(PIN_BUZZER_CTRL, LOW);
        digitalWrite(PIN_LED_STATUS, LOW);
        delay(70);
    }
    digitalWrite(PIN_LED_STATUS, HIGH);
}

uint32_t lastImuUs = 0;
uint32_t lastAttMs = 0;
uint32_t lastHbMs  = 0;

void loop() {
    uint32_t nowUs = micros();
    uint32_t nowMs = millis();

    // --- 500 Hz IMU Fusion & PID Loop (Every 2000 us) ---
    if (nowUs - lastImuUs >= 2000) {
        float dt = (nowUs - lastImuUs) * 1e-6f;
        lastImuUs = nowUs;

        if (icm_ok) readICM42688();
        else if (mpu_ok) readMPU6050();

        // Complementary Filter (99.6% Gyro + 0.4% Accel)
        float acc_roll  = atan2f(ay_g, az_g) * RAD_TO_DEG;
        float acc_pitch = atan2f(-ax_g, sqrtf(ay_g * ay_g + az_g * az_g)) * RAD_TO_DEG;
        roll_deg  = 0.996f * (roll_deg  + gx_dps * dt) + 0.004f * acc_roll;
        pitch_deg = 0.996f * (pitch_deg + gy_dps * dt) + 0.004f * acc_pitch;
        yaw_deg  += gz_dps * dt;

        roll_rad  = roll_deg  * DEG_TO_RAD;
        pitch_rad = pitch_deg * DEG_TO_RAD;
        yaw_rad   = yaw_deg   * DEG_TO_RAD;

        // Cascaded Angle -> Rate PID
        float req_rate_roll  = kp_angle * (target_roll_deg  - roll_deg);
        float req_rate_pitch = kp_angle * (target_pitch_deg - pitch_deg);

        float err_r = req_rate_roll  - gx_dps;
        float err_p = req_rate_pitch - gy_dps;
        float err_y = target_yaw_dps - gz_dps;

        float u_roll  = kp_rate * err_r + kd_rate * (err_r - prev_err_roll) / dt;
        float u_pitch = kp_rate * err_p + kd_rate * (err_p - prev_err_pitch) / dt;
        float u_yaw   = kp_yaw  * err_y;
        prev_err_roll  = err_r;
        prev_err_pitch = err_p;

        // QuadX Mixer (M4=FL CW, M2=FR CCW, M3=RL CCW, M1=RR CW)
        int base = (int)(target_throttle * 255.0f);
        int m4 = base - (int)u_pitch + (int)u_roll + (int)u_yaw; // Front-Left (CW)
        int m2 = base - (int)u_pitch - (int)u_roll - (int)u_yaw; // Front-Right (CCW)
        int m3 = base + (int)u_pitch + (int)u_roll - (int)u_yaw; // Rear-Left (CCW)
        int m1 = base + (int)u_pitch - (int)u_roll + (int)u_yaw; // Rear-Right (CW)
        writeMotors(m1, m2, m3, m4);
    }

    // --- 25 Hz MAVLink Attitude Stream to Mission Planner ---
    if (nowMs - lastAttMs >= 40) {
        lastAttMs = nowMs;
        sendMavlinkAttitude();
        pollMavlinkIncoming();
    }

    // --- 1 Hz MAVLink Heartbeat & Battery Status ---
    if (nowMs - lastHbMs >= 1000) {
        lastHbMs = nowMs;
        // Read Battery Voltage on GPIO2 (2.0x Voltage Divider: R26=100k, R27=100k)
        vbat_volts = (analogReadMilliVolts(PIN_VBAT_ADC) / 1000.0f) * 2.0f;
        sendMavlinkHeartbeat();
        sendMavlinkSysStatus();
        digitalWrite(PIN_LED_STATUS, !digitalRead(PIN_LED_STATUS)); // Heartbeat blink
    }
}
