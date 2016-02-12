
const int maxButton = 3; // 2 if you just want response buttons; 3 if you want "go" button
const int analogErrorWindow = 50; // error window for reading analog input (buttons)
int ledPin = 3;      // LED connected to digital pin 9
int buttonPin = 0;   // switch circuit input connected to analog pin 3
String pythonSays; // for reading commands from pythonboolean go = false;

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

  while (Serial.available() <= 0) {
    // wait for serial input
  }
  //get instructions from python over serial connection
  pythonSays = Serial.readString();

  //checking serial connection
  if (pythonSays == "ping") {
    Serial.println("ack");

  // get responses
  } else if (pythonSays == "go") {

    // get the response
    get_response();
 
  // other
  } else {
    Serial.print("I don't understand: ");
    Serial.println(pythonSays);
  }
}

void get_response() {
  int buttonValue = 0;
  int button = -1;
   
  while (button <= 0 or button > maxButton) {
    buttonValue = analogRead(buttonPin);
    if( buttonValue >= (767-analogErrorWindow) and buttonValue <= (767+analogErrorWindow) ) { 
      button = 1;
      
    } else if ( buttonValue >= (512-analogErrorWindow) and buttonValue <= (512+analogErrorWindow) ) { 
     button = 2;
     
    } else if ( buttonValue >= (256-analogErrorWindow) and buttonValue <= (256+analogErrorWindow) ) { 
     button = 3;
    } else
     button = 0;  // no button found to have been pushed 
  }
  Serial.println("response");
  Serial.println(button);
}
