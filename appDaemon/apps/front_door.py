import appdaemon.plugins.hass.hassapi as hass
import datetime
class FrontDoor(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.vacuum_ran = False
    self.listen_event(self.front_door_button_pushed, "front_door_button_pushed")
    self.run_daily(self.reset_vacuum_ran, datetime.time(0,30,0))
    self.log("Initialized Front Door successfully!", level="INFO")

  def front_door_button_pushed(self, event_name, data, kwargs):
    self.log("Front Door button was pushed", level="INFO")
    lights_on = False
    for light in self.globals.lights:
      if self.get_state(light) == 'on':
        lights_on = True
        self.log("Found light on: " + light, level="INFO")
        break

    if lights_on:
      self.call_service("remote/turn_off", entity_id="remote.harmony_hub")

      if self.datetime().weekday() in [0,3]:
        if self.vacuum_ran == False:
          self.roombalina = self.get_app('roombalina')
          self.roombalina.run('border','strong')
          self.run_in(self.roombalina.run, 480, clean_mode="auto", fan_strength="standard")
          self.vacuum_ran = True
      for light in self.globals.lights:
        self.turn_off(light)

      self.log("Turned the lights and TV off", level="INFO")
    else:
      for light in self.globals.lights:
        self.turn_on(light)
      self.log("Turned on the lights", level="INFO")

  def reset_vacuum_ran(self, kwargs):
    self.vacuum_ran = False
