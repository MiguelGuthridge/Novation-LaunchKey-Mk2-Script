"""
noteprocessors > processnotes.py
This script forwards events to note processors depending on the current mode.

Author: Miguel Guthridge

"""

#
# Add custom event processors to this list
#
imports = ["default", "error"]
#
#
#

import config
import internal
import internalconstants
import noteprocessors
import processorhelpers
import eventconsts
import lightingconsts

# Import custom processors specified in list above
print("Importing Note Processors")
customProcessors = []       # Not including hidden ones
customProcessorsAll = []    # Includes hidden ones
for x in range(len(imports)):
    try:
        __import__("noteprocessors." + imports[x])
        customProcessorsAll.append(imports[x])
        if not getattr(noteprocessors, imports[x]).SILENT:
            customProcessors.append(imports[x])
        print (" - Successfully imported: ", imports[x])
    except ImportError:
        print (" - Error importing: ", imports[x])
print("Note Processor import complete")


# Object to hold place in note mode menu
noteModeMenu = processorhelpers.UiModeHandler(len(customProcessors) // 16 + 1)

note_menu_active = False

def switchNoteModeMenu(newMode):
    global note_menu_active
    note_menu_active = newMode
    noteModeMenu.resetMode()

def process(command):
    for x in customProcessorsAll:
        object_to_call = getattr(noteprocessors, x)
        if object_to_call.NAME == internal.noteMode.getState():
            object_to_call.process(command)
        
            if command.handled: return

def redrawNoteModeMenu(lights):
    
    current_name = internal.noteMode.getState()
    for ctr in range(len(customProcessorsAll)):
        if getattr(noteprocessors, customProcessorsAll[ctr]).NAME == current_name:
            note_mode_index = ctr
            break
    
    if note_menu_active:
        light_mode = lightingconsts.MODE_PULSE
    else:
        light_mode = lightingconsts.MODE_ON
    
    lights.setPadColour(8, 1, getattr(noteprocessors, customProcessorsAll[note_mode_index]).COLOUR, state=light_mode)
    
    if note_menu_active:
        redrawTo = min(len(customProcessors) - 16*noteModeMenu.getMode(), 16)
        
        for ctr in range(16*noteModeMenu.getMode(), 16*noteModeMenu.getMode() + redrawTo):
            
            x = ctr % 8
            y = ctr // 8
            
            if getattr(noteprocessors, customProcessors[ctr]).NAME == internal.noteMode.getState():
                light_mode = lightingconsts.MODE_PULSE
            else:
                light_mode = lightingconsts.MODE_ON
            
            lights.setPadColour(x, y, getattr(noteprocessors, customProcessors[ctr]).COLOUR, state=light_mode)
            
            
        lights.solidifyAll()

def processNoteModeMenu(command):
    
    global note_menu_active
    
    if command.type is eventconsts.TYPE_PAD and command.is_lift:
        if command.getPadCoord() == (8, 1):
            
            if note_menu_active:
                if command.is_double_click:
                    internal.extendedMode.revert(eventconsts.INCONTROL_PADS)
                    switchNoteModeMenu(False)
                    command.handle("Close note mode menu")
                else:
                    noteModeMenu.nextMode()
                    command.handle("Next note mode menu")
            
            elif not note_menu_active:
                internal.extendedMode.setVal(True, eventconsts.INCONTROL_PADS)
                switchNoteModeMenu(True)
                command.handle("Open note mode menu")
                
        elif note_menu_active:
            note_mode_index = noteModeMenu.getMode()*16 + command.coord_X + 8*command.coord_Y
            
            if note_mode_index < len(customProcessors):
                setModeByIndex(note_mode_index)
                internal.sendCompleteInternalMidiMessage(internalconstants.MESSAGE_INPUT_MODE_SELECT + (note_mode_index << 16))
                switchNoteModeMenu(False)
                internal.extendedMode.revert(eventconsts.INCONTROL_PADS)
                command.handle("Select note mode")
            
            else:
                command.handle("Note mode catch-all")

    if command.type is eventconsts.TYPE_BASIC_PAD and command.is_lift:
        if command.getPadCoord() == (8, 1):
            
            if note_menu_active:
                if command.is_double_click:
                    internal.extendedMode.revert(eventconsts.INCONTROL_PADS)
                    switchNoteModeMenu(False)
                    command.handle("Close note mode menu")
                else:
                    noteModeMenu.nextMode()
                    command.handle("Next note mode menu")
            
            elif not note_menu_active:
                internal.extendedMode.setVal(True, eventconsts.INCONTROL_PADS)
                switchNoteModeMenu(True)
                command.handle("Open note mode menu")

def setModeByIndex(index):
    internal.noteMode.setState(getattr(noteprocessors, customProcessors[index]).NAME)

