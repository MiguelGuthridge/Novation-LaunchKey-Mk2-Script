"""
windowprocessors > processchannelrack.py

This script handles events when the channel rack is active.
It provides functionality including modification of grid bits, setting channel volumes/pans, and copy-pasting between tracks.

Author: Miguel Guthridge [hdsq@outlook.com.au]
"""

import math # For logarithm

import channels
import ui

import lightingconsts
import config
import internal.consts
import internal
import eventconsts
import processorhelpers

MENU_MODE_COLOUR = lightingconsts.UI_CHOOSE
BIT_MODE_COLOUR = lightingconsts.colours["RED"]

def process(command):

    command.actions.addProcessor("Channel rack Processor")

    current_channel = channels.selectedChannel()

    #---------------------------------
    # Pads
    #---------------------------------
    if command.type == eventconsts.TYPE_PAD:
        
        # UI Mode
        ui_mode.process(command)
        
        if not command.handled:
            command.handle("Drum pads catch-all", True)

    #---------------------------------
    # Faders
    #---------------------------------
    if command.type == eventconsts.TYPE_FADER:
        fader_num = command.coord_X

        if fader_num == 8 and not internal.shifts["MAIN"].use():
            channel_num = current_channel
        else:
            channel_num = fader_num

        setVolume(command, channel_num, command.value)

    #---------------------------------
    # Knobs
    #---------------------------------
    if command.type == eventconsts.TYPE_KNOB:
        knob_num = command.coord_X

        if knob_num == 7 and not internal.shifts["MAIN"].use():
            channel_num = current_channel
        else:
            channel_num = knob_num

        setPan(command, channel_num, command.value)


    #---------------------------------
    # Mixer Buttons - mute/solo tracks
    #---------------------------------
    if command.type == eventconsts.TYPE_FADER_BUTTON:
        fader_num = command.coord_X
        print(fader_num)
        if fader_num == 8 and not internal.shifts["MAIN"].use():
            channel_num = current_channel
        else:
            channel_num = fader_num

        processMuteSolo(channel_num, command)

    return

def redraw(lights):
    if internal.extendedMode.query(eventconsts.INCONTROL_PADS):
        ui_mode.redraw(lights)

    return


# Process when in grid bits
def processBitMode(command):
    current_channel = channels.selectedChannel()
    
    if command.type == eventconsts.TYPE_PAD and command.is_lift:
        # Grid bits
        if command.coord_Y == 0 and command.coord_X != 8:
            
            if channels.channelCount() <= current_channel:
                command.handle("Channel out of range", silent=True)
                return
            
            gridBits.toggleBit(current_channel, command.coord_X)
            command.handle("Grid Bits: Toggle bit")
        
        coord = [command.coord_X, command.coord_Y]


        # Scroll grid bits
        if coord == [4, 1]:
            if command.is_double_click:
                gridBits.resetScroll()
                command.handle("Grid Bits: Reset scroll")
            else:
                gridBits.scrollLeft()
                command.handle("Grid Bits: Scroll left")
        if coord == [5, 1]:
            gridBits.scrollRight()
            command.handle("Grid Bits: Scroll right")
        # Zoom grid bits
        if coord == [6, 1]:
            gridBits.zoomOut()
            command.handle("Grid Bits: Zoom out")
        if coord == [7, 1]:
            if command.is_double_click:
                gridBits.resetZoom()
                command.handle("Grid Bits: Reset zoom")
            else:
                gridBits.zoomIn()
                command.handle("Grid Bits: Zoom in")

# Process when in menu
def processMenuMode(command):
    if command.is_lift:
        coord = [command.coord_X, command.coord_Y]
        
        # Next/prev track
        if coord == [0, 0]:
            ui.previous()
            command.handle("Channel Rack: Previous channel")
        elif coord == [0, 1]:
            ui.next()
            command.handle("Channel Rack: Next channel")

        # Cut, Copy, Paste
        elif coord == [2, 0]:
            ui.cut()
            command.handle("UI: Cut")
        elif coord == [3, 0]:
            ui.copy()
            command.handle("UI: Copy")
        elif coord == [4, 0]:
            ui.paste()
            command.handle("UI: Paste")

        # To piano roll
        elif coord == [7, 1]:
            ui.showWindow(internal.consts.WINDOW_PIANO_ROLL)
            command.handle("Sent to pianoroll")

        # Plugin window
        elif coord == [6, 1]:
            channels.showEditor(channels.channelNumber())
            command.handle("Opened plugin window")


