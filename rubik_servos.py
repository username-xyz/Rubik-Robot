#!/usr/bin/python

# The code in this file is used to control the Rubiks Cube solver
# servo motors.
#
# My servos are DS3218 servos. All settings are set based on on these
# specific servos. These servos provide a 180 degrees of motion.
#
# Each gripper has two servos. A "Turn" servo that rotates the entire
# gripper and a "Grip" servo that open and closes the gripper.
#
# In this code "clockwise" and "counterclockwise" are defined looking
# down on the gripper from above. The counterclockwise position of the
# turn servo is also referred to as the -90 degree position.
# When the gripper is hoizontal it is in the 0 degree position.
# The clockwise position is 90 degrees.


# Import I2C pins.
import board
import busio

# Needed for file I/O functions
import os

from time import sleep

# Library to control the PCA9685 PWM board that drives the servos
from adafruit_pca9685 import PCA9685

# Display controller class
from rubik_display import RubikDisplay

# Button detection class
from rubik_buttons import RubikButtons, UP_BUTTON, DOWN_BUTTON, ENTER_BUTTON


# Set this to 0 to disable debug logging, 1 to enable.
DEBUG = 0


# Delay to allow servos to move (seconds)
# This time is probably conservative but I would rather be a litle slow
# than have errors caused by moving the servos too fast.
SERVO_MOVE_DELAY = 1.0

# Current servo positions
# These are used to optimize the servo move functions by keeping track
# of the current servo positions. This avoids having to move the servos
# back to a "home" position between movements. It does however make
# the servo logic more cpmplex.
# The actual values aren't important, they just need to be unique.
#
# Turn servos
T_POS_M90    = 0    # Counterclockwise 90 degree position
T_POS_0      = 1    # Center (horizontal) position
T_POS_P90    = 2    # Clockwise 90 degree position
# Grip servos
G_POS_OPEN   = 0    # Grip fully open position
G_POS_LOAD   = 1    # Grip in the load cube position
G_POS_CLOSED = 2    # Grip closed position


