import appdaemon.plugins.hass.hassapi as hass
import datetime

class Globals(hass.Hass):

  def initialize(self):
    self.defaultBrightToDimTime = "21:00:00"
    self.defaultDimToBrightTime = "9:30:00"
    self.defaultTransitionSeconds = 30
    self.concentrateRGB = [242,247,255]
    self.concentrateBrightness = 254
    self.relaxRGB = [255,195,55]
    self.relaxBrightness = 200
    self.lights = ["light.bedroom", "light.living_room"]
    self.wake_up_time = "07:30:00"
    self.log("Initialized Globals successfully!", level = "INFO")