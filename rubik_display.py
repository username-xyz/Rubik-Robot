#!/usr/bin/python

#
# This class controls the SSD1306 display to provide user feedback.
#
# The display is divided into two areas that can display independant messages.
# The upper part of the display is yellow and is referred to as the header
# area. The lower part of the display is blue. and is referred to as the
# body area.
#

# Import I2C pin information.
import board
import busio

# The Python Imaging Libary is used for drawing text into an image.
from PIL import Image, ImageDraw, ImageFont

# Import the SSD1306 display module library
import adafruit_ssd1306


# Rubik solver display class
#
class RubikDisplay(object):
    def __init__(self):
        # Create an image used for drawing text to be displayed
        # The image size matches the display size.
        self.image = Image.new('1',(128,64))
        self.draw = ImageDraw.Draw(self.image)

        # I2C bus used to communicate  with the display
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Display driver
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, self.i2c)

        # Fonts used to draw text on the display
        self.font_small = ImageFont.truetype('Perfect DOS VGA 437.ttf', 16)
        self.font_large = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 21)

        # Blank the display
        self.oled.fill(0)
        self.oled.show()

    # Write text to the header (top yellow part) of the display
    #
    # Input:
    #   text        The text string to be displayed
    #
    def write_header(self, text):
        # Clear the header part of the image before drawing new text
        self.draw.rectangle([(0,0), (128,16)], fill=0, outline=None)

        # Write the text to the header area
        self.draw.text((0,0), text, font=self.font_small, fill=255)
        self.oled.image(self.image)
        self.oled.show()

    # Write text to the body (bottom blue part) of the display
    #
    # Input:
    #   text        The text string to be displayed
    #
    def write_body(self, text):
        # Clear the body part of the image before drawing new text
        self.draw.rectangle([(0,16), (128,64)], fill=0, outline=None)

        # Write the text to the the body area
        self.draw.multiline_text((0,15), text, font=self.font_large, fill=255)
        self.oled.image(self.image)
        self.oled.show()
