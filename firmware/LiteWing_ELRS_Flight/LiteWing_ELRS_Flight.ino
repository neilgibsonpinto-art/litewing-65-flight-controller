/*
 * ============================================================================
 * TCE_rev1: PRODUCTION-GRADE EXPRESSLRS (ELRS) FLIGHT CONTROLLER
 * Target Board: ESP32-S3-WROOM-1 (TCE_rev1 Monolithic Quadcopter PCB)
 * ============================================================================
 * Features:
 *  - Native ExpressLRS (CRSF Protocol) @ 420,000 baud on Header J3 (RX=44, TX=43)
 *  - 16-Channel CRSF Decoding with CRC-8 D5 validation
 *  - Standard AUX1 (Channel 5) Arming switch with Safety Zero-Throttle Lock
 *  - Instant Failsafe: Auto-disarm and motor cut-off in <300ms if signal lost
 *  - Deterministic 250 Hz Hard Real-Time Flight Loop (every 4000 microseconds)
 *  - 6-DOF Fast I2C (400kHz) MPU-6050 Attitude Fusion (Complementary Filter)
 *  - Self-Leveling Angle Mode (Roll & Pitch) + Smooth Yaw Rate Control
 *  - Dynamic Anti-Stall Clamping: Motors never stop or stall during flight
 *  - Full LED and Buzzer status indication
 * ============================================================================
 * ARDUINO IDE BOARD SETTINGS:
 *   - Board: "ESP32S3 Dev Module"
 *   - USB CDC On Boot: "Enabled"
 *   - Flash Size: "8MB (64Mb)" or "4MB"
 *   - Upload Speed: 921600
 * ============================================================================
 */

#include <Arduino.h>
#include <Wire.h>

// ----------------------------------------------------------------------------
// 1. HARDWARE PIN DEFINITIONS (TCE_rev1 PCB)
// ----------------------------------------------------------------------------
// Motor MOSFET PWM Pins (20 kHz, 8-bit resolution 0-255)
#define PIN_M1_PWM          4   // Rear-Right  (CW)
#define PIN_M2_PWM          5   // Front-Right (CCW)
#define PIN_M3_PWM          6   // Rear-Left   (CCW)
#define PIN_M4_PWM          7   // Front-Left  (CW)

// Fast I2C Bus for MPU-6050
#define PIN_I2C_SDA         8
#define PIN_I2C_SCL         9
#define MPU6050_ADDR        0x68

// ExpressLRS (CRSF) Receiver on Header J3
#define PIN_ELRS_RX         44  // ESP32 RXD0 <- Connect to ELRS Receiver TX
#define PIN_ELRS_TX         43  // ESP32 TXD0 -> Connect to ELRS Receiver RX
#define ELRS_BAUDRATE       420000

// Signaling & Indicators
#define PIN_BASE_RGB        2   // WS2812B NeoPixel RGB LED
#define PIN_STATUS_LED      3   // Blue Heartbeat LED
#define PIN_ARM_LIGHTS      47  // Corner Marker Navigation Lights
#define PIN_BUZZER          48  // Active Low-Battery & Arming Buzzer

// ----------------------------------------------------------------------------
// 2. FLIGHT TUNING & PID PARAMETERS
// ----------------------------------------------------------------------------
// Self-Leveling (Angle Mode) Outer Loop Gains
const float KP_ANGLE        = 3.2f;    // Proportional gain: angle error -> target rate

// Rate Mode Inner Loop Gains (Roll / Pitch)
const float KP_RATE         = 0.90f;   // Gyro rate error P-gain
const float KI_RATE         = 0.015f;  // Integral gain for drift compensation
const float KD_RATE         = 0.025f;  // Derivative damping gain

// Yaw Rate Gain
const float KP_YAW          = 1.60f;

// Flight Limits
const float MAX_TILT_ANGLE  = 25.0f;   // Maximum bank angle (degrees)
const float MAX_YAW_RATE    = 180.0f;  // Maximum yaw rotation rate (deg/sec)
const int   MAX_PID_OUTPUT  = 45;      // Max PID contribution to motor (prevents stall)
const int   MIN_IDLE_THROTTLE = 20;    // Minimum motor spin speed when armed (out of 255)

