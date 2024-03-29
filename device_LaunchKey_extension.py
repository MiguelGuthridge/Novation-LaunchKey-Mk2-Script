# name=LaunchKey Mk2 Extension
# url=https://forum.image-line.com/viewtopic.php?f=1994&t=231871
# receiveFrom=LaunchKey Mk2

"""
device_LaunchKey_extension.py

This file is the controller file for port 2 of the LaunchKey Mk2.
It handles communication with the device, including colours.

Author: Miguel Guthridge [hdsq@outlook.com.au]
"""


#-------------------------------
# Edit this file at your own risk. All user-modifyable variables are found in 'config.py'.
#-------------------------------

import patterns
import channels
import mixer
import device
import transport
import arrangement
import general
import launchMapPages 
import playlist
import ui
# import screen

import midi
import utils

import time

# Other project files
import config
import internal
import internal.consts
import lighting
import eventconsts
import eventprocessor
import processorhelpers



initialisation_flag = False
initialisation_flag_response = False



class TGeneric():
    def __init__(self):
        return

    def OnInit(self):

        try:
            if internal.state.SHARED_INIT_STATE is internal.consts.INIT_INCOMPLETE:
                # Run shared init functions
                internal.sharedInit()

            # Set the device into Extended Mode
            internal.extendedMode.setVal(True, force=True)

            # Process inControl preferences | Say it's external since we want the settings to be applied regardless
            if config.START_IN_INCONTROL_KNOBS == False: internal.extendedMode.setVal(False, eventconsts.INCONTROL_KNOBS, from_internal=False) 
            if config.START_IN_INCONTROL_FADERS == False: internal.extendedMode.setVal(False, eventconsts.INCONTROL_FADERS, from_internal=False) 
            if config.START_IN_INCONTROL_PADS == False: internal.extendedMode.setVal(False, eventconsts.INCONTROL_PADS, from_internal=False) 
        
        except Exception as e:
            internal.errors.triggerError(e)

        print('Initialisation complete')
        print(internal.getLineBreak())
        print(internal.getLineBreak())
        print("")
        print("")

    def OnDeInit(self):
        try:
            # Return the device into Basic Mode
            internal.extendedMode.setVal(False)
            print('Deinitialisation complete')
            print(internal.getLineBreak())
            print(internal.getLineBreak())
            print("")
            print("")
        except Exception as e:
            internal.errors.triggerError(e)
        

    def OnMidiIn(self, event):
        event.handled = False
        internal.performance.eventClock.start()
        # Update active window (ui.onRefresh() isnt working properly)
        internal.ActiveWindow = ui.getFocusedFormCaption()

        # Process the event into ParsedEvent format
        command = processorhelpers.ParsedEvent(event)

        # Print event before processing
        internal.printCommand(command)

        # Check for shift button releases (return early)
        if event.handled:
            internal.printCommandOutput(command)
            return

        # Process command
        eventprocessor.processExtended(command)

        # If command was edited, update event object
        if command.edited:
            event.status = command.status
            event.data1 = command.note
            event.data2 = command.value
            
        internal.performance.eventClock.stop()

        # Print output of command
        internal.printCommandOutput(command)
        event.handled = True
    
    def OnIdle(self):
        internal.idleProcessor()
        eventprocessor.redraw()
        # Notify standard script that an idle event has occurred
        internal.messages.sendCompleteInternalMidiMessage(internal.consts.MESSAGE_IDLE_NOTIFICATION, "Idle notification")

    def OnRefresh(self, flags):
        internal.refreshProcessor()
        
        # Prevent idle lightshow when other parts of FL are being used
        internal.window.resetIdleTick()
    
    def OnUpdateBeatIndicator(self, beat):
        eventprocessor.beatChange(beat)
        
        # Prevent idle lightshow from being triggered during playback
        internal.window.resetIdleTick()
        
    def OnSendTempMsg(self, msg, duration):
        internal.window.resetIdleTick()

Generic = TGeneric()

def OnInit():
    Generic.OnInit()

def OnDeInit():
    Generic.OnDeInit()

def OnMidiIn(event):
    Generic.OnMidiIn(event)

def OnIdle():
    Generic.OnIdle()

def OnRefresh(flags):
    Generic.OnRefresh(flags)

def OnUpdateBeatIndicator(beat):
    Generic.OnUpdateBeatIndicator(beat)

def OnSendTempMsg(msg, duration):
    Generic.OnSendTempMsg(msg, duration)
