"""
noteprocessors > default.py
This script processes notes nomally.

Author: Miguel Guthridge [hdsq@outlook.com.au]
"""

import internal.consts
import eventconsts
import internal
import processorhelpers
import lightingconsts

NAME = internal.consts.NOTE_STATE_NORMAL

COLOUR = lightingconsts.colours["WHITE"]
DEFAULT_COLOUR = lightingconsts.colours["DARK GREY"]

SILENT = False

FORWARD_NOTES = False

INIT_COMPLETE = True

def process(command):
    """
    command.actions.addProcessor("Default Note Handler")
    
    if not command.is_lift:
        
        note = processorhelpers.ExtensibleNote(command, [])
        
        internal.notesDown.noteOn(note)
        
        command.handle("Note on")
        
    else:
        internal.notesDown.noteOff(command)
        command.handle("Note off")
    """
    pass

def redraw(lights):
    pass

def activeStart():
    pass

def activeEnd():
    pass

def beatChange(beat):
    pass