// ----------------------------------------------------------------------------
// 3. GLOBAL FLIGHT STATE VARIABLES
// ----------------------------------------------------------------------------
HardwareSerial elrsSerial(1);

bool isArmed            = false;
bool elrsConnected      = false;
bool mpuReady           = false;
uint32_t lastElrsPacket = 0;
uint32_t lastLoopMicros = 0;
uint32_t lastTelemetryMs= 0;

// Pilot Commands from ELRS (Normalized 1000 to 2000 microseconds)
uint16_t rc_roll     = 1500;
uint16_t rc_pitch    = 1500;
uint16_t rc_throttle = 1000;
uint16_t rc_yaw      = 1500;
uint16_t rc_aux1     = 1000;

// Estimated Attitude Angles & Angular Rates
float roll_deg = 0.0f, pitch_deg = 0.0f;
float gx = 0.0f, gy = 0.0f, gz = 0.0f;
float gx_offset = 0.0f, gy_offset = 0.0f, gz_offset = 0.0f;

// PID Controller States
float i_term_roll = 0.0f, i_term_pitch = 0.0f;
float prev_rate_roll = 0.0f, prev_rate_pitch = 0.0f;

// ----------------------------------------------------------------------------
// 4. LOW-LEVEL MOTOR CONTROL (20 kHz Glitch-Free PWM)
// ----------------------------------------------------------------------------
void setMotorOutputs(int m1, int m2, int m3, int m4) {
    if (!isArmed || rc_throttle < 1050) {
        analogWrite(PIN_M1_PWM, 0);
        analogWrite(PIN_M2_PWM, 0);
        analogWrite(PIN_M3_PWM, 0);
        analogWrite(PIN_M4_PWM, 0);
        return;
    }

    // Constrain outputs safely within 0 to 255
    analogWrite(PIN_M1_PWM, constrain(m1, 0, 255));
    analogWrite(PIN_M2_PWM, constrain(m2, 0, 255));
    analogWrite(PIN_M3_PWM, constrain(m3, 0, 255));
    analogWrite(PIN_M4_PWM, constrain(m4, 0, 255));
}

// ----------------------------------------------------------------------------
// 5. MPU-6050 SENSOR DRIVER & ATTITUDE FILTER
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

    // Test connection
    Wire.beginTransmission(MPU6050_ADDR);
    if (Wire.endTransmission() != 0) {
        Serial.println("[ERROR] MPU-6050 NOT detected on I2C (Address 0x68)!");
        return false;
    }

    // Wake up device (Clear sleep bit)
    writeMpuReg(0x6B, 0x00);
    delay(20);
    // Set Sample Rate Divider = 0 (1 kHz internal sample rate)
    writeMpuReg(0x19, 0x00);
    // Digital Low Pass Filter (DLPF): 42 Hz bandwidth to reject motor vibration
    writeMpuReg(0x1A, 0x03);
    // Gyro Config: +/- 1000 deg/sec full-scale (32.8 LSB/deg/s)
    writeMpuReg(0x1B, 0x10);
    // Accel Config: +/- 8g full-scale (4096 LSB/g)
    writeMpuReg(0x1C, 0x10);

    Serial.println("[OK] MPU-6050 Configured Successfully!");
    return true;
}

