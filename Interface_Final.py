#!/usr/bin/env python3
import kivy
import time
import serial
# import RPi.GPIO as GPIO
from kivy.config import Config

Config.set('graphics','fullscreen','auto')
Config.set('graphics','resizable','1')
Config.set('graphics','width','480')
Config.set('graphics','height','200')

#from kivy.core.window import Window
#Window.fullscreen=False
import threading
from threading import Timer
from threading import Thread
from time import sleep
#kivy.require("1.10.0")
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from threading import Timer
from kivy.uix.popup import Popup
from time import sleep
from time import gmtime, strftime, asctime
import datetime
from datetime import datetime

global ser
ser = serial.Serial('/dev/ttyACM0', 9600)
# ser = serial.Serial('/dev/tty.usbmodem11301', 9600)

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(27,GPIO.IN)
# GPIO.setup(17,GPIO.OUT, initial = 0)

from functools import partial
from SettingsChange import * #getAllBedStatus,getThresholds,wateringTime,saveThreshold,turnBedOff,turnBedOn,setSoaker,setDrip

# Clock Screen
class TickTock(Label):
    def update(self,*args):
        #self.text = time.asctime()
        timing = datetime.now().strftime("%H:%M:%S")
        self.text = timing

class home_screen(Screen):
#class irrigation_app(App):# switch to float layout and figure out the values for correct positioning
    global waterTime
    global Dialog
    global Bar
    global auto_states
    global auto_buttonstates
    global bed_color
    global water_type
    global water_buttonstates
    global water_color
    water_type=[0,0,0,0,0,0,0,0]
    water_buttonstates=[0,0,0,0,0,0,0,0]
    water_color=[0,0,0,0,0,0,0,0]
    auto_states=[0,0,0,0,0,0,0,0]
    auto_buttonstates=[0,0,0,0,0,0,0,0]
    bed_color=[0,0,0,0,0,0,0,0]
    waterTime=[0,0,0,0,0,0,0,0]

    def test_schedule(self,*args):
        test=Clock.schedule_once(lambda AA: self.auto_routine(),20)

    def auto_timer(self,*args):
        global auto_time
        global am_time
        global pm_time

        am_time, pm_time = getAutoWaitTime()
        clock_time = datetime.now().strftime("%H:%M:%S")
        print('-----------------------------------------------------------------')
        print(clock_time)
        print('-----------------------------------------------------------------')
        clock_time = clock_time.split(':')
        hourInSec = int(clock_time[0]) * 3600
        minuteInSec = int(clock_time[1]) * 60
        seconds = int(clock_time[2])
        now_timer = hourInSec + minuteInSec + seconds
##        print('-----------------------------------------------------------------')
##        print(hourInSec)
##        print('-----------------------------------------------------------------')
##        print(minuteInSec)
##        print('-----------------------------------------------------------------')
##        print(seconds)
##        print('-----------------------------------------------------------------')
##        print(now_timer)
##        print('-----------------------------------------------------------------')
##        #save for later
##        #firstWaterSched = 21600 # 6am
##        #secondWaterSched = 64800 # 6pm

        firstWaterSched = am_time*3600  # 7am
        secondWaterSched = pm_time*3600 # 7:35pm

        if (now_timer > firstWaterSched) and (now_timer < secondWaterSched):
                print('pm')
                timer = secondWaterSched - now_timer
                print(timer)
                auto_time=Clock.schedule_once(lambda A: self.auto_routine(), timer)
                return auto_time
        else:
                print('am')
                timer = firstWaterSched + (86399-now_timer)
                print(timer)
                auto_time=Clock.schedule_once(lambda A: self.auto_routine(), timer)
                return auto_time

    def auto_init(self,*args):
        #self.test_schedule()
        #self.auto_timer()
        global Threshold
        global Auto_BedState
        global WaterOption
        global Manual_BedState
        Threshold=getThresholds()
        Auto_BedState=getAllBedStatus()
        WaterOption=getWaterHose()
        waterTime=wateringTime()
        Manual_BedState=getAllBedStatus()

        for index in range(len(Auto_BedState)):
            if Auto_BedState[index]==1:
                auto_states[index]='ON'
                auto_buttonstates[index]='down'
                bed_color[index]=[.50,1,.99,1]
            else:
                auto_states[index]='OFF'
                auto_buttonstates[index]='normal'
                bed_color[index]=[.168,.25,.75,1]

        for index in range(len(WaterOption)):
            if WaterOption[index]==1:
                water_type[index]='Soaker'
                water_buttonstates[index]='down'
                water_color[index]=[.50,1,.99,2]
            else:
                water_type[index]='Drip'
                water_buttonstates[index]='normal'
                water_color[index]=[.168,.25,.75,1]


    def on_pre_enter(self,*args):

        self.auto_timer()
        Threshold=getThresholds()
        Auto_BedState=getAllBedStatus()
        WaterOption=getWaterHose()
        waterTime=wateringTime()
        Manual_BedState=getAllBedStatus()

        for index in range(len(Auto_BedState)):
            if Auto_BedState[index]==1:
                auto_states[index]='ON'
                auto_buttonstates[index]='down'
                bed_color[index]=[.50,1,.99,1]
            else:
                auto_states[index]='OFF'
                auto_buttonstates[index]='normal'
                bed_color[index]=[.168,.25,.75,1]

        for index in range(len(WaterOption)):
            if WaterOption[index]==1:
                water_type[index]='Soaker'
                water_buttonstates[index]='down'
                water_color[index]=[.50,1,.99,1]
            else:
                water_type[index]='Drip'
                water_buttonstates[index]='normal'
                water_color[index]=[.168,.25,.75,1]

        # Button state will be updated after creation

