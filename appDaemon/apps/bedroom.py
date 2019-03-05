import appdaemon.plugins.hass.hassapi as hass
from datetime import timedelta

class Bedroom(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.night_temp = 62
    self.day_temp = 67
    self.run_in(self.heater_control, 5)

    #listeners
    self.wake_up_handle = self.run_daily(self.heater_control, self.parse_time(self.globals.wake_up_time_hour_early))
    cool_down_time = self.get_state('input_datetime.bed_time')
    self.bed_time_handle = self.run_daily(self.heater_control, self.parse_time(cool_down_time))
    self.listen_state(self.heater_temp_change, 'sensor.temperature_bedroom')
    self.listen_state(self.wake_up_change, 'input_datetime.wake_up_time')
    self.listen_state(self.bed_time_change, 'input_datetime.bed_time')
    self.listen_event(self.bed_button, 'xiaomi_aqara.click')
    self.listen_state(self.fan_in_bed, 'switch.fan')
    self.listen_state(self.home_away, 'input_boolean.home')

    self.log('Successfully initialized Bedroom!' , level='INFO')


  def heater_control(self, kwargs):
    fan = self.get_state('input_boolean.in_bed')
    home = self.get_state('input_boolean.home')
    new = self.get_state('sensor.temperature_bedroom')
    if home == 'on':
      if fan == 'on' or self.now_is_between(self.get_state('input_datetime.bed_time'), self.globals.wake_up_time_hour_early):
        if float(new) > self.night_temp: 
          self.turn_off('switch.heater')
          self.log('Turned off heater, fan is on or bed time, temp is ' + new)
        else:
          self.turn_on('switch.heater')
          self.log('Turned on heater, fan is on or bed time, temp is ' + new)
      else:
        if float(new) > self.day_temp: 
          self.turn_off('switch.heater')
          self.log('Turned off heater, fan is off or wakeup time, temp is ' + new)
        else:
          self.turn_on('switch.heater')
          self.log('Turned on heater, fan is off or wakeup time, temp is ' + new)
    else:
      self.turn_off('switch.heater')
      self.log('Turned off heater, noone is home')


  def fan_in_bed(self, entity, attribute, old, new, kwargs):
    fan = new
    if fan == 'on':
      self.turn_on('input_boolean.in_bed')
    elif fan =='off':
      self.turn_off('input_boolean.in_bed')


  def heater_temp_change(self, entity, attribute, old, new, kwargs):
    self.run_in(self.heater_control, 1)


  def home_away(self, entity, attribute, old, new, kwargs):
    self.run_in(self.heater_control, 1)


  def wake_up_change(self, entity, attribute, old, new, kwargs):
    self.cancel_timer(self.wake_up_handle)
    self.run_in(self.get_new_wake_up, 5)


  def get_new_wake_up(self, kwargs):
    self.wake_up_handle = self.run_daily(self.wake_up_sleep, self.parse_time(self.globals.wake_up_time_hour_early), temp=self.day_temp)


  def bed_time_change(self, entity, attribute, old, new, kwargs):
    self.cancel_timer(self.bed_time_handle)
    self.run_in(self.get_new_bed_time, 5)


  def get_new_bed_time(self, kwargs):
    self.bed_time_handle = self.run_daily(self.wake_up_sleep, self.parse_time(self.get_state('input_datetime.bed_time')), temp=self.night_temp)
    self.log('Reset night heater time to ' + self.get_state('input_datetime.bed_time'))


  def bed_button(self, event_name, data, kwargs):
    button = data['entity_id']
    if button in ['binary_sensor.bed_switch_harry', 'binary_sensor.bed_switch_sage']:
      new = data['click_type']
      if new == 'single':
        self.toggle('input_boolean.in_bed')
        self.toggle('switch.fan')
        self.log('Toggle fan because button was ' + new)
      elif new == 'long_click_press':
        self.toggle('light.bedroom')
        self.log('Toggle lights because button was ' + new)
      elif new == 'double':
        self.log('Did nothing because button was  ' + new)
      elif new == 'hold':
        self.log('Did nothing because button was  ' + new)
