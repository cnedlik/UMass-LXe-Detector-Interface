# Co-developed by Chris Nedlik and Anthony Raykh

# -*- coding: utf-8 -*- 
import tkinter as tk 
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as anime
from matplotlib import style
from matplotlib.lines import Line2D
import u3
import nidaqmx
import time
from time import gmtime, strftime
import matplotlib.pyplot as plt
import numpy as np
import tkinter.filedialog as fd
import csv 
from pymodbus.client.sync import ModbusTcpClient as MC
from UliEngineering.Physics.RTD import pt100_temperature
import smtplib
import on_off as oo
import json
import requests

#=========================================================================#
##########################  PROGRAM START  ################################
#=========================================================================#

# Initial Alarm Thresholds
PT1_alarm_threshold = 3.0 # Detector
PT1_alarm_lower = -1.0     # Detector
PT2_alarm_threshold = 0.5 # Emergency Tank
PT4_alarm_threshold = 0.5 # LACO Vessel

# Initial Recipe Parameters
mfc3_delay      = 1.0   # sec 
mfc2_multiplier = 2.5
dose_flow_rate  = 50.0  # SCCM
dose_flow_time  = 120.0 # sec
flush_flow_rate = 50.0 # SCCM
flush_flow_time = 120.0 # sec

#Time between samples in ms
sample_interval = 3000

# Plot fontsizes
title_font = 10 # for plots
ylabel_font = 9 # for plots

# Plot linewidths
linewidth = 1

# Initial Plot Time Window 
t_window = 1.0
leading_buffer = 0.1
time_ = 'hours'

# Plot colors
pressure_color = 'k'
level_color = 'darkcyan'
temperature_color = 'crimson'
flow_color = 'b'
setpoint_color = 'y'

#Readout Box Position Parameters
x1=410
x2=610
x3=810
x4=1010

#MFC Correction Parameters
b1 = 0 #Best Fit Parameters for MFC2
m1 = 1.0415
b2 = 0 #Best Fit Paremeters for MFC2
m2 = 1.0414
b3 = 0 #Best Fit Parameters for MFC3
m3 = 1.0392

setpointconstant1 = 0; setpointconstant2 = 0; setpointconstant3 = 0; 

# Special Font Sizes 
LARGE_FONT  = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 8 )

#Level Sensor Board Access
host = '192.168.1.2'
port = 502
client = MC(host, port)
client.connect() 

#Initializing labjack 
d = u3.U3(localId = 1) #----> High Voltage 
g = u3.U3(localId = 2) #----> Low Voltage

# Initializing Matplotlib Figure     
fig = Figure() 
style.use("bmh")
plt.ion() ##look at this later 

# Initializing Timing
t0    = time.time()
t0str = strftime("%b%d%Y%H%M", gmtime()) 

#Creating Subplots
ax_PT1   = fig.add_subplot(4,4,1 )
ax_PT2   = fig.add_subplot(4,4,5 )
ax_PT3   = fig.add_subplot(4,4,9 )
ax_PT4   = fig.add_subplot(4,4,13)
ax_LVL0  = fig.add_subplot(4,4,2 )
ax_LVL1  = fig.add_subplot(4,4,6 )
ax_TEMP0 = fig.add_subplot(4,4,10)
ax_TEMP1 = fig.add_subplot(4,4,14)
ax_MFC1  = fig.add_subplot(4,4,3 )
ax_MFC2  = fig.add_subplot(4,4,7 )
ax_MFC3  = fig.add_subplot(4,4,11)
ax_CM1   = fig.add_subplot(4,4,4 )
ax_CM2   = fig.add_subplot(4,4,8 )
ax12 = fig.add_subplot(4,4,12); ax15 = fig.add_subplot(4,4,15); ax16 = fig.add_subplot(4,4,16)

#Setting the appropriate Y and X boundaries 
ax_PT1.set_ylim(1.0, 1.4)       # bara
ax_PT2.set_ylim(-0.05, 0.5)      # bara
ax_PT3.set_ylim(1, 1.8)      # bara
ax_PT4.set_ylim(-0.05, 0.25)       # bara
ax_LVL0.set_ylim(0.20, 0.28)     # arb.
ax_LVL1.set_ylim(0.770, 0.785)     # arb.
ax_TEMP0.set_ylim(-107, -104) # Celsius
ax_TEMP1.set_ylim(-112, 25) # Celsius
ax_MFC1.set_ylim(1, 2)      # slpm
ax_MFC2.set_ylim(0, 100)    # sccm
ax_MFC3.set_ylim(0, 60)     # sccm
ax_CM1.set_ylim(1, 1.8)    # bara
ax_CM2.set_ylim(-20, 1333)    # mbara 

#Titles and axes labels
ax_PT1.set_title("Detector Pressure (PT1)", fontsize=title_font);                  ax_PT1.set_ylabel("bara", fontsize=ylabel_font)
ax_PT2.set_title("Emergency Recovery Pressure (PT2)", fontsize=title_font);        ax_PT2.set_ylabel("bara", fontsize=ylabel_font)
ax_PT3.set_title("Injection Panel Outlet Pressure (PT3)", fontsize=title_font);    ax_PT3.set_ylabel("bara", fontsize=ylabel_font)
ax_PT4.set_title("LACO Vessel Pressure (PT4)", fontsize=title_font);               ax_PT4.set_ylabel("bara", fontsize=ylabel_font)
ax_LVL0.set_title("Inlet Level Sensor (LVL0)", fontsize=title_font);               ax_LVL0.set_ylabel('arb.', fontsize=ylabel_font)
ax_LVL1.set_title("Weir Level Sensor (LVL1)", fontsize=title_font);                ax_LVL1.set_ylabel("arb.", fontsize=ylabel_font)
ax_TEMP0.set_title("Bottom of Cryostat Temperature (TEMP0)", fontsize=title_font); ax_TEMP0.set_ylabel("Degrees Celsius", fontsize=ylabel_font)
ax_TEMP1.set_title("Temperature Sensor 1 (TEMP1)", fontsize=title_font);           ax_TEMP1.set_ylabel("Degrees Celsius", fontsize=ylabel_font)
ax_MFC1.set_title("Circulation Mass Flow (MFC1)", fontsize=title_font);            ax_MFC1.set_ylabel("slpm", fontsize=ylabel_font)
ax_MFC2.set_title("Injection Panel Flow (MFC2)", fontsize=title_font);             ax_MFC2.set_ylabel("sccm", fontsize=ylabel_font)
ax_MFC3.set_title("Dose Flow (MFC3)", fontsize=title_font);                        ax_MFC3.set_ylabel("sccm", fontsize=ylabel_font)
ax_CM1.set_title("Dose Volume Manometer (CM1)", fontsize=title_font);              ax_CM1.set_ylabel("bara", fontsize=ylabel_font)
ax_CM2.set_title("Bottle Region Manometer (CM2)", fontsize=title_font);            ax_CM2.set_ylabel("mbara", fontsize=ylabel_font)

