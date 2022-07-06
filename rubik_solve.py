#!/usr/bin/python

# This file contains the code that manipulates the cube to solve it.


import my_exceptions

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


    # List the faces that are reachable by a simple cube turn
    # based on the face currently held in the gripper.
    # The faces are listed in clockwise order.
    #
    # Input:
    #   face            The face heldin the gripper
    #
    # Return:
    #   A list of 4 faces
    #
    def get_faces(self, face):
        if (face == 'U'):
            return ['L', 'B', 'R', 'F']
        elif (face == 'L'):
            return ['F', 'D', 'B', 'U']
        elif (face == 'F'):
            return ['L', 'U', 'R', 'D']
        elif (face == 'R'):
            return ['F', 'U', 'B', 'D']
        elif (face == 'B'):
            return ['L', 'D', 'R', 'U']
        else: # face == 'D'
            return ['L', 'F', 'R', 'B']


    # Rotate the face held in the right gripper
    #
    # Input:
    #   turn            The amount of rotation needed
    #
    def rotate_face_right_grip(self, turn):
        if (turn == 1):
            if(DEBUG == 1):
                print("Right rotate face ccw")
            self.servos.right_rotate_face_90_ccw()
        elif(turn == 2):
             if(DEBUG == 1):
                 print("Right rotate face 180")
             self.servos.right_rotate_face_180()
        else: # turn == 3
             if(DEBUG == 1):
                 print("Right rotate face cw")
             self.servos.right_rotate_face_90_cw()


    # Rotate the face held in the left gripper
    #
    # Input:
    #   turn            The amount of rotation needed
    #
    def rotate_face_left_grip(self, turn):
        if (turn == 1):
            if(DEBUG == 1):
                print("Left rotate face ccw")
            self.servos.left_rotate_face_90_ccw()
        elif(turn == 2):
             if(DEBUG == 1):
                 print("Left rotate face 180")
             self.servos.left_rotate_face_180()
        else: # turn == 3
             if(DEBUG == 1):
                 print("Left rotate face cw")
             self.servos.left_rotate_face_90_cw()


    # Rotate the entire cube using the right gripper
    #
    # Input:
    #   turn            The amount of rotation needed
    #
    def rotate_cube_right_grip(self, turn):
        if (turn == 1):
            if(DEBUG == 1):
                print("Right rotate cube cw")
            self.servos.right_rotate_cube_90_cw()
        elif (turn == 2):
            if(DEBUG == 1):
                print("Right rotate cube 180")
            self.servos.right_rotate_cube_180()
        else: # turn == 3
            if(DEBUG == 1):
                print("Right rotate cube ccw")
            self.servos.right_rotate_cube_90_ccw()


    # Rotate the entire cube using the left gripper
    #
    # Input:
    #   turn            The amount of rotation needed
    #
    def rotate_cube_left_grip(self, turn):
        if (turn == 1):
            if(DEBUG == 1):
                print("Left rotate cube cw")
            self.servos.left_rotate_cube_90_cw()
        elif (turn == 2):
            if(DEBUG == 1):
                print("Left rotate cube 180")
            self.servos.left_rotate_cube_180()
        else: # turn == 3
            if(DEBUG == 1):
                print("Left rotate cube ccw")
            self.servos.left_rotate_cube_90_ccw()


    # Determine the cube rotation needed to put a face into a gripper
    #
    # Inputs:
    #   face_now        The face currently in the gripper
    #   next_face       The desired face
    #   face_list       A list of 4 faces that are reachable by rotation
    #
    # Return:
    # -1 if the next face isn't available.
    # 0, 1, 2 or 3 if the new face is found. The value indicates how much
    # the cube must be rotated to get to the new face.
    #
    def find_face(self, face_now, next_face, face_list):
        try:
            delta = face_list.index(next_face) - \
                    face_list.index(face_now)
            if (delta < 0):
                delta +=4
        except:
            delta = -1
        finally:
            return delta


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
        self.faces_l = self.get_faces(self.current_l)
        self.current_r = 'F'
        self.faces_r = self.get_faces(self.current_r)

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

            # Check if the right gripper already holds the correct face
            if (next_face == self.current_r):
                self.rotate_face_right_grip(next_turn)

            # Check if the left gripper already holds the correct face
            elif (next_face == self.current_l):
                self.rotate_face_left_grip(next_turn)

            else: # Need to rotate the cube to get the correct face

                # Check if rotating the left gripper will put the
                # desired face into the right gripper.

                delta = self.find_face(self.current_r, next_face, self.faces_l)

                if (delta == 0):
                    if(DEBUG == 1):
                        print ("Error finding face left")
                    # Should never get here
                    raise FaceException('Error finding face')

                if (delta != -1):
                    # Rotate the entire cube in the left gripper
                    self.rotate_cube_left_grip(delta)
                    self.current_r = next_face
                    self.faces_r = self.get_faces(self.current_r)

                    # Rotate the face using the right gripper
                    self.rotate_face_right_grip(next_turn)

                else:
                    # Check if rotating the right gripper will put the
                    # desired face into the left gripper.

                    delta = self.find_face(self.current_l, next_face, \
                                           self.faces_r)
                    if ((delta == 0) or (delta == -1)):
                        if(DEBUG == 1):
                            print ("Error finding face right " + str(delta))
                        # Should never get here
                        raise FaceException('Error finding face')

                    # Rotate the entire cube in the right gripper
                    self.rotate_cube_right_grip(delta)
                    self.current_l, = next_face
                    self.faces_l = self.get_faces(self.current_l)

                    # Rotate the face using the left gripper
                    self.rotate_face_left_grip(next_turn)

            if(DEBUG == 1):
                print("")
                print("Current Left " + self.current_l)
                print("Current Right " + self.current_r)
                print("")
