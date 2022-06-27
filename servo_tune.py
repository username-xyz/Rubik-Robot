#!/usr/bin/python


# Import I2C pins.
import board
import busio

# Needed for file I/O functions
import os

from time import sleep

# I2C bus
i2c = busio.I2C(board.SCL, board.SDA)


# Library to control the PCA9685 PWM board that drives the servos
from adafruit_pca9685 import PCA9685
pca = PCA9685(i2c)


# Servo calibration file name
cal_file = "servo_tune.txt"


# These need to be global
pwm_min = 0
pwm_max = 512


# Read a value from the servo tune file
#
# Input:
#   fh      file handle to the open tune values file
#
def read_tune_val(self, fh):
    tune_line  = fh.readline()
    tune_spilt = tune_line.split(" ")
    val = int(tune_spilt[0])
    if (val < self.pwm_min):
        val = self.pwm_min
    if (val > self.pwm_max):
        val = self.pwm_max
    return val


# Tune a single position of a single servo
#
# Inputs:
#   pwm_port        The PWN port that drives the servo being tuned
#   pwm_value       The initial pwm count
#
def tune_servo(pwm_port, pwm_value):
    global pwm_min, pwm_max

    done = 0
    while (done == 0):
        print ("Enter new pwm value (or 0 to tune the next servo)")
        tmp_value = int(input())
        if (tmp_value == 0):
            done = 1
        else:
            pwm_value = tmp_value
            if (pwm_value > pwm_max):
                pwm_value = pwm_max
            if (pwm_value < pwm_min):
                pwm_value = pwm_min
            print("Value " + str(pwm_value))

            pca.channels[pwm_port].duty_cycle = pwm_value << 4

    return pwm_value


# Read the calibration file
# Each line in the file has a single calibration number.
# The number can optionally be followed by a space and a text comment.
# The comments are ignored by the code, they are just to identify
# the values if the file is manually edited.
#
try:
    # Read the saved calibration values
    f = open(self.cal_file, 'r')
    pwm_freq = read_tune_val(f)
    pwm_min = read_tune_val(f)
    pwm_max = read_tune_val(f)
    rt_pwm = read_tune_val(f)
    rg_pwm = read_tune_val(f)
    lt_pwm = read_tune_val(f)
    lg_pwm = read_tune_val(f)
    rt_cal_m90 = read_tune_val(f)
    rt_cal_0   = read_tune_val(f)
    rt_cal_90  = read_tune_val(f)
    rg_cal_close = read_tune_val(f)
    rg_cal_open = read_tune_val(f)
    rg_cal_load = read_tune_val(f)
    lt_cal_m90 = read_tune_val(f)
    lt_cal_0 = read_tune_val(f)
    lt_cal_90 = read_tune_val(f)
    lg_cal_close = read_tune_val(f)
    lg_cal_open = read_tune_val(f)
    lg_cal_load = read_tune_val(f)
    f.close()

except:
    # Couldn't read an existing calibration file
    print("No existing calibration file")

    # Ask the user for the PWM frequency
    print ("PWM frequency")
    pwm_freq = int(input())

    # Ask the user for the minumum and maximum PWM counts
    print ("PWM minimum count")
    pwm_min = int(input())
    print ("PWM maximum count")
    pwm_max = int(input())

    # Ask the user for the servo port numbers
    print ("PWM port number on the Right Grip servo")
    rg_pwm = int(input())
    print ("PWM port number on the Right Turn servo")
    rt_pwm = int(input())
    print ("PWM port number on the Left Grip servo")
    lg_pwm = int(input())
    print ("PWM port number on the Left Turn servo")
    lt_pwm = int(input())

    # Set PWM count default values to the middle of the valid range
    pwm_mid = int(((pwm_min + pwm_max) / 2) + 0.5)
    rt_cal_m90   = pwm_mid
    rt_cal_0     = pwm_mid
    rt_cal_90    = pwm_mid
    rg_cal_close = pwm_mid
    rg_cal_open  = pwm_mid
    rg_cal_load  = pwm_mid
    lt_cal_m90   = pwm_mid
    lt_cal_0     = pwm_mid
    lt_cal_90    = pwm_mid
    lg_cal_close = pwm_mid
    lg_cal_open  = pwm_mid
    lg_cal_load  = pwm_mid
