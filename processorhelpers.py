"""
processorhelpers.py

This script includes objects useful for event processors. 
It is worth investigating potential applications of these functions when writing your processors, 
or adding other frequently-required functions here.

Author: Miguel Guthridge [hdsq@outlook.com.au]
"""

import time

import utils
import ui
import plugins

import config
import eventconsts
import internal
import internal.consts
import lightingconsts

class UIMode:
    def __init__(self, name, colour, process_function, redraw_function):
        self.name = name
        self.colour = colour
        self.process_function = process_function
        self.redraw_function = redraw_function
    
    def process(self, command):
        self.process_function(command)
    
    def redraw(self, lights):
        self.redraw_function(lights)

class UiModeHandler: 
    """This object is used to manage menu layers, which can be toggled and switched through.
        It is best used in handler scripts to allow for a plugin or window to have multiple menus.
    """
    
    def __init__(self):
        """Create instance of UIModeHandler.

        Args:
            num_modes (int): The number of different menus to be contained in the object
        """
        self.is_down = False
        self.used = False
        self.modes = []
        self.current_mode = 0

    # Switch to next mode
    def nextMode(self):
        """Jump to the next menu layer

        Returns:
            int: mode number
        """
        self.current_mode += 1
        if self.current_mode == len(self.modes):
            self.current_mode = 0
        
        return self.current_mode
    
    def prevMode(self):
        """Jump to previous menu layer
        
        Returns:
            int: mode number
        """
        self.current_mode -= 1
        if self.current_mode == -1:
            self.current_mode = len(self.modes) - 1
        
        return self.current_mode

    def resetMode(self):
        """Resets menu layer to zero
        """
        self.current_mode = 0

    # Get current mode number
    def getMode(self):
        """Returns mode number

        Returns:
            int: mode number
        """
        return self.current_mode

    def press(self):
        self.is_down = True
        self.used = False
    
    def lift(self):
        self.is_down = False
        if not self.used:
            self.nextMode()

    def redraw(self, lights):
        
        lights.setPadColour(8, 0, self.modes[self.current_mode].colour)
        
        self.modes[self.current_mode].redraw(lights)
        
    def process(self, command):
        
        # For mode toggle
        if (command.type is eventconsts.TYPE_BASIC_PAD or command.type is eventconsts.TYPE_PAD) and command.coord_Y == 0 and command.coord_X == 8:
            if command.is_lift:
                self.lift()
                command.handle("Lift UI mode button")
                internal.window.resetAnimationTick()
            else:
                self.press()
                command.handle("Press UI mode button")
            
        
        self.modes[self.current_mode].process(command)
    
    def addMode(self, name, colour, process_function, redraw_function):
        self.modes.append(UIMode(name, colour, process_function, redraw_function))

class UiModeSelector: 
    """This object is used to manage menu layers, which can be toggled and switched through.
        Unlike UiModeHandler, it doesn't handle calling functions for processing
        It is best used in handler scripts to allow for a plugin or window to have multiple menus.
    """
    
    def __init__(self, num_modes):
        """Create instance of UIModeHandler.

        Args:
            num_modes (int): The number of different menus to be contained in the object
        """
        self.is_down = False
        self.used = False
        self.mode = 0
        self.num_modes = num_modes

    # Switch to next mode
    def nextMode(self):
        """Jump to the next menu layer

        Returns:
            int: mode number
        """
        self.mode += 1
        if self.mode == self.num_modes:
            self.mode = 0
        
        return self.mode
    
    def prevMode(self):
        """Jump to previous menu layer
        
        Returns:
            int: mode number
        """
        self.mode -= 1
        if self.mode == -1:
            self.mode = self.num_modes - 1
        
        return self.mode

    def resetMode(self):
        """Resets menu layer to zero
        """
        self.mode = 0

    # Get current mode number
    def getMode(self):
        """Returns mode number

        Returns:
            int: mode number
        """
        return self.mode

    def press(self):
        self.is_down = True
        self.used = False
    
    def lift(self):
        self.is_down = False
        if not self.used:
            self.nextMode()

    def redraw(self, lights):
        pass
        
    def process(self, command):
        pass
    

def snap(value, snapTo):
    """Returns a snapped value

    Args:
        value (float): value being snapped
        snapTo (float or list of floats): value(s) to snap to

    Returns:
        float: value after snapping
    """
    if not config.ENABLE_SNAPPING:
        return value
    
    # Change to list
    if type(snapTo) is float or type(snapTo) is int:
        snapTo = [snapTo]
    
    for i in range(len(snapTo)):
        if abs(value - snapTo[i]) <= config.SNAP_RANGE:
            return snapTo[i]
    else: return value

