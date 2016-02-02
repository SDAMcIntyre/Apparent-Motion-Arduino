/* Apparent Motion v1.0 by Sarah McIntyre
 * Last updated 2nd Feb 2016
 *  
 * Up to 4 tactile actuators (e.g. vibrators, solenoids) can be used
 * to create an apparent motion stimulus.
 * 
 * Timing and order are supplied by a python script ApparentMotion.py
 * via serial connection
 * 
 * Button responses are recorded and sent back to python
 */

// stimulus variables (set to defaults)
const int stimMax=4;
int nStimToUse = stimMax;
int stimArray[stimMax] = {5,6,10,11};
int onset[stimMax] = {0,50,100,150};
int offset[stimMax] = {60,110,160,210};

// response variables
const int buttonArray[3] = {2,3,4};

// control variables
const int ledPin = 13;
String pythonSays; // for reading commands from pythonboolean go = false;

void setup(){
  //pin for driving LED
  pinMode(ledPin, OUTPUT);
  
  // pins for driving stimuli
  int pin;
  for (pin=0; pin<nStimToUse; pin++) {
    pinMode(stimArray[pin], OUTPUT);
  }

  // pins for button responses
  for (pin=0; pin<3; pin++) {
    pinMode(buttonArray[pin], INPUT);
  }

  // make serial connection
  Serial.begin(9600);
  Serial.setTimeout(10);
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

  // receive stimulus parameters
  } else if (pythonSays == "stim") {
    nStimToUse = serial_getInt(true);
    serial_getArray(stimArray,nStimToUse,true);
    serial_getArray(onset,nStimToUse,true);
    serial_getArray(offset,nStimToUse,true);

  // play stim
  } else if (pythonSays == "go") {

    // play the stimulus
    play_stim();

    // get the response
    get_response();

  
  // other
  } else {
    Serial.print("I don't understand: ");
    Serial.println(pythonSays);
  }
}

// FUNCTIONS

void get_response() {
  boolean buttonPressed = false;
  int buttonValue = -1;
  
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
}

void play_stim() {
  unsigned long startTime;
  unsigned long currentTime;
  boolean finishedOn = false; // have all stimuli been turned on
  boolean finishedOff = false; // have all stimuli been turned off again
  int iOn = 0; // iterate through onset times
  int iOff = 0; // iterate through offset times

  Serial.println("stimulus");
  startTime = millis();
  
  while (finishedOff == false) {
    currentTime = millis();

    // turning stimuli on
    if (finishedOn == false) {
      if (currentTime - startTime >= (unsigned long) onset[iOn]) {
        digitalWrite(stimArray[iOn], HIGH);
        Serial.print(currentTime-startTime);
        Serial.print(" ms: ");
        Serial.print(stimArray[iOn]);
        Serial.println(" on");
        if (iOn < nStimToUse-1) {
          iOn++;
        } else finishedOn = true;
      }
    }

    // turning stimuli off
    if (currentTime - startTime >= (unsigned long) offset[iOff]) {
      digitalWrite(stimArray[iOff], LOW);
      Serial.print(currentTime-startTime);
      Serial.print(" ms: ");
      Serial.print(stimArray[iOff]);
      Serial.println(" off");
      if (iOff < nStimToUse-1) {
        iOff++;
      } else finishedOff = true;
    }
    
  }
}

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

int serial_getInt(boolean echo){
  if (echo) Serial.println(pythonSays);
  int serialInt;
  while (Serial.available() <= 0){
    // wait
  }
  serialInt = Serial.parseInt();
  if (echo) Serial.println(serialInt);
  return serialInt;
}

void serial_getArray(int serialArray[], int arrayLength, boolean echo){
  if (echo) Serial.println(pythonSays);  
  int i=0;
  while (Serial.available() <= 0){
    // wait
  }
  for (i=0; i<arrayLength; i++) {
    serialArray[i] = Serial.parseInt();
    if (echo) {
      Serial.print(serialArray[i]);
      if (i < arrayLength - 1) {
        Serial.print(",");
      }
    }
  }
  if (echo) Serial.println();
  Serial.readString(); // clear brackets
}

