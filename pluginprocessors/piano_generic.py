"""
pluginprocessors > _template.py

The file acts as a template for plugin handlers. Copy it and edit to add your own plugin handlers.
To get it to be imported by the event processor, add its filename (without the .py) to processplugins.py

Author: Miguel Guthridge [hdsq@outlook.com.au]
"""

# Add names of plugins your script can process to this list
PLUGINS = ["Originals - Firewood Piano", "Originals - Cinematic Soft Piano", 
           "Originals - Felt Piano", "Addictive Keys"]


# Import any modules you might need\
import pluginswrapper
import config
import internal
import eventconsts
import eventprocessor
import lightingconsts
import processorhelpers


def topPluginStart():
    """Called when plugin is top plugin (not neccesarily focused)
    """
    
    # Only in extended mode: uncomment lines to set inControl mode
    if internal.getPortExtended():
        # internal.extendedMode.setVal(False, eventconsts.INCONTROL_FADERS) # Faders
        # internal.extendedMode.setVal(False, eventconsts.INCONTROL_KNOBS) # Knobs
        # internal.extendedMode.setVal(False, eventconsts.INCONTROL_PADS) # Pads
        pass
    return

def topPluginEnd():
    """Called when plugin is no longer top plugin (not neccesarily focused)
    """
    
    # Only in extended mode: uncomment lines to revert to previous inControl modes
    if internal.getPortExtended():
        # internal.extendedMode.revert(eventconsts.INCONTROL_FADERS) # Faders
        # internal.extendedMode.revert(eventconsts.INCONTROL_KNOBS) # Knobs
        # internal.extendedMode.revert(eventconsts.INCONTROL_PADS) # Pads
        pass
    return

def activeStart():
    """Called when plugin brought to foreground (focused)
    """
    return

def activeEnd():
    """Called when plugin no longer in foreground (end of focused)
    """
    
    return

def redraw(lights):
    """Called when redrawing UI on pads. Set colours of lights here.

    Args:
        lights (LightMap): object containing state of lights for next redraw. 
            Modify the object using it's methods to set light colours.
    """
    return

def process(command):
    """Called when processing commands. 

    Args:
        command (ParsedEvent): contains useful information about the event. 
            Use this to determing what actions your processor will take.
    """
    
    # Add event processor to actions list (useful for debugging)
    command.actions.addProcessor("Your Processor Name")

    # When you handle your events, use command.handle("Some action") to handle events.
    if command.id == eventconsts.PEDAL:
        pluginswrapper.setCCParam(command.note, command.value)
        command.handle("Pedal", 1)

    return

def beatChange(beat):
    """Called when the beat updates

    Args:
        beat (int): Beat type (refer to FL Studio docs)
    """
    return
