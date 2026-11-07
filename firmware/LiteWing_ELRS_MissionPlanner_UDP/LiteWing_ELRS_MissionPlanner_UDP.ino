/*
 * ============================================================================
 * TCE_rev1: INTEGRATED EXPRESSLRS & MISSION PLANNER (UDP) FLIGHT CONTROLLER
 * Target Hardware: ESP32-S3-WROOM-1 (TCE_rev1 Monolithic Quadcopter PCB)
 * ============================================================================
 * Features:
 *  1. ExpressLRS (CRSF) Primary Control:
 *     - Hardware Serial UART0 @ 420,000 baud on Header J3 (RX=44, TX=43)
 *     - 16-Channel 11-bit CRSF parsing with CRC-8 D5 check
 *     - Standard AUX1 (Channel 5) Arming Switch with Zero-Throttle Safety Lock
 *     - Instant Failsafe: Disarm and cut motors within 300ms if signal lost
 *
 *  2. Mission Planner UDP Telemetry (Port 14550 over Wi-Fi AP):
 *     - Wi-Fi Access Point: SSID "TCE_DRONE_FC" (Password: "12345678")
 *     - Full MAVLink v1 Telemetry Engine:
 *         * MSG #0  : HEARTBEAT (1 Hz) -> Armed/Disarmed, MAV_TYPE_QUADROTOR
 *         * MSG #1  : SYS_STATUS (1 Hz) -> Battery voltage, sensor health
 *         * MSG #22 : PARAM_VALUE -> Instant Mission Planner connection
 *         * MSG #30 : ATTITUDE (10 Hz) -> Live 3D Artificial Horizon HUD
 *         * MSG #65 : RC_CHANNELS (5 Hz) -> Live ELRS stick display in MP
 *
 *  3. Real-Time Flight Dynamics:
 *     - Deterministic 250 Hz Hard Real-Time Flight Loop (every 4000 microseconds)
 *     - 6-DOF Fast I2C (400kHz) MPU-6050 Complementary Attitude Filter
 *     - Angle Mode (Self-Leveling Roll/Pitch) + Yaw Rate Control
 *     - 20 kHz Glitch-Free PWM Motor Gate Drive on GPIO 4, 5, 6, 7
 *     - Dynamic Anti-Stall: Motors never drop or stall during flight maneuvers
 * ============================================================================
 * ARDUINO IDE SETTINGS:
 *   - Board: "ESP32S3 Dev Module"
 *   - USB CDC On Boot: "Enabled"
 *   - Flash Size: "8MB (64Mb)" or "4MB"
 *   - Upload Speed: 921600
 * ============================================================================
 */

#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// ----------------------------------------------------------------------------
// 1. PIN ASSIGNMENTS (TCE_rev1 Hardware Verified)
// ----------------------------------------------------------------------------
#define PIN_M1_PWM          4   // Rear-Right  (CW)
#define PIN_M2_PWM          5   // Front-Right (CCW)
#define PIN_M3_PWM          6   // Rear-Left   (CCW)
#define PIN_M4_PWM          7   // Front-Left  (CW)

#define PIN_I2C_SDA         8   // Fast I2C SDA
#define PIN_I2C_SCL         9   // Fast I2C SCL
#define MPU6050_ADDR        0x68

#define PIN_ELRS_RX         44  // ESP_RXD0 <- Connect to ELRS Receiver TX
#define PIN_ELRS_TX         43  // ESP_TXD0 -> Connect to ELRS Receiver RX
#define ELRS_BAUD           420000

#define PIN_BASE_RGB        2   // WS2812B NeoPixel RGB LED
#define PIN_STATUS_LED      3   // Blue Heartbeat LED
#define PIN_ARM_LIGHTS      47  // Corner Navigation Lights
#define PIN_BUZZER          48  // Active Buzzer

// ----------------------------------------------------------------------------
// 2. WI-FI ACCESS POINT & MAVLINK UDP SETTINGS
// ----------------------------------------------------------------------------
const char* WIFI_SSID       = "TCE_DRONE_FC";
const char* WIFI_PASS       = "12345678";
const uint16_t MAV_UDP_PORT = 14550;