##        water_option1.text=water_type[0]
##        water_option1.state=water_buttonstates[0]
##        water_option1.background_color=water_color[0]
##        water_option2.text=water_type[1]
##        water_option2.state=water_buttonstates[1]
##        water_option2.background_color=water_color[1]
##        water_option3.text=water_type[2]
##        water_option3.state=water_buttonstates[2]
##        water_option3.background_color=water_color[2]
##        water_option4.text=water_type[3]
##        water_option4.state=water_buttonstates[3]
##        water_option4.background_color=water_color[3]
##        water_option5.text=water_type[4]
##        water_option5.state=water_buttonstates[50, 100, 50, 50, 50, 50, 50, 50]
##        water_option5.background_color=water_color[4]
##        water_option6.text=water_type[5]
##        water_option6.state=water_buttonstates[5]
##        water_option6.background_color=water_color[5]
##        water_option7.text=water_type[6]
##        water_option7.state=water_buttonstates[6]
##        water_option7.background_color=water_color[6]
##        water_option8.text=water_type[7]
##        water_option8.state=water_buttonstates[7]
##        water_option8.background_color=water_color[7]
##
##        threshold1.text=str(Threshold[0])
##        threshold2.text=str(Threshold[1])
##        threshold3.text=str(Threshold[2])
##        threshold4.text=str(Threshold[3])
##        threshold5.text=str(Threshold[4])
##        threshold6.text=str(Threshold[5])
##        threshold7.text=str(Threshold[6])
##        threshold8.text=str(Threshold[7])

    def auto_routine(self,*args):
        def Dialog_Open():
            Dialog.open()
            pass

        def Reset_Buffs():
            ser.flushInput()
            ser.flushOutput()
            print("Resetting input and output buffer...")
            Bar.value = 10

        def Write_A():
            ser.write(b'A')
        def Write_G1():
            ser.write(b'G')
            ser.write(str(Threshold[0])+'\n')
            ser.write(str(Threshold[1])+'\n')
            ser.write(str(Threshold[2])+'\n')
            ser.write(str(Threshold[3])+'\n')
            ser.write(str(Threshold[4])+'\n')
            ser.write(str(Threshold[5])+'\n')
            ser.write(str(Threshold[6])+'\n')
            ser.write(str(Threshold[7])+'\n')
            print("Thresholds done.")
            Bar.value = 30
        def Write_G2():
            ser.write(b'G')
            ser.write(str(Auto_BedState[0])+'\n')
            ser.write(str(Auto_BedState[1])+'\n')
            ser.write(str(Auto_BedState[2])+'\n')
            ser.write(str(Auto_BedState[3])+'\n')
            ser.write(str(Auto_BedState[4])+'\n')
            ser.write(str(Auto_BedState[5])+'\n')
            ser.write(str(Auto_BedState[6])+'\n')
            ser.write(str(Auto_BedState[7])+'\n')
            print("Auto Beds On/Off done.")
            Bar.value = 50
        def Write_G3():
            ser.write(b'G')
            ser.write(str(WaterOption[0])+'\n')
            ser.write(str(WaterOption[1])+'\n')
            ser.write(str(WaterOption[2])+'\n')
            ser.write(str(WaterOption[3])+'\n')
            ser.write(str(WaterOption[4])+'\n')
            ser.write(str(WaterOption[5])+'\n')
            ser.write(str(WaterOption[6])+'\n')
            ser.write(str(WaterOption[7])+'\n')
            print("Timers done.")
            Bar.value = 70
        def Write_G4():
            ser.write(b'G')
            ser.write(str(Manual_BedState[0])+'\n')
            ser.write(str(Manual_BedState[1])+'\n')
            ser.write(str(Manual_BedState[2])+'\n')
            ser.write(str(Manual_BedState[3])+'\n')
            ser.write(str(Manual_BedState[4])+'\n')
            ser.write(str(Manual_BedState[5])+'\n')
            ser.write(str(Manual_BedState[6])+'\n')
            ser.write(str(Manual_BedState[7])+'\n')
            Bar.value = 90
        def Wait_Break():
            Bar.value = 100
            print("Reads are finished.")
        def Dialog_Close():
            Dialog.dismiss()
        def Write_S():
            ser.flushInput()
            ser.flushOutput()
            ser.write(b'S')

        def Read_watering():
            print("Read_watering")
            # if GPIO.input(27):
                # self.manager.current='Watering_screen'

        # Instantiate dialog
        Grid = GridLayout(rows=2)
        Dialog_Label = Label(text="Sending Data...",font_size=30)
        Grid.add_widget(Dialog_Label)
        Bar = ProgressBar(max=100)
        Grid.add_widget(Bar)
        Dialog = Popup(title='Automatic mode initialized...',title_size=20,title_align='center',content=Grid,size=(500,300),size_hint=(None,None),auto_dismiss=False)

        # Schedule the read/write events
        Clock.schedule_once(lambda C: Dialog_Open(),0)
        Clock.schedule_once(lambda D: Reset_Buffs(),0)
        Clock.schedule_once(lambda E: Write_A(),1.6)
        Clock.schedule_once(lambda F: Write_G1(),2.6)
        Clock.schedule_once(lambda G: Write_G2(),5.6)
        Clock.schedule_once(lambda H: Write_G3(),8.6)
        Clock.schedule_once(lambda I: Write_G4(),11.6)
        Clock.schedule_once(lambda J: Wait_Break(),14.6)
        #Clock.schedule_once(lambda K: Write_S(),16.6)
        Clock.schedule_once(lambda L: Dialog_Close(),17)
        Clock.schedule_once(lambda M: Read_watering(),17.5)

        #self.test_schedule()
        #self.auto_timer()


    def manual_routine(self,*args):
        #test.cancel()
        #auto_time.cancel()
        Clock.unschedule(auto_time)
        self.manager.current='Manual_screen'

    def settings_routine(self,event):
        #test.cancel()
        #auto_time.cancel()
        Clock.unschedule(auto_time)
        self.manager.current='Settings_screen'
    '''
    def increase_bed1(self,event):
        Threshold[0]=Threshold[0]+5
        if Threshold[0]>100:
            Threshold[0]=100
        threshold1.text=str(Threshold[0])
        saveThreshold(1,Threshold[0])
    def increase_bed2(self,event):
        Threshold[1]=Threshold[1]+5
        if Threshold[1]>100:
            Threshold[1]=100
        threshold2.text=str(Threshold[1])
        saveThreshold(2,Threshold[1])
    def increase_bed3(self,event):
        Threshold[2]=Threshold[2]+5
        if Threshold[2]>100:
            Threshold[2]=100
        threshold3.text=str(Threshold[2])
        saveThreshold(3,Threshold[2])
    def increase_bed4(self,event):
        Threshold[3]=Threshold[3]+5
        if Threshold[3]>100:
            Threshold[3]=100
        threshold4.text=str(Threshold[3])
        saveThreshold(4,Threshold[3])
    def increase_bed5(self,event):
        Threshold[4]=Threshold[4]+5
        if Threshold[4]>100:
            Threshold[4]=100
        threshold5.text=str(Threshold[4])
        saveThreshold(5,Threshold[4])
    def increase_bed6(self,event):
        Threshold[5]=Threshold[5]+5
        if Threshold[5]>100:
            Threshold[5]=100
        threshold6.text=str(Threshold[5])
        saveThreshold(6,Threshold[5])
    def increase_bed7(self,event):
        Threshold[6]=Threshold[6]+5
        if Threshold[6]>100:
            Threshold[6]=100
        threshold7.text=str(Threshold[6])
        saveThreshold(7,Threshold[6])
    def increase_bed8(self,event):
        Threshold[7]=Threshold[7]+5
        if Threshold[7]>100:
            Threshold[7]=100
        threshold8.text=str(Threshold[7])
        saveThreshold(8,Threshold[7])

    def decrease_bed1(self,event):
        Threshold[0]=Threshold[0]-5
        if Threshold[0]<0:
            Threshold[0]=0
        threshold1.text=str(Threshold[0])
        saveThreshold(1,Threshold[0])
    def decrease_bed2(self,event):
        Threshold[1]=Threshold[1]-5
        if Threshold[1]<0:
            Threshold[1]=0
        threshold2.text=str(Threshold[1])
        saveThreshold(2,Threshold[1])
    def decrease_bed3(self,event):
        Threshold[2]=Threshold[2]-5
        if Threshold[2]<0:
            Threshold[2]=0
        threshold3.text=str(Threshold[2])
        saveThreshold(3,Threshold[2])
    def decrease_bed4(self,event):
        Threshold[3]=Threshold[3]-5
        if Threshold[3]<0:
            Threshold[3]=0
        threshold4.text=str(Threshold[3])
        saveThreshold(4,Threshold[3])
    def decrease_bed5(self,event):
        Threshold[4]=Threshold[4]-5
        if Threshold[4]<0:
            Threshold[4]=0
        threshold5.text=str(Threshold[4])
        saveThreshold(5,Threshold[4])
    def decrease_bed6(self,event):
        Threshold[5]=Threshold[5]-5
        if Threshold[5]<0:
            Threshold[5]=0
        threshold6.text=str(Threshold[5])
        saveThreshold(6,Threshold[5])
    def decrease_bed7(self,event):
        Threshold[6]=Threshold[6]-5
        if Threshold[6]<0:
            Threshold[6]=0
        threshold7.text=str(Threshold[6])
        saveThreshold(7,Threshold[6])
    def decrease_bed8(self,event):
        Threshold[7]=Threshold[7]-5
        if Threshold[7]<0:
            Threshold[7]=0
        threshold8.text=str(Threshold[7])
        saveThreshold(8,Threshold[7])
    '''
    def bed_state1(self,event):
        if self.bed1_state.state=='down':
            print("bed1_state is down")
            self.bed1_state.text='ON'
            self.bed1_state.background_color=(.50,1,.99,1)
            Auto_BedState[0]=1
            turnBedOn(1)
        else:
            print("bed1_state is up")
            self.bed1_state.text='OFF'
            self.bed1_state.background_color=(.168,.25,.75,1)
            Auto_BedState[0]=0
            turnBedOff(1)
    def bed_state2(self,event):
        if self.bed2_state.state=='down':
            self.bed2_state.text='ON'
            self.bed2_state.background_color=(.50,1,.99,1)
            Auto_BedState[1]=1
            turnBedOn(2)
        else:
            self.bed2_state.text='OFF'
            self.bed2_state.background_color=(.168,.25,.75,1)
            Auto_BedState[1]=0
            turnBedOff(2)
    def bed_state3(self,event):
        if self.bed3_state.state=='down':
            self.bed3_state.text='ON'
            self.bed3_state.background_color=(.50,1,.99,1)
            Auto_BedState[2]=1
            turnBedOn(3)
        else:
            self.bed3_state.text='OFF'
            self.bed3_state.background_color=(.168,.25,.75,1)
            Auto_BedState[2]=0
            turnBedOff(3)
    def bed_state4(self,event):
        if self.bed4_state.state=='down':
            self.bed4_state.text='ON'
            self.bed4_state.background_color=(.50,1,.99,1)
            Auto_BedState[3]=1
            turnBedOn(4)
        else:
            self.bed4_state.text='OFF'
            self.bed4_state.background_color=(.168,.25,.75,1)
            Auto_BedState[3]=0
            turnBedOff(4)
    def bed_state5(self,event):
        if self.bed5_state.state=='down':
            self.bed5_state.text='ON'
            self.bed5_state.background_color=(.50,1,.99,1)
            Auto_BedState[4]=1
            turnBedOn(5)
        else:
            self.bed5_state.text='OFF'
            self.bed5_state.background_color=(.168,.25,.75,1)
            Auto_BedState[4]=0
            turnBedOff(5)
    def bed_state6(self,event):
        if self.bed6_state.state=='down':
            self.bed6_state.text='ON'
            self.bed6_state.background_color=(.50,1,.99,1)
            Auto_BedState[5]=1
            turnBedOn(6)
        else:
            self.bed6_state.text='OFF'
            self.bed6_state.background_color=(.168,.25,.75,1)
            Auto_BedState[5]=0
            turnBedOff(6)
    def bed_state7(self,event):
        if self.bed7_state.state=='down':
            self.bed7_state.text='ON'
            self.bed7_state.background_color=(.50,1,.99,1)
            Auto_BedState[6]=1
            turnBedOn(7)
        else:
            self.bed7_state.text='OFF'
            self.bed7_state.background_color=(.168,.25,.75,1)
            Auto_BedState[6]=0
            turnBedOff(7)
    def bed_state8(self,event):
        if self.bed8_state.state=='down':
            self.bed8_state.text='ON'
            self.bed8_state.background_color=(.50,1,.99,1)
            Auto_BedState[7]=1
            turnBedOn(8)
        else:
            self.bed8_state.text='OFF'
            self.bed8_state.background_color=(.168,.25,.75,1)
            Auto_BedState[7]=0
            turnBedOff(8)
    '''
    def watering_option1(self,event):
        if water_option1.state=='down':
            water_option1.text='Soaker'
            water_option1.background_color=(.50,1,.99,1)
            WaterOption[0]=1
            setSoaker(1)
        else:
            water_option1.text='Drip'
            water_option1.background_color=(0,0,1,1)
            WaterOption[0]=0
            setDrip(1)
    def watering_option2(self,event):
        if water_option2.state=='down':
            water_option2.text='Soaker'
            water_option2.background_color=(.50,1,.99,1)
            WaterOption[1]=1
            setSoaker(2)
        else:
            water_option2.text='Drip'
            water_option2.background_color=(0,0,1,1)
            WaterOption[1]=0
            setDrip(2)
    def watering_option3(self,event):
        if water_option3.state=='down':
            water_option3.text='Soaker'
            water_option3.background_color=(.50,1,.99,1)
            WaterOption[2]=1
            setSoaker(3)
        else:
            water_option3.text='Drip'
            water_option3.background_color=(0,0,1,1)
            WaterOption[2]=0
            setDrip(3)
    def watering_option4(self,event):
        if water_option4.state=='down':
            water_option4.text='Soaker'
            water_option4.background_color=(.50,1,.99,1)
            WaterOption[3]=1
            setSoaker(4)
        else:
            water_option4.text='Drip'
            water_option4.background_color=(0,0,1,1)
            WaterOption[3]=0
            setDrip(4)
    def watering_option5(self,event):
        if water_option5.state=='down':
            water_option5.text='Soaker'
            water_option5.background_color=(.50,1,.99,1)
            WaterOption[4]=1
            setSoaker(5)
        else:
            water_option5.text='Drip'
            water_option5.background_color=(0,0,1,1)
            WaterOption[4]=0
            setDrip(5)
    def watering_option6(self,event):
        if water_option6.state=='down':
            water_option6.text='Soaker'
            water_option6.background_color=(.50,1,.99,1)
            WaterOption[5]=1
            setSoaker(6)
        else:
            water_option6.text='Drip'
            water_option6.background_color=(0,0,1,1)
            WaterOption[5]=0
            setDrip(6)
    def watering_option7(self,event):
        if water_option7.state=='down':
            water_option7.text='Soaker'
            water_option7.background_color=(.50,1,.99,1)
            WaterOption[6]=1
            setSoaker(7)
        else:
            water_option7.text='Drip'
            water_option7.background_color=(0,0,1,1)
            WaterOption[6]=0
            setDrip(7)
    def watering_option8(self,event):
        if water_option8.state=='down':
            water_option8.text='Soaker'
            water_option8.background_color=(.50,1,.99,1)
            WaterOption[7]=1
            setSoaker(8)
        else:
            water_option8.text='Drip'
            water_option8.background_color=(0,0,1,1)
            WaterOption[7]=0
            setDrip(8)
    '''
    #global increase_routine
    #global decrease_routine
    #def increase_routine(thresh):
    #    thresh=thresh+5 #the rest of the function will read the index of the array and increase the threshold value stored there then stores the new value into the same index of the array. Decrease will be the same but obviously the inverse

    #def decrease_routine(thresh):
    #    thresh=thresh-5

    def __init__(self,**kwargs):
        super(home_screen,self).__init__(**kwargs)
        '''
        global threshold1
        global threshold2
        global threshold3
        global threshold4
        global threshold5
        global threshold6
        global threshold7
        global threshold8
        global water_option1
        global water_option2
        global water_option3
        global water_option4
        global water_option5
        global water_option6
        global water_option7
        global water_option8
        '''
        self.auto_init()
        Layout=GridLayout(cols=8,rows=4,size_hint=(1,.70),spacing=20)
        grid_layout=GridLayout(cols=8,size_hint=(1,.20),padding=[100,20,0,5],spacing=20)
        box_layout=BoxLayout(orientation='vertical',padding=[20,20,20,20])#use size_hint_y for the layouts added for the bed layout and pagebutton layout
        clock_layout=BoxLayout(size_hint=(1,.10),padding=[20,5,20,0],spacing=200) #left, top, right, bottom

        #create labels
        #threshold1=Label(text=str(Threshold[0]),color=[0,0,1,1],font_size=50)
        #threshold2=Label(text=str(Threshold[1]),color=[0,0,1,1],font_size=50)
        #threshold3=Label(text=str(Threshold[2]),color=[0,0,1,1],font_size=50)
        #threshold4=Label(text=str(Threshold[3]),color=[0,0,1,1],font_size=50)
        #threshold5=Label(text=str(Threshold[4]),color=[0,0,1,1],font_size=50)
        #threshold6=Label(text=str(Threshold[5]),color=[0,0,1,1],font_size=50)
        #threshold7=Label(text=str(Threshold[6]),color=[0,0,1,1],font_size=50)
        #threshold8=Label(text=str(Threshold[7]),color=[0,0,1,1],font_size=50)
        #create buttons and attach events
        #auto_button=Button(text="Auto",font_size=25,color=[0,1,0,1],width=200,on_press=self.auto_routine)
        manual_button=Button(text="Manual",font_size=50,on_press=self.manual_routine,background_color=[.38,.47,.6,2])
        manual_button.bind(on_pre_enter=manual_screen.on_pre_enter)
        settings_button=Button(text="Options",font_size=50,on_press=self.settings_routine,background_color=[.38,.47,.6,2])
        settings_button.bind(on_pre_enter=settings_screen.on_pre_enter)
        #update_button=Button(text="Update",font_size=25,color=[0,1,0,1],width=200,on_press=self.update_routine)
        #cancel_button=Button(text="Cancel",font_size=25,color=[0,1,0,1],width=200,on_press=self.cancel_routine)
        start_button=Button(text="Start",font_size=25,width=200,on_press=self.auto_routine,background_color=[.38,.47,.6,2])
        #increase_thresh1=Button(on_press=self.increase_bed1,border=(16,16,0,16),text='+',font_size=50,background_color=[.50,1,.99,2])
        #increase_thresh2=Button(on_press=self.increase_bed2,border=(16,16,0,16),text='+',font_size=50,background_color=[.50,1,.99,2])
        #increase_thresh3=Button(on_press=self.increase_bed3,border=(16,16,0,16),text='+',font_size=50,background_color=[.50,1,.99,2])
        #increase_thresh4=Button(on_press=self.increase_bed4,border=(16,16,0,16),text='+',font_size=50,background_color=[.50,1,.99,2])
        #increase_thresh5=Button(on_press=self.increase_bed5,border=(16,16,0,16),text='+',font_size=50,background_color=[.50,1,.99,2])
        #increase_thresh6=Button(on_press=self.increase_bed6,border=(16,16,0,16),text='+',font_size=50,background_color=[.50,1,.99,2])
        #increase_thresh7=Button(on_press=self.increase_bed7,border=(16,16,0,16),text='+',font_size=50,background_color=[.50,1,.99,2])
        #increase_thresh8=Button(on_press=self.increase_bed8,border=(16,16,0,16),text='+',font_size=50,background_color=[.50,1,.99,2])
        #decrease_thresh1=Button(on_press=self.decrease_bed1,border=(0,16,16,16),text='-',font_size=50,background_color=[.50,1,.99,2])
        #decrease_thresh2=Button(on_press=self.decrease_bed2,border=(0,16,16,16),text='-',font_size=50,background_color=[.50,1,.99,2])
        #decrease_thresh3=Button(on_press=self.decrease_bed3,border=(0,16,16,16),text='-',font_size=50,background_color=[.50,1,.99,2])
        #decrease_thresh4=Button(on_press=self.decrease_bed4,border=(0,16,16,16),text='-',font_size=50,background_color=[.50,1,.99,2])
        #decrease_thresh5=Button(on_press=self.decrease_bed5,border=(0,16,16,16),text='-',font_size=50,background_color=[.50,1,.99,2])
        #decrease_thresh6=Button(on_press=self.decrease_bed6,border=(0,16,16,16),text='-',font_size=50,background_color=[.50,1,.99,2])
        #decrease_thresh7=Button(on_press=self.decrease_bed7,border=(0,16,16,16),text='-',font_size=50,background_color=[.50,1,.99,2])
        #decrease_thresh8=Button(on_press=self.decrease_bed8,border=(0,16,16,16),text='-',font_size=50,background_color=[.50,1,.99,2])
        self.bed1_state=ToggleButton(on_press=self.bed_state1,text=auto_states[0],background_color=bed_color[0],state=auto_buttonstates[0], font_size=40, background_normal='')
        self.bed2_state=ToggleButton(on_press=self.bed_state2,text=auto_states[1],background_color=bed_color[1],state=auto_buttonstates[1], font_size=40, background_normal='')
        self.bed3_state=ToggleButton(on_press=self.bed_state3,text=auto_states[2],background_color=bed_color[2],state=auto_buttonstates[2], font_size=40, background_normal='')
        self.bed4_state=ToggleButton(on_press=self.bed_state4,text=auto_states[3],background_color=bed_color[3],state=auto_buttonstates[3], font_size=40, background_normal='')
        self.bed5_state=ToggleButton(on_press=self.bed_state5,text=auto_states[4],background_color=bed_color[4],state=auto_buttonstates[4], font_size=40, background_normal='')
        self.bed6_state=ToggleButton(on_press=self.bed_state6,text=auto_states[5],background_color=bed_color[5],state=auto_buttonstates[5], font_size=40, background_normal='')
        self.bed7_state=ToggleButton(on_press=self.bed_state7,text=auto_states[6],background_color=bed_color[6],state=auto_buttonstates[6], font_size=40, background_normal='')
        self.bed8_state=ToggleButton(on_press=self.bed_state8,text=auto_states[7],background_color=bed_color[7],state=auto_buttonstates[7], font_size=40, background_normal='')
        #water_option1=ToggleButton(on_press=self.watering_option1,text=water_type[0],size_hint=(.4,.4),background_color=water_color[0],state=water_buttonstates[0])
        #water_option2=ToggleButton(on_press=self.watering_option2,text=water_type[1],size_hint=(.4,.4),background_color=water_color[1],state=water_buttonstates[1])
        #water_option3=ToggleButton(on_press=self.watering_option3,text=water_type[2],size_hint=(.4,.4),background_color=water_color[2],state=water_buttonstates[2])
        #water_option4=ToggleButton(on_press=self.watering_option4,text=water_type[3],size_hint=(.4,.4),background_color=water_color[3],state=water_buttonstates[3])
        #water_option5=ToggleButton(on_press=self.watering_option5,text=water_type[4],size_hint=(.4,.4),background_color=water_color[4],state=water_buttonstates[4])
        #water_option6=ToggleButton(on_press=self.watering_option6,text=water_type[5],size_hint=(.4,.4),background_color=water_color[5],state=water_buttonstates[5])
        #water_option7=ToggleButton(on_press=self.watering_option7,text=water_type[6],size_hint=(.4,.4),background_color=water_color[6],state=water_buttonstates[6])
        #water_option8=ToggleButton(on_press=self.watering_option8,text=water_type[7],size_hint=(.4,.4),background_color=water_color[7],state=water_buttonstates[7])

        myClock = TickTock(font_size=60)
        Clock.schedule_interval(myClock.update, 1)

        #add the widgets to the layout
        for i in range(8):
            Layout.add_widget(Label(text=''))
        for i in range(1, 9):
            Layout.add_widget(Label(text=f"Bed {i}",font_size=30))
        Layout.add_widget(self.bed1_state)
        Layout.add_widget(self.bed2_state)
        Layout.add_widget(self.bed3_state)
        Layout.add_widget(self.bed4_state)
        Layout.add_widget(self.bed5_state)
        Layout.add_widget(self.bed6_state)
        Layout.add_widget(self.bed7_state)
        Layout.add_widget(self.bed8_state)
        for i in range(8):
            Layout.add_widget(Label(text=''))

        #float_layout.add_widget(auto_button)
        grid_layout.add_widget(manual_button)
        grid_layout.add_widget(settings_button)
        clock_layout.add_widget(Label(text='HOME',font_size=60))
        clock_layout.add_widget(myClock)
        #grid_layout.add_widget(update_button)
        #Layout.add_widget(cancel_button)
        box_layout.add_widget(clock_layout)
        box_layout.add_widget(Layout)
        box_layout.add_widget(grid_layout)

        self.add_widget(box_layout)

