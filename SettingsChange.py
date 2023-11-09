#!/usr/bin/python
from datetime import datetime
import time

dt = datetime.now()
Threshold=[20,20,20,20,20,20,20,20]
BedState=[1,0,0,0,0,0,0,0]
WaterOption=[0,0,0,0,0,0,0,0]
SensorValues=[0,0,0,0,0,0,0,0]
hoseType =[0,0,0,0,0,0,0,0]
filepath = '/home/pi/Aug24_Final/SettingsFile.txt'
#-------------------------------------------------------------------------
#Function takes in Bed Number & New Thrsholds
#opens settings file, rewrites selected line based on bed number input
def saveThreshold(BedNumber, NewThreshold):
    f = open(filepath, 'r')
    data = f.readlines()
    print (data)
    print ('old Threshold'+ data[BedNumber])
    data[31] = dt.strftime("Date: %m/%d/%y Time:%H:%M\n")
    data[BedNumber] ='Thresh '+str(BedNumber)+':'+str(NewThreshold)+'\n'
    print (data)
    f.close

    f = open(filepath,'w')
    f.seek(0)
    f.writelines(data)
    f.close
##test for saveThreshold 
#saveThreshold(1,54)
#---------------------------------------------------------------------------
#function updates the value set by the team for the max watering value (time or number? not sure)

def saveMaxWaterLvl(setMax):
    f = open(filepath, 'r')
    data = f.readlines()
    print (data)
    data[10] = 'Max Water Lvl:'+str(setMax)+'\n'
    data[31] = dt.strftime("Date: %m/%d/%y Time:%H:%M\n")
    f.close

    f = open(filepath,'w')
    f.seek(0)
    f.writelines(data)
    f.close    


#test for saveIncAmount
#saveMaxWaterLvl(88)

#---------------------------------------------------------------------------
#function updates the user setting for the amount that we increment the water adjustment

def saveIncAmount(setIncrement):
    f = open(filepath, 'r')
    data = f.readlines()   
    print (data)
    
    data[11] = 'Increment:'+str(setIncrement)+'\n'
    data[31] = dt.strftime("Date: %m/%d/%y Time:%H:%M\n")
    f.close
    
    f = open(filepath,'w')
    f.seek(0)
    f.writelines(data)
    f.close
    

#test for saveIncAmount
#saveIncAmount(8)

#-----------------------------------------------------------------------------
#function open SettingsFile and grabs saved value for team set increment amount 
def getIncAmount():
    f = open(filepath, 'r')
    data = f.readlines()   
    print (data)   


    x = data[11]
    f.close
    incAmount = int(x.split(":",1)[1])
    #Test Print statement
    print(incAmount)
    return incAmount
    
    
#test for getIncAmount()
#getIncAmount()
#------------------------------------------------------------------------------
#function to turn individual bed off

def turnBedOff(BedNumber):
    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)   

    data[11+BedNumber] = 'PWR Bed'+str(BedNumber)+':0'+'\n'
    data[31] = dt.strftime("Date: %m/%d/%y Time:%H:%M\n")
    f.close
    
    f = open(filepath, 'w')
    f.writelines(data)   
    f.close
    
#test for turn bed off
#turnBedOff(8)
#-------------------------------------------------------------------------------
#function to turn individual bed on

def turnBedOn(BedNumber):
    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)   

    data[11+BedNumber] = 'PWR Bed'+str(BedNumber)+':1'+'\n'
    data[31] = dt.strftime("Date: %m/%d/%y Time:%H:%M\n")
    f.close
    
    f = open(filepath, 'w')
    f.writelines(data)   
    f.close

#test for turn bed off
#turnBedOn(5)
#------------------------------------------------------------------------------
#function to get bed status

def getBedStatus(BedNum):
    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)   


    x = data[11 + BedNum]
    f.close
    incAmount = int(x.split(":",1)[1])
    #Test Print statement
    print(incAmount)
    return incAmount

def getThresholds():
    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)   
    f.close
    
    for num in range(1,9):
        thresh = data[num]
        value = int(thresh.split(":",1)[1])

        Threshold[num -1] = value
        print(Threshold)
    return Threshold 

def getAllBedStatus():
    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)   
    f.close
    
    for num in range(1,9):
        bedOnOff = data[11+num]
        value = int(bedOnOff.split(":",1)[1])

        BedState[num -1] = value
        print(BedState)
    return BedState

