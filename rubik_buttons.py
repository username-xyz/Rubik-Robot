#!/usr/bin/python

#
# This class detects button presses of the three buttons on the Rubik's
# cube solver hardware.
#
# It uses the GpioDebounce class to clean up the press and release events.
#
# It reports button press events through a queue supplied by the caller.
#

import threading

from queue import Queue

from GPIO_debounce import GpioDebounce
from GPIO_debounce import GPIO_PULL_UP, GPIO_PULL_DOWN, GPIO_PULL_OFF

# GPIO pin numbers of the buttons
# These are processor GPIO numbers, not header pin numbers.
#
UP_BUTTON_GPIO    = 17
DOWN_BUTTON_GPIO  = 27
ENTER_BUTTON_GPIO = 22

# Button values reported in the button queue
#
UP_BUTTON    = 0
DOWN_BUTTON  = 1
ENTER_BUTTON = 2


# Rubik solver button class
#
# Inputs:
#  out_q    Queue used to report button presses
#
class RubikButtons(threading.Thread):

    def __init__(self, btn_q):
        super().__init__(daemon=True)

        # Save the button queue used to report button presses
        self.out_q = btn_q

        # Create the queue used to receive GPIO debounce events
        self.in_q = Queue(maxsize = 8)

        # Create the GPIO button debounce objects
        self.pb = GpioDebounce(self.in_q, UP_BUTTON_GPIO, GPIO_PULL_UP, 50)
        self.mb = GpioDebounce(self.in_q, DOWN_BUTTON_GPIO, GPIO_PULL_UP, 50)
        self.eb = GpioDebounce(self.in_q, ENTER_BUTTON_GPIO, GPIO_PULL_UP, 50)

    def run(self):
        while 1:
            # Wait for a GPIO state change event
            button_event = self.in_q.get()

            # A button press will be a 0 level
            if (button_event[1] == 0):
                # Determine which button was pressed and report
                if (button_event[0] == UP_BUTTON_GPIO):
                    self.out_q.put(UP_BUTTON)
                elif (button_event[0] == DOWN_BUTTON_GPIO):
                    self.out_q.put(DOWN_BUTTON)
                elif (button_event[0] == ENTER_BUTTON_GPIO):
                    self.out_q.put(ENTER_BUTTON)