class manual_screen(Screen):
    global manual_states
    global manual_buttonstates
    global mbed_color
    global sensor_values
    global mwater_type
    global mwater_buttonstates
    global mwater_color
    global sensor_text
    global sensor_color

    mwater_type=[0,0,0,0,0,0,0,0]
    mwater_buttonstates=[0,0,0,0,0,0,0,0]
    mwater_color=[0,0,0,0,0,0,0,0]
    manual_states=[0,0,0,0,0,0,0,0]
    sensor_values=[0,0,0,0,0,0,0,0]
    sensor_text=[' ',' ',' ',' ',' ',' ',' ',' ']
    manual_buttonstates=[0,0,0,0,0,0,0,0]
    mbed_color=[0,0,0,0,0,0,0,0]
    sensor_color=[0,0,0,0,0,0,0,0]

    def manual_init(self,*args):
        Threshold=getThresholds()
        Auto_BedState=getAllBedStatus()
        WaterOption=getWaterHose()
        waterTime=wateringTime()
        Manual_BedState=getAllBedStatus()

        for index in range(len(Manual_BedState)):
            if Manual_BedState[index]==1:
                manual_states[index]='ON'
                manual_buttonstates[index]='down'
                mbed_color[index]=[.50,1,.99,1]
            else:
                manual_states[index]='OFF'
                manual_buttonstates[index]='normal'
                mbed_color[index]=[.168,.25,.75,1]

        for index in range(len(WaterOption)):
            if WaterOption[index]==1:
                mwater_type[index]='Soaker'
                mwater_buttonstates[index]='down'
                mwater_color[index]=[0,1,0,1]
            else:
                mwater_type[index]='Drip'
                mwater_buttonstates[index]='normal'
                mwater_color[index]=[0,0,1,1]

    def on_pre_enter(self,*args):
        Threshold=getThresholds()
        Auto_BedState=getAllBedStatus()
        WaterOption=getWaterHose()
        waterTime=wateringTime()
        Manual_BedState=getAllBedStatus()

        for index in range(len(Manual_BedState)):
            if Manual_BedState[index]==1:
                manual_states[index]='ON'
                manual_buttonstates[index]='down'
                mbed_color[index]=[.50,1,.99,1]
            else:
                manual_states[index]='OFF'
                manual_buttonstates[index]='normal'
                mbed_color[index]=[.168,.25,.75,1]

        for index in range(len(WaterOption)):
            if WaterOption[index]==1:
                mwater_type[index]='Soaker'
                mwater_buttonstates[index]='down'
                mwater_color[index]=[.50,1,.99,1]
            else:
                mwater_type[index]='Drip'
                mwater_buttonstates[index]='normal'
                mwater_color[index]=[.168,.25,.75,1]

        self.mbed1_state.text=manual_states[0]
        self.mbed1_state.state=manual_buttonstates[0]
        self.mbed1_state.background_color=mbed_color[0]
        self.mbed2_state.text=manual_states[1]
        self.mbed2_state.state=manual_buttonstates[1]
        self.mbed2_state.background_color=mbed_color[1]
        self.mbed3_state.text=manual_states[2]
        self.mbed3_state.state=manual_buttonstates[2]
        self.mbed3_state.background_color=mbed_color[2]
        self.mbed4_state.text=manual_states[3]
        self.mbed4_state.state=manual_buttonstates[3]
        self.mbed4_state.background_color=mbed_color[3]
        self.mbed5_state.text=manual_states[4]
        self.mbed5_state.state=manual_buttonstates[4]
        self.mbed5_state.background_color=mbed_color[4]
        self.mbed6_state.text=manual_states[5]
        self.mbed6_state.state=manual_buttonstates[5]
        self.mbed6_state.background_color=mbed_color[5]
        self.mbed7_state.text=manual_states[6]
        self.mbed7_state.state=manual_buttonstates[6]
        self.mbed7_state.background_color=mbed_color[6]
        self.mbed8_state.text=manual_states[7]
        self.mbed8_state.state=manual_buttonstates[7]
        self.mbed8_state.background_color=mbed_color[7]

