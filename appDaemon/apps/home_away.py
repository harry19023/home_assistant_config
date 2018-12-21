import appdaemon.plugins.hass.hassapi as hass
from datetime import timedelta

class HomeAway(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.sound = self.get_app('sound')
    #listeners
    self.door_listener_handle = self.listen_state(self.front_door_open, 'binary_sensor.door_window_front_door', new='on')
    self.listen_event(self.leave_button, 'xiaomi_aqara.click')

    self.log('Successfully initialized Home/Away!' , level='INFO')

  def front_door_open(self, entity, attribute, old, new, kwargs):
    home = self.get_state('input_boolean.home')
    if home == 'off':
      self.turn_on('input_boolean.home')
      self.log('Turned house to home mode')
      self.turn_on('light.front_door')
      self.sound.tts('Welcome home', 0.7, 5, 'media_player.bathroom_speaker')

  def leave_button(self, event_name, data, kwargs):
    button = data['entity_id']
    if button == 'binary_sensor.front_door_switch':
      click = data['click_type']
      if click in ['single', 'long_click_press']:
        self.cancel_listen_state(self.door_listener_handle)
        self.turn_off('input_boolean.home')
        self.log('Turned house to away mode')
        self.run_in(self.turn_on_door_listener, 60)
        self.sound.tts('Turning off the house', 0.7, 6, 'media_player.bathroom_speaker')

  def turn_on_door_listener(self, kwargs):
    self.log('Listening for door again')
    self.door_listener_handle = self.listen_state(self.front_door_open, 'binary_sensor.door_window_front_door', new='on')

  def announce_message(self, message):
    self.old_volume = self.get_state('media_player.bathroom_speaker', attribute='volume_level')
    self.log('volume was ' + str(self.old_volume))
    self.call_service('media_player/volume_set', entity_id='media_player.bathroom_speaker', volume_level=0.7)
    self.call_service('tts/google_say', entity_id='media_player.bathroom_speaker', message=message)
    self.run_in(self.reset_volume, 6)

  def reset_volume(self, kwargs):
    if self.old_volume is None:
      self.call_service('media_player/turn_off', entity_id='media_player.bathroom_speaker')
      self.log('Turned bathroom speaker back off')
    else:
      self.call_service('media_player/volume_set', entity_id='media_player.bathroom_speaker', volume_level=self.old_volume)
      self.log('reset volume to ' + str(self.old_volume))

