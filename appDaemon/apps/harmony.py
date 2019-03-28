import appdaemon.plugins.hass.hassapi as hass
from paramiko import client

class Harmony(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.computer_control = self.get_app('computer_control')
    self.min_delay=0.01
    self.stream_devices = ['surround', 'whole_house', 'living_room_tv']
    self.ent_to_activity = {'surround':'stereo music', 'whole_house':'stereo music', 'living_room_tv':'Chromecast'}
    self.activity_to_volume = {'stereo music':45, 'Chromecast':35, 'Computer':35}

    #listeners
    self.listen_state(self.everything_off, 'input_boolean.home', new='off')
    self.listen_state(self.stream_on, 'media_player', new='playing')
    self.listen_state(self.stream_on, 'media_player.living_room_tv', old='off', new='idle')
    self.listen_state(self.stream_off, 'media_player', new='off')
    self.listen_state(self.harmony_change, 'remote.harmony_hub', attribute='current_activity')


    self.log('Successfully initialized Harmony!' , level='INFO')


  def everything_off(self, entity, attribute, old, new, kwargs):
    self.call_service('remote/turn_off', entity_id='remote.harmony_hub')
    self.log('Turned off Harmony', level='INFO')

  def stream_on(self, entity, attribute, old, new, kwargs):
    device, ent = self.split_entity(entity)
    #self.log('Stream_on_on called with ' + ent + ' new=' + new + ' old=' + old)
    if ent in self.stream_devices:
      current_activity = self.get_state('remote.harmony_hub', attribute='current_activity')
      if current_activity != self.ent_to_activity[ent]:
        self.call_service('remote/turn_on', entity_id='remote.harmony_hub', activity=self.ent_to_activity[ent])
        self.log("Turned on " + self.ent_to_activity[ent] + " because current_activity was " + current_activity)
      if old == 'off':
        self.call_service('media_player/volume_set', entity_id=entity, volume_level=1.0)
        self.log('Turned ' + ent + ' to max volume')

  def stream_off(self, entity, attribute, old, new, kwargs):
    device, ent = self.split_entity(entity)
    self.log('stream_off called with ' + ent + ' new=' + new + ' old=' + old)
    if ent in self.stream_devices:
      current_activity = self.get_state('remote.harmony_hub', attribute='current_activity')
      if current_activity == self.ent_to_activity[ent]:
        self.log('checking if ' + entity +' is off in 5 seconds')
        self.run_in(self.stream_still_off, 10, entity_id=entity)
        self.log('left stream_off function')

  def stream_still_off(self, kwargs):
    if self.get_state(kwargs['entity_id']) == 'off':
      self.log(kwargs['entity_id'] + ' is  still off, turning off')
      self.call_service('remote/turn_off', entity_id='remote.harmony_hub')
      self.log("Turned off the stereo")
    else:
      self.log(kwargs['entity_id'] + 'is still on, leaving on')

  def harmony_change(self, entity, attribute, old, new, kwargs):
    self.log('Harmony_change called with old=' + str(old) + ' new=' + str(new))
    if new == 'Computer':
      self.computer_control.computer_on()
      self.log('called computer_control.computer_on()', level='INFO')
    if new in self.activity_to_volume:
      self.call_service('remote/send_command', entity_id='remote.harmony_hub', device='53047637', command='VolumeDown', num_repeats=50, delay_secs=self.min_delay)
      self.call_service('remote/send_command', entity_id='remote.harmony_hub', device='53047637', command='VolumeUp', num_repeats=self.activity_to_volume[new], delay_secs=self.min_delay)
      self.log('Set ' + new + ' volume to ' + str(self.activity_to_volume[new]))
    if old == 'Computer':
      self.computer_control.computer_off() 
      self.log('called computer_control.computer_off()', level='INFO')
    if old in ['Chromecast', 'stereo music']:
      if old == 'Chromecast':
        self.call_service('media_player/turn_off', entity_id='media_player.living_room_tv')
        self.log('Turned off Living Room TV')
      else:
        self.call_service('media_player/turn_off', entity_id='media_player.surround')
        self.call_service('media_player/turn_off', entity_id='media_player.whole_house')
        self.log('Turned off Surround and Whole House')
