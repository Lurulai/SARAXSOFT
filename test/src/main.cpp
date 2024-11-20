#include <Arduino.h>

void setup() {
    Serial.begin(9600);
}

void loop() {
   digitalWrite(2,HIGH);
   int arr[8] = {4,5,6,7,8,9,10,11};
   for(int id : arr){
      int check = digitalRead(id);
      if(check){
         Serial.println(id);
      }
   }
   delay(3000);
}
