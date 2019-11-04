# SmartBath.py
# Software per rendere smarth lo scaldabagno elettrico, con l'uso di Blynk e la libreria
# https://github.com/vshymanskyy/blynk-library-python
# La libreria è salvata in /lib/BlynkLib.py 

import BlynkLib
import network
import machine
import utime

#variabiles
WIFI_SSID = 'myssd'
WIFI_PASS = 'mypassword'
BLYNK_AUTH = 'mytoken'
#il modulo a 4 rele' viene comandato in NPN quindi con pin a livello basso si accendono i rele
v_on = 0
v_off = 1

# pins declaration
ventola = machine.Pin(0, machine.Pin.OUT) #V0 - D3
w1000 = machine.Pin(5, machine.Pin.OUT) #V1 - D1
w2000 = machine.Pin(4, machine.Pin.OUT) #V2 - D2

start_button = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP) #D5

w1000.value(v_off)
w2000.value(v_off)
ventola.value(v_off)

tempo = machine.Timer(-1)

status = 0 # dichiaro delle variabili per tenere traccia dello stato dei pin

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
    
def connessione(WIFI_SSID, WIFI_PASS):
    print("Connecting to WiFi...")
    wifi.connect(WIFI_SSID, WIFI_PASS)
    while not wifi.isconnected():
        pass
    print('IP:', wifi.ifconfig()[0])
    
#Connessione alla rete WIFI
connessione(WIFI_SSID, WIFI_PASS)

# Initialize Blynk
print("Connecting to Blynk...")
blynk = BlynkLib.Blynk(BLYNK_AUTH)

def fan_off(t):
    ventola.value(v_off)
    blynk.virtual_write(0, 0) # V0 = 0

def all_off():
    print("All off")
    global status
    status = 0
    w1000.value(v_off)
    w2000.value(v_off)
    tempo.init(period=30000, mode=machine.Timer.ONE_SHOT, callback=fan_off) # one shot firing after 30s

def all_on():
    tempo.deinit()
    print("All on")
    global status
    status = 1
    ventola.value(v_on)
    w1000.value(v_on)
    w2000.value(v_on)
    blynk.virtual_write(0, 1) # V0 = 1

# turn off all pin
all_off()

def start_pressed():
    print("Button pressed")
    global status
    if status == 1:
        all_off()
    elif status == 0:
        all_on()


@blynk.on("V0") #gestione degli I/O
def v0_write_handler(value):
    if int(value[0]) == 1:
        all_on()
    else:
        all_off()


while True:
    if wifi.isconnected():
        blynk.run()
        print("Blynk run...")
        if start_button.value() == 0:
            utime.sleep_ms(500)
            start_pressed()
    else:
        connessione(WIFI_SSID, WIFI_PASS)
        print("Connecting to Blynk...")
        blynk = BlynkLib.Blynk(BLYNK_AUTH)
        @blynk.on("V0") #gestione degli I/O
        def v0_write_handler(value):
            if int(value[0]) == 1:
                all_on()
            else:
                all_off()

