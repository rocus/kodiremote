from wifi3 import connected_to_wlan, disconnect_from_wlan, connect_to_wlan, which_wlan, which_ssid
from sys   import print_exception
from time  import sleep
from json  import load
from machine import Pin
from analogbutton import AnalogButtonPico
from urequests import post

def blink_led:
    tm = 0.3
    statusled.toggle()
    sleep(tm)
    statusled.toggle()
    sleep(tm)

def run(action):
    reader = AnalogButtonPico(buttonpin)   
    while True:
        btn_state, btn_name, raw_val, voltage = reader.get_button()
        if btn_state != "NO_PRESS":
           action (btn_name)
        sleep(0.2)
 
def send_kodi_command(method, params=None):
    url = f"http://{kodi_ip}:{kodi_port}/jsonrpc"
    headers = {"Content-Type": "application/json"}
    data = {"jsonrpc": "2.0", "id": 1,"method": method }
    if params:
        data["params"] = params
    try:
        r = post(url, headers=headers, json=data)
        print("Sent:", method, data)
        r.close()
    except Exception as e:
        print("Error sending command:", e)
 
def action (name):
    b= a[name]
    send_kodi_command ( b['method'], b['params'])
         
try:
    f = open('secrets.json')
    secrets = load(f)

    d = secrets['devices']
    statusled = Pin(d['ledpin'], Pin.OUT, value=d['ledvalue'])
    kodi_ip   = d['kodi_ip']
    kodi_port = d['kodi_port']
    buttonpin = d['buttonpin']
    blink_led(1)
    a = secrets['actions']
    blink_led(1)
    w = secrets['wifi']
    connect_to_wlan(w)
    blink_led(1)
    run(action)
    
except Exception as err:
    print_exception(err)
    disconnect_from_wlan()