# Rubik solver servo class
#
class RubikServo(object):
    def __init__(self, button_q):
        # Save the button queue class reference
        self.btn_q = button_q

        # Servo calibration file name
        self.cal_file = "servo_tune.txt"

        # I2C bus used to communicate with the PWM hardware
        i2c = busio.I2C(board.SCL, board.SDA)

        # PWM driver
        self.pca = PCA9685(i2c)

        # Read the calibration file
        # Each line in the file has a single calibration number.
        # The number can optionally be followed by a space and a text comment.
        # The comments are ignored by the code, they are just to identify
        # the values if the file is manually edited.
        try:
            f=open(self.cal_file, 'r')
            # Read the saved calibration values
            self.pwm_freq = self.read_tune_val(f)
            self.pwm_min = self.read_tune_val(f)
            self.pwm_max = self.read_tune_val(f)
            self.rg = self.read_tune_val(f)
            self.rt = self.read_tune_val(f)
            self.lg = self.read_tune_val(f)
            self.lt = self.read_tune_val(f)
            self.rt_cal_m90 = self.read_tune_val(f)
            self.rt_cal_0   = self.read_tune_val(f)
            self.rt_cal_90  = self.read_tune_val(f)
            self.rg_cal_close = self.read_tune_val(f)
            self.rg_cal_open = self.read_tune_val(f)
            self.rg_cal_load = self.read_tune_val(f)
            self.lt_cal_m90 = self.read_tune_val(f)
            self.lt_cal_0 = self.read_tune_val(f)
            self.lt_cal_90 = self.read_tune_val(f)
            self.lg_cal_close = self.read_tune_val(f)
            self.lg_cal_open = self.read_tune_val(f)
            self.lg_cal_load = self.read_tune_val(f)

            f.close() 
        except:
            f.close() 
            print("Calibration file error")
            raise
        else:
            print("Calibration file found")

        # Set the frequency for all PWM channels
        self.pca.frequency = self.pwm_freq

        # Set the initial PWM value for all ports
        # The shift left is needed to put a 12 bit value into a
        # 16 bit register
        self.set_pwm_value(self.rt, self.rt_cal_0)
        self.rt_pos = T_POS_0
        self.set_pwm_value(self.rg, self.rg_cal_open)
        self.rg_pos = G_POS_OPEN
        self.set_pwm_value(self.lt, self.lt_cal_0)
        self.lt_pos = T_POS_0
        self.set_pwm_value(self.lg, self.lg_cal_open)
        self.lg_pos = G_POS_OPEN


    # Read a value from the servo tune file
    #
    # Input:
    #   fh      file handle to the open tune values file
    #
    def read_tune_val(self, fh):
        tune_line  = fh.readline()
        tune_spilt = tune_line.split(" ")
        val = int(tune_spilt[0])
        return val

    # Program the PWM hardware to drive a servo.
    # The 12 bit pwm value must be shifted left 4 bits to put it into
    # the most significant bits of the 16 register.
    #
    # Inputs:
    #   port    Servo port number
    #   pwm     PWM count
    def set_pwm_value(self, port, pwm):
        # If the user pressed a button then abort
        if (self.btn_q.qsize() > 0):
            # Discard the button
            self.btn_q.get(False, 0)
            raise KeyboardInterrupt

        self.pca.channels[port].duty_cycle = pwm << 4


    ######################################################
    #
    # These functions move a single servo to implement a simple movement.
    ######################################################


    # Set the Right Turn servo to the counterclockwise position
    #
    def set_right_turn_m90(self):
        if (DEBUG == 1):
            print("set_right_turn_m90")
        if (self.rt_pos != T_POS_M90):
            self.set_pwm_value(self.rt, self.rt_cal_m90)
            self.rt_pos = T_POS_M90
            sleep(SERVO_MOVE_DELAY)


    # Set the Right Turn servo to the center (horizontal) position
    #
    def set_right_turn_0(self):
        if (DEBUG == 1):
            print("set_right_turn_0")
        if (self.rt_pos != T_POS_0):
            self.set_pwm_value(self.rt, self.rt_cal_0)
            self.rt_pos = T_POS_0
            sleep(SERVO_MOVE_DELAY)


    # Set the Right Turn servo to the clockwise position
    #
    def set_right_turn_90(self):
        if (DEBUG == 1):
            print("set_right_turn_90")
        if (self.rt_pos != T_POS_P90):
            self.set_pwm_value(self.rt, self.rt_cal_90)
            self.rt_pos = T_POS_P90
            sleep(SERVO_MOVE_DELAY)


    # Set the Right Grip server to the open position
    #
    def set_right_grip_open(self):
        if (DEBUG == 1):
            print("set_right_grip_open")
        if (self.rg_pos != G_POS_OPEN):
            if (self.rg_pos == G_POS_CLOSED):
                # Open just a little first to avoid messing up the cube
                self.set_pwm_value(self.rg, \
                             int((self.rg_cal_close + self.rg_cal_load)/2))
                sleep(SERVO_MOVE_DELAY / 4)
            self.set_pwm_value(self.rg, self.rg_cal_open)
            self.rg_pos = G_POS_OPEN
            sleep(SERVO_MOVE_DELAY)


    # Set the Right Grip server to the cube load position
    #
    def set_right_grip_load(self):
        if (DEBUG == 1):
            print("set_right_grip_load")
        if (self.rg_pos != G_POS_LOAD):
            self.set_pwm_value(self.rg, self.rg_cal_load)
            self.rg_pos = G_POS_LOAD
            sleep(SERVO_MOVE_DELAY)


    # Set the Right Grip server to the closed position
    #
    def set_right_grip_closed(self):
        if (DEBUG == 1):
            print("set_right_grip_closed")
        if (self.rg_pos != G_POS_CLOSED):
            self.set_pwm_value(self.rg, self.rg_cal_close)
            self.rg_pos = G_POS_CLOSED
            sleep(SERVO_MOVE_DELAY)


    # Set the Left Turn servo to the counterclockwise position
    #
    def set_left_turn_m90(self):
        if (DEBUG == 1):
            print("set_left_turn_m90")
        if (self.lt_pos != T_POS_M90):
            self.set_pwm_value(self.lt, self.lt_cal_m90)
            self.lt_pos = T_POS_M90
            sleep(SERVO_MOVE_DELAY)


    # Set the Left Turn servo to the center (horizontal) position
    #
    def set_left_turn_0(self):
        if (DEBUG == 1):
            print("set_left_turn_0")
        if (self.lt_pos != T_POS_0):
            self.set_pwm_value(self.lt, self.lt_cal_0)
            self.lt_pos = T_POS_0
            sleep(SERVO_MOVE_DELAY)


    # Set the Left Turn servo to the clockwise position
    #
    def set_left_turn_90(self):
        if (DEBUG == 1):
            print("set_left_turn_90")
        if (self.lt_pos != T_POS_P90):
            self.set_pwm_value(self.lt, self.lt_cal_90)
            self.lt_pos = T_POS_P90
            sleep(SERVO_MOVE_DELAY)


    # Set the Left Grip server to the open position
    #
    def set_left_grip_open(self):
        if (DEBUG == 1):
            print("set_left_grip_open")
        if (self.lg_pos != G_POS_OPEN):
            if (self.lg_pos == G_POS_CLOSED):
                # Open just a little first to avoid messing up the cube
                self.set_pwm_value(self.lg, \
                             int((self.lg_cal_close + self.lg_cal_load)/2))
                sleep(SERVO_MOVE_DELAY / 4)
            self.set_pwm_value(self.lg, self.lg_cal_open)
            self.lg_pos = G_POS_OPEN
            sleep(SERVO_MOVE_DELAY)


    # Set the Left Grip server to the cube load position
    #
    def set_left_grip_load(self):
        if (DEBUG == 1):
            print("set_left_grip_load")
        if (self.lg_pos != G_POS_LOAD):
            self.set_pwm_value(self.lg, self.lg_cal_load)
            self.lg_pos = G_POS_LOAD
            sleep(SERVO_MOVE_DELAY)


    # Set the Left Grip server to the closed position
    #
    def set_left_grip_closed(self):
        if (DEBUG == 1):
            print("set_left_grip_closed")
        if (self.lg_pos != G_POS_CLOSED):
            self.set_pwm_value(self.lg, self.lg_cal_close)
            self.lg_pos = G_POS_CLOSED
            sleep(SERVO_MOVE_DELAY)


    ######################################################
    # Complex movement functions
    #
    # These functions move multiple servos to implement more complex movements.
    ######################################################


    # Set all servos to the cube load position
    #
    # Inputs:
    #   display         The display controller class
    #   btn_q           The queue used to get button press events
    #
    def cube_load(self, display, btn_q):
        if(DEBUG == 1):
            print("cube_load")
        display.write_body("Load\nCube")
        # Make sure the turn servos are horizontal
        self.set_right_turn_0()
        self.set_left_turn_0()
        # Put the grippers into the load cube position
        self.set_pwm_value(self.rg, self.rg_cal_load)
        self.rg_pos = G_POS_LOAD
        self.set_pwm_value(self.lg, self.lg_cal_load)
        self.lg_pos = G_POS_LOAD
        sleep(SERVO_MOVE_DELAY)

        while 1:
            # Wait for a button event
            button_press = btn_q.get()

            if (button_press == ENTER_BUTTON):
                # Close the grippers
                self.set_pwm_value(self.rg, self.rg_cal_close)
                self.rg_pos = G_POS_CLOSED
                self.set_pwm_value(self.lg, self.lg_cal_close)
                self.lg_pos = G_POS_CLOSED
                sleep(SERVO_MOVE_DELAY)
                break


    # Open both grippers so the cube can be removed
    #
    def cube_release(self):
        if(DEBUG == 1):
            print("cube_release")
        if (self.rt_pos != T_POS_0):
            self.set_right_grip_open()
            self.set_right_turn_0()
            self.set_right_grip_closed()
        if (self.lt_pos != T_POS_0):
            self.set_left_grip_open()
            self.set_left_turn_0()
            self.set_left_grip_closed()
        self.set_pwm_value(self.rg, self.rg_cal_load)
        self.rg_pos = G_POS_LOAD
        self.set_pwm_value(self.lg, self.lg_cal_load)
        self.lg_pos = G_POS_LOAD
        sleep(SERVO_MOVE_DELAY)


    # Make sure the right gripper doesn't block the camera
    #
    def clear_camera(self):
        if(DEBUG == 1):
            print("clear_camera")
        if (self.rt_pos != T_POS_0):
            self.set_right_grip_open()
            self.set_right_turn_0()
            self.set_right_grip_closed()


    ######################################################
    # Cube Solver functions
    #
    # These functions move multiple servos to implement the cube movements
    # needed to solve the cube.
    #
    # These functions will look at the current gripper positions then
    # determine how to most efficiently do the requested movement.
    ######################################################


    # Use the right gripper to rotate the cube 90 degrees clockwise
    #
    def right_rotate_cube_90_cw(self):
        if(DEBUG == 1):
            print("right_rotate_cube_90_cw")
        # Make sure the left gripper won't be in the way
        if (self.lt_pos != T_POS_0):
            self.set_left_grip_open()
            self.set_left_turn_0()
        if (self.rt_pos == T_POS_P90):
            self.set_left_grip_closed()
            # The gripper must be repositioned because it can't turn
            # any farther clockwise.
            self.set_right_grip_open()
            self.set_right_turn_0()
            self.set_right_grip_closed()
        self.set_left_grip_open()
        if (self.rt_pos == T_POS_0):
            self.set_right_turn_90()
        else:
            self.set_right_turn_0()
        self.set_left_grip_closed()


    # Use the right gripper to rotate the cube 90 degrees counterclockwise
    #
    def right_rotate_cube_90_ccw(self):
        if(DEBUG == 1):
            print("right_rotate_cube_90_ccw")
        # Make sure the left gripper won't be in the way
        if (self.lt_pos != T_POS_0):
            self.set_left_grip_open()
            self.set_left_turn_0()
        if (self.rt_pos == T_POS_M90):
            self.set_left_grip_closed()
            # The gripper must be repositioned because it can't turn
            # any farther counterclockwise.
            self.set_right_grip_open()
            self.set_right_turn_0()
            self.set_right_grip_closed()
        self.set_left_grip_open()
        if (self.rt_pos == T_POS_0):
            self.set_right_turn_m90()
        else:
            self.set_right_turn_0()
        self.set_left_grip_closed()


    # Use the right gripper to rotate the cube 180 degrees
    #
    def right_rotate_cube_180(self):
        if(DEBUG == 1):
            print("right_rotate_cube_180")
        # Make sure the left gripper won't be in the way
        if (self.lt_pos != T_POS_0):
            self.set_left_grip_open()
            self.set_left_turn_0()
        if (self.rt_pos == T_POS_0):
            self.set_left_grip_closed()
            # The gripper must be repositioned because it can't turn
            # 180 degrees.
            self.set_right_grip_open()
            self.set_right_turn_m90()
            self.set_right_grip_closed()
        self.set_left_grip_open()
        if (self.rt_pos == T_POS_M90):
            self.set_right_turn_90()
        else:
            self.set_right_turn_m90()
        self.set_left_grip_closed()


    # Use the right gripper to rotate a face 90 degrees clockwise
    #
    def right_rotate_face_90_cw(self):
        if(DEBUG == 1):
            print("right_rotate_face_90_cw")
        # Make sure the left gripper won't be in the way
        if (self.lt_pos != T_POS_0):
            self.set_left_grip_open()
            self.set_left_turn_0()
            self.set_left_grip_closed()
        if (self.rt_pos == T_POS_P90):
            # The gripper must be repositioned because it can't turn
            # clockwise.
            self.set_right_grip_open()
            self.set_right_turn_0()
            self.set_right_grip_closed()
        if (self.rt_pos == T_POS_M90):
            self.set_right_turn_0()
        else:
            self.set_right_turn_90()


    # Use the right gripper to rotate a face 90 degrees counterclockwise
    #
    def right_rotate_face_90_ccw(self):
        if(DEBUG == 1):
            print("right_rotate_face_90_ccw")
        # Make sure the left gripper won't be in the way
        if (self.lt_pos != T_POS_0):
            self.set_left_grip_open()
            self.set_left_turn_0()
            self.set_left_grip_closed()
        if (self.rt_pos == T_POS_M90):
            # The gripper must be repositioned because it can't turn
            # counterclockwise.
            self.set_right_grip_open()
            self.set_right_turn_0()
            self.set_right_grip_closed()
        if (self.rt_pos == T_POS_M90):
            self.set_right_turn_0()
        else:
            self.set_right_turn_m90()


    # Use the right gripper to rotate a face 180 degrees
    #
    def right_rotate_face_180(self):
        if(DEBUG == 1):
            print("right_rotate_face_180")
        # Make sure the left gripper won't be in the way
        if (self.lt_pos != T_POS_0):
            self.set_left_grip_open()
            self.set_left_turn_0()
            self.set_left_grip_closed()
        if (self.rt_pos == T_POS_0):
            # The gripper must be repositioned because it can't turn
            # 180 degrees.
            self.set_right_grip_open()
            self.set_right_turn_m90()
            self.set_right_grip_closed()
        if (self.rt_pos == T_POS_P90):
            self.set_right_turn_m90()
        else:
            self.set_right_turn_90()


    # Use the left gripper to rotate the cube 90 degrees clockwise
    #
    def left_rotate_cube_90_cw(self):
        if(DEBUG == 1):
            print("left_rotate_cube_90_cw")
        # Make sure the right gripper won't be in the way
        if (self.rt_pos != T_POS_0):
            self.set_right_grip_open()
            self.set_right_turn_0()
        if (self.lt_pos == T_POS_P90):
            self.set_right_grip_closed()
            # The gripper must be repositioned because it can't turn
            # clockwise.
            self.set_left_grip_open()
            self.set_left_turn_0()
            self.set_left_grip_closed()
        self.set_right_grip_open()
        if (self.lt_pos == T_POS_0):
            self.set_left_turn_90()
        else:
            self.set_left_turn_0()
        self.set_right_grip_closed()


    # Use the left gripper to rotate the cube 90 degrees counterclockwise
    #
    def left_rotate_cube_90_ccw(self):
        if(DEBUG == 1):
            print("left_rotate_cube_90_ccw")
        # Make sure the right gripper won't be in the way
        if (self.rt_pos != T_POS_0):
            self.set_right_grip_open()
            self.set_right_turn_0()
        if (self.lt_pos == T_POS_M90):
            self.set_right_grip_closed()
            # The gripper must be repositioned because it can't turn
            # counterclockwise.
            self.set_left_grip_open()
            self.set_left_turn_0()
            self.set_left_grip_closed()
        self.set_right_grip_open()
        if (self.lt_pos == T_POS_0):
            self.set_left_turn_m90()
        else:
            self.set_left_turn_0()
        self.set_right_grip_closed()


    # Use the left gripper to rotate the cube 180 degrees
    #
    def left_rotate_cube_180(self):
        if(DEBUG == 1):
            print("left_rotate_cube_180")
        # Make sure the right gripper won't be in the way
        if (self.rt_pos != T_POS_0):
            self.set_right_grip_open()
            self.set_right_turn_0()
        if (self.lt_pos == T_POS_0):
            self.set_right_grip_closed()
            # The gripper must be repositioned because it can't turn
            # 180 degrees.
            self.set_left_grip_open()
            self.set_left_turn_m90()
            self.set_left_grip_closed()
        self.set_right_grip_open()
        if (self.lt_pos == T_POS_M90):
            self.set_left_turn_90()
        else:
            self.set_left_turn_m90()
        self.set_right_grip_closed()


    # Use the left gripper to rotate a face 90 degrees clockwise
    #
    def left_rotate_face_90_cw(self):
        if(DEBUG == 1):
            print("left_rotate_face_90_cw")
        # Make sure the right gripper won't be in the way
        if (self.rt_pos != T_POS_0):
            self.set_right_grip_open()
            self.set_right_turn_0()
            self.set_right_grip_closed()
        if (self.lt_pos == T_POS_P90):
            # The gripper must be repositioned because it can't turn
            # clockwise.
            self.set_left_grip_open()
            self.set_left_turn_0()
            self.set_left_grip_closed()
        if (self.lt_pos == T_POS_M90):
            self.set_left_turn_0()
        else:
            self.set_left_turn_90()


    # Use the left gripper to rotate a face 90 degrees counterclockwise
    #
    def left_rotate_face_90_ccw(self):
        if(DEBUG == 1):
            print("left_rotate_face_90_ccw")
        # Make sure the right gripper won't be in the way
        if (self.rt_pos != T_POS_0):
            self.set_right_grip_open()
            self.set_right_turn_0()
            self.set_right_grip_closed()
        if (self.lt_pos == T_POS_M90):
            # The gripper must be repositioned because it can't turn
            # counterclockwise.
            self.set_left_grip_open()
            self.set_left_turn_0()
            self.set_left_grip_closed()
        if (self.lt_pos == T_POS_P90):
            self.set_left_turn_0()
        else:
            self.set_left_turn_m90()


    # Use the left gripper to rotate a face 180 degrees 
    # 
    def left_rotate_face_180(self):
        if(DEBUG == 1):
            print("left_rotate_face_180")
        # Make sure the right gripper won't be in the way
        if (self.rt_pos != T_POS_0):
            self.set_right_grip_open()
            self.set_right_turn_0()
            self.set_right_grip_closed()
        if (self.lt_pos == T_POS_0):
            # The gripper must be repositioned because it can't turn
            # 180 degrees.
            self.set_left_grip_open()
            self.set_left_turn_m90()
            self.set_left_grip_closed()
        if (self.lt_pos == T_POS_P90):
            self.set_left_turn_m90()
        else:
            self.set_left_turn_90()


    # Calibrate a single servo
    #
    # Inputs:
    #   name        The servo name to be displayed to the user
    #   servo       The servo to be tuned
    #   val         The current calibration values being adjusted
    #   display     The display controller class
    #   btn_q       The queue used to get button press events
    # Returns: The new calibration value
    #
    def servo_cal(self, name, servo, val, display, btn_q):
        display.write_body(name+" "+str(val))
        self.set_pwm_value(servo, val)

        while 1:
            # Wait for a button event
            button_press = btn_q.get()

            if (button_press == UP_BUTTON):
                # Increase the PWM value
                val += 1
                if (val > self.pwm_max):
                    val = self.pwm_max
                self.set_pwm_value(servo, val)
                display.write_body(name+" "+str(val))
            elif (button_press == DOWN_BUTTON):
                # Decrease the PWM value
                val -= 1
                if (val < self.pwm_min):
                    val = self.pwm_min
                self.set_pwm_value(servo, val)
                display.write_body(name+" "+str(val))
            elif (button_press == ENTER_BUTTON):
                break
            else:
                display.write_body("Error")

        return val

    # Calibrate all servos
    #
    # This calibration function is only intended to be used for small
    # adjustment, not for full calibration of all serrvos.
    # The adjustments are done in increment of one PWM controller count,
    # full calibratin of all servos would require hundreds of button presses.
    # It is expected that initial calibration of the device is done using
    # the pwm_test.py code to find the servo settings which will be manually
    # entered into the calibration file.
    #
    # Inputs:
    #   display         The display controller class
    #   btn_q           The queue used to get button press events
    #
    def calibration(self, display, btn_q):
        display.write_header("Calibration")

        # Adjust all the calibration values for the Right Turn servo
        self.rt_cal_m90 = self.servo_cal("RTM90", self.rt, self.rt_cal_m90, \
                                         display, btn_q)
        self.rt_cal_0 = self.servo_cal("RT0", self.rt, self.rt_cal_0, \
                                       display, btn_q)
        self.rt_cal_90 = self.servo_cal("RT90", self.rt, self.rt_cal_90, \
                                        display, btn_q)
        self.set_pwm_value(self.rt, self.rt_cal_0)

        # Adjust all the calibration values for the Right Grip servo
        self.rg_cal_close = self.servo_cal("RGC", self.rg, self.rg_cal_close, \
                                           display, btn_q)
        self.rg_cal_open = self.servo_cal("RGO", self.rg, self.rg_cal_open, \
                                          display, btn_q)
        self.rg_cal_load = self.servo_cal("RGR", self.rg, self.rg_cal_load, \
                                          display, btn_q)
        self.set_pwm_value(self.rg, self.rg_cal_open)

        # Adjust all the calibration values for the Left Turn servo
        self.lt_cal_m90 = self.servo_cal("LTM90", self.lt, self.lt_cal_m90, \
                                         display, btn_q)
        self.lt_cal_0 = self.servo_cal("LT0", self.lt, self.lt_cal_0, \
                                       display, btn_q)
        self.lt_cal_90 = self.servo_cal("LT90", self.lt, self.lt_cal_90, \
                                        display, btn_q)
        self.set_pwm_value(self.lt, self.lt_cal_0)

        # Adjust all the calibration values for the Left Grip servo
        self.lg_cal_close = self.servo_cal("LGC", self.lg, self.lg_cal_close, \
                                           display, btn_q)
        self.lg_cal_open = self.servo_cal("LGO", self.lg, self.lg_cal_open, \
                                          display, btn_q)
        self.lg_cal_load = self.servo_cal("LGR", self.lg, self.lg_cal_load, \
                                          display, btn_q)
        self.set_pwm_value(self.lg, self.lg_cal_open)

        # Save the new calibration values
        f=open(self.cal_file,'w+')
        # Write the new calibration values
        f.write(str(self.pwm_freq) + " PWM frequency\n")
        f.write(str(self.pwm_min) + " PWM count minimum\n")
        f.write(str(self.pwm_max) + " PWM count maximum\n")
        f.write(str(self.rg) + " Right Grip PWM port\n")
        f.write(str(self.rt) + " Right Turn PWM port\n")
        f.write(str(self.lg) + " Left Grip PWM port\n")
        f.write(str(self.lt) + " Left Turn PWM port\n")
        f.write(str(self.rt_cal_m90) + " Right turn minus 90 degrees\n")
        f.write(str(self.rt_cal_0) + " Right turn 0 degrees\n")
        f.write(str(self.rt_cal_90) + " Right turn 90 degrees\n")
        f.write(str(self.rg_cal_close) + " Right grip closed\n")
        f.write(str(self.rg_cal_open) + " Right grip open\n")
        f.write(str(self.rg_cal_load) + " Right grip cube load\n")
        f.write(str(self.lt_cal_m90) + " Left turn minus 90 degrees\n")
        f.write(str(self.lt_cal_0) + " Left turn 0 degrees\n")
        f.write(str(self.lt_cal_90) + " Left turn 90 degrees\n")
        f.write(str(self.lg_cal_close) + " Left grip closed\n")
        f.write(str(self.lg_cal_open) + " Left grip open\n")
        f.write(str(self.lg_cal_load) + " Left grip cube load\n")
        f.close()
