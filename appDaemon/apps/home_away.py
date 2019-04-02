import appdaemon.plugins.hass.hassapi as hass
from datetime import timedelta
import os, os.path
import random

class HomeAway(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.sound = self.get_app('sound')
    #listeners
    self.door_listener_handle = self.listen_state(self.front_door_open, 'binary_sensor.door_window_front_door', new='on')
    self.listen_event(self.leave_button, 'xiaomi_aqara.click')

    self.message_queue = []
    # self.run_in(self.test, 5)

    self.log('Successfully initialized Home/Away!' , level='INFO')

  def test(self, kwargs):
    self.queue_message('tts', message='test', length=2)
    self.queue_message('tts', message='Roombalina finished, but couldn\'t get home', length=5)
    self.queue_message('sound', path='away/bye_bye_bye.mp3', audio_type='audio/mp3', length=7)
    self.play_queue()


  def play_queue(self):
    for message in self.message_queue:
      self.log(message)
      if message[0] == 'tts':
        self.sound.tts(message[1], 0.7, message[2], 'media_player.bathroom_speaker')
      else:
        self.sound.play(message[1], message[2], 0.7, message[3], 'media_player.bathroom_speaker')
    self.message_queue = []


  def queue_message(self, type, **kwargs):
    if type == 'tts':
      if ('message' in kwargs) and ('length' in kwargs):
        self.message_queue.append(('tts', kwargs['message'], kwargs['length']))
      else:
        self.log('Called queue TTS with no message and/or length arg: ' + kwargs)
    elif type == 'sound':
      if ('path' in kwargs) and ('audio_type' in kwargs) and ('length' in kwargs):
        self.message_queue.append(('sound', kwargs['path'], kwargs['audio_type'], kwargs['length']))
      else:
        self.log('Called queue soung with no path, audio_type, and/or length arg: ' + kwargs)
    else:
      self.log('Called queue message with bad type: ' + str(type))


  def play_song(self, status):
    path = '/home/homeassistant/.homeassistant/www/sounds/'
    if status in ['home', 'away']:
      path = path + status
      song_list = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
      song_choice = random.randint(0, len(song_list))
      if song_choice == len(song_list):
        message = ''
        if status == 'home':
          message = 'Welcome home'
        else:
          message = 'Turning off the house'
        self.sound.tts(message, 0.7, 5, 'media_player.bathroom_speaker')
      else:
        self.sound.play(os.path.join(status + '/',song_list[song_choice]), 'audio/mp3', 0.7, 5, 'media_player.bathroom_speaker')
    else:
      self.log('called play_song with bad status: ' + str(status))


  def front_door_open(self, entity, attribute, old, new, kwargs):
    home = self.get_state('input_boolean.home')
    if home == 'off':
      self.turn_on('input_boolean.home')
      self.log('Turned house to home mode')
      self.turn_on('light.front_door')
      self.play_song('home')
      self.play_queue()


  def leave_button(self, event_name, data, kwargs):
    button = data['entity_id']
    if button == 'binary_sensor.front_door_switch':
      click = data['click_type']
      if click in ['single', 'long_click_press']:
        self.cancel_listen_state(self.door_listener_handle)
        self.turn_off('input_boolean.home')
        self.log('Turned house to away mode')
        self.run_in(self.turn_on_door_listener, 60)
        self.play_song('away')


  def turn_on_door_listener(self, kwargs):
    self.log('Listening for door again')
    self.door_listener_handle = self.listen_state(self.front_door_open, 'binary_sensor.door_window_front_door', new='on')