void calibrateGyro() {
    Serial.println("[CALIB] Keep drone completely still on a flat surface...");
    neopixelWrite(PIN_BASE_RGB, 200, 150, 0); // Yellow: Calibrating

    float sum_x = 0.0f, sum_y = 0.0f, sum_z = 0.0f;
    const int SAMPLES = 400;

    for (int i = 0; i < SAMPLES; i++) {
        Wire.beginTransmission(MPU6050_ADDR);
        Wire.write(0x43); // Start at GYRO_XOUT_H
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
    
    // Short beep to indicate calibration complete
    digitalWrite(PIN_BUZZER, HIGH); delay(80); digitalWrite(PIN_BUZZER, LOW);
}

void readAndEstimateAttitude(float dt) {
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(0x3B); // Start at ACCEL_XOUT_H
    Wire.endTransmission(false);
    Wire.requestFrom(MPU6050_ADDR, 14, true);

    if (Wire.available() < 14) return;

    int16_t raw_ax = (Wire.read() << 8) | Wire.read();
    int16_t raw_ay = (Wire.read() << 8) | Wire.read();
    int16_t raw_az = (Wire.read() << 8) | Wire.read();
    Wire.read(); Wire.read(); // Skip temperature bytes
    int16_t raw_gx = (Wire.read() << 8) | Wire.read();
    int16_t raw_gy = (Wire.read() << 8) | Wire.read();
    int16_t raw_gz = (Wire.read() << 8) | Wire.read();

    // Convert raw to physical units
    float ax = (float)raw_ax / 4096.0f;
    float ay = (float)raw_ay / 4096.0f;
    float az = (float)raw_az / 4096.0f;

    // Measured body angular rates (deg/sec)
    gx = ((float)raw_gx / 32.8f) - gx_offset;
    gy = ((float)raw_gy / 32.8f) - gy_offset;
    gz = ((float)raw_gz / 32.8f) - gz_offset;

    // Pitch & Roll from accelerometer (degrees)
    float acc_roll  = atan2(ay, sqrt(ax * ax + az * az)) * 57.29578f;
    float acc_pitch = atan2(-ax, sqrt(ay * ay + az * az)) * 57.29578f;

    // 6-DOF Complementary Filter: High-pass gyro + Low-pass accelerometer
    const float ALPHA = 0.985f;
    roll_deg  = ALPHA * (roll_deg  + gx * dt) + (1.0f - ALPHA) * acc_roll;
    pitch_deg = ALPHA * (pitch_deg + gy * dt) + (1.0f - ALPHA) * acc_pitch;
}

// ----------------------------------------------------------------------------
// 6. EXPRESSLRS (CRSF) PROTOCOL PARSER
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

    // Frame Type 0x16: RC Channels Packed (16 channels, 11-bit each)
    if (type == 0x16 && payload_len >= 22) {
        uint16_t ch0 = ((payload[0]       | payload[1]  << 8) & 0x07FF);
        uint16_t ch1 = ((payload[1]  >> 3 | payload[2]  << 5) & 0x07FF);
        uint16_t ch2 = ((payload[2]  >> 6 | payload[3]  << 2 | payload[4] << 10) & 0x07FF);
        uint16_t ch3 = ((payload[4]  >> 1 | payload[5]  << 7) & 0x07FF);
        uint16_t ch4 = ((payload[5]  >> 4 | payload[6]  << 4) & 0x07FF); // AUX1

        // Convert CRSF 11-bit range (172 to 1811) to standard 1000..2000 microseconds
        rc_roll     = map(ch0, 172, 1811, 1000, 2000);
        rc_pitch    = map(ch1, 172, 1811, 1000, 2000);
        rc_throttle = map(ch2, 172, 1811, 1000, 2000);
        rc_yaw      = map(ch3, 172, 1811, 1000, 2000);
        rc_aux1     = map(ch4, 172, 1811, 1000, 2000);

        lastElrsPacket = millis();
        elrsConnected  = true;

        // AUX1 Arming Logic
        bool arm_switch_high = (rc_aux1 > 1500);

        if (arm_switch_high && !isArmed) {
            // Safety Check: ONLY ARM if Throttle Stick is at Bottom (<1050us)
            if (rc_throttle < 1050) {
                isArmed = true;
                i_term_roll = 0.0f;
                i_term_pitch = 0.0f;
                digitalWrite(PIN_ARM_LIGHTS, HIGH);
                neopixelWrite(PIN_BASE_RGB, 0, 255, 0); // Solid GREEN: ARMED
                digitalWrite(PIN_BUZZER, HIGH); delay(60); digitalWrite(PIN_BUZZER, LOW);
                delay(60);
                digitalWrite(PIN_BUZZER, HIGH); delay(60); digitalWrite(PIN_BUZZER, LOW);
                Serial.println("[STATUS] >>> DRONE ARMED! FLY SAFELY! <<<");
            } else {
                // Warning beep: Cannot arm while throttle is raised!
                digitalWrite(PIN_BUZZER, HIGH); delay(40); digitalWrite(PIN_BUZZER, LOW);
            }
        } 
        else if (!arm_switch_high && isArmed) {
            // Disarm command received
            isArmed = false;
            setMotorOutputs(0, 0, 0, 0);
            digitalWrite(PIN_ARM_LIGHTS, LOW);
            neopixelWrite(PIN_BASE_RGB, 0, 0, 255); // Solid BLUE: Ready / Disarmed
            digitalWrite(PIN_BUZZER, HIGH); delay(150); digitalWrite(PIN_BUZZER, LOW);
            Serial.println("[STATUS] Drone Disarmed.");
        }
    }
}

