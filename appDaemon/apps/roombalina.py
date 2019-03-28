import appdaemon.plugins.hass.hassapi as hass

class Roombalina(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.home_away = self.get_app('home_away')

    self.listen_state(self.went_away, 'input_boolean.home', new='off')
    self.run_daily(self.cleaning_scheduler, self.parse_time('00:30:00'))
    # self.run_in(self.test, 1)
    self.result = None
    self.last_battery = 100

    self.log("Initialized Roombalina successfully!", level="INFO")


  def test(self, kwargs):
    status = self.get_state('vacuum.roombalina', attribute='status')
    self.log('status: ' + status)
    self.run_in(self.monitor, 5)

  def cleaning_scheduler(self, kwargs):
    if self.datetime().weekday() in [0,3]:
      self.turn_on('input_boolean.cleaning_needed')

  def went_away(self, entity, attribute, old, new, kwargs):
    if self.get_state('input_boolean.cleaning_needed') == 'on':
      self.run_in(self.monitor, 10)
      self.run_in(self.run_scheduled, 1, clean_mode='border', fan_strength='strong')
      self.run_in(self.run_scheduled, 480, clean_mode='auto', fan_strength='standard')
      self.turn_off('input_boolean.cleaning_needed')

  def run_scheduled(self, kwargs):
    self.run(kwargs['clean_mode'], kwargs['fan_strength'])

  def run(self, clean_mode, fan_strength):
    self.call_service("vacuum/send_command", entity_id="vacuum.roombalina", command="Clean", params={"clean":{"type":clean_mode,"speed":fan_strength}})
    self.log("Ran Roombalina with clean_mode=%s and fan_strength=%s" % (clean_mode, fan_strength))

  def monitor(self, kwargs):
    status = self.get_state('vacuum.roombalina', attribute='status')
    if status in ['edge', 'auto']: # still cleaning
      # self.log('Still cleaning')
      self.run_in(self.monitor, 300)
    elif status == 'stop': # either stuck or trying to re-charge
      battery = self.get_state('vacuum.roombalina', attribute='battery_level')
      # self.log('battery: ' + str(battery))
      if battery > 20: # got stuck before trying to re-charge
        # self.log('Got stuck')
        self.last_battery = 100
        self.report('stuck')
      else:
        if battery == self.last_battery:
          # self.log('died while trying to charge')
          self.last_battery = 100
          self.report('finished_and_died')
        else:
         #  self.log('trying to recharge, battery: ' + str(battery))
          self.last_battery = battery
          self.run_in(self.monitor, 1200)
    elif status == 'charging': # success!
      # self.log('finished!')
      self.last_battery = 100
      self.report('finished')
    else:
      self.log('ERROR: Unexpected status: ' + status)

  def report(self, status):
    if status == 'finished':
      message = 'Roombalina ran. Be sure to clean her!'
      self.home_away.queue_message('tts', message=message, length=5)
    elif status == 'finished_and_died':
      message = 'Roombalina finished, but didn\'t make it home.'
      self.home_away.queue_message('tts', message=message, length=4)
    elif status == 'stuck':
      message = 'Roombalina got stuck before finishing'
      self.home_away.queue_message('tts', message=message, length=4)
    else:
      self.log('Called report with unknown status: ' + str(status))
