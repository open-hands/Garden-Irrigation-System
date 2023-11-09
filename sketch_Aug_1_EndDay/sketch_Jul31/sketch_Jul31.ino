#define BaudRate 9600
#define FlowSensorPin 40                                                             // Set flow sensor to pin 40

char currentState = 'Z';                                                             // The variable to be changed to transition to another case
char ByteRead = 'C';
int watering_needed = 0;
String temp = " ";
int tempval = 0;
int tank_dry;

boolean Error = false;

int valve_relay_pins[] = {22, 23, 24, 25, 26, 27, 28, 29};                           // Array defining the relay pins
int sensor_pwr_pins[] = {30, 31, 32, 33, 34, 35, 36, 37};                            // Array defining the power pins
int sensor_analog_read[] = {0, 1, 2, 3, 4, 5, 6, 7};                                 // Array defining the sensor pins
int ErrorPins[] = {2,3,4,5,6,7,8,9};                                                 // Array defining the error pins
int pump_relay_pin = 38;                                                             // Pin the pump relay is connected to, On-Off

float percent[8];                                                                    // Store sensor outputs in percentage out of [maxvolt] volts
float StartPercent[8];                                                               // Store sensor outputs in percentage out of [maxvolt] volts, read at START of watering
float EndPercent[8];                                                                 // Store sensor outputs in percentage out of [maxvolt] volts, read at END of watering

int maxvolt = 3.3;                                                                     // The maximum output value of the moisture sensors, temp value TBD later

int BNW[] = {1, 1, 1, 1, 1, 1, 1, 1};                                                // 0 means bed needs watering
int threshold[] = {50, 50, 50, 50, 50, 50, 50, 50};                                  // Actual thresholds for each individual bed, comes from Pi, this defaults them to 50%
int Auto_BedStates[] = {0, 0, 0, 0, 0, 0, 0, 0};                                     // 0 means no plants in that bed, don't bother watering, comes from Pi
int HoseType[] = {0, 0, 0, 0, 0, 0, 0, 0, 0};  
unsigned long Auto_WaterTimes[] = {5000,5000,5000,5000,5000,5000,5000,5000}; // Default watering times for AUTO and MANUAL to 30seconds
int Manual_BedStates[] = {1, 1, 1, 1, 1, 1, 1, 1};                                   // 0 means no plants in that bed, don't bother watering, comes from Pi

int prime = 1;                                                                       // Variable to change whether PRIME option is turned on

unsigned long duration = 0;
int Hz = 0;
unsigned long currentMillis = 0;
unsigned long previousMillis = 0;

//=== CHANGE ACCORDINGLY ===//

unsigned long DripTape = 135000;                                                    // DripTape duration
unsigned long SoakerHose = 135000;                                                  // Soaker hose duration
unsigned long PumpTime = 15000;                                                       // Pump run duration for priming

//=== ------------------ ===//

int WaterFlowCheck = 1;

void setup() 
{
  Serial.begin(BaudRate);                                                           // Setting up the Serial port for communication
  pinMode(13,OUTPUT);                                                                // Set Pin 13 as output for debugging purposes when watering
  for(int y = 0; y < 8; y++)
  {
    pinMode(sensor_pwr_pins[y], OUTPUT);                                             // Set sensor power pins as OUTPUTS
    pinMode(valve_relay_pins[y], OUTPUT);                                            // Set valve relay pins as OUTPUTS
    pinMode(ErrorPins[y], OUTPUT);                                                   // Set error pins as OUTPUTS
    pinMode(FlowSensorPin, INPUT);                                                   // Set flow sensor pin as INPUT
    digitalWrite(valve_relay_pins[y], HIGH);                                         // Initial states of relay pins, this doesn't draw any current
  }  
  pinMode(pump_relay_pin, OUTPUT);                                                   // Set pump relay pin as OUTPUT
  //pinMode(13, INPUT);
  digitalWrite(13,LOW);                                                              // Set LED off
}

