int sensor_analog_read[] = {0, 1, 2, 3, 4, 5, 6, 7};                                 // Array defining the sensor pins

void setup() 
{
  Serial.begin(9600);                                                           // Setting up the Serial port for communication
}

void loop() 
{
  Serial.print(millis());
  Serial.print(",");
  for (int i = 0; i < 7; i++)
  {
    Serial.print(readVH400(i));
    Serial.print(",");
  }
  Serial.println(readVH400(7));
  //Serial.println("");
  delay(1000);
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
