import appdaemon.plugins.hass.hassapi as hass
from paramiko import client

class ssh:
  client = None

  def __init__(self, address, username, password):
    print("Connecting to server.")
    self.client = client.SSHClient()
    self.client.set_missing_host_key_policy(client.AutoAddPolicy())
    self.client.connect(address, username=username, password=password, look_for_keys=False)

  def sendCommand(self, command):
    if(self.client):
      stdin, stdout, stderr = self.client.exec_command(command)
      while not stdout.channel.exit_status_ready():
        # Print data when available
        if stdout.channel.recv_ready():
          alldata = stdout.channel.recv(1024)
          prevdata = b"1"
          while prevdata:
            prevdata = stdout.channel.recv(1024)
            alldata += prevdata

          print(str(alldata, "utf8"))
    else:
      print("Connection not opened.")


class Harmony(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')
    self.computer_control = self.get_app('computer_control')

    self.listen_state(self.computer_on, 'remote.harmony_hub', attribute='current_activity', new='Computer')
    self.listen_state(self.computer_off, 'remote.harmony_hub', attribute='current_activity', old='Computer')
    self.listen_state(self.everything_off, 'input_boolean.home', new='off')

    self.log('Successfully initialized Harmony!' , level='INFO')

  def computer_on(self, entity, attribute, old, new, kwargs):
    self.computer_control.computer_on()
    self.log('called computer_control.computer_on()', level='INFO')

  def computer_off(self, entity, attribute, old, new, kwargs):
    self.computer_control.computer_off() 
    self.log('called computer_control.computer_off()', level='INFO')

  def everything_off(self, entity, attribute, old, new, kwargs):
    self.call_service('remote/turn_off', entity_id='remote.harmony_hub')
    self.log('Turned off Harmony', level='INFO')
