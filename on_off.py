# Co-developed by Chris Nedlik and Anthony Raykh

# Defining functions for buttons      

import nidaqmx

def IV19(x):
    with nidaqmx.Task() as task: #Naming the task
        task.do_channels.add_do_chan("""
                                     Dev1/Port0/Line0""") #Naming the device/port/line numbers 
        task.write(x, auto_start = True)  #the x is on or off (True/False) 
        task.start()  #Start the on/off command 
    
def IV20(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port0/Line1""")
        task.write(x, auto_start = True)
        task.start()
        
def IV21(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port0/Line2""")
        task.write(x, auto_start = True)
        task.start()
        
def IV22(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port0/Line3""")
        task.write(x, auto_start = True)
        task.start()
        
def CV5(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port0/Line4""")
        task.write(x, auto_start = True)
        task.start()
        
def CV0(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port0/Line5""")
        task.write(x, auto_start = True)
        task.start()
        
def a6(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port0/Line6""")
        task.write(x, auto_start = True)
        task.start()
        
def a7(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port0/Line7""")
        task.write(x, auto_start = True)
        task.start()
def IV15(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port1/Line0""")
        task.write(x, auto_start = True)
        task.start()
    
def IV14(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port1/Line1""")
        task.write(x, auto_start = True)
        task.start()
        
def IV13(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port1/Line2""")
        task.write(x, auto_start = True)
        task.start()
        
def IV16(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port1/Line3""")
        task.write(x, auto_start = True)
        task.start()
        
def IV5(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port1/Line4""")
        task.write(x, auto_start = True)
        task.start()
        
def IV6(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port1/Line5""")
        task.write(x, auto_start = True)
        task.start()
        
def IV7(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port1/Line6""")
        task.write(x, auto_start = True)
        task.start()
        
def IV8(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port1/Line7""")
        task.write(x, auto_start = True)
        task.start()
def IV9(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port2/Line0""")
        task.write(x, auto_start = True)
        task.start()
    
def IV10(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port2/Line1""")
        task.write(x, auto_start = True)
        task.start()
        
def IV11(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port2/Line2""")
        task.write(x, auto_start = True)
        task.start()
        
def IV12(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port2/Line3""")
        task.write(x, auto_start = True)
        task.start()
        
def IV1(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port2/Line4""")
        task.write(x, auto_start = True)
        task.start()
        
def IV2(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port2/Line5""")
        task.write(x, auto_start = True)
        task.start()
        
def IV3(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port2/Line6""")
        task.write(x, auto_start = True)
        task.start()
        
def IV4(x):
    with nidaqmx.Task() as task: 
        task.do_channels.add_do_chan("""
                                     Dev1/Port2/Line7""")
        task.write(x, auto_start = True)
        task.start()