"""
processchannelrack.py
This script handles events when the channel rack is active

"""

import math # For logarithm

import channels
import ui

import lighting
import config
import internalconstants
import internal
import eventconsts
import processorhelpers

ui_mode = processorhelpers.UI_mode_handler(2)


MENU_MODE_COLOUR = lighting.UI_CHOOSE
BIT_MODE_COLOUR = lighting.COLOUR_RED

def process(command):

    command.actions.addProcessor("Channel rack Processor")

    
    #---------------------------------
    # Pads
    #---------------------------------
    if command.type == eventconsts.TYPE_PAD and command.is_lift:
        # UI Mode
        if command.padY == 1 and command.padX == 0:
            ui_mode.nextMode()
            internal.window.reset_animation_tick()
            command.actions.appendAction("Channel Rack: Next UI mode")
            command.handled = True

        elif ui_mode.getMode() == 1:
            process_bit_mode(command)

        elif ui_mode.getMode() == 0:
            process_menu_mode(command)

    #---------------------------------
    # Faders
    #---------------------------------
    if command.type == eventconsts.TYPE_FADER:
        # Fader 1
        if command.id == eventconsts.FADER_1: 
            setVolume(command, 0, command.value)
            command.handled = True
        
        # Fader 2
        if command.id == eventconsts.FADER_2: 
            setVolume(command, 1, command.value)
            command.handled = True

        # Fader 3
        if command.id == eventconsts.FADER_3: 
            setVolume(command, 2, command.value)
            command.handled = True
        
        # Fader 4
        if command.id == eventconsts.FADER_4: 
            setVolume(command, 3, command.value)
            command.handled = True

        # Fader 5
        if command.id == eventconsts.FADER_5: 
            setVolume(command, 4, command.value)
            command.handled = True
        
        # Fader 6
        if command.id == eventconsts.FADER_6: 
            setVolume(command, 5, command.value)
            command.handled = True
        
        # Fader 7
        if command.id == eventconsts.FADER_7: 
            setVolume(command, 6, command.value)
            command.handled = True

        # Fader 8
        if command.id == eventconsts.FADER_8: 
            setVolume(command, 7, command.value)
            command.handled = True

        # Fader 9
        if command.id == eventconsts.FADER_9: 
            # If shift key held, change master track
            if command.shifted:
                setVolume(command, 8, command.value)
                command.handled = True
            # Otherwise change current track
            else:
                # Get current track number
                track = channels.channelNumber()
                setVolume(command, track, command.value)
                command.handled = True

    #---------------------------------
    # Knobs
    #---------------------------------
    if command.type == eventconsts.TYPE_KNOB:
        # Knob 1
        if command.id == eventconsts.KNOB_1: 
            setPan(command, 0, command.value)
            command.handled = True
        
        # Knob 2
        if command.id == eventconsts.KNOB_2: 
            setPan(command, 1, command.value)
            command.handled = True

        # Knob 3
        if command.id == eventconsts.KNOB_3: 
            setPan(command, 2, command.value)
            command.handled = True
        
        # Knob 4
        if command.id == eventconsts.KNOB_4: 
            setPan(command, 3, command.value)
            command.handled = True

        # Knob 5
        if command.id == eventconsts.KNOB_5: 
            setPan(command, 4, command.value)
            command.handled = True
        
        # Knob 6
        if command.id == eventconsts.KNOB_6: 
            setPan(command, 5, command.value)
            command.handled = True
        
        # Knob 7
        if command.id == eventconsts.KNOB_7: 
            setPan(command, 6, command.value)
            command.handled = True

        # Knob 8
        if command.id == eventconsts.KNOB_8: 
            # If shift key held, change track 7
            if command.shifted:
                setPan(command, 7, command.value)
                command.handled = True
            # Otherwise change current track
            else:
                # Get current track number
                track = channels.channelNumber()
                setPan(command, track, command.value)
                command.handled = True


    #---------------------------------
    # Mixer Buttons - mute/solo tracks
    #---------------------------------
    if command.type == eventconsts.TYPE_FADER_BUTTON:
        if command.id == eventconsts.FADER_BUTTON_1:
            processMuteSolo(0, command)
            command.handled = True

        if command.id == eventconsts.FADER_BUTTON_2:
            processMuteSolo(1, command)
            command.handled = True

        if command.id == eventconsts.FADER_BUTTON_3:
            processMuteSolo(2, command)
            command.handled = True

        if command.id == eventconsts.FADER_BUTTON_4:
            processMuteSolo(3, command)
            command.handled = True

        if command.id == eventconsts.FADER_BUTTON_5:
            processMuteSolo(4, command)
            command.handled = True

        if command.id == eventconsts.FADER_BUTTON_6:
            processMuteSolo(5, command)
            command.handled = True

        if command.id == eventconsts.FADER_BUTTON_7:
            processMuteSolo(6, command)
            command.handled = True

        if command.id == eventconsts.FADER_BUTTON_8:
            processMuteSolo(7, command)
            command.handled = True

        if command.id == eventconsts.FADER_BUTTON_9:
            # If shift key held, change 9th track
            if command.shifted:
                processMuteSolo(8, command)
                command.handled = True
            else:
                processMuteSolo(channels.channelNumber(), command)
                command.handled = True

    return