def didSnap(value, snapTo):
    """Returns a boolean indicating whether a value was snapped

    Args:
        value (float): value being snapped
        snapTo (float or list of floats): value(s) to snap to

    Returns:
        bool: whether the value would snap
    """
    return abs(value - snapTo) <= config.SNAP_RANGE and config.ENABLE_SNAPPING

def toFloat(value, min = 0, max = 1):
    """Converts a MIDI event value (data2) to a float to set parameter values.

    Args:
        value (int): MIDI event value (0-127)
        min (float, optional): lower value to set between. Defaults to 0.
        max (float, optional): upper value to set between. Defaults to 1.

    Returns:
        float: range value
    """
    return (value / 127) * (max - min) + min

class ExtensibleNote():
    """A note with other notes tacked on. Used for playing chords in note processors.
    """
    def __init__(self, root_note, extended_notes):
        """Create instance of ExtensibleNote object

        Args:
            root_note (note event): the note that the user pressed (or a modified version of it). 
                Can be of type RawEvent, ParsedEvent or FLMidiMessage.
                
            extended_notes (list of note events): List of notes that should also be pressed. Can be of 
                same types as root_note, but RawEvent is recommended for performance reasons.
        """
        self.root = root_note
        self.extended_notes = extended_notes


def convertPadMapping(padNumber):
    """Converts between basic mode pad mapping and extended mode mapping

    Args:
        padNumber (int): note number for extended pad

    Returns:
        int: note number for basic pad
    """
    for y in range(len(eventconsts.Pads)):
        for x in range(len(eventconsts.Pads[y])):
            if padNumber == eventconsts.Pads[y][x]:
                return eventconsts.BasicPads[y][x]


lastPressID = -1
lastPressTime = -1
def isDoubleClickPress(id_val):
    """Returns whether a press event was a double click

    Args:
        id_val (int): Event ID

    Returns:
        bool: whether the event was a double click
    """
    global lastPressID
    global lastPressTime
    ret = False
    currentTime = time.perf_counter()
    if id_val == lastPressID and (currentTime - lastPressTime < config.DOUBLE_PRESS_TIME):
        ret = True
    lastPressID = id_val
    lastPressTime = currentTime
    return ret


lastLiftID = -1
lastLiftTime = -1
def isDoubleClickLift(id_val):
    """Returns whether a lift event was a double click

    Args:
        id_val (int): Event ID

    Returns:
        bool: whether the event was a double click
    """
    global lastLiftID
    global lastLiftTime
    ret = False
    currentTime = time.perf_counter()
    if id_val == lastLiftID and (currentTime - lastLiftTime < config.DOUBLE_PRESS_TIME):
        ret = True
    lastLiftID = id_val
    lastLiftTime = currentTime
    return ret

def isLongPressLift(id_val):
    """Returns whether a lift event was held down for a long time
    
    Args:
        id_val (int): Event ID
    
    Returns:
        bool: whether the event was a long press
    """
    global lastPressID, lastPressTime
    
    currentTime = time.perf_counter()

    return (id_val == lastPressID) and (currentTime - lastPressTime >= config.LONG_PRESS_TIME)
    
    


class Action:
    """Stores an action as a string
    """
    def __init__(self, act, silent):
        """Create an event action

        Args:
            act (str): The action taken
            silent (bool): Whether the action should be set as a hint message
        """
        self.act = act
        self.silent = silent

class ActionList:
    """Stores a list of actions taken by a single processor
    """
    def __init__(self, name):
        """Create an action list

        Args:
            name (str): Name of the processor
        """
        self.name = name
        self.list = []
        self.handle_type = False

    
    def appendAction(self, action, silent, handle):
        """Append action to list of actions

        Args:
            action (str): The action taken
            silent (bool): Whether the action should be set as a hint message
            handle (int): How this action handled the event (using internal.consts.EVENT_<handle type>)
        """
        self.list.append(Action(action, silent))

        # Set flag indicating that this processor handled the event
        self.handle_type = handle

    def getString(self):
        """Returns a string of the actions taken

        Returns:
            str: actions taken
        """
        # Return that no action was taken if list is empty
        if len(self.list) == 0:
            return internal.getTab(self.name + ":", 2) + "[No actions]"

        # No indentation required if there was only one action
        elif len(self.list) == 1:
            ret = internal.getTab(self.name + ":", 2) + self.list[0].act

        # If there are multiple actions, indent them
        else:
            ret = self.name + ":"
            for i in range(len(self.list)):
                ret += '\n' + internal.getTab("") + self.list[i].act

        if self.handle_type == internal.consts.EVENT_HANDLE:
            ret += '\n' + internal.getTab("") + "[Handled]"
        elif self.handle_type == internal.consts.EVENT_IGNORE:
            ret += '\n' + internal.getTab("") + "[Ignored]"
        return ret

    # Returns the latest non-silent action to set as the hint message
    def getHintMsg(self):
        """Returns string of hint message to set, empty string if none

        Returns:
            str: Hint message
        """
        ret = ""
        for i in range(len(self.list)):
            if self.list[i].silent == False:
                ret = self.list[i].act
        return ret


