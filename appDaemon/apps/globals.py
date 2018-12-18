import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta

class Globals(hass.Hass):

  def initialize(self):
    self.defaultBrightToDimTime = "21:00:00"
    self.defaultDimToBrightTime = "8:45:00"
    self.defaultTransitionSeconds = 30
    self.concentrateRGB = [242,247,255]
    self.concentrateBrightness = 254
    self.relaxRGB = [255,195,55]
    self.relaxBrightness = 200
    self.lights = ["light.bedroom", "light.living_room", "light.bathroom", "light.front_door"]
    self.wake_up_time = "08:00:00"
    self.wake_up_time_hour_early = '07:00:00'
    self.wake_up_time_20_min_early = '16:49:00'
    self.log("Successfully initialized Globals!", level = "INFO")

    self.listen_state(self.wake_up_change,  entity='input_datetime.wake_up_time')

  def wake_up_change(self, entity, attribute, old, new, kwargs):
    self.wake_up_time = new
    hour_new, min_new, sec_new = new.split(':')
    time =  datetime(2000, 1, 1,0,0,0) + timedelta(hours=int(hour_new), minutes=int(min_new), seconds=int(sec_new))
    time_hour_early = time - timedelta(hours=1)
    self.wake_up_time_hour_early = self.datetime_to_str(time_hour_early)
    time_20_early = time - timedelta(minutes=20)
    self.wake_up_time_20_min_early = self.datetime_to_str(time_20_early)
    self.log('wake up is ' + self.wake_up_time)
    self.log('20 early is ' + self.wake_up_time_20_min_early)
    self.log('hour early is '+ self.wake_up_time_hour_early)

  def datetime_to_str(self, dt):
    time_str = ''
    if dt.hour >= 10:
      time_str += str(dt.hour)
    else:
      time_str += '0' + str(dt.hour)

    if dt.minute >= 10:
      time_str += ':' + str(dt.minute)
    else:
      time_str += ':0' + str(dt.minute)

    if dt.second >= 10:
      time_str += ':' + str(dt.second)
    else:
      time_str += ':0' + str(dt.second)

    return time_str
