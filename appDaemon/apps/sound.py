import appdaemon.plugins.hass.hassapi as hass
from queue import Queue
from threading import Thread
from threading import Event
import time
#
# App to manage announcements via TTS and stream sound files to Sonos
#
# Provides methods to enqueue TTS and Media file requests and make sure that only one is executed at a time
# Volume of the media player is set to a specified level and then restored afterwards
#
# Args:
#
# player - media player to use for announcements
# base = base directory for media - this will be a subdirectory under <home assistant config dir>/www
# ip = IP address of machine running this app
# port = HASS port
#
# To use from another APP:
# TTS:
# sound = self.get_app("Sound")
# sound.tts(text, volume, duration)
# duration should be set to longer than the expected duration of the speech
#
# e.g.:
#
# sound = self.get_app("Sound")
# sound.tts("Warning: Intuder alert", 0.5, 10)#
#
# SOUND:
# sound = self.get_app("Sound")
# sound.play(file, volume, content_type, duration)
# file is the path of the file to play relative to "base"
# Content type is the mime type of the media e.g. "audio/mp3" or "audio/wav"
# duration should be set to longer than the expected duration of the media file
#
# e.g.:
# sound = self.get_app("Sound")
# sound.play("warning.wav", "audio/wav", 0.5, 10)
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class Sound(hass.Hass):

  def initialize(self):

    # Create Queue
    self.queue = Queue(maxsize=0)

    # Create worker thread
    t = Thread(target=self.worker)
    t.daemon = True
    t.start()

    self.log('Successfully initiated Sound!', level='INFO')


    self.event = Event()

  def worker(self):
    active = True
    while active:
      try:
        # Get data from queue
        data = self.queue.get()
        if data["type"] == "terminate":
          active = False
        else:
          old_volume = self.get_state(data["player"], attribute="volume_level")
          self.call_service("media_player/volume_set", entity_id = data["player"], volume_level = data["volume"])
          if data["type"] == "tts":
            # Call TTS service
            self.call_service("tts/google_say", entity_id = data["player"], message = data["text"])
          if data["type"] == "play":
            netpath = netpath = 'http://{}:{}/local/{}/{}'.format(self.args["ip"], self.args["port"], self.args["base"], data["path"])
            self.log('netpath: ' + netpath)
            self.call_service("media_player/play_media", entity_id = data["player"], media_content_id = netpath, media_content_type = data["content"])

          # Sleep to allow message to complete before restoring volume
          time.sleep(int(data["length"]))
          # Restore volume
          if old_volume is None:
            self.call_service("media_player/turn_off", entity_id = data["player"])
            self.set_state(data["player"], state = "off")
          else:
            self.call_service("media_player/volume_set", entity_id = data["player"], volume_level = old_volume)
            # Set state locally as well to avoid race condition
            self.set_state(data["player"], attributes = {"volume_level": old_volume})
      except:
        self.log("Error")
        self.log(sys.exc_info())

      # Rinse and repeat
      self.queue.task_done()

    self.log("Worker thread exiting")
    self.event.set()

  def tts(self, text, volume, length, player):
    self.log('here')
    self.queue.put({"type": "tts", "text": text, "volume": volume, "length": length, "player": player})

  def play(self, path, content, volume, length, player):
    self.queue.put({"type": "play", "path": path, "content": content, "volume": volume, "length": length, "player": player})

  def terminate(self):
    self.event.clear()
    self.queue.put({"type": "terminate"})
    self.event.wait()