class ActionPrinter:
    """Object containing actions taken by all processor modules
    """

    def __init__(self):
        # String that is output after each event is processed
        self.eventProcessors = []

    
    def addProcessor(self, name):
        """Add an event processor

        Args:
            name (str): Name of the processor
        """
        self.eventProcessors.append(ActionList(name))

    
    def appendAction(self, act, silent=False, handle_type=internal.consts.EVENT_NO_HANDLE):
        """Appends an action to the current event processor

        Args:
            act (str): The action taken
            silent (bool, optional): Whether the action should be set as a hint message. Defaults to False.
            handled (int, optional): How the action handled/ignored the event. Defaults to internal.consts.EVENT_NO_HANDLE.
        """

        # Add some random processor if a processor doesn't exist for some reason
        if len(self.eventProcessors) == 0:
            self.addProcessor("NoProcessor")
            internal.debugLog("Added NoProcessor Processor", internal.consts.DEBUG.WARNING_DEPRECIATED_FEATURE)
        # Append the action
        self.eventProcessors[len(self.eventProcessors) - 1].appendAction(act, silent, handle_type)

    def flush(self):
        """Log all actions taken, and set a hint message if applicable
        """
        # Log all actions taken
        for x in range(len(self.eventProcessors)):
            internal.debugLog(self.eventProcessors[x].getString(), internal.consts.DEBUG.EVENT_ACTIONS)

        # Get hint message to set (ignores silent messages)
        hint_msg = ""
        for x in range(len(self.eventProcessors)):
            cur_msg = self.eventProcessors[x].getHintMsg()

            # Might want to fix this some time, some handler modules append this manually
            if cur_msg != "" and cur_msg != "[Did not handle]":
                hint_msg = cur_msg

        if hint_msg != "":
            # Sometimes this fails...
            try:
                ui.setHintMsg(hint_msg)
            except:
                pass
        self.eventProcessors.clear()


class RawEvent:
    """Stores event in raw form. A quick way to generate events for editing.
    """
    def __init__(self, status, data1, data2):
        """Create a RawEvent object

        Args:
            status (int): Status byte
            data1 (int): First data byte
            data2 (int): 2nd data byte
        """
        self.status = status
        self.data1 = data1
        self.data2 = data2