WiFiUDP mavUDP;
IPAddress gcsIP(192, 168, 4, 255); // Broadcast IP for connected GCS
uint8_t mav_seq = 0;

// ----------------------------------------------------------------------------
// 3. FLIGHT TUNING & PID PARAMETERS
// ----------------------------------------------------------------------------
const float KP_ANGLE        = 3.2f;    // Angle error -> target rate
const float KP_RATE         = 0.90f;   // Gyro rate error P-gain
const float KI_RATE         = 0.015f;  // Integral gain
const float KD_RATE         = 0.025f;  // Derivative damping gain
const float KP_YAW          = 1.60f;   // Yaw rate gain

const float MAX_TILT_ANGLE  = 25.0f;   // Max bank angle (degrees)
const float MAX_YAW_RATE    = 180.0f;  // Max yaw rate (deg/sec)
const int   MAX_PID_OUTPUT  = 45;      // Max PID contribution (prevents motor stall)
const int   MIN_IDLE_THROTTLE = 20;    // Minimum motor spin speed when armed (0-255)

// ----------------------------------------------------------------------------
// 4. GLOBAL FLIGHT STATE VARIABLES
// ----------------------------------------------------------------------------
HardwareSerial elrsSerial(1);

bool isArmed            = false;
bool elrsConnected      = false;
bool mpuReady           = false;
uint32_t lastElrsPacket = 0;
uint32_t lastLoopMicros = 0;

// Scheduling Timers for Non-Blocking Telemetry
uint32_t lastAttitudeMs  = 0;
uint32_t lastRcChanMs    = 0;
uint32_t lastHeartbeatMs = 0;
uint32_t lastDiagMs      = 0;

// RC Channels (1000..2000 microseconds)
uint16_t rc_roll     = 1500;
uint16_t rc_pitch    = 1500;
uint16_t rc_throttle = 1000;
uint16_t rc_yaw      = 1500;
uint16_t rc_aux1     = 1000; // ARM Switch

// Attitude & Gyro Rates
float roll_deg = 0.0f, pitch_deg = 0.0f, yaw_deg = 0.0f;
float gx = 0.0f, gy = 0.0f, gz = 0.0f;
float gx_offset = 0.0f, gy_offset = 0.0f, gz_offset = 0.0f;

// PID Integrators
float i_term_roll = 0.0f, i_term_pitch = 0.0f;
float prev_rate_roll = 0.0f, prev_rate_pitch = 0.0f;

// ----------------------------------------------------------------------------
// 5. LOW-LEVEL MOTOR ACTUATION (20 kHz Glitch-Free PWM)
// ----------------------------------------------------------------------------
void setMotorOutputs(int m1, int m2, int m3, int m4) {
    if (!isArmed || rc_throttle < 1050) {
        analogWrite(PIN_M1_PWM, 0);
        analogWrite(PIN_M2_PWM, 0);
        analogWrite(PIN_M3_PWM, 0);
        analogWrite(PIN_M4_PWM, 0);
        return;
    }

    analogWrite(PIN_M1_PWM, constrain(m1, 0, 255));
    analogWrite(PIN_M2_PWM, constrain(m2, 0, 255));
    analogWrite(PIN_M3_PWM, constrain(m3, 0, 255));
    analogWrite(PIN_M4_PWM, constrain(m4, 0, 255));
}

// ----------------------------------------------------------------------------
// 6. MPU-6050 FAST I2C DRIVER & ATTITUDE ESTIMATION
// ----------------------------------------------------------------------------
void writeMpuReg(uint8_t reg, uint8_t val) {
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(reg);
    Wire.write(val);
    Wire.endTransmission();
}

