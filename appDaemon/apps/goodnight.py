import appdaemon.plugins.hass.hassapi as hass
import datetime

class Goodnight(hass.Hass):

  def initialize(self):
    self.globals = self.get_app("globals")
    self.listen_event(self.goodnight_button_pushed, "harry_goodnight_button_pushed")
    self.log("Initialized Goodnight successfully!", level = "INFO")

  def goodnight_button_pushed(self, event_name, data, kwargs):
    fan_state = self.get_state("switch.fan")
    if fan_state == "off":
      self.turn_on("switch.fan")
      for light in self.globals.lights:
        self.turn_off(light)
      self.call_service("remote/turn_off", entity_id="remote.harmony_hub")
      self.log("turning fan on, lights and TV off", level="INFO")
    else:
      self.turn_off("switch.fan")
      for light in self.globals.lights:
        self.turn_on(light)
      self.log("turning fan off and lights on", level="INFO")
