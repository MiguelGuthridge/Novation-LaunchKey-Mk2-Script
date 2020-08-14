"""
otherprocessors > processfirst_basic.py
This file processes events before anything else when basic mode is active.

Author: Miguel Guthridge
"""

import transport
import ui
import general

import config
import internalconstants
import eventprocessor
import eventconsts
import internal
import lighting



def process(command):

    command.actions.addProcessor("Primary Processor")

    if command.id == eventconsts.PITCH_BEND:
        internal.state.pitchBend.setVal(command.value)
        if internal.shift.getDown():
            pitch_val = internal.state.pitchBend.getParsedVal()
            increase = internal.state.pitchBend.getDirection()
            
            if pitch_val > 0 and increase == 1:
                direction = 1
            elif pitch_val < 0 and increase == -1:
                direction = -1
            else:
                direction = 0
            ui.jog(direction)
            command.handle("Pitch bend jog wheel")

    # Forward onto main processor for lighting
    if command.type == eventconsts.TYPE_BASIC_PAD:
        internal.sendInternalMidiMessage(command.status, command.note, command.value)
        command.actions.appendAction("Forward to extended script processor")
    
    # Add did not handle flag if not handled
    if command.handled is False: 
        command.actions.appendAction("[Did not handle]")