##        mwater_option1.text=mwater_type[0]
##        mwater_option1.state=mwater_buttonstates[0]
##        mwater_option1.background_color=mwater_color[0]
##        mwater_option2.text=mwater_type[1]
##        mwater_option2.state=mwater_buttonstates[1]
##        mwater_option2.background_color=mwater_color[1]
##        mwater_option3.text=mwater_type[2]
##        mwater_option3.state=mwater_buttonstates[2]
##        mwater_option3.background_color=mwater_color[2]
##        mwater_option4.text=mwater_type[3]
##        mwater_option4.state=mwater_buttonstates[3]
##        mwater_option4.background_color=mwater_color[3]
##        mwater_option5.text=mwater_type[4]
##        mwater_option5.state=mwater_buttonstates[4]
##        mwater_option5.background_color=mwater_color[4]
##        mwater_option6.text=mwater_type[5]
##        mwater_option6.state=mwater_buttonstates[5]
##        mwater_option6.background_color=mwater_color[5]
##        mwater_option7.text=mwater_type[6]
##        mwater_option7.state=mwater_buttonstates[6]
##        mwater_option7.background_color=mwater_color[6]
##        mwater_option8.text=mwater_type[7]
##        mwater_option8.state=mwater_buttonstates[7]
##        mwater_option8.background_color=mwater_color[7]
        self.read_sensors()

    def return_toAuto(self,event):
        self.manager.current='Home_screen'

    def to_settings(self,event):
        self.manager.current='Settings_screen'

    def read_sensors(self,*args):
        def writeR():
                ser.flushInput()
                ser.flushOutput()
                ser.write(b'R')

                sens_read1.text='Loading...'
                sens_read2.text='Loading...'
                sens_read3.text='Loading...'
                sens_read4.text='Loading...'
                sens_read5.text='Loading...'
                sens_read6.text='Loading...'
                sens_read7.text='Loading...'
                sens_read8.text='Loading...'

                sens_read1.color = [1,1,1,1]
                sens_read2.color = [1,1,1,1]
                sens_read3.color = [1,1,1,1]
                sens_read4.color = [1,1,1,1]
                sens_read5.color = [1,1,1,1]
                sens_read6.color = [1,1,1,1]
                sens_read7.color = [1,1,1,1]
                sens_read8.color = [1,1,1,1]

        def read_sens():
            while ser.inWaiting()==0:
                pass
            for index in range(len(sensor_values)):
                tempval = ser.readline()
                sensor_values[index] = float(tempval)

        def change_sensval():
            print("change_sensval() called")
            for index in range(len(sensor_values)):
                    # Subject to change
                    if sensor_values[index] >= 35:
                            print(sensor_values[index])
                            sensor_text[index] = 'Great!'
                            sensor_color[index] = [1,1,1,1]
                    if sensor_values[index] <= 34 and sensor_values[index] >= 20:
                            print(sensor_values[index])
                            sensor_text[index] = 'Okay.'
                            sensor_color[index] = [1,1,1,1]
                    if sensor_values[index] < 21:
                            print(sensor_values[index])
                            sensor_text[index] = 'Needs\nWater'
                            sensor_color[index] = [1,0,0,1]

            sens_read1.text=sensor_text[0]
            sens_read2.text=sensor_text[1]
            sens_read3.text=sensor_text[2]
            sens_read4.text=sensor_text[3]
            sens_read5.text=sensor_text[4]
            sens_read6.text=sensor_text[5]
            sens_read7.text=sensor_text[6]
            sens_read8.text=sensor_text[7]

            sens_read1.color = sensor_color[0]
            sens_read2.color = sensor_color[1]
            sens_read3.color = sensor_color[2]
            sens_read4.color = sensor_color[3]
            sens_read5.color = sensor_color[4]
            sens_read6.color = sensor_color[5]
            sens_read7.color = sensor_color[6]
            sens_read8.color = sensor_color[7]


        Clock.schedule_once(lambda N: writeR(),0)
        Clock.schedule_once(lambda O: read_sens(),1.5)
        Clock.schedule_once(lambda P: change_sensval(),2)

    def start_manual(self,event):
        def Dialog_Open():
            Dialog.open()
            pass

        def Reset_Buffs():
            ser.flushInput()
            ser.flushOutput()
            print("Resetting input and output buffer...")
            Bar.value = 10

        def Write_A():
            ser.write(b'A')
        def Write_G1():
            ser.write(b'G')
            for x in Threshold:
                ser.write(str.encode(f"{x}\n"))
            print("Thresholds done.")
            Bar.value = 30
        def Write_G2():
            ser.write(b'G')
            for x in Auto_BedState:
                ser.write(str.encode(f"{x}\n"))
            print("Auto Beds On/Off done.")
            Bar.value = 50
        def Write_G3():
            ser.write(b'G')
            for x in WaterOption:
                ser.write(str.encode(f"{x}\n"))
            print("Timers done.")
            Bar.value = 70
        def Write_G4():
            ser.write(b'G')
            for x in Manual_BedState:
                ser.write(str.encode(f"{x}\n"))
            Bar.value = 90
        def Wait_Break():
            Bar.value = 100
            print("Reads are finished.")
        def Dialog_Close():
            Dialog.dismiss()
        def Write_M():
            ser.write(b'M')


        def Read_watering():
            self.manager.current='Watering_screen'

        # Instantiate dialog
        Grid = GridLayout(rows=2)
        Dialog_Label = Label(text="Sending Data...",font_size=30)
        Grid.add_widget(Dialog_Label)
        Bar = ProgressBar(max=100)
        Grid.add_widget(Bar)
        Dialog = Popup(title='Manual mode initialized...',title_size=20,title_align='center',content=Grid,size=(500,300),size_hint=(None,None),auto_dismiss=False)


        # Schedule the read/write events
        Clock.schedule_once(lambda C: Dialog_Open(),0)
        Clock.schedule_once(lambda D: Reset_Buffs(),0)
        Clock.schedule_once(lambda E: Write_M(),1.6)
        Clock.schedule_once(lambda F: Write_G1(),2.6)
        Clock.schedule_once(lambda G: Write_G2(),5.6)
        Clock.schedule_once(lambda H: Write_G3(),8.6)
        Clock.schedule_once(lambda I: Write_G4(),11.6)
        Clock.schedule_once(lambda J: Wait_Break(),14.6)
        #Clock.schedule_once(lambda K: Write_M(),16.6)
        Clock.schedule_once(lambda L: Dialog_Close(),17)
        Clock.schedule_once(lambda M: Read_watering(),18)



    def mbed_state1(self,event):
        if self.mbed1_state.state=='down':
            self.mbed1_state.text='ON'
            self.mbed1_state.background_color=(.50,1,.99,1)
            Manual_BedState[0]=1
        else:
            self.mbed1_state.text='OFF'
            self.mbed1_state.background_color=(.168,.25,.75,1)
            Manual_BedState[0]=0


    def mbed_state2(self,event):
        if self.mbed2_state.state=='down':
            self.mbed2_state.text='ON'
            self.mbed2_state.background_color=(.50,1,.99,1)
            Manual_BedState[1]=1
        else:
            self.mbed2_state.text='OFF'
            self.mbed2_state.background_color=(.168,.25,.75,1)
            Manual_BedState[1]=0


    def mbed_state3(self,event):
        if self.mbed3_state.state=='down':
            self.mbed3_state.text='ON'
            self.mbed3_state.background_color=(.50,1,.99,1)
            Manual_BedState[2]=1
        else:
            self.mbed3_state.text='OFF'
            self.mbed3_state.background_color=(.168,.25,.75,1)
            Manual_BedState[2]=0


    def mbed_state4(self,event):
        if self.mbed4_state.state=='down':
            self.mbed4_state.text='ON'
            self.mbed4_state.background_color=(.50,1,.99,1)
            Manual_BedState[3]=1
        else:
            self.mbed4_state.text='OFF'
            self.mbed4_state.background_color=(.168,.25,.75,1)
            Manual_BedState[3]=0


    def mbed_state5(self,event):
        if self.mbed5_state.state=='down':
            self.mbed5_state.text='ON'
            self.mbed5_state.background_color=(.50,1,.99,1)
            Manual_BedState[4]=1
        else:
            self.mbed5_state.text='OFF'
            self.mbed5_state.background_color=(.168,.25,.75,1)
            Manual_BedState[4]=0


    def mbed_state6(self,event):
        if self.mbed6_state.state=='down':
            self.mbed6_state.text='ON'
            self.mbed6_state.background_color=(.50,1,.99,1)
            Manual_BedState[5]=1
        else:
            self.mbed6_state.text='OFF'
            self.mbed6_state.background_color=(.168,.25,.75,1)
            Manual_BedState[5]=0


    def mbed_state7(self,event):
        if self.mbed7_state.state=='down':
            self.mbed7_state.text='ON'
            self.mbed7_state.background_color=(.50,1,.99,1)
            Manual_BedState[6]=1
        else:
            self.mbed7_state.text='OFF'
            self.mbed7_state.background_color=(.168,.25,.75,1)
            Manual_BedState[6]=0


    def mbed_state8(self,event):
        if self.mbed8_state.state=='down':
            self.mbed8_state.text='ON'
            self.mbed8_state.background_color=(.50,1,.99,1)
            Manual_BedState[7]=1
        else:
            self.mbed8_state.text='OFF'
            self.mbed8_state.background_color=(.168,.25,.75,1)
            Manual_BedState[7]=0