class ParsedEvent:
    """Stores data about an event, including useful parsed data
    """
    def __init__(self, event):
        """Create ParsedEvent from event object

        Args:
            event (MIDI Event): FL Studio MIDI Event
        """
        self.recieved_internal = False
        self.edited = False
        self.actions = ActionPrinter()

        self.handled = False
        self.ignored = False

        self.status = event.status
        
        self.note = event.data1
        self.data1 = event.data1
        
        self.value = event.data2
        self.data2 = event.data2
        
        self.status_nibble = event.status >> 4              # Get first half of status byte
        self.channel = event.status & int('00001111', 2)    # Get 2nd half of status byte
        
        if self.channel == internal.consts.INTERNAL_CHANNEL_STATUS:
            self.recieved_internal = True

        # PME Flags to make sure errors don't happen or something
        self.processPmeFlags(event.pmeFlags)

        # Add sysex information
        self.sysex = event.sysex

        # Bit-shift status and data bytes to get event ID
        self.id = (self.status + (self.note << 8))

        self.parse()

        # Process sysex events
        if self.type is eventconsts.TYPE_SYSEX_EVENT:
            internal.processSysEx(self)
                                                                                                          
    def parse(self):
        """Parses information about the event
        """
        
        # Indicates whether to consider as a value or as an on/off
        self.isBinary = False

        

        # Determine type of event | unrecognised by default
        self.type = eventconsts.TYPE_UNRECOGNISED

        # If using basic port, check for notes

        if self.status == eventconsts.SYSEX:
            self.type = eventconsts.TYPE_SYSEX_EVENT

        elif self.id in eventconsts.InControlButtons: 
            self.type = eventconsts.TYPE_INCONTROL
            self.isBinary = True

        elif self.id in eventconsts.SystemMessages: 
            self.type = eventconsts.TYPE_SYSTEM_MSG
            self.isBinary = True

        elif self.id in eventconsts.TransportControls: 
            self.type = eventconsts.TYPE_TRANSPORT
            self.isBinary = True

        elif self.id in eventconsts.Knobs: 
            self.type = eventconsts.TYPE_KNOB
            self.coord_X = self.note - 0x15

        elif self.id in eventconsts.BasicKnobs: 
            self.type = eventconsts.TYPE_BASIC_KNOB
            self.coord_X = self.note - 0x15

        elif self.id in eventconsts.Faders: 
            self.type = eventconsts.TYPE_FADER
            self.coord_X = self.note - 0x29
            if self.note == 0x07: self.coord_X = 8

        elif self.id in eventconsts.BasicFaders: 
            self.type = eventconsts.TYPE_BASIC_FADER
            self.coord_X = self.note - 0x29
            if self.note == 0x07: self.coord_X = 8

        elif self.id in eventconsts.FaderButtons: 
            self.type = eventconsts.TYPE_FADER_BUTTON
            self.coord_X = self.note - 0x33
            self.isBinary = True

        elif self.id in eventconsts.BasicFaderButtons: 
            self.type = eventconsts.TYPE_BASIC_FADER_BUTTON
            self.coord_X = self.note - 0x33
            self.isBinary = True
        
        elif self.id in eventconsts.BasicEvents:
            self.type = eventconsts.TYPE_BASIC_EVENT
            if self.id == eventconsts.PEDAL:
                self.isBinary = True

        elif self.status_nibble == eventconsts.NOTE_ON or self.status_nibble == eventconsts.NOTE_OFF:
            # Pads are actually note events
            if (self.status == 0x9F or self.status == 0x8F) or ((self.status == 0x99 or self.status == 0x89)):
                x, y = self.getPadCoord()
                if x != -1 and y != -1:
                    # Is a pad
                    self.coord_X = x
                    self.coord_Y = y
                    self.isBinary = True
                    if self.isPadExtendedMode():
                        self.type = eventconsts.TYPE_PAD
                    else:
                        self.type = eventconsts.TYPE_BASIC_PAD
            else:
                self.type = eventconsts.TYPE_NOTE
                self.isBinary = True

        # Detect basic circular pads
        elif self.status == 0xB0 and self.note in eventconsts.BasicPads[8]:
            self.type = eventconsts.TYPE_BASIC_PAD
            self.coord_X = 8
            self.coord_Y = eventconsts.BasicPads[8].index(self.note)
            self.isBinary = True
        
        if self.recieved_internal:
            self.type = eventconsts.TYPE_INTERNAL_EVENT
        
        # Check if buttons were lifted
        if self.value == 0: 
            self.is_lift = True
        else: 
            self.is_lift = False
        
        # Don't process these for internal events
        if self.type != eventconsts.TYPE_INTERNAL_EVENT:
            
        
            # Process long presses
            if self.is_lift:
                self.is_long_press = isLongPressLift(self.id)
            else:
                self.is_long_press = False

            # Process double presses (seperate for lifted and pressed buttons)
            self.is_double_click = False
            if self.isBinary is True: 
                if self.is_lift is True:
                    self.is_double_click = isDoubleClickLift(self.id)
                elif self.is_lift is False and self.isBinary is True: 
                    self.is_double_click = isDoubleClickPress(self.id)
        
        else:
            self.is_double_click = False
            self.is_long_press = False
        
    def edit(self, event, reason):
        """Edit the event to change data

        Args:
            event (RawEvent): A MIDI Event to change this event to
        """
        self.edited = True
        
        self.status = event.status
        
        self.note = event.data1
        self.data1 = event.data1
        
        self.value = event.data2
        self.data2 = event.data2
        
        self.status_nibble = event.status >> 4              # Get first half of status byte
        self.channel = event.status & int('00001111', 2)    # Get 2nd half of status byte

        # Bit-shift status and data bytes to get event ID
        self.id = (self.status + (self.note << 8))

        self.parse()
        newEventStr = "Changed event: " + reason
        if internal.consts.DEBUG.EVENT_DATA in config.CONSOLE_DEBUG_MODE:
            newEventStr += "\n" + self.getInfo()

        self.act(newEventStr)
    
    def handle(self, action, silent=False):
        """Handles the event and prevents further processing, both in the script and in FL Studio.

        Args:
            action (str): The action that handled the event
            silent (bool, optional): Whether the action should be set as a hint message. Defaults to False.
        """
        self.handled = True
        self.ignored = True
        self.actions.appendAction(action, silent, internal.consts.EVENT_HANDLE)

    def ignore(self, action, silent=False):
        """Prevents further processing in the script but allows processing in FL Studio.

        Args:
            action (str): The action taken
            silent (bool, optional): Whether the action should be written to the hint panel. 
                Defaults to False.
        """
        self.ignored = True
        self.actions.appendAction(action, silent, internal.consts.EVENT_IGNORE)

    def act(self, action, silent=True):
        """Adds an action to the event without handling it.

        Args:
            action (str): The action taken
        """
        self.actions.appendAction(action, silent, internal.consts.EVENT_NO_HANDLE)

    def addProcessor(self, name):
        """Adds an event processor to the processor list.

        Args:
            name (str): Name of processor
        """
        self.actions.addProcessor(name)
    
    def getInfo(self):
        """Returns info about event

        Returns:
            str: Details about the event
        """
        out = "Event:"
        out = internal.getTab(out)

        # Event type and ID
        temp = self.getType()
        out += temp
        out = internal.getTab(out)

        # Event value
        temp = self.getValue()
        out += temp
        out = internal.getTab(out)

        # Event full data
        temp = self.getDataString()
        out += temp
        out = internal.getTab(out)

        if self.is_double_click:
            out += "[Double Click]"
            out = internal.getTab(out)
        
        if self.is_long_press:
            out += "[Long Press]"
            out = internal.getTab(out)
        
        if internal.shifts.query():
            out += "[Shifted | " + internal.shifts.current_down + "]"
            out = internal.getTab(out)
        
        """ # Add this back soon hopefully
        if self.id == config.SHIFT_BUTTON:
            out += "[Shift Key]"
            out = internal.getTab(out)
        """
        
        # For internal events, have a different printing  flag
        if self.type == eventconsts.TYPE_INTERNAL_EVENT:
            if not internal.consts.DEBUG.PRINT_INTERNAL_EVENTS in config.CONSOLE_DEBUG_MODE:
                out = ""
        
        return out

    
    def printInfo(self):
        """Prints string info about event
        """
        internal.debugLog(self.getInfo(), internal.consts.DEBUG.EVENT_DATA)
    
    
    def printOutput(self):
        """Prints actions taken whilst handling event
        """
        if internal.consts.DEBUG.PRINT_INTERNAL_EVENTS in config.CONSOLE_DEBUG_MODE or self.type != eventconsts.TYPE_INTERNAL_EVENT:
            internal.debugLog("", internal.consts.DEBUG.EVENT_ACTIONS)
            self.actions.flush()
            if self.handled:
                internal.debugLog("[Event was handled]", internal.consts.DEBUG.EVENT_ACTIONS)
            else: 
                internal.debugLog("[Event wasn't handled]", internal.consts.DEBUG.EVENT_ACTIONS)

    
    def getType(self):
        """Returns string detailing type and ID of event

        Returns:
            str: Type and ID of event info
        """
        a = ""
        b = ""
        if self.type is eventconsts.TYPE_UNRECOGNISED: 
            a = "Unrecognised"
        elif self.type is eventconsts.TYPE_SYSEX_EVENT:
            a = "Sysex"
        elif self.type is eventconsts.TYPE_NOTE:
            a = "Note"
            b = utils.GetNoteName(self.note) + " (Ch. " + str(self.channel) + ')'
        elif self.type is eventconsts.TYPE_SYSTEM_MSG: 
            a = "System"
            b = self.getID_System()
        elif self.type is eventconsts.TYPE_INCONTROL: 
            a = "InControl"
            b = self.getID_InControl()
        elif self.type is eventconsts.TYPE_TRANSPORT: 
            a = "Transport"
            b = self.getID_Transport()
        elif self.type is eventconsts.TYPE_KNOB or self.type is eventconsts.TYPE_BASIC_KNOB: 
            a = "Knob"
            b = self.getID_Knobs()
        elif self.type is eventconsts.TYPE_FADER or self.type is eventconsts.TYPE_BASIC_FADER: 
            a = "Fader"
            b = self.getID_Fader()
        elif self.type is eventconsts.TYPE_FADER_BUTTON or self.type is eventconsts.TYPE_BASIC_FADER_BUTTON: 
            a = "Fader Button"
            b = self.getID_FaderButton()
        elif self.type is eventconsts.TYPE_PAD: 
            a = "Pad"
            b = self.getID_Pads()
        elif self.type is eventconsts.TYPE_BASIC_PAD:
            a = "Pad (Basic)"
            b = self.getID_Pads()
        elif self.type is eventconsts.TYPE_BASIC_EVENT:
            a = "Basic Event"
            b = self.getID_Basic()
        elif self.type is eventconsts.TYPE_INTERNAL_EVENT:
            a = "Internal event"
        else: 
            internal.debugLog("Bad event type")
            a = "ERROR!!!"
        a = internal.getTab(a)
        return a + b

    def processPmeFlags(self, flags):
        """Processes PME flags on event (Currently very broken)

        Args:
            flags (int): PME flags
        """
        #print(flags)
        bin_string = format(flags, '8b')[:5]
        #print(bin_string)
        flags_list = [x == '1' for x in bin_string]
        self.pme_system = flags_list[0]
        
        self.pme_system_safe = flags_list[1]
        
        self.pme_preview_note = flags_list[2]
        
        self.pme_from_host = flags_list[3]
        
        self.pme_from_midi = flags_list[4]
        

    def getID_System(self):
        """Returns string event ID for system events

        Returns:
            str: Event ID details
        """
        if   self.id == eventconsts.SYSTEM_EXTENDED: return "InControl"
        elif self.id == eventconsts.SYSTEM_MISC: return "Misc"
        else: return "ERROR"

    
    def getID_InControl(self):
        """Returns string event ID for InControl events

        Returns:
            str: Event ID details
        """
        if   self.id == eventconsts.INCONTROL_KNOBS: return "Knobs"
        elif self.id == eventconsts.INCONTROL_FADERS: return "Faders"
        elif self.id == eventconsts.INCONTROL_PADS: return "Pads"
        else: return "ERROR"
    
    
    def getID_Basic(self):
        """Returns string event ID for basic events

        Returns:
            str: Event ID Details
        """
        if self.id == eventconsts.PEDAL: return "Pedal"
        elif self.id == eventconsts.MOD_WHEEL: return "Modulation"
        elif self.id == eventconsts.PITCH_BEND: return "Pitch Bend"
        else: return "ERROR"

    
    def getID_Transport(self):
        """Returns string event ID for transport events

        Returns:
            str: Event ID details
        """
        if   self.id == eventconsts.TRANSPORT_BACK: return "Back"
        elif self.id == eventconsts.TRANSPORT_FORWARD: return "Forward"
        elif self.id == eventconsts.TRANSPORT_STOP: return "Stop"
        elif self.id == eventconsts.TRANSPORT_PLAY: return "Play"
        elif self.id == eventconsts.TRANSPORT_LOOP: return "Loop"
        elif self.id == eventconsts.TRANSPORT_RECORD: return "Record"
        elif self.id == eventconsts.TRANSPORT_TRACK_NEXT: return "Next Track"
        elif self.id == eventconsts.TRANSPORT_TRACK_PREVIOUS: return "Previous Track"
        else: return "ERROR"
    
    
    def getID_Pads(self):
        """Returns string eventID for pad events

        Returns:
            str: Event ID details
        """
        x_map, y_map = self.getPadCoord()
        
        ret_str = ""

        if y_map == 0:   ret_str += "Top "
        elif y_map == 1: ret_str += "Bottom "
        else: return "ERROR"
        if x_map == 8:
            ret_str += "Button"
            return ret_str
        ret_str += str(x_map + 1)

        return ret_str
    
    
    def getID_Fader(self):
        """Returns string eventID for fader events

        Returns:
            str: Event ID details
        """
        return str(self.coord_X + 1)


    def getID_FaderButton(self):
        """Returns string eventID for fader button events

        Returns:
            str: Event ID details
        """
        return str(self.coord_X + 1)
    
    def getID_Knobs(self):
        """Returns string eventID for knob events

        Returns:
            str: Event ID details
        """
        return str(self.coord_X + 1)
    
    
    def getPadCoord(self):
        """Returns X, Y coordinates for pad events

        Returns:
            int: X
            int: Y
        """
        y_map = -1
        x_map = -1
        done_flag = False
        for x in range(len(eventconsts.Pads)):
            for y in range(len(eventconsts.Pads[x])):
                if self.note == eventconsts.Pads[x][y] or self.note == eventconsts.BasicPads[x][y]:
                    y_map = y
                    x_map = x
                    done_flag = True
                    break
            if done_flag: break
        return x_map, y_map

    
    def isPadExtendedMode(self):
        """Returns True if Pad is Extended

        Returns:
            bool: whether pad is extended
        """
        if self.note == eventconsts.Pads[self.coord_X][self.coord_Y]: return True
        elif self.note == eventconsts.BasicPads[self.coord_X][self.coord_Y]: return False
        else: print("ERROR!!?")

    
    def getValue(self):
        """Returns (formatted) value of event  

        Returns:
            str: Formatted value (data2) of event
        """
        a = str(self.value)
        b = ""
        if self.isBinary:
            if self.value == 0:
                b = "(Off)"
            else: b = "(On)"
        a = internal.getTab(a, length=5)
        return a + b

    
    def getDataString(self):
        """Returns string with (formatted) hex of event

        Returns:
            str: hex of event
        """
        if self.type is eventconsts.TYPE_SYSEX_EVENT:
            return str(self.sysex)

        # Append hex value of ID
        a = str(hex(self.id + (self.value << 16)))
        # If string requires leading zeros
        if len(a) == 7: a = "0x0" + a[2:].upper()
        elif len(a) == 6: a = "0x00" + a[2:].upper()
        elif len(a) == 5: a = "0x000" + a[2:].upper()
        elif len(a) == 4: a = "0x0000" + a[2:].upper()
        elif len(a) == 3: a = "0x00000" + a[2:].upper()
        elif len(a) == 2: a = "0x000000" + a[2:].upper()
        else: a = "0x" + a[2:].upper()

        a = a[:2] + " " + a[2:4] + " " + a[4:6] + " " + a[6:8]
        
        return a

    
    def getDataMIDI(self):
        """Returns int with hex of event

        Returns:
            int: MIDI event
        """
        return internal.toMidiMessage(self.status, self.note, self.value)

