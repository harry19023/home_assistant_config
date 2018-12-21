import appdaemon.plugins.hass.hassapi as hass

class MotionLight(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.sensor = self.args['sensor']
    self.light = self.args['light']

    #listeners
    self.listen_state(self.lights_on, self.sensor, new='on')
    if self.light == 'light.front_door':
      self.listen_state(self.lights_off, self.sensor, new='off')

    self.log('Successfully initialized ' + self.light + ' motion app!' , level='INFO')


  def lights_on(self, entity, attribute, old, new, kwargs):
    fan = self.get_state('input_boolean.in_bed')
    status = self.get_state(self.light)
    if status == 'off':
      if fan == 'on':
        if self.light == 'light.bedroom':
          self.log('Bedroom motion detected, but fan on so lights stay off', level='INFO')
          return
        self.turn_on(self.light, rgb_color=self.globals.nightlightRGB, brightness=self.globals.nightlightBrightness, transition=1)
        self.log('Turned on ' + self.light + ' dim because fas was on and motion was detected', level='INFO')
      else:
        self.turn_on(self.light)
      # self.log('Turned on ' + self.light + ' because motion was detected', level='INFO')

  def lights_off(self, entity, attribute, old, new, kwargs):
    self.turn_off(self.light)
   # self.log('Turned off ' + self.light)