##
##
##    def mwatering_option1(self,event):
##        if mwater_option1.state=='down':
##            mwater_option1.text='Soaker'
##            mwater_option1.background_color=(.50,1,.99,1)
##            WaterOption[0]=1
##        else:
##            mwater_option1.text='Drip'
##            mwater_option1.background_color=(0,0,1,1)
##            WaterOption[0]=0
##
##
##    def mwatering_option2(self,event):
##        if mwater_option2.state=='down':
##            mwater_option2.text='Soaker'
##            mwater_option2.background_color=(.50,1,.99,1)
##            WaterOption[1]=1
##        else:
##            mwater_option2.text='Drip'
##            mwater_option2.background_color=(0,0,1,1)
##            WaterOption[1]=0
##
##
##    def mwatering_option3(self,event):
##        if mwater_option3.state=='down':
##            mwater_option3.text='Soaker'
##            mwater_option3.background_color=(.50,1,.99,1)
##            WaterOption[2]=1
##        else:
##            mwater_option3.text='Drip'
##            mwater_option3.background_color=(0,0,1,1)
##            WaterOption[2]=0
##
##    def mwatering_option4(self,event):
##        if mwater_option4.state=='down':
##            mwater_option4.text='Soaker'
##            mwater_option4.background_color=(.50,1,.99,1)
##            WaterOption[3]=1
##        else:
##            mwater_option4.text='Drip'
##            mwater_option4.background_color=(0,0,1,1)
##            WaterOption[3]=0
##
##
##    def mwatering_option5(self,event):
##        if mwater_option5.state=='down':
##            mwater_option5.text='Soaker'
##            mwater_option5.background_color=(.50,1,.99,1)
##            WaterOption[4]=1
##        else:
##            mwater_option5.text='Drip'
##            mwater_option5.background_color=(0,0,1,1)
##            WaterOption[4]=0
##
##
##    def mwatering_option6(self,event):
##        if mwater_option6.state=='down':
##            mwater_option6.text='Soaker'
##            mwater_option6.background_color=(.50,1,.99,1)
##            WaterOption[5]=1
##        else:
##            mwater_option6.text='Drip'
##            mwater_option6.background_color=(0,0,1,1)
##            WaterOption[5]=0
##
##
##    def mwatering_option7(self,event):
##        if mwater_option7.state=='down':
##            mwater_option7.text='Soaker'
##            mwater_option7.background_color=(.50,1,.99,1)
##            WaterOption[6]=1
##        else:
##            mwater_option7.text='Drip'
##            mwater_option7.background_color=(0,0,1,1)
##            WaterOption[6]=0
##
##
##    def mwatering_option8(self,event):
##        if mwater_option8.state=='down':
##            mwater_option8.text='Soaker'
##            mwater_option8.background_color=(.50,1,.99,1)
##            WaterOption[7]=1
##        else:
##            mwater_option8.text='Drip'
##            mwater_option8.background_color=(0,0,1,1)
##            WaterOption[7]=0


    def __init__(self,**kwargs):