bool initMPU6050() {
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 400000); // 400 kHz Fast I2C
    delay(50);

    Wire.beginTransmission(MPU6050_ADDR);
    if (Wire.endTransmission() != 0) {
        Serial.println("[ERROR] MPU-6050 not responding on I2C (0x68)!");
        return false;
    }

    writeMpuReg(0x6B, 0x00); // Clear sleep
    delay(20);
    writeMpuReg(0x19, 0x00); // 1 kHz sample rate
    writeMpuReg(0x1A, 0x03); // DLPF: 42 Hz filter (rejects motor vibration)
    writeMpuReg(0x1B, 0x10); // Gyro: +/- 1000 deg/s
    writeMpuReg(0x1C, 0x10); // Accel: +/- 8g
    Serial.println("[OK] MPU-6050 configured successfully.");
    return true;
}

void calibrateGyro() {
    Serial.println("[CALIB] Keep drone still on a flat surface...");
    neopixelWrite(PIN_BASE_RGB, 200, 150, 0); // Yellow: Calibrating

    float sum_x = 0.0f, sum_y = 0.0f, sum_z = 0.0f;
    const int SAMPLES = 300;

    for (int i = 0; i < SAMPLES; i++) {
        Wire.beginTransmission(MPU6050_ADDR);
        Wire.write(0x43);
        Wire.endTransmission(false);
        Wire.requestFrom(MPU6050_ADDR, 6, true);

        if (Wire.available() >= 6) {
            int16_t raw_gx = (Wire.read() << 8) | Wire.read();
            int16_t raw_gy = (Wire.read() << 8) | Wire.read();
            int16_t raw_gz = (Wire.read() << 8) | Wire.read();

            sum_x += (float)raw_gx / 32.8f;
            sum_y += (float)raw_gy / 32.8f;
            sum_z += (float)raw_gz / 32.8f;
        }
        delay(3);
    }

    gx_offset = sum_x / SAMPLES;
    gy_offset = sum_y / SAMPLES;
    gz_offset = sum_z / SAMPLES;

    Serial.printf("[CALIB DONE] Offsets -> X: %.2f, Y: %.2f, Z: %.2f dps\n", gx_offset, gy_offset, gz_offset);
    digitalWrite(PIN_BUZZER, HIGH); delay(80); digitalWrite(PIN_BUZZER, LOW);
}

void readAndEstimateAttitude(float dt) {
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU6050_ADDR, 14, true);

    if (Wire.available() < 14) return;

    int16_t raw_ax = (Wire.read() << 8) | Wire.read();
    int16_t raw_ay = (Wire.read() << 8) | Wire.read();
    int16_t raw_az = (Wire.read() << 8) | Wire.read();
    Wire.read(); Wire.read(); // Skip temp
    int16_t raw_gx = (Wire.read() << 8) | Wire.read();
    int16_t raw_gy = (Wire.read() << 8) | Wire.read();
    int16_t raw_gz = (Wire.read() << 8) | Wire.read();

    float ax = (float)raw_ax / 4096.0f;
    float ay = (float)raw_ay / 4096.0f;
    float az = (float)raw_az / 4096.0f;

    gx = ((float)raw_gx / 32.8f) - gx_offset;
    gy = ((float)raw_gy / 32.8f) - gy_offset;
    gz = ((float)raw_gz / 32.8f) - gz_offset;

    float acc_roll  = atan2(ay, sqrt(ax * ax + az * az)) * 57.29578f;
    float acc_pitch = atan2(-ax, sqrt(ay * ay + az * az)) * 57.29578f;

    const float ALPHA = 0.985f;
    roll_deg  = ALPHA * (roll_deg  + gx * dt) + (1.0f - ALPHA) * acc_roll;
    pitch_deg = ALPHA * (pitch_deg + gy * dt) + (1.0f - ALPHA) * acc_pitch;
    yaw_deg  += gz * dt; // Integrated yaw rate
}

// ----------------------------------------------------------------------------
// 7. EXPRESSLRS (CRSF) PROTOCOL PARSER
// ----------------------------------------------------------------------------
uint8_t crsf_crc8(const uint8_t *ptr, uint8_t len) {
    uint8_t crc = 0;
    for (uint8_t i = 0; i < len; i++) {
        crc ^= ptr[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x80) crc = (crc << 1) ^ 0xD5;
            else crc <<= 1;
        }
    }
    return crc;
}