#Creating Line objects with colors and linewidths to populate graphs 
line_PT1   = Line2D([],[]); line_PT2   = Line2D([],[]); line_PT3   = Line2D([],[]); line_PT4   = Line2D([],[]) 
line_LVL0  = Line2D([],[]); line_LVL1  = Line2D([],[]); line_TEMP0 = Line2D([],[]); #line_TEMP1 = Line2D([],[])
line_MFC1  = Line2D([],[]); line_MFC2  = Line2D([],[]); line_MFC3  = Line2D([],[]); 
line_CM1   = Line2D([],[]); line_CM2   = Line2D([],[])  
line_PT1.set_color(pressure_color); line_PT2.set_color(pressure_color); line_PT3.set_color(pressure_color); line_PT4.set_color(pressure_color)
line_LVL0.set_color(level_color);   line_LVL1.set_color(level_color);   line_TEMP0.set_color(temperature_color); #line_TEMP1.set_color(temperature_color)
line_MFC1.set_color(flow_color);    line_MFC2.set_color(flow_color);    line_MFC3.set_color(flow_color)
line_CM1.set_color(pressure_color); line_CM2.set_color(pressure_color)
line_PT1.set_linewidth(linewidth);  line_PT2.set_linewidth(linewidth);  line_PT3.set_linewidth(linewidth); line_PT4.set_linewidth(linewidth)
line_LVL0.set_linewidth(linewidth); line_LVL1.set_linewidth(linewidth); line_TEMP0.set_linewidth(linewidth); #line_TEMP1.set_linewidth(linewidth)
line_MFC1.set_linewidth(linewidth); line_MFC2.set_linewidth(linewidth); line_MFC3.set_linewidth(linewidth)
line_CM1.set_linewidth(linewidth);  line_CM2.set_linewidth(linewidth)

#MFC Setpoint Lines
line_MFC1_sp = Line2D([], []); line_MFC1_sp.set_color(setpoint_color); line_MFC1_sp.set_linestyle('-.'); line_MFC1_sp.set_linewidth(linewidth)
line_MFC2_sp = Line2D([], []); line_MFC2_sp.set_color(setpoint_color); line_MFC2_sp.set_linestyle('-.'); line_MFC2_sp.set_linewidth(linewidth)
line_MFC3_sp = Line2D([], []); line_MFC3_sp.set_color(setpoint_color); line_MFC3_sp.set_linestyle('-.'); line_MFC3_sp.set_linewidth(linewidth)

#Attributing the line objects to the correct axes
ax_PT1.add_line(line_PT1);      ax_PT2.add_line(line_PT2);      ax_PT3.add_line(line_PT3);      ax_PT4.add_line(line_PT4);
ax_MFC1.add_line(line_MFC1);    ax_MFC2.add_line(line_MFC2);    ax_MFC3.add_line(line_MFC3);
ax_LVL0.add_line(line_LVL0);    ax_LVL1.add_line(line_LVL1);    ax_TEMP0.add_line(line_TEMP0);  #ax_TEMP1.add_line(line_TEMP1);
ax_CM1.add_line(line_CM1);      ax_CM2.add_line(line_CM2);
ax_MFC1.add_line(line_MFC1_sp); ax_MFC2.add_line(line_MFC2_sp); ax_MFC3.add_line(line_MFC3_sp);

#Initializing Data Arrays
t_sec=[]; t_min=[]; t_hour=[]; t_day=[];
setpoint1 = []; setpoint2 = []; setpoint3 = [];
PT1  = []; PT2  = []; PT3   = []; PT4   = [];
CM1  = []; CM2  = [];  
MFC1 = []; MFC2 = []; MFC3  = []; 
LVL0 = []; LVL1 = []; TEMP0 = []; #TEMP1 = []; 

#Function to create pop up messages. Creates new tkinter window with pop up message as the (string) input. 
def popupmsg(msg): 
    popup = tk.Tk()
    def leavemini(): 
        popup.destroy()
    popup.wm_title("!")
    label = ttk.Label(popup, text = msg, font = MEDIUM_FONT)
    label.pack(side = "top", fill = "x", pady = 10)
    B1 = ttk.Button(popup, text = "Okay", command = leavemini)
    B1.pack()
    popup.mainloop()
    
# Function to save data 
def Save(path, name, data):
    with open(str(path) + "\\" + str(name) + "." + "csv", "w") as output:
        writer = csv.writer(output, lineterminator = '\n')
        for val in data:
            writer.writerow([val])
        output.close()
        
def OpenFile():
    global path
    path = fd.askdirectory(initialdir = "C:\\users\\hertel\\desktop\\.spyder-py3\\LXe_System_Data\\")
        
# Calls the capitalized "Save" function with the path being the one chosen in "OpenFile".
def save(): 
    Save(path, str(t0str) + "Pressure_Transducer_1"  , PT1)
    Save(path, str(t0str) + "Pressure_Transducer_2"  , PT2)
    Save(path, str(t0str) + "Pressure_Transducer_3"  , PT3)
    Save(path, str(t0str) + "Pressure_Transducer_4"  , PT4)
    Save(path, str(t0str) + "Mass_Flow_Controller_1" , MFC1)
    Save(path, str(t0str) + "Mass_Flow_Controller_2" , MFC2)
    Save(path, str(t0str) + "Mass_Flow_Controller_3" , MFC3)
    Save(path, str(t0str) + "Capacitance_Manometer_1", CM1)
    Save(path, str(t0str) + "Capacitance_Manometer_2", CM2)
    Save(path, str(t0str) + "Setpoint_MFC1"          , setpoint1)
    Save(path, str(t0str) + "Setpoint_MFC2"          , setpoint2)
    Save(path, str(t0str) + "Setpoint_MFC3"          , setpoint3)
    Save(path, str(t0str) + "Level_O"                , LVL0)
    Save(path, str(t0str) + "Level_1"                , LVL1)
    Save(path, str(t0str) + "Temperature_Sensor_O"   , TEMP0)
    #Save(path, str(t0str) + "Temperature_Sensor_1"   , TEMP1)

def setMFC1(Voltage): #MFC1
    DAC0_VALUE = d.voltageToDACBits(Voltage, dacNumber = 0, is16Bits = False)
    d.getFeedback(u3.DAC0_8(DAC0_VALUE))
    
def setMFC2(Voltage):
    DAC0_VALUE = g.voltageToDACBits(Voltage, dacNumber = 1, is16Bits = False)
    g.getFeedback(u3.DAC1_8(DAC0_VALUE)) 
    
def setMFC3(Voltage):
    DAC0_VALUE = g.voltageToDACBits(Voltage, dacNumber = 0, is16Bits = False)
    g.getFeedback(u3.DAC0_8(DAC0_VALUE))     

def extend_setpoint1(setpoint):
    setpoint1.extend([setpoint])
def extend_setpoint2(setpoint):
    setpoint2.extend([setpoint])