##        global mwater_option1
##        global mwater_option2
##        global mwater_option3
##        global mwater_option4
##        global mwater_option5
##        global mwater_option6
##        global mwater_option7
##        global mwater_option8
        global sens_read1
        global sens_read2
        global sens_read3
        global sens_read4
        global sens_read5
        global sens_read6
        global sens_read7
        global sens_read8

        super(manual_screen,self).__init__(**kwargs)
        self.manual_init()
        mgrid_layout1=GridLayout(cols=8,rows=5,size_hint=(1,.7),spacing=20,padding=[5,0,5,0])
        mgrid_layout2=GridLayout(cols=8,size_hint=(1,.20),padding=[100,30,0,5],spacing=20)
        mbox_layout=BoxLayout(orientation='vertical')
        clock_box=BoxLayout(size_hint=(1,.10),padding=[20,5,20,0],spacing=200)

        home_button=Button(text='Home',font_size=50,on_press=self.return_toAuto,background_color=[.38,.47,.6,2])
        home_button.bind(on_pre_enter=home_screen.on_pre_enter)
        settings_button=Button(text='Options',font_size=50,on_press=self.to_settings,background_color=[.38,.47,.6,2])
        settings_button.bind(on_pre_enter=settings_screen.on_pre_enter)
        # sensorRead_button=Button(text='Read Sensors',font_size=25,on_press=self.read_sensors,width=300,background_color=[.38,.47,.6,2])
        manual_start=Button(text='Start',font_size=50,on_press=self.start_manual,background_color=[.38,.47,.6,2])

        self.mbed1_state=ToggleButton(text=manual_states[0],state=manual_buttonstates[0],background_color=mbed_color[0],on_press=self.mbed_state1,font_size=40)
        self.mbed2_state=ToggleButton(text=manual_states[1],state=manual_buttonstates[1],background_color=mbed_color[1],on_press=self.mbed_state2,font_size=40)
        self.mbed3_state=ToggleButton(text=manual_states[2],state=manual_buttonstates[2],background_color=mbed_color[2],on_press=self.mbed_state3,font_size=40)
        self.mbed4_state=ToggleButton(text=manual_states[3],state=manual_buttonstates[3],background_color=mbed_color[3],on_press=self.mbed_state4,font_size=40)
        self.mbed5_state=ToggleButton(text=manual_states[4],state=manual_buttonstates[4],background_color=mbed_color[4],on_press=self.mbed_state5,font_size=40)
        self.mbed6_state=ToggleButton(text=manual_states[5],state=manual_buttonstates[5],background_color=mbed_color[5],on_press=self.mbed_state6,font_size=40)
        self.mbed7_state=ToggleButton(text=manual_states[6],state=manual_buttonstates[6],background_color=mbed_color[6],on_press=self.mbed_state7,font_size=40)
        self.mbed8_state=ToggleButton(text=manual_states[7],state=manual_buttonstates[7],background_color=mbed_color[7],on_press=self.mbed_state8,font_size=40)
        screen_label=Label(text='MANUAL',font_size=60)

        sens_read1=Label(text=sensor_text[0],font_size=25) #should dynamically change the color of the sensor values red green or yellow based on our data
        sens_read2=Label(text=sensor_text[1],font_size=25) #should dynamically change the color of the sensor values red green or yellow based on our data
        sens_read3=Label(text=sensor_text[2],font_size=25) #should dynamically change the color of the sensor values red green or yellow based on our data
        sens_read4=Label(text=sensor_text[3],font_size=25) #should dynamically change the color of the sensor values red green or yellow based on our data
        sens_read5=Label(text=sensor_text[4],font_size=25) #should dynamically change the color of the sensor values red green or yellow based on our data
        sens_read6=Label(text=sensor_text[5],font_size=25) #should dynamically change the color of the sensor values red green or yellow based on our data
        sens_read7=Label(text=sensor_text[6],font_size=25) #should dynamically change the color of the sensor values red green or yellow based on our data
        sens_read8=Label(text=sensor_text[7],font_size=25) #should dynamically change the color of the sensor values red green or yellow based on our data
        '''
        mwater_option1=ToggleButton(text=mwater_type[0],size_hint=(.25,.25),background_color=mwater_color[0],state=mwater_buttonstates[0],on_press=self.mwatering_option1)
        mwater_option2=ToggleButton(text=mwater_type[1],size_hint=(.25,.25),background_color=mwater_color[1],state=mwater_buttonstates[1],on_press=self.mwatering_option2)
        mwater_option3=ToggleButton(text=mwater_type[2],size_hint=(.25,.25),background_color=mwater_color[2],state=mwater_buttonstates[2],on_press=self.mwatering_option3)
        mwater_option4=ToggleButton(text=mwater_type[3],size_hint=(.25,.25),background_color=mwater_color[3],state=mwater_buttonstates[3],on_press=self.mwatering_option4)
        mwater_option5=ToggleButton(text=mwater_type[4],size_hint=(.25,.25),background_color=mwater_color[4],state=mwater_buttonstates[4],on_press=self.mwatering_option5)
        mwater_option6=ToggleButton(text=mwater_type[5],size_hint=(.25,.25),background_color=mwater_color[5],state=mwater_buttonstates[5],on_press=self.mwatering_option6)
        mwater_option7=ToggleButton(text=mwater_type[6],size_hint=(.25,.25),background_color=mwater_color[6],state=mwater_buttonstates[6],on_press=self.mwatering_option7)
        mwater_option8=ToggleButton(text=mwater_type[7],size_hint=(.25,.25),background_color=mwater_color[7],state=mwater_buttonstates[7],on_press=self.mwatering_option8)
        '''

        myClock = TickTock(font_size=60)
        Clock.schedule_interval(myClock.update, 1)

        for i in range(8):
            mgrid_layout1.add_widget(Label(text=''))
        for i in range(1, 9):
            mgrid_layout1.add_widget(Label(text=f"Bed {i}",font_size=30))
        mgrid_layout1.add_widget(sens_read1)
        mgrid_layout1.add_widget(sens_read2)
        mgrid_layout1.add_widget(sens_read3)
        mgrid_layout1.add_widget(sens_read4)
        mgrid_layout1.add_widget(sens_read5)
        mgrid_layout1.add_widget(sens_read6)
        mgrid_layout1.add_widget(sens_read7)
        mgrid_layout1.add_widget(sens_read8)
        mgrid_layout1.add_widget(self.mbed1_state)
        mgrid_layout1.add_widget(self.mbed2_state)
        mgrid_layout1.add_widget(self.mbed3_state)
        mgrid_layout1.add_widget(self.mbed4_state)
        mgrid_layout1.add_widget(self.mbed5_state)
        mgrid_layout1.add_widget(self.mbed6_state)
        mgrid_layout1.add_widget(self.mbed7_state)
        mgrid_layout1.add_widget(self.mbed8_state)
        for i in range(8):
            mgrid_layout1.add_widget(Label(text=''))