# Redraw when in menu
def redrawMenuMode(lights):
    
    # Set colours for controls
    if internal.window.getAnimationTick() >= 1:
        lights.setPadColour(0, 1, lightingconsts.UI_NAV_VERTICAL)     # Next track

    if internal.window.getAnimationTick() >= 2:
        lights.setPadColour(0, 0, lightingconsts.UI_NAV_VERTICAL)     # Prev track
        lights.setPadColour(2, 0, lightingconsts.UI_COPY)             # Copy
    if internal.window.getAnimationTick() >= 3:
        lights.setPadColour(3, 0, lightingconsts.UI_CUT)              # Cut
    if internal.window.getAnimationTick() >= 4:
        lights.setPadColour(4, 0, lightingconsts.UI_PASTE)            # Paste

    if internal.window.getAnimationTick() >= 2:
        lights.setPadColour(6, 1, lightingconsts.UI_CHOOSE)
    if internal.window.getAnimationTick() >= 3:
        lights.setPadColour(7, 1, lightingconsts.UI_ACCEPT, lightingconsts.MODE_PULSE)           # To piano roll

# Redraw when in grid bits
def redrawBitMode(lights):
    setGridBits(lights)

    # Set colours for controls
    if internal.window.getAnimationTick() >= 6:
        lights.setPadColour(4, 1, lightingconsts.UI_NAV_HORIZONTAL)   # Move left
    if internal.window.getAnimationTick() >= 5:
        lights.setPadColour(5, 1, lightingconsts.UI_NAV_HORIZONTAL)   # Move right
    if internal.window.getAnimationTick() >= 4:
        lights.setPadColour(6, 1, lightingconsts.UI_ZOOM)             # Zoom out
    if internal.window.getAnimationTick() >= 3:
        lights.setPadColour(7, 1, lightingconsts.UI_ZOOM)             # Zoom in


def activeStart():
    internal.extendedMode.setVal(True, eventconsts.INCONTROL_PADS)
    return

def activeEnd():
    
    
    internal.extendedMode.revert(eventconsts.INCONTROL_PADS)
    return

def topWindowStart():
    
    return

def topWindowEnd():
    # Reset Grid Bit controller
    gridBits.resetZoom()
    gridBits.resetScroll()
    ui_mode.resetMode()
    return

def beatChange(beat):
    pass

# Internal functions

class GridBitMgr:
    scroll = 0
    zoom = 1
    
    def drawHighlight(self):
        current_ch = channels.channelNumber()
        
        left = 8*self.scroll
        right = 8*self.zoom
        top = current_ch
        bottom = 1
        
        ui.crDisplayRect(left, top, right, bottom, 1000)

    def getBit(self, track, position):
        return channels.getGridBit(track, position*self.zoom + 8*self.scroll)
    
    def toggleBit(self, track, position):
        val = not channels.getGridBit(track, position*self.zoom + 8*self.scroll)
        return channels.setGridBit(track, position*self.zoom + 8*self.scroll, val)
    
    def resetScroll(self):
        self.scroll = 0
        self.drawHighlight()

    def scrollLeft(self):
        if self.scroll > 0:
            self.scroll -= 1
        self.drawHighlight()
        
    def scrollRight(self):
        self.scroll += 1
        self.drawHighlight()

    def zoomOut(self):
        self.zoom *= 2
        self.drawHighlight()
    
    def zoomIn(self):
        if self.zoom > 1: self.zoom = int(self.zoom / 2)
        self.drawHighlight()

    def resetZoom(self):
        self.zoom = 1
        self.drawHighlight()

gridBits = GridBitMgr()

