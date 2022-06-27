#!/usr/bin/python

#
# This is a fairly simple GPIO pin debouncer.
# It just uses a fixed debounce time to wait for a signal to stop bouncing.
# This is good enough for uses like detecting user push buttons where
# the signal doesn't change often or quickly.
#
# This class debounces a single GPIO pin. To debounce multiple GPIOs
# create multiple instances of this class.
#
# This class will pass events using a queue supplied by the code that
# created it.
#

import threading
from time import sleep

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)  # Use processor GPIO pin numbers

from queue import Queue


# Pull up or pull down resistor selection for the GPIO port
# These vales are passed in by the code that uses this class,
#
GPIO_PULL_UP   = 0
GPIO_PULL_DOWN = 1
GPIO_PULL_OFF  = 2


# GPIO pin debounce class
#
# Inputs:
#   msg_q          Queue used to pass gpio events
#   pin_num        GPIO pin number to debounce
#   pupd           Pull up or down configuration for the GPIO pin
#   debounce_time  The time to wait for the pin to stop bouncing
#
class GpioDebounce(threading.Thread):
    def __init__(self, msg_q, pin_num, pupd, debounce_time=200):
        super().__init__(daemon=True)

        # Save the vales supplied by the calling code
        self.gpio_pin = pin_num
        self.pull = pupd
        self.db_time = debounce_time
        self.q = msg_q

        # Configure the GPIO hardware
        if (self.pull == GPIO_PULL_UP):
            GPIO.setup(self.gpio_pin, GPIO.IN, GPIO.PUD_UP)
        elif (self.pull == GPIO_PULL_OFF):
            GPIO.setup(self.gpio_pin, GPIO.IN, GPIO.PUD_DOWN)
        else:
            GPIO.setup(self.gpio_pin, GPIO.IN, GPIO.PUD_OFF)

        # Save the current pin state
        self.old_state = GPIO.input(self.gpio_pin)
        self.new_state = self.old_state

        # Detect pin change events
        GPIO.add_event_detect(self.gpio_pin, GPIO.BOTH, \
                              callback=self.event_cb, bouncetime=self.db_time)

    # Pin change event handler function
    #
    # Input:
    #   pin     Pin number of the GPIO that changed state
    #
    def event_cb(self, pin):
        # Delay to allow the pin to stop bouncing
        sleep(float(self.db_time/1000))

        # Read the new pin state
        self.new_state = GPIO.input(self.gpio_pin)

        # Check if the state has changed
        if (self.old_state != self.new_state):
            if (self.new_state == 0):
                # Report that the pin has gone low
                self.q.put((self.gpio_pin, 0))
            else:
                # Report that the pin has gone high
                self.q.put((self.gpio_pin, 1))

            # Save the new state
            self.old_state = self.new_state
