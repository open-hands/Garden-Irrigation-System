#define BaudRate 9600                                                                // Set Baud Rate of serial communication
#define WaterPin 43                                                                  // Set water pin 43
#define FlowSensorPin 42                                                             // Set flow sensor to pin 42
#define PowerFlowSensorPin 41                                                        // Set power flow sensor to pin 41

// Debug purpose: Set to L to read sensors //
// char currentState = 'L';                                                             // The variable to be changed to transition to another case

char currentState = 'Z';                                                             // The variable to be changed to transition to another case
char ByteRead = 'C';
int watering_needed = 0;
String temp = " ";
int tempval = 0;
int tank_dry;

int valve_relay_pins[] = {22, 23, 24, 25, 26, 27, 28, 29};                           // Array defining the relay pins
int sensor_pwr_pins[] = {30, 31, 32, 33, 34, 35, 36, 37};                            // Array defining the power pins
int sensor_analog_read[] = {0, 1, 2, 3, 4, 5, 6, 7};                                 // Array defining the sensor pins
int ErrorPins[] = {2,3,4,5,6,7,8,9};                                                 // Array defining the error pins
int pump_relay_pin = 38;                                                             // Pin the pump relay is connected to, On-Off

float percent[8];                                                                    // Store sensor outputs in percentage out of [maxvolt] volts
float StartPercent[8];                                                               // Store sensor outputs in percentage out of [maxvolt] volts, read at START of watering
float EndPercent[8];                                                                 // Store sensor outputs in percentage out of [maxvolt] volts, read at END of watering

int EndStartDelta[] = {30, 30, 30, 30, 30, 30, 30, 30};                              // Store delta of sensor output between end and start of water, used in SensorCheck function

int maxvolt = 3.3;                                                                   // The maximum output value of the moisture sensors, temp value TBD later

int BNW[] = {1, 1, 1, 1, 1, 1, 1, 1};                                                // 0 means bed needs watering
int threshold[] = {20, 20, 20, 20, 20, 20, 20, 20};                                  // Actual thresholds for each individual bed, comes from Pi, this defaults them to 50%
int Auto_BedStates[] = {0, 0, 0, 0, 0, 0, 0, 0};                                     // 0 means no plants in that bed, don't bother watering, comes from Pi
int Manual_BedStates[] = {1, 1, 1, 1, 1, 1, 1, 1};                                   // 0 means no plants in that bed, don't bother watering, comes from Pi
int HoseType[] = {0, 0, 0, 0, 0, 0, 0, 0, 0};                                        // Hose type, 0 = DripTape, 1 = SoakerHose
unsigned long Auto_WaterTimes[] = {135000,135000,135000,135000,135000,135000,135000,135000};         // Default watering times for AUTO and MANUAL to 30seconds


int prime = 1;                                                                       // Variable to change whether PRIME option is turned on

int Hz = 0;
unsigned long duration = 0;
unsigned long currentMillis = 0;
unsigned long previousMillis = 0;

int ErrorArray[] = {0, 0, 0, 0, 0, 0, 0, 0, 0};                                      // Indices 0-7 are moisture sensor related errors, Index 8 is flow sensor related error

//======== CHANGE ACCORDINGLY ========//
unsigned long DripTape = 135000;                                                     // DripTape duration
unsigned long SoakerHose = 135000;                                                   // Soaker hose duration
unsigned long PumpTime = 30000;                                                      // Pump run duration for priming
//====================================//



