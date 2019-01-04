import appdaemon.plugins.hass.hassapi as hass
import datetime

class Bathroom(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.humidity_shower = 65
    self.humidity_post_shower = 51
    self.dehum_min_on = 0
    self.dehum_min_max = 30
    self.humidity_away = 55

    self.turn_off('switch.dehumidifier')

    #listeners
    self.listen_state(self.lights_off, 'binary_sensor.motion_sensor_bathroom', new='off')
    self.listen_state(self.shower_dehumidify_listener, 'sensor.humidity_bathroom')
    self.listen_state(self.home_off, 'input_boolean.home', new='on')

    self.log('Successfully initialized Bathroom!' , level='INFO')

  def home_off(self, entity, attribute, old, new, kwargs):
    self.turn_off('switch.dehumidifier')

  def lights_off(self, entity, attribute, old, new, kwargs):
    door = self.get_state('binary_sensor.door_window_bathroom_door')
    humidity = self.get_state('sensor.humidity_bathroom')
    if door == 'on' and float(humidity) < self.humidity_shower:
      self.turn_off('light.bathroom')
      self.log('Turned off bathroom lights, door is open, no shower detected. humidity is ' + humidity)
    else:
      self.log('Didn\'t off bathroom lights, door is closed or shower is detected. humidity is ' + humidity)

  def shower_dehumidify_listener(self, entity, attribute, old, new, kwargs):
    humidity = self.get_state('sensor.humidity_bathroom')
    humidifier_status = self.get_state('switch.dehumidifier')
    home = self.get_state('input_boolean.home')
    if home == 'on':
      if (float(humidity) > self.humidity_shower) and (humidifier_status == 'off'):
        self.log('Shower detected, turning on dehumidifier (humidity:' + humidity)
        self.turn_on('switch.dehumidifier')
        self.run_in(self.turn_off_dehumidifier, 60)
    else:
      if (float(humidity) > self.humidity_away) and (humidifier_status == 'off'):
        self.log('Away humidity too high, (vaca: not) turning on dehumidifier (humidity: ' + humidity)
       # self.turn_on('switch.dehumidifier')
       # self.run_in(self.turn_off_dehumidifier, 60)

  def turn_off_dehumidifier(self, kwargs):
    self.dehum_min_on += 1
    humidity = self.get_state('sensor.humidity_bathroom')
    home = self.get_state('input_boolean.home')
    if float(humidity) < self.humidity_post_shower and home == 'on':
      self.turn_off('switch.dehumidifier')
      self.log('Turned off dehumidifier, humidity at ' + humidity)
      self.dehum_min_on = 0
    elif self.dehum_min_on > self.dehum_min_max:
      self.log('Dehumidifier has been on for ' + str(self.dehum_min_max) + ' minutes, turning off')
      self.log('Humidity was ' + humidity + ' when turned off')
      self.turn_off('switch.dehumidifier')
      self.run_in(self.reset_dehum_timer, 60*30)
    else:
      if self.dehum_min_on % 5 == 0:
        self.log('Still running, humidity:' + humidity +', min_on:' + str(self.dehum_min_on))
      self.run_in(self.turn_off_dehumidifier, 60)

  def reset_dehum_timer(self, kwargs):
    humidity = self.get_state('sensor.humidity_bathroom')
    self.log('Dehumidifier has been off for 30 mintutes, humidity at ' + humidity)
    self.dehum_min_on = 0