void loop() 
{
  switch (currentState) 
  {
    case 'A': // Initialize or Update 
      digitalWrite(13,HIGH);
      ReceiveData();                                                                 // Fill the arrays with proper information
      ConvertData();                                                                 // Conver necessary data
      currentState = 'Z';
      break;
    
    case 'S': // Automatic watering  
      //digitalWrite(13,LOW);
      digitalWrite(13,HIGH);    
      ReadSensors();                                                                 // Read the sensors
      NeedsWater();                                                                  // Determine which beds need watering
      //FakeWater();                                                                 // Hardcode values to BNW
      AutoWaterBeds();                                                               // Water the appropriate beds with proper durations
      currentState = 'Z';                                                            // Transition to Default case
      break;
    
   case 'M': // Manual watering
      digitalWrite(13,LOW); 
      ManualWaterBeds();                                                             // Manually water the beds
      currentState = 'Z';                                                            // Transition to Default case
      break;
      
    case 'R':
      ReadSensors();
      writePi();
      currentState='Z';
      break;
      
    default:
      break;
  }
  
  while(Serial.available()!=1)                                                      // Wait until there is data in the serial line
  {
    //do nothing here
  }
  MySerialEvent();                                                                   // Check for case transition
}

void MySerialEvent() 
{
  while (Serial.available()) 
  {
    currentState = Serial.read();
  }
}

int FlowCheck()
{
  duration = 0;
  for( int i = 0; i <5; i++)
  {
    duration +=  pulseIn(FlowSensorPin, HIGH);
    delay(1000);    
  }
  duration /= 5;  
  if(duration == 0)
  {
    Hz = 0;
  }
  else
  {
    Hz = 500000/duration; 
  }
  return Hz;
}

void StartRead(int bedNumber)                                                                      // BedNumber indexed at 0 
{                                              
  unsigned long internalDelay = 1000;                                                              // Delay for 1[s] read
  digitalWrite(sensor_pwr_pins[bedNumber], HIGH);                                                  // Turn on sensor
  delay(1000);                                                                                   // Delay time between powerup and read as per vegetronics                                                                  
  StartPercent[bedNumber] = (((analogRead(bedNumber) * 5.0) / (1023.0 * maxvolt))*100);            // Converts analog read to a percent representing [analog voltage] / [maxvolt]
  delay(50);
  StartPercent[bedNumber] = StartPercent[bedNumber] * Auto_BedStates[bedNumber];                   // Will only record the sensor reading if bed is in use                                                                         
  digitalWrite(sensor_pwr_pins[bedNumber], LOW);                                                   // Loop to turn off sensors
}

void EndRead(int bedNumber)                                                                        // BedNumber indexed at 0 
{                                              
  digitalWrite(sensor_pwr_pins[bedNumber], HIGH);                                                  // Turn on sensor
  delay(1000);                                                                                     // Delay time between powerup and read as per vegetronics                                                                   
  EndPercent[bedNumber] = (((analogRead(bedNumber) * 5.0) / (1023.0 * maxvolt))*100);              // Converts analog read to a percent representing [analog voltage] / [maxvolt]
  delay(50);
  EndPercent[bedNumber] = EndPercent[bedNumber] * Auto_BedStates[bedNumber];                       // Will only record the sensor reading if bed is in use                                                                           
  digitalWrite(sensor_pwr_pins[bedNumber], LOW);                                                   // Loop to turn off sensors
}