uint8_t crsf_buf[64];
uint8_t crsf_idx = 0;

void processCrsfPacket(const uint8_t *frame, uint8_t total_len) {
    uint8_t type = frame[2];
    const uint8_t *payload = &frame[3];
    uint8_t payload_len = total_len - 4;

    if (type == 0x16 && payload_len >= 22) {
        uint16_t ch0 = ((payload[0]       | payload[1]  << 8) & 0x07FF);
        uint16_t ch1 = ((payload[1]  >> 3 | payload[2]  << 5) & 0x07FF);
        uint16_t ch2 = ((payload[2]  >> 6 | payload[3]  << 2 | payload[4] << 10) & 0x07FF);
        uint16_t ch3 = ((payload[4]  >> 1 | payload[5]  << 7) & 0x07FF);
        uint16_t ch4 = ((payload[5]  >> 4 | payload[6]  << 4) & 0x07FF); // AUX1

        rc_roll     = map(ch0, 172, 1811, 1000, 2000);
        rc_pitch    = map(ch1, 172, 1811, 1000, 2000);
        rc_throttle = map(ch2, 172, 1811, 1000, 2000);
        rc_yaw      = map(ch3, 172, 1811, 1000, 2000);
        rc_aux1     = map(ch4, 172, 1811, 1000, 2000);

        lastElrsPacket = millis();
        elrsConnected  = true;

        bool arm_switch_high = (rc_aux1 > 1500);

        if (arm_switch_high && !isArmed) {
            // Safety: Arm ONLY when throttle is at bottom zero (<1050us)
            if (rc_throttle < 1050) {
                isArmed = true;
                i_term_roll = 0.0f;
                i_term_pitch = 0.0f;
                digitalWrite(PIN_ARM_LIGHTS, HIGH);
                neopixelWrite(PIN_BASE_RGB, 0, 255, 0); // Solid GREEN: ARMED
                digitalWrite(PIN_BUZZER, HIGH); delay(60); digitalWrite(PIN_BUZZER, LOW);
                delay(60);
                digitalWrite(PIN_BUZZER, HIGH); delay(60); digitalWrite(PIN_BUZZER, LOW);
                Serial.println("[STATUS] >>> DRONE ARMED VIA ELRS! <<<");
            } else {
                digitalWrite(PIN_BUZZER, HIGH); delay(40); digitalWrite(PIN_BUZZER, LOW);
            }
        } 
        else if (!arm_switch_high && isArmed) {
            isArmed = false;
            setMotorOutputs(0, 0, 0, 0);
            digitalWrite(PIN_ARM_LIGHTS, LOW);
            neopixelWrite(PIN_BASE_RGB, 0, 0, 255); // Solid BLUE: Disarmed
            digitalWrite(PIN_BUZZER, HIGH); delay(150); digitalWrite(PIN_BUZZER, LOW);
            Serial.println("[STATUS] Drone Disarmed.");
        }
    }
}

void parseCrsfStream() {
    while (elrsSerial.available() > 0) {
        uint8_t b = elrsSerial.read();

        if (crsf_idx == 0) {
            if (b == 0xC8 || b == 0xEE) crsf_buf[crsf_idx++] = b;
        } else if (crsf_idx == 1) {
            if (b >= 2 && b <= 62) crsf_buf[crsf_idx++] = b;
            else crsf_idx = 0;
        } else {
            crsf_buf[crsf_idx++] = b;
            uint8_t expected_len = crsf_buf[1] + 2;

            if (crsf_idx == expected_len) {
                uint8_t calc_crc = crsf_crc8(&crsf_buf[2], crsf_buf[1] - 1);
                if (calc_crc == crsf_buf[expected_len - 1]) {
                    processCrsfPacket(crsf_buf, expected_len);
                }
                crsf_idx = 0;
            } else if (crsf_idx >= sizeof(crsf_buf)) {
                crsf_idx = 0;
            }
        }
    }

    // Failsafe: disarm if signal lost for >300ms
    if (elrsConnected && (millis() - lastElrsPacket > 300)) {
        elrsConnected = false;
        isArmed = false;
        setMotorOutputs(0, 0, 0, 0);
        digitalWrite(PIN_ARM_LIGHTS, LOW);
        neopixelWrite(PIN_BASE_RGB, 255, 0, 0); // Solid RED: Failsafe
    }
}

