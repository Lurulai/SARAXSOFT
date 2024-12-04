#include <Arduino.h>

void setup() {
    Serial.begin(9600);
    int arr[8] = {4, 5, 6, 7, 8, 9, 10, 11};

    // Set each pin as input with the internal pull-up resistor enabled
    for (int id : arr) {
        pinMode(id, INPUT_PULLUP);
    }
}

void loop() {
    int arr[8] = {4, 5, 6, 7, 8, 9, 10, 11};
    for (int id : arr) {
        // Check if the pin is connected to GND (reads LOW)
        if (digitalRead(id) == LOW) {
            //Serial.print("Pin ");
            Serial.println(id);
            //Serial.println(" is connected to GND");
        }
 
        delay(100);
    }
}