int ManualWaterBeds()
{
  digitalWrite(13, LOW);
  //previousMillis = 0;
  //currentMillis = 0;
  int fake_result = 0;
  if (prime == 1)                                                                                  // If prime option is turned on, prime
  {
    digitalWrite(13, HIGH);
    digitalWrite(pump_relay_pin, HIGH);
    //delay(PumpTime);
    currentMillis = millis();
    //PumpTime = PumpTime + millis();
    while ((millis() - currentMillis) <= PumpTime)                                          // Delay for PumpTimer duration 
    {
      //currentMillis = millis(); 
    }
  }
  else                                                                                             // If prime option is turned off, don't prime
  {

    digitalWrite(pump_relay_pin, HIGH);
    //prime = 1;                                                                                   // Only set for debugging purposes
  }   
  
  for (int i = 0; i < 8; i++)
  {
    if (Manual_BedStates[i] == 1)
    {                  
      digitalWrite(valve_relay_pins[i], !Manual_BedStates[i]);                                     // Writes to the pin called in the relaypin[i] to be the state of BedNeedsWatering[i] where 0 is relay open, 1 is relay closed
      myDelay(Auto_WaterTimes[i]);
      //Auto_WaterTimes[i] = Auto_WaterTimes[i] + millis();
//      while ((millis() - currentMillis) <= Auto_WaterTimes[i])                               // Delay for PumpTimer duration 
//      {
//        FlowCheck();
//        if (Hz > 100)                                                                               // If flow rate is greater than '10', no error
//        {                                                                                          // Otherwise, error
//          Error = false;
//        }
//        else
//        {
//          Error = true;
//          digitalWrite(valve_relay_pins[i], HIGH);
//          digitalWrite(pump_relay_pin, LOW);
//          break;
//        }
        //currentMillis = millis();
        //digitalWrite(valve_relay_pins[i], HIGH);                                                     // Turns off the relay
        //myDelay(1000);                                                                               //drop lower for delay to the pump so we reduce strain on the pump
    //}
      digitalWrite(valve_relay_pins[i], HIGH);  
      if(tank_dry==1){
        break;
      }
  }
  }
  digitalWrite(pump_relay_pin, LOW);
  watering_needed = 0;
  tempval = watering_needed;
  Serial.print(tempval); 
}


int AutoWaterBeds()                                                                                // Function controls the relays to water the beds according to BNW array   
{                            
  if (prime == 1)
  {
    digitalWrite(pump_relay_pin, HIGH);
    delay(PumpTime);
  }
  else
  {
    digitalWrite(pump_relay_pin, HIGH);
    prime = 1;
  }  
  
  for (int i = 0; i < 8; i++)
  {      
    // NEED WATER FLOW METHOD //  
      if(BNW[i] == 0)                                                                            //only runs bed watering if BNW is 0
      {
        //int num = 0;
        digitalWrite(valve_relay_pins[i], BNW[i]);                                                   // Writes to the pin called in the relaypin[i] to be the state of BedNeedsWatering[i] where 0 is relay open, 1 is relay closed
        //delay(3000);                                                                                // Delay between valve open and pump on
        //digitalWrite(pump_relay_pin, !BNW[i]);                                                       // Turns on the pump relay pin if BNW[i] == 0
        myDelay(Auto_WaterTimes[i]);
        //delay(num);     
        //digitalWrite(pump_relay_pin, 0);                                                             // Turns off the pump
        //delay(3000);                                                                                // Delay between pump off and valve close
        digitalWrite(valve_relay_pins[i], HIGH);                                                     // Turns off the relay
        delay(1000);                                                                                 //drop lower for delay to the pump so we reduce strain on the pump
        if(tank_dry==1){
          break;
        }
      }
      
    } 
  digitalWrite(pump_relay_pin, LOW);
  watering_needed=0;
  tempval=watering_needed;
  Serial.print(tempval);  
}

int NeedsWater()                                                                                   // Populates the BNW array according to percent array, threshold array, and Auto_BedStates array
{                                                       
  for(int i = 0; i < 8; i++)
  {
    if(Auto_BedStates[i] == 1)
    {
      if(percent[i] < threshold[i])
      {
        BNW[i] = 0;
      }
      else
      {
        BNW[i] = 1;
      }
    }
    else
    {
      BNW[i] = 1;
    }
  } 
}

