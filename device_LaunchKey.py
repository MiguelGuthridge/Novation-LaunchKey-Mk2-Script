# name=LaunchKey Mk2
# url=https://forum.image-line.com/viewtopic.php?f=1994&t=231871
# receiveFrom=LaunchKey Mk2 Extension

"""
device_LaunchKey.py

This file is the controller file for port 1 of the LaunchKey Mk2.
It handles most note and controller events.

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

import config
import internal
import eventprocessor
import internal.consts
import processorhelpers


# device.dispatch(2, 0x9F + (0x0C << 8) + (0x00 << 16))

class TGeneric():
    def __init__(self):
        return

    def OnInit(self):
        
        try:
            if internal.state.SHARED_INIT_STATE is internal.consts.INIT_INCOMPLETE:
                # Run shared init functions
                internal.sharedInit()
        except Exception as e:
            internal.errors.triggerError(e)
        
        print('Initialisation complete')
        print(internal.getLineBreak())
        print(internal.getLineBreak())
        print("")
        print("")



    def OnDeInit(self):
        print('Deinitialisation complete')

    def OnMidiIn(self, event):
        event.handled = False
        internal.performance.eventClock.start()
        
        
        # Process the event into ParsedEvent format
        command = processorhelpers.ParsedEvent(event)
        
        # Print event before processing
        internal.printCommand(command)

        # Process event
        eventprocessor.processBasic(command)
        
        # If command was edited, update event object
        if command.edited:
            event.status = command.status
            event.data1 = command.note
            event.data2 = command.value
        
        if command.handled:
            event.handled = True
        
        internal.performance.eventClock.stop()

        # Print output
        internal.printCommandOutput(command)
    
    def OnIdle(self):
        internal.idleProcessor()
        
        if internal.shifts["MAIN"].query():
            internal.state.idleShift()
    
    def OnUpdateBeatIndicator(self, beat):
        eventprocessor.beatChange(beat)
        


Generic = TGeneric()

def OnInit():
    Generic.OnInit()

def OnDeInit():
    Generic.OnDeInit()

def OnMidiIn(event):
    Generic.OnMidiIn(event)

def OnIdle():
    Generic.OnIdle()
    
def OnUpdateBeatIndicator(beat):
    Generic.OnUpdateBeatIndicator(beat)
