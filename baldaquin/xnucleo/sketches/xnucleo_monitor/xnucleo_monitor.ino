#include <HTS221Sensor.h>
#include <LPS22HBSensor.h>

#define DEV_I2C Wire
#define SerialPort Serial

// Components.
HTS221Sensor HumTemp(&DEV_I2C);
LPS22HBSensor PressTemp(&DEV_I2C);

// Sketch identification.
char* sketch_name = "xnucleo_monitor";
uint8_t sketch_version = 2;

// Global variables.
char header = '#';
char separator = ';';
char line_feed = '\n';
uint8_t readout_code;
uint16_t adc1, adc2;
float humidity, temperature1, pressure, temperature2;


void handshake() {
  // Handshake with the host.
  Serial.print(header);
  Serial.print(sketch_name);
  Serial.print(separator);
  Serial.print(sketch_version);
  Serial.print(line_feed);
}


void setup() {
  // Setting up the led---we want to have it blinking when we read data.
  pinMode(LED_BUILTIN, OUTPUT);

  // Initialize serial for output---note the baud rate is hard-coded and we should
  // make sure we do the same thing on the client side.
  SerialPort.begin(115200);

  // Initialize I2C bus.
  DEV_I2C.begin();

  // Initialize the necessary sensors.
  HumTemp.begin();
  HumTemp.Enable();
  PressTemp.begin();
  PressTemp.Enable();

  handshake();
}


void loop() {
  // The event loop is entirely embedded into this if---since this application
  // is driven by the host PC, the arduino board is idle until it receives a byte
  // for the serial port, which triggers a readout cycle.
  if (Serial.available() > 0) {

    // Note at this time we are not doing anything with the command byte, and assume
    // that, whatever value is received, we just trigger a full readout cycle.
    // At some point we might be fancier and do different things depending on the
    // input value, e.g., read or not specific pieced.
    readout_code = Serial.read();

    // Led on.
    digitalWrite(LED_BUILTIN, HIGH);

    // Read humidity and temperature.
    HumTemp.GetHumidity(&humidity);
    HumTemp.GetTemperature(&temperature1);
    // Read pressure and temperature.
    PressTemp.GetPressure(&pressure);
    PressTemp.GetTemperature(&temperature2);
    // Read the two arduino analog channels.
    adc1 = analogRead(0);
    adc2 = analogRead(1);

    // Write the stuff to the serial port.
    Serial.print(header);
    Serial.print(humidity, 3);
    Serial.print(separator);
    Serial.print(temperature1, 3);
    Serial.print(separator);
    Serial.print(pressure, 3);
    Serial.print(separator);
    Serial.print(temperature2, 3);
    Serial.print(separator);
    Serial.print(adc1);
    Serial.print(separator);
    Serial.print(adc2);
    Serial.print(header);

    // Led off.
    digitalWrite(LED_BUILTIN, LOW);
  }
}
