unsigned long duration = 2000UL;
unsigned long startTime;
boolean go = true;
boolean finished = false;

void setup() {
  // put your setup code here, to run once:
  pinMode(5, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (go) {
    startTime = millis();
    while (finished == false){
      if (millis() - startTime > duration) {
        digitalWrite(5, LOW);
        finished = true;
      }
      else if (millis() - startTime > 0UL) {
        digitalWrite(5, HIGH);
      }
    }
  }
}
