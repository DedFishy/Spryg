from machine import SPI,Pin,I2S
import os
import math
import struct
import time
from ST7735 import TFT
from framebuf import FrameBuffer, RGB565

try:
    import sd as sdcard
    try_sd = True
except ImportError as e:
    print("[?] SD card module not found. SD Card will not be initialized.")
    try_sd = False

def bytes_to_gb(b):
    return b/1e+9


class Spryg:
    BUTTONS = {
        "W": Pin(5, Pin.IN, Pin.PULL_UP),
        "A": Pin(6, Pin.IN, Pin.PULL_UP),
        "S": Pin(7, Pin.IN, Pin.PULL_UP),
        "D": Pin(8, Pin.IN, Pin.PULL_UP),
        
        "I": Pin(12, Pin.IN, Pin.PULL_UP),
        "J": Pin(13, Pin.IN, Pin.PULL_UP),
        "K": Pin(14, Pin.IN, Pin.PULL_UP),
        "L": Pin(15, Pin.IN, Pin.PULL_UP), 
    }
    
    LED_L = Pin(28, Pin.OUT)
    LED_R = Pin(4, Pin.OUT)
    
    
    SCK_PIN = 10 #BCLK
    WS_PIN = 11 #LCK
    SD_PIN = 9 #DIN
    I2S_ID = 0 
    BUFFER_LENGTH_IN_BYTES = 2000
    SAMPLE_RATE_IN_HZ = 22_050
    SAMPLE_SIZE_IN_BITS = 16
    
    def __init__(self):
        
        # Screen setup
        
        # The backlight, by default on because the screen practically needs it
        self.backlight = Pin(17, Pin.OUT)
        self.backlight.on()
        
        # Set up the SPI protocol
        spi = SPI(0, baudrate=20000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
        # Set up the screen class
        self.tft=TFT(spi, 22, 26, 20)
        self.tft.initr()
        self.tft.rgb(True)
        # Rotate it to the correct orientation
        self.tft.rotation(1)
        # By default we want it black
        self.tft.fill(TFT.BLACK)

        # Set up a buffer so screen writing is smooth
        self.buf = bytearray(128*160*2)
        self.screen = FrameBuffer(self.buf, 160, 128, RGB565)
        
        # Final bit of screen set up
        self.tft._setwindowloc((0,0),(159,127))
        
        # Set up audio
        self.audio_out = I2S(
            self.I2S_ID,
            sck=Pin(self.SCK_PIN),
            ws=Pin(self.WS_PIN),
            sd=Pin(self.SD_PIN),
            mode=I2S.TX,
            bits=self.SAMPLE_SIZE_IN_BITS,
            format=I2S.MONO,
            rate=self.SAMPLE_RATE_IN_HZ,
            ibuf=self.BUFFER_LENGTH_IN_BYTES,
        )
        
        if try_sd:
            try:
                # Set up SD Card
                self.sd_spi = SPI(0,baudrate=40000000,sck=Pin(18),mosi=Pin(19),miso=Pin(16))
                # Initialize SD card
                self.sd = sdcard.SDCard(self.sd_spi, Pin(21))
                os.mount(self.sd, "/sd")

                print("Files: " + str(os.listdir("/sd")))
                
                self.loaded_sd = True
            except Exception as e:
                print("[!] " + str(e))
                self.loaded_sd = False
    
    ## Buttons
    def get_button(self, bid):
        return not bool(self.BUTTONS[bid].value())
    
    ## LEDs
    def set_led(self, name, state):
        if name == "L":
            if state:
                self.LED_L.on()
            else:
                self.LED_L.off()
        if name == "R":
            if state:
                self.LED_R.on()
            else:
                self.LED_R.off()
    
    ## Audio
    def make_tone(self, frequency):
        # create a buffer containing the pure tone samples
        samples_per_cycle = self.SAMPLE_RATE_IN_HZ // frequency
        sample_size_in_bytes = self.SAMPLE_SIZE_IN_BITS // 8
        samples = bytearray(samples_per_cycle * sample_size_in_bytes)
        volume_reduction_factor = 32
        range = pow(2, self.SAMPLE_SIZE_IN_BITS) // 2 // volume_reduction_factor
        
        if self.SAMPLE_SIZE_IN_BITS == 16:
            format = "<h"
        else:  # assume 32 bits
            format = "<l"
        
        for i in range(samples_per_cycle):
            sample = range + int((range - 1) * math.sin(2 * math.pi * i / samples_per_cycle))
            struct.pack_into(format, samples, i * sample_size_in_bytes, sample)
            
        return samples
    
    def play_audio(self, audio, total_time):
        # continuously write tone sample buffer to an I2S DAC
        try:
            start = time.ticks_ms()
            
            while time.ticks_diff(time.ticks_ms(), start) < total_time:
                #print(time.ticks_diff(start, time.ticks_ms()))
                num_written = self.audio_out.write(audio)

        except (KeyboardInterrupt, Exception) as e:
            print("caught exception {} {}".format(type(e).__name__, e))
    
    # Show text only on screen
    def show_text(self, text, color):
        # Show a message
        text = text.split("\n")
        
        self.screen.fill(0)
        for i in range(0, len(text)):
            self.screen.text(text[i], 0, i*10, color)
        self.flip()
    
    # Update display with one call (as opposed to still one but it's more verbose)
    def flip(self):
        self.tft._writedata(self.buf)
    
    # Make this run the loaded program later
    def run(self):
        try:
            try:
                import game
                
                game.run(self)
                
            except ImportError: # Could not find the game
                # Show an error message
                self.show_text("""Welcome to Spryg!
It seems that there
is no game loaded on
this console. For
instructions, refer
to the Spryg docs on
Github. Good luck!
____________________

If you did load a
game, be sure to
file a bug report
on Github.""", 0xFFFF)
        
        except Exception as e:
            self.show_text("""An error occurred.
If you're debugging
your game with a
computer, you can
see the error in
the MicroPython
terminal. Otherwise,
restart your Sprig.
The type of error
seems to be:
""" + str(e), 0x00F8)
            print("ERROR OCCURRED: " + str(e))
        except:
            print("Gracefully exiting.")
        
        self.audio_out.deinit()

spryg = Spryg()

spryg.run()