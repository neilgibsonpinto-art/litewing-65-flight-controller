/*
 * ============================================================================
 * TCE_rev1: VERIFIED ALL 4 BRUSHED MOTORS SEQUENTIAL & SYNCHRONOUS TEST
 *
 * COPPER ROUTING VERIFICATION (FROM PCB):
 *   - M1: Header J4 (Rear-Right  Arm | CW ) -> Q1 Gate -> ESP32-S3 GPIO4
 *   - M2: Header J5 (Front-Right Arm | CCW) -> Q2 Gate -> ESP32-S3 GPIO5
 *   - M3: Header J6 (Rear-Left   Arm | CCW) -> Q3 Gate -> ESP32-S3 GPIO6
 *   - M4: Header J7 (Front-Left  Arm | CW ) -> Q4 Gate -> ESP32-S3 GPIO7
 *
 * PWM Frequency: 20 kHz (Smooth, silent brushed motor drive)
 * ============================================================================
 *
 * ARDUINO IDE UPLOAD SETTINGS:
 *   1. Board            : "ESP32S3 Dev Module"
 *   2. USB CDC On Boot  : "Enabled"
 *   3. Upload Mode      : "UART0 / Hardware CDC"
 * ============================================================================
 */

#include <Arduino.h>

// Exact PCB Motor Pins (100% Verified)
#define PIN_M1_PWM       4   // M1: Rear-Right  (CW  Rotation, Header J4)
#define PIN_M2_PWM       5   // M2: Front-Right (CCW Rotation, Header J5)
#define PIN_M3_PWM       6   // M3: Rear-Left   (CCW Rotation, Header J6)
#define PIN_M4_PWM       7   // M4: Front-Left  (CW  Rotation, Header J7)

#define PIN_STATUS_LED   3   // Top Blue Status LED (D8)
#define PIN_BUZZER       48  // Active Buzzer (BZ1)
#define PIN_ARM_LEDS     47  // Corner Arm LEDs (D10-D13)

// Safe test throttle speeds (0 to 255 for 8-bit PWM)
const int PWM_SPIN_LOW = 40;  // ~16% throttle (gentle test speed)
const int PWM_SPIN_MED = 80;  // ~31% throttle (medium speed)

void stopAllMotors() {
    analogWrite(PIN_M1_PWM, 0);
    analogWrite(PIN_M2_PWM, 0);
    analogWrite(PIN_M3_PWM, 0);
    analogWrite(PIN_M4_PWM, 0);
}

void setup() {
    pinMode(PIN_STATUS_LED, OUTPUT);
    pinMode(PIN_BUZZER, OUTPUT);
    pinMode(PIN_ARM_LEDS, OUTPUT);

    pinMode(PIN_M1_PWM, OUTPUT);
    pinMode(PIN_M2_PWM, OUTPUT);
    pinMode(PIN_M3_PWM, OUTPUT);
    pinMode(PIN_M4_PWM, OUTPUT);

    // Ensure all motors are OFF at boot
    stopAllMotors();

    // Set 20 kHz smooth PWM frequency on all 4 motor pins
    analogWriteFrequency(PIN_M1_PWM, 20000);
    analogWriteFrequency(PIN_M2_PWM, 20000);
    analogWriteFrequency(PIN_M3_PWM, 20000);
    analogWriteFrequency(PIN_M4_PWM, 20000);

    Serial.begin(115200);
    delay(1000);

    Serial.println("\n============================================");
    Serial.println("  TCE_rev1: ALL 4 MOTORS VERIFICATION TEST  ");
    Serial.println("============================================");
    Serial.println("M1 -> GPIO4 | J4 (Rear-Right,  CW )");
    Serial.println("M2 -> GPIO5 | J5 (Front-Right, CCW)");
    Serial.println("M3 -> GPIO6 | J6 (Rear-Left,   CCW)");
    Serial.println("M4 -> GPIO7 | J7 (Front-Left,  CW )");
    Serial.println("\nEnsure 1S LiPo battery is connected & SW3 is ON!\n");

    // 3 short warning beeps before spinning
    Serial.println("Starting in 3 seconds...");
    for (int i = 0; i < 3; i++) {
        digitalWrite(PIN_BUZZER, HIGH);
        digitalWrite(PIN_STATUS_LED, HIGH);
        delay(100);
        digitalWrite(PIN_BUZZER, LOW);
        digitalWrite(PIN_STATUS_LED, LOW);
        delay(900);
    }
}

