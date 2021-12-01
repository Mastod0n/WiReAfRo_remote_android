# This project and all related work & material by the author is licensed under Creative Commons - Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
# For more info, visit https://creativecommons.org/licenses/by-nc-sa/4.0/
# ______
# This application was written for a proof-of-concept project to utilize everyday wifi networks and TCP sockets as remote controls for RC vehicles and robotics.
# Now it's used for a educational and affordable beginner project to build and remotely control a small vehicle utilizing an ESP8266, Motor controller, some motors and suitable batteries.
# ______
# In this usage case, the application will send two values in a string, each for one motor and each ranges 1024 steps for each forward and reverse movement.
# values: 0 - 1023 reverse, 1023 - 2046 forward, where 1023 is shared to stop.
# String formatting: x.y\n (x = integer left, y = integer right), example for stop: "1023.1023\n", "\n" is used by the receiver as a mark to stop reading the string.
# ______
# Project pages:
# github.com/Mastod0n
# thingiverse.com/Mastod0n
# schaffenburg.org/Projekte (German)
# [hackaday.io URl]


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
import socket


class Body(BoxLayout):
    def __init__(self, **kwargs):
        super(Body, self).__init__(**kwargs)

        self.ip = "192.168.3.1"
        self.port = "40"
        self.deadzone = 400
        self.stepsize = 50
        self.threshold = 50
        self.recentL = 1023
        self.recentR = 1023
        
        def TCPsender(valL, valR):
            try:
                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soc.connect((inputIP.text, int(inputPort.text)))
                soc.send(("".join([str(int(valL)), ".", str(int(valR)), "\n"])).encode())
                soc.close
                labelDebug.text = "No errors."
            except socket.error:
                labelDebug.text = "A socket error occurred.\nAre you connected to the correct WiFi?\nAre IP and Port valid and correct?"

        
        def ConnectionHandlerL(value):
            if (value >= 1023 - self.deadzone and value <= 1023 + self.deadzone) and self.recentL != 1023:
                self.recentL = 1023
                TCPsender(1023, self.recentR)

            elif value >= 2046 - self.threshold and self.recentL != 2046:
                self.recentL = 2046
                TCPsender(2046, self.recentR)

            elif value <= 0 + self.threshold and self.recentL != 0:
                self.recentL = 0
                TCPsender(0, self.recentR)

            elif (value > 1023 + self.deadzone or value < 1023 - self.deadzone) and (value >= self.recentL + self.stepsize or value <= self.recentL - self.stepsize):
                self.recentL = value
                TCPsender(value, self.recentR)
                

        def ConnectionHandlerR(value):
            if (value >= 1023 - self.deadzone and value <= 1023 + self.deadzone) and self.recentR != 1023:
                self.recentR = 1023
                TCPsender(self.recentL, 1023)

            elif value >= 2046 - self.threshold and self.recentR != 2048:
                self.recentR = 2046
                TCPsender(self.recentL, 2046)

            elif value <= 0 + self.threshold and self.recentR != 0:
                self.recentR = 0
                TCPsender(self.recentL, 0)
            
            elif (value > 1023 + self.deadzone or value < 1023 - self.deadzone) and (value >= self.recentR + self.stepsize or value <= self.recentR - self.stepsize):
                self.recentR = value
                TCPsender(self.recentL, value)


        sLayoutMid = BoxLayout(orientation = "vertical")
        ssLayoutSV = BoxLayout(orientation = "horizontal", size_hint = (1, .1))
        ssLayoutDebug = BoxLayout(orientation = "vertical")
        ssLayoutIP = BoxLayout(orientation = "horizontal", size_hint = (1, .15))
        ssLayoutPort = BoxLayout(orientation = "horizontal", size_hint = (1, .15))
        
        sliderL = Slider(min = 0,
                         max = 2046,
                         value = 1023,
                         orientation = "vertical",
                         step = 1)
        
        sliderR = Slider(min = 0,
                         max = 2046,
                         value = 1023,
                         orientation = "vertical",
                         step = 1)
        
        labelL = Label(text = str(int(sliderL.value)))
        labelR = Label(text = str(int(sliderR.value)))

        labelDebug = Label(text="TCP Remote V1.1")

        labelIP = Label(text = "IP: ", size_hint = (.1, .6))
        labelPort = Label(text = "Port: ", size_hint = (.1, .6))
        inputIP = TextInput(text = self.ip, size_hint_x = .6, size_hint_y = .6, multiline = False)
        inputPort = TextInput(text = self.port, size_hint_x = .6, size_hint_y = .6, multiline = False)
        
        def SliderLabelUpdaterL(instance, value):
            labelL.text = str(int(value))
            ConnectionHandlerL(value)

        def SliderLabelUpdaterR(instance, value):
            labelR.text = str(int(value))
            ConnectionHandlerR(value)

        def TouchUpHandlerL(self, touch):
            if touch.grab_current is self:
                self.value = 1023
                touch.ungrab(self)
                ConnectionHandlerL(1023)
                return True

        def TouchUpHandlerR(self, touch):
            if touch.grab_current is self:
                self.value = 1023
                touch.ungrab(self)
                ConnectionHandlerR(1023)
                return True

        sliderL.bind(value = SliderLabelUpdaterL)
        sliderR.bind(value = SliderLabelUpdaterR)

        sliderL.bind(on_touch_up = TouchUpHandlerL)
        sliderR.bind(on_touch_up = TouchUpHandlerR)

        ssLayoutSV.add_widget(labelL)
        ssLayoutSV.add_widget(labelR)
        sLayoutMid.add_widget(ssLayoutSV)

        ssLayoutDebug.add_widget(labelDebug)
        sLayoutMid.add_widget(ssLayoutDebug)

        ssLayoutIP.add_widget(labelIP)
        ssLayoutIP.add_widget(inputIP)
        sLayoutMid.add_widget(ssLayoutIP)

        ssLayoutPort.add_widget(labelPort)
        ssLayoutPort.add_widget(inputPort)
        sLayoutMid.add_widget(ssLayoutPort)
        
        self.add_widget(sliderL)
        self.add_widget(sLayoutMid)
        self.add_widget(sliderR)
        


class WiFiremote(App):
    def build(self):
        return Body()
        

if __name__ == "__main__":
    WiFiremote().run()
