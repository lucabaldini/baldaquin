#include <HTS221Sensor.h>
#include <LPS22HBSensor.h>

#define DEV_I2C Wire
#define SerialPort Serial

// Components.
HTS221Sensor HumTemp(&DEV_I2C);
LPS22HBSensor PressTemp(&DEV_I2C);

// Global variables.
uint8_t readout_code;
float humidity, temperature1, pressure, temperature2;


void setup() {
  // Led.
  pinMode(LED_BUILTIN, OUTPUT);

  // Initialize serial for output.
  SerialPort.begin(115200);

  // Initialize I2C bus.
  DEV_I2C.begin();

  // Initialize components.
  HumTemp.begin();
  HumTemp.Enable();
  PressTemp.begin();
  PressTemp.Enable();
  //AccGyr.begin();
  //AccGyr.Enable_X();
  //AccGyr.Enable_G();
  //Acc2.begin();
  //Acc2.Enable();
  //Mag.begin();
  //Mag.Enable();
}

void loop() {

  if (Serial.available() > 0) {
    readout_code = Serial.read();
    digitalWrite(LED_BUILTIN, HIGH);
    // Read humidity and temperature.
    HumTemp.GetHumidity(&humidity);
    HumTemp.GetTemperature(&temperature1);
    // Read pressure and temperature.
    PressTemp.GetPressure(&pressure);
    PressTemp.GetTemperature(&temperature2);

    Serial.print('#');
    Serial.print(humidity, 2);
    Serial.print(';');
    Serial.print(temperature1, 2);
    Serial.print(';');
    Serial.print(pressure, 2);
    Serial.print(';');
    Serial.print(temperature2, 2);
    Serial.print('#');
    delay(250);
    digitalWrite(LED_BUILTIN, LOW);
  }

}