def wateringTime():
# Option for Soaker Hose
    f = open(filepath, 'r')
    data = f.readlines()
    f.close()
    soak = 1
    drip = 0
    print(data) 
    for num in range(1,9):
        x = num + 22
        val = data[x]
        splitWater = int(val.split(':',1)[1])        
        print(splitWater) 
        if splitWater == 1:
            
            watertime = data[21]
            print(data[21])
            waterTime = int(watertime.split(':',1)[1])
            WaterOption[num -1] = waterTime
            print (waterTime)
            print (WaterOption) 

      
        elif splitWater == 0:
#option for drip tape         

            watertime = data[20]
            print(data[20])
            waterTime = int(watertime.split(':',1)[1])
            WaterOption[num-1] = waterTime
            print (waterTime)
            print(WaterOption)
    print(num) 
    return WaterOption

    
def setSoaker(x):
#option to set watering time 

    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)
    f.close
    data[22 +x] = 'Wtr Option '+str(x)+':1'+'\n'
    data[31] = dt.strftime("Date: %m/%d/%y Time:%H:%M\n")
    print(x)
    f = open(filepath, 'w')
    f.writelines(data)   
    f.close

def setDrip(x):
#option to set watering time 

    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)
    f.close
    data[22 + x] = 'Wtr Option '+str(x)+':0'+'\n'
    data[31] = dt.strftime("Date: %m/%d/%y Time:%H:%M\n")
    print(x)
    f = open(filepath, 'w')
    f.writelines(data)   
    f.close

# Function to get intitial hose type based on text file     
def getWaterHose():
    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)   
    f.close
    
    for num in range(1,9):
        hose = data[22+num]
        hoseValue = int(hose.split(":",1)[1])

        hoseType [num -1] = hoseValue
        print(hoseType)
    return hoseType

##
def setAutoWaitTime(x, y):

    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)
    f.close
    data[32] = 'AM:' + str(x) + '\n'
    data[33] = 'PM:' + str(y) + '\n'
    data[31] = dt.strftime("Date: %m/%d/%y Time:%H:%M\n")

    f = open(filepath, 'w')
    f.writelines(data)   
    f.close
   
def getAutoWaitTime():
    print "AM"
    f = open(filepath, 'r')
    data = f.readlines()   
    print (data)   
    f.close
    
    am = int(data[32].split(':')[1])
    pm = int(data[33].split(':')[1])
    
    return am,pm
##

def setSystemStatus(x):

    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)
    f.close
    
    data[34] = 'SystemStatus:' + str(x) + '\n'
    data[31] = dt.strftime("Date: %m/%d/%y Time:%H:%M\n")
    
    f = open(filepath, 'w')
    f.writelines(data)   
    f.close
   
def getSystemStatus():
    f = open(filepath, 'r')
    data = f.readlines()   
    #print (data)   
    f.close
    
    status = int(data[34].split(':')[1])
    
    return status



##def setDrip(x)
##
##
##    f = open('SettingsFile.txt', 'r')
##    data = f.readlines()   
##    #print (data)   
##    data[22 +x] = 'Wtr Option '+str(x)+':1'\n'
##    data[31] = dt.strftime("Date: %m/%d/%y Time:%H:%M")
##    f.close        
##

             
##saveThreshold(1,54)
##saveThreshold(2,45)
##saveThreshold(3,33)
##saveThreshold(4,22)
##saveThreshold(5,24)
##saveThreshold(6,45)
##saveThreshold(7,66)
##saveThreshold(8,11)
##
##getThresholds() 
##
##getAllBedStatus()

###wateringTime()
###setWateringTime(
##
##setSoaker(1)
##setSoaker(2)
##setSoaker(4)
##setDrip(3)
##setDrip(5)
##setDrip(6)
##setDrip(7)
##setSoaker(8)
##
#wateringTime()
##
##'''
##turnBedOn(1)
##turnBedOff(2)
##turnBedOn(3)
##turnBedOff(4)
##turnBedOn(5)
##turnBedOff(6)
##turnBedOn(7)
##turnBedOff(8)
##getBedStatus(1)
##getBedStatus(2)
##getBedStatus(3)
##getBedStatus(4)
##getBedStatus(5)
##getBedStatus(6)
##getBedStatus(7)
##getBedStatus(8)
##'''
##for num in range(1,8):
##    turnBedOn(num)
##
##for num in range(1,8):
##    getBedStatus(num) 

    



