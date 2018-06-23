import appdaemon.plugins.hass.hassapi as hass

class DefaultLights(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.light_turned_on_handles = []

    self.turn_on_light_listeners(kwargs=None)
    self.run_daily(self.transition, self.parse_time(self.globals.defaultDimToBrightTime), transition="dimToBright")
    self.run_daily(self.transition, self.parse_time(self.globals.defaultBrightToDimTime), transition="brightToDim")
    self.listen_state(self.home_away, 'input_boolean.home')

    self.log("Initialized DefaultLights successfully", level = "INFO")

  def home_away(self, entity, attribute, old, new, kwargs):
    if new == 'on':
      for light in self.globals.lights:
        self.turn_on(light)
      self.log('Turned all the lights on', level='INFO')
    else:
      for light in self.globals.lights:
        self.turn_off(light)
      self.log('Turned all the lights off', level='INFO')

  def light_turned_on(self, entity, attribute, old, new, kwargs):
    if self.now_is_between(self.globals.defaultDimToBrightTime, self.globals.defaultBrightToDimTime):
      self.turn_on(entity, rgb_color=self.globals.concentrateRGB, brightness=self.globals.concentrateBrightness, transition=1)
      self.log("Turned " + entity + " to concentrate", level="INFO")
    else:
      self.turn_on(entity, rgb_color=self.globals.relaxRGB, brightness=self.globals.relaxBrightness, transition=1) 
      self.log("Turned " + entity + " to relax", level="INFO")

  def transition(self, kwargs):
    transition = kwargs['transition']
    if transition == 'dimToBright':
      for light in self.globals.lights:
        if self.get_state(light) == "on":
          self.turn_on(light, rgb_color=self.globals.concentrateRGB, brightness=self.globals.concentrateBrightness, transition=1200)
          self.log("Transitioned " + light + " from dim to bright", level="INFO")
    elif transition == 'brightToDim':
      for light in self.globals.lights:
        if self.get_state(light) == "on":
          self.turn_on(light, rgb_color=self.globals.relaxRGB, brightness=self.globals.relaxBrightness,transition=1200)
          self.log("Transitioned " + light + " from bright to dim", level="INFO")
    else:
      self.log("Called transition with transition value of " + transition, level="INFO")

  def turn_off_light_listeners(self, time):
    for handle in self.light_turned_on_handles:
      self.cancel_listen_state(handle)
    self.light_turned_on_handels = []
    self.log("Turned off light listeners", level="INFO")
    self.run_in(self.turn_on_light_listeners, time)

  def turn_on_light_listeners(self, kwargs):
    self.light_turned_on_handles = []
    for light in self.globals.lights:
      self.light_turned_on_handles.append(self.listen_state(self.light_turned_on, light, old="off", new="on"))
      self.log("listening for " + light + " which is " + self.get_state(light), level="INFO")
    self.log("Turned on light listeners", level="INFO")
