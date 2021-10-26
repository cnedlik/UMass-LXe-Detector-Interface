# UMass-LXe-Detector-Interface
Code for reading out and interacting with the various sensors and instruments on the UMass liquid xenon (LXe) detector hardware.

"Valve_Interface.py" creates a graphical user interface (GUI) for opening and closing the valves on the UMass LXe detector, referencing functions contained in "on_off.py".

"DAQ.py" is the GUI for reading out the array of sensors on the UMass LXe detector in live plots, and also for executing automated calibration source injection procedures, also referencing functions contained in "on_off.py". The sensors interface with the computer using National Instruments and LabJack DAQ hardware.
