"""
Connect to TCP port 5250 on CasparCG server and instruct it to play
video.

Protocol http://casparcg.com/wiki/CasparCG_2.1_AMCP_Protocol

We use layers 10 for the fallback screen, 50 for the video playout and
100 for the logo in the corner.

"""

import logging
import os
from vision.players.base_player import BasePlayer
from vision.players.casparcg import CasparCG

MEDIA_LAYER = 50
BUG_LAYER = 100

class CasparCGPlayer(BasePlayer):

    def __init__(self, loop_filename):
        self.caspar = CasparCG()
        self.caspar.connect('localhost')
        self.channel = 1
        self.layer = MEDIA_LAYER
        self.framerate = 25
        self.caspar._send_command("CLEAR 1")
        watermarkimage = 'screenbug'
        self._play_file(watermarkimage, layer=BUG_LAYER, loop=True)

    def _play_file(self, filename, resume_offset=0, layer=None, loop=False):
        if layer is None:
            layer = self.layer
        if filename is not None:
            print('CasparCG is being asked to play filename' + filename)
            # ffs. 
            if '/' in filename:
                fullpath = '/mnt/media/' + filename
                print(os.listdir(fullpath))
                filename = 'library/' +  filename + '/' + os.listdir(fullpath)[0]
            #fixme: must check caspar's own library
            if True: # os.path.exists(filename):
                assetname = os.path.splitext(filename)[0]
                if loop:
                    loop = "LOOP"
                else:
                    loop = ""

                if resume_offset != 0:
                    seek = "SEEK %d" % int(resume_offset * self.framerate)
                else:
                    seek = ""

                # FIXME filename should be escaped, ie using \" \\, etc.
                self.caspar._send_command("PLAY %d-%d \"%s\" MIX 50 1 Linear RIGHT %s %s" %
                                   (self.channel, layer, assetname, loop, seek))
            else:
                self.caspar._send_command("CLEAR %d-%d" % (self.channel, layer))
                logging.error(
                    "Didn't find file. Playback never started: %s" % filename)
        else:
            self.caspar._send_command("CLEAR %d-%d" % (self.channel, layer))

    def play_program(self, program=None, resume_offset=0):
        filename = None
        loop = False
        if program is not None:
            filename = program.get_filename()
            loop = program.loop
        self._play_file(filename, resume_offset, self.layer, loop)

    def show_still(self, filename):
        self._play_file(filename, resume_offset, self.layer)

    def pause_screen(self):
        # FIXME todo
        pass

    def seconds_until_end_of_playing_video(self):
	"""
INFO 1-10
201 INFO OK
<?xml version="1.0" encoding="utf-8"?>
<layer>
   <auto_delta>null</auto_delta>
   <frame-number>2230399</frame-number>
   <nb_frames>268</nb_frames>
   <frames-left>4292737165</frames-left>
   <frame-age>81</frame-age>
   <foreground>
      <producer>
         <type>ffmpeg-producer</type>
         <filename>media/AMB.mp4</filename>
         <width>1920</width>
         <height>1080</height>
         <progressive>true</progressive>
         <fps>25</fps>
         <loop>false</loop>
         <frame-number>2230399</frame-number>
         <nb-frames>268</nb-frames>
         <file-frame-number>268</file-frame-number>
         <file-nb-frames>268</file-nb-frames>
      </producer>
   </foreground>
   <background>
      <producer>
         <type>empty-producer</type>
      </producer>
   </background>
   <index>10</index>
</layer>
"""
        #(code, response) = self._send_command("INFO %d-%d" % (self.channel, self.layer),
        #                                      xmlreply = True)
        # xml = lxml...(response)
        # layer/frame-number?
        # FIXME todo
        logging.debug("unable to figure out time to next end")
        return -1