def setGridBits(lights):
    current_track = channels.selectedChannel()

    if channels.channelCount() <= current_track:
        return

    # Set scroll indicator
    light_num_scroll = gridBits.scroll
    if light_num_scroll < 8:

        if not gridBits.getBit(current_track, light_num_scroll):
            lights.setPadColour(light_num_scroll, 0, lightingconsts.colours["LIGHT LILAC"])
        else:
            lights.setPadColour(light_num_scroll, 0, lightingconsts.colours["PINK"], lightingconsts.MODE_PULSE)
         
    # Set zoom indicator
    light_num_zoom = 7 - int(math.log(gridBits.zoom, 2))
    if light_num_zoom >= 0 and internal.window.getAnimationTick() > 7:
        if not gridBits.getBit(current_track, light_num_zoom):
            lights.setPadColour(light_num_zoom, 0, lightingconsts.colours["LIGHT LIGHT BLUE"])
        else:
            lights.setPadColour(light_num_zoom, 0, lightingconsts.colours["BLUE"], lightingconsts.MODE_PULSE)

    # If zoom and scroll lie on same pad
    if light_num_scroll == light_num_zoom:
        if not gridBits.getBit(current_track, light_num_zoom):
            lights.setPadColour(light_num_zoom, 0, lightingconsts.colours["LIGHT YELLOW"])
        else:
            lights.setPadColour(light_num_zoom, 0, lightingconsts.colours["PINK"], lightingconsts.MODE_PULSE)

    # Set remaining grid bits
    for i in range(8):
        if i <= internal.window.getAnimationTick():
            if gridBits.getBit(current_track, i):
                lights.setPadColour(i, 0, lightingconsts.colours["RED"], lightingconsts.MODE_PULSE)
            else:
                lights.setPadColour(i, 0, lightingconsts.colours["DARK GREY"])

    return

def processMuteSolo(channel, command):

    if channels.channelCount() <= channel:
        command.handle("Channel out of range. Couldn't process mute", silent=True)
        return

    if command.value == 0: return
    if channels.isChannelSolo(channel) and channels.channelCount() != 1:
        channels.soloChannel(channel)
        action = "Unsolo channel"
        
    elif command.is_double_click:
        channels.soloChannel(channel)
        action = "Solo channel"
    else: 
        channels.muteChannel(channel)
        if channels.isChannelMuted(channel):
            action = "Mute channel"
        else: 
            action = "Unmute channel"

    command.handle(action)

def setVolume(command, channel, value):

    if channels.channelCount() <= channel:
        command.handle("Channel out of range. Couldn't set volume", silent=True)
        return

    volume = getVolumeSend(value)
    channels.setChannelVolume(channel, volume)
    action = "Set " + channels.getChannelName(channel) + " volume to " + getVolumeValue(value)
    if processorhelpers.didSnap(processorhelpers.toFloat(value), internal.consts.CHANNEL_VOLUME_SNAP_TO):
        action += " [Snapped]"
    command.handle(action)

def setPan(command, channel, value):
    if channels.channelCount() <= channel:
        command.handle("Channel out of range. Couldn't set pan", silent=True)
        return

    volume = getPanSend(value)
    channels.setChannelPan(channel, volume)
    action = "Set " + channels.getChannelName(channel) + " pan to " + getPanValue(value)
    if processorhelpers.didSnap(processorhelpers.toFloat(value, -1), internal.consts.CHANNEL_PAN_SNAP_TO):
        action = "[Snapped]"
    command.handle(action)

# Returns volume value set to send to FL Studio
def getVolumeSend(inVal):
    if config.ENABLE_SNAPPING:
        return processorhelpers.snap(processorhelpers.toFloat(inVal), internal.consts.CHANNEL_VOLUME_SNAP_TO)
    else: return processorhelpers.toFloat(inVal)


def getVolumeValue(inVal):
    
    return str(round(getVolumeSend(inVal) * 100)) + "%"



# Returns volume value set to send to FL Studio
def getPanSend(inVal):
    if config.ENABLE_SNAPPING:
        return processorhelpers.snap(processorhelpers.toFloat(inVal, -1), internal.consts.CHANNEL_PAN_SNAP_TO)
    else: return processorhelpers.toFloat(inVal, -1)


def getPanValue(inVal):
    
    a = round(getPanSend(inVal) * 100)
    if a < 0: b = str(a) + "% Left"
    elif a > 0: b = str(a) + "% Right"
    else: b = "Centred"
    return b

#
# UI Mode settings
#

ui_mode = processorhelpers.UiModeHandler()
ui_mode.addMode("Menu", lightingconsts.UI_CHOOSE, processMenuMode, redrawMenuMode)
ui_mode.addMode("Grid Bits", lightingconsts.colours["RED"], processBitMode, redrawBitMode)

