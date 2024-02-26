#include "Arduino.h"
#include "LoRa_E32.h"
#include <SoftwareSerial.h>
#include <DHT11.h>
#include <Servo.h>

// Initialize serial communication and the LoRa module
SoftwareSerial mySerial(2, 3); // RX, TX pins
LoRa_E32 e32ttl100(&mySerial);

// Initialize the servo and ESCs
Servo rudder; 
Servo esc;  
Servo esc2;

// Initialize the DHT11 sensor
DHT11 dht11(13);

// Variables needed for smooth transition
int lastEscPulseWidth = 1500; // Last ESC pulse width
unsigned long lastUpdate = 0; // Time of the last update
const long updateInterval = 20; // Update interval (milliseconds)
float escPulseWidthIncrement = 0; // Increment for each update
const int smoothDuration = 1000; // Duration of the smooth transition (milliseconds)

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
  e32ttl100.begin();

  // Attach the servo and ESCs
  esc.attach(9, 1000, 2000);
  esc2.attach(6, 1000, 2000);
  rudder.attach(11);
}

void loop() {
  // Check if there is data from the LoRa module
  if (e32ttl100.available()) {
    ResponseContainer rc = e32ttl100.receiveMessageUntil('A');
    if (rc.status.code != 1) {
      rc.status.getResponseDescription();
    } else {
      // Parse data and control the servo and ESCs
      if (rc.data.length() == 3 && rc.data.endsWith("B")) {
        int escValue = rc.data.substring(0 , 1).toInt();
        int rudderValue = rc.data.substring(1 , 2).toInt();
        // Map escValue from 1-5 to 1000-2000
        int targetEscPulseWidth = map(escValue, 1, 5, 1000, 2000);
        // Map rudderValue from 1-5 to 0-180
        rudderValue = map(rudderValue, 1, 5, 0, 180);

        // Set the target for smooth transition
        escPulseWidthIncrement = (targetEscPulseWidth - lastEscPulseWidth) / (float)(smoothDuration / updateInterval);
        lastUpdate = millis(); // Reset update time
        rudder.write(rudderValue);
      }
      // Print the received data
      Serial.println(rc.data);
    }
  }

  // Logic for smooth transition
  if (millis() - lastUpdate < smoothDuration && escPulseWidthIncrement != 0) {
    lastEscPulseWidth += escPulseWidthIncrement;
    esc.writeMicroseconds(lastEscPulseWidth);
    esc2.writeMicroseconds(lastEscPulseWidth);
    lastUpdate += updateInterval;
  }

  // Send temperature and humidity data every 10 seconds
  static unsigned long lastSendTime = 0;
  if (millis() - lastSendTime > 10000) {
    lastSendTime = millis();

    int temperature = dht11.readTemperature();
    int humidity = dht11.readHumidity();
    
    String dataToSend = "T" + String(temperature) + "H" + String(humidity) + "F";
    e32ttl100.sendMessage(dataToSend);
  }
}