##        mgrid_layout1.add_widget(mwater_option1)
##        mgrid_layout1.add_widget(mwater_option2)
##        mgrid_layout1.add_widget(mwater_option3)
##        mgrid_layout1.add_widget(mwater_option4)
##        mgrid_layout1.add_widget(mwater_option5)
##        mgrid_layout1.add_widget(mwater_option6)
##        mgrid_layout1.add_widget(mwater_option7)
##        mgrid_layout1.add_widget(mwater_option8)

        mgrid_layout2.add_widget(home_button)
        mgrid_layout2.add_widget(settings_button)
        # mgrid_layout2.add_widget(sensorRead_button)
        mgrid_layout2.add_widget(manual_start)

        clock_box.add_widget(screen_label)
        clock_box.add_widget(myClock)

        mbox_layout.add_widget(clock_box)
        mbox_layout.add_widget(mgrid_layout1)
        mbox_layout.add_widget(mgrid_layout2)

        self.add_widget(mbox_layout)

class watering_screen(Screen):

    def check_watering(self,*args):
        print("check_watering")
        # if GPIO.input(27):
        #     check()
        # else:
        #     check.cancel()
        #     self.manager.current='Home_screen'

    def check_schedule(self,*args):
        global check
        check=Clock.schedule_once(lambda W:self.check_watering(),60)
        return check
    def on_enter(self,*args):
        self.check_schedule()

    def RestartDuino(self,*args):
        print("RestartDuino")
        # GPIO.output(17,1)
        # sleep(0.5)
        # GPIO.output(17,0)

    def __init__(self,**kwargs):
        super(watering_screen,self).__init__(**kwargs)
        watering_screen_grid = GridLayout(cols = 3, rows = 3)

        watering_screen_grid.add_widget(Label(text="Currently watering...", font_size=30))
        watering_screen_grid.add_widget(Button(text="ABORT", background_color=[1,0,0,1], font_size=50, on_press=self.RestartDuino))

        self.add_widget(watering_screen_grid)

class settings_screen(Screen):

    global wait_times
    global AM_label
    global PM_label

    wait_times = []
    tempAM,tempPM = getAutoWaitTime()
    wait_times.append(tempAM)
    wait_times.append(tempPM)

##    def change_thresh(self,*args):
##        self.thresh_dialog.open()

    def winterize(self,*args):
        self.winterize_dialog.open()

    def wait_time(self,*args):
        self.waittime_dialog.open()

    def check_faults(self,*args):
        self.manager.current='Fault_screen'

    def return_toAuto(self,event):
        self.manager.current='Home_screen'

##    def thresh_popup(self,*args):
##        self.thresh_options.open()

    def start_winter(self,*args):
        ser.flushInput()
        ser.flushOutput()
        ser.write(b'W')

    def inc_wait_time(self,*args):
        if wait_times[0] == 11:
            pass
        else:
            wait_times[0] = wait_times[0] + 1

        if wait_times[1] == 23:
            pass
        else:
            wait_times[1] = wait_times[1] + 1

        am_time = wait_times[0]
        pm_time = wait_times[1]

        AM_label.text=str(am_time) + ":00"
        PM_label.text=str(pm_time) + ":00"

        setAutoWaitTime(am_time,pm_time)

    def dec_wait_time(self,*args):

        if wait_times[0] == 0:
            pass
        else:
            wait_times[0] = wait_times[0] - 1

        if wait_times[1] == 12:
            pass
        else:
            wait_times[1] = wait_times[1] - 1

        am_time = wait_times[0]
        pm_time = wait_times[1]

        AM_label.text=str(am_time) + ":00"
        PM_label.text=str(pm_time) + ":00"

        setAutoWaitTime(am_time,pm_time)

