"""
controllerprocessors > keys.py

This script handles initialisation and some event handling specific to certain devices

Author: Miguel Guthridge [hdsq@outlook.com.au]
"""

import eventconsts
import internal
import internal.consts

import controllerprocessors.key_25 as k25
import controllerprocessors.key_49 as k49
import controllerprocessors.key_61 as k61

def process(command):
    """Process event based on number of keys in device

    Args:
        command (ParsedEvent): Event to process
    """
    if internal.state.DEVICE_TYPE == internal.consts.DEVICE_KEYS_25:
        k25.process(command)
    
    if internal.state.DEVICE_TYPE == internal.consts.DEVICE_KEYS_49:
        k49.process(command)
        
    if internal.state.DEVICE_TYPE == internal.consts.DEVICE_KEYS_61:
        k61.process(command)

def onInit():
    """Initialise keys
    """
    if internal.state.DEVICE_TYPE == internal.consts.DEVICE_KEYS_25:
        k25.onInit()
    
    if internal.state.DEVICE_TYPE == internal.consts.DEVICE_KEYS_49:
        k49.onInit()
        
    if internal.state.DEVICE_TYPE == internal.consts.DEVICE_KEYS_61:
        k61.onInit()
