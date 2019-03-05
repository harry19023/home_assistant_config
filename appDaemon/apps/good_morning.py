import appdaemon.plugins.hass.hassapi as hass
import datetime
class GoodMorning(hass.Hass):

  def initialize(self):
    self.globals = self.get_app("globals")
    self.default_lights = self.get_app("default_lights")
    self.alarm_handle = self.run_daily(self.wake_up, self.parse_time(self.globals.wake_up_time_20_min_early))
    self.listen_state(self.alarm_changed, 'input_datetime.wake_up_time')

    self.log("Initialized Good Morning successfully!", level = "INFO")

  def wake_up(self, kwargs):
    day_of_week = self.datetime().weekday()
    if self.get_state('input_boolean.alarm_on') == 'on' and self.get_state('input_boolean.home') == 'on':
      self.default_lights.turn_off_light_listeners(10)
      for light in self.globals.lights:
        self.turn_on(light, rgb_color=self.globals.relaxRGB, brightness=self.globals.relaxBrightness, transition=900)

    self.call_service('input_datetime/set_datetime', entity_id='input_datetime.wake_up_time',time = self.globals.wake_up_time)
    if day_of_week in [0,1,2,3,6]:
      self.turn_on('input_boolean.alarm_on')
    else:
      self.turn_off('input_boolean.alarm_on')

  def alarm_changed(self, entity, attribute, old, new, kwargs):
    self.cancel_timer(self.alarm_handle)
    self.run_in(self.update_alarm, 5)

  def update_alarm(self, kwargs):
    self.alarm_handle = self.run_daily(self.wake_up, self.parse_time(self.globals.wake_up_time_20_min_early))
    self.log('Reset wake up time to ' + new_time)
    self.turn_on('input_boolean.alarm_on')

