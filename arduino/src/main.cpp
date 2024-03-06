#include "Arduino.h"

//TODO: mix of define and int
#define BaudRate           9600 // Set Baud Rate of serial communication
#define WaterPin           43   // tell the pi we are watering, always set the same as pump_relay_pin excpet winterize
#define pump_relay_pin     38   // Pin the pump relay is connected to, On-Off
#define FlowSensorPin      42   // Set flow sensor to pin 42
#define PowerFlowSensorPin 41   // Set power flow sensor to pin 41
#define DEBUG_LED          13   // mega built in LED


/**
 * program flow:
 * * wait for command from pi, store into into currentState
 * * run command requested by pi
 * * return to waiting
 *
 * if you manually set currentState to L it's a debug mode thingy
 **/

// Debug purpose: Set to L to read sensors
char currentState = 'Z'; // The variable to be changed to transition to another case

int tank_dry;


// HIGH appears to be off
int valve_relay_pins[] = { 22, 23, 24, 25, 26, 27, 28, 29 };
// HIGH is on
int sensor_pwr_pins[] = { 30, 31, 32, 33, 34, 35, 36, 37 };
//TODO: use this mapping array anywhere
int sensor_analog_read[] = { 0, 1, 2, 3, 4, 5, 6, 7 };       // Array defining the sensor pins

float percent[8];      // VWC (volumetric water content) percentage from sensors
float StartPercent[8]; // VWC at start of watering
float EndPercent[8];   // VWC at end of watering

// Store delta of sensor output between end and start of water, used in SensorCheck function
int EndStartDelta[] = { 30, 30, 30, 30, 30, 30, 30, 30 };

// populated by NeedsWater which compares percent to threshold
// 0 means bed needs watering, 1 means no watering
int BNW[] = { 1, 1, 1, 1, 1, 1, 1, 1 };

// Actual thresholds for each individual bed, comes from Pi, this defaults them to 50%
int threshold[] = { 20, 20, 20, 20, 20, 20, 20, 20 };

// 0 means no plants in that bed, don't bother watering, comes from Pi
int Auto_BedStates[] = { 0, 0, 0, 0, 0, 0, 0, 0 };

// 0 means no plants in that bed, don't bother watering, comes from Pi
int Manual_BedStates[] = { 1, 1, 1, 1, 1, 1, 1, 1 };

int HoseType[] = { 0, 0, 0, 0, 0, 0, 0, 0, 0 }; // Hose type, 0 = DripTape, 1 = SoakerHose

// Default watering times for AUTO and MANUAL to 30seconds
unsigned long Auto_WaterTimes[] = { 135000, 135000, 135000, 135000,
                                    135000, 135000, 135000, 135000 };

int prime = 1; // Variable to change whether PRIME option is turned on

int Hz = 0;
unsigned long duration = 0;
unsigned long currentMillis = 0;
unsigned long previousMillis = 0;

// Indices 0-7 are moisture sensor related errors, Index 8 is flow sensor related error
int ErrorArray[] = { 0, 0, 0, 0, 0, 0, 0, 0, 0 };

//======== CHANGE ACCORDINGLY ========//
unsigned long DripTape = 135000;   // DripTape duration
unsigned long SoakerHose = 135000; // Soaker hose duration
unsigned long PumpTime = 30000;    // Pump run duration for priming
//====================================//

void setup();
void loop();
void MySerialEvent();
int FlowCheck();
void AutoSensorCheck();
void ManualSensorCheck();
void ManualWaterBeds();
void AutoWaterBeds();
void NeedsWater();
void ReadSensors();
void ReceiveData();
void SendSensorData();
void ConvertData();
void Winterize();
void SendErrors();
void FakeWater();
int FlowDelay(unsigned long local_duration);
void MillisDelay(unsigned long local_duration);
float readVH400(int sensorID);


