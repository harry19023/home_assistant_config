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
    self.turn_on(self.light)
    self.log('Turned on ' + self.light + ' because motion was detected', level='INFO')

  def lights_off(self, entity, attribute, old, new, kwargs):
    self.turn_off(self.light)
    self.log('Turned off ' + self.light)