#-------------------------
# KEYSWITCH FUNCTIONS
#-------------------------


class KeyswitchMgr:
    """Provides functionality relating to keyswitches. Can be used by any event processor.
    """
    palette_cache = [
        [-1, -1],
        [-1, -1],
        [-1, -1],
        [-1, -1],
        [-1, -1],
        [-1, -1],
        [-1, -1],
        [-1, -1]
    ]

    def redraw(self, lights, colour_palette, x_len=-1, y_len=-1, full_keyswitches=-1):
        """Draw keyswitch lights

        Args:
            lights (LightMap): lights to draw onto
            colour_palette (list/int): Colour or palette of colours
            x_len (int, optional): how wide is each page of articulations. Defaults to -1.
            y_len (int, optional): height of each page of articulations. Defaults to -1.
            full_keyswitches (int, optional): whether to use full keyswitches. Defaults to -1.
        """
        animation_tick = internal.window.getAnimationTick()
        if full_keyswitches == -1: full_keyswitches = config.USE_FULL_KEYSWITCHES
        
        # For 4x2 or 4x1 sets of keyswitches, use textured palette
        if x_len == 4 and (y_len == 2 or y_len == 1) and type(colour_palette) is list:
            if not (self.palette_cache[0][0] == colour_palette[0] and self.palette_cache[7][1] == colour_palette[5]):
                self.palette_cache = [
                    [colour_palette[0], colour_palette[1]],
                    [colour_palette[1], colour_palette[2]],
                    [colour_palette[2], colour_palette[3]],
                    [colour_palette[3], colour_palette[4]],
                    [colour_palette[1], colour_palette[2]],
                    [colour_palette[2], colour_palette[3]],
                    [colour_palette[3], colour_palette[4]],
                    [colour_palette[4], colour_palette[5]]
                ]
            
            if full_keyswitches:
                for y in range(2):
                    for x in range(8):
                        if (x % 4) + y + 2*(x >= 4) < animation_tick:
                            lights.setPadColour(x, y, self.palette_cache[x][y])
            else:
                for x in range(0, 8):
                    if (x % 4) + 2*(x >= 4) < animation_tick:
                        lights.setPadColour(x, 1, self.palette_cache[x][0])
        
        # Any other set size, just draw colours normally
        else:
            if type(colour_palette) is list:
                colour = colour_palette[3]
            else: 
                colour = colour_palette
            if full_keyswitches:
                for y in range(2):
                    for x in range(8):
                        if x + y < animation_tick:
                            lights.setPadColour(x, y, colour)
            else:
                for x in range(0, 8):
                    if x < animation_tick:
                        lights.setPadColour(x, 1, colour)

    def getNum(self, x, y, x_len, y_len, full_keyswitches=-1):
        """Get the keyswitch number of a pad with coordinates (x, y). 
                Eg: if it is the first keyswitch, return 0
                or if it is the secons, return 1

        Args:
            x (int): x coordinate
            y (int): y coordinate
            x_len (int): width of each page of articulation
            y_len (int): height of each page of articulation
            full_keyswitches (int, optional): whether to use full keyswitches. Defaults to -1.

        Returns:
            int: keyswitch number
        """
        if full_keyswitches == -1: full_keyswitches = config.USE_FULL_KEYSWITCHES
        
        if full_keyswitches:
            # Fancy branchless stuff
            return (x)*(x < x_len) + (x + x_len)*(x_len <= x < 2*x_len) + x_len*y
        else:
            if y == 1:
                # Use coord_X number for keyswitch number
                return x
            