# Process when in grid bits
def process_bit_mode(command):
    current_track = channels.channelNumber()
    #---------------------------------
    # Pads
    #---------------------------------
    if command.type == eventconsts.TYPE_PAD and command.is_lift:
        # Grid bits
        if command.padY == 0 and command.padX != 8:
            command.handled = True

            gridBits.toggleBit(current_track, command.padX)
            command.actions.appendAction("Grid Bits: Toggle bit")
        
        coord = [command.padX, command.padY]


        # Scroll grid bits
        if coord == [4, 1]:
            if command.is_double_click:
                gridBits.resetScroll()
                command.actions.appendAction("Grid Bits: Reset scroll")
                command.handled = True
            else:
                gridBits.scrollLeft()
                command.actions.appendAction("Grid Bits: Scroll left")
                command.handled = True
        if coord == [5, 1]:
            gridBits.scrollRight()
            command.actions.appendAction("Grid Bits: Scroll right")
            command.handled = True
        # Zoom grid bits
        if coord == [6, 1]:
            gridBits.zoomOut()
            command.actions.appendAction("Grid Bits: Zoom out")
            command.handled = True
        if coord == [7, 1]:
            if command.is_double_click:
                gridBits.resetZoom()
                command.actions.appendAction("Grid Bits: Reset zoom")
            else:
                gridBits.zoomIn()
                command.actions.appendAction("Grid Bits: Zoom in")
            command.handled = True

# Process when in menu
def process_menu_mode(command):
    coord = [command.padX, command.padY]

    # Next/prev track
    if coord == [1, 0]:
        ui.previous()
        command.actions.appendAction("Channel Rack: Previous channel")
        command.handled = True
    if coord == [1, 1]:
        ui.next()
        command.actions.appendAction("Channel Rack: Next channel")
        command.handled = True

    # Cut, Copy, Paste
    if coord == [3, 0]:
        ui.copy()
        command.actions.appendAction("UI: Copy")
        command.handled = True
    if coord == [4, 0]:
        ui.cut()
        command.actions.appendAction("UI: Cut")
        command.handled = True
    if coord == [5, 0]:
        ui.paste()
        command.actions.appendAction("UI: Paste")
        command.handled = True

    # To piano roll
    if coord == [7, 1]:
        ui.showWindow(internalconstants.WINDOW_PIANO_ROLL)
        command.actions.appendAction("Sent to pianoroll")
        command.handled = True

def redraw(lights):
    if internal.extendedMode.query(eventconsts.INCONTROL_PADS):
        current_ui_mode = ui_mode.getMode()

        if current_ui_mode == 0:
            ui_button_colour = MENU_MODE_COLOUR
        else:
            ui_button_colour = BIT_MODE_COLOUR

        lights.setPadColour(0, 1, ui_button_colour)    

        if current_ui_mode == 0:
            redraw_menu_mode(lights)

        elif current_ui_mode == 1:
            redraw_bit_mode(lights)

    return

# Redraw when in menu
def redraw_menu_mode(lights):
    
    # Set colours for controls
    if internal.window.get_animation_tick() >= 1:
        lights.setPadColour(1, 1, lighting.UI_NAV_VERTICAL)     # Next track

    if internal.window.get_animation_tick() >= 2:
        lights.setPadColour(1, 0, lighting.UI_NAV_VERTICAL)     # Prev track
        lights.setPadColour(3, 0, lighting.UI_COPY)             # Copy
    if internal.window.get_animation_tick() >= 3:
        lights.setPadColour(4, 0, lighting.UI_CUT)              # Cut
    if internal.window.get_animation_tick() >= 4:
        lights.setPadColour(5, 0, lighting.UI_PASTE)            # Paste


    if internal.window.get_animation_tick() >= 3:
        lights.setPadColour(7, 1, lighting.UI_ACCEPT, 2)           # To piano roll

# Redraw when in grid bits
def redraw_bit_mode(lights):
    setGridBits(lights)

    # Set colours for controls
    if internal.window.get_animation_tick() >= 6:
        lights.setPadColour(4, 1, lighting.UI_NAV_HORIZONTAL)   # Move left
    if internal.window.get_animation_tick() >= 5:
        lights.setPadColour(5, 1, lighting.UI_NAV_HORIZONTAL)   # Move right
    if internal.window.get_animation_tick() >= 4:
        lights.setPadColour(6, 1, lighting.UI_ZOOM)             # Zoom out
    if internal.window.get_animation_tick() >= 3:
        lights.setPadColour(7, 1, lighting.UI_ZOOM)             # Zoom in


def activeStart():

    internal.extendedMode.setVal(True, eventconsts.INCONTROL_PADS)

    return

def activeEnd():

    # Reset Grid Bit controller
    gridBits.resetZoom()
    gridBits.resetScroll()
    ui_mode.resetMode()

    internal.extendedMode.revert(eventconsts.INCONTROL_PADS)

    return

