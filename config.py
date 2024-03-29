"""
config.py

This file contains variables intended for the user to edit to suit their needs.
All these variables should be safe to edit, but if things break, you might want to revert your changes.
Consider making a backup of this file before editing it.

Author: Miguel Guthridge [hdsq@outlook.com.au]
"""
import eventconsts
from internal.consts import DEBUG

#-------------------------------
# CONFIGURATION OPTIONS
#-------------------------------

# Setup options
#-----------------------

# Check for updates online. Change to False if you don't want to be notified or something
CHECK_UPDATES = True
# THIS DOESN'T WORK YET :(

# Port values. Change these to match the ports for each device set in FL Studio
DEVICE_PORT_BASIC = 220
DEVICE_PORT_EXTENDED = 225


# Interaction options
#-----------------------

LONG_PRESS_TIME = 1.0 # Change how long a long press needs to be held for
DOUBLE_PRESS_TIME = 0.2 # Change how quickly a double press needs to be done to be detected

# If enabled, double pressing shift key keeps the shift button enabled until it is used, or pressed again.
ENABLE_SUSTAINED_SHIFT = True
# If enabled, sustained shifts will automatically lift when you press a button.
AUTOCANCEL_SUSTAINED_SHIFT = False

# Determines the navigation speed using the pitch bend wheel in the shift menu
PITCH_BEND_JOG_SPEED = 0.05

# Whether the script should automatically set the incontrol mode when changing windows
AUTO_SET_INCONTROL_MODE = True

# These values determine whether the controller will start with inControl modes enabled for each type
START_IN_INCONTROL_KNOBS = True
START_IN_INCONTROL_FADERS = True
START_IN_INCONTROL_PADS = True


# Parameter options
#-----------------------

ENABLE_SNAPPING = True # Change to False to prevent faders and knobs from snapping to default values
SNAP_RANGE = 0.05 # Will snap if within this disatnce of snap value

# Plugin options
#-----------------------

# If a plugin handler uses keyswitches, this controls whether the entire dum pad is used for key switches.
# This may be used to add a split rows option for the drum pad later.
USE_FULL_KEYSWITCHES = True

# Whether to force full velocity drum pads in omni-mode and FPC
DRUM_PADS_FULL_VELOCITY = False

#-------------------------------
# LIGHTING OPTIONS
#-------------------------------

# Enable idle light show
IDLE_LIGHTS_ENABLED = True
# Time to wait before entering idle light show = 1156 * number of minutes
IDLE_WAIT_TIME = 1156 * 5

# Controls the frequency at which the script executes a full redraw (to fix dud lights)
LIGHTS_FULL_REDRAW_FREQUENCY = 5
# If enabled, animations will be disabled
LIGHTS_REDUCE_MOTION = False


#-------------------------------
# DEBUGGING OPTIONS
#-------------------------------

# For fun when the script crashes
CHAOTIC_EVIL_ERROR_NOTE_HANDLER = False

# Controls which console messages are printed. Add things from the DEBUG object
CONSOLE_DEBUG_MODE = []

# Whether script should stop entirely when it encounters an error.
DEBUG_HARD_CRASHING = False
