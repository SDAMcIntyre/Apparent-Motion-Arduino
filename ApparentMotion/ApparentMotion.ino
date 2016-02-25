/* Apparent Motion v1.2 by Sarah McIntyre
 * Last updated 24th Feb 2016
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
int onset[stimMax] = {0,200,400,600};
int offset[stimMax] = {5,205,405,605};

// response variables 
const int buttonPin = 0;   // analog pin for buttons
const int buttonReadValues[3] = {767,512,256};
const int analogErrorWindow = 50; // error window for reading analog input (buttons)
int responseButton[2] = {0,1};
boolean useResponseButtons = true;
int goButton[1] = {2};
boolean useGoButton = true;

// control variables
const int ledPin = 3;
String pythonSays; // for reading commands from python

void setup(){
  //pin for driving LED
  pinMode(ledPin, OUTPUT);
  
  // pins for driving stimuli
  for (int pin=0; pin<nStimToUse; pin++) {
    pinMode(stimArray[pin], OUTPUT);
  }

  // pin for button responses
  digitalWrite(14+buttonPin, HIGH); // enable the 20k internal pullup

  // make serial connection
  Serial.begin(9600);
  Serial.setTimeout(10);
}

void loop() {

  while (Serial.available() <= 0) {
    // wait for serial input
  }
  
  // get instructions from python over serial connection
  pythonSays = Serial.readString();

  // checking serial connection
  if (pythonSays == "ping") {
    Serial.println("ack");

  // use go button
  } else if (pythonSays == "go button on") {
    useGoButton = true;
    Serial.println(pythonSays);
  } else if (pythonSays == "go button off") {
    useGoButton = false;
    Serial.println(pythonSays);
    
  // use response buttons
  } else if (pythonSays == "responses on") {
    useResponseButtons = true;
    Serial.println(pythonSays);
  } else if (pythonSays == "responses off") {
    useResponseButtons = false;
    Serial.println(pythonSays);
    
  // receive stimulus parameters
  } else if (pythonSays == "stim") {
    nStimToUse = serial_get_int(true);
    serial_get_int_array(stimArray,nStimToUse,true);
    serial_get_int_array(onset,nStimToUse,true);
    serial_get_int_array(offset,nStimToUse,true);

  // play stim
  } else if (pythonSays == "go") {
    play_stim();
    if (useResponseButtons) get_response();
  
  // other
  } else {
    Serial.print("I don't understand: ");
    Serial.println(pythonSays);
  }
}

// FUNCTIONS

int get_button_press(int nButtons, int checkButton[]) {
  int buttonValue = 0;
  int button = -1;

  while (button < 0) {
    buttonValue = analogRead(buttonPin);
    for (int b=0; b<nButtons; b++) {
      if ( buttonValue >= (buttonReadValues[checkButton[b]]-analogErrorWindow) and 
      buttonValue <= (buttonReadValues[checkButton[b]]+analogErrorWindow) ) {
        button = checkButton[b];
        digitalWrite(ledPin, HIGH);
      }
    } 
  }
  delay(10);
  digitalWrite(ledPin, LOW);
  return button;
}

void get_response() {
  int pressed = get_button_press(2, responseButton);
  Serial.println("response");
  Serial.println(pressed);
}

void play_stim() {
  unsigned long startTime;
  unsigned long currentTime;
  boolean finishedOn = false; // have all stimuli been turned on
  boolean finishedOff = false; // have all stimuli been turned off again
  int iOn = 0; // iterate through onset times
  int iOff = 0; // iterate through offset times

  if (useGoButton) {
    int pressed = get_button_press(1, goButton);
    }
  delay(500);
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

String serial_get_string(boolean echo) {
  if (echo) Serial.println(pythonSays);
  String serialStr;
  while (Serial.available() <= 0){
    // wait
  }
  serialStr = Serial.readString();
  if (echo) Serial.println(serialStr);
  return serialStr;  
}

int serial_get_int(boolean echo){
  if (echo) Serial.println(pythonSays);
  int serialInt;
  while (Serial.available() <= 0){
    // wait
  }
  serialInt = Serial.parseInt();
  if (echo) Serial.println(serialInt);
  return serialInt;
}

void serial_get_int_array(int serialArray[], int arrayLength, boolean echo){
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