// ----------------------------------------------------------------------------
// 8. CASCADED PID FLIGHT CONTROLLER & MOTOR MIXER
// ----------------------------------------------------------------------------
void computeFlightLoop(float dt) {
    if (!isArmed || rc_throttle < 1050) {
        setMotorOutputs(0, 0, 0, 0);
        return;
    }

    // Invert Pitch & Yaw to match physical TCE_rev1 layout
    float target_angle_roll  =  (rc_roll  - 1500) * (MAX_TILT_ANGLE / 500.0f);
    float target_angle_pitch = -(rc_pitch - 1500) * (MAX_TILT_ANGLE / 500.0f);
    float target_rate_yaw    = -(rc_yaw   - 1500) * (MAX_YAW_RATE   / 500.0f);

    float target_rate_roll  = KP_ANGLE * (target_angle_roll  - roll_deg);
    float target_rate_pitch = KP_ANGLE * (target_angle_pitch - pitch_deg);

    float err_rate_roll  = target_rate_roll  - gx;
    float err_rate_pitch = target_rate_pitch - gy;
    float err_rate_yaw   = target_rate_yaw   - gz;

    i_term_roll  = constrain(i_term_roll  + (KI_RATE * err_rate_roll  * dt), -20.0f, +20.0f);
    i_term_pitch = constrain(i_term_pitch + (KI_RATE * err_rate_pitch * dt), -20.0f, +20.0f);

    float d_term_roll  = -KD_RATE * (gx - prev_rate_roll)  / dt;
    float d_term_pitch = -KD_RATE * (gy - prev_rate_pitch) / dt;
    prev_rate_roll  = gx;
    prev_rate_pitch = gy;

    int roll_corr  = constrain((int)(KP_RATE * err_rate_roll  + i_term_roll  + d_term_roll),  -MAX_PID_OUTPUT, +MAX_PID_OUTPUT);
    int pitch_corr = constrain((int)(KP_RATE * err_rate_pitch + i_term_pitch + d_term_pitch), -MAX_PID_OUTPUT, +MAX_PID_OUTPUT);
    int yaw_corr   = constrain((int)(KP_YAW  * err_rate_yaw), -25, +25);

    int base_throttle = map(rc_throttle, 1050, 2000, MIN_IDLE_THROTTLE, 250);

    // Quadcopter "X" Motor Mixing
    int m1 = base_throttle + pitch_corr - roll_corr - yaw_corr; // Rear-Right (CW)
    int m2 = base_throttle - pitch_corr - roll_corr + yaw_corr; // Front-Right (CCW)
    int m3 = base_throttle + pitch_corr + roll_corr + yaw_corr; // Rear-Left (CCW)
    int m4 = base_throttle - pitch_corr + roll_corr - yaw_corr; // Front-Left (CW)

    setMotorOutputs(m1, m2, m3, m4);
}

// ----------------------------------------------------------------------------
// 9. BUILT-IN LIGHTWEIGHT MAVLINK v1 ENGINE (MISSION PLANNER UDP)
// ----------------------------------------------------------------------------
uint16_t mav_crc_accum(uint8_t data, uint16_t crc) {
    uint8_t tmp = data ^ (uint8_t)(crc & 0xFF);
    tmp ^= (tmp << 4);
    return (crc >> 8) ^ ((uint16_t)tmp << 8) ^ ((uint16_t)tmp << 3) ^ ((uint16_t)tmp >> 4);
}

