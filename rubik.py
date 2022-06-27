#!/usr/bin/python

#
# Rubik's Cube solver control software.
#
# This file contains the top level code for the Rubik's Cube solver robot.
#
# The solver is run by executing "python rubik.py"
#
# This code will create the main user menu and execute the appropriate
# sub-functions based on the users selection.
#

import sys
import os

from time import sleep

from queue import Queue

# Display controller class
from rubik_display import RubikDisplay

# Button press detection class
from rubik_buttons import RubikButtons, UP_BUTTON, DOWN_BUTTON, ENTER_BUTTON

# Servo control class
from rubik_servos import RubikServo

# Cube color scanner class
from rubik_scan import RubikScan

# Cube solver class
from rubik_solve import RubikSolve

# Create the display class
#
# This is created here so the display can be used during initilization
# to let the user know something is happening. Importing the solver
# library can take quite a while.
#
display = RubikDisplay()
display.write_body("Init")

# This library provieds the moves needed to solve the cube.
import twophase.solver as solver


# Create the queue used to get button events
btn_q = Queue(maxsize = 8)

# Create the button class
button = RubikButtons(btn_q)
button.start()

# Create the servo controller class
try:
    servos = RubikServo(btn_q)
except:
    display.write_body("File Error")
    raise

# Create the cube scanner class
scanner = RubikScan(servos)

# Create the cube solution class
cube_solver = RubikSolve(servos, display)


#############################################
# Main menu functions
#############################################


# Solve the cube
#
def solve():
    global display

    # Initialize the camera
    scanner.camera_init()

    # Set the grippers to the load cube position
    servos.cube_load(display, btn_q)

    try:
        # Read the cube faces to get the current color arrangement
        result = scanner.scan_cube(display)
        success = result[0]
        cube_string = result[1]
        # Flush any output messages
        sys.stdout.flush()
        if (success != True):
            display.write_body("Scan Error")
            # Wait for a button press
            button_press = btn_q.get()
        else:
            # Get the moves needed to solve the cube.
            # Search a full 2 seconds for the best solution.
            solve_string = solver.solve(cube_string, 0, 2)
            print(solve_string)
            # Flush any output messages
            sys.stdout.flush()

            # Manipulate the cube to implement the solution
            cube_solver.solve(display, servos, solve_string)

            # Release the cube so it can be removed
            servos.cube_release()
            # Flush any output messages
            sys.stdout.flush()

            display.write_body("Done")
            # Wait for a button press
            button_press = btn_q.get()
    except KeyboardInterrupt:
        display.write_body("Abort")
        servos.cube_release()
    except:
        display.write_body("Error")
        servos.cube_release()
        raise


# Exit the application
#
def quit():
    global display
    display.write_header("")
    display.write_body("Exit")
    servos.cube_release()
    sys.exit(0)


# Calibrate the servos
#
def calibrate_servos():
    global display
    servos.calibration(display, btn_q)


#############################################
# Main Menu
#############################################


# Flush any startup output messages
sys.stdout.flush()

# Display the main menu header
display.write_header("Main menu")

# Main menu prompt and function array
main_menu = [("Solve",solve), \
             ("Quit", quit), \
             ("Calibrate", calibrate_servos)]
main_menu_size = len(main_menu)

# Start menu at position 0
menu_index = 0
display.write_body(main_menu[0][0])

# Get the user input to select a function
#
# The DOWN button advances to the next function
# The UP button goes back to the previous function
# The ENTER button executes the current function
#
while (1):
    # Wait for a button press
    button_press = btn_q.get()

    if (button_press == UP_BUTTON):
        if (menu_index > 0):
            menu_index -= 1
        else:
            menu_index = 0
        display.write_body(main_menu[menu_index][0])
    elif(button_press == DOWN_BUTTON):
        if (menu_index < (main_menu_size - 1)):
            menu_index += 1
        else:
            menu_index = main_menu_size - 1
        display.write_body(main_menu[menu_index][0])
    elif(button_press == ENTER_BUTTON):
        main_menu[menu_index][1]()
        menu_index = 0
        display.write_header("Main menu")
        display.write_body(main_menu[0][0])