##    bed_grid = GridLayout(cols=8,padding=[20,70,20,70],spacing=25)
##    bed1=Button(text='Bed 1',on_press=thresh_popup)
##    bed2=Button(text='Bed 2',on_press=thresh_popup)
##    bed3=Button(text='Bed 3',on_press=thresh_popup)
##    bed4=Button(text='Bed 4',on_press=thresh_popup)
##    bed5=Button(text='Bed 5',on_press=thresh_popup)
##    bed6=Button(text='Bed 6',on_press=thresh_popup)
##    bed7=Button(text='Bed 7',on_press=thresh_popup)
##    bed8=Button(text='Bed 8',on_press=thresh_popup)
##    bed_grid.add_widget(bed1)
##    bed_grid.add_widget(bed2)
##    bed_grid.add_widget(bed3)
##    bed_grid.add_widget(bed4)
##    bed_grid.add_widget(bed5)
##    bed_grid.add_widget(bed6)
##    bed_grid.add_widget(bed7)
##    bed_grid.add_widget(bed8)
##    thresh_dialog = Popup(title="Please select which bed's threshold you would like to change",title_size=20,content=bed_grid,title_align='center',size_hint=(.50,.25),auto_dismiss=False)
##
##    thresh_grid = GridLayout(cols=2,padding=[20,70,20,70],spacing=50)
##    increase=Button(text='Increase watering frequency')
##    decrease=Button(text='Decrease watering frequency')
##    thresh_grid.add_widget(increase)
##    thresh_grid.add_widget(decrease)
##    thresh_options = Popup(title="Please select an option",title_size=20,content=thresh_grid,title_align='center',size_hint=(.50,.25),auto_dismiss=False)

    winter_layout = BoxLayout(orientation='vertical')
    continue_box=BoxLayout()
    winterL1=Label(text='Please open all manual valves!',font_size=50,color=[1,0,0,1])
    winterL2=Label(text='Please disconnect all hoses!',font_size=50,color=[1,0,0,1])
    begin_btn=Button(text='Begin!',size_hint=(.50,.50),font_size=50,on_press=start_winter)
    cancel_btn=Button(text='Cancel',size_hint=(.50,.50),font_size=50)
    winter_layout.add_widget(winterL1)
    winter_layout.add_widget(winterL2)
    continue_box.add_widget(begin_btn)
    continue_box.add_widget(cancel_btn)
    winter_layout.add_widget(continue_box)

    winterize_dialog = Popup(title="Winterize Steps",title_size=20,content=winter_layout,title_align='center',size_hint=(.88,.88),auto_dismiss=False)
    begin_btn.bind(on_press=winterize_dialog.dismiss)
    cancel_btn.bind(on_press=winterize_dialog.dismiss)

    wait_time_layout=BoxLayout(orientation='vertical',spacing=40)
    wait_grid1=GridLayout(cols=2,size_hint=(1,.20))
    wait_grid2=GridLayout(cols=2,rows=2,size_hint=(1,.70),spacing=20)
    AM_label=Label(text=str(wait_times[0]) + ":00",font_size=50)
    PM_label=Label(text=str(wait_times[1]) + ":00",font_size=50)
    morningwater=Label(text='Morning Water Time', font_size=30)
    eveningwater=Label(text='Evening Water Time', font_size=30)
    exitwait_btn=Button(text='Exit',font_size=50,size_hint=(.20,.20))

    increase_btn=Button(text='Increase time intervals',font_size=25, on_press=inc_wait_time)
    decrease_btn=Button(text='Decrease time intervals',font_size=25, on_press=dec_wait_time)
    wait_grid1.add_widget(morningwater)
    wait_grid1.add_widget(eveningwater)
    wait_grid2.add_widget(AM_label)
    wait_grid2.add_widget(PM_label)
    wait_grid2.add_widget(decrease_btn)
    wait_grid2.add_widget(increase_btn)
    wait_time_layout.add_widget(wait_grid1)
    wait_time_layout.add_widget(wait_grid2)
    wait_time_layout.add_widget(exitwait_btn)
    waittime_dialog=Popup(title='Auto Wait Time Settings',title_size=40,content=wait_time_layout,title_align='center',size_hint=(.85,.85),auto_dismiss=False)
    exitwait_btn.bind(on_press=waittime_dialog.dismiss)




    def __init__(self,**kwargs):
        super(settings_screen,self).__init__(**kwargs)
        box=BoxLayout(orientation='vertical',padding=[50,80,50,80],spacing=45)

        #change_thresh_btn=Button(text='Change Thresholds',on_press=self.change_thresh,font_size=48,background_color=[.38,.47,.6,2])
        winterize_btn=Button(text='Winterize Routine',on_press=self.winterize,font_size=48,background_color=[.38,.47,.6,2])
        wait_time_btn=Button(text='Auto Wait Time',on_press=self.wait_time,font_size=48,background_color=[.38,.47,.6,2])
        faults_btn=Button(text='Check Faults',on_press=self.check_faults,font_size=48,background_color=[.38,.47,.6,2])
        faults_btn.bind(on_pre_enter=fault_screen.on_pre_enter)
        home_btn=Button(text='Return to Home',font_size=48,on_press=self.return_toAuto,background_color=[.38,.47,.6,2])
        #box.add_widget(change_thresh_btn)
        box.add_widget(winterize_btn)
        box.add_widget(wait_time_btn)
        box.add_widget(faults_btn)
        box.add_widget(home_btn)

        self.add_widget(box)

class fault_screen(Screen):

    def __init__(self,**kwargs):
        super(fault_screen,self).__init__(**kwargs)
        #box = BoxLayout(orientation='vertical',padding=[50,80,50,80],spacing=20)
        box = GridLayout(cols=2,rows=5,padding=[50,80,50,80],spacing=20)

        global bed_fault_btns
        global flow_fault_btn
        bed_fault_btns = [0, 0, 0, 0, 0, 0, 0, 0]

        for i in range(len(bed_fault_btns)):
            bed_fault_btns[i] = Button(text=' ',
                                       color=[0,1,0,1],
                                       font_size=35,
                                       background_color=[.38,.47,.6,2],
                                       disabled=True,
                                       )
        flow_fault_btn = Button(text=' ',
                                   color=[0,1,0,1],
                                   font_size=35,
                                   background_color=[.38,.47,.6,2],
                                   disabled=True,
                                   )
        home_btn=Button(text='Return to Home',font_size=48,on_press=self.return_toAuto,background_color=[.38,.47,.6,2])

        for btn in bed_fault_btns:
            box.add_widget(btn)
        box.add_widget(flow_fault_btn)
        box.add_widget(home_btn)

        self.add_widget(box)

    def return_toAuto(self,event):
        self.manager.current='Home_screen'

    def read_faults(self,*args):
        global faults
        global temp_text
        global temp_color

        faults=[0,0,0,0,0,0,0,0,0]
        temp_text=[0,0,0,0,0,0,0,0,0]
        temp_color=[0,0,0,0,0,0,0,0,0]

        def Write_E():
            ser.flushInput()
            ser.flushOutput()
            ser.write(b'E')

            for btn in bed_fault_btns:
                btn.text = "Loading..."
                btn.color = [1,1,1,1]
            flow_fault_btn.text = "Loading..."
            flow_fault_btn.color = [1,1,1,1]

        def get_faults():
            for btn in bed_fault_btns:
                btn.text = "Obtaining data..."
                btn.color = [1,1,1,1]
            flow_fault_btn.text = "Obtaining data..."
            flow_fault_btn.color = [1,1,1,1]

            sleep(.1)

            while ser.inWaiting()==0:
                pass

            for index in range(len(faults)):
                tempval = ser.readline()
                faults[index] = float(tempval)

        def update_faults():
            for i in range(len(faults)):
                if faults[i] == 1:
                    temp_text[i] = 'Error on Bed ' + str(i+1)
                    temp_color[i] = [1,0,0,1]
                else:
                    temp_text[i] = "Bed " + str(i+1) + " good"
                    temp_color[i] = [1,1,1,1]

            if faults[8] == 1:
                temp_text[8] = "Flow sensor error"
                temp_color[8] = [1,0,0,1]
            else:
                temp_text[8] = "Flow sensor good"
                temp_color[8] = [1,1,1,1]

            for i in range(len(bed_fault_btns)):
                bed_fault_btns[i].text = temp_text[i]
                bed_fault_btns[i].color = temp_color[i]

            flow_fault_btn.text = temp_text[8]
            flow_fault_btn.color = temp_color[8]

        Clock.schedule_once(lambda Q: Write_E(),0)
        Clock.schedule_once(lambda R: get_faults(),1.5)
        Clock.schedule_once(lambda S: update_faults(),3)

    #def on_pre_enter(self,*args):
    def on_enter(self,*args):
        self.read_faults()

class display_app(App):
    def build(self):
        sm=ScreenManager()
        Home_screen = home_screen(name='Home_screen')
        Manual_screen = manual_screen(name='Manual_screen')
        Watering_screen = watering_screen(name='Watering_screen')
        Settings_screen = settings_screen(name='Settings_screen')
        Fault_screen = fault_screen(name='Fault_screen')
        sm.add_widget(Home_screen)
        sm.add_widget(Manual_screen)
        sm.add_widget(Watering_screen)
        sm.add_widget(Settings_screen)
        sm.add_widget(Fault_screen)
        return sm

if __name__=="__main__":
    display_app().run()
