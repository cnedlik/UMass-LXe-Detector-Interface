# Co-developed by Chris Nedlik and Anthony Raykh

#Takes a function from on_off to toggle a switch, if it's true, the function
#evaluates to true and vice versa. booleanvar is an input from an
#anonymous function on the button itself so that every button doesn't
#get pressed at the same time 

import on_off as oo
import tkinter
from tkinter import ttk 
import atexit 
import pickle

#initializing the GUI 
window = tkinter.Tk()
window.title("Pneumatic Stuff")
window.geometry("1000x1000")

LARGE_FONT  = ("Verdana", 12)
MEDIUM_FONT = ("Verdana", 8 )
SMALL_FONT  = ("Verdana", 5 )

#List of port names later to be used for the buttons 
port  = ['IV1', 'IV2','IV3', 'IV4','IV5', 'IV6','IV7', 'IV8'         ]
port2 = ['IV9', 'IV10','IV11', 'IV12','IV13', 'IV14','IV15', 'IV16'  ]
port3 = ['IV19', 'IV20','IV21', 'IV22','CV5', 'CV0', 'OPEN1', 'OPEN2']

file = open("Dependencies/GUI/state.pkl", 'rb')
state = pickle.load(file)
file.close()
    
def toggle(function,booleanvar,i):
    chk_state = booleanvar
    val = chk_state.get()
    if val:
        function(True)
        state[str(port[i-1])] = True
        with open("Dependencies/GUI/state.pkl", 'wb') as file:
            pickle.dump(state,file)
            file.close() 
    else:
        function(False)
        state[str(port[i-1])] = False
        with open("Dependencies/GUI/state.pkl", 'wb') as file:
            pickle.dump(state,file)
            file.close()
            
def toggle1(function,booleanvar,i):
    chk_state = booleanvar
    val = chk_state.get()
    if val:
        function(True)
        state[str(port2[i-1])] = True
        with open("Dependencies/GUI/state.pkl", 'wb') as file:
            pickle.dump(state,file)
            file.close()
    else:
        function(False)
        state[str(port2[i-1])] = False
        with open("Dependencies/GUI/state.pkl", 'wb') as file:
            pickle.dump(state,file)
            file.close()
        
        
def toggle2(function,booleanvar,i):
    chk_state = booleanvar
    val = chk_state.get()
    if val:
        function(True)
        state[str(port3[i-1])] = True
        with open("Dependencies/GUI/state.pkl", 'wb') as file:
            pickle.dump(state,file)
            file.close()
    else:
        function(False)
        state[str(port3[i-1])] = False
        with open("Dependencies/GUI/state.pkl", 'wb') as file:
            pickle.dump(state,file)
            file.close()
    
window.title("Port 0 (First 8)")


#importing the P&ID background
C = tkinter.Canvas(bg="blue", height=250, width=300)
filename = tkinter.PhotoImage(file = "C:\\Users\Hertel\.spyder-py3\Pneumatics\Capture.png")
background_label = tkinter.Label(image=filename)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
#C.pack()


#Takes an input function from on_off.py and uses it to create a button, then passes
#an anonymous function to toggle
def buttons(function, x, y, i):
    chk_state = tkinter.BooleanVar()
    try:
        chk_state.set(state[str(port[i-1])])
    except: 
        state[str(port[i-1])] = False

    chk = ttk.Checkbutton(window, text = str(port[i-1]), var = chk_state, command = lambda: toggle(function,chk_state, i))
    chk.place(x = x, y = y)


#Port A, creating buttons at desired locations (corresponding to the P&ID)
IV1 = buttons(oo.IV1,385,750,1)
IV2 = buttons(oo.IV2,430,715,2)
IV3 = buttons(oo.IV3,670,750,3)
IV4 = buttons(oo.IV4,580,660,4)
IV5 = buttons(oo.IV5,660,660,5)
IV6 = buttons(oo.IV6,710,655,6)
IV7 = buttons(oo.IV7,580,380,7)
IV8 = buttons(oo.IV8,650,380,8)

def buttons2(function, x, y, i):
    chk_state = tkinter.BooleanVar()
    try:
        chk_state.set(state[str(port2[i-1])])
    except: 
        state[str(port2[i-1])] = False
    chk = ttk.Checkbutton(window, text = str(port2[i-1]), var = chk_state, command = lambda: toggle1(function,chk_state, i))
    chk.place(x = x, y = y)


#Port B
IV9  = buttons2(oo.IV9,610,355,1)
IV10 = buttons2(oo.IV10,530,355,2)
IV11 = buttons2(oo.IV11,470,355,3)
IV12 = buttons2(oo.IV12,400,355,4)
IV13 = buttons2(oo.IV13,580,330,5)
IV14 = buttons2(oo.IV14,580,275,6)
IV15 = buttons2(oo.IV15,635,275,7)
IV16 = buttons2(oo.IV16,610,250,8)

def buttons3(function, x, y, i):
    chk_state = tkinter.BooleanVar()
    try:
        chk_state.set(state[str(port3[i-1])])

    except: 
        state[str(port3[i-1])] = False
    chk = ttk.Checkbutton(window, text = str(port3[i-1]), var = chk_state, command = lambda: toggle2(function,chk_state, i))
    chk.place(x = x, y = y)

#Port C    
IV19  = buttons3(oo.IV19,300,330,1 )
IV20  = buttons3(oo.IV20,300,270,2 )
IV21  = buttons3(oo.IV21,225,290,3 )
IV22  = buttons3(oo.IV22,225,405,4 )
CV5   = buttons3(oo.CV5 ,90 ,565,5 )
CV0   = buttons3(oo.CV0 ,90 ,510,6 )


def masterbuttonstate():
    oo.IV1(False)
    oo.IV2(False)
    oo.IV3(False)
    oo.IV4(False)
    oo.IV5(False)
    oo.IV6(False)
    oo.IV7(False)
    oo.IV8(False)
    oo.IV9(False)
    oo.IV10(False)
    oo.IV11(False)
    oo.IV12(False)
    oo.IV13(False)
    oo.IV14(False)
    oo.IV15(False)
    oo.IV16(False)
    oo.IV19(False)
    oo.IV20(False)
    oo.IV21(False)
    oo.IV22(False)
    oo.CV5(False)
    oo.CV0(False)
    oo.a6(False)
    oo.a7(False)
   
def masterbutton(x, y):
    button = ttk.Button(window, text = "Close All", command = lambda: masterbuttonstate())
    button.place(x = x, y = y)
    
masterbutton(100,100)


legend_text = """
-------------------
|     Checked = Open   |
|   Unchecked = Closed |
-------------------"""
w = tkinter.Label(window,text = str(legend_text))
w.place(x = 800, y = 150)

window.mainloop()

atexit.register(masterbuttonstate())