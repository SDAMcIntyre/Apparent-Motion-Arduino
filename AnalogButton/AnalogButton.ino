
int ledPin = 3;     
int buttonPin = 0;   // analog pin for buttons
const int nButtons = 3; 
const int buttonReadValues[3] = {767,512,256}; // expected analog read values for each button
const int analogErrorWindow = 50; // error window for reading analog input (buttons)
int buttonValue = 0;

void setup(){
 //pin for driving LED
 pinMode(ledPin, OUTPUT); 

 // pin for button responses
 digitalWrite(14+buttonPin, HIGH); // enable the 20k internal pullup

 // make serial connection
 Serial.begin(9600);
 Serial.setTimeout(10);
}


void loop() {
  buttonValue = analogRead(buttonPin);
  Serial.println(buttonValue);
  for (int b=0; b<nButtons; b++) {
    if ( buttonValue >= (buttonReadValues[b]-analogErrorWindow) and buttonValue <= (buttonReadValues[b]+analogErrorWindow) ) {
      Serial.print("button pressed: ");
      Serial.println(b);
      digitalWrite(ledPin, HIGH);
    }
  }
  delay(200);
  digitalWrite(ledPin, LOW);
}

