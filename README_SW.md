#Software Information

##Downloaded Software

###Raspberry PI OS

The Raspberry Pi operating system imager is downloaded from:
[Raspberry Pi Imager](https://www.raspberrypi.com/software/)
Install the Raspberry Pi OS (32-bit).
I suggest that you go into the advanced options when configuring the imager
and configure the following:
- Enable SSH
- Set username and password
- Configure wireless LAN (including country)

This will allow you to log into the board by SSH over WiFi without needing
a display and keyboard connected to the Raspberry Pi. This can be quite
useful.

After the Raspberry Pi powers up run **sudo raspi-config** in a terminal
window and configure:
Interface Options -> Legacy Camera -> Yes
Interface Options -> I2C -> YES

###Adafruit Libraries

Some libraries from Adafruit are used to control the display and PWM module.
These are installed with:
sudo pip3 install adafruit-circuitpython-ssd1306
sudo pip3 install adafruit-circuitpython-pca9685

Information on the above libraries can be found at:
[Adafruit_CircuitPython_SSD1306](https://github.com/adafruit/Adafruit_CircuitPython_SSD1306)
[Adafruit_CircuitPython_PCA9685](https://github.com/adafruit/Adafruit_CircuitPython_PCA9685)

###Rubik's Cube Solver Library

The Rubik's Cube solver library is used to determine the necessary steps to
solve the cube based an description of the colors of each square on the faces. 
It installed with:
sudo pip install RubikTwoPhase

Information on the cube solver library is available from:
[RubiksCube-TwophaseSolver](https://github.com/hkociemba/RubiksCube-TwophaseSolver)

###Python Imaging Library

The Python Imaging Library (PIL) is need for writing text on the display and
reading pixels from the camera images.
This is installed with:
sudo apt-get install python3-pil

The display fonts were downloaded from:
[Fonts](https://www.dafont.com/bitmap.php)


###My Software

I examined the software from:
[Rubik_solver](https://github.com/DrVoHo/Rubik_solver)
before beginning to write my own software. I used a few ideas from this code in
my own code and want to give credit. However, I didn't directly copy this code
but wrote it all new.

I didn't support all the features of the original code because I'm only
really interested in solving scrambled cubes.

All the python files here need to be copied into the home directory on the
Raspberry Pi board. In addition, the font files (*.ttf) and the rubik.sh file
should also be copied to the home directory.

It is also necessary to edit the /etc/rc.local file on the Raspberry Pi.
The following line should be added as the 2nd last line of the file:
'sudo -H -u pi /usr/bin/sh /home/pi/rubik.sh &'
This will auto start the program at boot up.
**Important** You should verify that everything working correctly by running the
program manually before making this edit. If the program crashes you can get
into a state when the board can't boot because it auto runs and then crashes
at every power up.

##Software description

###Design Decisions

Raspberry Pi GPIO pins can be specified by header pin numbers or by GPIO
numbers. I chose to use GPIO pin numbers. It doesn't make any real difference
to how the code operates, but it's important that the software configuration
uses the correct numbers.

For programming the servos I chose to store the raw PWM count values for each
position of each servo. Since there are only a total of 12 values needed it
wasn't worth writing an algorithm to calculate the vales based on the desired
servo position.

The PWM count values range from 0 (minimum on time) to 4095 (maximum on time),
but depending on the type servos used only a portion of that range will be valid.

In the code I chose to describe servo rotation angles with 0 degrees being the
center of the servo range. Counterclockwise rotation is negative and clockwise
rotation is positive. Angles are always relative to the servo and not the
Rubik's cube. A clockwise servo rotation will rotate the cube counterclockwise.

###Servo Testing

There is a **servo_set.py** program included that can be used to test the
servos. The program expects 2 command line parameters, a servo port number
and a PWM count value. It will program the specified servo.

This is useful during hardware assembly to make sure the gripper is put
together correctly and has the full range of motion available.

###Servo Tuning

Before running the software the first time it is necessary to tune the servos.
The **servo_tune.py** program was created to do this. This is a command line
program to be run in a terminal window.

When the program is run it first asks for the PWM frequency. The servo
specifications should have this value.

It then asks for the port numbers on the PCA9685 that are used for each servo.

The program will then go through each servo and tune each position used for
that servo.

Turn servos that rotate the grippers have three positions:
- Minus 90 degrees (rotated counterclockwise)
- 0 degrees (horizontal)
- 90 degrees (rotated clockwise)

Gripper servos that grab the cube also have three positions:
- Open (fully open such that the opposite gripper can freely rotate the cube)
- Load (almost closed, enough space to insert or remove the cube)
- Closed (a firm grip on the cube)

For tuning each value you can type a PWN setting and the servo being tuned will
be programmed with that value. Keep adjusting the value until the servo is in
the correct position. Once the value is correct enter **0** to save the value
and start tuning the next servo.

Once all servos are tuned all the values are written to a file named
**servo_tune.txt**. This file will be read by the cube solver software and used
when programming the servos.

###Running the code

If the rc.local auto start method isn't used, the program can be run manually
in a terminal with **python rubik.py".

As the program boots you will see **Init** in the display.

**Important** The first time you run the program the RubikTwoPhase library
needs to create a lot of files that it will use when solving the cube.
This process will take over an hour, so just let it run until it finishes.
Once the files have been created later startups are much faster.

Once the initialization has finished you will see the Main Menu in the display.
The Up and Down arrow buttons can be used to scroll through the menu options
and the Right arrow (Enter) button will select an option to run.

**The Menu options are:**
- Solve
- Quit
- Calibrate

####Solve

Solve will solve a scrambled cube. First it will ask that a cube be loaded.
Press Enter again when the cube is loaded properly. The robot will then scan
the cube to determine the color pattern, then solve the cube.

If there is an error during scanning there can be a **Scan Error** message.
Press Enter to clear the error.

When the cube is solved the display will show **Done**. Press Enter to clear
the message and return to the Main Menu.

When the grippers are being used to solve the cube any of the three buttons
can be used to abort the operation. This can be needed if the cube slips in
the grippers and the robot needs to be stopped.

####Quit

Quit will exit the program.

If The **rubik.sh** shell script was used to start the program then a **halt**
command will be executed when the program exits. This will shut down the
Raspberry Pi so that power can be safely removed. Just pulling power from a
running processor is a bad idea.

####Calibrate

Calibrate allows adjustment of the saved servo tuning values.

It will go through all the values one at a time and allow adjustment using the
Up and Down arrow buttons. The Enter button moves to the next value.

This is useful for just doing small adjustments to values previously set with
the **servo_tune.py** program.
The calibrate code assumes the **servo_tune.txt** file already exists.
Doing a full calibration using the buttons isn't practical because it would
require hundreds of button presses.
