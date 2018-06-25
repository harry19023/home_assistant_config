import appdaemon.plugins.hass.hassapi as hass

class HomeAway(hass.Hass):

  def initialize(self):
    self.listen_event(self.front_door_button_pushed, 'front_door_button_pushed')
    self.log("Initialized Home Away successfully!", level="INFO")

  def front_door_button_pushed(self, event_name, data, kwargs):
    self.log("Front Door button was pushed", level="INFO")
    self.call_service('input_boolean/toggle', entity_id='input_boolean.home')
    self.log('input_boolean.home is now %s' % self.get_state('input_boolean.home'))
