String pythonSays;
const int buttonArray[3] = {2,3,4};
int buttonValue = 0;
int response = 99;
boolean buttonPressed = false;

void setup() {
  // put your setup code here, to run once:
  // pins for button responses
  for (int pin=0; pin<3; pin++) {
    pinMode(buttonArray[pin], INPUT);
  }

  // make serial connection
  Serial.begin(9600);
}

void loop() {
  while (Serial.available() <= 0) {
    // wait for serial input
  }

  //get instructions from python over serial connection
  pythonSays = Serial.readString();

  //checking serial connection
  if (pythonSays == "ping") {
    Serial.println("ack");

  // wait for a button press
  } else if (pythonSays == "go") {
    Serial.println(pythonSays);
    while (buttonPressed == false) {
      for (int button = 0; button < 2; button++) {
        buttonValue = digitalRead(buttonArray[button]);
        if (buttonValue > 0) {
          Serial.println("response");
          Serial.println(button);
          buttonPressed = true;
        }
      }
    }
    buttonPressed = false;
  
  // other
  } else Serial.println("try again");
}

// FUNCTIONS

String serial_getString(boolean echo) {
  if (echo) Serial.println(pythonSays);
  String serialStr;
  while (Serial.available() <= 0){
    // wait
  }
  serialStr = Serial.readString();
  if (echo) Serial.println(serialStr);
  return serialStr;  
}
