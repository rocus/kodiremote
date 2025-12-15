**GENERAL**

As a longtime user of Kodi (a video streamer on cheap hardware i.e. a raspberry pi) and yatse (a Kodi remote control app on Android) I miss a device (with limited remote control functions) with real buttons instead of a touchscreen buttons. 

This (small) project shows how to make and design a small handheld device that let you use the most used functions of a kodi remote control with real buttons.

It consists of:
 - a raspberry pico W
 - a 5 button board
 - a rechargable battery
 - a battery charger unit
 - a small casing

The 5 button board is advertised as an analog button board what means that internally a voltage divider is used to supply a variable voltage as output. That means that this output must be connected to an analog input pin of the pico. I found a python module that let you test an analog button board and gives you voltage value ranges that the different buttons give. You must add these value's into the module to identify the buttons correctly.

In my main module I use the class defined in the analogbutton module and perform the different actions. The actions are defined in a json file (secrets.json). The appropriate actions are send to the Kodi http port as activated and defined in the kodi setup section. (see system.settings.services.control). You must define in the json file also (mutiple) wifi settings, Kodi's ipaddress and port, the pico's led and the analog input pin.  

I use the buttons for:
 - pause/play toggle
 - go some seconds back
 - go some seconds forward
 - increment the volume
 - decrement the volume

But you are ofcourse free to use buttons for other purposes.

The rest explains itself.