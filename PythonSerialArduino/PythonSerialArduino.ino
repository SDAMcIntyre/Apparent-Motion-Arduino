String pythonStr;
int pythonInt;
float pythonFloat;
int pythonArray[4];
const int arrayLength = sizeof(pythonArray) / sizeof(int);

void setup() {
  Serial.begin(115200);
  serial_connect();
  pythonStr = serial_getString(true);
  pythonInt = serial_getInt(true);
  pythonFloat = serial_getFloat(true);
  serial_getArray(pythonArray,arrayLength,true);
}

void loop(){ 

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

float serial_getFloat(boolean confirm) {
  float serialFloat;
  while (Serial.available() <= 0){
    // wait
  }
  serialFloat = Serial.parseFloat();
  if (confirm) {
    Serial.println(serialFloat); 
  }
  return serialFloat;
}

void serial_getArray(int serialArray[], int nElements, boolean confirm){
  int i=0;
  while (Serial.available() <= 0){
    // wait
  }
  for (i=0; i<nElements; i++) {
    serialArray[i] = Serial.parseInt();
    if (confirm) {
      Serial.print(serialArray[i]);
      if (i < nElements - 1) {
        Serial.print(",");
      }
    }
  }
  if (confirm) {
    Serial.println();
  }
}


