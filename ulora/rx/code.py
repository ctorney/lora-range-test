# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the RFM95 LoRa radio.
# Author: Tony DiCola
import board
import busio
import digitalio

import ulora

from time import sleep

# Define radio parameters.
#RADIO_FREQ_MHZ = 869.45  # Frequency of the radio in Mhz. Must match your
RADIO_FREQ_MHZ = 868.0 #869.45  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

CS = digitalio.DigitalInOut(board.RFM9X_CS)
RESET = digitalio.DigitalInOut(board.RFM9X_RST)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9x = ulora.LoRa(spi, CS, modem_config=ulora.ModemConfig.Bw31_25Cr48Sf512,tx_power=23) 

while True:
    print("waiting for message...")
    packet = rfm9x.receive(timeout=20.0)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        # Received a packet!
        LED.value = True
        # Print out the raw bytes of the packet:
        print("Received (raw bytes): {0}".format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        try: 
            packet_text = str(packet, "ascii")
            print("Received (ASCII): {0}".format(packet_text))
        except:
            print("Message garbled")
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
        rfm9x.send(bytes("And hello back to you\n", "utf-8"),1)
    else:
        print('no message')

    sleep(0.01)
    LED.value = False