def extend_setpoint3(setpoint):
    setpoint3.extend([setpoint])


#Email and Text Alarm Setup
def text_email_alarm(textmessage, emailmessage):
    email = '#####.###.########@gmail.com'
    smtpObj = smtplib.SMTP_SSL('64.233.184.108', 465)
    smtpObj.ehlo()
    smtpObj.login(email,'password')
    # Mark
    smtpObj.sendmail(email, '##########@tmomail.net', textmessage)
    smtpObj.sendmail(email, '######@umass.edu', emailmessage)
    # Chris
    smtpObj.sendmail(email, '##########@vtext.com', textmessage)
    smtpObj.sendmail(email, '########@gmail.com', emailmessage)
    # Scott
    smtpObj.sendmail(email, '##########@vtext.com', textmessage ) 
    smtpObj.sendmail(email, '############@gmail.com', emailmessage)

# Slack Alarm Function
def slack_alarm(message):
    webhook_url = "https://hooks.slack.com/services/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"
    response = requests.post(webhook_url, data =json.dumps({'text': message}),\
                             headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise ValueError('Request to slack returned an error %s, the response is:\n%s'\
                         % (response.status_code, response.text))

### Functions to read out labjack
PT1_counter  = 0
PT1_corrected = []
def read_PT1():
    global PT1_counter
    global PT1_alarm_threshold
    global PT1_alarm_lower
    with nidaqmx.Task() as task: 
        task.ai_channels.add_ai_voltage_chan("Dev2/ai1")
        v = task.read() 
        j = np.size(t_sec)
        pressure = (((v/330)*10**3)-4)*(5/16)
        PT1.extend([pressure])
        
        # Data filter #####################################################
        if j >= 3:
           PT1_avg = ((PT1[j-1] + PT1[j-2] + PT1[j-3])/3)
           if (pressure <= PT1_avg*1.013) and (pressure >= PT1_avg*0.988):
               PT1_corrected.extend([pressure])
           else:
               PT1_corrected.extend([PT1_avg])
        else:
            PT1_corrected.extend([pressure])

        # Alarm Code ######################################################
        if ((PT1_corrected[-1] > PT1_alarm_threshold) & (PT1_counter == 0)):
            close_all()
            oo.CV0(True)
            text_message = 'Pressure in PT1 (Detector Volume) has exceeded '+str(PT1_alarm_threshold)+' bar.'
            email_message = 'Subject:PT1 Alarm Triggered\n'+text_message
            slack_alarm(text_message)
            text_email_alarm(text_message, email_message)
            PT1_counter = 1
        if ((PT1_corrected[-1] < PT1_alarm_lower) & (PT1_counter == 0)):
            close_all()
            text_message = 'Pressure in PT1 has dropped below '+str(PT1_alarm_lower)+' bar.'
            email_message = 'Subject:PT1 Alarm Triggered\n'+text_message
            slack_alarm(text_message)
            text_email_alarm(text_message, email_message)
            PT1_counter = 1


PT2_counter = 0
PT2_corrected = []
def read_PT2():
    global PT2_counter
    global PT2_alarm_threshold
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev2/ai2")
        v2 = task.read()
        pressure2 = (((v2/330.0)*10.0**3.0)-4.0)*(10.0/16.0)
        PT2.extend([pressure2])
        j = np.size(t_sec)
        
        # Data Filter #####################################################
        if j >= 3:
           PT2_avg = ((PT2[j-1] + PT2[j-2] + PT2[j-3])/3)
           if (pressure2 <= PT2_avg*1.026) and (pressure2 >= PT2_avg*0.976):
               PT2_corrected.extend([pressure2])
           else:
               PT2_corrected.extend([PT2_avg])
        else:
            PT2_corrected.extend([pressure2])     

        # Alarm Code ######################################################
        if ((PT2_corrected[-1] > PT2_alarm_threshold) & (PT2_counter == 0)):
            close_all()
            text_message = 'Pressure in PT2 (propane tank) has exceeded '+str(PT2_alarm_threshold)+' bar.'
            email_message = 'Subject:PT2 Alarm Triggered\n'+text_message
            slack_alarm(text_message)
            text_email_alarm(text_message, email_message)
            PT2_counter = 1
            
            
PT3_corrected = []
def read_PT3():
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev2/ai3")
        v5 = task.read()
        pressure5 = (((v5/330.0)*10.0**3.0)-4.0)*(15.0/16.0)
        PT3.extend([pressure5])
        
        # Data Filter ######################################################
        j = np.size(t_sec)
        if j >= 3:
           PT3_avg = ((PT3[j-1] + PT3[j-2] + PT3[j-3])/3)
           if (pressure5 <= PT3_avg*1.039) and (pressure5 >= PT3_avg*0.964):
               PT3_corrected.extend([pressure5])
           else:
               PT3_corrected.extend([PT3_avg])
        else:
            PT3_corrected.extend([pressure5])     


PT4_counter = 0 
PT4_corrected= []
def read_PT4():
    global PT4_counter
    global PT4_alarm_threshold
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev2/ai5")
        v9 = task.read()
        pressure9 = (((v9/330.0)*10.0**3.0)-4)*(3/16.0)
        PT4.extend([pressure9])
        
        # Data Filter######################################################
        j = np.size(t_sec)

        if j >= 3:
           PT4_avg = ((PT4[j-1] + PT4[j-2] + PT4[j-3])/3)
           if (pressure9 <= PT4_avg*1.008) and (pressure9 >= PT4_avg*0.992):
               PT4_corrected.extend([pressure9])
           else:
               PT4_corrected.extend([PT4_avg])
        else:
            PT4_corrected.extend([pressure9])     
        ####################################################################
        
        # Alarm Code ######################################################
        if ((PT4_corrected[-1] > PT4_alarm_threshold) & (PT4_counter == 0)):
            close_all()
            text_message = 'Pressure in PT4 (LACO Volume) has exceeded '+str(PT4_alarm_threshold)+' bar.'
            email_message = 'Subject:PT4 Alarm Triggered\n'+text_message
            slack_alarm(text_message)
            text_email_alarm(text_message, email_message)
            PT4_counter = 1
   
def read_MFC1():
    flow1 = d.getAIN(3)
    MFC1.extend([flow1])

def read_MFC2():
    flow2 = d.getAIN(1)  
    MFC2.extend([flow2*50])

def read_MFC3(): 
    flow3 = d.getAIN(0)
    MFC3.extend([flow3*10.0]) #SCCM 

def read_CM1(): 
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev2/ai4")
        P1 = task.read()
        CM1.extend([(25*P1)/14.5038])

def read_CM2():
    P2 = d.getAIN(2)
    CM2.extend([(P2*100.0)*1.333])
    
def read_LVL0():
    rr = client.read_input_registers(0, 4, unit=1)
    if rr.getRegister(0) > 32767:
        lvl0 = (rr.getRegister(0) - 65536)/4096.0
    else:
        lvl0 = rr.getRegister(0)/4096.0 
    LVL0.extend([-lvl0])
    
def read_LVL1():
    rr = client.read_input_registers(0, 4, unit=1)
    if rr.getRegister(1) > 32767:
        lvl1 = (rr.getRegister(1) - 65536)/4096.0
    else:
        lvl1 = rr.getRegister(1)/4096.0 
    LVL1.extend([-lvl1])
    
def read_TEMP0():
    rr = client.read_input_registers(0, 4, unit=1)
    temp0 = pt100_temperature(rr.getRegister(2)/512)
    TEMP0.extend([temp0])
        
#def read_TEMP1():
#    rr = client.read_input_registers(0, 4, unit=1)
#    temp1 = pt100_temperature(rr.getRegister(3)/512)
#    TEMP1.extend([temp1])
    
def extend_time(): 
    global counter
    t_sec.extend([(round(time.time()-t0,3))])
    t_min.extend([(round(time.time()-t0,3)/60.0)])
    t_hour.extend([(round(time.time()-t0,3)/3600.0)])
    t_day.extend([(round(time.time()-t0,3)/86400.0)])
    
def close_all():
    oo.IV1(False); oo.IV2(False); oo.IV3(False); oo.IV4(False); oo.IV5(False); oo.IV6(False); oo.IV7(False); oo.IV8(False)
    oo.IV9(False); oo.IV10(False); oo.IV11(False); oo.IV12(False); oo.IV13(False); oo.IV14(False); oo.IV15(False); oo.IV16(False)
    oo.IV19(False); oo.IV20(False); oo.IV21(False); oo.IV22(False); oo.CV5(False); oo.CV0(False);

#### Beginning of GUI Class 
class DAQGui(tk.Tk):
    def __init__(self, *args, **kwargs):       
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Sensor Data and MFC inputs")
        
    #Initializing GUI Container (Borders)
        container = tk.Frame(self) 
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
               
    #Menubar (File, Edit, etc.. at the top of the container)
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff = 0)        
        Save_Menu = tk.Menu(menubar)
        Save_Menu.add_command(label = "Choose Save Directory", command = lambda: OpenFile())
        Save_Menu.add_command(label = "Save", command = lambda: save())
        
        filemenu.add_cascade(label = "Save Menu", menu = Save_Menu)
        menubar.add_cascade(label = "File", menu = filemenu)
        
        timeunits = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = "Units of Time", menu = timeunits)
        timeunits.add_command(label = "Seconds", command = lambda: timefunction('secs' ))
        timeunits.add_command(label = "Minutes", command = lambda: timefunction('mins' ))
        timeunits.add_command(label = "Hours  ", command = lambda: timefunction('hours'))
        timeunits.add_command(label = "Days   ", command = lambda: timefunction('days' ))
        
    #################################################    
   ############## Recipes for injection ##############
    #################################################
    
    #Recipe Buttons
        recipe_button2 = ttk.Button(self, text = "Bay 1 Inj", command = lambda: Bay1_recipe())
        recipe_button2.place(x = 300, y = 16)
        
        #recipe_button1 = ttk.Button(self, text = "Rn220 Inj", command = lambda: Rn220_recipe())
        recipe_button1 = ttk.Button(self, text = "Bay 2 Inj", command = lambda: Bay2_recipe())
        recipe_button1.place(x = 200, y = 16)
            
    #Recipe status box
        statusstring = tk.StringVar() 
        statusstring.set('Standby')
        status = tk.Label(self, textvariable = statusstring)
        status.place(x = 40, y = 18)
        def statusfunction(text):
            statusstring.set(str(text))         

        def Bay1_recipe():
            import time
            close_all(); mfc2get(0); mfc3get(0);
            self.after(3000, oo.CV5(True)); statusfunction('CV5 Opened'); self.update()
            self.after(250, oo.IV22(True)); statusfunction('IV22 Opened'); self.update()
            self.after(250, oo.IV21(True)); statusfunction('IV21 Opened'); self.update()
            self.after(250, oo.IV16(True)); statusfunction('IV16 Opened'); self.update()
            self.after(250, oo.IV15(True)); statusfunction('IV15 Opened'); self.update()
            self.after(250, oo.IV8(True)); statusfunction('IV8 Opened'); self.update()
            self.after(250, oo.IV1(True)); statusfunction('IV1 Opened'); self.update()
            self.after(250, oo.IV5(True)); statusfunction('IV5 Opened'); self.update()
            self.after(100, mfc2get(dose_rate*mfc2_mult)); statusfunction('MFC2 -> '+str(dose_rate*mfc2_mult)+' SCCM'); self.update()
            time1 = int(time.time())
            while (int(time.time())-time1 < mfc3_del):
                self.after(100, self.update()) # just tells the code to wait X ms
            # Begin Dose
            self.after(100, mfc3get(dose_rate)); statusfunction(str(dose_rate)+' SCCM Bay 1 Dose');  self.update()
            time2 = int(time.time())
            while (int(time.time())-time2 < dose_t):
                self.after(1000, self.update())
            # End Dose
            oo.IV15(False)
            mfc2get(0)
            oo.IV5(False)
            oo.IV8(False)
            mfc3get(0)
            # Begin Flush
            oo.IV6(True)
            mfc2get(flush_rate); statusfunction(str(flush_rate)+' SCCM Flush'); self.update()
            mfcget(float(MFC1input.get())-(flush_rate/2000.0));
            time3 = int(time.time())
            while (int(time.time())-time3 < flush_t):
                self.after(1000, self.update())
            # End Flush
            close_all(); statusfunction('Injection Panel Closed'); self.update()
            mfc2get(0)
            mfcget(float(MFC1input.get()))
            self.after(1000, statusfunction('Bay 1 Inj Complete')); self.update()

        def Bay2_recipe():
            import time
            close_all(); mfc2get(0); mfc3get(0);
            self.after(3000, oo.CV5(True)); statusfunction('CV5 Opened'); self.update()
            self.after(250, oo.IV22(True)); statusfunction('IV22 Opened'); self.update()
            self.after(250, oo.IV21(True)); statusfunction('IV21 Opened'); self.update()
            self.after(250, oo.IV16(True)); statusfunction('IV16 Opened'); self.update()
            self.after(250, oo.IV15(True)); statusfunction('IV15 Opened'); self.update()
            self.after(250, oo.IV9(True)); statusfunction('IV9 Opened'); self.update()
            self.after(250, oo.IV7(True)); statusfunction('IV7 Opened'); self.update()
            self.after(250, oo.IV1(True)); statusfunction('IV1 Opened'); self.update()
            self.after(250, oo.IV4(True)); statusfunction('IV4 Opened'); self.update()
            self.after(100, mfc2get(dose_rate*mfc2_mult)); statusfunction('MFC2 -> '+str(dose_rate*mfc2_mult)+' SCCM'); self.update()
            time1 = int(time.time())
            while (int(time.time())-time1 < mfc3_del):
                self.after(100, self.update())
            # Begin Dose
            # Add time (sec) to account for larger downstream (2cc) volume for Bay 2, where the pressure is ~ 2 bara
            add_time = ((2.0*2.0)/dose_rate)*60.0 
            self.after(100, mfc3get(dose_rate)); statusfunction(str(dose_rate)+' SCCM Bay 2 Dose');  self.update()
            time2 = int(time.time())
            while (int(time.time())-time2 < (dose_t+add_time)):
                self.after(1000, self.update())
            # End Dose
            oo.IV15(False)
            mfc2get(0)
            oo.IV4(False)
            oo.IV9(False)
            oo.IV7(False)
            mfc3get(0)
            # Begin Flush
            oo.IV6(True)
            mfc2get(flush_rate); statusfunction(str(flush_rate)+' SCCM Flush'); self.update()
            mfcget(float(MFC1input.get())-(flush_rate/2000.0)); # 2000 is from dividing by 1000 to change from sccm to slpm, and 2 to get half
            time3 = int(time.time())
            while (int(time.time())-time3 < flush_t):
                self.after(1000, self.update())
            # End Flush
            close_all(); statusfunction('Injection Panel Closed'); self.update()
            mfc2get(0)
            mfcget(float(MFC1input.get()))
            self.after(1000, statusfunction('Bay 2 Inj Complete')); self.update()

        def Rn220_recipe():
            import time
            close_all(); mfc2get(0); mfc3get(0);
            self.after(3000, oo.CV5(True)); statusfunction('CV5 Opened'); self.update()
            self.after(250, oo.IV22(True)); statusfunction('IV22 Opened'); self.update()
            self.after(250, oo.IV21(True)); statusfunction('IV21 Opened'); self.update()
            self.after(250, oo.IV16(True)); statusfunction('IV16 Opened'); self.update()
            self.after(250, oo.IV14(True)); statusfunction('IV14 Opened'); self.update()
            self.after(250, oo.IV13(True)); statusfunction('IV13 Opened'); self.update()
            self.after(250, oo.IV7(True)); statusfunction('IV7 Opened'); self.update()
            self.after(250, oo.IV1(True)); statusfunction('IV1 Opened'); self.update()
            self.after(250, oo.IV4(True)); statusfunction('IV4 Opened'); self.update()
            # Begin Dose
            self.after(100, mfc2get(dose_rate)); statusfunction(str(dose_rate)+' SCCM Rn220 Flow'); self.update()
            mfcget(float(MFC1input.get())-(dose_rate/2000.0));
            time2 = int(time.time())
            while (int(time.time())-time2 < dose_t):
                self.after(1000, self.update())
            # End Dose
            mfc2get(0)
            oo.IV14(False)
            oo.IV4(False)
            oo.IV13(False)
            oo.IV7(False)
            # Begin Flush
            oo.IV6(True)
            mfc2get(flush_rate); statusfunction(str(flush_rate)+' SCCM Rn220 Dose Flush'); self.update()
            mfcget(float(MFC1input.get())-(flush_rate/2000.0));
            time3 = int(time.time())
            while (int(time.time())-time3 < flush_t):
                self.after(1000, self.update())
            # End Flush
            close_all(); statusfunction('Injection Panel Closed'); self.update()
            mfc2get(0)
            mfcget(float(MFC1input.get()))
            self.after(1000, statusfunction('Rn220 Inj Complete')); self.update()

    #############################################
    ##################END RECIPES################
    #############################################
        
    #Creating textboxes and entry windows for MFCs and time window 
        mfcframe = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(mfcframe, text = 'MFC1 [SLPM] (0-5)           ').pack(side = tk.RIGHT, padx = 1)
        MFC1in = tk.StringVar() 
        MFC1input = tk.Entry(mfcframe, textvariable = MFC1in)
        MFC1input.pack(side = tk.RIGHT, padx = 1)
        mfcframe.place(x = 40, y = 46)

        mfcframe2 = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(mfcframe2, text = 'MFC2 [SCCM] (0-250)      ').pack(side = tk.RIGHT, padx = 1)
        MFC2in = tk.StringVar() 
        MFC2input = tk.Entry(mfcframe2, textvariable = MFC2in)
        MFC2input.pack(side = tk.RIGHT, padx = 1)
        mfcframe2.place(x = 40, y = 76)        
        
        mfcframe3 = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(mfcframe3, text = 'MFC3 [SCCM] (0-50)        ').pack(side = tk.RIGHT, padx = 1)
        MFC3in = tk.StringVar() 
        MFC3input = tk.Entry(mfcframe3, textvariable = MFC3in)
        MFC3input.pack(side = tk.RIGHT, padx = 1)
        mfcframe3.place(x = 40, y = 106)
        
        PT1_upper_frame = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(PT1_upper_frame, text = 'PT1 Upper Alarm (bara)   ').pack(side = tk.RIGHT, padx = 1)
        PT1_upper_value = tk.StringVar() 
        PT1_upper = tk.Entry(PT1_upper_frame, textvariable = PT1_upper_value)
        PT1_upper.pack(side = tk.RIGHT, padx = 1)
        PT1_upper_frame.place(x = 40, y = 136)
        
        PT1_lower_frame = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(PT1_lower_frame, text = 'PT1 Lower Alarm (bara)   ').pack(side = tk.RIGHT, padx = 1)
        PT1_lower_value = tk.StringVar() 
        PT1_lower = tk.Entry(PT1_lower_frame, textvariable = PT1_lower_value)
        PT1_lower.pack(side = tk.RIGHT, padx = 1)
        PT1_lower_frame.place(x = 40, y = 166)
        
        time_window_frame = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(time_window_frame, text = 'Data time-window            ').pack(side = tk.RIGHT, padx = 1)
        time_window_value = tk.StringVar() 
        time_window = tk.Entry(time_window_frame, textvariable = time_window_value)
        time_window.pack(side = tk.RIGHT, padx = 1)
        time_window_frame.place(x = 40, y = 196)
        
        buffer_frame = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(buffer_frame, text = 'Leading time                     ').pack(side = tk.RIGHT, padx = 1)
        buffer_value = tk.StringVar() 
        buffer = tk.Entry(buffer_frame, textvariable = buffer_value)
        buffer.pack(side = tk.RIGHT, padx = 1)
        buffer_frame.place(x = 40, y = 226)
        
        mfc3_delay_frame = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(mfc3_delay_frame, text = 'MFC3 Dose Delay (sec)   ').pack(side = tk.RIGHT, padx = 1)
        mfc3_delay_value = tk.StringVar() 
        mfc3_delay = tk.Entry(mfc3_delay_frame, textvariable = mfc3_delay_value)
        mfc3_delay.pack(side = tk.RIGHT, padx = 1)
        mfc3_delay_frame.place(x = 580, y = 166)
        
        dose_flow_rate_frame = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(dose_flow_rate_frame, text = 'Dose Flow Rate (SCCM) ').pack(side = tk.RIGHT, padx = 1)
        dose_flow_rate_value = tk.StringVar() 
        dose_flow_rate = tk.Entry(dose_flow_rate_frame, textvariable = dose_flow_rate_value)
        dose_flow_rate.pack(side = tk.RIGHT, padx = 1)
        dose_flow_rate_frame.place(x = 580, y = 196)
        
        dose_flow_time_frame = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(dose_flow_time_frame, text = 'Dose Flow Time (sec)     ').pack(side = tk.RIGHT, padx = 1)
        dose_flow_time_value = tk.StringVar() 
        dose_flow_time = tk.Entry(dose_flow_time_frame, textvariable = dose_flow_time_value)
        dose_flow_time.pack(side = tk.RIGHT, padx = 1)
        dose_flow_time_frame.place(x = 580, y = 226)
        
        mfc2_multiplier_frame = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(mfc2_multiplier_frame, text = 'MFC2 Dose Multiplier    ').pack(side = tk.RIGHT, padx = 1)
        mfc2_multiplier_value = tk.StringVar() 
        mfc2_multiplier = tk.Entry(mfc2_multiplier_frame, textvariable = mfc2_multiplier_value)
        mfc2_multiplier.pack(side = tk.RIGHT, padx = 1)
        mfc2_multiplier_frame.place(x = 925, y = 166)
        
        flush_flow_rate_frame = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(flush_flow_rate_frame, text = 'Flush Flow Rate (SCCM)').pack(side = tk.RIGHT, padx = 1)
        flush_flow_rate_value = tk.StringVar() 
        flush_flow_rate = tk.Entry(flush_flow_rate_frame, textvariable = flush_flow_rate_value)
        flush_flow_rate.pack(side = tk.RIGHT, padx = 1)
        flush_flow_rate_frame.place(x = 925, y = 196)
        
        flush_flow_time_frame = tk.Frame(self, bd = 2, relief = tk.RIDGE)
        tk.Label(flush_flow_time_frame, text = 'Flush Flow Time (sec)    ').pack(side = tk.RIGHT, padx = 1)
        flush_flow_time_value = tk.StringVar() 
        flush_flow_time = tk.Entry(flush_flow_time_frame, textvariable = flush_flow_time_value)
        flush_flow_time.pack(side = tk.RIGHT, padx = 1)
        flush_flow_time_frame.place(x = 925, y = 226)
        
    #Making the enter buttons for the MFCs and timewindow and alarm thresholds
        mfc1_enter = ttk.Button(self, text = "Enter", command = lambda: mfcget(float(MFC1input.get())))
        mfc1_enter.place(x = 300, y = 46)
       
        mfc2_enter = ttk.Button(self, text = "Enter", command = lambda: mfc2get(float(MFC2input.get())))
        mfc2_enter.place(x = 300, y = 76)
        
        mfc3_enter = ttk.Button(self, text = "Enter", command = lambda: mfc3get(float(MFC3input.get())))
        mfc3_enter.place(x = 300, y = 106)
        
        PT1_upper_enter = ttk.Button(self, text = "Enter", command = lambda: PT1_upper_alarm_get(float(PT1_upper.get())))
        PT1_upper_enter.place(x = 300, y = 136)
        
        PT1_lower_enter = ttk.Button(self, text = "Enter", command = lambda: PT1_lower_alarm_get(float(PT1_lower.get())))
        PT1_lower_enter.place(x = 300, y = 166)

        time_enter = ttk.Button(self, text = "Enter", command = lambda: t_window_get(float(time_window.get())))
        time_enter.place(x = 300, y = 196)
        
        buffer_enter = ttk.Button(self, text = "Enter", command = lambda: buffer_get(float(buffer.get())))
        buffer_enter.place(x = 300, y = 226)

        mfc3_delay_enter = ttk.Button(self, text = "Enter", command = lambda: mfc3_delay_get(float(mfc3_delay.get())))
        mfc3_delay_enter.place(x = 840, y = 166)
        
        dose_flow_rate_enter = ttk.Button(self, text = "Enter", command = lambda: dose_flow_rate_get(float(dose_flow_rate.get())))
        dose_flow_rate_enter.place(x = 840, y = 196)
        
        dose_flow_time_enter = ttk.Button(self, text = "Enter", command = lambda: dose_flow_time_get(float(dose_flow_time.get())))
        dose_flow_time_enter.place(x = 840, y = 226)
        
        mfc2_multiplier_enter = ttk.Button(self, text = "Enter", command = lambda: mfc2_multiplier_get(float(mfc2_multiplier.get())))
        mfc2_multiplier_enter.place(x = 1185, y = 166)
        
        flush_flow_rate_enter = ttk.Button(self, text = "Enter", command = lambda: flush_flow_rate_get(float(flush_flow_rate.get())))
        flush_flow_rate_enter.place(x = 1185, y = 196)
        
        flush_flow_time_enter = ttk.Button(self, text = "Enter", command = lambda: flush_flow_time_get(float(flush_flow_time.get())))
        flush_flow_time_enter.place(x = 1185, y = 226)
        
    #Current Time Unit box
        timestring = tk.StringVar() 
        timestring.set('Time Units = hours')
        time = tk.Label(self, textvariable = timestring)
        time.place(x = 430, y = 219)
        def timefunction(text):
            global time_
            time_ = str(text)
            timestring.set('Time Units = '+str(text))
            self.update()
        
    #Get the input from the textbox and calling setpoint to set the setpoint 
        def mfcget(mfcin): 
            global setpointconstant1
            setpointconstant1 = mfcin
            volttemp = float(mfcin) 
            volt = (volttemp - b1)/(m1)
            if volt > 5:
                popupmsg("This device only allows up to 5 slpm")
            else: 
                setMFC1(volt)
           
        def mfc2get(mfcin):
            global setpointconstant2
            setpointconstant2 = mfcin
            volttemp = float(mfcin/50.0)
            volt = (volttemp - b2)/(m2)
            if volt > 5:
                popupmsg("This device only allows up to 250 sccm")
            else:
                setMFC2(volt)
            
        def mfc3get(mfcin):
            global setpointconstant3
            setpointconstant3 = mfcin
            volttemp = float(mfcin/10.0)
            volt = (volttemp - b3)/(m3)
            if volt > 5:
                popupmsg("This device only allows up to 50 sccm")
            else:
                setMFC3(volt)
                
    # Get the input from the data window cells to set the display parameters
        def t_window_get(window):
            global t_window
            t_window = float(window)
        
        def buffer_get(buffer):
            global leading_buffer
            leading_buffer = float(buffer)
            
    # Get the input from the alarm input cells to set the alarm thresholds
        def PT1_upper_alarm_get(PT1_up):
            global PT1_alarm_threshold
            global PT1_counter
            PT1_alarm_threshold = float(PT1_up)
            PT1_counter = 0
            
        def PT1_lower_alarm_get(PT1_low):
            global PT1_alarm_lower
            global PT1_counter
            PT1_alarm_lower = float(PT1_low)
            PT1_counter = 0
            
    # Recipe Parameter Button Functions
        def mfc3_delay_get(mfc3_delay_value):
            global mfc3_del
            mfc3_del = float(mfc3_delay_value)
            
        def dose_flow_rate_get(dose_flow_rate_value):
            global dose_rate
            dose_rate = float(dose_flow_rate_value)
            
        def dose_flow_time_get(dose_flow_time_value):
            global dose_t
            dose_t = float(dose_flow_time_value)
            
        def mfc2_multiplier_get(mfc2_multiplier_value):
            global mfc2_mult
            mfc2_mult = float(mfc2_multiplier_value)
            
        def flush_flow_rate_get(flush_flow_rate_value):
            global flush_rate
            flush_rate = float(flush_flow_rate_value)
            
        def flush_flow_time_get(flush_flow_time_value):
            global flush_t
            flush_t = float(flush_flow_time_value)
            
    #Making digital readout
        global PT1str;   global PT2str;  global PT3str;   global PT4str
        global LVL0str;  global LVL1str; global TEMP0str; #global TEMP1str;
        global MFC1str;  global MFC2str; global MFC3str;
        global CM1str;   global CM2str;
        
        PT1str  = tk.StringVar(); PT2str  = tk.StringVar(); PT3str   = tk.StringVar(); PT4str    = tk.StringVar()
        LVL0str = tk.StringVar(); LVL1str = tk.StringVar(); TEMP0str = tk.StringVar(); #TEMP1str  = tk.StringVar()
        MFC1str = tk.StringVar(); MFC2str = tk.StringVar(); MFC3str = tk.StringVar();
        CM1str = tk.StringVar();  CM2str = tk.StringVar();
        
        #Column 1
        tk.Label(text = 'Detector Pressure (PT1)').place(x = x1, y = 16)
        tk.Entry(textvariable = PT1str, state = tk.DISABLED).place(x = x1, y = 38)
        tk.Label(text = 'Emergency Recovery Pressure (PT2)').place(x = x1, y = 60)
        tk.Entry(textvariable = PT2str, state = tk.DISABLED).place(x = x1, y = 83)
        tk.Label(text = 'Injection Panel Outlet Pressure (PT3)').place(x = x1, y = 105)
        tk.Entry(textvariable = PT3str, state = tk.DISABLED).place(x = x1, y = 128)
        tk.Label(text = 'LACO Vessel Pressure (PT4)').place(x = x1, y = 147)
        tk.Entry(textvariable = PT4str, state = tk.DISABLED).place(x = x1, y = 170)
        
        #Column 2
        tk.Label(text = 'Inlet Level Sensor (LVL0)').place(x = x2, y = 16)
        tk.Entry(textvariable = LVL0str, state = tk.DISABLED).place(x = x2, y = 38)
        tk.Label(text = 'Weir Level Sensor (LVL1)').place(x = x2, y = 60)
        tk.Entry(textvariable = LVL1str, state = tk.DISABLED).place(x = x2, y = 83)
        tk.Label(text = 'Bottom of Dewar Temp (TEMP0)').place(x = x2, y = 105)
        tk.Entry(textvariable = TEMP0str, state = tk.DISABLED).place(x = x2, y = 128)
        #tk.Label(text = 'Temp 1 (TEMP1)').place(x = x2, y = 157)
        #tk.Entry(textvariable = TEMP1str, state = tk.DISABLED).place(x = x2, y = 170)
                
        #Column 3
        tk.Label(text = 'Circulation Flow (MFC1)').place(x = x3, y = 16)
        tk.Entry(textvariable = MFC1str, state = tk.DISABLED).place(x = x3, y = 38)
        tk.Label(text = 'Injection Panel Flow (MFC2)').place(x = x3, y = 60)
        tk.Entry(textvariable = MFC2str, state = tk.DISABLED).place(x = x3, y = 83)
        tk.Label(text = 'Dose Flow (MFC3)').place(x = x3, y = 105)
        tk.Entry(textvariable = MFC3str, state = tk.DISABLED).place(x = x3, y = 128)
        
        #Column 4
        tk.Label(text = 'Dose Volume Manometer (CM1)').place(x = x4, y = 16)
        tk.Entry(textvariable = CM1str, state = tk.DISABLED).place(x = x4, y = 38)
        tk.Label(text = 'Bottle Region Manometer (CM2)').place(x = x4, y = 60)
        tk.Entry(textvariable = CM2str, state = tk.DISABLED).place(x = x4, y = 83)
        
        tk.Tk.config(self, menu = menubar)       
                                
        #specifying dictionary to call different pages
        self.frames = {}        
        
        for F in (StartPage, PageOne):            
            frame = F(container, self)            
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew") 
            
        frame = StartPage(container, self)
        self.frames[StartPage] = frame 
        frame.grid(row = 0, column = 0, sticky = "nsew")
        self.show_frame(StartPage)
        
        #Graphs 
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill = tk.BOTH, expand = 1)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(fill = tk.BOTH, expand = 1)
        self.ani = anime.FuncAnimation(fig, self.animate, interval = sample_interval, blit = False)

    def show_frame(self, controller): #Allows me to call different pages 
        frame = self.frames[controller]
        frame.tkraise()
            
    def animate(self,i):
        extend_setpoint1(setpointconstant1)
        extend_setpoint2(setpointconstant2)
        extend_setpoint3(setpointconstant3)
        if len(t_sec) > 1: 
            #Calling functions to set the digital display
            PT1str.set(round(float(PT1_corrected[-1]),3))
            PT2str.set(round(float(PT2_corrected[-1]),3))
            PT3str.set(round(float(PT3_corrected[-1]),3))
            PT4str.set(round(float(PT4_corrected[-1]),3))
            MFC1str.set(round(float(MFC1[-1]),3))
            MFC2str.set(round(float(MFC2[-1]),3))
            MFC3str.set(round(float(MFC3[-1]),3))
            CM1str.set(round(float(CM1[-1]),3))
            CM2str.set(round(float(CM2[-1]),3))
            LVL0str.set(round(float(LVL0[-1]),3))
            LVL1str.set(round(float(LVL1[-1]),3))
            TEMP0str.set(round(float(TEMP0[-1]),3))
            #TEMP1str.set(round(float(TEMP1[-1]),3))
               
            # Set Saving Frequncy in Minutes
            if(t_min[-1]%15 < 0.05 ): 
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_PT1", PT1)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_PT2", PT2)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_PT3", PT3)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_PT4", PT4)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_CM1", CM1)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_CM2", CM2)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_MFC1", MFC1)                
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_MFC2", MFC2)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_MFC3", MFC3)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_setpoint1", setpoint1)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_setpoint2", setpoint2)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_setpoint3", setpoint3)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_LVL0", LVL0)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_LVL1", LVL1)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_time_sec", t_sec)
                np.save("C:/Users/Hertel/Desktop/LXe_System_Data/"+str(t0str)+"_time_min", t_min)
                print('saved')

        extend_time()
        
        #Functionality to change units of time 
        if time_ == 'secs':
            ax_PT1.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);    line_PT1.set_data(t_sec, PT1_corrected)
            ax_PT2.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);    line_PT2.set_data(t_sec, PT2_corrected)
            ax_PT3.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);    line_PT3.set_data(t_sec, PT3_corrected)
            ax_PT4.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);    line_PT4.set_data(t_sec, PT4_corrected)
            ax_CM1.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);    line_CM1.set_data(t_sec, CM1)
            ax_CM2.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);    line_CM2.set_data(t_sec, CM2)
            ax_MFC1.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);   line_MFC1.set_data(t_sec, MFC1)
            ax_MFC2.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);   line_MFC2.set_data(t_sec, MFC2)
            ax_MFC3.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);   line_MFC3.set_data(t_sec, MFC3)
            ax_LVL0.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);   line_LVL0.set_data(t_sec, LVL0)
            ax_LVL1.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);   line_LVL1.set_data(t_sec, LVL1)
            ax_TEMP0.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer);  line_TEMP0.set_data(t_sec, TEMP0)
            #ax_TEMP1.set_xlim(t_sec[-1]-t_window, t_sec[-1] + leading_buffer); line_TEMP1.set_data(t_sec, TEMP1)
            line_MFC1_sp.set_data(t_sec, setpoint1)
            line_MFC2_sp.set_data(t_sec, setpoint2)
            line_MFC3_sp.set_data(t_sec, setpoint3)
        
        if time_ == 'mins': 
            ax_PT1.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);    line_PT1.set_data(t_min, PT1_corrected)
            ax_PT2.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);    line_PT2.set_data(t_min, PT2_corrected)
            ax_PT3.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);    line_PT3.set_data(t_min, PT3_corrected)
            ax_PT4.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);    line_PT4.set_data(t_min, PT4_corrected)
            ax_CM1.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);    line_CM1.set_data(t_min, CM1)
            ax_CM2.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);    line_CM2.set_data(t_min, CM2)
            ax_MFC1.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);   line_MFC1.set_data(t_min, MFC1)
            ax_MFC2.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);   line_MFC2.set_data(t_min, MFC2)
            ax_MFC3.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);   line_MFC3.set_data(t_min, MFC3)
            ax_LVL0.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);   line_LVL0.set_data(t_min, LVL0)
            ax_LVL1.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);   line_LVL1.set_data(t_min, LVL1)
            ax_TEMP0.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);  line_TEMP0.set_data(t_min, TEMP0)
            #ax_TEMP1.set_xlim(t_min[-1]-t_window, t_min[-1] + leading_buffer);  line_TEMP1.set_data(t_min, TEMP1)
            line_MFC1_sp.set_data(t_min, setpoint1)
            line_MFC2_sp.set_data(t_min, setpoint2)
            line_MFC3_sp.set_data(t_min, setpoint3)
            
        if time_ == 'hours':
            ax_PT1.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);    line_PT1.set_data(t_hour, PT1_corrected)
            ax_PT2.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);    line_PT2.set_data(t_hour, PT2_corrected)
            ax_PT3.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);    line_PT3.set_data(t_hour, PT3_corrected)
            ax_PT4.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);    line_PT4.set_data(t_hour, PT4_corrected)
            ax_CM1.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);    line_CM1.set_data(t_hour, CM1)
            ax_CM2.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);    line_CM2.set_data(t_hour, CM2)
            ax_MFC1.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);   line_MFC1.set_data(t_hour, MFC1)
            ax_MFC2.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);   line_MFC2.set_data(t_hour, MFC2)
            ax_MFC3.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);   line_MFC3.set_data(t_hour, MFC3)
            ax_LVL0.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);   line_LVL0.set_data(t_hour, LVL0)
            ax_LVL1.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);   line_LVL1.set_data(t_hour, LVL1)
            ax_TEMP0.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer);  line_TEMP0.set_data(t_hour, TEMP0)
            #ax_TEMP1.set_xlim(t_hour[-1]-t_window, t_hour[-1] + leading_buffer); line_TEMP1.set_data(t_hour, TEMP1)
            line_MFC1_sp.set_data(t_hour, setpoint1)
            line_MFC2_sp.set_data(t_hour, setpoint2)
            line_MFC3_sp.set_data(t_hour, setpoint3)
            
        if time_ == 'days': 
            ax_PT1.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);    line_PT1.set_data(t_day, PT1_corrected)
            ax_PT2.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);    line_PT2.set_data(t_day, PT2_corrected)
            ax_PT3.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);    line_PT3.set_data(t_day, PT3_corrected)
            ax_PT4.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);    line_PT4.set_data(t_day, PT4_corrected)
            ax_CM1.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);    line_CM1.set_data(t_day, CM1)
            ax_CM2.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);    line_CM2.set_data(t_day, CM2)
            ax_MFC1.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);   line_MFC1.set_data(t_day, MFC1)
            ax_MFC2.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);   line_MFC2.set_data(t_day, MFC2)
            ax_MFC3.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);   line_MFC3.set_data(t_day, MFC3)
            ax_LVL0.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);   line_LVL0.set_data(t_day, LVL0)
            ax_LVL1.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);   line_LVL1.set_data(t_day, LVL1)
            ax_TEMP0.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer);  line_TEMP0.set_data(t_day, TEMP0)
            #ax_TEMP1.set_xlim(t_day[-1]-t_window, t_day[-1] + leading_buffer); line_TEMP1.set_data(t_day, TEMP1)
            line_MFC1_sp.set_data(t_day, setpoint1)
            line_MFC2_sp.set_data(t_day, setpoint2)
            line_MFC3_sp.set_data(t_day, setpoint3)

        #Calling functions to read data and append to array 
        read_PT1(); read_PT2(); read_PT3(); read_PT4()
        read_CM1(); read_CM2(); read_MFC1(); read_MFC2(); read_MFC3()
        
        ############
        read_LVL0(); read_LVL1(); read_TEMP0(); 
        #read_TEMP1()

#Start page for the gui, will be added to the dictionary and called by the initial class.
class StartPage(tk.Frame):
    def __init__(self, parent, controller):     
        tk.Frame.__init__(self, parent)
        
#### Was going to make a second page for the MFC's, realized it wasn't necessary 
class PageOne(tk.Frame): 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = "Mass Flow Controls (WIP)", font = LARGE_FONT)
        label.pack(pady = 10, padx = 10)
        
fig.subplots_adjust(left=0.06, bottom=0.05, right=0.97, top=0.95, wspace = 0.33, hspace = 0.41)
plt.show()
app = DAQGui()
app.geometry("1280x720")
app.mainloop()