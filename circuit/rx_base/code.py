
# Copyright 2021 Colin Torney
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This code is for the collar-follower base station. It is based on adafruit code
and will send messages to a GPS tag to turn on high frequency fix mode then 
forward fixes over bluetooth to an android tablet. 
"""

import board
import busio
import displayio
import terminalio
from time import sleep
import time

from adafruit_display_text import label
import adafruit_displayio_sh1107
from digitalio import DigitalInOut, Direction, Pull
import digitalio

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet

#import ulora
import adafruit_rfm9x

DEBUG = 1                   # In debug mode we just listen and forward
"""
Constant parameters
"""
# LED DISPLAY
WIDTH = 128
HEIGHT = 64
BORDER = 2

screen_refresh = 30         # time interval (s) for rewriting screen (mainly for RSSI) 

# RADIO MESSAGES
WAKE = "BASE,PING"          # wake-up message constantly sent
SLEEP = "BASE,GOTOSLEEP,"   # sleep message, sent on button press to deactivate the tag
ACK = "BASE,ACK"            # acknowledge receipt of message and tell tag to proceed

# RADIO
RADIO_FREQ_MHZ = 868.00
MAX_TX_POWER = 23

NO_COLLAR = -1              # ID to return if no collar is found
COLLAR_TIME_OUT = 120       # how long to wait before giving up on a collar

"""
Initialise the bluetooth device
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)


"""
Initialise the display
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
displayio.release_displays()

button_A = DigitalInOut(board.D9)
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP

# Use for I2C
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000 # black 

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)

splash.append(bg_sprite)

text_area = label.Label(terminalio.FONT, text='Starting....', color=0xFFFFFF, x=8, y=8)
splash.append(text_area)

def screen_write(text=""):

    splash[1] = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=8, y=8)


"""
Initialise the LORA radio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Define pins connected to the chip - this needs some wiring on the LoRa featherwing
# CS needs to be wired to B and RST needs to be wired to A and soldered in 
CS = digitalio.DigitalInOut(board.D10)
RESET = digitalio.DigitalInOut(board.D11)

# Initialze RFM radio
# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23
rfm9x.spreading_factor = 11
rfm9x.signal_bandwidth = 125000
rfm9x.coding_rate = 5
rfm9x.node = 0

# Set to max transmit power!
#rfm9x.tx_power = MAX_TX_POWER
#rfm9x.spreading_factor = 8
#rfm9x.signal_bandwidth = 250000#a62500
#rfm9x.coding_rate = 5

#print(rfm9x.bw_bins)
packetnum=0
while False:
    sleep(1.0)
    print("Transmitting...")
    rfm9x.send(bytes("Hello World #" + str(packetnum) + "\n", "utf-8"))

    packetnum+=1
    sleep(0.01)

while True:
    print("waiting for message...")
    screen_write("waiting for message...")
    packet = rfm9x.receive(timeout=7.0)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        # Received a packet!
        # Print out the raw bytes of the packet:
        print("Received (raw bytes): {0}".format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        try: 
            packet_text = str(packet, "ascii")
            print("Received (ASCII): {0}".format(packet_text))
            screen_write("Received (ASCII): {0}".format(packet_text))
        except:
            print("Message garbled")
            screen_write("Message garbled")
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
        screen_write("Received signal strength: {0} dB".format(rssi))
        rfm9x.send(bytes("Message received at base", "utf-8"))
    else:
        print('no message')
        screen_write('no message')

    sleep(0.01)