void setup()
{
  Serial.begin(BaudRate);                                                           // Setting up the Serial port for communication
  pinMode(13,OUTPUT);                                                                // Set Pin 13 as output for debugging purposes when watering

  pinMode(FlowSensorPin, INPUT);                                                   // Set flow sensor pin as INPUT
  pinMode(PowerFlowSensorPin, OUTPUT);                                             // Set power flow sensor pin as OUTPUT
  pinMode(WaterPin, OUTPUT);                                                       // Set water pin as OUTPUT

  for(int y = 0; y < 8; y++)
  {
    pinMode(sensor_pwr_pins[y], OUTPUT);                                             // Set sensor power pins as OUTPUTS
    pinMode(valve_relay_pins[y], OUTPUT);                                            // Set valve relay pins as OUTPUTS
    pinMode(ErrorPins[y], OUTPUT);                                                   // Set error pins as OUTPUTS
    digitalWrite(valve_relay_pins[y], HIGH);                                         // Initial states of relay pins, this doesn't draw any current
    // DATA COLLECTION PURPOSES //
    // digitalWrite(sensor_pwr_pins[y], HIGH);
  }
  digitalWrite(WaterPin, LOW);
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
      digitalWrite(13,LOW);
      ReadSensors();                                                                 // Read the sensors
      NeedsWater();                                                                  // Determine which beds need watering
      AutoWaterBeds();                                                               // Water the appropriate beds with proper durations
      AutoSensorCheck();                                                             // Determine error values based on Start and End Percents
      currentState = 'Z';
      break;

    case 'S': // Automatic watering
      digitalWrite(13,LOW);
      //ReadSensors();                                                                 // Read the sensors
      //NeedsWater();                                                                  // Determine which beds need watering
      //AutoWaterBeds();                                                               // Water the appropriate beds with proper durations
      //AutoSensorCheck();                                                             // Determine error values based on Start and End Percents
      currentState = 'Z';                                                            // Transition to Default case
      break;

    case 'M': // Manual watering
      digitalWrite(13,HIGH);
      ReceiveData();                                                                 // Fill the arrays with proper information
      ConvertData();                                                                 // Conver necessary data
      digitalWrite(13,LOW);
      ManualWaterBeds();                                                             // Manually water the beds
      ManualSensorCheck();
      currentState = 'Z';                                                            // Transition to Default case
      break;

    case 'W': // Winterizing
      Winterize();                                                                   // Blow out the system
      currentState = 'Z';

    case 'R':
      ReadSensors();
      SendSensorData();
      currentState = 'Z';
      break;

    case 'E': // Error comms to Pi
      SendErrors();
      currentState = 'Z';
      break;

    case 'L': // Debug read sensors
       for (int i = 0; i < 7; i++)
      {
        Serial.println(readVH400(i));
        //Serial.print(",");
      }
      Serial.println(readVH400(7));
      //Serial.println("");
      currentState = 'L';
      delay(3000);
      break;

    default:
      break;
  }

  while(Serial.available()!=1)                                                      // Wait until there is data in the serial line
  {
  }

  MySerialEvent();                                                                   // Check for case transition
}

