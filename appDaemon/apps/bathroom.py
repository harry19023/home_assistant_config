import appdaemon.plugins.hass.hassapi as hass
import datetime

class Bathroom(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.humidity_shower = 65
    self.humidity_post_shower = 51
    self.dehum_min_on = 0
    self.dehum_min_max = 30
    self.humidity_away = 48

    self.run_in(self.init_humidity_check, 5)

    #listeners
    self.listen_state(self.lights_off, 'binary_sensor.motion_sensor_bathroom', new='off')
    self.listen_state(self.shower_listener, 'sensor.humidity_bathroom')
    self.listen_state(self.home_listener, 'input_boolean.home')

    self.log('Successfully initialized Bathroom!' , level='INFO')


  def init_humidity_check(self, kwargs):
    bath_humidity = self.get_state('sensor.humidity_bathroom')
    bed_humidity = self.get_state('sensor.humidity_bedroom')
    humid_status = self.get_state('switch.dehumidifier')
    home = self.get_state('input_boolean.home')
    if home == 'on':
      if humid_status == 'on':
        self.humidity_post_shower = float(self.get_state('sensor.humidity_bedroom'))
        self.run_in(self.shower_timer, 1)
      else:
        self.set_lasts()
    else:
      if bed_humidity > self.humidity_away:
        self.run_in(self.away_dehumidifier, 5)
      else:
        self.turn_off('switch.dehumidifier')


  def shower_listener(self, entity, attribute, old, new, kwargs):
    humidity = self.get_state('sensor.humidity_bathroom')
    humid_status = self.get_state('switch.dehumidifier')
    self.log('Humidity: ' + humidity)
    if humid_status == 'off':
      # if humidity jumps more than 5 in one reading, its a shower
      if float(humidity) > float(self.last_humidity) + 5:
        self.log('Shower detected, last humidity: ' + self.last_humidity)
        self.humidity_post_shower = float(self.get_state('sensor.humidity_bedroom'))
        self.turn_on('switch.dehumidifier')
        self.set_lasts()
        self.run_in(self.shower_timer, 60)
      elif float(humidity) > float(self.last_humidity):
        # if humidity jumps twice in 3 minutes, its a shower
        if (self.datetime() - self.last_time).total_seconds() / 60 < 3:
          self.turn_on('switch.dehumidifier')
          self.log('Shower detected, last humidity was less than 5 minutes ago: ' + self.last_humidity)
          self.humidity_post_shower = float(self.get_state('sensor.humidity_bedroom'))
          self.run_in(self.shower_timer, 60)
          self.set_lasts()
        else:
          self.set_lasts()
      else:
          self.set_lasts()
    else:
      self.set_lasts()


  def home_listener(self, entity, attribute, old, new, kwargs):
    if new == 'on':
      self.turn_off('switch.dehumidifier')
      status = self.get_state('switch.dehumidifier')
      self.log('turning off dehum b\c home, status: ' + status)
      self.set_lasts()
    else:
      self.run_in(self.away_dehumidifier, 20)

  def lights_off(self, entity, attribute, old, new, kwargs):
    door = self.get_state('binary_sensor.door_window_bathroom_door')
    if door == 'on':
      self.turn_off('light.bathroom')


  def away_dehumidifier(self, kwargs):
    humidity = self.get_state('sensor.humidity_bedroom')
    if (float(humidity) > self.humidity_away):
      self.log('Away humidity too high, turning on dehumidifier (humidity: ' + humidity)
      self.turn_on('switch.dehumidifier')
      self.run_in(self.away_dehumidifier, 60*15)
    else:
      self.turn_off('switch.dehumidifier')
      self.log('Away humidity low, turning off dehumidifier (humidity: ' + humidity)


  def shower_timer(self, kwargs):
    self.dehum_min_on += 1
    humidity = self.get_state('sensor.humidity_bathroom')
    home = self.get_state('input_boolean.home')
    if home == 'on':
      if float(humidity) < self.humidity_post_shower:
        self.turn_off('switch.dehumidifier')
        self.log('Turned off dehumidifier, humidity at ' + humidity)
        self.dehum_min_on = 0
        self.set_lasts()
      elif self.dehum_min_on > self.dehum_min_max:
        self.log('Dehumidifier has been on for ' + str(self.dehum_min_max) + ' minutes, turning off')
        self.log('Humidity was ' + humidity + ' when turned off')
        self.turn_off('switch.dehumidifier')
        self.dehum_min_on = 0
        self.set_lasts()
      else:
        if self.dehum_min_on % 5 == 0:
          self.log('Still running, humidity:' + humidity +', min_on:' + str(self.dehum_min_on))
        self.run_in(self.shower_timer, 60)
    else:
      self.log('shower timer canceled because no one is home anymore')


  def set_lasts(self):
    self.last_humidity = self.get_state('sensor.humidity_bathroom')
    self.last_time = self.datetime()
