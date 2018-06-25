import appdaemon.plugins.hass.hassapi as hass
import secrets
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


class ComputerControl(hass.Hass):

  def initialize(self):
    self.globals = self.get_app('globals')

    self.log('Successfully initialized computer control!' , level='INFO')


  def computer_on(self):
    self.call_service('wake_on_lan/send_magic_packet', mac=secrets.LivingRoom_MAC, broadcast_address=secrets.LivingRoom_IP)
    self.log('turned computer on', level='INFO')

  def computer_off(self):
    connection =ssh(secrets.LivingRoom_IP ,"LivingRoom", secrets.LivingRoom_password)
    connection.sendCommand("shutdown /h")
    self.log('turned computer off', level='INFO')