void loop() {
    digitalWrite(PIN_ARM_LEDS, HIGH);

    // =============================================================
    // PHASE 1: TEST EACH MOTOR INDIVIDUALLY (2 SECONDS EACH)
    // =============================================================

    // --- MOTOR 1: Rear-Right (CW) ---
    Serial.println(">>> [1/4] Spinning MOTOR 1 (Rear-Right, CW) on GPIO4...");
    digitalWrite(PIN_STATUS_LED, HIGH);
    analogWrite(PIN_M1_PWM, PWM_SPIN_LOW);
    delay(2000);
    stopAllMotors();
    digitalWrite(PIN_STATUS_LED, LOW);
    delay(1000);

    // --- MOTOR 2: Front-Right (CCW) ---
    Serial.println(">>> [2/4] Spinning MOTOR 2 (Front-Right, CCW) on GPIO5...");
    digitalWrite(PIN_STATUS_LED, HIGH);
    analogWrite(PIN_M2_PWM, PWM_SPIN_LOW);
    delay(2000);
    stopAllMotors();
    digitalWrite(PIN_STATUS_LED, LOW);
    delay(1000);

    // --- MOTOR 3: Rear-Left (CCW) ---
    Serial.println(">>> [3/4] Spinning MOTOR 3 (Rear-Left, CCW) on GPIO6...");
    digitalWrite(PIN_STATUS_LED, HIGH);
    analogWrite(PIN_M3_PWM, PWM_SPIN_LOW);
    delay(2000);
    stopAllMotors();
    digitalWrite(PIN_STATUS_LED, LOW);
    delay(1000);

    // --- MOTOR 4: Front-Left (CW) ---
    Serial.println(">>> [4/4] Spinning MOTOR 4 (Front-Left, CW) on GPIO7...");
    digitalWrite(PIN_STATUS_LED, HIGH);
    analogWrite(PIN_M4_PWM, PWM_SPIN_LOW);
    delay(2000);
    stopAllMotors();
    digitalWrite(PIN_STATUS_LED, LOW);
    delay(1500);

    // =============================================================
    // PHASE 2: ALL 4 MOTORS TOGETHER (SYNCHRONOUS CRUISE)
    // =============================================================
    Serial.println(">>> [ALL] SPINNING ALL 4 MOTORS TOGETHER!");
    digitalWrite(PIN_STATUS_LED, HIGH);

    // Start all 4 at gentle speed (~16% throttle)
    analogWrite(PIN_M1_PWM, PWM_SPIN_LOW);
    analogWrite(PIN_M2_PWM, PWM_SPIN_LOW);
    analogWrite(PIN_M3_PWM, PWM_SPIN_LOW);
    analogWrite(PIN_M4_PWM, PWM_SPIN_LOW);
    delay(2000);

    // Accelerate all 4 to medium speed (~31% throttle)
    Serial.println(">>> [ALL] Accelerating to 30% throttle...");
    analogWrite(PIN_M1_PWM, PWM_SPIN_MED);
    analogWrite(PIN_M2_PWM, PWM_SPIN_MED);
    analogWrite(PIN_M3_PWM, PWM_SPIN_MED);
    analogWrite(PIN_M4_PWM, PWM_SPIN_MED);
    delay(2500);

    // Stop all and pause
    Serial.println(">>> [ALL] STOPPED. Pausing 4 seconds before next cycle.\n");
    stopAllMotors();
    digitalWrite(PIN_STATUS_LED, LOW);
    digitalWrite(PIN_ARM_LEDS, LOW);
    delay(4000);
}
