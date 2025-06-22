const int ledPins[4] = {0, 2, 3, 0}; 
const int ledButtonPins[4] = {0, 4, 5, 8}; 
bool lastButtonStatesLed[4] = {HIGH, HIGH, HIGH, HIGH};

const int pirPins[4] = {0, 0, 13, 0};
bool lastMotionStates[4] = {LOW, LOW, LOW, LOW};

const int pirLeds[4] = {0, 0, 12, 0}; 
const int pirButtonPins[4] = {0, 0, 11, 0};
bool lastButtonStatesPirLed[4] = {HIGH, HIGH, HIGH, HIGH};

bool pirEnabled[4] = {false, false, true, false}; // exemple : seul PIR[2] activé

const int rollerShades[4] = {0, 0, 7, 0}; 
const int rollerShadesButton[4] = {0, 0, 4, 0}; 
bool lastButtonRoller[4] = {LOW, LOW, LOW, LOW};

const int airControl[4] = {0, 0, A2, 0}; 
const int airControlButton[4] = {0, 0, 10, 0};
const int airControlLed[4] = {0, 0, 9, 0}; 
bool lastButtonAirControl[4] = {LOW, LOW, LOW, LOW};

const int buzzerPin = 6;
const int tempPin = A1;
const int gasPin = A0;
const int FANPINs = A2;
float temperature;

unsigned long lastTempTime = 0;
unsigned long lastGasTime = 0;
unsigned long lastBuzzTime = 0;
int buzzDuration = 0;

void setup() {
  Serial.begin(9600);
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);
  for (int i = 2; i < 3; i++) {
    pinMode(ledPins[i], OUTPUT);
    pinMode(ledButtonPins[i], INPUT_PULLUP);
    pinMode(pirPins[i], INPUT);
    pinMode(rollerShades[i], OUTPUT);
    pinMode(rollerShadesButton[i], INPUT_PULLUP);
    pinMode(pirLeds[i], OUTPUT);
    pinMode(pirButtonPins[i], INPUT_PULLUP);
    pinMode(ledPins[i], OUTPUT);
    pinMode(ledPins[i], OUTPUT);

    pinMode(airControl[i], OUTPUT);
    pinMode(airControlLed[i], OUTPUT);
    pinMode(airControlButton[i], INPUT_PULLUP);
  }

}

void buzz(int durationMs) {
  digitalWrite(buzzerPin, HIGH);
  lastBuzzTime = millis();
  buzzDuration = durationMs;
}
void buzzDuringRollerMovement(int durationMs) {
  unsigned long start = millis();
  while (millis() - start < durationMs) {
    digitalWrite(buzzerPin, HIGH);
    delay(100); // Durée du bip
    digitalWrite(buzzerPin, LOW);
    delay(200); // Pause entre bips
  }
}


void handleBuzz() {
  if (buzzDuration > 0 && millis() - lastBuzzTime >= buzzDuration) {
    digitalWrite(buzzerPin, LOW);
    buzzDuration = 0;
  }
}

void loop() {

  unsigned long now = millis();

  // TEMPÉRATURE toutes les 1000ms
   if (false) {
  //if (now - lastTempTime >= 1000) {
    int val = analogRead(tempPin);
    temperature = val * (5.0 / 1024.0) * 100.0;
    Serial.print("TEMP:");
    Serial.println(temperature);
    lastTempTime = now;
  }

  // GAZ toutes les 2000ms
 // if (false) {
  if (now - lastGasTime >= 4000) {
    int gasVal = analogRead(gasPin);
    Serial.print("Sensor Value: ");
    Serial.print(gasVal);
    if (gasVal > 300) {
      Serial.print(" | Smoke detected!");
      buzz(900);
    }
    Serial.println();
    lastGasTime = now;
  }

  // Gérer les boutons LEDS
  for (int i = 2; i < 3; i++) {
    bool state = digitalRead(ledButtonPins[i]);
    if (state != lastButtonStatesLed[i]) {
      if (state == LOW) {
        Serial.print(i + 1);
        Serial.println(":LED_BUTTON_PRESSED");
      }
      lastButtonStatesLed[i] = state;
    }
  }
    // Gérer les boutons Motion LEDS
  for (int i = 2; i < 3; i++) {
    bool state = digitalRead(pirButtonPins[i]);
    if (state != lastButtonStatesPirLed[i]) {
      if (state == LOW) {
        Serial.print(i + 1);
        Serial.println(":MOTION_LED_BUTTON_PRESSED");
      }
      lastButtonStatesPirLed[i] = state;
    }
  }
    // Gérer les boutons rollerShades
  for (int i = 2; i < 3; i++) {
    bool state = digitalRead(rollerShadesButton[i]);
    if (state != lastButtonRoller[i]) {
      if (state == LOW) {
        Serial.print(i + 1);
        Serial.println(":ROLLER_BUTTON_PRESSED");
      }
      lastButtonRoller[i] = state;
    }
  }
      // Gérer les boutons Aircontroll
  for (int i = 2; i < 3; i++) {
    bool state = digitalRead(airControlButton[i]);
    if (state != lastButtonAirControl[i]) {
      if (state == LOW) {
        Serial.print(i + 1);
        Serial.println(":AIR_BUTTON_PRESSED");
      }
      lastButtonAirControl[i] = state;
    }
  }

  // Gérer les capteurs PIR
  for (int i = 2; i < 3; i++) {
    if (pirEnabled[i]) {
    bool motion = digitalRead(pirPins[i]);
    if (motion != lastMotionStates[i]) {
      if (motion == HIGH) {
        Serial.print(i + 1);
        Serial.println(":MOTION_DETECTED");
      }
      lastMotionStates[i] = motion;
    }
    }
  }

  // Commandes via Serial
  if (Serial.available()) {
  String command = Serial.readStringUntil('\n');
  command.trim();

  int sepIndex = command.indexOf(':');
  if (sepIndex != -1) {
    String id = command.substring(0, sepIndex);
    String state = command.substring(sepIndex + 1);

    // Commande LED (ex: "LED1:ON")
    if (id.startsWith("LED")) {
      int ledIndex = id.substring(3).toInt() - 1;
      if (ledIndex >= 0 && ledIndex < 4) {
        digitalWrite(ledPins[ledIndex], (state == "ON") ? HIGH : LOW);
        buzz(300);
      }
    }

    // Commande RollerShades (ex: "ROLLER1:ON")
    if (id.startsWith("ROLLER")) {
      int rollerIndex = id.substring(6).toInt() - 1;
      if (rollerIndex >= 0 && rollerIndex < 4) {
        digitalWrite(rollerShades[rollerIndex], (state == "ON") ? HIGH : LOW);
        buzzDuringRollerMovement(2000);
      }
    }
        // Commande AIRCONTROL 
    if (id.startsWith("AIR")) {
      int airIndex = id.substring(3).toInt() - 1;
      if (airIndex >= 0 && airIndex < 4) {
        digitalWrite(airControl[airIndex], (state == "ON") ? HIGH : LOW);
        digitalWrite(airControlLed[airIndex], (state == "ON") ? HIGH : LOW);
        
      }
    }
        // Commande MOTION_STATUS 
    if (id.startsWith("MOTION")) {
      int PirIndex = id.substring(6).toInt() - 1;
      if (PirIndex >= 0 && PirIndex < 4) {
        digitalWrite(pirLeds[PirIndex], (state == "ON") ? HIGH : LOW);
        buzz(300);
      }
    }
  }
}


  handleBuzz(); // Vérifie si le buzzer doit s'éteindre
}
