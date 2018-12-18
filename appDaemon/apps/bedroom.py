import appdaemon.plugins.hass.hassapi as hass
from datetime import timedelta

class Bedroom(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.night_temp = 65
    self.day_temp = 68

    #listeners
    self.wake_up_handle = self.run_daily(self.wake_up_sleep, self.parse_time(self.globals.wake_up_time_hour_early), temp=self.day_temp)
    self.run_daily(self.wake_up_sleep, self.parse_time('22:00:00'), temp=self.night_temp)
    self.listen_state(self.heater, 'sensor.temperature_bedroom')
    self.listen_state(self.wake_up_change, 'input_datetime.wake_up_time')

    self.log('Successfully initialized Bedroom!' , level='INFO')

  def wake_up_sleep(self, kwargs):
    temp = self.get_state('sensor.temperature_bedroom')
    if float(temp) < kwargs['temp'] and self.get_state('input_boolean.home') == 'on':
      self.turn_on('switch.heater')
      self.log('Turned on heater at ' + str(self.time()) + ', temp is ' + temp)
    else:
      self.turn_off('switch.heater')
      self.log('Turned off heater at ' + str(self.time()) + ', temp is ' + temp)


  def heater(self, entity, attribute, old, new, kwargs):
    fan = self.get_state('switch.fan')
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