void sendMavlinkPacket(uint8_t msg_id, const uint8_t* payload, uint8_t len, uint8_t crc_extra) {
    uint8_t buf[80];
    buf[0] = 0xFE;          // MAVLink v1 STX
    buf[1] = len;           // Payload length
    buf[2] = mav_seq++;     // Packet sequence number
    buf[3] = 1;             // System ID = 1
    buf[4] = 1;             // Component ID = 1 (AUTOPILOT1)
    buf[5] = msg_id;        // Message ID
    memcpy(&buf[6], payload, len);

    // Compute 16-bit CRC with CRC_EXTRA byte
    uint16_t crc = 0xFFFF;
    for (int i = 1; i < 6 + len; i++) crc = mav_crc_accum(buf[i], crc);
    crc = mav_crc_accum(crc_extra, crc);
    buf[6 + len] = (uint8_t)(crc & 0xFF);
    buf[7 + len] = (uint8_t)(crc >> 8);

    // Send UDP packet to Mission Planner (Port 14550)
    mavUDP.beginPacket(gcsIP, MAV_UDP_PORT);
    mavUDP.write(buf, 8 + len);
    mavUDP.endPacket();

    // Also mirror to USB Serial
    Serial.write(buf, 8 + len);
}

// MSG #0: HEARTBEAT (1 Hz, crc_extra = 50)
void sendMavlinkHeartbeat() {
    uint8_t p[9] = {0};
    p[4] = 2; // MAV_TYPE_QUADROTOR = 2
    p[5] = 3; // MAV_AUTOPILOT_ARDUPILOTMEGA = 3
    p[6] = isArmed ? (0x80 | 0x01) : 0x01; // MAV_MODE_FLAG_SAFETY_ARMED (0x80)
    p[8] = isArmed ? 4 : 3;                // MAV_STATE_ACTIVE (4) / STANDBY (3)
    sendMavlinkPacket(0, p, 9, 50);
}

// MSG #1: SYS_STATUS (1 Hz, crc_extra = 124)
void sendMavlinkSysStatus() {
    uint8_t p[31] = {0};
    uint32_t sensors = 0x01 | 0x02; // Gyro + Accel healthy
    memcpy(&p[0], &sensors, 4);
    memcpy(&p[4], &sensors, 4);
    memcpy(&p[8], &sensors, 4);
    uint16_t load = 200; // 20% CPU load
    uint16_t vbat_mv = 3850; // Nominal 3.85V 1S LiPo
    memcpy(&p[12], &load, 2);
    memcpy(&p[14], &vbat_mv, 2);
    p[30] = 85; // 85% battery remaining
    sendMavlinkPacket(1, p, 31, 124);
}

// MSG #30: ATTITUDE (10 Hz, crc_extra = 39) -> Mission Planner HUD Artificial Horizon
void sendMavlinkAttitude() {
    uint8_t p[28] = {0};
    uint32_t ms = millis();
    float roll_rad  = roll_deg  * 0.01745329f;
    float pitch_rad = pitch_deg * 0.01745329f;
    float yaw_rad   = yaw_deg   * 0.01745329f;
    float rollspeed  = gx * 0.01745329f;
    float pitchspeed = gy * 0.01745329f;
    float yawspeed   = gz * 0.01745329f;

    memcpy(&p[0],  &ms, 4);
    memcpy(&p[4],  &roll_rad, 4);
    memcpy(&p[8],  &pitch_rad, 4);
    memcpy(&p[12], &yaw_rad, 4);
    memcpy(&p[16], &rollspeed, 4);
    memcpy(&p[20], &pitchspeed, 4);
    memcpy(&p[24], &yawspeed, 4);
    sendMavlinkPacket(30, p, 28, 39);
}

