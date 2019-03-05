import appdaemon.plugins.hass.hassapi as hass
from datetime import timedelta

class Nest(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')

    #listeners
    self.listen_state(self.home_away, 'input_boolean.home')

    self.log('Successfully initialized Nest!' , level='INFO')

  def home_away(self, entity, attribute, old, new, kwargs):
    if new == 'on':
      if self.now_is_between('07:00:00', '08:30:00'):
        self.call_service('climate/set_temperature', entity_id='climate.hallway', temperature='69')
      elif self.now_is_between('08:30:00', '21:00:00'):
        self.call_service('climate/set_temperature', entity_id='climate.hallway', temperature='67')
      elif self.now_is_between('21:00:00', '22:00:00'):
        self.call_service('climate/set_temperature', entity_id='climate.hallway', temperature='65')
      elif self.now_is_between('22:00:00', '07:00:00'):
        self.call_service('climate/set_temperature', entity_id='climate.hallway', temperature='62')
    else:
        self.call_service('climate/set_temperature', entity_id='climate.hallway', temperature='55')
