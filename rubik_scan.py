#!/usr/bin/python

#
# The code in this file takes images of all sides of a Rubik's cube
# and analyzes the images to determine the color pattern on the cube.
#


# Needed for file access and math functions
import os, math

from time import sleep

# Needed for reading pixel values from images
from PIL import Image

# Raspberry Pi camera library
from picamera import PiCamera

# Display controller class
from rubik_display import RubikDisplay


# The image size for my camera
IMG_WIDTH = 3280
IMG_HIGHT = 2464


# Set this to 0 to disable debug logging, 1 to enable.
DEBUG = 0


# Pixel locations of the centers of the 9 squares on the side of rubiks cube.
# These are used to determine the colors of each square.
#
LEFT_COLUMN  = 1000 # X coordinates of the columns
MID_COLUMN   = 1580
RIGHT_COLUMN = 2160
TOP_ROW      =  500 # Y coordinates of the rows
MID_ROW      = 1100
BOTTOM_ROW   = 1700


# Rubic cube scanner class
#
# Input:
#   serv        The servo controller class
#
class RubikScan(object):
    def __init__(self, serv):
        # Save the servo info provided by the caller
        self.servos = serv

        # These are the pixel locations for the center of the 9 colored squares
        # on a cube face that is oriented right side up.
        # The order of the locations matches the order expected by the rubik
        # solver code.
        self.pxl_locs = [(LEFT_COLUMN,  TOP_ROW),
                         (MID_COLUMN,   TOP_ROW),
                         (RIGHT_COLUMN, TOP_ROW),
                         (LEFT_COLUMN,  MID_ROW),
                         (MID_COLUMN,   MID_ROW),
                         (RIGHT_COLUMN, MID_ROW),
                         (LEFT_COLUMN,  BOTTOM_ROW),
                         (MID_COLUMN,   BOTTOM_ROW),
                         (RIGHT_COLUMN, BOTTOM_ROW)]

        # Make sure the cube image directory exists
        if not os.path.exists("Cube"):
            os.makedirs("Cube")
            os.chmod("Cube", 0o777)


    # Initialize the camera
    #
    def camera_init(self):
        # Initialize the camera driver and hardware
        self.camera = PiCamera()
        self.camera.resolution = (IMG_WIDTH, IMG_HIGHT)
        self.camera.start_preview()
        self.camera.iso = 400


    # Read cube faces
    #
    # The cube solver code expects the faces in the following order:
    #   0 = Up
    #   1 = Right
    #   2 = Front
    #   3 = Down
    #   4 = Left
    #   5 = Back
    #
    # The faces are imaged out of order to reduce the necessary gripper
    # movements. In addition, the Down face will be imaged upside down.
    #
    def get_cube(self, display):
        # Set the camera exposure settings.
        # Using fixed settings rather than auto exposure produces more
        # consistant colors from image to image. This make the color
        # detection more reliable.
        es = self.camera.exposure_speed
        self.camera.exposure_mode = 'off'
        self.camera.shutter_speed = es
        g = self.camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g

        self.camera.saturation = 50

        # Give the camera time to adjust
        sleep(2)

        display.write_body("Front")
        self.camera.capture('Cube/face2.jpg')    

        self.servos.right_rotate_cube_90_cw()
        self.servos.clear_camera()

        display.write_body("Right")
        self.camera.capture('Cube/face1.jpg')

        self.servos.right_rotate_cube_90_cw()
        self.servos.clear_camera()

        display.write_body("Back")
        self.camera.capture('Cube/face5.jpg')

        self.servos.right_rotate_cube_90_cw()
        self.servos.clear_camera()

        display.write_body("Left")
        self.camera.capture('Cube/face4.jpg')

        self.servos.left_rotate_cube_90_cw()
        self.servos.right_rotate_cube_90_cw()
        self.servos.clear_camera()

        display.write_body("Up")
        self.camera.capture('Cube/face0.jpg')

        self.servos.right_rotate_cube_180()
        self.servos.clear_camera()

        # This face will be upside down
        display.write_body("Down")
        self.camera.capture('Cube/face3.jpg')

        # Release the camera
        self.camera.close()


    # Scan and analyse the colors on a scrambled cube
    #
    # Input:
    #   display     The display contoller class
    def scan_cube(self, display):
        display.write_header("Scanning")

        # Get images for all sides of the cube.
        self.get_cube(display)

        display.write_header("Analysis")
        display.write_body(" ")

        # Determine the color of each square.
        return self.get_colors() 


    # Average the pixel colors in a 5x5 square area
    # This is used to prevent single pixel errors from messing up the
    # The color detection.
    #
    # Inputs:
    #   im          The image of the cube face to process
    #   x           The x coordinate of the center pixel of the area
    #   y           The y coordinate of the center pixel of the area
    #
    def pix_average(self, im, x, y):
        # Clear averages
        r_avg = 0
        g_avg = 0
        b_avg = 0

        # Set x and y values to the corner pixel of the averaging area
        x -= 2
        y -= 2

        # Add the RGB values of all pixels
        for x_inc in range (0,5):
            for y_inc in range (0,5):
                # Read the RGB values for a single pixel
                r_pix, g_pix, b_pix = im.getpixel((x + x_inc, y + y_inc))
                r_avg += r_pix
                g_avg += g_pix
                b_avg += b_pix

        # Divide by the number of pixels
        r_avg = r_avg / 25
        g_avg = g_avg / 25
        b_avg = b_avg / 25

        return r_avg, g_avg, b_avg


    # Get the color of the center square of a cube side.
    # This sets the correct color for the entire side since the
    # centers quares don't move when solving the cube.
    #
    # Inputs:
    #   text        Cube side name used in debug messages
    #   file        Image file for one side of the cube
    #
    def get_center_color(self, text, file):
        if(DEBUG == 1):
            print(text)
        im = Image.open(file)
        im = im.convert('RGB')
        r, g, b = self.pix_average(im, \
                                   self.pxl_locs[4][0], \
                                   self.pxl_locs[4][1])
        if(DEBUG == 1):
            print("rgb,%6.2f,%6.2f,%6.2f\n" % (r, g, b))
        return r, g, b 

    # Get the color of each square on the cube
    #
    def get_colors(self):
        # First get the center colors of each face.
        # These will set the face color for the solved cube and also
        # be used as a reference when identifying the other squares.
        center_colors = []

        r, g, b = self.get_center_color("Face 0 - Up", "Cube/face0.jpg")
        center_colors.append((r, g, b, "U"))

        r, g, b = self.get_center_color("Face 1 - Right", "Cube/face1.jpg")
        center_colors.append((r, g, b, "R"))

        r, g, b = self.get_center_color("Face 2 - Front", "Cube/face2.jpg")
        center_colors.append((r, g, b, "F"))

        r, g, b = self.get_center_color("Face 3 - Down", "Cube/face3.jpg")
        center_colors.append((r, g, b, "D"))

        r, g, b = self.get_center_color("Face 4 - Left", "Cube/face4.jpg")
        center_colors.append((r, g, b, "L"))

        r, g, b = self.get_center_color("Face 5 - Back", "Cube/face5.jpg")
        center_colors.append((r, g, b, "B"))

        # This string will be used to hold the cube definition.
        # This defines the color of all squaares on the cube.
        cube_def_string = ""

        # This array is used to keep of count of haw many squares of each
        # color are found. This will prove a check on the color matching
        # algorithm. There should be 9 squares of each color.
        color_count = [0, 0, 0, 0, 0, 0]

        # Find the color for all squares on the cube.

        # Loop through the 6 cube faces
        for img_iter in range(0, 6):
            if(DEBUG == 1):
                print("-- Face " + str(img_iter))
            img_path = "Cube/face" + str(img_iter) + ".jpg"
            im = Image.open(img_path)
            im = im.convert('RGB')

            # Loop through the 9 squares on a face
            for pix_iter in range(0,9):
                if (img_iter == 3):
                    # The Down face's image is upside down.
                    # Scan the pixels in reverse order.
                    r, g, b = self.pix_average(im, \
                                              self.pxl_locs[8 - pix_iter][0], \
                                              self.pxl_locs[8 - pix_iter][1])
                else:
                    # All other images are right side up.
                    r, g, b = self.pix_average(im, \
                                              self.pxl_locs[pix_iter][0], \
                                              self.pxl_locs[pix_iter][1])
                if(DEBUG == 1):
                    print("rgb,%6.2f,%6.2f,%6.2f" % (r, g, b))

                # Find the closest color match to the center squares
                # This just uses Euclidian distance which isn't very accurate
                # for colors, but it works well enough most of the time
                # and it's easy to implement.
                # The square root isn't done in the distance calculation
                # because we are just looking for the minimum value and don't
                # care what the actual number is.
                min_dist = -1
                face = 'X'
                for index in range(0, len(center_colors)):
                    cc_r, cc_g, cc_b, f = center_colors[index]
                    dist = math.pow(r - cc_r, 2) + math.pow(g - cc_g, 2) \
                           + math.pow(b - cc_b, 2)

                    if(DEBUG == 1):
                        print(str(dist))

                    if((min_dist == -1) or (dist < min_dist)):
                        min_dist = dist
                        face = f
                        min_index = index

                # Add the square's color to the cube definition string.
                if(DEBUG == 1):
                    print("Face " + face)
                cube_def_string = cube_def_string + face
                color_count[min_index] += 1

        print(cube_def_string)

        # Verify there are 9 squares of each color
        success = True
        for index in range(0, 6):
            if(DEBUG == 1):
                print(str(str(index)) + ": " + str(color_count[index]))
            if (color_count[index] != 9):
                success = False

        return success, cube_def_string
