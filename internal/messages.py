"""
internal > messages.py

This module contains functions to help sending messages to the device, and to other running script.

Author: Miguel Guthridge [hdsq@outlook.com.au]
"""

import device

import config
from . import consts

from .logging import debugLog, getLineBreak

def sendMidiMessage(status, data1, data2):
    """Sends a MIDI message to the controller

    Args:
        status (int): The status byte of the MIDI message
        data1 (int): The first data byte of the MIDI message
        data2 (int): The second data byte of the MIDI message
    """
    event_out  = toMidiMessage(status, data1, data2)
    str_event_out = str(status) + " " + str(data1) + " " + str(data2)
    sendCompleteMidiMessage(event_out, str_event_out)


def sendInternalMidiMessage(status, data1, data2):
    """Sends a MIDI message to the other running script associated with the device. Used for internal communication to help maintain consistent states between controllers.

    Args:
        status (int): Status byte
        data1 (int): First data byte
        data2 (int): Second data byte
    """
    event_out  = toMidiMessage(status, data1, data2)
    str_event_out = str(status) + " " + str(data1) + " " + str(data2)
    sendCompleteInternalMidiMessage(event_out, str_event_out)


def sendCompleteMidiMessage(message, str_event_out = ""):
    """Sends a MIDI message to the controller, in completed form (as one int).

    Args:
        message (int): MIDI message
        str_event_out (str, optional): What to print about the message. Defaults to "".
    """
    try:
        debugLog("Dispatched external MIDI message " + str_event_out + " (" + str(message) + ")", consts.DEBUG.DISPATCH_EVENT)
        device.midiOutMsg(message)
    except TypeError as e:
        print(getLineBreak())
        print('\n'.join([
            "An error occurred when attempting to communicate with the device.",
            "Please ensure that device input and output ports are configured correctly,",
            "then reload the script and try again."
            ]))
        raise e


def sendCompleteInternalMidiMessage(message, str_event_out = ""):
    """Sends a MIDI message to the other running script associated with the device, except in completed form (as one int). Used for internal communication to maintain states between cotntrollers.

    Args:
        message (int): MIDI message
        str_event_out (str, optional): What to print about the message. Defaults to "".
    """
    try:
        debugLog("Dispatched internal MIDI message: " + str_event_out + " (" + str(message) + ")", consts.DEBUG.DISPATCH_EVENT)
        device.dispatch(0, message)
    except TypeError as e:
        print(getLineBreak())
        print('\n'.join([
            "An error occurred when attempting to communicate with the other script port.",
            "Please ensure that device input and output ports are configured correctly,",
            "then reload the script and try again."
            ]))
        raise e


def toMidiMessage(status, data1, data2):
    """Returns a full MIDI message given status, data1 and data2 bytes

    Args:
        status (int): Status byte
        data1 (int): 1st data byte
        data2 (int): 2nd data byte

    Returns:
        int: Completed MIDI message
    """
    return status + (data1 << 8) + (data2 << 16)


def sendUniversalDeviceEnquiry():
    """Sends a universal device enquiry to the controller.
    """
    try:
        device.midiOutSysex(consts.DEVICE_ENQUIRY_MESSAGE)
    except TypeError as e:
        print(getLineBreak())
        print('\n'.join([
            "An error occurred when attempting to communicate with the device.",
            "Please ensure that device input and output ports are configured correctly,",
            "then reload the script and try again."
            ]))
        raise e