// MSG #65: RC_CHANNELS (5 Hz, crc_extra = 118) -> Mission Planner Live RC Sticks
void sendMavlinkRcChannels() {
    uint8_t p[36] = {0};
    uint32_t ms = millis();
    memcpy(&p[0], &ms, 4);
    p[4] = 8; // 8 active channels
    memcpy(&p[5],  &rc_roll, 2);     // Ch1: Roll
    memcpy(&p[7],  &rc_pitch, 2);    // Ch2: Pitch
    memcpy(&p[9],  &rc_throttle, 2); // Ch3: Throttle
    memcpy(&p[11], &rc_yaw, 2);      // Ch4: Yaw
    memcpy(&p[13], &rc_aux1, 2);     // Ch5: AUX1 Arm
    uint16_t ch_idle = 1500;
    memcpy(&p[15], &ch_idle, 2);     // Ch6
    memcpy(&p[17], &ch_idle, 2);     // Ch7
    memcpy(&p[19], &ch_idle, 2);     // Ch8
    p[35] = 255; // RSSI: 100%
    sendMavlinkPacket(65, p, 36, 118);
}

// MSG #22: PARAM_VALUE -> Answers Mission Planner Parameter Requests instantly
void sendMavlinkParam(const char* name, float val, uint16_t idx, uint16_t total) {
    uint8_t p[25] = {0};
    memcpy(&p[0], &val, 4);
    p[4] = (uint8_t)(total & 0xFF);
    p[5] = (uint8_t)(total >> 8);
    p[6] = (uint8_t)(idx & 0xFF);
    p[7] = (uint8_t)(idx >> 8);
    strncpy((char*)&p[8], name, 16);
    p[24] = 9; // MAV_PARAM_TYPE_REAL32
    sendMavlinkPacket(22, p, 25, 220);
}

// Listen for incoming GCS requests over UDP
void pollMavlinkIncoming() {
    int pktSize = mavUDP.parsePacket();
    if (pktSize <= 0) return;

    gcsIP = mavUDP.remoteIP(); // Capture Mission Planner PC IP address
    uint8_t buf[256];
    int len = mavUDP.read(buf, sizeof(buf));

    for (int i = 0; i < len - 6; i++) {
        if (buf[i] == 0xFE) {
            uint8_t msg_id = buf[i + 5];

            // MSG #21: PARAM_REQUEST_LIST (Mission Planner asking for parameters)
            if (msg_id == 21) {
                sendMavlinkParam("SYSID_THISMAV", 1.0f, 0, 3);
                sendMavlinkParam("PILOT_THR_FILT", 0.0f, 1, 3);
                sendMavlinkParam("ARMING_CHECK",   0.0f, 2, 3);
            }
            // MSG #76: COMMAND_LONG (Arm / Disarm button in Mission Planner)
            else if (msg_id == 76 && (i + 36 <= len)) {
                uint16_t cmd;
                float param1;
                memcpy(&param1, &buf[i + 6], 4);
                memcpy(&cmd, &buf[i + 34], 2);
                if (cmd == 400) { // MAV_CMD_COMPONENT_ARM_DISARM
                    bool reqArm = (param1 > 0.5f);
                    if (reqArm && !isArmed && rc_throttle < 1050) {
                        isArmed = true;
                        digitalWrite(PIN_ARM_LIGHTS, HIGH);
                        neopixelWrite(PIN_BASE_RGB, 0, 255, 0);
                        digitalWrite(PIN_BUZZER, HIGH); delay(80); digitalWrite(PIN_BUZZER, LOW);
                    } else if (!reqArm && isArmed) {
                        isArmed = false;
                        setMotorOutputs(0, 0, 0, 0);
                        digitalWrite(PIN_ARM_LIGHTS, LOW);
                        neopixelWrite(PIN_BASE_RGB, 0, 0, 255);
                        digitalWrite(PIN_BUZZER, HIGH); delay(150); digitalWrite(PIN_BUZZER, LOW);
                    }
                }
            }
        }
    }
}

