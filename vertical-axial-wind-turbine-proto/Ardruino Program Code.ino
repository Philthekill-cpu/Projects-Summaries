//////////////////////////////////////////////////////////User_Inputs//
int readPin = A3;
int outPin = 4;
float MinVolt = 0.9;   // Minimum Voltage                       //
float MaxVolt = 5.0;   // Maximum Voltage                       //
int SleepTime = 400;        // Morse Code Dit Time (ms)              //
int message[90] = {1,0,1,0,0,0,1,1,1,0,   // Morse Code Message      //
                   0,0,0,0,0,0,1,0,1,0,                              // 
                   0,0,1,0,1,0,1,0,0,0,                              //
                   0,0,0,0,1,0,1,1,1,0,                              //
                   1,1,1,0,0,0,1,0,1,0,                              //
                   0,0,1,1,1,0,1,0,0,0,                              //
                   1,1,1,0,1,0,1,0,0,0,                              //
                   1,1,1,0,1,0,1,1,1,0,                              //
                   1,1,1,1,0,0,0,0,0,0};    




void setup() {
  // put your setup code here, to run once:
// Start serial communication with a baud rate of 9600
  Serial.begin(9600);
  
  // Set pin A3 as INPUT
  pinMode(A3, INPUT);
  
  // Set pin 4 as OUTPUT
  pinMode(4, OUTPUT);



}

void loop() {
  // put your main code here, to run repeatedly:

  int measurement = analogRead(readPin); //measurement can be any number from 0 to 1023
  float Vin = (5.0 / 1023.0) * measurement;
 
  if ((Vin >= MinVolt) and (Vin <= MaxVolt)) { //checking if the voltage is within the desired range
    for (int position = 0; position < 90; position++) {
      measurement = analogRead(readPin);
      Vin = (5.0 / 1023.0) * measurement; // transform the voltage from volts  into an arduino scale from 0 to 1023   
      Serial.println(Vin); //print voltage on screen
      delay(SleepTime);

       if ((Vin < MinVolt) or (Vin > MaxVolt)){  // Stop reading morse code if voltage is not within range. 
        digitalWrite(outPin, LOW);
        break;
      } else if (message[position] == 1) {                // Assigning high to 1 and low to 0 
        digitalWrite(outPin, HIGH);
        Serial.println("HIGH");
        //delay(1000);
      } else {
        digitalWrite(outPin, LOW);
      }
    }
  } else {                                                // Initial checked voltage invalid
    Serial.println(Vin);
    digitalWrite(outPin,LOW);
    delay(SleepTime);
  }
}
