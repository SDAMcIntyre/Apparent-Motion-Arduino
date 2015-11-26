const int vibMax=4;
int nVibToUse=vibMax;
int vibArray[vibMax] = {5,6,10,11};
int onset[vibMax];
int offset[vibMax];
boolean reportBack = true;
boolean go = false;
boolean finished = false;
String pythonSays;
int iOn=0;
int iOff=0;
unsigned long startTime;
unsigned long currentTime;

void setup(){
  // make serial connection
  Serial.begin(115200);
  serial_connect();

  // pins for driving vibrators
  int pin;
  for (pin=0; pin<nVibToUse; pin++) {
    pinMode(vibArray[pin], OUTPUT);
  }
}

void loop() {

  if (go == false) {
    // get stimulus parameters
    nVibToUse = serial_getInt(reportBack);
    serial_getArray(vibArray,nVibToUse,reportBack);
    serial_getArray(onset,nVibToUse,reportBack);
    serial_getArray(offset,nVibToUse,reportBack);

    // wait for go signal
    pythonSays = serial_getString(reportBack);
    if (pythonSays == "go") {
      go = true;
      startTime = millis();
    }
  }
  
  else {
    while (finished == false){
      currentTime = millis();
      if (currentTime - startTime >= (unsigned long) onset[iOn]) {
        digitalWrite(vibArray[iOn], HIGH);
        Serial.print(currentTime-startTime);
        Serial.print(": ");
        Serial.print(vibArray[iOn]);
        Serial.println(" on");
        if (iOn < nVibToUse-1) iOn++;
      }
      if (currentTime - startTime >= (unsigned long) offset[iOff]) {
        digitalWrite(vibArray[iOff], LOW);
        Serial.print(currentTime-startTime);
        Serial.print(": ");
        Serial.print(vibArray[iOff]);
        Serial.println(" off");
        if (iOff < nVibToUse-1) {
          iOff++;
        }
        else {
          finished = true;
          Serial.println(currentTime-startTime);  
          Serial.println("finished");
        }
      }
    }
  }
}

void serial_connect(){
  String connectString;
  while (Serial.available() <= 0){
    // wait
  }
  connectString = Serial.readString();
  Serial.println(connectString);
}

String serial_getString(boolean confirm) {
  String serialStr;
  while (Serial.available() <= 0){
    // wait
  }
  serialStr = Serial.readString();
  if (confirm) {
    Serial.println(serialStr);
  }
  return serialStr;  
}

int serial_getInt(boolean confirm){
  int serialInt;
  while (Serial.available() <= 0){
    // wait
  }
  serialInt = Serial.parseInt();
  if (confirm) {
    Serial.println(serialInt);
  }
  return serialInt;
}

void serial_getArray(int serialArray[], int arrayLength, boolean confirm){
  int i=0;
  while (Serial.available() <= 0){
    // wait
  }
  for (i=0; i<arrayLength; i++) {
    serialArray[i] = Serial.parseInt();
    if (confirm) {
      Serial.print(serialArray[i]);
      if (i < arrayLength - 1) {
        Serial.print(",");
      }
    }
  }
  if (confirm) {
    Serial.println();
  }
  Serial.read();
}

