"""

Connect to TCP port 5250 on CasparCG server and instruct it to play
video.

Protocol http://casparcg.com/wiki/CasparCG_2.1_AMCP_Protocol
"""

import logging
import os
import socket
from vision.players.base_player import BasePlayer

class CasparCGPlayer(BasePlayer):
    def __init__(self, loop_filename):
        self.serverhostname = "caspar.frikanalen.no"
        self.serverport = 5250
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.serverhostname, self.serverport))
        self.channel = 1
        self.layer = 10
        self.framerate = 25
        watermarkimage ='/home/phed/Playout/stills/screenbug.png' 
        self._play_file(watermarkimage, layer=15, loop=True)

    def _disconnect(self):
        self.socket.close()
        self.socket = None

    def _send_command(self, command, xmlreply = False):
        self.socket.send("%s\r\n" % command)
        bufsize = 4096
        response = self.socket.recv(bufsize)
        # FIXME add code to split response in first line and the rest
        return (response, reply)

    def _play_file(self, filename, resume_offset=0, layer=None, loop=False):
        if layer is None:
            layer = self.layer
        if filename is not None:
            if os.path.exists(filename):
                if loop:
                    loop = "LOOP"
                else:
                    loop = ""
                if resume_offset != 0:
                    seek = "SEEK %d" % int(resume_offset * self.framerate)
                # FIXME filename should be escaped, ie using \" \\, etc.
                self._send_command("PLAY %d-%d \"%s\" MIX 50 1 Linear RIGHT %s %s" % \
                                   (self.channel, layer, filename, loop, seek))
            else:
                self._send_command("CLEAR %d-%d" % (channel, layer))
                logging.error("Didn't find file. Playback never started: %s" % filename)
        else:
            self._send_command("CLEAR %d-%d" % (self.channel, layer))


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
        #xml = lxml...(response)
        #layer/frame-number?
        # FIXME todo
        return -1
