#include <HTS221Sensor.h>
#include <LPS22HBSensor.h>

#define DEV_I2C Wire
#define SerialPort Serial

// Components.
HTS221Sensor HumTemp(&DEV_I2C);
LPS22HBSensor PressTemp(&DEV_I2C);

// Global variables.
char line_header = '#';
char line_separator = ';';
char line_feed = '\n';
uint8_t readout_code;
uint16_t adc1, adc2;
float humidity, temperature1, pressure, temperature2;


// Basic readout structure.
struct readout_t {
  float humidity;
  float temperature1;
  float pressure;
  float temperature2;
  uint16_t adc1;
  uint16_t adc2;
};


/* Handshake function.
 *
 * This function is called at the beginning of the sketch to send a handshake
 * message to the host PC. The message contains the sketch name and version.
 * The format of the message is:
 * #<sketch_name>;<sketch_version>\n
 *
 * This is a good candidate to be factored out in a library, if we settle on
 * this type of protocol.
 */
void handshake(char* sketch_name, int sketch_version) {
  Serial.print(line_header);
  Serial.print(sketch_name);
  Serial.print(line_separator);
  Serial.print(sketch_version);
  Serial.print(line_feed);
}


// Write a single readout to the serial port.
void write_readout(readout_t readout){
  Serial.print(line_header);
  Serial.print(readout.humidity, 3);
  Serial.print(line_separator);
  Serial.print(readout.temperature1, 3);
  Serial.print(line_separator);
  Serial.print(readout.pressure, 3);
  Serial.print(line_separator);
  Serial.print(readout.temperature2, 3);
  Serial.print(line_separator);
  Serial.print(readout.adc1);
  Serial.print(line_separator);
  Serial.print(readout.adc2);
  Serial.print(line_feed);
}


// setup() function.
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

  handshake("xnucleo_monitor", 3);
}


// loop() function.
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

    // Write the readout to the serial port.
    readout_t readout = {humidity, temperature1, pressure, temperature2, adc1, adc2};
    write_readout(readout);

    // Led off.
    digitalWrite(LED_BUILTIN, LOW);
  }
}