int ReadSensors()
{
  for(int x = 0; x < 8; x++)                                                                      // Loop to turn on sensors
  {                                                
    digitalWrite(sensor_pwr_pins[x], HIGH);
  }
  delay(1000);                                                                                    // Delay time between powerup and read as per vegetronics
  for(int x = 0; x < 8; x++)
  {                                                                                               // Loop to read analog pins form A0 to A7
    percent[x] = (((analogRead(x) * 5.0) / (1023.0 * maxvolt))*100);                              // Converts analog read to a percent representing [analog voltage] / [maxvolt]
    delay(50);
    percent[x] = percent[x] * Auto_BedStates[x];                                                  // Will only record the sensor reading if bed is in use
  }
  for(int x = 0; x < 8; x++)
  {                                                                                               // Loop to turn off sensors
    digitalWrite(sensor_pwr_pins[x], LOW);
  }
}

void ReceiveData()                                                                                // Receive data communication with Pi
{
  ByteRead = 'Z';
  while (ByteRead != 'G')
  {
    ByteRead = Serial.peek();
  }
    // Serial.println("Waiting for write to finish");
  Serial.read(); 
  delay(1500);
  
  for (int i = 0; i < 8; i++)
  {
    temp = Serial.readStringUntil('\n');
    threshold[i]=temp.toInt();
  }    
  ByteRead = 'Z';
  delay(1500);
  while (ByteRead != 'G')
  {
    ByteRead = Serial.peek();
  }
    // Serial.println("Waiting for write to finish");
  Serial.read(); 
  delay(1500);
  
  for (int i = 0; i < 8; i++)
  {
    temp = Serial.readStringUntil('\n');
    Auto_BedStates[i]=temp.toInt();
  }
  ByteRead = 'Z';
  delay(1500);
  while (ByteRead != 'G')
  {
    ByteRead = Serial.peek();
  }
    // Serial.println("Waiting for write to finish");
  Serial.read(); 
  delay(1500);
  
  for (int i = 0; i < 8; i++)
  {
    temp = Serial.readStringUntil('\n');
    HoseType[i]=temp.toInt();
  }
  
  ByteRead = 'Z';
  delay(1500);
  while (ByteRead != 'G')
  {
    ByteRead = Serial.peek();
  }
    // Serial.println("Waiting for write to finish");
  Serial.read(); 
  delay(1500);
  
  for (int i = 0; i < 8; i++)
  {
    temp = Serial.readStringUntil('\n');
    Manual_BedStates[i]=temp.toInt();
  }  
  ByteRead = 'Z';  
}

void writeWatering(){
   for(int i=0;i<8;i++){
     if(BNW[i]==0){
       watering_needed=1;
       break; 
     }
     else{
       watering_needed=0;
     }
   }
   tempval=watering_needed;
   Serial.print(tempval);
   while(Serial.available()>0){}
}

void writePi()
{
  for(int i=0;i<8;i++)
  {
    tempval=percent[i];
    Serial.println(tempval);
  }
}

void ConvertData()
{
  for (int i = 0; i < 8; i++)
  {
    if (HoseType[i] == 0)
    {
      Auto_WaterTimes[i] = DripTape;
    }
    else
    {
      Auto_WaterTimes[i] = SoakerHose;
    }
  }
}
  
void Wait4Pi()
{
  while (Serial.available() > 0)
  {
    delay(250);
  }
}

void FakeWater()
{
  for (int i = 0; i < 8; i++)
  {
    BNW[i] = 1;
  }
  BNW[0] = 0;
}

int myDelay(unsigned long local_duration)
{
  unsigned long local_currentMillis = millis();
  while ((millis() - local_currentMillis) <= local_duration)                          // Delay for flow check 1s duration replacement
  {/*
    FlowCheck();
    if(Hz==0){
      tank_dry=1;
      break;
    }
    else{
      tank_dry=0;
    }*/
  }
  //return tank_dry;

}
