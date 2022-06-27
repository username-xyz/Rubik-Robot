#!/usr/bin/python

# Needed for command line argument parsing
import sys

# Needed for sleep
from time import sleep

# Import I2C pins.
import board
import busio

# I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Library to control the PCA9685 PWM board that drives the servos
from adafruit_pca9685 import PCA9685
pca = PCA9685(i2c)


# Use a 50 Hz PWM frequency
pwm_freq = 50

if (len(sys.argv) == 3):
    pwm_port = int(sys.argv[1])
    pwm_value = int(sys.argv[2])

    # Set the frequency for all PWM outputs
    pca.frequency = pwm_freq

    sleep(1)

    # Program the PWM port
    pca.channels[pwm_port].duty_cycle = pwm_value << 4
else:
    print ("Invalid command line arguments")