else:
    print("Calibration file read")

# Set the frequency for all PWM outputs
pca.frequency = pwm_freq

print ("Tune the -90 position of the Right Turn servo")
rt_cal_m90 = tune_servo(rt_pwm, rt_cal_m90)

print ("Tune the 0 degree position of the Right Turn servo")
rt_cal_0 = tune_servo(rt_pwm, rt_cal_0)

print ("Tune the 90 degree position of the Right Turn servo")
rt_cal_90 = tune_servo(rt_pwm, rt_cal_90)

# Set the right gripper to horizontal before adjusting the grip settings
pca.channels[rt_pwm].duty_cycle = rt_cal_0 << 4

print ("Tune the closed position of the Right Grip servo")
rg_cal_close = tune_servo(rg_pwm, rg_cal_close)

print ("Tune the cube load position of the Right Grip servo")
rg_cal_load = tune_servo(rg_pwm, rg_cal_load)

print ("Tune the open position of the Right Grip servo")
rg_cal_open = tune_servo(rg_pwm, rg_cal_open)

print ("Tune the -90 position of the Left Turn servo")
lt_cal_m90 = tune_servo(lt_pwm, lt_cal_m90)

print ("Tune the 0 degree position of the Left Turn servo")
lt_cal_0 = tune_servo(lt_pwm, lt_cal_0)

print ("Tune the 90 degree position of the Left Turn servo")
lt_cal_90 = tune_servo(lt_pwm, lt_cal_90)

# Set the left gripper to horizontal before adjusting the grip settings
pca.channels[lt_pwm].duty_cycle = lt_cal_0 << 4

print ("Tune the closed position of the Left Grip servo")
lg_cal_close = tune_servo(lg_pwm, lg_cal_close)

print ("Tune the cube load position of the Left Grip servo")
lg_cal_load = tune_servo(lg_pwm, lg_cal_load)

print ("Tune the open position of the Left Grip servo")
lg_cal_open = tune_servo(lg_pwm, lg_cal_open)


# Save the new calibration values
print ("Writing the tune file")
f=open(cal_file,'w+')
# Write the new calibration values
f.write(str(pwm_freq) + " PWM frequency\n")
f.write(str(pwm_min) + " PWM count minimum\n")
f.write(str(pwm_max) + " PWM count maximum\n")
f.write(str(rg_pwm) + " Right Grip PWM port\n")
f.write(str(rt_pwm) + " Right Turn PWM port\n")
f.write(str(lg_pwm) + " Left Grip PWM port\n")
f.write(str(lt_pwm) + " Left Turn PWM port\n")
f.write(str(rt_cal_m90) + " Right turn minus 90 degrees\n")
f.write(str(rt_cal_0) + " Right turn 0 degrees\n")
f.write(str(rt_cal_90) + " Right turn 90 degrees\n")
f.write(str(rg_cal_close) + " Right grip closed\n")
f.write(str(rg_cal_open) + " Right grip open\n")
f.write(str(rg_cal_load) + " Right grip cube load\n")
f.write(str(lt_cal_m90) + " Left turn minus 90 degrees\n")
f.write(str(lt_cal_0) + " Left turn 0 degrees\n")
f.write(str(lt_cal_90) + " Left turn 90 degrees\n")
f.write(str(lg_cal_close) + " Left grip closed\n")
f.write(str(lg_cal_open) + " Left grip open\n")
f.write(str(lg_cal_load) + " Left grip cube load\n")
f.close()
