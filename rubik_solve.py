#!/usr/bin/python

# This file contains the code that manipulates the cube to solve it.
#
# To simplify this algorithm, only a subset of the possible cube positions
# in the two grippers will be allowed.
# The left gripper will only hold the Up, Right, Down or Left faces.
# The right gripper will only hold teh Front or Back faces.
# This allows turning any face but makes tracking the cube positin easier.
# It may not produce an optimum minumum-gripper-mode solution, but it works
# reasonable well.


# Display controller class
from rubik_display import RubikDisplay

# Servo controller class
from rubik_servos import RubikServo

# Set this to 0 to disable debug logging, 1 to enable.
DEBUG = 0


# Rubic's cube solve class
#
# Inputs:
#   serv        The servo controller class
#   disp        The display controller class
#
class RubikSolve(object):
    def __init__(self, serv, disp):
        # Save the servo info provided by the caller
        self.servos = serv
        # Save the display info provided by the caller
        self.display = disp


    # Manipulate the cube to solve it.
    #
    # Inputs:
    #   display         The display class used to display user messages
    #   servos          The servo class used to controll the grippers
    #   solve_string    The sequence of moves to be done to solve the cube
    #
    # It's important to note the all clockwise and counter clockwise
    # directions in this function are referenced to the gripper and not
    # to the cube. Turning the gripper clockwise turns the cube face
    # counter clockwise.
    #
    def solve(self, display, servos, solve_string):
        display.write_header("Solving")

        # These variables will be used to track the current orientation of
        # cube in the grippers.
        # After image scanning, the left gripper holds the Up face and the
        # right gripper holds the Front face.
        self.current_l = 'U'
        self.current_r = 'F'

        # This array is used to hold the order of the faces
        # when the right gripper is rotated clockwise.
        self.faces = ['U', 'R', 'D', 'L']

        # Seperate the solution string into individual moves.
        solve_array = solve_string.split(" ")
        if (len(solve_array) == 1):
            return

        if(DEBUG == 1):
            print(" ")
            print("Current Left " + self.current_l)
            print("Current Right " + self.current_r)
            print(" ")

        # Step through each move in the solution.
        # Skip the last element because it's a count of the number of moves.
        for step in range(0, len(solve_array) - 1):
            # Parse the move command into the face and rotation parts.
            next_chars = solve_array[step]
            next_face = next_chars[0]
            next_turn = int(next_chars[1])

            # Provide a count down for the user.
            display.write_body(str(len(solve_array) - 1 - step))

            if(DEBUG == 1):
                print("Next move " + next_face + " " + str(next_turn))

            # Check for a face to be rotated by the right gripper.
            if ((next_face == 'F') or (next_face == 'B')):
                # Check if the right gripper already holds the correct face.
                if (next_face == self.current_r):
                    if(DEBUG == 1):
                        print("Left no rotation")
                else:
                    # Spin the cube around to get the correct face.
                    if(DEBUG == 1):
                        print("Left rotate cube 180")
                    servos.left_rotate_cube_180()
                    if (self.current_r == 'F'):
                        self.current_r = 'B'
                        self.faces = ['L', 'D', 'R', 'U']
                    else:
                        self.current_r = 'F'
                        self.faces = ['U', 'R', 'D', 'L']
                # Rotate the face by the requested amount.
                if (next_turn == 1):
                    if(DEBUG == 1):
                        print("Right rotate face ccw")
                    servos.right_rotate_face_90_ccw()
                elif(next_turn == 2):
                    if(DEBUG == 1):
                        print("Right rotate face 180")
                    servos.right_rotate_face_180()
                else:
                    if(DEBUG == 1):
                        print("Right rotate face cw")
                    servos.right_rotate_face_90_cw()
            else: # This face will be rotated by the left gripper
                # Calculate how much the cube needs to be rotated to
                # get the correct face in the gripper.
                delta = self.faces.index(next_face) - \
                        self.faces.index(self.current_l)
                if (delta < 0):
                    delta +=4
                if (delta == 0):
                    # Already have the correct face.
                    if(DEBUG == 1):
                        print("Right no rotation")
                else:
                    # Rotate the cube to get the correct face.
                    if (delta == 1):
                        if(DEBUG == 1):
                            print("Right rotate cube cw")
                        servos.right_rotate_cube_90_cw()
                    elif (delta == 2):
                        if(DEBUG == 1):
                            print("Right rotate cube 180")
                        servos.right_rotate_cube_180()
                    else:
                        if(DEBUG == 1):
                            print("Right rotate cube ccw")
                        servos.right_rotate_cube_90_ccw()
                    self.current_l = next_face
                # Rotate the face by the requested amount.
                if (next_turn == 1):
                    if(DEBUG == 1):
                        print("Left rotate face ccw")
                    servos.left_rotate_face_90_ccw()
                elif(next_turn == 2):
                    if(DEBUG == 1):
                        print("Left rotate face 180")
                    servos.left_rotate_face_180()
                else:
                    if(DEBUG == 1):
                        print("Left rotate face cw")
                    servos.left_rotate_face_90_cw()

            if(DEBUG == 1):
                print("")
                print("Current Left " + self.current_l)
                print("Current Right " + self.current_r)
                print("")
