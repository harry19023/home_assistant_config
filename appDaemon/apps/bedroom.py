import appdaemon.plugins.hass.hassapi as hass
from datetime import timedelta

class Bedroom(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.night_temp = 65
    self.day_temp = 68
    self.run_in(self.fan_heater_init, 15)

    #listeners
    self.wake_up_handle = self.run_daily(self.wake_up_sleep, self.parse_time(self.globals.wake_up_time_hour_early), temp=self.day_temp)
    self.run_daily(self.wake_up_sleep, self.parse_time('22:00:00'), temp=self.night_temp)
    self.listen_state(self.heater, 'sensor.temperature_bedroom')
    self.listen_state(self.wake_up_change, 'input_datetime.wake_up_time')
    self.listen_event(self.bed_button, 'xiaomi_aqara.click')
    self.listen_state(self.fan_in_bed, 'switch.fan')

    self.log('Successfully initialized Bedroom!' , level='INFO')

  def wake_up_sleep(self, kwargs):
    temp = self.get_state('sensor.temperature_bedroom')
    if float(temp) < kwargs['temp'] and self.get_state('input_boolean.home') == 'on':
      self.turn_on('switch.heater')
      self.log('Turned on heater at ' + str(self.time()) + ', temp is ' + temp)
    else:
      self.turn_off('switch.heater')
      self.log('Turned off heater at ' + str(self.time()) + ', temp is ' + temp)

  def fan_heater_init(self, kwargs):
    fan = self.get_state('switch.fan')
    if fan == 'on':
      self.turn_on('input_boolean.in_bed')
    elif fan =='off':
      self.turn_off('input_boolean.in_bed')
    else:
      self.log('Fan changed but didn\'t do anything, state is ' + fan)
    home = self.get_state('input_boolean.home')
    new = self.get_state('sensor.temperature_bedroom')
    if home == 'on':
      if fan == 'on':
        if float(new) > self.night_temp: 
          self.turn_off('switch.heater')
          self.log('Turned off heater, temp is ' + new)
        else:
          self.turn_on('switch.heater')
          self.log('Turned on heater, temp is ' + new)
      else:
        if float(new) > self.day_temp: 
          self.turn_off('switch.heater')
          self.log('Turned off heater, temp is ' + new)
        else:
          self.turn_on('switch.heater')
          self.log('Turned on heater, temp is ' + new)
    else:
      self.turn_off('switch.heater')
      self.log('Turned off heater, noone is home')


  def fan_in_bed(self, entity, attribute, old, new, kwargs):
    fan = new
    if fan == 'on':
      self.turn_on('input_boolean.in_bed')
    elif fan =='off':
      self.turn_off('input_boolean.in_bed')
    else:
      self.log('Fan changed but didn\'t do anything, state is ' + fan)


  def heater(self, entity, attribute, old, new, kwargs):
    fan = self.get_state('input_boolean.in_bed')
    home = self.get_state('input_boolean.home')
    if home == 'on':
      if fan == 'on':
        if float(new) > self.night_temp: 
          self.turn_off('switch.heater')
          self.log('Turned off heater, temp is ' + new)
        else:
          self.turn_on('switch.heater')
          self.log('Turned on heater, temp is ' + new)
      else:
        if float(new) > self.day_temp: 
          self.turn_off('switch.heater')
          self.log('Turned off heater, temp is ' + new)
        else:
          self.turn_on('switch.heater')
          self.log('Turned on heater, temp is ' + new)
    else:
      self.turn_off('switch.heater')
      self.log('Turned off heater, noone is home')

  def wake_up_change(self, entity, attribute, old, new, kwargs):
    self.cancel_timer(self.wake_up_handle)
    self.run_in(self.get_new_wake_up, 5)

  def get_new_wake_up(self, kwargs):
    self.wake_up_handle = self.run_daily(self.wake_up_sleep, self.parse_time(self.globals.wake_up_time_hour_early), temp=self.day_temp)

  def bed_button(self, event_name, data, kwargs):
    button = data['entity_id']
    if button in ['binary_sensor.bed_switch_harry', 'binary_sensor.bed_switch_sage']:
      new = data['click_type']
      if new == 'single':
        self.toggle('switch.fan')
        self.log('Toggle fan because button was ' + new)
      elif new == 'long_click_press':
        self.toggle('light.bedroom')
        self.log('Toggle lights because button was ' + new)
      elif new == 'double':
        self.log('Did nothing because button was  ' + new)
      elif new == 'hold':
        self.log('Did nothing because button was  ' + new)