void MySerialEvent()
{
    currentState = Serial.read();
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

int AutoSensorCheck()
{
  for (int i = 0; i < 8; i++)
  {
    if (BNW[i] == 1)
    {
      EndStartDelta[i] = EndPercent[i] - StartPercent[i];

      if(EndStartDelta[i] <= 10)
      {
        ErrorArray[i] == 1;
      }
      else
      {
        ErrorArray[i] == 0;
      }
    }
    else
    {
      ErrorArray[i] == 0;
    }
  }
}

int ManualSensorCheck()
{
  for (int i = 0; i < 8; i++)
  {
    if (Manual_BedStates[i] == 1)
    {
      EndStartDelta[i] = EndPercent[i] - StartPercent[i];

      if(EndStartDelta[i] <= 10)
      {
        ErrorArray[i] == 1;
      }
      else
      {
        ErrorArray[i] == 0;
      }
    }
    else
    {
      ErrorArray[i] == 0;
    }
  }
}

void StartRead(int bedNumber)                                                                      // BedNumber indexed at 0
{
  unsigned long internalDelay = 1000;                                                              // Delay for 1[s] read
  digitalWrite(sensor_pwr_pins[bedNumber], HIGH);                                                  // Turn on sensor
  MillisDelay(1000);                                                                              // Delay time between powerup and read as per vegetronics
  StartPercent[bedNumber] = readVH400(bedNumber);                                                  // Obtain VWC
  MillisDelay(50);
  //StartPercent[bedNumber] = StartPercent[bedNumber] * Auto_BedStates[bedNumber];                 // Will only record the sensor reading if bed is in use
  digitalWrite(sensor_pwr_pins[bedNumber], LOW);                                                   // Loop to turn off sensors
}

void EndRead(int bedNumber)                                                                        // BedNumber indexed at 0
{
  digitalWrite(sensor_pwr_pins[bedNumber], HIGH);                                                  // Turn on sensor
  MillisDelay(1000);                                                                              // Delay time between powerup and read as per vegetronics
  EndPercent[bedNumber] = readVH400(bedNumber);                                                    // Obtain VWC
  MillisDelay(50);
  //EndPercent[bedNumber] = EndPercent[bedNumber] * Auto_BedStates[bedNumber];                     // Will only record the sensor reading if bed is in use
  digitalWrite(sensor_pwr_pins[bedNumber], LOW);                                                   // Loop to turn off sensors
}

int ManualWaterBeds()
{
  digitalWrite(WaterPin, HIGH);
  if (prime == 1)                                                                                  // If prime option is turned on, prime
  {
    //digitalWrite(13, HIGH);
    digitalWrite(pump_relay_pin, HIGH);                                                            // Turn on pump
    currentMillis = millis();
    while ((millis() - currentMillis) <= PumpTime)                                                 // Delay for PumpTimer duration
    {
    }
  }
  else                                                                                             // If prime option is turned off, don't prime
  {
    //digitalWrite(13, LOW);
    digitalWrite(pump_relay_pin, HIGH);
  }

  digitalWrite(PowerFlowSensorPin, HIGH);                                                          // Turn ON power for Flow Sensor
  for (int i = 0; i < 8; i++)
  {
    if (Manual_BedStates[i] == 1)
    {
      //StartRead(i);
      digitalWrite(valve_relay_pins[i], !Manual_BedStates[i]);                                     // Writes to the pin called in the relaypin[i] to be the state of BedNeedsWatering[i] where 0 is relay open, 1 is relay closed
      FlowDelay(Auto_WaterTimes[i]);                                                               // Flowcheck inside FlowDelay function
      digitalWrite(valve_relay_pins[i], HIGH);

      if(tank_dry==1)                                                                              // If flow sensor determines no water, break!
      {
      }
      else
      {
        EndRead(i);                                                                                // Sensor reading after watering
      }
      delay(3000);
    }
  }
  digitalWrite(PowerFlowSensorPin, LOW);                                                           // Turn OFF power for Flow Sensor
  digitalWrite(pump_relay_pin, LOW);                                                               // Turn off pump
  digitalWrite(WaterPin, LOW);

}


int AutoWaterBeds()                                                                                // Function controls the relays to water the beds according to BNW array
{
  digitalWrite(WaterPin, HIGH);
  if (prime == 1)                                                                                  // If prime option is turned on, prime
  {
    //digitalWrite(13, HIGH);
    digitalWrite(pump_relay_pin, HIGH);                                                            // Turn on pump
    currentMillis = millis();
    while ((millis() - currentMillis) <= PumpTime)                                                 // Delay for PumpTimer duration
    {
    }
  }
  else                                                                                             // If prime option is turned off, don't prime
  {
    //digitalWrite(13, LOW);
    digitalWrite(pump_relay_pin, HIGH);
  }

  digitalWrite(PowerFlowSensorPin, HIGH);

  for (int i = 0; i < 8; i++)
  {
  //Running without sensor readings//
  //  BNW[i] = 0;
  //===============================//
    if(BNW[i] == 0)                                                                                //only runs bed watering if BNW is 0
    {
      //StartRead[i];
      digitalWrite(valve_relay_pins[i], BNW[i]);                                                   // Writes to the pin called in the relaypin[i] to be the state of BedNeedsWatering[i] where 0 is relay open, 1 is relay closed
      FlowDelay(Auto_WaterTimes[i]);
      digitalWrite(valve_relay_pins[i], HIGH);                                                     // Turns off the relay

      if(tank_dry==1)
      {
      }
      else
      {
        EndRead(i);
      }
      delay(3000);
    }
  }
  digitalWrite(PowerFlowSensorPin, LOW);
  digitalWrite(pump_relay_pin, LOW);
  digitalWrite(WaterPin, LOW);

}

int NeedsWater()                                                                                   // Populates the BNW array according to percent array, threshold array, and Auto_BedStates array
{
  for(int i = 0; i < 8; i++)
  {
    if(Auto_BedStates[i] == 1)                                                                     // Checks if bed is turned on
    {
      if(percent[i] < threshold[i])                                                                // Checks if sensor read < threshold
      {
        BNW[i] = 0;                                                                                // Set to water
      }
      else
      {
        BNW[i] = 1;                                                                                // Does not need water
      }
    }
    else
    {
      BNW[i] = 1;                                                                                  // Does not need water since turned off
    }
  }
}

int ReadSensors()
{
  for(int i = 0; i < 8; i++)                                                                       // Loop to turn on sensors
  {
    //UNCOMMENT FOR REAL
    digitalWrite(sensor_pwr_pins[i], HIGH);
    //TESTING READ PROBLEMS
    delay(50);
  }
  delay(1000);                                                                                     // Delay time between powerup and read as per vegetronics
  for(int i = 0; i < 8; i++)
  {                                                                                                // Loop to read analog pins form A0 to A7
    percent[i] = readVH400(i);
    StartPercent[i] = percent[i];
//======================================================= Keep old sensor read =======================================================//
//    percent[x] = (((analogRead(x) * 5.0) / (1023.0 * maxvolt))*100);  // Converts analog read to a percent representing [analog voltage] / [maxvolt]
//    delay(50);                                                        // Delay after each read
//    percent[x] = percent[x] * Auto_BedStates[x];                      // Will only record the sensor reading if bed is in use
//====================================================================================================================================//
  }
  for(int x = 0; x < 8; x++)
  {                                                                                                // Loop to turn off sensors
    //UNCOMMENT FOR REAL
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
  Serial.read();
  delay(1500);

  for (int i = 0; i < 8; i++)
  {
    temp = Serial.readStringUntil('\n');
    threshold[i] = temp.toInt();
  }
  ByteRead = 'Z';
  delay(1500);
  while (ByteRead != 'G')
  {
    ByteRead = Serial.peek();
  }
  Serial.read();
  delay(1500);

  for (int i = 0; i < 8; i++)
  {
    temp = Serial.readStringUntil('\n');
    Auto_BedStates[i] = temp.toInt();
  }
  ByteRead = 'Z';
  delay(1500);
  while (ByteRead != 'G')
  {
    ByteRead = Serial.peek();
  }
  Serial.read();
  delay(1500);

  for (int i = 0; i < 8; i++)
  {
    temp = Serial.readStringUntil('\n');
    HoseType[i] = temp.toInt();
  }

  ByteRead = 'Z';
  delay(1500);
  while (ByteRead != 'G')
  {
    ByteRead = Serial.peek();
  }
  Serial.read();
  delay(1500);

  for (int i = 0; i < 8; i++)
  {
    temp = Serial.readStringUntil('\n');
    Manual_BedStates[i] = temp.toInt();
  }
  ByteRead = 'Z';
}

void SendSensorData()
{
  for (int i = 0; i < 8; i++)
  {
    tempval = percent[i];
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

void Winterize()
{
  digitalWrite(pump_relay_pin, HIGH);
  delay(5000);
  for (int i = 0; i < 8; i++)
  {
    if (i == 0)
    {
      digitalWrite(valve_relay_pins[7-i], 0);
    }
    else
    {
      digitalWrite(valve_relay_pins[8-i], 1);
      delay(5000);                                                                     // Each bed will be primed for 3s
      digitalWrite(valve_relay_pins[7-i], 0);
    }
    delay(5000);                                                                       // Each bed will be open for this long, 30s
  }

  for (int i = 0; i < 8; i++)
  {
    digitalWrite(valve_relay_pins[i], 0);
    delay(10);
  }
  delay(120000);                                                                       // All valves open for 2mins
  digitalWrite(pump_relay_pin, LOW);

  for (int i = 0; i < 8; i++)
  {
    digitalWrite(valve_relay_pins[i], 1);
    delay(10);
  }
}

void SendErrors()
{
  for (int i = 0; i < 9; i++)
  {
    tempval = ErrorArray[i];
    Serial.println(tempval);
  }
}

void FakeWater()
{
  for (int i = 0; i < 8; i++)
  {
    BNW[i] = 0;
  }
}

int FlowDelay(unsigned long local_duration)
{
  unsigned long local_currentMillis = millis();
  while ((millis() - local_currentMillis) <= local_duration)                          // Delay for flow check 1s duration replacement
  {
    FlowCheck();
    if (Hz < 10)
    {
      tank_dry = 1;
      ErrorArray[8] = 1;
      break;
    }
    else
    {
      tank_dry = 0;
      ErrorArray[8] = 0;
    }
  }
  return tank_dry;
}

void MillisDelay(unsigned long local_duration)
{
  unsigned long local_currentMillis = millis();
  while ((millis() - local_currentMillis) <= local_duration)                          // Delay for flow check 1s duration replacement
  {
  }
}

/*********************** ARDUINO SENSOR READ FROM VEGETRONIX **********************/

float readVH400(int analogPin) {
  // NOTE: You need to set analogPin to input in your setup block
  // ex. pinMode(<analogPin>, INPUT);
  // replace <analogPin> with the number of the pin you're going to read from.

  float VWC;
  float VWCavg;
  float tempVWC;
  for(int i = 0; i < 5; i++)
  {

    // Read value and convert to voltage
    int sensor1DN = analogRead(analogPin);
    float sensorVoltage = sensor1DN*(5.0 / 1023.0);

    // Calculate VWC
    if(sensorVoltage <= 1.1)
    {
      tempVWC = 10*sensorVoltage-1;
    }
    else if(sensorVoltage > 1.1 && sensorVoltage <= 1.3)
    {
      tempVWC = 25*sensorVoltage-17.5;
    }
    else if(sensorVoltage > 1.3 && sensorVoltage <= 1.82)
    {
      tempVWC = 48.08*sensorVoltage-47.5;
    }
    else if(sensorVoltage > 1.82)
    {
      tempVWC = 26.32*sensorVoltage-7.89;
    }

    VWC = VWC + tempVWC;
  }
  VWCavg = (VWC / 5);
  return(VWCavg);
}

struct VH400 {
  double analogValue;
  double analogValue_sd;
  double voltage;
  double voltage_sd;
  double VWC;
  double VWC_sd;
};

struct VH400 readVH400_wStats(int analogPin, int nMeasurements = 100, int delayBetweenMeasurements = 50)
{
  // This variant calculates the mean and standard deviation of 100 measurements over 5 seconds.
  // It reports mean and standard deviation for the analog value, voltage, and WVC.

  // This function returns Volumetric Water Content by converting the analogPin value to voltage
  // and then converting voltage to VWC using the piecewise regressions provided by the manufacturer
  // at http://www.vegetronix.com/Products/VH400/VH400-Piecewise-Curve.phtml

  // NOTE: You need to set analogPin to input in your setup block
  //   ex. pinMode(<analogPin>, INPUT);
  //   replace <analogPin> with the number of the pin you're going to read from.

  struct VH400 result;

  // Sums for calculating statistics
  int sensorDNsum = 0;
  double sensorVoltageSum = 0.0;
  double sensorVWCSum = 0.0;
  double sqDevSum_DN = 0.0;
  double sqDevSum_volts = 0.0;
  double sqDevSum_VWC = 0.0;

  // Arrays to hold multiple measurements
  int sensorDNs[nMeasurements];
  double sensorVoltages[nMeasurements];
  double sensorVWCs[nMeasurements];

  // Make measurements and add to arrays
  for (int i = 0; i < nMeasurements; i++) {
    // Read value and convert to voltage
    int sensorDN = analogRead(analogPin);
    double sensorVoltage = sensorDN*(3.0 / 1023.0);

    // Calculate VWC
    float VWC;
    if(sensorVoltage <= 1.1) {
      VWC = 10*sensorVoltage-1;
    } else if(sensorVoltage > 1.1 && sensorVoltage <= 1.3) {
      VWC = 25*sensorVoltage-17.5;
    } else if(sensorVoltage > 1.3 && sensorVoltage <= 1.82) {
      VWC = 48.08*sensorVoltage-47.5;
    } else if(sensorVoltage > 1.82) {
      VWC = 26.32*sensorVoltage-7.89;
    }

    // Add to statistics sums
    sensorDNsum += sensorDN;
    sensorVoltageSum += sensorVoltage;
    sensorVWCSum += VWC;

    // Add to arrays
    sensorDNs[i] = sensorDN;
    sensorVoltages[i] = sensorVoltage;
    sensorVWCs[i] = VWC;

    // Wait for next measurement
    delay(delayBetweenMeasurements);
  }

  // Calculate means
  double DN_mean = double(sensorDNsum)/double(nMeasurements);
  double volts_mean = sensorVoltageSum/double(nMeasurements);
  double VWC_mean = sensorVWCSum/double(nMeasurements);

  // Loop back through to calculate SD
  for (int i = 0; i < nMeasurements; i++) {
    sqDevSum_DN += pow((DN_mean - double(sensorDNs[i])), 2);
    sqDevSum_volts += pow((volts_mean - double(sensorVoltages[i])), 2);
    sqDevSum_VWC += pow((VWC_mean - double(sensorVWCs[i])), 2);
  }
  double DN_stDev = sqrt(sqDevSum_DN/double(nMeasurements));
  double volts_stDev = sqrt(sqDevSum_volts/double(nMeasurements));
  double VWC_stDev = sqrt(sqDevSum_VWC/double(nMeasurements));

  // Setup the output struct
  result.analogValue = DN_mean;
  result.analogValue_sd = DN_stDev;
  result.voltage = volts_mean;
  result.voltage_sd = volts_stDev;
  result.VWC = VWC_mean;
  result.VWC_sd = VWC_stDev;

  // Return the result
  return(result);
}