keyswitches = KeyswitchMgr()

def getAbsNoteName(note):
    """Returns note name relative to C

    Args:
        note (int): ntoe number relative to C (0-11)
    """
    # Get note in correct range
    note %= 12
    
    # Whether a note is sharp or not
    sharps_flats = [0, 1, 0, -1, 0, 0, 1, 0, -1, 0, -1, 0]
    
    # To append sharps or flats to note names
    #                  0   1    2     -2   -1
    sharp_flat_str = ["", "#", "##", "bb", "b"]
    
    # Interval numbers
    interval_nums = [1, 1, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7]
    
    # Note names for each key, used with interval number
    note_names = ['_', 'C', 'D', 'E', 'F', 'G', 'A', 'B']

    # Calculate root name
    return note_names[interval_nums[note]] + sharp_flat_str[sharps_flats[note]]

def getRelNoteName(note, key_root):
    """Returns note name relative to root of key

    Args:
        note (int): note number relative to root (0-11)
        key_root (int): note number of key relative to C (0-11)

    Returns:
        str: note name
    """
    
    # Get notes in correct range
    note %= 12
    key_root %= 12
    
    # Whether a note is sharp or not
    sharps_flats = [0, 1, 0, -1, 0, 0, 1, 0, -1, 0, -1, 0]
    
    # To append sharps or flats to note names
    #                  0   1    2     -2   -1
    sharp_flat_str = ["", "#", "##", "bb", "b"]
    
    # Interval numbers
    interval_nums = [1, 1, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7]
    
    # Note names for each key, used with interval number
    note_names = ['_', 'C', 'D', 'E', 'F', 'G', 'A', 'B']
    
    # Get absolute note value
    note_abs = (note + key_root) % 12
    
    # Calculate absolute shar and flat
    abs_sharp_flat = sharps_flats[note_abs]
    
    # If it's a natural note, just return its name
    if abs_sharp_flat == 0:
        return note_names[interval_nums[note_abs]]
    
    # Otherwise get whether its a sharp or a flat in that key
    note_sharp_flat = sharps_flats[note]
    
    # If it's relatively natural
    if note_sharp_flat == 0:
        # If the key is flat or F major, return flattened note
        if sharps_flats[key_root] == -1 or key_root == 5:
            # If absolute is flat
            if abs_sharp_flat == -1:
                return note_names[interval_nums[note_abs]] + sharp_flat_str[abs_sharp_flat]
            # Otherwise (absolute is sharp)
            else:
                return note_names[interval_nums[note_abs] + 1] + sharp_flat_str[-1]
        
        # Otherwise (they key is sharp or some other natural key)
        else:
            # If absolute is sharp
            if abs_sharp_flat == 1:
                return note_names[interval_nums[note_abs]] + sharp_flat_str[abs_sharp_flat]
            # Otherwise (absolute is flat)
            else:
                return note_names[interval_nums[note_abs] - 1] + sharp_flat_str[1]
    
    # If it's the same sharp/flat for absolute and relative, return that
    if note_sharp_flat == abs_sharp_flat:
        return note_names[interval_nums[note_abs]] + sharp_flat_str[note_sharp_flat]
    
    # If it's relatively sharp but absolutely flat (assumed), return the sharpened one
    if note_sharp_flat == 1:
        return note_names[interval_nums[note_abs - 1]] + sharp_flat_str[note_sharp_flat]
        
    # Otherwise (it's relatively sharp but absolutely flat), return the sharpened one
    if note_sharp_flat == -1 and abs_sharp_flat == 1:
        return note_names[interval_nums[note_abs + 1]] + sharp_flat_str[note_sharp_flat]
    
