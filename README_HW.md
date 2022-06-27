#Hardware Information

##3-D Printed Hardware

The mechanical parts can be 3D printed with any hobbyist printer.
The part files can be found at:
https://www.thingiverse.com/thing:3826740
https://www.thingiverse.com/thing:5183895
https://www.thingiverse.com/thing:4701388
The first contains the main design and the other two are remixes that
modify a few parts.

The other parts needed are standard screws, nuts and threaded inserts
that can be purchased many places.

##Electronic Hardware

The electronic hardware includes:
- Raspberry Pi 4 Model B
- PCA9685 16 Channel 12-Bit PWM Servo Motor Board Module
- 128 x 64 pixel SSD1306 display
- Raspberry Pi camera with cable
- 4 DS3218 servos
- 5V 5A power supply
- 3 push button switches
- Power switch
- 7cm X 3cm prototype board
- Wire
- Speed cube

The robot works much better using a speed cube rather than an original
Rubik's Cube. The original cube can jam if everything isn't perfectly
aligned. Speed cubes are designed to be more forgiving of misalignment.
Any logos printed on the cube faces will need to scraped off or covered over
so that the camera can properly detect the color.

It's really important to get a quality camera. I couldn't get the color
identification to work properly until I swapped the cheap camera for a better
quality camera. With the good camera it worked perfectly.

The servo selection is also important. I first tried using MG996R servos
and found they weren't strong enough to handle the gripper plus a cube.
When I upgraded to DS3218 servos there was a significant improvement.