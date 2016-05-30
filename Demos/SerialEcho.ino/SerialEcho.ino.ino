String serialSays;
void setup() {
  Serial.begin(9600);
  Serial.setTimeout(10);
}

void loop() {
  while (Serial.available() <= 0) {
    // wait for serial input
  }
  
  serialSays = Serial.readString();
  Serial.println(serialSays);

}