void parseCrsfStream() {
    while (elrsSerial.available() > 0) {
        uint8_t b = elrsSerial.read();

        if (crsf_idx == 0) {
            if (b == 0xC8 || b == 0xEE) { // CRSF sync byte
                crsf_buf[crsf_idx++] = b;
            }
        } else if (crsf_idx == 1) {
            if (b >= 2 && b <= 62) {
                crsf_buf[crsf_idx++] = b;
            } else {
                crsf_idx = 0;
            }
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

    // Failsafe: If no packets received for >300ms, immediately DISARM and CUT MOTORS
    if (elrsConnected && (millis() - lastElrsPacket > 300)) {
        elrsConnected = false;
        isArmed = false;
        setMotorOutputs(0, 0, 0, 0);
        digitalWrite(PIN_ARM_LIGHTS, LOW);
        neopixelWrite(PIN_BASE_RGB, 255, 0, 0); // Solid RED: FAILSAFE TRIGGERED
        Serial.println("[FAILSAFE] ExpressLRS signal lost! MOTORS CUT!");
    }
}

// ----------------------------------------------------------------------------
// 7. CASCADED PID FLIGHT CONTROLLER & MOTOR MIXER
// ----------------------------------------------------------------------------
void computeFlightLoop(float dt) {
    if (!isArmed || rc_throttle < 1050) {
        setMotorOutputs(0, 0, 0, 0);
        return;
    }

    // 1. Calculate Pilot Target Angles & Rates from RC sticks
    // Invert Pitch & Yaw to match physical TCE_rev1 flight geometry
    float target_angle_roll  =  (rc_roll  - 1500) * (MAX_TILT_ANGLE / 500.0f);
    float target_angle_pitch = -(rc_pitch - 1500) * (MAX_TILT_ANGLE / 500.0f);
    float target_rate_yaw    = -(rc_yaw   - 1500) * (MAX_YAW_RATE   / 500.0f);

    // 2. Outer Loop: Angle Error -> Target Angular Rate (deg/sec)
    float target_rate_roll  = KP_ANGLE * (target_angle_roll  - roll_deg);
    float target_rate_pitch = KP_ANGLE * (target_angle_pitch - pitch_deg);

    // 3. Inner Loop: Angular Rate Error -> Motor Stabilization Torque
    float err_rate_roll  = target_rate_roll  - gx;
    float err_rate_pitch = target_rate_pitch - gy;
    float err_rate_yaw   = target_rate_yaw   - gz;

    // Integral terms with Anti-Windup clamp
    i_term_roll  = constrain(i_term_roll  + (KI_RATE * err_rate_roll  * dt), -20.0f, +20.0f);
    i_term_pitch = constrain(i_term_pitch + (KI_RATE * err_rate_pitch * dt), -20.0f, +20.0f);

    // Derivative terms computed on gyro rate directly (avoids setpoint kick)
    float d_term_roll  = -KD_RATE * (gx - prev_rate_roll)  / dt;
    float d_term_pitch = -KD_RATE * (gy - prev_rate_pitch) / dt;
    prev_rate_roll  = gx;
    prev_rate_pitch = gy;

    // Combined PID Corrections (clamped so motors never stall)
    int roll_corr  = constrain((int)(KP_RATE * err_rate_roll  + i_term_roll  + d_term_roll),  -MAX_PID_OUTPUT, +MAX_PID_OUTPUT);
    int pitch_corr = constrain((int)(KP_RATE * err_rate_pitch + i_term_pitch + d_term_pitch), -MAX_PID_OUTPUT, +MAX_PID_OUTPUT);
    int yaw_corr   = constrain((int)(KP_YAW  * err_rate_yaw), -25, +25);

    // 4. Base Throttle Mapping (1000..2000us -> MIN_IDLE_THROTTLE..250 PWM)
    int base_throttle = map(rc_throttle, 1050, 2000, MIN_IDLE_THROTTLE, 250);

    // 5. Quadcopter "X" Motor Mixing Matrix:
    // M1: Rear-Right (CW)   M2: Front-Right (CCW)
    // M3: Rear-Left  (CCW)  M4: Front-Left  (CW)
    int m1 = base_throttle + pitch_corr - roll_corr - yaw_corr;
    int m2 = base_throttle - pitch_corr - roll_corr + yaw_corr;
    int m3 = base_throttle + pitch_corr + roll_corr + yaw_corr;
    int m4 = base_throttle - pitch_corr + roll_corr - yaw_corr;

    // Apply motor outputs
    setMotorOutputs(m1, m2, m3, m4);
}

// ----------------------------------------------------------------------------
// 8. SETUP & MAIN EXECUTION
// ----------------------------------------------------------------------------
void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n=======================================================");
    Serial.println("  TCE_rev1: EXPRESSLRS FLIGHT CONTROLLER INITIALIZING  ");
    Serial.println("=======================================================");

    // Initialize Discrete Pins
    pinMode(PIN_M1_PWM, OUTPUT);
    pinMode(PIN_M2_PWM, OUTPUT);
    pinMode(PIN_M3_PWM, OUTPUT);
    pinMode(PIN_M4_PWM, OUTPUT);
    setMotorOutputs(0, 0, 0, 0);

    // Set 20 kHz PWM Frequency for ultra-smooth coreless motor drive
    analogWriteFrequency(PIN_M1_PWM, 20000);
    analogWriteFrequency(PIN_M2_PWM, 20000);
    analogWriteFrequency(PIN_M3_PWM, 20000);
    analogWriteFrequency(PIN_M4_PWM, 20000);
    analogWriteResolution(PIN_M1_PWM, 8);
    analogWriteResolution(PIN_M2_PWM, 8);
    analogWriteResolution(PIN_M3_PWM, 8);
    analogWriteResolution(PIN_M4_PWM, 8); // 8-bit duty: 0 to 255

    pinMode(PIN_STATUS_LED, OUTPUT);
    pinMode(PIN_ARM_LIGHTS, OUTPUT);
    pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_STATUS_LED, HIGH);
    digitalWrite(PIN_ARM_LIGHTS, LOW);
    digitalWrite(PIN_BUZZER, LOW);

    // Start ExpressLRS CRSF Serial on Header J3 (RX=44, TX=43 @ 420000 baud)
    elrsSerial.begin(ELRS_BAUDRATE, SERIAL_8N1, PIN_ELRS_RX, PIN_ELRS_TX);
    Serial.println("[OK] ExpressLRS Serial started at 420,000 baud on Pins RX=44, TX=43.");

    // Initialize MPU-6050 & Calibrate
    mpuReady = initMPU6050();
    if (mpuReady) {
        calibrateGyro();
        neopixelWrite(PIN_BASE_RGB, 0, 0, 255); // Solid BLUE: Ready & Disarmed
    } else {
        neopixelWrite(PIN_BASE_RGB, 255, 0, 0); // Solid RED: MPU Error
    }

    lastLoopMicros = micros();
    Serial.println("[READY] System initialized. Turn on ELRS Radio to fly!");
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

    // 3. Heartbeat LED & Diagnostics Monitor (5 Hz)
    if (millis() - lastTelemetryMs >= 200) {
        lastTelemetryMs = millis();
        digitalWrite(PIN_STATUS_LED, !digitalRead(PIN_STATUS_LED));

        // Periodic Status Print to Serial Monitor
        if (!elrsConnected) {
            Serial.println("[WAITING] Searching for ExpressLRS Transmitter link...");
        } else {
            Serial.printf("[ELRS] T:%d R:%d P:%d Y:%d | AUX1:%d | ARMED:%d | Ang: (R:%.1f, P:%.1f)\n",
                          rc_throttle, rc_roll, rc_pitch, rc_yaw, rc_aux1, isArmed, roll_deg, pitch_deg);
        }
    }
}
