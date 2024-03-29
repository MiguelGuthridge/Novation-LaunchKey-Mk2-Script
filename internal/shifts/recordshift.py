"""
internal > shifts > recordshift.py

Contains class to manage shift mode for recording options

Author: Miguel Guthridge [hdsq@outlook.com.au]
"""

import general
import ui
import transport

from ..shiftstate import ShiftState
from ..windowstate import window
import config
import eventconsts
from .. import consts
import lightingconsts
from ..state import extendedMode
from ..misc import beat

class RecordShift(ShiftState):
    def __init__(self):
        """Creates instance of ShiftState object

        Args:
            name (str): Name of shift button
            id_listen (int): Event ID for a shift button. This is checked when determining whether to enable shift.
        """
        self.name = "Record"
        self.id_listen = eventconsts.TRANSPORT_RECORD
        
        self.enable_sustain = True
        self.is_down = False
        self.is_sustained = False
        self.is_used = False
        
    def process(self, command):
        """Process commands in record shift menu

        Args:
            command (ParsedEvent): Event to process
        """
        command.addProcessor("Record shift menu")
        if command.type == eventconsts.TYPE_PAD:
            if command.is_lift:
                coord = command.getPadCoord()
                if coord == (0, 0):
                    transport.globalTransport(eventconsts.midi.FPT_Metronome, 1)
                    command.handle("Toggled metronome")
                    self.use()
                    
                elif coord == (1, 0):
                    transport.globalTransport(eventconsts.midi.FPT_WaitForInput, True)
                    command.handle("Toggled wait for input")
                    self.use()
                    
                elif coord == (2, 0):
                    transport.globalTransport(eventconsts.midi.FPT_CountDown, True)
                    command.handle("Toggled record countdown")
                    self.use()
                    
                elif coord == (3, 0):
                    transport.globalTransport(eventconsts.midi.FPT_Overdub, True)
                    command.handle("Toggled overdub")
                    self.use()

                elif coord == (4, 0):
                    transport.globalTransport(eventconsts.midi.FPT_LoopRecord, True)
                    command.handle("Toggled loop record")
                    self.use()
                    
                elif coord == (2, 1):
                    transport.globalTransport(eventconsts.midi.FPT_StepEdit, True)
                    command.handle("Toggled step editing")
                    self.use()
                
                elif coord == (7, 1):
                    transport.globalTransport(eventconsts.midi.FPT_TapTempo, True)
                    command.handle("Tapped Tempo")
                    self.use()
                    
                else:
                    command.handle("Shift menu catch others")

            else:
                command.handle("Shift menu catch press")

        
    def redraw(self, lights):
        """Redraw in shift menu

        Args:
            lights (LightMap): Lights to draw onto
        """
        if window.getAnimationTick() > 0:
            # Metronome
            if general.getUseMetronome():
                mode = lightingconsts.MODE_PULSE
            else:
                mode = lightingconsts.MODE_ON
            lights.setPadColour(0, 0, lightingconsts.colours["WHITE"], mode)
            
            # Tempo tapper
            lights.setPadColour(7, 1, lightingconsts.TEMPO_TAP)

        if window.getAnimationTick() > 1:
            # Wait for input
            if ui.isStartOnInputEnabled():
                mode = lightingconsts.MODE_PULSE
            else:
                mode = lightingconsts.MODE_ON
            lights.setPadColour(1, 0, lightingconsts.colours["LIGHT BLUE"], mode)
            
        if window.getAnimationTick() > 2:
            # Count down
            if ui.isPrecountEnabled():
                mode = lightingconsts.MODE_PULSE
            else:
                mode = lightingconsts.MODE_ON
            lights.setPadColour(2, 0, lightingconsts.colours["GREEN"], mode)
            
            # Step editing
            lights.setPadColour(2, 1, lightingconsts.colours["YELLOW"])

        if window.getAnimationTick() > 3:
            # Overdub
            lights.setPadColour(3, 0, lightingconsts.colours["BLUE"])
        
        if window.getAnimationTick() > 4:
            # Loop recording
            if ui.isLoopRecEnabled():
                mode = lightingconsts.MODE_PULSE
            else:
                mode = lightingconsts.MODE_ON
            lights.setPadColour(4, 0, lightingconsts.colours["ORANGE"], mode)
            
            

        lights.solidifyAll()

    def onPress(self):
        """When shift button is pressed
        """
        extendedMode.setVal(True, eventconsts.INCONTROL_PADS)
        
    def onLift(self):
        """When shift button is lifted
        """
        extendedMode.revert(eventconsts.INCONTROL_PADS)
        
            