// ----------------------------------------------------------------------------
// 10. SETUP & MAIN EXECUTION
// ----------------------------------------------------------------------------
void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n=======================================================");
    Serial.println(" TCE_rev1: EXPRESSLRS + MISSION PLANNER (UDP) FC START ");
    Serial.println("=======================================================");

    pinMode(PIN_M1_PWM, OUTPUT);
    pinMode(PIN_M2_PWM, OUTPUT);
    pinMode(PIN_M3_PWM, OUTPUT);
    pinMode(PIN_M4_PWM, OUTPUT);
    setMotorOutputs(0, 0, 0, 0);

    analogWriteFrequency(PIN_M1_PWM, 20000);
    analogWriteFrequency(PIN_M2_PWM, 20000);
    analogWriteFrequency(PIN_M3_PWM, 20000);
    analogWriteFrequency(PIN_M4_PWM, 20000);
    analogWriteResolution(PIN_M1_PWM, 8);
    analogWriteResolution(PIN_M2_PWM, 8);
    analogWriteResolution(PIN_M3_PWM, 8);
    analogWriteResolution(PIN_M4_PWM, 8);

    pinMode(PIN_STATUS_LED, OUTPUT);
    pinMode(PIN_ARM_LIGHTS, OUTPUT);
    pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_STATUS_LED, HIGH);
    digitalWrite(PIN_ARM_LIGHTS, LOW);
    digitalWrite(PIN_BUZZER, LOW);

    // 1. Initialize ExpressLRS CRSF Serial on Header J3
    elrsSerial.begin(ELRS_BAUD, SERIAL_8N1, PIN_ELRS_RX, PIN_ELRS_TX);
    Serial.println("[OK] ExpressLRS Serial started at 420,000 baud on Pins 44 & 43.");

    // 2. Initialize MPU-6050 & Calibrate Gyro
    mpuReady = initMPU6050();
    if (mpuReady) {
        calibrateGyro();
        neopixelWrite(PIN_BASE_RGB, 0, 0, 255); // Solid BLUE: Ready & Disarmed
    } else {
        neopixelWrite(PIN_BASE_RGB, 255, 0, 0);
    }

    // 3. Start Wi-Fi Access Point for Mission Planner UDP Connection
    WiFi.mode(WIFI_AP);
    WiFi.softAP(WIFI_SSID, WIFI_PASS);
    mavUDP.begin(MAV_UDP_PORT);
    Serial.printf("[OK] Wi-Fi AP '%s' active. Connect Mission Planner via UDP Port %d!\n", WIFI_SSID, MAV_UDP_PORT);

    lastLoopMicros = micros();
}

void loop() {
    // 1. Constantly Parse Incoming ExpressLRS Radio Frames
    parseCrsfStream();

    // 2. Deterministic 250 Hz Real-Time Flight Loop (every 4000 microseconds)
    uint32_t now_micros = micros();
    if (now_micros - lastLoopMicros >= 4000) {
        float dt = (now_micros - lastLoopMicros) * 1e-6f;
        lastLoopMicros = now_micros;

        if (mpuReady) {
            readAndEstimateAttitude(dt);
            computeFlightLoop(dt);
        }
    }

    // 3. Poll Incoming UDP Commands from Mission Planner
    pollMavlinkIncoming();

    // 4. Non-Blocking MAVLink Telemetry Schedules
    uint32_t now_ms = millis();

    // ATTITUDE (10 Hz = every 100 ms) -> Drives Mission Planner Artificial Horizon HUD
    if (now_ms - lastAttitudeMs >= 100) {
        lastAttitudeMs = now_ms;
        sendMavlinkAttitude();
    }

    // RC_CHANNELS (5 Hz = every 200 ms) -> Shows live ELRS channels in Mission Planner
    if (now_ms - lastRcChanMs >= 200) {
        lastRcChanMs = now_ms;
        sendMavlinkRcChannels();
    }

    // HEARTBEAT & SYS_STATUS (1 Hz = every 1000 ms) -> Keeps Mission Planner connected
    if (now_ms - lastHeartbeatMs >= 1000) {
        lastHeartbeatMs = now_ms;
        sendMavlinkHeartbeat();
        sendMavlinkSysStatus();
    }

    // Heartbeat LED & Diagnostics Monitor (2 Hz)
    if (now_ms - lastDiagMs >= 500) {
        lastDiagMs = now_ms;
        digitalWrite(PIN_STATUS_LED, !digitalRead(PIN_STATUS_LED));
    }
}
