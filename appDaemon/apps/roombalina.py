import appdaemon.plugins.hass.hassapi as hass

class Roombalina(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.listen_state(self.went_away, 'input_boolean.home', new='off')
    self.run_daily(self.cleaning_scheduler, self.parse_time('00:30:00'))
    self.log("Initialized Roombalina successfully!", level="INFO")

  def cleaning_scheduler(self, kwargs):
    if self.datetime().weekday() in [0,3]:
      self.turn_on('input_boolean.cleaning_needed')

  def went_away(self, entity, attribute, old, new, kwargs):
    if self.get_state('input_boolean.cleaning_needed') == 'on':
      self.run_in(self.run_scheduled, 1, clean_mode='border', fan_strength='strong')
      self.run_in(self.run_scheduled, 480, clean_mode='auto', fan_strength='standard')
      self.turn_off('input_boolean.cleaning_needed')

  def run_scheduled(self, kwargs):
    self.run(kwargs['clean_mode'], kwargs['fan_strength'])

  def run(self, clean_mode, fan_strength):
    self.call_service("vacuum/send_command", entity_id="vacuum.roombalina", command="Clean", params={"clean":{"type":clean_mode,"speed":fan_strength}})
    self.log("Ran Roombalina with clean_mode=%s and fan_strength=%s" % (clean_mode, fan_strength))