void setup()
{
    Serial.begin(BaudRate);
    pinMode(DEBUG_LED, OUTPUT);

    pinMode(FlowSensorPin, INPUT);
    pinMode(PowerFlowSensorPin, OUTPUT);
    pinMode(WaterPin, OUTPUT);

    for (int y = 0; y < 8; y++) {
        pinMode(sensor_pwr_pins[y], OUTPUT);
        pinMode(valve_relay_pins[y], OUTPUT);
        pinMode(sensor_analog_read[y], INPUT);

        // Initial states of relay pins, this doesn't draw any current
        digitalWrite(valve_relay_pins[y], HIGH);

        // DATA COLLECTION PURPOSES //
        // digitalWrite(sensor_pwr_pins[y], HIGH);
    }
    digitalWrite(WaterPin, LOW);
    pinMode(pump_relay_pin, OUTPUT); // Set pump relay pin as OUTPUT
    digitalWrite(DEBUG_LED, LOW); // Set LED off
}

void loop()
{
    switch (currentState) {
        case 'A': // Initialize or Update
            digitalWrite(DEBUG_LED, HIGH);
            ReceiveData(); // Fill the arrays with proper information
            ConvertData(); // Conver necessary data
            digitalWrite(DEBUG_LED, LOW);
            ReadSensors();     // Read the sensors
            NeedsWater();      // Determine which beds need watering
            AutoWaterBeds();   // Water the appropriate beds with proper durations
            AutoSensorCheck(); // Determine error values based on Start and End Percents
            currentState = 'Z';
            break;

        case 'S': // Automatic watering
            digitalWrite(DEBUG_LED, LOW);
            //ReadSensors();     // Read the sensors
            //NeedsWater();      // Determine which beds need watering
            //AutoWaterBeds();   // Water the appropriate beds with proper durations
            //AutoSensorCheck(); // Determine error values based on Start and End Percents
            currentState = 'Z'; // Transition to Default case
            break;

        case 'M': // Manual watering
            digitalWrite(DEBUG_LED, HIGH);
            ReceiveData(); // Fill the arrays with proper information
            ConvertData(); // Conver necessary data
            digitalWrite(DEBUG_LED, LOW);
            ManualWaterBeds(); // Manually water the beds
            ManualSensorCheck();
            currentState = 'Z'; // Transition to Default case
            break;

        case 'W':        // Winterizing
            Winterize(); // Blow out the system
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
            for (int i = 0; i < 7; i++) {
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

    // Wait until there is data in the serial line
    while (Serial.available() != 1) {
    }

    MySerialEvent(); // Check for case transition
}

void MySerialEvent()
{
    currentState = Serial.read();
}

int FlowCheck()
{
    duration = 0;
    for (int i = 0; i < 5; i++) {
        duration += pulseIn(FlowSensorPin, HIGH);
        delay(1000);
    }
    duration /= 5;
    if (duration == 0) {
        Hz = 0;
    } else {
        Hz = 500000 / duration;
    }
    return Hz;
}

void AutoSensorCheck()
{
    for (int i = 0; i < 8; i++) {
        if (BNW[i] == 1) {
            EndStartDelta[i] = EndPercent[i] - StartPercent[i];

            if (EndStartDelta[i] <= 10) {
                ErrorArray[i] = 1;
            } else {
                ErrorArray[i] = 0;
            }
        } else {
            ErrorArray[i] = 0;
        }
    }
}

void ManualSensorCheck()
{
    for (int i = 0; i < 8; i++) {
        if (Manual_BedStates[i] == 1) {
            EndStartDelta[i] = EndPercent[i] - StartPercent[i];

            if (EndStartDelta[i] <= 10) {
                ErrorArray[i] = 1;
            } else {
                ErrorArray[i] = 0;
            }
        } else {
            ErrorArray[i] = 0;
        }
    }
}

void StartRead(int bedNumber) // BedNumber indexed at 0
{
    unsigned long internalDelay = 1000;             // Delay for 1[s] read
    digitalWrite(sensor_pwr_pins[bedNumber], HIGH); // Turn on sensor
    MillisDelay(1000); // Delay time between powerup and read as per vegetronics
    StartPercent[bedNumber] = readVH400(bedNumber); // Obtain VWC
    MillisDelay(50);
    //StartPercent[bedNumber] = StartPercent[bedNumber] * Auto_BedStates[bedNumber];                 // Will only record the sensor reading if bed is in use
    digitalWrite(sensor_pwr_pins[bedNumber], LOW); // Loop to turn off sensors
}

void EndRead(int bedNumber) // BedNumber indexed at 0
{
    digitalWrite(sensor_pwr_pins[bedNumber], HIGH); // Turn on sensor
    MillisDelay(1000); // Delay time between powerup and read as per vegetronics
    EndPercent[bedNumber] = readVH400(bedNumber); // Obtain VWC
    MillisDelay(50);
    //EndPercent[bedNumber] = EndPercent[bedNumber] * Auto_BedStates[bedNumber];                     // Will only record the sensor reading if bed is in use
    digitalWrite(sensor_pwr_pins[bedNumber], LOW); // Loop to turn off sensors
}

void ManualWaterBeds()
{
    digitalWrite(WaterPin, HIGH);
    if (prime == 1) { // If prime option is turned on, prime
        //digitalWrite(DEBUG_LED, HIGH);
        digitalWrite(pump_relay_pin, HIGH); // Turn on pump
        currentMillis = millis();

        // Delay for PumpTimer duration
        while ((millis() - currentMillis) <= PumpTime) {
        }
    } else { // If prime option is turned off, don't prime
        //digitalWrite(DEBUG_LED, LOW);
        digitalWrite(pump_relay_pin, HIGH);
    }

    digitalWrite(PowerFlowSensorPin, HIGH); // Turn ON power for Flow Sensor
    for (int i = 0; i < 8; i++) {
        if (Manual_BedStates[i] == 1) {
            //StartRead(i);
            // Writes to the pin called in the relaypin[i] to be the state of BedNeedsWatering[i] where 0 is relay open, 1 is relay closed
            digitalWrite(valve_relay_pins[i], !Manual_BedStates[i]);
            FlowDelay(Auto_WaterTimes[i]); // Flowcheck inside FlowDelay function
            digitalWrite(valve_relay_pins[i], HIGH);

            if (tank_dry == 1) { // If flow sensor determines no water, break!
            } else {
                EndRead(i); // Sensor reading after watering
            }
            delay(3000);
        }
    }
    digitalWrite(PowerFlowSensorPin, LOW); // Turn OFF power for Flow Sensor
    digitalWrite(pump_relay_pin, LOW);     // Turn off pump
    digitalWrite(WaterPin, LOW);
}


// Function controls the relays to water the beds according to BNW array
void AutoWaterBeds()
{
    digitalWrite(WaterPin, HIGH);
    if (prime == 1) { // If prime option is turned on, prime
        //digitalWrite(DEBUG_LED, HIGH);
        digitalWrite(pump_relay_pin, HIGH); // Turn on pump
        currentMillis = millis();
        // Delay for PumpTimer duration
        while ((millis() - currentMillis) <= PumpTime) {
        }
    } else { // If prime option is turned off, don't prime
        //digitalWrite(DEBUG_LED, LOW);
        digitalWrite(pump_relay_pin, HIGH);
    }

    digitalWrite(PowerFlowSensorPin, HIGH);

    for (int i = 0; i < 8; i++) {
        //Running without sensor readings//
        //  BNW[i] = 0;
        //===============================//
        if (BNW[i] == 0) { //only runs bed watering if BNW is 0
            //StartRead[i];
            // Writes to the pin called in the relaypin[i] to be the state of BedNeedsWatering[i] where 0 is relay open, 1 is relay closed
            digitalWrite( valve_relay_pins[i], BNW[i]);
            FlowDelay(Auto_WaterTimes[i]);
            digitalWrite(valve_relay_pins[i], HIGH); // Turns off the relay

            if (tank_dry == 1) {
            } else {
                EndRead(i);
            }
            delay(3000);
        }
    }
    digitalWrite(PowerFlowSensorPin, LOW);
    digitalWrite(pump_relay_pin, LOW);
    digitalWrite(WaterPin, LOW);
}

// Populates the BNW array according to percent array, threshold array, and Auto_BedStates array
void NeedsWater()
{
    for (int i = 0; i < 8; i++) {
        // Checks if bed is turned on
        if (Auto_BedStates[i] == 1) {
            // Checks if sensor read < threshold
            if (percent[i] < threshold[i]) {
                BNW[i] = 0; // Set to water
            } else {
                BNW[i] = 1; // Does not need water
            }
        } else {
            BNW[i] = 1; // Does not need water since turned off
        }
    }
}

void ReadSensors()
{
    // Loop to turn on sensors
    for (int i = 0; i < 8; i++) {
        //UNCOMMENT FOR REAL
        digitalWrite(sensor_pwr_pins[i], HIGH);
        //TESTING READ PROBLEMS
        delay(50);
    }
    delay(1000); // Delay time between powerup and read as per vegetronics
    // Loop to read analog pins form A0 to A7
    for (int i = 0; i < 1; i++) {
        percent[i] = readVH400(i);
        StartPercent[i] = percent[i];
    }
    // Loop to turn off sensors
    for (int x = 0; x < 8; x++) {
        //UNCOMMENT FOR REAL
        digitalWrite(sensor_pwr_pins[x], LOW);
    }
}

// Receive data communication with Pi
void ReceiveData()
{
    char ByteRead = 'C';
    String temp = " ";
    ByteRead = 'Z';
    while (ByteRead != 'G') {
        ByteRead = Serial.peek();
    }
    Serial.read();
    delay(1500);

    for (int i = 0; i < 8; i++) {
        temp = Serial.readStringUntil('\n');
        threshold[i] = temp.toInt();
    }
    ByteRead = 'Z';
    delay(1500);
    while (ByteRead != 'G') {
        ByteRead = Serial.peek();
    }
    Serial.read();
    delay(1500);

    for (int i = 0; i < 8; i++) {
        temp = Serial.readStringUntil('\n');
        Auto_BedStates[i] = temp.toInt();
    }
    ByteRead = 'Z';
    delay(1500);
    while (ByteRead != 'G') {
        ByteRead = Serial.peek();
    }
    Serial.read();
    delay(1500);

    for (int i = 0; i < 8; i++) {
        temp = Serial.readStringUntil('\n');
        HoseType[i] = temp.toInt();
    }

    ByteRead = 'Z';
    delay(1500);
    while (ByteRead != 'G') {
        ByteRead = Serial.peek();
    }
    Serial.read();
    delay(1500);

    for (int i = 0; i < 8; i++) {
        temp = Serial.readStringUntil('\n');
        Manual_BedStates[i] = temp.toInt();
    }
    ByteRead = 'Z';
}

void SendSensorData()
{
    for (int i = 0; i < 8; i++) {
        Serial.println(percent[i]);
    }
}

void ConvertData()
{
    for (int i = 0; i < 8; i++) {
        if (HoseType[i] == 0) {
            Auto_WaterTimes[i] = DripTape;
        } else {
            Auto_WaterTimes[i] = SoakerHose;
        }
    }
}

void Winterize()
{
    digitalWrite(pump_relay_pin, HIGH);
    delay(5000);
    for (int i = 0; i < 8; i++) {
        if (i == 0) {
            digitalWrite(valve_relay_pins[7 - i], 0);
        } else {
            digitalWrite(valve_relay_pins[8 - i], 1);
            delay(5000); // Each bed will be primed for 3s
            digitalWrite(valve_relay_pins[7 - i], 0);
        }
        delay(5000); // Each bed will be open for this long, 30s
    }

    for (int i = 0; i < 8; i++) {
        digitalWrite(valve_relay_pins[i], 0);
        delay(10);
    }
    delay(120000); // All valves open for 2mins
    digitalWrite(pump_relay_pin, LOW);

    for (int i = 0; i < 8; i++) {
        digitalWrite(valve_relay_pins[i], 1);
        delay(10);
    }
}

void SendErrors()
{
    for (int i = 0; i < 9; i++) {
        Serial.println(ErrorArray[i]);
    }
}

void FakeWater()
{
    for (int i = 0; i < 8; i++) {
        BNW[i] = 0;
    }
}

int FlowDelay(unsigned long local_duration)
{
    unsigned long local_currentMillis = millis();
    // Delay for flow check 1s duration replacement
    while ((millis() - local_currentMillis) <= local_duration) {
        FlowCheck();
        if (Hz < 10) {
            tank_dry = 1;
            ErrorArray[8] = 1;
            break;
        } else {
            tank_dry = 0;
            ErrorArray[8] = 0;
        }
    }
    return tank_dry;
}

void MillisDelay(unsigned long local_duration)
{
    unsigned long local_currentMillis = millis();
    // Delay for flow check 1s duration replacement
    while ((millis() - local_currentMillis) <= local_duration) {
    }
}

/*********************** ARDUINO SENSOR READ FROM VEGETRONIX **********************/

// ORIGINAL
float readVH400(int sensorID)
{
    float VWC;
    float VWCavg;
    float tempVWC;
    for (int i = 0; i < 5; i++) {
        // Read value and convert to voltage
        int sensorDN = analogRead(sensor_analog_read[sensorID]);
        float sensorVoltage = sensorDN * (5.0 / 1023.0);
        Serial.write(sensorDN);
        Serial.write(sensorVoltage);

        // Calculate VWC
        if (sensorVoltage <= 1.1) {
            tempVWC = 10 * sensorVoltage - 1;
        } else if (sensorVoltage > 1.1 && sensorVoltage <= 1.3) {
            tempVWC = 25 * sensorVoltage - 17.5;
        } else if (sensorVoltage > 1.3 && sensorVoltage <= 1.82) {
            tempVWC = 48.08 * sensorVoltage - 47.5;
        } else if (sensorVoltage > 1.82 && sensorVoltage <= 2.2) {
            tempVWC = 26.32 * sensorVoltage - 7.89;
        } else if (sensorVoltage > 2.2 && sensorVoltage <= 3) {
            tempVWC = 62.5 * sensorVoltage - 87.5;
        } else {
            // TODO: invalid data
        }

        VWC = VWC + tempVWC;
    }
    VWCavg = (VWC / 5);
    return (VWCavg);
}

// UPDATED on 3/6/23 for testing
// float readVH400(int sensorID)
// {
//     // Read value and convert to voltage
//     int sensorDN = analogRead(sensor_analog_read[sensorID]);
//     float sensorVoltage = sensorDN * (5.0 / 1023.0);
//     float VWC;

//     // Calculate VWC
//     if (sensorVoltage <= 1.1) {
//         VWC = 10 * sensorVoltage - 1;
//     } else if (sensorVoltage > 1.1 && sensorVoltage <= 1.3) {
//         VWC = 25 * sensorVoltage - 17.5;
//     } else if (sensorVoltage > 1.3 && sensorVoltage <= 1.82) {
//         VWC = 48.08 * sensorVoltage - 47.5;
//     } else if (sensorVoltage > 1.82 && sensorVoltage <= 2.2) {
//         VWC = 26.32 * sensorVoltage - 7.89;
//     } 
//     // else if (sensorVoltage > 2.2 && sensorVoltage <= 3) {
//     //     VWC = 62.5 * sensorVoltage - 87.5;
//     // } 

//     return (VWC);
// }