def topWindowStart():
    internal.window.reset_animation_tick()

    return

def topWindowEnd():
    

    return


    # Internal functions

class gridBitMgr:
    scroll = 0
    zoom = 1

    def getBit(self, track, position):
        return channels.getGridBit(track, position*self.zoom + 8*self.scroll)
    
    def toggleBit(self, track, position):
        val = not channels.getGridBit(track, position*self.zoom + 8*self.scroll)
        return channels.setGridBit(track, position*self.zoom + 8*self.scroll, val)
    
    def resetScroll(self):
        self.scroll = 0

    def scrollLeft(self):
        if self.scroll > 0:
            self.scroll -= 1
        
    def scrollRight(self):
        self.scroll += 1

    def zoomOut(self):
        self.zoom *= 2
    
    def zoomIn(self):
        if self.zoom > 1: self.zoom = int(self.zoom / 2)

    def resetZoom(self):
        self.zoom = 1

gridBits = gridBitMgr()

def setGridBits(lights):
    current_track = channels.channelNumber()

    # Set scroll indicator
    light_num_scroll = gridBits.scroll
    if light_num_scroll < 8:

        if not gridBits.getBit(channels.channelNumber(), light_num_scroll):
            lights.setPadColour(light_num_scroll, 0, lighting.COLOUR_LIGHT_LILAC)
        else:
            lights.setPadColour(light_num_scroll, 0, lighting.COLOUR_PINK, 2)
         
    # Set zoom indicator
    light_num_zoom = 7 - int(math.log(gridBits.zoom, 2))
    if light_num_zoom >= 0 and internal.window.get_animation_tick() > 7:
        if not gridBits.getBit(channels.channelNumber(), light_num_zoom):
            lights.setPadColour(light_num_zoom, 0, lighting.COLOUR_LIGHT_LIGHT_BLUE)
        else:
            lights.setPadColour(light_num_zoom, 0, lighting.COLOUR_BLUE, 2)

    # If zoom and scroll lie on same pad
    if light_num_scroll == light_num_zoom:
        if not gridBits.getBit(channels.channelNumber(), light_num_zoom):
            lights.setPadColour(light_num_zoom, 0, lighting.COLOUR_LIGHT_YELLOW)
        else:
            lights.setPadColour(light_num_zoom, 0, lighting.COLOUR_PINK, 2)

    # Set remaining grid bits
    for i in range(8):
        if i <= internal.window.get_animation_tick():
            if gridBits.getBit(current_track, i):
                lights.setPadColour(i, 0, lighting.COLOUR_RED, 2)
            else:
                lights.setPadColour(i, 0, lighting.COLOUR_DARK_GREY)

    return

def processMuteSolo(channel, command):
    if command.value == 0: return
    if channels.isChannelSolo(channel):
        channels.soloChannel(channel)
        command.actions.appendAction("Unsolo channel " + str(channel))
        return
    channels.muteChannel(channel)
    if command.is_double_click:
        channels.soloChannel(channel)
        command.actions.appendAction("Solo channel " + str(channel))
    else: 
        if channels.isChannelMuted(channel):
            command.actions.appendAction("Mute channel " + str(channel))
        else: 
            command.actions.appendAction("Unmute channel " + str(channel))

def setVolume(command, track, value):
    volume = getVolumeSend(value)
    channels.setChannelVolume(track, volume)
    command.actions.appendAction("Set " + channels.getChannelName(track) + " volume to " + getVolumeValue(value))
    if internal.didSnap(internal.toFloat(value), internalconstants.CHANNEL_VOLUME_SNAP_TO):
        command.actions.appendAction("[Snapped]")

# Returns volume value set to send to FL Studio
def getVolumeSend(inVal):
    if config.ENABLE_SNAPPING:
        return internal.snap(internal.toFloat(inVal), internalconstants.CHANNEL_VOLUME_SNAP_TO)
    else: return internal.toFloat(inVal)


def getVolumeValue(inVal):
    
    return str(round(getVolumeSend(inVal) * 100)) + "%"

def setPan(command, track, value):
    volume = getPanSend(value)
    channels.setChannelPan(track, volume)
    command.actions.appendAction("Set " + channels.getChannelName(track) + " pan to " + getPanValue(value))
    if internal.didSnap(internal.toFloat(value, -1), internalconstants.CHANNEL_PAN_SNAP_TO):
        command.actions.appendAction("[Snapped]")

# Returns volume value set to send to FL Studio
def getPanSend(inVal):
    if config.ENABLE_SNAPPING:
        return internal.snap(internal.toFloat(inVal, -1), internalconstants.CHANNEL_PAN_SNAP_TO)
    else: return internal.toFloat(inVal, -1)


def getPanValue(inVal):
    
    a = round(getPanSend(inVal) * 100)
    if a < 0: b = str(a) + "% Left"
    elif a > 0: b = str(a) + "% Right"
    else: b = "Centred"
    return b